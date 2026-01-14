import tkinter as tk
from tkinter import ttk
import numpy as np
import pickle
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .diabfunct import potential_functions, kappa_compatible
from .couplingfunct import linear_coupling
from tensorflow import convert_to_tensor
from typing import Any, List, Optional, Tuple
from .logging_config import get_logger

logger = get_logger(__name__)


class GuessImprover(tk.Tk):
    # Constants for plot limits and slider bounds
    SLIDER_BOUND = 40.0
    PLOT_YLIM_STATE0 = [0.0, 6.0]
    PLOT_XLIM_STATE0 = [-8, 8]
    PLOT_Y_OFFSET_OTHER_STATES = [-0.2, 4]

    """
    A Tkinter application for dynamic parameter adjustment.

    This application creates a GUI that displays a matplotlib plot
    and provides entries and sliders for adjusting parameters. It
    uses a given 'system' object (VCSystem) and an 'initial_guess'
    object to configure and update the display.
    """

    def __init__(self, system: Any) -> None:
        """
        Initialize the Application.

        Parameters
        ----------
        system : Any
            An object containing attributes such as n_diab_params,
            diab_funct, displacement_vector, database_abinitio,
            vib_freq, energy_shift, symmetry_matrix, symmetry_modes,
            totally_sym_irrep, units, etc.
        initial_guess : Any
            The initial guess values used in the application.
        """
        super().__init__()

        # Core references
        self.system = system
        # Convert optimized_params (list of tf.Variable) to a list of numpy arrays
        # for easier manipulation within the GUI.
        self.initial_guess = [[param.numpy() for param in mode_params] 
                              for mode_params in self.system.optimized_params]

        self.title("Dynamic Parameter Adjustment")

        # Default mode/state
        self.mode = 0
        self.state = 0
        self.kappa: float = 0.0

        # Lists to hold dynamically created widgets for easy cleanup
        self.entries: List[tk.Entry] = []
        self.sliders: List[tk.Scale] = []
        self.labels: List[tk.Label] = []
        self.frames: List[tk.Frame] = []

        # Create the matplotlib figure and embed it into the Tkinter interface
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create frames for mode/state selection and diabatic function info
        self._create_mode_state_frame()
        self._create_diabfunct_frame()

        # Create kappa frame if needed
        if self.system.symmetry_modes[self.mode] == self.system.totally_sym_irrep:
            if kappa_compatible[self.system.diab_funct[self.mode][self.state]]:
                self._create_kappa_frame()

        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill="x", pady=10)

        params_label = tk.Label(self, text="Parameters")
        params_label.pack(side=tk.TOP, padx=5)

        # Create entries and sliders for parameter adjustment
        self.bound = self.SLIDER_BOUND
        lower_bound = int(
            np.sum(self.system.n_diab_params[self.mode][: self.state], dtype=np.int8)
        )
        upper_bound = int(
            lower_bound + self.system.n_diab_params[self.mode][self.state]
        )
        self.default_params = (
            self.initial_guess[self.mode][0][lower_bound:upper_bound]
        )
        self._create_entries_and_sliders(self.default_params, self.bound)

        # Draw initial plot using default parameter values
        self._draw_plot(*self.default_params)

        # Create button to output all parameters and kappa values
        self._create_output_button()

    # ---------------------------
    # Public Methods
    # ---------------------------

    def run(self) -> None:
        """Start the Tkinter main loop."""
        self.mainloop()

    # ---------------------------
    # UI Setup
    # ---------------------------

    def _create_mode_state_frame(self) -> None:
        """
        Create the frame for modifying the mode and state.
        """
        mode_frame = tk.Frame(self)
        mode_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(mode_frame, text="Mode:").grid(row=0, column=0, padx=5, sticky="e")
        self.mode_entry = tk.Entry(mode_frame)
        self.mode_entry.grid(row=0, column=1, padx=5, sticky="w")
        self.mode_entry.insert(0, str(self.mode))

        tk.Label(mode_frame, text="State:").grid(row=0, column=2, padx=5, sticky="e")
        self.state_entry = tk.Entry(mode_frame)
        self.state_entry.grid(row=0, column=3, padx=5, sticky="w")
        self.state_entry.insert(0, str(self.state))

        save_button_state = tk.Button(
            mode_frame,
            text="Modify Mode/State",
            command=self._update_plot_from_states
        )
        save_button_state.grid(row=0, column=4, padx=5, sticky="w")

    def _create_diabfunct_frame(self) -> None:
        """
        Create the frame that displays diabatic function information.
        """
        diabfunct_frame = tk.Frame(self)
        diabfunct_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        diab_funct_label = tk.Label(diabfunct_frame, text="Diabatic function:")
        diab_funct_label.grid(row=0, column=1, sticky="e", padx=5)

        self.diabfunct_label = tk.Label(
            diabfunct_frame,
            text=f"{self.system.diab_funct[self.mode][self.state]} potential",
        )
        self.diabfunct_label.grid(row=0, column=2, sticky="w", padx=5)

    def _create_kappa_frame(self) -> None:
        """
        Create a frame with an entry and button for entering a kappa value.
        Only shown if the mode corresponds to the totally symmetric irreducible representation.
        """
        self.kappa_frame = tk.Frame(self)
        self.kappa_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(self.kappa_frame, text="Kappa:").pack(side=tk.LEFT, padx=5)
        self.kappa_entry = tk.Entry(self.kappa_frame)
        self.kappa_entry.pack(side=tk.LEFT, padx=5)

        # Set the default kappa value from the initial guess
        default_kappa = self.initial_guess[self.mode][1][self.state]
        self.kappa_entry.insert(0, str(default_kappa))
        self.kappa = default_kappa

        kappa_button = tk.Button(
            self.kappa_frame,
            text="Update Kappa",
            command=self._update_kappa_value
        )
        kappa_button.pack(side=tk.LEFT, padx=5)

    def _create_output_button(self) -> None:
        """
        Create a button that outputs all parameters and kappas as nested lists,
        and pickles them to a file.
        """
        output_button = tk.Button(
            self,
            text="Output All Parameters",
            command=self._output_all_parameters
        )
        output_button.pack(side=tk.TOP, padx=5, pady=5)

    # ---------------------------
    # Handlers and Callbacks
    # ---------------------------

    def _update_kappa_value(self) -> None:
        """
        Update the kappa value from the entry field and optionally redraw the plot.
        """
        try:
            self.kappa = float(self.kappa_entry.get())
            logger.info("Kappa value updated to: %f", self.kappa)
            current_values = [float(entry.get()) for entry in self.entries]
            self._draw_plot(*current_values)
        except ValueError:
            logger.error("Please enter a valid numeric value for kappa.")

    def _output_all_parameters(self) -> None:
        """
        Retrieve and log the nested lists of parameters and kappas, then store them via pickle.
        """
        parameters_nested, kappas_nested = self._get_nested_parameters_and_kappas()
        all_params = {"parameters": parameters_nested, "kappas": kappas_nested}

        file_name = "initial_guess_gui.pkl"
        with open(file_name, "wb") as file:
            pickle.dump(all_params, file)
        logger.info("All parameters saved successfully to %s", file_name)

    def _update_plot_from_states(self, event: Optional[Any] = None) -> None:
        """
        Update the plot when the user changes the mode/state. Rebuild
        the parameter sliders/entries accordingly.
        """
        try:
            self.state = int(self.state_entry.get())
            self.mode = int(self.mode_entry.get())

            lower_bound = int(
                np.sum(self.system.n_diab_params[self.mode][: self.state], dtype=np.int8)
            )
            upper_bound = int(
                lower_bound + self.system.n_diab_params[self.mode][self.state]
            )
            default_params = (
                self.initial_guess[self.mode][0][lower_bound:upper_bound]
            )
            self.diabfunct_label.config(
                text=f"{self.system.diab_funct[self.mode][self.state]} potential"
            )

            self._create_entries_and_sliders(default_params, self.bound)
            function_type = self.system.diab_funct[self.mode][self.state]

            if self.system.symmetry_modes[self.mode] == self.system.totally_sym_irrep:
                if kappa_compatible[function_type]:
                    if not hasattr(self, "kappa_frame"):
                        self._create_kappa_frame()
                    else:
                        self.kappa_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
                        default_kappa = (
                            self.initial_guess[self.mode][1][self.state]
                        )
                        self.kappa_entry.delete(0, tk.END)
                        self.kappa_entry.insert(0, str(default_kappa))
                        self.kappa = default_kappa
                else:
                    if hasattr(self, "kappa_frame"):
                        self.kappa_frame.pack_forget()
            self._draw_plot(*default_params)
            logger.info("State updated to: %d", self.state)
        except ValueError:
            logger.error("Please enter a valid integer for the mode/state.")

    # ---------------------------
    # Parameter and Kappa Logic
    # ---------------------------

    def _get_nested_parameters_and_kappas(
        self
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Build and return two nested lists:

        1. parameters_nested: A list (per mode) of lists (per state)
           containing the diabatic function parameters.
        2. kappas_nested: A list (per mode) of lists (per state)
           containing the corresponding kappa values. If a state
           has no kappa, we store an empty list instead.

        Returns
        -------
        (parameters_nested, kappas_nested)
        """
        parameters_nested = []
        kappas_nested = []

        for mode_idx in range(len(self.initial_guess)):
            mode_params: List[List[float]] = []
            mode_kappas: List[float] = []

            # Get the parameters for the current mode
            current_mode_params = self.initial_guess[mode_idx][0]
            current_mode_kappas = self.initial_guess[mode_idx][1] if len(self.initial_guess[mode_idx]) > 1 else []

            lower_bound = 0
            for state_idx, num_params in enumerate(self.system.n_diab_params[mode_idx]):
                upper_bound = lower_bound + num_params
                state_params = list(current_mode_params[lower_bound:upper_bound])
                mode_params.append(state_params)
                lower_bound = upper_bound

                # Check if we have a kappa for this state
                if self.system.summary_output[mode_idx][state_idx] == "kappa":
                    mode_kappas.append(float(current_mode_kappas[state_idx]))
                else:
                    mode_kappas.append(0.0)  # Store 0.0 if no kappa

            parameters_nested.append(mode_params)
            kappas_nested.append(mode_kappas)

        return parameters_nested, kappas_nested

    def save_values(self) -> None:
        """
        Save the current slider values back to the initial guess and
        optionally save the kappa value.

        NOTE: This modifies the numpy array returned by .numpy().
        If your `initial_guess` references an actual tf.Variable,
        reassigning to that tensor might be necessary to fully persist changes.
        """
        # Update parameter values
        lower_bound = int(
            np.sum(self.system.n_diab_params[self.mode][: self.state], dtype=np.int8)
        )
        upper_bound = int(
            lower_bound + self.system.n_diab_params[self.mode][self.state]
        )
        # Get the numpy array from the tensor
        arr = self.initial_guess[self.mode][0].numpy() # Get numpy array from tf.Variable

        for i, slider in enumerate(self.sliders):
            arr[lower_bound + i] = slider.get()
        
        # Convert the updated array back to a tensor and reassign it
        self.initial_guess[self.mode][0].assign(convert_to_tensor(arr)) # Use .assign() for tf.Variable

        # If a kappa value exists, update it
        if self.system.summary_output[self.mode][self.state] == "kappa":
            try:
                kappa_arr = self.initial_guess[self.mode][1].numpy() # Get numpy array from tf.Variable
                kappa_arr[self.state] = self.kappa
                self.initial_guess[self.mode][1].assign(convert_to_tensor(kappa_arr)) # Use .assign() for tf.Variable
            except Exception as exc:
                logger.error("Error updating kappa value: %s", str(exc))

        # Saving changes to a file
        file_name = "initial_guess_gui.pkl"
        with open(file_name, "wb") as file:
            pickle.dump(self.initial_guess, file) # Pickle self.initial_guess directly
        logger.info("Values saved successfully to %s", file_name)

    # ---------------------------
    # UI for Parameter Controls
    # ---------------------------

    def _clear_entries_and_sliders(self) -> None:
        """
        Remove all dynamically created entries, sliders, labels, and frames
        to prepare for a fresh set.
        """
        widget_groups = [self.entries, self.sliders, self.labels, self.frames]
        for widget_list in widget_groups:
            for widget in widget_list:
                widget.pack_forget()
                widget.destroy()
            widget_list.clear()

    def _create_entries_and_sliders(self, default_values: List[float], bound: float) -> None:
        """
        Create entry fields and sliders for each parameter.

        Parameters
        ----------
        default_values : List[float]
            The default parameter values to display.
        bound : float
            The bound for the slider (from -bound to bound).
        """
        self._clear_entries_and_sliders()

        for i, default_val in enumerate(default_values):
            frame = tk.Frame(self)
            frame.pack(side=tk.TOP, fill=tk.X, pady=2)
            self.frames.append(frame)

            label = tk.Label(frame, text=f"k{i+1}")
            label.grid(row=0, column=0, padx=5)
            self.labels.append(label)

            entry = tk.Entry(frame)
            entry.grid(row=0, column=1, padx=5, sticky="ew")
            entry.insert(0, str(default_val))
            # Bind to re-draw the plot on Enter press
            entry.bind("<Return>", self._update_plot_from_entry)
            self.entries.append(entry)

            slider = tk.Scale(
                frame,
                from_=-bound,
                to=bound,
                resolution=1e-5,
                orient=tk.HORIZONTAL,
                command=self._update_plot_from_sliders,
            )
            slider.set(default_val)
            slider.grid(row=0, column=2, padx=5, sticky="ew")
            self.sliders.append(slider)

            # Only add the "Save Values" button in the last row
            if i == len(default_values) - 1:
                save_button = tk.Button(
                    frame, text="Save Values", command=self.save_values
                )
                save_button.grid(row=0, column=3, padx=5)

    def _update_plot_from_sliders(self, event: Optional[str] = None) -> None:
        """
        Update the plot when a slider value changes.
        Synchronize the entry fields with slider values.
        """
        values = [slider.get() for slider in self.sliders]
        self._draw_plot(*values)

        # Sync entry fields
        for entry, val in zip(self.entries, values):
            entry.delete(0, tk.END)
            entry.insert(0, str(val))

    def _update_plot_from_entry(self, event: Optional[Any] = None) -> None:
        """
        Update the plot when an entry field is modified (e.g. pressing <Return>).
        Sync the slider positions to match the new entry values.
        """
        try:
            values = [float(entry.get()) for entry in self.entries]
            for slider, val in zip(self.sliders, values):
                slider.set(val)
            self._draw_plot(*values)
        except ValueError:
            logger.error("Please enter valid numeric values in the entries.")

    # ---------------------------
    # Plotting
    # ---------------------------

    def _draw_plot(self, *args: float) -> None:
        """
        Clear the current figure and redraw the plot with the provided parameters.

        Parameters
        ----------
        *args : float
            Parameter values to pass to the potential function(s).
        """
        self.fig.clear()
        axis = self.fig.add_subplot(111)

        n_states = self.system.number_states
        disp_vector = np.array(self.system.displacement_vector[self.mode])
        db_abinitio = np.array(self.system.database_abinitio[self.mode])

        # Plot the reference data for each state
        for i in range(n_states):
            axis.scatter(disp_vector, db_abinitio[i], s=0.5)

        # Compute the min value from the second state's data to adjust y-limits
        if n_states > 1:
            min_value = db_abinitio[1].min() - 0.5
            max_value = db_abinitio[-1].min() + 0.5
        else:
            min_value = 0.0
            max_values = 8.0

        # Retrieve parameters for the potential
        function_type = self.system.diab_funct[self.mode][self.state]
        logger.info(
            "Mode: %d, State: %d, Diab func: %s, params: %s",
            self.mode, self.state, function_type, args
        )

        potential_fn = potential_functions.get(function_type)
        if potential_fn is None:
            logger.error("Unknown function type '%s' encountered.", function_type)
            axis.set_xlabel("Displacement [Q]")
            axis.set_ylabel(f"Energy [{self.system.units}]")
            self.canvas.draw()
            return

        e0 = self.system.energy_shift[self.state]
        omega = self.system.vib_freq[self.mode]
        total_sym_irrep = self.system.totally_sym_irrep
        sym_mode = self.system.symmetry_modes[self.mode]

        # Evaluate potential, possibly including kappa
        if kappa_compatible[function_type]:
            # Wrap the function to include kappa if needed
            def potential_fn_with_kappa(q, om, p):
                return (
                    linear_coupling(q, self.kappa)
                    + potential_fn(q, om, p)
                )
            y_vals = potential_fn_with_kappa(disp_vector, omega, args) + e0
        elif function_type in ["morse", "antimorse"] and self.state == 0:
            y_vals = potential_fn(disp_vector, args, gs=True) + e0
        else:
            y_vals = potential_fn(disp_vector, args) + e0

        axis.plot(disp_vector, y_vals, "r-")
        axis.set_xlabel("Displacement [Q]")
        axis.set_ylabel(f"Energy [{self.system.units}]")

        # Set typical plot limits based on state
        if self.state == 0:
            axis.set_ylim(self.PLOT_YLIM_STATE0)
            axis.set_xlim(self.PLOT_XLIM_STATE0)
        else:
            axis.set_ylim([min_value + self.PLOT_Y_OFFSET_OTHER_STATES[0], max_value + self.PLOT_Y_OFFSET_OTHER_STATES[1]])

        self.canvas.draw()