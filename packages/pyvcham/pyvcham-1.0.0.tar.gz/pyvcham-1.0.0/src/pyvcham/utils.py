"""
Utility functions for PyVCHAM package.
This module provides various utility functions for handling molecular geometries,
rotating geometries, encoding data to JSON, and processing VCHAM parameters.
"""

import json
import numpy as np
import tensorflow as tf

from .diabfunct import n_var
from .logging_config import get_logger

from typing import Union, List, Optional, Tuple, Any, Dict
from itertools import combinations_with_replacement, combinations, product
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

# Setup logging
logger = get_logger(__name__)

# --- Geometry Utilities ---

def eulerMatrix(xhi, theta, phi):
    """
    Generate a rotation matrix for Euler angles in ZYZ convention.
    This function constructs a 3x3 rotation matrix based on the provided Euler angles.

    Parameters
    ----------
    xhi : float
        Euler angle in radians for the first rotation about the Z-axis.
    theta : float
        Euler angle in radians for the second rotation about the Y-axis.
    phi : float
        Euler angle in radians for the third rotation about the Z-axis.

    Returns
    -------
    np.ndarray
        A 3x3 rotation matrix corresponding to the Euler angles in ZYZ convention.
    """
    Rz_xhi = np.array([
        [np.cos(xhi), -np.sin(xhi), 0],
        [np.sin(xhi),  np.cos(xhi), 0],
        [0,             0,              1]
    ])
    Ry_theta = np.array([
        [np.cos(theta),  0, np.sin(theta)],
        [0,             1,            0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])
    Rz_phi = np.array([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi),  np.cos(phi), 0],
        [0,             0,              1]
    ])
    return Rz_xhi @ Ry_theta @ Rz_phi

def rotate_geometry(geometry, xhi, theta, phi):
    """
    Rotate a 3D geometry using Euler angles in ZYZ convention.
    """
    geometry = np.atleast_2d(geometry)
    if geometry.shape[1] != 3:
        raise ValueError("Geometry must have shape (Natoms,3)")
    rotMat = eulerMatrix(xhi, theta, phi)
    rotated_vectors = (rotMat @ geometry.T).T
    if rotated_vectors.shape[0] == 1:
        rotated_vectors = rotated_vectors[0]
    rotated_vectors[np.abs(rotated_vectors) < 1e-10] = 0.0
    return rotated_vectors

def rotate_dipole_matrix(dipole_matrix, xhi, theta, phi):
    """
    Rotate a dipole moment matrix using Euler angles in ZYZ convention.
    """
    if dipole_matrix.shape[2] != 3:
        raise ValueError("The last dimension of dipole_matrix must be 3.")
    rotMat = eulerMatrix(xhi, theta, phi)
    dipole_matrix_lab = np.einsum('kl,ijl->ijk', rotMat, dipole_matrix)
    dipole_matrix_lab[np.abs(dipole_matrix_lab) < 1e-10] = 0.0
    return dipole_matrix_lab

# --- JSON Serialization Utilities ---

class _CustomEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for serializing TensorFlow tensors and NumPy arrays.
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (tf.Tensor, np.ndarray)):
            return obj.tolist()
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        return super().default(obj)

def _custom_json_dump(obj: Any, file, indent_level: int = 0) -> None:
    """
    Write a Python object to a file in JSON format with custom list formatting.
    """
    if isinstance(obj, (np.ndarray, tf.Tensor)):
        obj = obj.tolist()
    
    indent_str = ' ' * (indent_level * 2)
    
    if isinstance(obj, dict):
        file.write(indent_str + '{\n')
        items = list(obj.items())
        for i, (key, value) in enumerate(items):
            file.write(indent_str + '  ' + json.dumps(key) + ': ')
            _custom_json_dump(value, file, indent_level + 1)
            file.write(',\n' if i < len(items) - 1 else '\n')
        file.write(indent_str + '}')
    elif isinstance(obj, list):
        is_scalar_list = all(isinstance(item, (int, float, str, bool, type(None))) for item in obj)
        if is_scalar_list and obj:
            file.write('[' + ', '.join(json.dumps(item) for item in obj) + ']')
        else:
            file.write('[\n')
            for i, item in enumerate(obj):
                file.write(indent_str + '  ')
                _custom_json_dump(item, file, indent_level + 1)
                file.write(',\n' if i < len(obj) - 1 else '\n')
            file.write(indent_str + ']')
    else:
        file.write(json.dumps(obj, cls=_CustomEncoder))

