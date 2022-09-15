import importlib
from datetime import datetime
from os import getpid
from random import seed
from socket import gethostname
from time import time

from algorithm.parameters import params
from utilities.stats import trackers
from utilities.stats.file_io import generate_folders_and_files


def initialise_run_params(create_files, first=False):
    """
    Initialises all lists and trackers. Generates save folders and initial
    parameter files if debugging is not active.

    :return: Nothing
    """

    start = datetime.now()
    trackers.time_list.append(time())

    # Set random seed
    if params['RANDOM_SEED'] is None:
        params['RANDOM_SEED'] = int(start.microsecond)
    seed(params['RANDOM_SEED'])

    # Generate a time stamp for use with folder and file names.
    hms = "%02d%02d%02d" % (start.hour, start.minute, start.second)
    params['TIME_STAMP'] = "_".join([gethostname(),
                                     str(start.year)[2:],
                                     str(start.month),
                                     str(start.day),
                                     hms,
                                     str(start.microsecond),
                                     str(getpid()),
                                     str(params['RANDOM_SEED'])])
    if not params['SILENT']:
        print("\nStart:\t", start, "\n")

    # Generate save folders and files
    if params['DEBUG']:
        print("Seed:\t", params['RANDOM_SEED'], "\n")
    elif create_files:
        generate_folders_and_files(first)


def set_param_imports():
    """
    This function makes the command line experience easier for users. When
    specifying operators listed in the lists below, users do not need to
    specify the full file path to the functions themselves. Users can simply
    specify a single word, e.g.

        "--mutation subtree"

    Using the special_ops dictionary for example, this will default to
    "operators.mutation.subtree. Executes the correct imports for specified
    modules and then saves the correct parameters in the params dictionary.
    Users can still specify the full direct path to the operators if they so
    desire, allowing them to create new operators and save them wherever
    they like.

    Sets the fitness function for a problem automatically. Fitness functions
    must be stored in fitness. Fitness functions must be classes, where the
    class name matches the file name.

    :return: Nothing.
    """

    # For these ops we let the param equal the function itself.
    ops = {'operators': ['INITIALISATION', 'SELECTION', 'CROSSOVER',
                         'MUTATION', 'REPLACEMENT'],
           'utilities.fitness': ['ERROR_METRIC'],
           'fitness': ['FITNESS_FUNCTION'],
           'algorithm': ['SEARCH_LOOP', 'STEP']}

    # We have to take 'algorithm' first as the functions from
    # algorithm need to be imported before any others to prevent
    # circular imports. We have to take 'utilities.fitness' before
    # 'fitness' because ERROR_METRIC has to be set in order to call
    # the fitness function constructor.

    for special_ops in ['algorithm', 'utilities.fitness',
                        'operators', 'fitness']:

        if all([callable(params[op]) for op in ops[special_ops]]):
            # params are already functions
            pass

        else:

            for op in ops[special_ops]:

                if special_ops == "fitness":
                    # Fitness functions represent a special case.

                    get_fit_func_imports()

                elif params[op] is not None:
                    # Split import name based on "." to find nested modules.
                    split_name = params[op].split(".")

                    if len(split_name) > 1:
                        # Check to see if a full path has been specified.

                        # Get attribute name.
                        attr_name = split_name[-1]

                        try:
                            # Try and use the exact specified path to load
                            # the module.

                            # Get module name.
                            module_name = ".".join(split_name[:-1])

                            # Import module and attribute and save.
                            params[op] = return_attr_from_module(module_name,
                                                                 attr_name)

                        except Exception:
                            # Either a full path has not actually been
                            # specified, or the module doesn't exist. Try to
                            # append specified module to default location.

                            # Get module name.
                            module_name = ".".join([special_ops,
                                                    ".".join(split_name[:-1])])

                            try:
                                # Import module and attribute and save.
                                params[op] = return_attr_from_module(
                                    module_name,
                                    attr_name)

                            except Exception:
                                s = "utilities.algorithm.initialise_run." \
                                    "set_param_imports\n" \
                                    "Error: Specified %s function not found:" \
                                    " %s\n" \
                                    "       Checked locations: %s\n" \
                                    "                          %s\n" \
                                    "       Please ensure parameter is " \
                                    "specified correctly." % \
                                    (op.lower(), attr_name, params[op],
                                     ".".join([module_name, attr_name]))
                                raise Exception(s)

                    else:
                        # Just module name specified. Use default location.

                        # If multi-agent is specified need to change
                        # how search and step module is called
                        # Loop and step functions for multi-agent is contained
                        # inside algorithm search_loop_distributed and 
                        # step_distributed respectively

                        if params['MULTIAGENT'] and \
                                (op == 'SEARCH_LOOP' or op == 'STEP'):
                            # Define the directory structure for the multi-agent search
                            # loop and step
                            multiagent_ops = {
                                'search_loop': 'distributed_algorithm.search_loop' \
                                , 'step': 'distributed_algorithm.step'}

                            # Get module and attribute names
                            module_name = ".".join(
                                [special_ops, multiagent_ops[op.lower()]])
                            attr_name = split_name[-1]

                        else:
                            # Get module and attribute names.
                            module_name = ".".join([special_ops, op.lower()])
                            attr_name = split_name[-1]

                        # Import module and attribute and save.
                        params[op] = return_attr_from_module(module_name,
                                                             attr_name)


