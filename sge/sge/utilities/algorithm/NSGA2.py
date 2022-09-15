from collections import defaultdict

from sge.parameters import params
from numpy import isnan
from sge.utilities.fitness.math_functions import percentile


def compute_pareto_metrics(population):
    """
    Compute the pareto fronts using NSGA-II.

    :param population: A population to be sorted into fronts using NSGA-II.
    :return: The pareto fronts.
    """

    # Calculate the pareto fronts using Non-Dominated Sorting.
    pareto = sort_non_dominated(population)

    # Calculate the crowding distance
    pareto = calculate_crowding_distance(pareto)

    return pareto


def sort_non_dominated(population):
    """Sort the first *k* *population* into different non-domination levels
    using the "Fast Nondominated Sorting Approach" proposed by Deb et al.,
    see [Deb2002]_. This algorithm has a time complexity of :math:`O(MN^2)`,
    where :math:`M` is the number of objectives and :math:`N` the number of
    individuals.

    :param population: A list of individuals to select from.

    :returns: A list of Pareto fronts (lists), the first list includes
              non-dominated individuals.

    .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
       non-dominated sorting genetic algorithm for multi-objective
       optimization: NSGA-II", 2002.

    """

    # Initialise empty pareto class instance.
    pareto = ParetoInfo()

    # Compute the Inter-Quartile Range (+1) value used to normalize the
    # crowding distance
    pareto.compute_iqr(population)

    # The naming *p* and *q* is the same adopted in [Deb2002]_
    for p in population:

        # Compute the domination counter of p
        for q in population:

            if dominates(p, q):
                # Add *q* to the set of solutions dominated by *p*
                pareto.dominated_solutions[p].append(q)

            elif dominates(q, p):
                # Increment the domination counter of p
                pareto.update_domination_count(p, True)

        # *p* belongs to the first front
        if pareto.get_domination_count(p) == 0:
            pareto.fronts[0].append(p)
            pareto.rank[p] = 0

    # Initialize the front counter
    i = 0

    # Compute the fronts.
    while len(pareto.fronts[i]) > 0:

        # Used to store the members of the next front
        big_q = []

        # For each each solution in the current front
        for p in pareto.fronts[i]:

            # Decrement the domination counter of each solution dominated by
            # *p*
            for q in pareto.dominated_solutions[p]:
                pareto.update_domination_count(q, False)

                # If the counter reaches 0, the solution is added to the next
                # front.
                if pareto.get_domination_count(q) == 0:
                    pareto.rank[q] = i + 1
                    big_q.append(q)

        # Update the front counter
        i += 1

        # Add the solutions selected in this iteration to the next front
        pareto.fronts.append(big_q)

    return pareto


def dominates(individual1, individual2):
    """
    Returns whether or not *individual1* dominates *individual2*. An individual
    dominates another if all fitness values are at least as good on all
    objectives, and strictly better than on at least one objective.

    :param individual1: The individual that would be dominated.
    :param individual2: The individual dominant.
    :returns: :obj:`True` if *individual1* dominates *individual2*,
              :obj:`False` otherwise.
    """

    if any([isnan(fit) for fit in individual1.fitness]):
        # Individual 1 is invalid.
        return False

    elif any([isnan(fit) for fit in individual2.fitness]):
        # Individual 2 is invalid.
        return True

    # Get fitness functions.
    ffs = params['FITNESS_FUNCTION'].fitness_functions

    # Check how many fitness values are equal.
    equal_fit = [False] * len(ffs)

    # Iterate over all fitness values and fitness functions.
    for ind1_value, ind2_value, ff, i in zip(individual1.fitness,
                                             individual2.fitness,
                                             ffs, range(len(ffs))):
        # Check for fitness equality
        if ind1_value == ind2_value:
            equal_fit[i] = True

        elif not compare_fitnesses(ind1_value, ind2_value, ff):
            # ind1 does not dominate over ind2.
            return False

    # If all fitness values are equal, no domination
    if all(equal_fit):
        return False

    return True


def compare_fitnesses(ind1_value, ind2_value, ff):
    """
    Comparison function for checking whether ind1 dominates ind2 on a given
    fitness value.

    :param ind1_value: The fitness of ind1.
    :param ind2_value: The fitness of ind2.
    :param ff: The fitness function that generated the above values.
    :return: Whether or not ind1_value is better than ind2_value.
    """

    if ff.maximise:
        # The fitness function is maximising.

        # Check whether ind1_value is better than ind2_value.
        return ind1_value > ind2_value

    else:
        # The fitness function is minimising.

        # Check whether ind1_value is better than ind2_value.
        return ind1_value < ind2_value


