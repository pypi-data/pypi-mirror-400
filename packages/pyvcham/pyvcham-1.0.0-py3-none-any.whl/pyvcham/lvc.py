import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import time

from . import diabfunct
from . import couplingfunct

from typing import List, Optional, Tuple, Any
from .logging_config import get_logger

logger = get_logger(__name__)


# --- Plotting Utility ---
# Moved out of the LVCHam class to separate computation from visualization.

def _set_plot_labels(ax, normal_mode, sym_mode, units, size=6):
    """Set common plot labels on a matplotlib axes object."""
    ax.set_xlabel(f"Q_{normal_mode} - irrep: {sym_mode}")
    ax.set_ylabel(f"Energy [{units}]")
    ax.legend(prop={"size": size})
    ax.grid(True)

def _plot_lvc_results(lvc, final_tensor_np: np.ndarray, loss_history: List[float]) -> None:
    """
    Visualize the optimized eigenvalues and loss history.
    """
    disp_np = lvc.displacement_vector.numpy()
    data_db_np = lvc.data_db.numpy()

    # Plot fitted energies vs. ab initio data
    fig, ax = plt.subplots(figsize=(10, 6))
    if lvc.coupling_with_gs:
        for i in range(final_tensor_np.shape[0]):
            ax.plot(disp_np, final_tensor_np[i], label=f"State {i}")
            ax.scatter(disp_np, data_db_np[i], s=10, marker='x')
        _set_plot_labels(ax, lvc.normal_mode, lvc.sym_mode, lvc.VCSystem.units)
    else:
        # Plot ground state separately if not coupled
        ax.plot(disp_np, final_tensor_np[0], label="Ground State")
        ax.scatter(disp_np, data_db_np[0], s=10, marker='x')
        # Plot excited states
        fig, ax = plt.subplots(figsize=(10, 6))
        for i in range(1, final_tensor_np.shape[0]):
            ax.plot(disp_np, final_tensor_np[i], label=f"State {i}")
            ax.scatter(disp_np, data_db_np[i], s=10, marker='x')
        _set_plot_labels(ax, lvc.normal_mode, lvc.sym_mode, lvc.VCSystem.units, size=7)
    plt.show()

    # Plot loss history
    if loss_history:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(loss_history)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_title("Optimization Loss")
        ax.grid(True)
        plt.show()