# --- VCHAM Parameter Processing ---

def _process_parameters(param_name: str, vcham_params: List[tf.Variable],
                       count: int, n_var: int) -> Tuple[Optional[np.ndarray], int]:
    """
    Extract parameters from a tf.Variable object in vcham_params by name.
    """
    for param in vcham_params:
        if param.name.startswith(param_name):
            return param.numpy()[count : count + n_var], count + n_var
    return None, count

def _process_diagonal_parameters(mode_data, VCSystem, mode, vcham_param):
    """
    Process the diagonal parameters for a given mode.
    """
    counts = {"fn": 0, "kappa": 0}
    for state in range(VCSystem.number_states):
        function_type = VCSystem.diab_funct[mode][state]
        n_variables = n_var[function_type]
        state_data = {"state": state, "diab_funct": function_type}

        summary = VCSystem.summary_output[mode][state]
        if summary == "":
            params, counts["fn"] = _process_parameters("funct_param:0", vcham_param, counts["fn"], n_variables)
            state_data["parameters"] = params
        elif summary == "JT":
            params, counts["fn"] = _process_parameters("jt_on_param:0", vcham_param, counts["fn"], n_variables)
            if params is None or len(params) == 0:
                params, counts["fn"] = _process_parameters("jt_on_param_inactive:0", vcham_param, counts["fn"], n_variables)
                if params is not None and len(params) > 0:
                    kappa_params, _ = _process_parameters("jt_off_param_inactive:0", vcham_param, 0, n_variables)
                    state_data["kappa"] = kappa_params[0]
            if params is None or len(params) == 0:
                 params = mode_data["diagonal"][state - 1]["parameters"]
            state_data["parameters"] = params
            if state > 0 and mode_data["diagonal"][state - 1].get("kappa") is not None:
                state_data["kappa"] = -mode_data["diagonal"][state - 1].get("kappa")

        elif summary == "kappa":
            kappa, counts["kappa"] = _process_parameters("kappa_param:0", vcham_param, counts["kappa"], 1)
            params, counts["fn"] = _process_parameters("funct_param:0", vcham_param, counts["fn"], n_variables)
            state_data["parameters"] = params
            state_data["kappa"] = kappa[0]

        mode_data["diagonal"].append(state_data)

def _process_nondiagonal_parameters(mode_data, VCSystem, mode, vcham_param):
    """
    Process the non-diagonal parameters for a given mode.
    """
    lambdas_indexes = VCSystem.idx_dict["lambda"]
    jt_indexes_off = VCSystem.idx_dict["jt_off"]

    for param in vcham_param:
        if param.name.startswith("lambda_param:0"):
            mode_data["non-diagonal"] = {"idx": lambdas_indexes[mode], "lambda": param.numpy()}
        elif param.name.startswith("jt_off_param:0"):
            mode_data["non-diagonal"] = {"idx": jt_indexes_off[mode], "lambda": param.numpy()}

def VCSystem_to_json(VCSystem: Any, general_data: Dict[str, Any] = {},
                     output_name: str = "vcham_data.json",
                     rewrite: bool = False) -> None:
    """
    Convert a VCSystem object to JSON and save to a file.
    """
    data = []
    vcham_params = VCSystem.optimized_params

    for mode in range(VCSystem.number_normal_modes):
        mode_data: Dict[str, Any] = {"mode": mode, "diagonal": [], "non-diagonal": None}
        
        _process_diagonal_parameters(mode_data, VCSystem, mode, vcham_params[mode])
        _process_nondiagonal_parameters(mode_data, VCSystem, mode, vcham_params[mode])

        data.append(mode_data)

    VCSystem.lvc_data["lvcham"] = [data]
    output_data = {"general_data": general_data, "vcham_data": VCSystem.lvc_data}

    output_path = Path(output_name)
    if output_path.is_file() and not rewrite:
        output_name = output_name.replace(".json", "_new.json")
    elif rewrite:
        logger.info(f"Warning: Overwriting existing file {output_name}")

    with open(output_name, "w") as json_file:
        _custom_json_dump(output_data, json_file)
    logger.info(f"Data successfully saved to {output_name}")


