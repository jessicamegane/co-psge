import re
from sge.utilities import ordered_set
import json
import numpy as np

class Grammar:
    """Class that represents a grammar. It works with the prefix notation."""
    NT = "NT"
    T = "T"
    NT_PATTERN = "(<.+?>)"
    RULE_SEPARATOR = "::="
    PRODUCTION_SEPARATOR = "|"

    def __init__(self):
        self.grammar_file = None
        self.grammar = {}
        self.productions_labels = {}
        self.non_terminals, self.terminals = set(), set()
        self.ordered_non_terminals = ordered_set.OrderedSet()
        self.non_recursive_options = {}
        self.number_of_options_by_non_terminal = None
        self.start_rule = None
        self.max_depth = None
        self.max_init_depth = None
        self.max_number_prod_rules = 0
        self.pcfg = None
        self.pcfg_mask = None
        self.pcfg_path = None
        self.index_of_non_terminal = {}

    def set_path(self, grammar_path):
        self.grammar_file = grammar_path

    def set_pcfg_path(self, pcfg_path):
        self.pcfg_path = pcfg_path

    def get_non_recursive_options(self):
        return self.non_recursive_options

    def set_min_init_tree_depth(self, min_tree_depth):
        self.max_init_depth = min_tree_depth

    def set_max_tree_depth(self, max_tree_depth):
        self.max_depth = max_tree_depth

    def get_max_depth(self):
        return self.max_depth
    
    def get_max_init_depth(self):
        return self.max_init_depth

    def read_grammar(self):
        """
        Reads a Grammar in the BNF format and converts it to a python dictionary
        This method was adapted from PonyGE version 0.1.3 by Erik Hemberg and James McDermott
        """
        if self.grammar_file is None:
            raise Exception("You need to specify the path of the grammar file")


        with open(self.grammar_file, "r") as f:
            for line in f:
                if not line.startswith("#") and line.strip() != "":
                    if line.find(self.PRODUCTION_SEPARATOR):
                        left_side, productions = line.split(self.RULE_SEPARATOR)
                        left_side = left_side.strip()
                        if not re.search(self.NT_PATTERN, left_side):
                            raise ValueError("Left side not a non-terminal!")
                        self.non_terminals.add(left_side)
                        self.ordered_non_terminals.add(left_side)
                        # assumes that the first rule in the file is the axiom
                        if self.start_rule is None:
                            self.start_rule = (left_side, self.NT)
                        temp_productions = []
                        for production in [production.strip() for production in productions.split(self.PRODUCTION_SEPARATOR)]:
                            temp_production = []
                            if not re.search(self.NT_PATTERN, production):
                                if production == "None":
                                    production = ""
                                self.terminals.add(production)
                                temp_production.append((production, self.T))
                            else:
                                for value in re.findall("<.+?>|[^<>]*", production):
                                    if value != "":
                                        if re.search(self.NT_PATTERN, value) is None:
                                            sym = (value, self.T)
                                            self.terminals.add(value)
                                        else:
                                            sym = (value, self.NT)
                                        temp_production.append(sym)
                            temp_productions.append(temp_production)                          
                        self.max_number_prod_rules = max(self.max_number_prod_rules, len(temp_productions))
                        if left_side not in self.grammar:
                            self.grammar[left_side] = temp_productions
        
        self.compute_non_recursive_options()

        if self.pcfg_path is not None:
            # load PCFG probabilities from json file. List of lists, n*n, with n = max number of production rules of a NT
            with open(self.pcfg_path) as f:
                self.pcfg = np.array(json.load(f))
        else:
            self.generate_uniform_pcfg()


    def create_counter(self):
        self.counter = dict.fromkeys(self.grammar.keys(),[])
        for k in self.counter.keys():
            self.counter[k] = [0] * len(self.grammar[k])

    def generate_uniform_pcfg(self):
        """
        assigns uniform probabilities to grammar
        """
        array = np.zeros(shape=(len(self.grammar.keys()),self.max_number_prod_rules))
        for i, nt in enumerate(self.grammar):
            number_probs = len(self.grammar[nt])
            prob = 1.0 / number_probs
            array[i,:number_probs] = prob
            if nt not in self.index_of_non_terminal:
                self.index_of_non_terminal[nt] = i
        self.pcfg = array
        self.pcfg_mask = self.pcfg != 0


    def generate_random_pcfg(self):
        pass

    def get_mask(self):
        return self.pcfg_mask

    def get_index_of_non_terminal(self):
        return self.index_of_non_terminal

    def get_non_terminals(self):
        return self.ordered_non_terminals

    def count_number_of_options_in_production(self):
        if self.number_of_options_by_non_terminal is None:
            self.number_of_options_by_non_terminal = {}
            for nt in self.ordered_non_terminals:
                self.number_of_options_by_non_terminal.setdefault(nt, len(self.grammar[nt]))
        return self.number_of_options_by_non_terminal

    def compute_non_recursive_options(self):
        self.non_recursive_options = {}
        for nt in self.ordered_non_terminals:
            choices = []
            for nrp in self.list_non_recursive_productions(nt):
                choices.append(self.grammar[nt].index(nrp))
            self.non_recursive_options[nt] = choices

    def list_non_recursive_productions(self, nt):
        non_recursive_elements = []
        for options in self.grammar[nt]:
            for option in options:
                if option[1] == self.NT and option[0] == nt:
                    break
            else:
                non_recursive_elements += [options]
        return non_recursive_elements

    def recursive_individual_creation(self, genome, symbol, current_depth, gram):
        codon = np.random.uniform()

        if current_depth > self.max_init_depth:
            non_recursive_prods, prob_non_recursive = self.get_non_recursive_productions(gram, symbol)
            prob_aux = 0.0

            for index, option in non_recursive_prods:
                if prob_non_recursive == 0.0:
                    new_prob = 1.0 / len(non_recursive_prods)
                else:
                    new_prob = (gram[self.index_of_non_terminal[symbol],index] * 1.0) / prob_non_recursive
                prob_aux += new_prob
                if codon <= round(prob_aux,3):
                    expansion_possibility = index
                    break
        else:
            prob_aux = 0.0
            for index, option in enumerate(self.grammar[symbol]):
                prob_aux += gram[self.index_of_non_terminal[symbol],index]
                if codon <= round(prob_aux,3):
                    expansion_possibility = index
                    break

        genome[self.get_non_terminals().index(symbol)].append([expansion_possibility,codon])
        expansion_symbols = self.grammar[symbol][expansion_possibility]
        depths = [current_depth]
        for sym in expansion_symbols:
            if sym[1] != self.T:
                depths.append(self.recursive_individual_creation(genome, sym[0], current_depth + 1, gram))
        return max(depths)

    def mapping(self, mapping_rules, gram, positions_to_map=None, needs_python_filter=False):
        if positions_to_map is None:
            positions_to_map = [0] * len(self.ordered_non_terminals)
        output = []
        max_depth = self._recursive_mapping(mapping_rules, positions_to_map, self.start_rule, 0, output, gram)
        output = "".join(output)
        if self.grammar_file.endswith("pybnf"):
            output = self.python_filter(output)
        return output, max_depth

    def _recursive_mapping(self, mapping_rules, positions_to_map, current_sym, current_depth, output, gram):
        depths = [current_depth]
        if current_sym[1] == self.T:
            output.append(current_sym[0])
        else:
            current_sym_pos = self.ordered_non_terminals.index(current_sym[0])
            choices = self.grammar[current_sym[0]]
            codon = np.random.uniform()
            if positions_to_map[current_sym_pos] >= len(mapping_rules[current_sym_pos]):
                # Experiencia
                if current_depth > self.max_depth:
                    non_recursive_prods, prob_non_recursive = self.get_non_recursive_productions(gram, current_sym[0])
                    prob_aux = 0.0
                    for index, option in non_recursive_prods:
                        if prob_non_recursive == 0.0:
                            new_prob = 1.0 / len(non_recursive_prods)
                        else:
                            new_prob = ((gram[self.index_of_non_terminal[current_sym[0]],index] * 1.0) / prob_non_recursive)
                        prob_aux += new_prob
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                else:
                    prob_aux = 0.0
                    for index, option in enumerate(self.grammar[current_sym[0]]):
                        prob_aux += gram[self.index_of_non_terminal[current_sym[0]],index]
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                mapping_rules[current_sym_pos].append([expansion_possibility,codon])
            else:
                # re-mapping with new probabilities                
                codon = mapping_rules[current_sym_pos][positions_to_map[current_sym_pos]][1]
                if current_depth > self.max_depth:
                    non_recursive_prods, prob_non_recursive = self.get_non_recursive_productions(gram, current_sym[0])    
                    prob_aux = 0.0
                    for index, option in non_recursive_prods:
                        if prob_non_recursive == 0.0:
                            new_prob = 1.0 / len(non_recursive_prods)
                        else:
                            new_prob = ((gram[self.index_of_non_terminal[current_sym[0]],index] * 1.0) / prob_non_recursive)
                        prob_aux += new_prob
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
                else:
                    prob_aux = 0.0
                    for index, option in enumerate(self.grammar[current_sym[0]]):
                        prob_aux += gram[self.index_of_non_terminal[current_sym[0]],index]
                        if codon <= round(prob_aux,3):
                            expansion_possibility = index
                            break
            # update mapping rules com a updated expansion possibility
            mapping_rules[current_sym_pos][positions_to_map[current_sym_pos]] = [expansion_possibility, codon]
            current_production = expansion_possibility
            positions_to_map[current_sym_pos] += 1
            next_to_expand = choices[current_production]
            for next_sym in next_to_expand:
                depths.append(
                    self._recursive_mapping(mapping_rules, positions_to_map, next_sym, current_depth + 1, output, gram))
        return max(depths)

    def get_non_recursive_productions(self, gram, symbol):
        prob_non_recursive = 0.0
        non_recursive_prods = []
        for index, option in enumerate(self.grammar[symbol]):
            for s in option:
                if s[0] == symbol:
                    break
            else:
                prob_non_recursive += gram[self.index_of_non_terminal[symbol],index]
                non_recursive_prods.append([index, option])
        return non_recursive_prods, prob_non_recursive

    def get_dict(self):
        return self.grammar

    def get_pcfg(self):
        return self.pcfg

    @staticmethod
    def python_filter(txt):
        """ Create correct python syntax.
        We use {: and :} as special open and close brackets, because
        it's not possible to specify indentation correctly in a BNF
        grammar without this type of scheme."""
        txt = txt.replace("\le", "<=")
        txt = txt.replace("\ge", ">=")
        txt = txt.replace("\l", "<")
        txt = txt.replace("\g", ">")
        txt = txt.replace("\eb", "|")
        indent_level = 0
        tmp = txt[:]
        i = 0
        while i < len(tmp):
            tok = tmp[i:i+2]
            if tok == "{:":
                indent_level += 1
            elif tok == ":}":
                indent_level -= 1
            tabstr = "\n" + "  " * indent_level
            if tok == "{:" or tok == ":}" or tok == "\\n":
                tmp = tmp.replace(tok, tabstr, 1)
            i += 1
            # Strip superfluous blank lines.
            txt = "\n".join([line for line in tmp.split("\n") if line.strip() != ""])
        return txt

    def get_start_rule(self):
        return self.start_rule

    def __str__(self):
        grammar = self.grammar
        text = ""
        for key in self.ordered_non_terminals:
            text += key + " ::= "
            for options in grammar[key]:
                for option in options:
                    text += option[0]
                if options != grammar[key][-1]:
                    text += " | "
            text += "\n"
        return text