class LVCHam:
    """
    Builder and optimizer for a Linear Vibronic Coupling (LVC) Hamiltonian.

    This class extracts parameters from a VCSystem object, prepares both
    diagonal (on-diagonal) and off-diagonal terms, and performs gradient-based
    optimization.
    """

    def __init__(
        self,
        normal_mode: int,
        VCSystem: Any,
        funct_guess: Optional[Any] = None,
        nepochs: int = 3000,
        optimization: bool = True,
    ) -> None:
        """
        Initialize the LVCHam instance with system references and configuration.

        Args:
            normal_mode (int): The vibrational mode index to process.
            VCSystem (Any): Object containing system data (displacements, energies, etc.).
            funct_guess (Optional[Any]): Initial guesses for diabatic function parameters. Defaults to None.
            nepochs (int): Number of optimization epochs. Defaults to 3000.

        Raises:
            ValueError: If `normal_mode` is invalid or `VCSystem` lacks required attributes.
        """
        self._validate_constructor_input(normal_mode, VCSystem)
        self.normal_mode = normal_mode
        self.VCSystem = VCSystem
        self.guess_params = funct_guess
        self.nepochs = nepochs
        self.optimization = optimization
        self.optimizer = tf.optimizers.Adam(learning_rate=0.001)  # Configurable optimizer

        logger.info("\n\n----- Initializing LVC Hamiltonian Builder -----")
        logger.info("Normal mode: %d", normal_mode)

        self._initialize_object_params()
        self._initialize_internal_variables()

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def initialize_params(
        self,
        lambda_guess: float = 0.1,
        jt_guess: float = 0.01,
        kappa_guess: float = 0.1,
    ) -> None:
        """
        Initialize TensorFlow variables for optimization based on symmetry and Jahn-Teller (JT) effects.

        Args:
            lambda_guess (float): Initial guess for off-diagonal lambda parameters. Defaults to 0.1.
            jt_guess (float): Initial guess for JT off-diagonal parameters. Defaults to 0.01.
            kappa_guess (float): Initial guess for on-diagonal kappa parameters. Defaults to 0.1.
        """
        on_diag_idx = self._create_on_diag_coupling_param(kappa_guess=kappa_guess)
        off_diag_idx = self._create_off_diag_coupling_param(lambda_guess=lambda_guess, jt_guess=jt_guess)

        self.optimize_params = []
        self.ntotal_param = 0

        for param in [self.funct_param, self.lambda_param, self.kappa_param, 
                      getattr(self, "jt_on_param", None), self.jt_off_param]:
            if param is not None and param.shape[0] > 0:
                self.optimize_params.append(param)
                self.ntotal_param += int(np.prod(param.shape))

        logger.info("Total parameters to optimize: %d", self.ntotal_param)

        # Store indices in VCSystem for bookkeeping
        self.VCSystem.idx_dict["kappa"][self.normal_mode] = on_diag_idx[0]
        self.VCSystem.idx_dict["jt_on"][self.normal_mode] = on_diag_idx[1]
        self.VCSystem.idx_dict["lambda"][self.normal_mode] = off_diag_idx[0]
        self.VCSystem.idx_dict["jt_off"][self.normal_mode] = off_diag_idx[1]

    def initialize_loss_function(self, fn: str = "huber", **kwargs) -> None:
        """
        Set up the loss function for optimization.

        Args:
            fn (str): Name of the loss function (e.g., "huber", "mse"). Defaults to "huber".
            **kwargs: Additional arguments for the loss function.

        Raises:
            NotImplementedError: If the specified loss function is not supported.
        """
        loss_fn_map = {
            "huber": lambda: tf.keras.losses.Huber(**kwargs),
            "mse": lambda: tf.keras.losses.MeanSquaredError(),
            "mae": lambda: tf.keras.losses.MeanAbsoluteError(),
            "msle": lambda: tf.keras.losses.MeanSquaredLogarithmicError(),
            "logcosh": lambda: tf.keras.losses.LogCosh(),
            "kld": lambda: tf.keras.losses.KLDivergence(),
            "poisson": lambda: tf.keras.losses.Poisson(),
            "cosine": lambda: tf.keras.losses.CosineSimilarity(),
            "sparse": lambda: tf.keras.losses.SparseCategoricalCrossentropy(),
            "binary": lambda: tf.keras.losses.BinaryCrossentropy(),
        }
        fn_lower = fn.lower()
        if fn_lower not in loss_fn_map:
            raise NotImplementedError(f"Loss function '{fn_lower}' not supported.")
        self.loss_fn = loss_fn_map[fn_lower]()
    def optimize(self) -> None:
        """
        Perform gradient-based optimization with a smart early-stopping mechanism.
        """
        if self._check_inactive_mode() or self.ntotal_param == 0 or not self.optimization:
            logger.info("Skipping optimization: mode inactive or no parameters.")
            final_tensor = self._build_vcham_tensor().numpy()
            _plot_lvc_results(self, final_tensor, loss_history=[])
            self._finalize_output()
            return

        t_start = time.perf_counter()

        # ------------------- Smart early stopping settings -------------------
        patience          = 150          # how many steps we wait after last improvement
        min_rel_delta     = 1e-4         # 0.01 % relative improvement → counts as progress
        min_abs_delta     = 1e-7         # when loss is tiny, this is the fallback
        patience_counter  = 0
        best_loss         = float("inf")
        # ---------------------------------------------------------------------

        loss_history: List[float] = []
        logger.info("Optimizing mode %d...", self.normal_mode)

        for step in range(self.nepochs):
            loss_val = float(self._train_step())
            loss_history.append(loss_val)

            if step % 100 == 0:
                logger.info("Step %d, Loss: %.6f", step, loss_val)

            # ---- decide if this step brought a meaningful improvement ----
            improved = False
            if best_loss == float("inf"):
                improved = True                       # first iteration always improves
            elif best_loss > 1.0:
                # when loss is still "large" → use relative improvement
                if loss_val < best_loss * (1.0 - min_rel_delta):
                    improved = True
            else:
                # when loss is already very small → use absolute improvement
                if loss_val < best_loss - min_abs_delta:
                    improved = True

            if improved:
                best_loss = loss_val
                patience_counter = 0
                logger.debug("New best loss: %.3e (step %d)", best_loss, step)
            else:
                patience_counter += 1

            # ---- early stopping ----
            if patience_counter >= patience:
                logger.info(
                    "Early stopping triggered at step %d (no improvement for %d steps). "
                    "Best loss: %.6f", step, patience, best_loss
                )
                break

        elapsed_time = time.perf_counter() - t_start
        final_tensor = self._build_vcham_tensor().numpy()
        _plot_lvc_results(self, final_tensor, loss_history)

        if hasattr(self, "active_jt_states"):
            self._save_jt()

        logger.info("Optimization finished – Final reported loss: %.6f", best_loss)
        logger.info("Optimization completed in %.2f seconds.", elapsed_time)
        self._finalize_output()

    # def optimize(self) -> None:
    #     """
    #     Perform gradient-based optimization or build the Hamiltonian directly if no optimization is needed.
    #     """
    #     if self._check_inactive_mode() or self.ntotal_param == 0 or not self.optimization:
    #         logger.info("Skipping optimization: mode inactive or no parameters.")
    #         final_tensor = self._build_vcham_tensor().numpy()
    #         _plot_lvc_results(self, final_tensor, loss_history=[])
    #         self._finalize_output()
    #         return

    #     t_start = time.perf_counter()
    #     best_loss, patience, patience_counter = float("inf"), 10000, 0
    #     loss_history: List[float] = []

    #     logger.info("Optimizing mode %d...", self.normal_mode)
    #     for step in range(self.nepochs):
    #         loss_val = float(self._train_step())
    #         loss_history.append(loss_val)

    #         if step % 100 == 0:
    #             logger.info("Step %d, Loss: %.6f", step, loss_val)

    #         if loss_val < best_loss - 1e-2:
    #             best_loss = loss_val
    #             patience_counter = 0
    #         else:
    #             patience_counter += 1
    #             if patience_counter >= patience:
    #                 logger.info("Early stopping at step %d.", step)
    #                 break

    #     elapsed_time = time.perf_counter() - t_start
    #     final_tensor = self._build_vcham_tensor().numpy()
    #     _plot_lvc_results(self, final_tensor, loss_history)

    #     if hasattr(self, "active_jt_states"):
    #         self._save_jt()

    #     logger.info("Final loss: %.6f", best_loss)
    #     logger.info("Optimization completed in %.2f seconds.", elapsed_time)
    #     self._finalize_output()

    # -------------------------------------------------------------------------
    # Internal Methods: Building the TensorFlow Graph
    # -------------------------------------------------------------------------

    @tf.function
    def _build_vcham_tensor(self) -> tf.Tensor:
        """
        Construct the Hamiltonian tensor and compute its eigenvalues.

        Returns:
            tf.Tensor: Eigenvalues [n_states, n_disp].
        """
        diag_vals = self._build_diagonal_potentials()
        vcham_tensor = tf.linalg.diag(tf.transpose(diag_vals))

        idx_all, vals_all = [], []
        for idx, param in [(self.lambda_idx, self.lambda_param), (self.jt_off_idx, self.jt_off_param)]:
            lam_idx, lam_vals = self._collect_off_diagonal_contributions(idx, param)
            idx_all.extend(lam_idx)
            vals_all.extend(lam_vals)

        if idx_all:
            vcham_tensor = tf.tensor_scatter_nd_add(vcham_tensor, tf.concat(idx_all, axis=0), 
                                                    tf.concat(vals_all, axis=0))
        vcham_tensor = (vcham_tensor + tf.transpose(vcham_tensor, perm=[0, 2, 1])) / 2

        return tf.transpose(tf.linalg.eigvalsh(vcham_tensor))

    @tf.function
    def _train_step(self) -> tf.Tensor:
        """
        Execute one optimization step.

        Returns:
            tf.Tensor: Loss value.
        """
        with tf.GradientTape() as tape:
            loss_val = self._cost_function()
        grads = tape.gradient(loss_val, self.optimize_params)
        grads, _ = tf.clip_by_global_norm(grads, 1.0)
        self.optimizer.apply_gradients(zip(grads, self.optimize_params))
        return loss_val

    # -------------------------------------------------------------------------
    # Internal Helpers: On/Off Diagonal, Potential Assembly, JT Handling
    # -------------------------------------------------------------------------

    def _build_diagonal_potentials(self) -> tf.Tensor:
        """
        Compute diagonal potential terms for each state by assembling the correct
        diabatic function with its corresponding optimized parameters.
        This method handles JT and non-JT states.
        """
        diag_per_state = []
        # These offsets track the position while slicing the flat parameter tensors.
        non_jt_param_offset, jt_param_offset = 0, 0

        for s in range(self.nstates):
            func_type = self.diab_functions[s]
            params_chunk = None
            n_vars = diabfunct.n_var.get(func_type, 0)

            # Determine which parameter tensor to use and slice the appropriate chunk.
            if s in self.non_jt_states:
                if n_vars > 0 and self.funct_param is not None:
                    params_chunk = self.funct_param[non_jt_param_offset : non_jt_param_offset + n_vars]
                    non_jt_param_offset += n_vars
            elif hasattr(self, 'active_jt_states') and (s in self.active_jt_states or s in self.inactive_jt_states):
                if n_vars > 0 and self.jt_on_param is not None:
                    params_chunk = self.jt_on_param[jt_param_offset : jt_param_offset + n_vars]
                    # This logic ensures that an inactive JT state reuses the parameters of its
                    # active partner by only advancing the offset after the inactive state.
                    if hasattr(self, 'inactive_jt_states') and s in self.inactive_jt_states:
                        jt_param_offset += n_vars
            
            # The _assemble_on_diag_term function handles cases with and without parameters
            # and adds the necessary energy shift. It returns a tensor of the correct shape.
            potential_term = self._assemble_on_diag_term(s, func_type, params_chunk)

            diag_per_state.append(potential_term)

        return tf.stack(diag_per_state, axis=0)

    def _assemble_on_diag_term(self, state_idx: int, func_name: str, param_var: Optional[tf.Tensor]) -> tf.Tensor:
        """Assemble a single diagonal potential term."""
        disp = self.displacement_vector # Displacement vector
        e0_shift = self.e0_shifts[state_idx] # Energy shift
        pot_fn = diabfunct.potential_functions[func_name] # Diabatic function
        coupling_fn = couplingfunct.coupling_funct.get(self.coupling_order) # Coupling function
        base_term = pot_fn(disp, self.omega, param_var) if diabfunct.kappa_compatible[func_name] else pot_fn(disp, param_var)

        if diabfunct.kappa_compatible[func_name]:
            if self.sym_mode == self.total_sym_irrep and self.kappa_param is not None and state_idx in self.kappa_idx:
                kappa_val = self.kappa_param[self.kappa_idx.index(state_idx)]
                base_term += coupling_fn(disp, kappa_val)
            elif self.inactive_mode:
                if not hasattr(self, "active_jt_state_map"):
                    self.active_jt_state_map = {st_id: idx for idx, st_id in enumerate(sorted(self.active_jt_states))}
                k_idx = self.active_jt_state_map[state_idx]
                kappa_val = self.jt_off_param[k_idx if self.sign_k_params == 1 else k_idx - 1] * self.sign_k_params
                base_term += coupling_fn(disp, kappa_val)
                self.sign_k_params *= -1
        elif state_idx == 0 and not diabfunct.kappa_compatible[func_name]:
            base_term = pot_fn(disp, param_var, gs=True)

        return base_term + e0_shift

    def _collect_off_diagonal_contributions(self, idx_list: List[List[int]], param_var: Optional[tf.Variable]) -> Tuple[List[tf.Tensor], List[tf.Tensor]]:
        """Gather off-diagonal terms."""
        if not idx_list or param_var is None:
            return [], []

        n_disp = tf.shape(self.displacement_vector)[0]
        coupling_fn = couplingfunct.coupling_funct.get(self.coupling_order)
        if not coupling_fn:
            raise NotImplementedError(f"Coupling '{self.coupling_order}' not implemented.")

        indices, values = [], []
        for i, (st1, st2) in enumerate(idx_list):
            p_val = param_var[i] if len(param_var.shape) > 0 else param_var
            update_vals = coupling_fn(self.displacement_vector, p_val)
            disp_indices = tf.range(n_disp, dtype=tf.int32)
            idx1 = tf.stack([disp_indices, tf.fill([n_disp], st1), tf.fill([n_disp], st2)], axis=1)
            idx2 = tf.stack([disp_indices, tf.fill([n_disp], st2), tf.fill([n_disp], st1)], axis=1)
            indices.extend([idx1, idx2])
            values.extend([update_vals, update_vals])

        return indices, values

    @tf.function
    def _cost_function(self) -> tf.Tensor:
        """Compute the optimization loss."""
        return tf.reduce_mean(self.loss_fn(self.data_db, self._build_vcham_tensor()))

    # -------------------------------------------------------------------------
    # Jahn-Teller Handling
    # -------------------------------------------------------------------------

    def _initialize_diab_fn_variables(self) -> None:
        """Prepare parameters based on JT effects."""
        self.inactive_mode = False
        if not self.jt_effects or not any(eff.get("mode") == self.normal_mode for eff in self.jt_effects):
            self._prepare_non_jt_param()
        else:
            self._prepare_jt_param()

    def _prepare_jt_param(self) -> None:
        """
        Handle JT parameter preparation. This is a critical and complex part of the logic.
        It distinguishes between:
        1. Active JT modes: Parameters are optimized.
        2. Inactive JT modes: Parameters are copied from a specified 'source' mode.
           This is used for coupled JT modes (e.g., E x e problems) where two modes
           share the same coupling parameters but with opposite signs for kappa.
        """
        current_effects = [eff for eff in self.jt_effects if eff.get("mode") == self.normal_mode]
        inactive_effects = [eff for eff in current_effects if not eff.get("active", True)]
        active_effects = [eff for eff in current_effects if eff.get("active", True)]

        jt_state_pairs = []
        if inactive_effects:
            # --- Inactive JT Mode Logic ---
            # An inactive mode does not optimize its own parameters. Instead, it reuses
            # the parameters from an 'active' source mode, which must have been
            # processed already. This is key for creating degenerate potentials.
            source_mode = inactive_effects[0].get("source")
            if source_mode is None:
                raise ValueError("Inactive JT effect requires a 'source' key.")
            jt_state_pairs.extend(sum([eff.get("state_pairs", []) for eff in inactive_effects], []))
            total_jt_states = self._gather_jt_states(jt_state_pairs)

            if hasattr(self.VCSystem, "jt_params") and source_mode in self.VCSystem.jt_params:
                source_jt = self.VCSystem.jt_params[source_mode]
                self.jt_on_param = tf.Variable(source_jt["on"], dtype=tf.float32, name="jt_on_param_inactive")
                self.jt_off_param = tf.Variable(source_jt["off"], dtype=tf.float32, name="jt_off_param_inactive")
                # This flag is used in _assemble_on_diag_term to create the +kappa/-kappa splitting for the degenerate states.
                self.sign_k_params = 1
                self.active_jt_states = sorted(list(total_jt_states))
                self.inactive_mode = True
                self.non_jt_states = list(set(range(self.nstates)) - set(total_jt_states))
                for s in range(self.nstates):
                    self.summary_output[s] = "" if s in self.non_jt_states else "JT"
                return

        jt_state_pairs.extend(sum([eff.get("state_pairs", []) for eff in active_effects], []))
        active_jt_states, inactive_jt_states, total_jt_states = self._classify_jt_state_pairs(jt_state_pairs)
        self.active_jt_states, self.inactive_jt_states = sorted(list(active_jt_states)), sorted(list(inactive_jt_states))
        self.non_jt_states = list(set(range(self.nstates)) - set(total_jt_states))

        diab_non_jt, diab_jt = [self.diab_functions[s] for s in self.non_jt_states], [self.diab_functions[s] for s in self.active_jt_states]
        self.n_var_list, self.n_var_jt = [diabfunct.n_var[f] for f in diab_non_jt], [diabfunct.n_var[f] for f in diab_jt]

        if self.guess_params is None:
            self.funct_param = tf.Variable(np.array([diabfunct.initial_guesses[f] for f in diab_non_jt]).flatten().tolist(), 
                                           dtype=tf.float32, name="funct_param")
            self.jt_on_param = tf.Variable(np.array([diabfunct.initial_guesses[f] for f in diab_jt]).flatten().tolist(), 
                                           dtype=tf.float32, name="jt_on_param")

        for s in range(self.nstates):
            self.summary_output[s] = "" if s in self.non_jt_states else "JT"

    def _prepare_non_jt_param(self) -> None:
        """
        Prepare parameters for a mode that has no JT effects.
        """
        self.non_jt_states = list(range(self.nstates))
        if self.guess_params is None:
            self.guess_params = [
                diabfunct.initial_guesses[f] for f in self.diab_functions
            ]

        self.VCSystem.n_diab_params[self.normal_mode] = [
            diabfunct.n_var[f] for f in self.diab_functions
        ]
        logger.info("n_var_list (non-JT): %s", self.VCSystem.n_diab_params[self.normal_mode])

        if self.guess_params is not None:
            flat_guess = np.array(self.guess_params).flatten().tolist()
            self.funct_param = tf.Variable(flat_guess, dtype=tf.float32, name="funct_param")
        else:
            self.funct_param = None

    def _save_jt(self) -> None:
        """Save JT parameters to VCSystem."""
        jt_values = {"mode": self.normal_mode, "params": {"on": None, "off": None}}
        if hasattr(self, "jt_on_param") and self.jt_on_param is not None:
            jt_values["params"]["on"] = self.jt_on_param.numpy()
        if self.jt_off_param is not None:
            jt_values["params"]["off"] = self.jt_off_param.numpy()
        self.VCSystem._append_jt_param(jt_values)
        logger.info("Saved JT parameters for mode %d.", self.normal_mode)

    def _gather_jt_states(self, jt_state_pairs: List[Tuple[int, int]]) -> set:
        """Collect JT states from pairs."""
        total_states = set()
        for pair in jt_state_pairs:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError("JT state pairs must be 2-element lists/tuples.")
            total_states.update(pair)
        return total_states

    def _classify_jt_state_pairs(self, jt_state_pairs: List[Tuple[int, int]]) -> Tuple[set, set, set]:
        """Classify JT states."""
        active, inactive, total = set(), set(), set()
        for pair in jt_state_pairs:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError("JT state pairs must be 2-element lists/tuples.")
            active.add(pair[0])
            inactive.add(pair[1])
            total.update(pair)
        return active, inactive, total

    # -------------------------------------------------------------------------
    # Core Initialization
    # -------------------------------------------------------------------------

    def _initialize_object_params(self) -> None:
        """Extract and convert VCSystem parameters."""
        sys_ = self.VCSystem
        nm = self.normal_mode
        self.nstates = sys_.number_states
        self.displacement_vector = tf.convert_to_tensor(sys_.displacement_vector[nm], dtype=tf.float32)
        self.data_db = tf.convert_to_tensor(sys_.database_abinitio[nm], dtype=tf.float32)
        self.diab_functions = [func.lower() for func in sys_.diab_funct[nm]]
        self._validate_diabatic_functions()
        self.coupling_with_gs, self.omega = sys_.coupling_with_gs, sys_.vib_freq[nm]
        self.e0_shifts = tf.convert_to_tensor(sys_.energy_shift, dtype=tf.float32)
        self.symmetry_mask = tf.convert_to_tensor(sys_.symmetry_matrix[nm], dtype=tf.float32)
        self.symmetry_point_group, self.sym_mode = sys_.symmetry_point_group.upper(), sys_.symmetry_modes[nm].upper()
        self.jt_effects, self.total_sym_irrep = sys_.jt_effects, sys_.totally_sym_irrep
        self.coupling_order = getattr(sys_, "vc_type", "linear").lower()
        if self.coupling_order not in couplingfunct.COUPLING_TYPES:
            raise NotImplementedError(f"Coupling '{self.coupling_order}' not implemented.")
        self.idx_dict = sys_.idx_dict

    def _validate_constructor_input(self, normal_mode: int, VCSystem: Any) -> None:
        """Validate constructor inputs."""
        if not isinstance(normal_mode, int) or normal_mode < 0:
            raise ValueError("Normal mode must be a non-negative integer.")
        if VCSystem is None or any(not hasattr(VCSystem, attr) for attr in 
                                  ["displacement_vector", "database_abinitio", "diab_funct", "vib_freq", "symmetry_matrix", "symmetry_point_group"]):
            raise ValueError("VCSystem must provide required attributes.")

    def _validate_diabatic_functions(self) -> None:
        """Check diabatic function validity."""
        for func in self.diab_functions:
            if func not in diabfunct.potential_functions:
                raise ValueError(f"Unsupported diabatic function: {func}")

    def _initialize_internal_variables(self) -> None:
        """Set up internal variables."""
        self.summary_output = [""] * self.nstates
        self.kappa_idx, self.lambda_idx, self.jt_off_idx = [], [], []
        self.ntotal_param = 0
        self.funct_param = self.kappa_param = self.lambda_param = self.jt_on_param = self.jt_off_param = None
        self.n_var_list, self.optimize_params = [], []

    # -------------------------------------------------------------------------
    # On-diagonal & Off-diagonal Parameter Generation
    # -------------------------------------------------------------------------
    def _create_on_diag_coupling_param(self, kappa_guess: float = 0.1) -> Tuple[List[int], List[int]]:
        """Generate on-diagonal parameters."""
        diag_sym_mask = tf.linalg.diag_part(self.symmetry_mask)
        # There is no kappa for the ground state (int(idx[0]) == 0)
        self.kappa_idx = [int(idx[0]) for idx in tf.where(tf.equal(diag_sym_mask, 1)).numpy() 
                          if int(idx[0]) != 0 and diabfunct.kappa_compatible[self.diab_functions[int(idx[0])]]]
        if self.kappa_idx:
            self.kappa_param = self._process_guess(kappa_guess, len(self.kappa_idx), "kappa_param")
            for s in self.kappa_idx:
                self.summary_output[s] = "kappa"
        self.jt_on_idx = [int(i[0]) for i in tf.where(tf.equal(diag_sym_mask, 2)).numpy()]
        return self.kappa_idx, self.jt_on_idx

    def _create_off_diag_coupling_param(self, lambda_guess: float = 0.01, jt_guess: float = 0.01) -> Tuple[List[List[int]], List[List[int]]]:
        """Generate off-diagonal parameters."""
        upper_tri = tf.linalg.band_part(self.symmetry_mask, 0, -1) - tf.linalg.diag(tf.linalg.diag_part(self.symmetry_mask))
        self.lambda_idx = [[int(i[0]), int(i[1])] for i in tf.where(tf.equal(upper_tri, 1)).numpy()]
        if self.lambda_idx:
            self.lambda_param = self._process_guess(lambda_guess, len(self.lambda_idx), "lambda_param")
        self._create_jt_off_diag(jt_guess)
        self._initialize_diab_fn_variables()
        return self.lambda_idx, self.jt_off_idx
    


    def _create_jt_off_diag(self, jt_guess: float = 0.01) -> None:
        """
        Identify JT off-diagonal terms (symmetry_mask == 2) and initialize JT parameters.

        Parameters
        ----------
        jt_guess : float, optional
            Initial guess for JT off-diagonal parameters (default: 0.01).
        """
        upper_tri = tf.linalg.band_part(self.symmetry_mask, 0, -1) - tf.linalg.diag(
            tf.linalg.diag_part(self.symmetry_mask)
        )
        jt_off_tensor = tf.where(tf.equal(upper_tri, 2))
        self.jt_off_idx = [
            [int(i[0]), int(i[1])] for i in jt_off_tensor.numpy()
        ]
        logger.info("JT off-diagonal pairs: %s", self.jt_off_idx)

        if self.jt_off_idx:
            self.jt_off_param = self._process_guess(
                jt_guess, len(self.jt_off_idx), name="jt_off_param"
            )
        else:
            self.jt_off_param = None

    # -------------------------------------------------------------------------
    # Utility and Validation
    # -------------------------------------------------------------------------

    def _check_inactive_mode(self) -> bool:
        """Check if the mode is inactive."""
        return any(eff.get("mode") == self.normal_mode and not eff.get("active", True) for eff in self.jt_effects or [])

    def _process_guess(self, guess: Any, n_pairs: int, name: str = "param") -> tf.Variable:
        """Convert guess to a TensorFlow variable."""
        if isinstance(guess, (float, int)):
            arr_guess = [guess] * n_pairs
        elif isinstance(guess, list) and len(guess) <= n_pairs:
            arr_guess = (guess * ((n_pairs // len(guess)) + 1))[:n_pairs]
        else:
            raise ValueError(f"Guess must be a scalar or list of length <= {n_pairs}.")
        
        return tf.Variable(arr_guess, dtype=tf.float32, name=name)

    def _finalize_output(self) -> None:
        """Store results in VCSystem."""
        self.VCSystem.summary_output[self.normal_mode] = self.summary_output

        # Replace any NaNs in optimized parameters with zeros, in-place.
        for param in self.optimize_params:
            if isinstance(param, tf.Variable):
                numpy_val = param.numpy()
                if np.isnan(numpy_val).any():
                    # Create a tensor of zeros with the same shape and type
                    zeros = tf.zeros_like(param)
                    # Assign the zeros back to the variable, preserving its name and other properties.
                    param.assign(zeros)

        # Store the (potentially modified) list of tf.Variable objects
        self.VCSystem.optimized_params[self.normal_mode] = self.optimize_params