@dataclass
class Molecule:
    """
    Represents a molecule in the VCHAM system.

    Attributes
    ----------
    molecule_idx : int
        Index of the molecule in the system.
    interacting_states : Optional[List[int]]
        List of interacting states for the molecules.
    CM : np.ndarray
        Center of mass of the molecule in Bohr units.
    rot_angles : Tuple[float, float, float]
        Euler angles for the molecule's rotation (degrees).
    """
    def __init__(self, molecule_idx: int, interacting_states: Optional[List[int]] = None,
                 CM: np.ndarray = None, rot_angles: Tuple[float, float, float] = None):
        self.molecule_idx = molecule_idx
        self.interacting_states = interacting_states or []
        self.CM = CM if CM is not None else np.array([0.0, 0.0, 0.0])
        self.rot_angles = rot_angles if rot_angles is not None else (0.0, 0.0, 0.0)

    def __post_init__(self):
        logger.info("Units are in Bohr for the CM and degrees for the Euler Angles.")
        if not isinstance(self.CM, np.ndarray):
            raise ValueError("CM must be a numpy array.")
        if len(self.CM) != 3:
            raise ValueError("CM must be a 3D vector.")
        if not isinstance(self.rot_angles, tuple) or len(self.rot_angles) != 3:
            raise ValueError("rot_angles must be a tuple of three angles.")
        logger.info(f"Initialized Molecule {self.molecule_idx} with CM: {self.CM} and Euler angles (degrees) -  χ: {self.rot_angles[0]}, θ: {self.rot_angles[1]}, φ: {self.rot_angles[2]}")


def _read_data_blocks_json(infile: str) -> Tuple[dict, dict, str]:
    """
    Reads a JSON file from 'infile' and returns general_data and vcham_data blocks.
    Also checks units for potential mismatches (logs a warning if found).

    Parameters
    ----------
    infile : str
        JSON file path.

    Returns
    -------
    Tuple[dict, dict, str]
        general_data, vcham_data, master_units
    """
    if not isinstance(infile, str):
        raise ValueError("Input file must be a string representing a JSON file path.")

    with open(infile, "r") as f:
        json_data = json.load(f)
    
    try:
        general = json_data["general_data"]
        vcham = json_data["vcham_data"]
    except KeyError as e:
        raise ValueError(f"Missing key in JSON data: {e}")

    units = vcham["units"]
    units_lower = [unit.lower() for unit in units]
    if len(set(units_lower)) > 1:
        logger.warning(
            f"Units mismatch found in {infile}. "
            f"Units: {units_lower}. Using the first one: {units[0]}"
        )
    master_units = units[0]

    return general, vcham, master_units


def _write_header_section(fh: Any) -> None:
    """
    Writes the MCTDH header section to the file handle 'fh'.
    """
    fh.write(
        "OP_DEFINE-SECTION\n"
        "    TITLE\n"
        "        MCTDH-Operator-file created by PyVCHAM\n"
        f"        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "    END-TITLE\n"
        "END-OP_DEFINE-SECTION\n\n"
    )

def _compute_morse_offset(parameters: List[float]) -> float:
    """
    Computes the offset for Morse or Anti-Morse potentials.

    Parameters
    ----------
    parameters : List[float]
        List of parameters [D, alpha, r0] for the potential.

    Returns
    -------
    float
        Computed offset value.
    """
    return -parameters[0] * (np.exp(parameters[1] * parameters[2]) - 1)**2


