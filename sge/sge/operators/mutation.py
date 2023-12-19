import copy
import numpy as np
import sge.grammar as grammar

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
                current_depth = current_value[2]
                shortest_path = grammar.get_shortest_path()[(nt,'NT')]
                nt_index = grammar.get_index_of_non_terminal()[nt]
                # gaussian mutation
                codon = np.clip(np.random.normal(current_value[1], 0.5), 0.0, 1.0)
                if current_depth >= (grammar.get_max_depth() - shortest_path[0]):
                    sum_available_prods = 0.0
                    for rule in shortest_path[1:]:
                        index = grammar.get_dict()[nt].index(rule)
                        sum_available_prods += p['pcfg'][nt_index,index]
                    prob_aux = 0.0
                    for rule in shortest_path[1:]:
                        index = grammar.get_dict()[nt].index(rule)
                        if sum_available_prods == 0.0: 
                            # when the probability of choosing the symbol is 0, we use uniform probabilities
                            new_prob = 1.0 / len(shortest_path[1:])
                        else:
                            new_prob = p['pcfg'][nt_index,index] / sum_available_prods
                        prob_aux += new_prob
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                else:
                    prob_aux = 0.0
                    for index in range(len(grammar.get_dict()[nt])):
                        prob_aux += p['pcfg'][nt_index,index]
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                  
                p['genotype'][at_gene][position_to_mutate] = [expansion_possibility, codon, current_depth]
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
    pmutation = p['mutation_prob']
    size_of_genes = grammar.count_number_of_options_in_production()
    mutable_genes = [index for index, nt in enumerate(grammar.get_non_terminals()) if size_of_genes[nt] != 1 and len(p['genotype'][index]) > 0]
    for at_gene in mutable_genes:
        nt = list(grammar.get_non_terminals())[at_gene]
        temp = p['mapping_values']
        mapped = temp[at_gene]
        for position_to_mutate in range(0, mapped):
            if np.random.uniform() < pmutation[at_gene]:
                current_value = p['genotype'][at_gene][position_to_mutate]
                current_depth = current_value[2]
                shortest_path = grammar.get_shortest_path()[(nt,'NT')]
                nt_index = grammar.get_index_of_non_terminal()[nt]
                # codon = random.random()
                # gaussian mutation
                codon = np.clip(np.random.normal(current_value[1], 0.5), 0.0, 1.0)
                expansion_possibility = 0
                if current_depth >= grammar.get_max_depth():
                    sum_available_prods = 0.0
                    for rule in shortest_path[1:]:
                        index = grammar.get_dict()[nt].index(rule)
                        sum_available_prods += grammar.get_pcfg()[nt_index,index]
                    prob_aux = 0.0
                    for rule in shortest_path[1:]:
                        index = grammar.get_dict()[nt].index(rule)
                        if sum_available_prods == 0.0: 
                            # when the probability of choosing the symbol is 0
                            new_prob = 1.0 / len(shortest_path[1:])
                        else:
                            new_prob = grammar.get_pcfg()[nt_index,index] / sum_available_prods
                        prob_aux += new_prob
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                else:
                    prob_aux = 0.0
                    for index in range(len(grammar.get_dict()[nt])):
                        prob_aux += p['pcfg'][nt_index]
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                  
                p['genotype'][at_gene][position_to_mutate] = [expansion_possibility, codon]
    return p