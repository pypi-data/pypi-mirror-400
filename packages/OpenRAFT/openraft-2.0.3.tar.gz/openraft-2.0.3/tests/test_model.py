# tests RAFT FOWT functionality and results

import pytest
import numpy as np
from numpy.testing import assert_allclose
import yaml
import pickle
import raft
import os
from wisdem.inputs import load_yaml, write_yaml


'''
 Define files for testing
'''
# Name of the subfolder where the test data is located
test_dir = 'test_data'

# List of input file names to be tested
list_files = [
    'OC3spar.yaml',
    'VolturnUS-S.yaml',
    'VolturnUS-S-pointInertia.yaml',
    'VolturnUS-S_farm.yaml',
    'OC4semi-WAMIT_Coefs.yaml',
    'VolturnUS-S-moorMod2.yaml',
    'VolturnUS-S_farm-moorMod1.yaml',
    'VolturnUS-S-flexible.yaml',
]

save_references = False
plot_diffs = False

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change directory to the 'tests' folder due to yaml files that use relative paths
os.chdir(current_dir)

# To avoid problems with different platforms, get the full path of the file
list_files = [os.path.join(current_dir, test_dir, file) for file in list_files]


# Single test case used in test_solveStatics and test_solveDynamics
# Multiple cases from the yaml file are tested in test_analyzeCases only

'''
 Aux functions
'''
# Function used to create FOWT instance
# Not explicitly inside the fixture below so that we can also run this file as a script
#
def create_model(file):
    with open(file) as f:
        design = yaml.load(f, Loader=yaml.FullLoader)

    if 'array_mooring' in design: # Relative paths may be different in different platforms, so we make sure the path is correct
        if design['array_mooring']['file']:
            design['array_mooring']['file'] = os.path.join(current_dir, test_dir, design['array_mooring']['file'])

    if 'hydroPath' in design['platform']:
        design['platform']['hydroPath'] = os.path.join(current_dir, test_dir, design['platform']['hydroPath'])

    model = raft.Model(design)
    return model

# Define a fixture to loop fowt instances with the index to loop the desired values as well
# Could also zip the lists with the desired values, but I think the approach below is simpler
@pytest.fixture(params=enumerate(list_files))
def index_and_model(request):
    index, file = request.param
    model = create_model(file)
    return index, model

'''
 Test functions
'''
#===== model.solveStatics for different loading conditions
cases4solveStatics = {
    'wind':              {'wind_speed': 8, 'wind_heading': 30, 'turbulence': 0, 'turbine_status': 'operating', 'yaw_misalign': 0, 'wave_spectrum': 'JONSWAP', 'wave_period':  0, 'wave_height': 0, 'wave_heading':   0, 'current_speed': 0, 'current_heading':  0},
    'wave':              {'wind_speed': 0, 'wind_heading':  0, 'turbulence': 0, 'turbine_status': 'operating', 'yaw_misalign': 0, 'wave_spectrum': 'JONSWAP', 'wave_period': 10, 'wave_height': 4, 'wave_heading': -30, 'current_speed': 0, 'current_heading':  0},
    'current':           {'wind_speed': 0, 'wind_heading':  0, 'turbulence': 0, 'turbine_status': 'operating', 'yaw_misalign': 0, 'wave_spectrum': 'JONSWAP', 'wave_period':  0, 'wave_height': 0, 'wave_heading':   0, 'current_speed': 0.6, 'current_heading': 15},
    'wind_wave_current': {'wind_speed': 8, 'wind_heading': 30, 'turbulence': 0, 'turbine_status': 'operating', 'yaw_misalign': 0, 'wave_spectrum': 'JONSWAP', 'wave_period': 10, 'wave_height': 4, 'wave_heading': -30, 'current_speed': 0.6, 'current_heading': 15}
}