def _write_parameter_section(
    fh: Any,
    data_blocks: dict,
    master_units: str
) -> Optional[np.ndarray]:
    """
    Writes the PARAMETER-SECTION:
      - Frequencies (omega_i)
      - Energies (E_i)
      - Diabatic curves with parameters, kappa/lambda, placeholders, ...

    Parameters
    ----------
    fh : Any
        File handle to write to.
    data_blocks : dict
        vcham_data block containing simulation parameters.
    master_units : str
        Unit to use for parameters.

    Returns
    -------
    None
    """
    nmodes = data_blocks["number_normal_modes"]
    nstates = data_blocks["number_states"]

    fh.write("PARAMETER-SECTION\n\n# frequencies\n")

    vib_freqs = data_blocks["vib_freq"]
    for idx_mol, nmode in enumerate(nmodes):
        for mode in range(nmode):
            freq = vib_freqs[idx_mol][mode]
            fh.write(f"omega_m{idx_mol}M{mode + 1}    =    {freq:.6f} , {master_units}\n")

    fh.write("\n# Energies\n")

    e_shifts = data_blocks["energy_shift"]
    for idx_mol, mol in enumerate(nstates):
        for state in range(mol):
            energy = e_shifts[idx_mol][state]
            fh.write(f"E_m{idx_mol}_S{state + 1}    =    {energy:.6f} , {master_units}\n")

    fh.write("\n# Diabatic curves with parameters\n")

    vcham_modes = data_blocks["lvcham"]

    for idx_mol, nmode in enumerate(nmodes):
        for mode in range(nmode):
            diag_list = vcham_modes[idx_mol][mode]["diagonal"]
            for state in range(nstates[idx_mol]):
                diag = diag_list[state]
                diab_funct = diag["diab_funct"]
                parameters = diag["parameters"]
                for idx_param, param in enumerate(parameters):
                    line = (
                        f"m{idx_mol}M{mode+1}S{state+1}_{idx_param+1}"
                        f"    =    {param:.6f}"
                    )
                    if idx_param == 0 or diab_funct in ["ho", "quartic"]:
                        fh.write(line + f" , {master_units}\n")
                    elif diab_funct in ["morse", "antimorse"] and idx_param == 2:
                        fh.write(line + "\n")
                        offset = _compute_morse_offset(parameters)
                        line = (
                            f"m{idx_mol}M{mode+1}S{state+1}_{idx_param+2}"
                            f"    =    {offset:.6f} , {master_units}\n"
                        )
                        fh.write(line)
                    else:
                        fh.write(line + "\n")
                fh.write("\n")
        fh.write("# on-diagonal linear coupling constants (kappa)\n")
        for mode in range(nmode):
            diag_list = vcham_modes[idx_mol][mode]["diagonal"]
            for state in range(nstates[idx_mol]):
                kappa = diag_list[state].get("kappa")
                if kappa is not None:
                    fh.write(
                        f"kappa_m{idx_mol}M{mode+1}S{state + 1}"
                        f"    =    {kappa:.6f} , {master_units}\n"
                    )

        fh.write("\n# off-diagonal linear coupling constants (lambda)\n")
        for mode in range(nmode):
            non_diag = vcham_modes[idx_mol][mode]["non-diagonal"]
            if non_diag:
                indexes = non_diag["idx"]
                lambdas = non_diag["lambda"]
                for idx_pair, (st1, st2) in enumerate(indexes):
                    lam_val = lambdas[idx_pair]
                    fh.write(
                        f"lam_m{idx_mol}M{mode + 1}S{st1 + 1}S{st2 + 1}"
                        f" = {lam_val:.6f} , {master_units}\n"
                    )
        fh.write("\n")

    fh.write("\n# on-diagonal bilinear coupling constants (gamma)\n")
    fh.write("# Third order quad-lin and cube terms (iota)\n")
    fh.write("# off-diagonal bilinear coupling constants (mu)\n")
    fh.write("end-parameter-section\n\n")

def _write_labels_section(fh: Any, data_blocks: dict) -> None:
    """
    Writes the LABELS-SECTION for all blocks (Morse/Anti-Morse).
    """
    nmodes = data_blocks["number_normal_modes"]
    nstates = data_blocks["number_states"]
    vcham_modes = data_blocks["lvcham"]

    fh.write("LABELS-SECTION\n# Diabatic function labels\n")

    for idx_mol, nmode in enumerate(nmodes):
        for mode in range(nmode):
            diag_list = vcham_modes[idx_mol][mode]["diagonal"]
            for state in range(nstates[idx_mol]):
                diab_funct = diag_list[state]["diab_funct"]
                if diab_funct in ["morse", "antimorse"]:
                    fh.write(
                        f"vm{idx_mol}M{mode + 1}S{state + 1} = morse1["
                        f"m{idx_mol}M{mode+1}S{state+1}_1,"
                        f"m{idx_mol}M{mode+1}S{state+1}_2,"
                        f"m{idx_mol}M{mode+1}S{state+1}_3,"
                        f"m{idx_mol}M{mode+1}S{state+1}_4"
                        "]\n"
                    )
    fh.write("end-labels-section\n\n")