def calculate_crowding_distance(pareto):
    """
    Compute the crowding distance of each individual in each Pareto front.
    The value is stored inside the dictionary *crowding_distance* kept by
    the object *pareto*.

    :param pareto: A ParetoInfo object with the information regarding
                   the Pareto fronts defined by the current population

    :return: A list of Pareto fronts (lists), the first list includes
             non-dominated individuals.
    """

    # The crowding distance is computed per front
    for front in pareto.fronts:

        if len(front) > 0:

            # Number of solutions in the front
            solutions_num = len(front)

            for individual in front:
                # Initialize the distances
                pareto.crowding_distance[individual] = 0

            for m in range(pareto.n_objectives):
                # Sort the solutions using each objective value
                front = sorted(front, key=lambda item: params[
                    'FITNESS_FUNCTION'].value(item.fitness, m),
                               reverse=params['FITNESS_FUNCTION'].
                               fitness_functions[m].maximise)

                # The boundary solutions are assigned an infinite distance
                # value
                pareto.crowding_distance[front[0]] = float("inf")
                pareto.crowding_distance[front[solutions_num - 1]] = float(
                    "inf")

                # All other intermediate solutions have the distance computed
                for index in range(1, solutions_num - 1):
                    # The distance value equals to the absolute normalized
                    # difference in the function values of two adjacent
                    # solutions. The normalization uses (IQR + 1) instead of
                    # (max-min)
                    pareto.crowding_distance[front[index]] += \
                        (params['FITNESS_FUNCTION'].value(
                            front[index + 1].fitness, m) -
                         params['FITNESS_FUNCTION'].value(
                             front[index - 1].fitness, m)) / \
                        pareto.fitness_iqr[m]

    return pareto


def crowded_comparison_operator(self, other, pareto):
    """
    The crowded-comparison operator guides the selection process at the various
    stages of the algorithm toward a uniformly spread-out Pareto-optimal front.
    The operator returns True if *self* is better than *other* and
    False otherwise.

    :param self: First individual of the comparison
    :param other: Second individual of the comparison
    :param pareto: A ParetoInfo object with the information regarding
                   the Pareto fronts defined by the current population
    :return: True if *self* is better than *other* and False otherwise.
    """

    # Between two solutions with differing non-domination ranks, we prefer the
    # solution with the lower (better) rank. Otherwise, if both solutions
    # belong to the same front, then we prefer the solution that is located in
    # a lesser crowded region, i.e., with the larger crowding distance.
    if (pareto.rank[self] < pareto.rank[other]) or \
            (pareto.rank[self] == pareto.rank[other] and
             pareto.crowding_distance[self] > pareto.crowding_distance[other]):
        return True

    else:
        return False


def get_population_iqr(population, n_objectives):
    """
    Compute the inter-quartile range (IQR) of the population regarding
    each objective.

    :param population: The input population
    :param n_objectives: Total number of objectives
    :return: List with the IQR regarding each objective
    """

    # Initialise base IQR as 0 for each objective
    iqr = [0 for _ in range(n_objectives)]

    for m in range(n_objectives):
        # Iterate over all objectives

        # Sort the population with respect to the current objective.
        sorted_pop = sorted(population, key=lambda ind:
        params['FITNESS_FUNCTION'].value(ind.fitness, m),
                            reverse=params['FITNESS_FUNCTION'].
                            fitness_functions[m].maximise)

        # Get the inter-quartile fitness ranges for the current objective.
        iqr[m] = (params['FITNESS_FUNCTION'].value(percentile(sorted_pop,
                                                              75).fitness, m) -
                  params['FITNESS_FUNCTION'].value(percentile(sorted_pop,
                                                              25).fitness, m))
    return iqr


class ParetoInfo:

    def __init__(self):
        self.fronts = [[]]
        self.rank = dict()
        self.domination_count = dict()
        self.crowding_distance = dict()
        self.dominated_solutions = defaultdict(list)

        try:
            self.n_objectives = params['FITNESS_FUNCTION'].num_obj

        except AttributeError:
            s = "utilities.algorithm.NSGA2\n" \
                "Error: Specified fitness function does not have " \
                "'num_obj' attribute.\n" \
                "       If using multiple objective optimisation, ensure " \
                "fitness.base_ff_classes.base_moo_ff is implemented.\n" \
                "       See README documentation for more information."
            raise Exception(s)

        self.fitness_iqr = [0] * self.n_objectives

    def compute_iqr(self, population):
        """
        Compute the Inter-Quartile Range for a population for all fitness
        objectives.

        :param population: A population.
        :return: Nothing.
        """

        # Get the inter-quartile ranges for all objectives.
        self.fitness_iqr = get_population_iqr(population, self.n_objectives)

        # If the IQR value is zero, we replace it for 1---which is equivalent
        # to disregard the normalization process for that objective dimension.
        self.fitness_iqr = [1 if i == 0 else i for i in self.fitness_iqr]

    def update_domination_count(self, individual, should_increment=True):
        """
        Update the domination count of the *individual* by incrementing:

            (*should_increment*=:obj:`True`)

        or decrementing:

            (*should_increment*=:obj:`False`)

        :param individual: The referring individual
        :param should_increment: Indicates if the methods increment or
                                 decrement the value.
        :return: Nothing.
        """

        if individual in self.domination_count:
            if should_increment:
                self.domination_count[individual] += 1
            else:
                self.domination_count[individual] -= 1
        else:
            if should_increment:
                self.domination_count[individual] = 1
            else:
                self.domination_count[individual] = -1

    def get_domination_count(self, individual):
        """
        Avoids references to uninitialised positions in the dictionary.

        :param individual: Individual used as key in the dictionary.
        :return: The value regarding the key, if any, or 0 otherwise.
        """

        if individual in self.domination_count:
            return self.domination_count[individual]

        return 0

    def get_crowding_distance(self, individual):
        """
        Avoids references to uninitialised positions in the dictionary.

        :param individual: Individual used as key in the dictionary.
        :return: The value regarding the key, if any, or 0 otherwise.
        """

        if individual in self.crowding_distance:
            return self.crowding_distance[individual]

        return 0