def solveStatics(index_and_model, test_case_key, rtol=1e-05, atol=1e-10):
    '''
    We test only the mean offsets and linearized mooring properties.
    '''
    index, model = index_and_model
    testCase = cases4solveStatics[test_case_key]
    model.solveStatics(testCase)
    r6 = np.array([])
    for i, fowt in enumerate(model.fowtList):
        if save_references:
            desired_X0[test_case_key][index][6*i:6*(i+1)] = fowt.r6
        
        # Compare results
        assert_allclose(fowt.r6, desired_X0[test_case_key][index][6*i:6*(i+1)], rtol=rtol, atol=atol)

        if plot_diffs:
            import matplotlib.pyplot as plt
            width = 0.35
            labels = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
            x = np.arange(len(labels))
            plt.figure()
            plt.bar(x - width/2, fowt.r6, width, label='RAFT Calculated')
            plt.bar(x + width/2, desired_X0[test_case_key][index][6*i:6*(i+1)], width, label='Previous Ref.')
            plt.xticks(x, labels)
            plt.legend()
            plt.show()

def test_solveStatics_Wind(index_and_model):
    solveStatics(index_and_model, 'wind')

def test_solveStatics_Wave(index_and_model):
    solveStatics(index_and_model, 'wave', rtol=1e-05, atol=1e-8)

def test_solveStatics_Current(index_and_model):
    solveStatics(index_and_model, 'current')

def test_solveStatics_Wind_Wave_Current(index_and_model):
    solveStatics(index_and_model, 'wind_wave_current')



#===== model.solveEigen for different cases
cases4solveEigen = {
    'unloaded': {'wind_speed': 0, 'wind_heading': 0, 'turbulence': 0, 'turbine_status': 'idle', 'yaw_misalign': 0, 'wave_spectrum': 'JONSWAP', 'wave_period': 0, 'wave_height': 0, 'wave_heading': 0, 'current_speed': 0, 'current_heading': 0},
    'loaded':   {'wind_speed': 8, 'wind_heading': 30, 'turbulence': 0, 'turbine_status': 'operating', 'yaw_misalign': 0, 'wave_spectrum': 'JONSWAP', 'wave_period': 10, 'wave_height': 4, 'wave_heading': -30, 'current_speed': 0.6, 'current_heading': 15}
}


# unpack reference values
reference_values = load_yaml(os.path.join(os.path.dirname(__file__), 'test_model_reference_values.yaml'))
desired_modes = reference_values['desired_modes']
desired_fn = reference_values['desired_fn']
desired_X0 = reference_values['desired_X0']
print('here')

def solveEigen(index_and_model, test_case_key):
    index, model = index_and_model
    testCase = cases4solveEigen[test_case_key]
    model.solveStatics(testCase)
    fns, modes = model.solveEigen()

    if save_references:
        desired_fn[test_case_key][index] = fns[:12]
        desired_modes[test_case_key][index] = modes[:12, :12]

    # Compare results
    assert_allclose(fns[:12], desired_fn[test_case_key][index], rtol=1e-05, atol=1e-5) # Compare the 12 first natural frequencies. That's all modes for the 2-unit array of rigid turbines and enough for the flexible tests
    # assert_allclose(modes[:12, :12], desired_modes[test_case_key][index], rtol=1e-05, atol=1e-5) # this one is too sensitive to machine precision because there are some very small values

def test_solveEigen_unloaded(index_and_model):
    solveEigen(index_and_model, 'unloaded')

def test_solveEigen_loaded(index_and_model):
    solveEigen(index_and_model, 'loaded')