def _write_hamiltonian_section(fh: Any, data_blocks: dict) -> None:
    """
    Writes the HAMILTONIAN-SECTION for all blocks, using proper offset logic.
    """
    fh.write("HAMILTONIAN-SECTION\n")
    fh.write("------------------------------------------------------------------\n\n")
    
    total_modes = sum(data_blocks["number_normal_modes"])
    number_molecules = len(data_blocks["number_normal_modes"])
    
    max_length = 60
    mode_header = " ".join(f"v{m+1} |" for m in range(total_modes))
    header_prefix = "modes | "

    current_line = header_prefix
    lines = []
    segments = mode_header.split(" | ")
    for i, segment in enumerate(segments):
        if len(current_line) + len(segment) > max_length:
            lines.append(current_line.strip())
            current_line = header_prefix + segment
        else:
            if i > 0:
                current_line += " | "
            current_line += segment

    if number_molecules == 1:
        lines.append(current_line.strip() + " el")
    else:
        lines.append(current_line.strip() + " el1")
        current_line = header_prefix
        elec = ""
        if number_molecules > 1:
            for mol in range(number_molecules):
                if mol == number_molecules - 1:
                    elec += f" el{mol+1}"
                elif mol == 0:
                    pass
                else:
                    elec += f" el{mol+1} |"
            lines.append(current_line.strip() + elec)

    for line in lines:
        fh.write(line + "\n")
    fh.write("------------------------------------------------------------------\n\n")

    fh.write("# Kinetic Energy\n")
    mode_offset = 0
    vcham_modes = data_blocks["lvcham"]
    nstates = data_blocks["number_states"]
    for idx_mol, nmode in enumerate(data_blocks["number_normal_modes"]):
        fh.write(f"\n# Molecule {idx_mol} \n\n")
        for mode in range(nmode):
            total_mode = mode_offset + mode
            fh.write(f"omega_m{idx_mol}M{mode + 1}    |{total_mode + 1}    KE\n")
        
        fh.write("\n# Harmonic term\n")
        for mode in range(nmode):
            total_mode = mode_offset + mode
            diag_list = vcham_modes[idx_mol][mode]["diagonal"]
            diab_functs = [d["diab_funct"] for d in diag_list]
            if any(f in ["ho", "quartic"] for f in diab_functs):
                fh.write(f"0.5*omega_m{idx_mol}M{mode + 1}    |{total_mode + 1}    q^2\n")
        
        fh.write("\n# Electronic States\n")
        for state in range(nstates[idx_mol]):
            fh.write(
                f"E_m{idx_mol}_S{state + 1}    |{total_modes + 1 + idx_mol}    S{state + 1}&{state + 1}\n"
            )

        fh.write("\n# Lambda\n")
        for mode in range(nmode):
            total_mode = mode_offset + mode
            non_diag = vcham_modes[idx_mol][mode]["non-diagonal"]
            if non_diag:
                indexes = non_diag["idx"]
                for i, (st1, st2) in enumerate(indexes):
                    fh.write(
                        f"lam_m{idx_mol}M{mode + 1}S{st1 + 1}S{st2 + 1}"
                        f"    |{total_mode + 1}    q    |{total_modes + 1 + idx_mol}"
                        f"    S{st1 + 1}&{st2 + 1}\n"
                    )

        fh.write("\n# Kappa\n")
        for mode in range(nmode):
            total_mode = mode_offset + mode
            diag_list = vcham_modes[idx_mol][mode]["diagonal"]
            for state in range(nstates[idx_mol]):
                kappa = diag_list[state].get("kappa")
                if kappa is not None:
                    fh.write(
                        f"kappa_m{idx_mol}M{mode+1}S{state + 1}"
                        f"    |{total_mode + 1}    q    |{total_modes + 1 + idx_mol}"
                        f"    S{state + 1}&{state + 1}\n"
                    )
        fh.write("\n# Harmonic potential\n")
        for mode in range(nmode):
            total_mode = mode_offset + mode
            diag_list = vcham_modes[idx_mol][mode]["diagonal"]
            for state in range(nstates[idx_mol]):
                diag = diag_list[state]
                if diag["diab_funct"] == "ho":
                    fh.write(
                        f"{0.5:.6f}*m{idx_mol}M{mode+1}S{state+1}_1"
                        f"    |{total_mode + 1}    q^2"
                        f"    |{total_modes + 1 + idx_mol}    S{state + 1}&{state + 1}\n"
                    )

        fh.write("\n# Quartic potential\n")
        for mode in range(nmode):
            total_mode = mode_offset + mode
            diag_list = vcham_modes[idx_mol][mode]["diagonal"]
            for state in range(nstates[idx_mol]):
                diag = diag_list[state]
                if diag["diab_funct"] == "quartic":
                    fh.write(
                        f"{0.5:.6f}*m{idx_mol}M{mode+1}S{state+1}_1"
                        f"    |{total_mode + 1}    q^2"
                        f"    |{total_modes + 1 + idx_mol}    S{state + 1}&{state + 1}\n"
                    )
                    fh.write(
                        f"{(1/24):.6f}*m{idx_mol}M{mode+1}S{state+1}_2"
                        f"    |{total_mode + 1}    q^4"
                        f"    |{total_modes + 1 + idx_mol}    S{state + 1}&{state + 1}\n"
                    )

        fh.write("\n# Morse/Anti-Morse potential\n")
        for mode in range(nmode):
            total_mode = mode_offset + mode
            diag_list = vcham_modes[idx_mol][mode]["diagonal"]
            for state in range(nstates[idx_mol]):
                diag = diag_list[state]
                if diag["diab_funct"] in ["morse", "antimorse"]:
                    fh.write(
                        f"1.0    |{total_mode + 1}    "
                        f"vm{idx_mol}M{mode + 1}S{state + 1}"
                        f"    |{total_modes + 1 + idx_mol}    S{state + 1}&{state + 1}\n"
                    )
        # Update the mode offset for the next molecule
        mode_offset += nmode

    # Check for interactions and that is not empty list
    if "interactions" in data_blocks and data_blocks["interactions"]:
            logger.info("Interactions found!")
            if "dipole_interaction" in data_blocks["interactions"][0]:
                dipole_interactions = data_blocks["interactions"][0]["dipole_interaction"]
                logger.info("Dipole interactions found!")
                for interaction in dipole_interactions:
                    mol1 = interaction["molecules"][0]
                    mol2 = interaction["molecules"][1]
                    fh.write(f"\n\n# Dipole interaction for Molecules {mol1}-{mol2}\n")
                    for idx, dipole in enumerate(interaction["values"]):
                        s1, s2 = interaction['states'][idx][0]
                        s3, s4 = interaction['states'][idx][1]
                        el1 = total_modes + 1 + mol1
                        el2 = total_modes + 1 + mol2
                        fh.write(f"\n{dipole:0.8f} |{el1} S{s1+1}&{s2+1} |{el2} S{s3+1}&{s4+1}")
    else:
            logger.info("No interactions found.")

    fh.write("\nEND-HAMILTONIAN-SECTION\n\n")
    fh.write("END-OPERATOR\n")


