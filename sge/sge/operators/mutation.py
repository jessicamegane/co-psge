import copy
import numpy as np
import sge.grammar as grammar
from sge.parameters import params

def mutate(p, pmutation):
    p = copy.deepcopy(p)
    p['fitness'] = None
    size_of_genes = grammar.count_number_of_options_in_production()
    mutable_genes = [index for index, nt in enumerate(grammar.get_non_terminals()) if size_of_genes[nt] != 1 and len(p['genotype'][index]) > 0]
    for at_gene in mutable_genes:
        nt = list(grammar.get_non_terminals())[at_gene]
        temp = p['mapping_values']
        mapped = temp[at_gene]
        for position_to_mutate in range(0, mapped):
            if np.random.uniform() < pmutation:
                current_value = p['genotype'][at_gene][position_to_mutate]
                # gaussian mutation
                codon = np.random.normal(current_value[1], 0.5)
                codon = min(codon,1.0)
                codon = max(codon,0.0)
                if p['tree_depth'] >= grammar.get_max_depth():
                    prob_non_recursive = 0.0
                    for rule in grammar.get_shortest_path()[(nt,'NT')][1:]:
                        index = grammar.get_dict()[nt].index(rule)
                        prob_non_recursive += p['pcfg'][grammar.get_index_of_non_terminal()[nt],index]
                    prob_aux = 0.0
                    for rule in grammar.get_shortest_path()[(nt,'NT')][1:]:
                        index = grammar.get_dict()[nt].index(rule)
                        if prob_non_recursive == 0.0: 
                            # when the probability of choosing the symbol is 0
                            new_prob = 1.0 / len(grammar.get_shortest_path()[(nt,'NT')][1:])
                        else:
                            new_prob = p['pcfg'][grammar.get_index_of_non_terminal()[nt],index] / prob_non_recursive
                        prob_aux += new_prob
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                else:
                    prob_aux = 0.0
                    for index, option in enumerate(grammar.get_dict()[nt]):
                        prob_aux += p['pcfg'][grammar.get_index_of_non_terminal()[nt],index]
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                  
                p['genotype'][at_gene][position_to_mutate] = [expansion_possibility, codon]
    return p

def get_mutation_probability_from_p_grammar(grammar):
    pmutation = []
    for rule in grammar:
        rule_mutation_probability = rule[1]
        pmutation.append(rule_mutation_probability)
    return pmutation

def mutate_level(p):
    p = copy.deepcopy(p)
    p['fitness'] = None
    pmutation = p['mutation_probs']
    size_of_genes = grammar.count_number_of_options_in_production()
    mutable_genes = [index for index, nt in enumerate(grammar.get_non_terminals()) if size_of_genes[nt] != 1 and len(p['genotype'][index]) > 0]
    for at_gene in mutable_genes:
        nt = list(grammar.get_non_terminals())[at_gene]
        temp = p['mapping_values']
        mapped = temp[at_gene]
        for position_to_mutate in range(0, mapped):
            if np.random.uniform() < pmutation[at_gene]:
                current_value = p['genotype'][at_gene][position_to_mutate]
                # codon = random.random()
                # gaussian mutation
                codon = np.random.normal(current_value[1], 0.5)
                codon = min(codon,1.0)
                codon = max(codon,0.0)
                expansion_possibility = 0
                if p['tree_depth'] >= grammar.get_max_depth():
                    prob_non_recursive = 0.0
                    for rule in grammar.get_shortest_path()[(nt,'NT')][1:]:
                        index = grammar.get_dict()[nt].index(rule)
                        prob_non_recursive += grammar.get_pcfg()[grammar.get_index_of_non_terminal()[nt],index]
                    prob_aux = 0.0
                    for rule in grammar.get_shortest_path()[(nt,'NT')][1:]:
                        index = grammar.get_dict()[nt].index(rule)
                        if prob_non_recursive == 0.0: 
                            # when the probability of choosing the symbol is 0
                            new_prob = 1.0 / len(grammar.get_shortest_path()[(nt,'NT')][1:])
                        else:
                            new_prob = grammar.get_pcfg()[grammar.get_index_of_non_terminal()[nt],index] / prob_non_recursive
                        prob_aux += new_prob
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                else:
                    prob_aux = 0.0
                    for index, option in enumerate(grammar.get_dict()[nt]):
                        prob_aux += p['pcfg'][grammar.get_index_of_non_terminal()[nt],index]
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                  
                p['genotype'][at_gene][position_to_mutate] = [expansion_possibility, codon]

def mutation_prob_mutation(ind):
    '''
    Code to mutate the array that contains the probabilities of mutating each non-terminal (mutation_probs).
    '''
    mutation_probabilities = ind['mutation_probs']
    new_p = []
    for nt in mutation_probabilities:
        if np.random.uniform() < params['PROB_MUTATION_PROBS']:
            gauss = np.random.normal(0.0,params['GAUSS_SD'])
            nt = max(nt+gauss,0)
            nt = min(nt,1)
        new_p.append(nt)
    ind['mutation_probs'] = new_p
    return ind