#===== model.analyzeCases for multiple environmental conditions specified in the yaml file
def test_analyzeCases(index_and_model, plotPSDs=False, flagSaveValues=False):
    '''Solve cases listed in the yaml file
    Set flagSaveValues to true to replace the true values file with the values calculated below
    '''
    index, model = index_and_model
    true_values_file = list_files[index].replace('.yaml', '_true_analyzeCases.pkl')
    metrics2check = ['wave_PSD', 'surge_PSD', 'sway_PSD', 'heave_PSD', 'roll_PSD', 'pitch_PSD', 'yaw_PSD', 'AxRNA_PSD', 'Mbase_PSD', 'Tmoor_PSD']

    model.analyzeCases()

    computed_values = {
        'freq_rad': model.results['freq_rad'],
        'case_metrics': model.results['case_metrics'],
    }

    # Save or read the true values
    if flagSaveValues:
        with open(true_values_file, 'wb') as f:
            pickle.dump(computed_values, f)
        return # If saving, we don't need to check the results
    else:
        with open(true_values_file, 'rb') as f:
            true_values = pickle.load(f)

    # Check computed results against previously computed true values
    nCases = len(model.results['case_metrics'])
    for iCase in range(nCases):
        for ifowt in range(model.nFOWT):
            for imetric, metric in enumerate(metrics2check):
                if metric in model.results['case_metrics'][iCase][ifowt]:
                    assert_allclose(model.results['case_metrics'][iCase][ifowt][metric], true_values['case_metrics'][iCase][ifowt][metric], rtol=1e-05, atol=1e-3)
                elif 'array_mooring' in model.results['case_metrics'][iCase] and metric in model.results['case_metrics'][iCase]['array_mooring']:
                    assert_allclose(model.results['case_metrics'][iCase]['array_mooring'][metric], true_values['case_metrics'][iCase]['array_mooring'][metric], rtol=1e-05, atol=1e-3)

    if plotPSDs:
        import matplotlib.pyplot as plt
        for ifowt in range(model.nFOWT):
            fig, ax = plt.subplots(3, 3, figsize=(15, 10))
            for iCase in range(nCases):
                for imetric, metric in enumerate(metrics2check):
                    w_true = true_values['freq_rad']
                    if metric in model.results['case_metrics'][iCase][ifowt]:
                        y = model.results['case_metrics'][iCase][ifowt][metric]
                        y_true = true_values['case_metrics'][iCase][ifowt][metric]
                    elif 'array_mooring' in model.results['case_metrics'][iCase] and metric in model.results['case_metrics'][iCase]['array_mooring']:
                        y = model.results['case_metrics'][iCase]['array_mooring'][metric]
                        y_true = true_values['case_metrics'][iCase]['array_mooring'][metric]

                    if metric == 'Tmoor_PSD':
                        if iCase == 0:
                            fig2, ax2 = plt.subplots(y.shape[0], 1, figsize=(15, 10))
                        for i in range(y.shape[0]):
                            ax2[i].plot(model.w/2/np.pi, y[i, :])
                            ax2[i].plot(w_true/2/np.pi, y_true[i, :], linestyle='--')
                            ax2[i].set_ylabel(f'Line channel {i+1}')
                            ax2[i].set_xlabel('Frequency (Hz)')
                        ax2[0].set_title(f'{metric}')
                    else:
                        # assert_allclose(model.results['case_metrics'][iCase][ifowt][metric], true_values[idxTrueValues][ifowt][metric], rtol=1e-05, atol=1e-5)
                        ax[imetric//3, imetric%3].plot(model.w/2/np.pi, y, label=f'Case {iCase+1}')
                        ax[imetric//3, imetric%3].plot(w_true/2/np.pi, y_true, linestyle='--')
                        ax[imetric//3, imetric%3].set_ylabel(metric)
                        ax[imetric//3, imetric%3].set_xlabel('Frequency (Hz)')
        plt.show()

'''
 To run as a script. Useful for debugging.
'''
if __name__ == "__main__":

    # When saving reference values, run all test cases
    # When testing, just do first one to save time
    if save_references:
        test_indices = range(len(list_files))
    else:
        test_indices = range(1)


    for index in test_indices:

        model = create_model(list_files[index])
        test_solveStatics_Wind((index,model))

        model = create_model(list_files[index])
        test_solveStatics_Wave((index,model))

        model = create_model(list_files[index])
        test_solveStatics_Current((index,model))

        model = create_model(list_files[index])
        test_solveStatics_Wind_Wave_Current((index,model))

        model = create_model(list_files[index])
        test_solveEigen_unloaded((index,model))

        model = create_model(list_files[index])
        test_solveEigen_loaded((index,model))

        model = create_model(list_files[index])
        test_analyzeCases((index,model), plotPSDs=True, flagSaveValues=save_references)  # Set flagSaveValues to True to save new true values

    if save_references:
        # # pack reference values into a yaml file
        reference_values = {}
        reference_values['desired_modes'] = desired_modes
        reference_values['desired_fn'] = desired_fn
        reference_values['desired_X0'] = desired_X0
        write_yaml(reference_values, os.path.join(os.path.dirname(__file__), 'test_model_reference_values.yaml'))
