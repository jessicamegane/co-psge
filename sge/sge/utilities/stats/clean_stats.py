from algorithm.parameters import params
from stats.stats import stats


def clean_stats():
    """
    Removes certain unnecessary stats from the stats.stats.stats dictionary
    to clean up the current run.
    
    :return: Nothing.
    """

    if not params['CACHE']:
        stats.pop('unique_inds')
        stats.pop('unused_search')

    if not params['MUTATE_DUPLICATES']:
        stats.pop('regens')
