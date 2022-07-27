import random
import sge.grammar as grammar
from sge.parameters import params

def crossover(p1, p2):
    xover_p_value = 0.5
    gen_size = len(p1['genotype'])
    mask = [random.random() for i in range(gen_size)]
    genotype = []
    for index, prob in enumerate(mask):
        if prob < xover_p_value:
            genotype.append(p1['genotype'][index][:])
        else:
            genotype.append(p2['genotype'][index][:])
    mapping_values = [0] * gen_size
    # check parent with highest fitness
    # off spring inherits the grammar of the best fitted parent
    gram = p1['grammar'] if p1['fitness'] < p2['fitness'] else p2['grammar']
    mutation_prob = p1['mutation_prob'] if p1['fitness'] < p2['fitness'] else p2['mutation_prob']    

   
    # compute nem individual
    _, tree_depth = grammar.mapping(genotype, gram, mapping_values)
    return {'genotype': genotype, 'fitness': None, 'mapping_values': mapping_values, 'tree_depth': tree_depth, 'grammar': gram, 'mutation_prob': mutation_prob}