def get_fit_func_imports():
    """
    Special handling needs to be done for fitness function imports,
    as fitness functions can be specified a number of different ways. Notably,
    a list of fitness functions can be specified, indicating multiple
    objective optimisation.

    Note that fitness functions must be classes where the class has the same
    name as its containing file. Fitness functions must be contained in the
    `fitness` module.

    :return: Nothing.
    """

    op = 'FITNESS_FUNCTION'

    if "," in params[op]:
        # List of fitness functions given in parameters file.

        # Convert specified fitness functions into a list of strings.
        params[op] = params[op].strip("[()]").split(",")

    if isinstance(params[op], list) and len(params[op]) == 1:
        # Single fitness function given in a list format. Don't use
        # multi-objective optimisation.
        params[op] = params[op][0]

    if isinstance(params[op], list):
        # List of multiple fitness functions given.

        for i, name in enumerate(params[op]):
            # Split import name based on "." to find nested modules.
            split_name = name.strip().split(".")

            # Get module and attribute names.
            module_path = ".".join(['fitness', name.strip()])
            attr = split_name[-1]

            # Import this fitness function.
            params[op][i] = return_attr_from_module(module_path, attr)

        # Import base multi-objective fitness function class.
        from fitness.base_ff_classes.moo_ff import moo_ff

        # Set main fitness function as base multi-objective fitness
        # function class.
        params[op] = moo_ff(params[op])

    else:
        # A single fitness function has been specified.

        # Split import name based on "." to find nested modules.
        split_name = params[op].strip().split(".")

        # Get attribute name.
        attr_name = split_name[-1]

        # Get module name.
        module_name = ".".join(["fitness", params[op]])

        # Import module and attribute and save.
        params[op] = return_attr_from_module(module_name, attr_name)

        # Initialise fitness function.
        params[op] = params[op]()


def return_attr_from_module(module_name, attr_name):
    """
    Given a module path and the name of an attribute that exists in that
    module, import the attribute from the module using the importlib package
    and return it.

    :param module_name: The name/location of the desired module.
    :param attr_name: The name of the attribute.
    :return: The imported attribute from the module.
    """

    try:
        # Import module.
        module = importlib.import_module(module_name)

    except ModuleNotFoundError:
        s = "utilities.algorithm.initialise_run.return_attr_from_module\n" \
            "Error: Specified module not found: %s" % (module_name)
        raise Exception(s)

    try:
        # Import specified attribute and return.
        return getattr(module, attr_name)

    except AttributeError:
        s = "utilities.algorithm.initialise_run.return_attr_from_module\n" \
            "Error: Specified attribute '%s' not found in module '%s'." \
            % (attr_name, module_name)
        raise Exception(s)


def pool_init(params_):
    """
    When initialising the pool the original params dict (params_) is passed in
    and used to update the newly created instance of params, as Windows does
    not retain the system memory of the parent process.

    :param params_: original params dict
    :return: Nothing.
    """

    from platform import system

    if system() == 'Windows':
        params.update(params_)
