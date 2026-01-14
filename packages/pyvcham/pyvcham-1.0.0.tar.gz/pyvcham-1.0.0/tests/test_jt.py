import vcham
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def test_jt():
    """Test function to create a simple model with a Jahn-Teller effect and two states, and then create a supersystem with two identical subsystems.
    This function simulates the Jahn-Teller effect in a linear molecule (Li3) with three normal modes and two electronic states (ground state and core-excited state).
    It processes ab initio data for the normal modes, initializes the vibrational coupling Hamiltonian, and optimizes the parameters.
    Finally, it saves the system data to a JSON file and generates an MCTDH operator file.
    """
    # Import the necessary modules
    # Define the number of states and normal modes
    number_states = 2
    number_normal_modes = 3

    all_q = []
    all_data = []


    # Define the normal modes to process
    normal_modes_to_process = [1, 1, 3]
    # This is done because the first two modes are degenerate (1, 1) and the third mode is different (3).

    # Loop over selected normal modes
    for normal_mode in normal_modes_to_process:
        mode_data = []
        
        # For each state (root 1 for ground state, root 2 for core-excited in this case)
        for root in range(1, 3):
            # Construct the filename and load the data
            filename = f'Examples/li3/li3_abinitio/gs{root}_v{normal_mode}.dat'
            data = np.genfromtxt(filename)
            # Assume data columns: first column = displacement (x), second column = energy (y)
            displacements = data[:, 0] / 10  # Scale displacement as needed
            energies = data[:, 1]
            
            # Create a DataFrame for clarity (optional)
            df = pd.DataFrame({'disp': displacements, 'gs': energies})
            # Shift the energies and convert from atomic units to eV
            adjusted_energies = (df["gs"].to_numpy() + 22.35342994) * vcham.constants.AU_TO_EV
            mode_data.append(adjusted_energies)
        
        # Convert the data for this mode to a numpy array and store the displacement vector
        all_data.append(np.array(mode_data))
        all_q.append(df["disp"].to_numpy())

    # The dimensions of the all_q and all_data lists are:
    # all_q: (number_normal_modes, number of displacements)
    # all_data: (number_normal_modes, number_states, number of displacements)

    # Define vibrational frequencies in cm^-1 and convert to eV
    vib_freq = np.array([389.55, 389.55, 308.52]) * vcham.constants.CM1_TO_AU * vcham.constants.AU_TO_EV

    # Define Jahn-Teller effects
    jt_effects = [
        {
            'mode': 0,                 # Normal mode index where the JT effect is active
            'state_pairs': [(0, 1)],   # State pair(s) coupled by the JT effect
            'types': ['Exe'],          # JT effect type(s)
            'active': True             # This mode is actively optimized
        },
        {
            'mode': 1,                 # Another normal mode where the same JT effect applies
            'state_pairs': [(0, 1)],   # Same state pairs as in mode 0
            'types': ['Exe'],          # Same JT type
            'active': False,           # This mode is inactive; parameters will be copied from mode 0
            'source': 0                # Indicates that parameters from mode 0 should be reused
        }
    ]

    # Define diabatic function types for each mode based on the abinitio data.
    # Antimorse means that the asymptotic behavior is at negative displacement.
    diab_f_each_mode = ["ho", "ho", "antimorse"]
    # For each mode, replicate the chosen diabatic function for all states.
    diabatic_functions = [[mode_type] * number_states for mode_type in diab_f_each_mode]

    # Create the VCSystem object
    system = vcham.VCSystem(
        vc_type="linear",
        units="eV",
        number_normal_modes=3,  # For HCCF: 3N-5 vibrational modes
        number_states=2,        # Ground state + 1 core-excited state (2 states total)
        coupling_with_gs=True,  # Core-excitation: gs-ce couplings are (or are not) accounted
        symmetry_point_group="Cs",
        symmetry_states=["A'", "A''"],
        symmetry_modes=["A''", "A'", "A'"],
        vib_freq=vib_freq,
        diab_funct=diabatic_functions,
        displacement_vector=all_q,
        database_abinitio=all_data,
        jt_effects=jt_effects
    )
    # Note: Energy shifts are nonzero because of the calculation issues in the abinitio data (the distances are not optimized for the method).

    # Initialize the LVC Hamiltonian for each normal mode
    # and optimize the parameters

    for mode in range(system.number_normal_modes):
        model = vcham.LVCHam(normal_mode=mode, VCSystem=system, nepochs=5000)
        model.initialize_params()
        model.initialize_loss_function()
        model.optimize()

    # Define general system information for output
    general_data = {
        "molecule": "Li3",
        "calculation_info": "Ground state and first excited state",
        "method": "CASSCF(3,7)",
        "basis": "cc-pvtz",
        "software": "OpenMolcas",
        "additional_info": "-"
    }
    # Add the reference geometry to the system
    ref_geom = "Examples/li3/li3_abinitio/geo_v1_00.xyz"
    system.add_geometry(ref_geom)

    # Define the JSON filename for saving the VCSystem data
    import os
    os.makedirs("tests/result_test", exist_ok=True)  # Ensure the directory exists
    filename_json = "tests/result_test/lvc_li3.json"

    # Convert the VCSystem to JSON and save it
    vcham.utils.VCSystem_to_json(system, general_data, filename_json, rewrite=True)

    # Define the output operator filename
    output_op = "tests/result_test/lvc_li3.op"

    # Generate the MCTDH operator file from the JSON data
    vcham.utils.json_to_mctdh(infile=filename_json, outfile=output_op)

if __name__ == "__main__":
    test_jt()
    print("Test completed successfully.")