def json_to_mctdh(infile: str, outfile: str) -> None:
    """
    Reads a JSON file and writes a single MCTDH operator file.

    Parameters
    ----------
    infile : str
        JSON file path.
    outfile : str
        Output MCTDH operator file path.
    """
    general_data, data_blocks, master_units = _read_data_blocks_json(infile)

    try:
        with open(outfile, "w") as fh:
            _write_header_section(fh)
            _write_parameter_section(fh, data_blocks, master_units)
            _write_labels_section(fh, data_blocks)
            _write_hamiltonian_section(fh, data_blocks)
        logger.info(f"MCTDH operator file successfully written to: {outfile}")
    except IOError as e:
        logger.error(f"Error writing MCTDH file: {e}")
        raise


def merge_jsons(
    infiles: Union[str, List[str]],
    outfile: str,
    molecules: List[Molecule] = None,
    interactions: Optional[Any] = None,
    rewrite: bool = False
) -> None:
    """
    Reads multiple JSON files and writes a single JSON file file by concatenating
    them with proper indexing offsets and possible coupling terms coming from the functions
    specified in the functions list.

    Parameters
    ----------
    infiles : Union[str, List[str]]
        One or more JSON file paths.
    outfile : str
        Output MCTDH operator file path.
    """
    if isinstance(infiles, str):
        infiles = [infiles]

    data_blocks = []
    general_data = []
    all_units = []

    for path in infiles:
        with open(path, "r") as f:
            json_data = json.load(f)
        general = json_data["general_data"] # General data is being merged here
        vcham = json_data["vcham_data"]
        general_data.append(general)
        data_blocks.append(vcham)
        all_units.append(vcham["units"])

    logger.info(f"Reading {len(data_blocks)} JSON files and merging them.")

    # Merge the two jsons

    merged_data = {
        "number_normal_modes": data_blocks[0]["number_normal_modes"],
        "number_states": data_blocks[0]["number_states"],
        "units": data_blocks[0]["units"],
        "vib_freq": data_blocks[0]["vib_freq"],
        "energy_shift": data_blocks[0]["energy_shift"],
        "coupling_with_gs": data_blocks[0]["coupling_with_gs"],
        "symmetry_point_group": data_blocks[0]["symmetry_point_group"],
        "totally_sym_irrep": data_blocks[0]["totally_sym_irrep"],
        "symmetry_modes": data_blocks[0]["symmetry_modes"],
        "elements": data_blocks[0]["elements"],
        "reference_geometry": data_blocks[0]["reference_geometry"],
        "lvcham": data_blocks[0]["lvcham"],
        "dipole_matrix": data_blocks[0]["dipole_matrix"],

        "molecules": [],
        "interactions": []
    }

    for idx, block in enumerate(data_blocks[1:], start=1):
        merged_data["number_normal_modes"].append(block["number_normal_modes"][0])
        merged_data["number_states"].append(block["number_states"][0])
        merged_data["units"].append(block["units"][0])
        merged_data["vib_freq"].append(block["vib_freq"][0])
        merged_data["energy_shift"].append(block["energy_shift"][0])
        merged_data["coupling_with_gs"].append(block.get("coupling_with_gs")[0])
        merged_data["symmetry_point_group"].append(block.get("symmetry_point_group")[0])
        merged_data["totally_sym_irrep"].append(block.get("totally_sym_irrep")[0])
        merged_data["symmetry_modes"].append(block.get("symmetry_modes")[0])
        merged_data["elements"].append(block["elements"][0])
        merged_data["reference_geometry"].append(block.get("reference_geometry")[0])
        merged_data["dipole_matrix"].append(block.get("dipole_matrix")[0])

        merged_data["lvcham"].append(block["lvcham"][0])
    # print(f"Geometry: {merged_data['reference_geometry']}")

    # Add Molecule objects to the merged data
    if molecules is not None:
        for molecule in molecules:
            if not isinstance(molecule, Molecule):
                raise ValueError("Molecules must be instances of the Molecule class.")
            # Check if the molecule is present in the block
            if molecule.molecule_idx >= len(merged_data["lvcham"]):
                raise ValueError(f"Molecule index {molecule.molecule_idx} out of range.")
            # Print the molecule's new geometry
            geometry = np.array(merged_data["reference_geometry"][molecule.molecule_idx])

            logger.info(f"\nMolecule {molecule.molecule_idx} new geometry in the fixed lab frame: \n{rotate_geometry(geometry, *molecule.rot_angles)} \n")
            mol_dict = {
                "idx": molecule.molecule_idx,
                "CM": molecule.CM,
                "rot_angles": molecule.rot_angles
            }
            merged_data["molecules"].append(mol_dict)
            

    # There could be several types of interactions, for dipole interactions
    # we need to assure that the dipole matrix is present

    if interactions is not None:
        data_interactions = {}
        for interaction in interactions:
            if isinstance(interaction, DipoleInteraction):
                # If the key dipole_interaction is not present in data_interactions, create it
                if "dipole_interaction" not in data_interactions:
                    data_interactions["dipole_interaction"] = []

                # Check if the dipole matrix is present in the block
                if len(merged_data["dipole_matrix"]) == 0:
                    raise ValueError(f"Dipole matrix is needed for {interaction}.")
                # Calculate the dipole interaction for the given pairs of molecules
                all_interactions = interaction._calculate(merged_data)
                # Update the dipole_interaction key with the new data
                data_interactions["dipole_interaction"].append(all_interactions)
        merged_data["interactions"].append(data_interactions)

                
    total_merged_data = {
        "general_data": general_data,
        "vcham_data": merged_data
    }


     # Check for file existence and handle rewriting
    output_path = Path(outfile)
    if output_path.is_file():
        if rewrite:
            logger.info(f"Warning: Overwriting existing file {outfile}")
        else:
            outfile = outfile.replace(".json", "_new.json")

    with open(outfile, "w") as json_file:
        _custom_json_dump(total_merged_data, json_file)
    logger.info(f"Data successfully saved to {outfile}")

