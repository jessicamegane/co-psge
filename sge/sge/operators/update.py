import numpy as np

def grammar_mutation(ind, prob_mutation, gauss_std):
    ind['fitness'] = None
    gram = ind['pcfg']
    for nt_values in gram:
        if len(nt_values)  <= 1:
            continue
        for prob_idx in range(len(nt_values)):
            if np.random.uniform() < prob_mutation:
                gauss = np.random.normal(0.0,gauss_std)
                diff = (gauss / (len(nt_values) - 1))
                nt_values[prob_idx] += (gauss + diff)
                nt_values -= diff
                nt_values = np.clip(nt_values, 0, np.infty) / np.sum(np.clip(nt_values, 0, np.infty))
                break
    return ind