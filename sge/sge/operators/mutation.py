import copy
import random
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
            if random.random() < pmutation:
                current_value = p['genotype'][at_gene][position_to_mutate]
                # codon = random.random()
                # gaussian mutation
                codon = random.gauss(current_value[1], 0.5)
                codon = min(codon,1.0)
                codon = max(codon,0.0)
                expansion_possibility = 0
                if p['tree_depth'] >= grammar.get_max_depth():
                    non_recursive_prods, prob_non_recursive = grammar.get_non_recursive_productions(nt)    
                    prob_aux = 0.0
                    for index, option in non_recursive_prods:
                        new_prob = (option[1] * 1.0) / prob_non_recursive
                        prob_aux += new_prob

                        if codon < prob_aux:
                            expansion_possibility = index
                            break
                else:
                    prob_aux = 0.0
                    for index, option in enumerate(grammar.get_dict()[nt]):
                        prob_aux += option[1]
                        if codon < prob_aux:
                            expansion_possibility = index
                            break
                  
                p['genotype'][at_gene][position_to_mutate] = [expansion_possibility, codon]
    return p
