import argparse
from operator import attrgetter


class SortingHelpFormatter(argparse.HelpFormatter):
    """
    Custom class for sorting the arguments of the arg parser for printing. When
    "--help" is called, arguments will be listed in alphabetical order. Without
    this custom class, arguments will be printed in the order in which they are
    defined.
    """

    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


def parse_cmd_args(arguments):
    """
    Parser for command line arguments specified by the user. Specified command
    line arguments over-write parameter file arguments, which themselves
    over-write original values in the algorithm.parameters.params dictionary.

    The argument parser structure is set up such that each argument has the
    following information:

        dest: a valid key from the algorithm.parameters.params dictionary
        type: an expected type for the specified option (i.e. str, int, float)
        help: a string detailing correct usage of the parameter in question.

    Optional info:

        default: The default setting for this parameter.
        action : The action to be undertaken when this argument is called.

    NOTE: You cannot add a new parser argument and have it evaluate "None" for
    its value. All parser arguments are set to "None" by default. We filter
    out arguments specified at the command line by removing any "None"
    arguments. Therefore, if you specify an argument as "None" from the
    command line and you evaluate the "None" string to a None instance, then it
    will not be included in the eventual parameters.params dictionary. A
    workaround for this would be to leave "None" command line arguments as
    strings and to eval them at a later stage.

    :param arguments: Command line arguments specified by the user.
    :return: A dictionary of parsed command line arguments, along with a
    dictionary of newly specified command line arguments which do not exist
    in the params dictionary.
    """

    # Initialise parser
    parser = argparse.ArgumentParser(
        formatter_class=SortingHelpFormatter,
        usage=argparse.SUPPRESS,
        description="""Welcome to PonyGE2 - Help.
        The following are the available command line arguments. Please see
        src/algorithm/parameters.py for a more detailed explanation of each
        argument and its possible values.""",
        epilog="""To try out PonyGE2 from the command line simply navigate to
        the src directory and type: python ponyge.py.""")

    parser._optionals.title = 'PonyGE2 command-line usage'

    # Set up class for parsing list arguments.
    class ListAction(argparse.Action):
        """
        Class for parsing a given string into a list.
        """

        def __init__(self, option_strings, **kwargs):
            super(ListAction, self).__init__(option_strings, **kwargs)

        def __call__(self, parser, namespace, value, option_string=None):
            if type(eval(value)) != list or any([type(i) != int for i in
                                                 eval(value)]):
                s = "utilities.algorithm.command_line_parser.ListAction\n" \
                    "Error: parameter %s is not a valid genome.\n" \
                    "       Value given: %s" % (option_string, value)
                raise Exception(s)
            else:
                setattr(namespace, self.dest, eval(value))

    # Set up class for checking float arguments.
    class FloatAction(argparse.Action):
        """
        Class for checking a given float is within the range [0:1].
        """

        def __init__(self, option_strings, **kwargs):
            super(FloatAction, self).__init__(option_strings, **kwargs)

        def __call__(self, parser, namespace, value, option_string=None):
            if not 0 <= float(value) <= 1:
                s = "utilities.algorithm.command_line_parser.FloatAction\n" \
                    "Error: parameter %s outside allowed range [0:1].\n" \
                    "       Value given: %s" % (option_string, value)
                raise Exception(s)
            else:
                setattr(namespace, self.dest, float(value))

    # Set up class for checking raw string arguments to catch "tab" inputs.
    class CatchTabStr(argparse.Action):
        """
        Class for checking raw string arguments to catch "tab" inputs.
        """

        def __init__(self, option_strings, **kwargs):
            super(CatchTabStr, self).__init__(option_strings, **kwargs)

        def __call__(self, parser, namespace, value, option_string=None):
            if repr(value) == repr("\\t"):
                value = "\t"
            setattr(namespace, self.dest, value)

    # LOAD PARAMETERS FILE
    parser.add_argument('--parameters',
                        dest='PARAMETERS',
                        type=str,
                        help='Specifies the parameters file to be used. Must '
                             'include the full file extension. Full file path'
                             'does NOT need to be specified.')

    # LOAD STEP AND SEARCH LOOP FUNCTIONS
    parser.add_argument('--search_loop',
                        dest='SEARCH_LOOP',
                        type=str,
                        help='Sets the desired search loop function.')
    parser.add_argument('--step',
                        dest='STEP',
                        type=str,
                        help='Sets the desired search step function.')

    # POPULATION OPTIONS
    parser.add_argument('--population_size',
                        dest='POPULATION_SIZE',
                        type=int,
                        help='Sets the population size, requires int value.')
    parser.add_argument('--generations',
                        dest='GENERATIONS',
                        type=int,
                        help='Sets the number of generations, requires int '
                             'value.')
    parser.add_argument('--hill_climbing_history',
                        dest='HILL_CLIMBING_HISTORY',
                        type=int,
                        help='Sets the history-length for late-acceptance'
                             'and step-counting hill-climbing.')
    parser.add_argument('--schc_count_method',
                        dest='SCHC_COUNT_METHOD',
                        type=str,
                        help='Sets the counting method for step-counting '
                             'hill-climbing. Optional values are "count_all", '
                             '"acp", and "imp".')

    # INDIVIDUAL SIZE
    parser.add_argument('--max_tree_depth',
                        dest='MAX_TREE_DEPTH',
                        type=int,
                        help='Sets the max derivation tree depth for the '
                             'algorithm, requires int value. The default max '
                             'tree depth is set to None, i.e. trees can grow'
                             'indefinitely. This can also be set by '
                             'specifying the max tree depth to be 0.')
    parser.add_argument('--max_tree_nodes',
                        dest='MAX_TREE_NODES',
                        type=int,
                        help='Sets the max derivation tree nodes for the '
                             'algorithm, requires int value. The default max '
                             'tree nodes is set to None, i.e. trees can grow'
                             'indefinitely. This can also be set by '
                             'specifying the max tree nodes to be 0.')
    parser.add_argument('--codon_size',
                        dest='CODON_SIZE',
                        type=int,
                        help='Sets the range from 0 to codon_size to be used '
                             'in genome, requires int value')
    parser.add_argument('--max_genome_length',
                        dest='MAX_GENOME_LENGTH',
                        type=int,
                        help='Sets the maximum chromosome length for the '
                             'algorithm, requires int value. The default max '
                             'genome length is set to None, i.e. genomes can '
                             'grow indefinitely. This can also be set by '
                             'specifying the max genome length to be 0.')
    parser.add_argument('--max_wraps',
                        dest='MAX_WRAPS',
                        type=int,
                        help='Sets the maximum number of times the genome '
                             'mapping process can wrap over the length of the '
                             'genome. Requires int value.')
    parser.add_argument('--permutation_ramps',
                        dest='PERMUTATION_RAMPS',
                        type=int,
                        help='Set the number of depths permutations are '
                             'calculated for (starting from the minimum path '
                             'of the grammar). Mainly for use with '
                             'the grammar analyser script. Requires int '
                             'value.')

    # INITIALISATION
    parser.add_argument('--max_init_tree_depth',
                        dest='MAX_INIT_TREE_DEPTH',
                        type=int,
                        help='Sets the max tree depth for initialisation.')
    parser.add_argument('--min_init_tree_depth',
                        dest='MIN_INIT_TREE_DEPTH',
                        type=int,
                        help='Sets the min tree depth for initialisation.')
    parser.add_argument('--init_genome_length',
                        dest='INIT_GENOME_LENGTH',
                        type=int,
                        help='Sets the length for chromosomes to be '
                             'initialised to. Requires int value.')
    parser.add_argument('--initialisation',
                        dest='INITIALISATION',
                        type=str,
                        help='Sets the initialisation strategy, requires a '
                             'string such as "rhh" or a direct path string '
                             'such as "operators.initialisation.rhh".')

    # SELECTION
    parser.add_argument('--selection',
                        dest='SELECTION',
                        type=str,
                        help='Sets the selection to be used, requires string '
                             'such as "tournament" or direct path string such '
                             'as "operators.selection.tournament".')
    parser.add_argument('--invalid_selection',
                        dest='INVALID_SELECTION',
                        action='store_true',
                        default=None,
                        help='Allow for the selection of invalid individuals '
                             'during selection.')
    parser.add_argument('--tournament_size',
                        dest='TOURNAMENT_SIZE',
                        type=int,
                        help='Sets the number of individuals to contest tournament,'
                             ' requires int.')
    parser.add_argument('--selection_proportion',
                        dest='SELECTION_PROPORTION',
                        action=FloatAction,
                        help='Sets the proportion for truncation selection, '
                             'requires float, e.g. 0.5.')

    # OPERATOR OPTIONS
    parser.add_argument('--within_used',
                        dest='WITHIN_USED',
                        default=None,
                        action='store_true',
                        help='Boolean flag for selecting whether or not '
                             'mutation is confined to within the used portion '
                             'of the genome. Default set to True.')

    # CROSSOVER
    parser.add_argument('--crossover',
                        dest='CROSSOVER',
                        type=str,
                        help='Sets the type of crossover to be used, requires '
                             'string such as "subtree" or direct path string '
                             'such as "operators.crossover.subtree".')
    parser.add_argument('--crossover_probability',
                        dest='CROSSOVER_PROBABILITY',
                        action=FloatAction,
                        help='Sets the crossover probability, requires float, '
                             'e.g. 0.9.')
    parser.add_argument('--no_crossover_invalids',
                        dest='NO_CROSSOVER_INVALIDS',
                        default=None,
                        action='store_true',
                        help='Prevents invalid individuals from being '
                             'generated by crossover.')

    # MUTATION
    parser.add_argument('--mutation',
                        dest='MUTATION',
                        type=str,
                        help='Sets the type of mutation to be used, requires '
                             'string such as "int_flip_per_codon" or direct '
                             'path string such as '
                             '"operators.mutation.int_flip_per_codon".')
    parser.add_argument('--mutation_events',
                        dest='MUTATION_EVENTS',
                        type=int,
                        help='Sets the number of mutation events based on '
                             'probability.')
    parser.add_argument('--mutation_probability',
                        dest='MUTATION_PROBABILITY',
                        action=FloatAction,
                        help='Sets the rate of mutation probability for linear'
                             ' genomes')
    parser.add_argument('--no_mutation_invalids',
                        dest='NO_MUTATION_INVALIDS',
                        default=None,
                        action='store_true',
                        help='Prevents invalid individuals from being '
                             'generated by mutation.')

    # EVALUATION
    parser.add_argument('--fitness_function',
                        dest='FITNESS_FUNCTION',
                        type=str,
                        nargs='+',
                        help='Sets the fitness function to be used. '
                             'Requires string such as "regression". '
                             'Multiple fitness functions can be specified'
                             'for multiple objective optimisation (using '
                             'NSGA-II). To specify multiple fitness '
                             'functions simply enter in the desired names of'
                             ' the functions separated by spaces.')
    parser.add_argument('--dataset_train',
                        dest='DATASET_TRAIN',
                        type=str,
                        help='For use with problems that use a dataset. '
                             'Specifies the training data for evolution. '
                             'Full file name must be specified.')
    parser.add_argument('--dataset_test',
                        dest='DATASET_TEST',
                        type=str,
                        help='For use with problems that use a dataset. '
                             'Specifies the testing data for evolution. '
                             'Full file name must be specified.')
    parser.add_argument('--dataset_delimiter',
                        dest='DATASET_DELIMITER',
                        action=CatchTabStr,
                        help='For use with problems that use a dataset. '
                             'Specifies the delimiter for the dataset. '
                             'Requires string such as "\\t".')
    parser.add_argument('--target',
                        dest='TARGET',
                        type=str,
                        help='For string match problem. Requires target '
                             'string.')
    parser.add_argument('--error_metric',
                        dest='ERROR_METRIC',
                        type=str,
                        help='Sets the error metric to be used with supervised'
                             ' learning problems. Requires string such as '
                             '"mse" or "rmse".')
    parser.add_argument('--optimize_constants',
                        dest='OPTIMIZE_CONSTANTS',
                        action='store_true',
                        default=None,
                        help='Whether to optimize numerical constants by '
                             'gradient descent in supervised learning '
                             'problems. Requires True or False, default '
                             'False.')
    parser.add_argument('--multicore',
                        dest='MULTICORE',
                        action='store_true',
                        default=None,
                        help='Turns on multi-core evaluation.')
    parser.add_argument('--cores',
                        dest='CORES',
                        type=int,
                        help='Specify the number of cores to be used for '
                             'multi-core evaluation. Requires int.')

    # REPLACEMENT
    parser.add_argument('--replacement',
                        dest='REPLACEMENT',
                        type=str,
                        help='Sets the replacement strategy, requires string '
                             'such as "generational" or direct path string '
                             'such as "operators.replacement.generational".')
    parser.add_argument('--elite_size',
                        dest='ELITE_SIZE',
                        type=int,
                        help='Sets the number of elites to be used, requires '
                             'int value.')

    # PROBLEM SPECIFICS
    parser.add_argument('--grammar_file',
                        dest='GRAMMAR_FILE',
                        type=str,
                        help='Sets the grammar to be used, requires string.')
    parser.add_argument('--experiment_name',
                        dest='EXPERIMENT_NAME',
                        type=str,
                        help='Optional parameter to save results in '
                             'results/[EXPERIMENT_NAME] folder. If not '
                             'specified then results are saved in default '
                             'results folder.')
    parser.add_argument('--runs',
                        dest='RUNS',
                        type=int,
                        help='Optional parameter to specify the number of '
                             'runs to be performed for an experiment. Only '
                             'used with experiment manager.')
    parser.add_argument('--extra_parameters',
                        dest='EXTRA_PARAMETERS',
                        type=str,
                        nargs='+',
                        help='Optional extra command line parameter for '
                             'inclusion of any extra information required '
                             'for user-specific runs. Can be whatever you '
                             'want it to be. Specified arguments are parsed '
                             'as a list. Specify as many values as desired, '
                             'separated by spaces.')

    # OPTIONS
    parser.add_argument('--random_seed',
                        dest='RANDOM_SEED',
                        type=int,
                        help='Sets the random seed to be used with both the '
                             'standard Python RNG and the NumPy RNG. '
                             'requires int value.')
    parser.add_argument('--debug',
                        dest='DEBUG',
                        action='store_true',
                        default=None,
                        help='Disables saving of all ancillary files.')
    parser.add_argument('--verbose',
                        dest='VERBOSE',
                        action='store_true',
                        default=None,
                        help='Turns on the verbose output of the program in '
                             'terms of command line and extra files.')
    parser.add_argument('--silent',
                        dest='SILENT',
                        action='store_true',
                        default=None,
                        help='Prevents any output from being printed to the '
                             'command line.')
    parser.add_argument('--save_all',
                        dest='SAVE_ALL',
                        action='store_true',
                        default=None,
                        help='Saves the best phenotypes at each generation.')
    parser.add_argument('--save_plots',
                        dest='SAVE_PLOTS',
                        action='store_true',
                        default=None,
                        help='Saves plots for best fitness.')

    # REVERSE-MAPPING
    parser.add_argument('--reverse_mapping_target',
                        dest='REVERSE_MAPPING_TARGET',
                        type=str,
                        help='Target string to parse into a GE individual.')
    parser.add_argument('--target_seed_folder',
                        dest='TARGET_SEED_FOLDER',
                        type=str,
                        help='Specify a target seed folder in the "seeds" '
                             'directory that contains a population of '
                             'individuals with which to seed a run.')

    # STATE SAVING/LOADING
    parser.add_argument('--save_state',
                        dest='SAVE_STATE',
                        action='store_true',
                        default=None,
                        help='Saves the state of the evolutionary run every '
                             'generation. You can specify how often you want '
                             'to save the state with the command '
                             '"--save_state_step".')
    parser.add_argument('--save_state_step',
                        dest='SAVE_STATE_STEP',
                        type=int,
                        help='Specifies how often the state of the current '
                             'evolutionary run is saved (i.e. every n-th '
                             'generation). Requires int value.')
    parser.add_argument('--load_state',
                        dest='LOAD_STATE',
                        type=str,
                        help='Load an evolutionary run from a saved state. '
                             'You must specify the full file path to the '
                             'desired state file. Note that state files have '
                             'no file type.')

    # MULTIAGENT
    parser.add_argument('--multiagent',
                        dest='MULTIAGENT',
                        action='store_true',
                        default=None,
                        help='This enable the multi-agent mode. If this mode is'
                             ' enabled the search_loop and step parameter are'
                             ' overridden with search_multiagent and step_multiagent'
                             ' respectively')
    parser.add_argument('--agent_size',
                        dest='AGENT_SIZE',
                        type=int,
                        help='Specifies how many agents are initialize in'
                             ' the environment. By default 100 agents are initialize.'
                             ' Greater the number of agents the time to find the'
                             ' would be reduced')
    parser.add_argument('--interaction_probability',
                        dest='INTERACTION_PROBABILITY',
                        action=FloatAction,
                        help='Specifies the probability of agent interacting with'
                             ' other nearby agents in the environment. By default'
                             ' 0.5 probability is used. Higher the probability the time'
                             ' to find the solution would be reduced')

    # CACHING
    class CachingAction(argparse.Action):
        """
        Class for defining special mutually exclusive options for caching.
        """

        def __init__(self, option_strings, CACHE=None, LOOKUP_FITNESS=None,
                     LOOKUP_BAD_FITNESS=None, MUTATE_DUPLICATES=None,
                     **kwargs):
            self.CACHE = CACHE
            self.LOOKUP_FITNESS = LOOKUP_FITNESS
            self.LOOKUP_BAD_FITNESS = LOOKUP_BAD_FITNESS
            self.MUTATE_DUPLICATES = MUTATE_DUPLICATES
            super(CachingAction, self).__init__(option_strings, nargs=0,
                                                **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, 'CACHE', self.CACHE)
            if 'LOOKUP_FITNESS' not in namespace or \
                    getattr(namespace, 'LOOKUP_FITNESS') is not False:
                # able to overwrite if True or None
                setattr(namespace, 'LOOKUP_FITNESS', self.LOOKUP_FITNESS)
            if self.LOOKUP_BAD_FITNESS and \
                    'LOOKUP_BAD_FITNESS' not in namespace:
                setattr(namespace, 'LOOKUP_BAD_FITNESS',
                        self.LOOKUP_BAD_FITNESS)
            if self.MUTATE_DUPLICATES and 'MUTATE_DUPLICATES' not in namespace:
                setattr(namespace, 'MUTATE_DUPLICATES', self.MUTATE_DUPLICATES)

    # Generate a mutually exclusive group for caching options. This means
    # that you cannot specify multiple caching options simultaneously,
    # only one at a time.
    parser.add_argument("--cache",
                        dest='CACHE',
                        action=CachingAction,
                        CACHE=True,
                        LOOKUP_FITNESS=True,
                        help='Tracks unique phenotypes and is used to '
                             'lookup duplicate fitnesses.')
    caching_group = parser.add_mutually_exclusive_group()
    caching_group.add_argument("--dont_lookup_fitness",
                               dest='CACHE',
                               action=CachingAction,
                               CACHE=True,
                               LOOKUP_FITNESS=False,
                               help='Uses cache to track duplicate '
                                    'individuals, but does not use the cache '
                                    'to save fitness evaluations.')
    caching_group.add_argument("--lookup_bad_fitness",
                               dest='CACHE',
                               action=CachingAction,
                               CACHE=True,
                               LOOKUP_FITNESS=False,
                               LOOKUP_BAD_FITNESS=True,
                               help='Gives duplicate phenotypes a bad fitness '
                                    'when encountered. Uses cache.')
    caching_group.add_argument("--mutate_duplicates",
                               dest='CACHE',
                               action=CachingAction,
                               CACHE=True,
                               LOOKUP_FITNESS=False,
                               MUTATE_DUPLICATES=True,
                               help='Replaces duplicate individuals with '
                                    'mutated versions. Uses cache.')

    # Parse command line arguments using all above information.
    args, unknown = parser.parse_known_args(arguments)

    # All default args in the parser are set to "None". Only take arguments
    # which are not "None", i.e. arguments which have been passed in from
    # the command line.
    cmd_args = {key: value for key, value in vars(args).items() if value is
                not None}

    # Set "None" values correctly.
    for key in sorted(cmd_args.keys()):
        # Check all specified arguments.

        if type(cmd_args[key]) == str and cmd_args[key].lower() == "none":
            # Allow for people not using correct capitalisation.

            cmd_args[key] = None

    return cmd_args, unknown