# Create one instance and export its methods as module-level functions.
# The functions share state across all uses
# (both in the user's code and in the Python libraries), but that's fine
# for most programs and is easier for the casual user


_inst = Grammar()
set_path = _inst.set_path
set_pcfg_path = _inst.set_pcfg_path
read_grammar = _inst.read_grammar
get_non_terminals = _inst.get_non_terminals
count_number_of_options_in_production = _inst.count_number_of_options_in_production
compute_non_recursive_options = _inst.compute_non_recursive_options
list_non_recursive_productions = _inst.list_non_recursive_productions
recursive_individual_creation = _inst.recursive_individual_creation
mapping = _inst.mapping
start_rule = _inst.get_start_rule
set_max_tree_depth = _inst.set_max_tree_depth
set_min_init_tree_depth = _inst.set_min_init_tree_depth
get_max_depth = _inst.get_max_depth
get_non_recursive_options = _inst.get_non_recursive_options
get_dict = _inst.get_dict
get_pcfg = _inst.get_pcfg
get_mask = _inst.get_mask
get_index_of_non_terminal = _inst.get_index_of_non_terminal
ordered_non_terminals = _inst.ordered_non_terminals
max_init_depth = _inst.get_max_init_depth
python_filter = _inst.python_filter
get_non_recursive_productions = _inst.get_non_recursive_productions

if __name__ == "__main__":
    np.random.seed(42)
    g = Grammar("grammars/regression.txt", 9)
    genome = [[0], [0, 3, 3], [0], [], [1, 1]]
    mapping_numbers = [0] * len(genome)
    print(g.mapping(genome, mapping_numbers, needs_python_filter=True))

