import pickle
import random
from os import path


def create_state(individuals):
    """
    Create a dictionary representing the current state of an evolutionary
    run. The state includes the current population, the current random state,
    the parameters dictionary, the stats dictionary, and all lists in the
    utilities.stats.trackers module.
    
    :param individuals: A population of individuals to be saved.
    :return: The complete state of a run.
    """

    from algorithm.parameters import params
    from stats.stats import stats
    from utilities.stats import trackers
    from time import time

    # Get time.
    state_time = time()

    # Get random state.
    random_state = random.getstate()

    # Create a picklable version of the params dictionary. Since the params
    # dictionary contains functions and class instances, we need to replace
    # these with the names of their respective modules, since module
    # instances are not picklable.
    pickle_params = {param: (check_name(params[param]) if callable(
        params[param]) else params[param]) for param in params}

    # Create a picklable version of the trackers module.
    pickle_trackers = {i: getattr(trackers, i) for i in dir(trackers)
                       if not i.startswith("__")}

    # Create state dictionary
    state = {"trackers": pickle_trackers, "params": pickle_params,
             "stats": stats, "individuals": individuals,
             "random_state": random_state, "time": state_time}

    save_state(state)


def save_state(state):
    """
    Save the current state of a run. Allows for interrupted runs to be
    re-loaded and continued from the last save point.
    
    :param state: A dictionary describing the current state of a run.
    :return: Nothing.
    """

    # Create pickle file
    state_file = open(path.join(state['params']['FILE_PATH'], "state"), "wb")

    # Save state information
    pickle.dump(state, state_file)

    # Close file.
    state_file.close()


def load_state(state):
    """
    Load in the state of a previous run.
    
    :param state: A .mat file containing all information about the state of
    a run.
    :return: The loaded state of a run.
    """

    # Open pickle file
    state_file = open(state, "rb")

    # Get state information
    loaded_state = pickle.load(state_file)

    # Close file.
    state_file.close()

    # Set state.
    individuals = set_state(loaded_state)

    # Return individuals.
    return individuals


def set_state(state):
    """
    Given a dictionary representing the state of an evolutionary run, set all
    aspects of the system to re-create that state. The state includes the
    current population, the current random state, the parameters dictionary,
    the stats dictionary, and all lists in the utilities.stats.trackers module.
    
    Sets all aspects of the system and then returns a population of
    individuals at the current generation.
    
    :param state: The complete state of a run.
    :return: A population of individuals.
    """

    from algorithm.parameters import params
    from utilities.algorithm.initialise_run import set_param_imports
    from stats.stats import stats
    from utilities.stats import trackers
    from time import time

    # Set random state.
    random.setstate(state['random_state'])

    # Set stats.
    for stat in state['stats']:
        stats[stat] = state['stats'][stat]

    # Set trackers.
    for tracker in state['trackers']:
        setattr(trackers, tracker, state['trackers'][tracker])

    # Set parameters.
    for param in state['params']:
        params[param] = state['params'][param]

    # Set correct param imports for specified function options, including
    # error metrics and fitness functions.
    set_param_imports()

    # Set time adjustment to account for old time.
    stats['time_adjust'] = time() - state['time']

    return state['individuals']


def check_name(obj):
    """
    Function for returning the name of a callable object. Function and class
    instances are handled differently, so we use a try/except clause to
    differentiate between the two.

    :param obj: An object for which we want to find the name.
    :return: The name of the object
    """

    try:
        return obj.__name__
    except AttributeError:
        return obj.__class__.__name__
