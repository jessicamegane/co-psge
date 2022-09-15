import re

import scipy
from algorithm.parameters import params
from utilities.fitness.math_functions import *


def optimize_constants(x, y, ind):
    """
    Use gradient descent to search for values for the constants in
    ind.phenotype which minimise loss.
    
    :param x: Input (an array of x values).
    :param y: Expected output (expected y values for given inputs).
    :param ind: A GE individual.
    :return: The value of the error metric at those values
    """

    # Save the old phenotype (has c[0] etc, but may not be consecutive from
    # zero)
    ind.phenotype_original = ind.phenotype

    # Parse the phenotype to make the constants consecutive.
    s, n_consts = make_consts_consecutive(ind.phenotype)

    # Create new consecutive constant attribute for individual.
    ind.phenotype_consec_consts = s

    # Eval the phenotype.
    f = eval("lambda x, c: " + s)

    # Pre-load the error metric fitness function.
    loss = params['ERROR_METRIC']

    shape_mismatch_txt = """Shape mismatch between y and yhat. Please check
that your grammar uses the `x[:, 0]` style, not `x[0]`. Please see change
at https://github.com/PonyGE/PonyGE2/issues/130."""

    if n_consts == 0:
        # ind doesn't refer to c: no need to optimize
        c = []
        yhat = f(x, c)
        if not np.isscalar(yhat):
            if y.shape != yhat.shape:
                raise ValueError(shape_mismatch_txt)
        fitness = loss(y, yhat)
        ind.opt_consts = c
        return fitness

    obj = lambda c: loss(y, f(x, c))
    # obj is now a function of c only for L-BFGS-B. Using 0 as the init seems a
    # reasonable choice. But for scipy.curve_fit we might use [1.0] * n_consts.
    # Maybe other minimizers do better with some other choices? There are other
    # methods to try out.
    init = [0.0] * n_consts

    try:
        res = scipy.optimize.minimize(obj, init, method="L-BFGS-B")
    except ValueError:
        raise ValueError("Error during optimization of constants. " \
                         "Possible cause: " + shape_mismatch_txt)
        

    # the result is accessed like a dict
    ind.opt_consts = res['x']  # the optimum values of the constants

    # the most useful form of the phenotype: c[0], c[1] etc replaced
    # with actual numbers, so can be eval'd directly
    ind.phenotype = replace_consts_with_values(s, ind.opt_consts)

    return res['fun']


def make_consts_consecutive(s):
    """
    The given phenotype will have zero or more occurrences of each const c[0],
    c[1], etc. But eg it might have c[7], but no c[0]. We need to remap, eg:
        7 -> 0
        9 -> 1
    so that we just have c[0], c[1], etc.
    
    :param s: A given phenotype string.
    :return: The phenotype string but with consecutive constants.
    """

    p = r"c\[(\d+)\]"
    # find the consts, extract idxs as ints, unique-ify and sort
    const_idxs = sorted(map(int, set(re.findall(p, s))))

    for i, j in enumerate(const_idxs):
        ci = "c[%d]" % i
        cj = "c[%d]" % j
        s = s.replace(cj, ci)

    return s, len(const_idxs)


def replace_consts_with_values(s, c):
    """
    Replace the constants in a given string s with the values in a list c.
    
    :param s: A given phenotype string.
    :param c: A list of values which will replace the constants in the
    phenotype string.
    :return: The phenotype string with the constants replaced.
    """

    for i in range(len(c)):
        s = s.replace("c[%d]" % i, str(c[i]))

    return s