@dataclass
class DipoleInteraction:
    """
    A class representing dipole interactions between pairs of molecules.

    Attributes
    ----------
    molecules : List['Molecule']
        List of Molecule objects involved in the dipole interactions.
    pairs_interacting : Optional[List[Tuple[int, int]]]
        List of tuples specifying which pairs of molecules (by their indices in the `molecules` list)
        interact via dipole interactions. If None, all possible unique pairs are used.
    """

    def __init__(self, molecules: List['Molecule'], pairs_interacting: Optional[List[Tuple[int, int]]] = None):
        self.molecules = molecules
        self.pairs_interacting = pairs_interacting or list(combinations(range(len(self.molecules)), 2))

    def _calculate(self, data) -> None:
        """
        Calculate dipole interactions for the specified pairs of molecules.
        """

        # Dipole interaction calculation for fixed R
        molecules_idx, states, values = self._calculate_dipoles_pair(data, self.molecules[0], self.molecules[1])

        return {"molecules": molecules_idx, "states": states, "values": values}
    def _calculate_dipoles_pair(self,
        data_blocks: List[dict],
        molecule_i: Molecule,
        molecule_j: Molecule
    ) -> List[float]:
        """
        Compute dipole interactions between two molecules.

        Parameters
        ----------
        fh : file handle
            File handle to write output.
        data_blocks : List[dict]
            Data blocks from JSON files.
        molecule_i : Molecule
            Dipole settings for molecule i.
        molecule_j : Molecule
            Dipole settings for molecule j.

        Returns
        -------
        List[float]
            List of computed dipole interaction values.
        """
        molecule_i_idx = molecule_i.molecule_idx
        molecule_j_idx = molecule_j.molecule_idx
        molecules_idx = [molecule_i.molecule_idx, molecule_j.molecule_idx]
        logger.info(f"Calculating dipole interaction for pair Molecule{molecule_i_idx} - Molecule{molecule_j_idx}\n")
        len_mol = len(data_blocks["molecules"])

        if molecule_i_idx >= len_mol or molecule_j_idx >= len_mol:
            raise ValueError(f"Invalid molecule indices {molecule_i_idx} or {molecule_j_idx} for dipole calc.")
        
        nstates1 = data_blocks["number_states"][molecule_i_idx]
        nstates2 = data_blocks["number_states"][molecule_j_idx]
        dipoles1 = data_blocks["dipole_matrix"][molecule_i_idx]
        dipoles2 = data_blocks["dipole_matrix"][molecule_j_idx]

        dipoles1 = np.array(dipoles1)
        dipoles2 = np.array(dipoles2)

        sel_states1 = molecule_i.interacting_states or list(range(nstates1))
        sel_states2 = molecule_j.interacting_states or list(range(nstates2))

        mu_mol1_rot = rotate_dipole_matrix(dipoles1, *molecule_i.rot_angles)
        mu_mol2_rot = rotate_dipole_matrix(dipoles2, *molecule_j.rot_angles)

        print(f"Rotated dipole matrix for molecule {molecule_i_idx}: \n{mu_mol1_rot}")
        print(f"Rotated dipole matrix for molecule {molecule_j_idx}: \n{mu_mol2_rot}")

        pairs1 = list(combinations_with_replacement(sel_states1, 2))
        pairs2 = list(combinations_with_replacement(sel_states2, 2))

        cm1 = molecule_i.CM
        cm2 = molecule_j.CM

        # Calculate displacement vector
        r_vec = cm2 - cm1
        r_norm = np.linalg.norm(r_vec)
        if r_norm < 1e-10:
            logger.error("Distance between center of masses is too small, cannot proceed.")
            raise ValueError("Distance between center of masses is too small, cannot proceed.")
    
        u = r_vec / r_norm
        distance_factor = 1 / r_norm**3

        # Storage for results
        interactions = {}
        # Calculate all unique interaction terms
        for (i,j), (k,l) in product(pairs1, pairs2):
            mu1 = mu_mol1_rot[i,j,:]
            mu2 = mu_mol2_rot[k,l,:]
            
            # Dot products
            mu1_dot_mu2 = np.dot(mu1, mu2)
            mu1_dot_u = np.dot(mu1, u)
            mu2_dot_u = np.dot(mu2, u)

            first_term = mu1_dot_mu2
            second_term = 3 * mu1_dot_u * mu2_dot_u
            # print(f"mu1_dot_mu2: {mu1_dot_mu2}, mu1_dot_u: {mu1_dot_u}, mu2_dot_u: {mu2_dot_u}, First term: {first_term}, Second term: {second_term}")
            # print(f"First term: {first_term}, Second term: {second_term}")
            
            # Dipole-dipole interaction formula
            interaction = distance_factor * (mu1_dot_mu2 - 3 * mu1_dot_u * mu2_dot_u)
            
            interactions[((i,j), (k,l))] = interaction

        indexes = list(interactions.keys())
        values = list(interactions.values())
        # logger.info(f"Indexes: {indexes}")
        # logger.info(f"Values: {values}")

        return molecules_idx, indexes, values
