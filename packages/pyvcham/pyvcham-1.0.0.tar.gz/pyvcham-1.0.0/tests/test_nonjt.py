import vcham
import numpy as np
import matplotlib.pyplot as plt
import json  
def test_nonjt():
    """Test function to create a simple model with a single normal mode and two states, and then create a supersystem with two identical subsystems.
    """ 
    # Create a database in eV with all the abinitio data
    step = 10
    q = np.arange(-100, 100 + step, step)
    nmodes = 6
    data_gs = []
    data_val = []
    data_carbon = []
    all_q = []

    path  = "Examples/model_2_lvc/abinitio_data/"
    min_scf = np.array(json.load(open(path + "geo_v1_00.json"))["ground_state"]["scf_energy"])
    min_mp2 = np.array(json.load(open(path + "geo_v1_00.json"))["ground_state"]["mp2_correction"])
    min_mp3 = np.array(json.load(open(path + "geo_v1_00.json"))["ground_state"]["mp3_correction"])
    min_gs = min_scf + min_mp2 + min_mp3

    for mode in range(1, nmodes+1):
        temp_gs = []
        temp_val = []
        temp_carbon = []
        temp_q = []
        for disp in q:
            geo = f"geo_v{mode}_{disp:02d}"
            path2 = f"{path}{geo}.json"
            data = json.load(open(path2))
            scf = data["ground_state"]["scf_energy"]
            mp2 = data["ground_state"]["mp2_correction"]
            mp3 = data["ground_state"]["mp3_correction"]
            gs_energy = scf + mp2 + mp3
            val = data["valence"]["excitation_energy"]
            carbon = data["carbon_core"]["excitation_energy"]

            # gs_energy should be below a threshold
            if gs_energy - min_gs < 0.4:
                temp_gs.append(gs_energy)
                temp_val.append(val)
                temp_carbon.append(carbon)
                temp_q.append(disp)

        temp_gs = np.array(temp_gs)
        temp_val = np.array(temp_val)
        temp_carbon = np.array(temp_carbon)
        temp_q = np.array(temp_q)

        temp_val = np.transpose(temp_val, (1,0))
        temp_val = ((temp_val + temp_gs) - min_gs)* vcham.constants.AU_TO_EV

        temp_carbon = np.transpose(temp_carbon, (1,0))
        temp_carbon = ((temp_carbon + temp_gs) - min_gs)* vcham.constants.AU_TO_EV
        temp_gs = (temp_gs - min_gs)* vcham.constants.AU_TO_EV


        all_q.append(temp_q)
        data_gs.append(temp_gs)
        data_val.append(temp_val)
        data_carbon.append(temp_carbon)

    data_pyvcham = []
    q_pyvcham = []
    for mode in range(nmodes):
        data_mode = []
        data_mode.append(data_gs[mode])
        for state in range(5):
            data_mode.append(data_val[mode][state])
        q_pyvcham.append(np.array(all_q[mode])/10)
        data_pyvcham.append(np.array(data_mode))

    data_pyvcham[2][1] = data_pyvcham[2][1] + 0.3 *q_pyvcham[2]

    # Creating the VC system object
    vib_freq = np.array([1113.0039]) * vcham.constants.CM1_TO_AU * vcham.constants.AU_TO_EV  # in eV

    # Guess diabatic function for each mode
    diab_f_each_mode = ["morse"]
    diab_funct_mode = [[mode] * 2 for mode in diab_f_each_mode]

    system = vcham.VCSystem(
        vc_type= "linear",
        units="eV",
        number_normal_modes=1,  
        number_states=2,         # GS + 1 excited state
        coupling_with_gs=True, 
        symmetry_point_group="Cs",
        symmetry_states = ["A'", "A''"],
        symmetry_modes = [ "A'"],
        vib_freq= vib_freq,  # to eV
        diab_funct= diab_funct_mode,
        displacement_vector= [q_pyvcham[2]],
        database_abinitio=[data_pyvcham[2][:2]],
        
    )

    # Setting up the model parameters

    for mode in range(system.number_normal_modes):
        model = vcham.LVCHam(normal_mode=mode,VCSystem=system,nepochs=7000)
        model.initialize_params()
        model.initialize_loss_function()
        model.optimize()


    # Defining the geometry of the system
    geometry = [("X", [0,0,-0.5]),  # X means Ghost atom
                ("X", [0,0,0.5])]

    # Adding the geometry to the system
    system.add_geometry(geometry)

    # Defining the general data of the system
    general_data = {
        "molecule": "diatomic model",
        "calculation_info": "Valence excitation",
    }
    # Defining the dipole matrix
    dipole_matrix = np.array([
        [[0, 0, 0], [0, 0, 1]],  
        [[0, 0, 1], [0, 0, 0]]    
    ])
    # The dipole matrix size should be (number_states, number_states, 3). The last dimension corresponds to the x, y, z components of the dipole moment.
    # Adding the dipole matrix to the system
    system.add_dipole_matrix(dipole_matrix)

    # Saving the system to a JSON file and converting it to MCTDH format
    name = "tests/result_test/model_sigma_plus"
    # Create the directory if it does not exist
    import os
    if not os.path.exists("tests/result_test"):
        os.makedirs("tests/result_test")
    filename_json = name + ".json"
    vcham.utils.VCSystem_to_json(system, general_data, filename_json,rewrite=True)
    output_file = name + ".op"
    vcham.utils.json_to_mctdh(filename_json, output_file)

    # Now let us create a supersystem with the model consisting of two identical subsystems.
    # The two subsystems will be placed at a distance of 10 Bohr.

    r = 10
    r_angstrom = r * vcham.constants.BOHR_TO_ANGSTROM
    print(f"Distance in Angstrom: {r_angstrom}, Distance in Bohr: {r}")


    # We have to define the molecules and interactions between them
    # Define the two molecules with their interacting states and positions
    # The first molecule is at the origin, the second one is at (0, 0, r)
    # The two molecules will be parallel to the z-axis, but you can change the rotation angles to make them perpendicular or at any other angle.

    mol1 = vcham.utils.Molecule(molecule_idx=0, interacting_states=[0,1],CM=np.array([0.0, 0.0, 0.0]), rot_angles=(0.0, 0.0, 0.0))
    # mol2 = vcham.utils.Molecule(molecule_idx=1, interacting_states=[0,1],CM=np.array([0.0, 0.0, r]), rot_angles=(0.0,0.0,0.0)) # Parallel to the z-axis
    mol2 = vcham.utils.Molecule(molecule_idx=1, interacting_states=[0,1],CM=np.array([0.0, 0.0, r]), rot_angles=(np.pi/2,np.pi/2,0.0)) # Perpendicular to the z-axis

    # Define interactions among molecules
    # In this case, we will use the dipole-dipole interaction.
    int1 = vcham.utils.DipoleInteraction(molecules=[mol1,mol2])

    # Save the interaction data to a JSON file
    # The infiles are the JSON files of the individual molecules, which we will use to merge them into a single JSON file.
    # The outfile is the name of the output JSON file, which will contain the merged data of the two molecules and their interaction.
    # The molecules and interactions are passed as lists, so you can add more molecules and interactions if needed.
    vcham.utils.merge_jsons(infiles=[filename_json, filename_json], 
                    outfile="tests/result_test/2mol_model_sigma_plus.json", 
                    molecules=[mol1, mol2],
                    interactions=[int1],
                    rewrite=True
                    )

    vcham.utils.json_to_mctdh("tests/result_test/2mol_model_sigma_plus.json", "tests/result_test/2mol_model_sigma_plus.op")

if __name__ == "__main__":
    test_nonjt()
    print("Test completed successfully.")