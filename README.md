# Co-evolutionary Probabilistic Structured Grammatical Evolution python3 code

Co-evolutionary Probabilistic Structured Grammatical Evolution (Co-PSGE) is an extension to Structured Grammatical Evolution (SGE).

In Co-PSGE each individual in the population is composed by a grammar and a genotype, which is a list of dynamic lists, each corresponding to a non-terminal of the grammar containing real numbers that correspond to the probability of choosing a derivation rule. Each individual uses its own grammar to map the genotype into a program. During the evolutionary process both the grammar and the genotype are subject to variation operators.

A more in-depth explanation of the method and an analysis of its performance can be found in the [article](https://jessicamegane.pt/files/gecco_copsge.pdf), published at the Genetic and Evolutionary Computation Conference 2022 (GECCO). If you use this code, a reference to the following work would be greatly appreciated:

```
@inproceedings{megane2022copsge,
author = {M\'{e}gane, Jessica and Louren\c{c}o, Nuno and Machado, Penousal},
title = {Co-Evolutionary Probabilistic Structured Grammatical Evolution},
year = {2022},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3512290.3528833},
doi = {10.1145/3512290.3528833},
}

```


### Requirements
This code needs python3.5 or a newer version. More detail on the required libraries can be found in the `requirements.txt` file.

### Execution

Like all grammar-based Evolutionary Algorithms, to run the algorithm to solve a problem you need a **grammar** and a **fitness function**.
The folder `examples/` contains the code for some benchmark problems used in Genetic Programming, and the folder ``grammars/`` contain the respective grammars. To run, for example, a Symbolic Regression problem, you can use the following command:

```
python3 -m examples.symreg --grammar grammars/regression.pybnf
```

#### Parameters

The folder `parameters/` contains an example of standard parameters to run. You can define the parameters on a file and specify them when executing the code. For example:

```
python3 -m examples.symreg --grammar grammars/regression.pybnf --parameters parameters/standard.yml
```

You can also add manually more parameters when calling the code without changing the parameter file. Here is an example where we define the seed:

```
python3 -m examples.symreg --grammar grammars/regression.pybnf --parameters parameters/standard.yml --seed 123
```

If you need to know the possible parameters, you can use the flag ``--help``. For example:
```
python -m examples.symreg --help
```

Here is the list of possible parameters, and how to call them.

| argument | type | description |
| --------------- | ----------- | ------------ |
| --parameters | str | Specifies the parameters file to be used. Must include the full file extension. | 
| --popsize | int | Specifies the population size. |
| --generations | int | Specifies the total number of generations.
| --elitism | int | Specifies the total number of individuals that should survive in each generation. |
| --prob_crossover | float | Specifies the probability of crossover usage. Float required. |
| --prob_mutation | float | Specifies the probability of mutation usage. Float required. |
| --tsize | int | Specifies the tournament size for parent selection. |
| --min_tree_depth | int | Specifies the initialisation tree depth. |
| --max_tree_depth | int | Specifies the maximum tree depth. |
| --grammar | str | pecifies the path to the grammar file. |
| --grammar_probs | str | Path to file that has a list of probabilities to initialisate the grammars. Otherwise it starts with uniform distribution for each non-terminal. Json file required. | 
| --mutate_grammar | bool | Specifies if we want the grammars to mutate. |
| --prob_mutation_grammar | float | Specifies the probability of occurring a mutation in the grammar of each individual. |
| --normal_dist_sd | float | Specifies the value of the standard deviation used in the generation of a number with a normal distribution. |
| --adaptive_mutation | bool | Specifies if we want to use the traditional mutation or the Adaptive Facilitated Mutation. |
| --prob_mutation_probs | float | Specifies the probability of occurring a mutation in the prob mutation. Option only if --adaptive_mutation is set to true. |
| --gauss_sd | float | Specifies the value of the standard deviation used in the generation of a number with a normal distribution. Option only if --adaptive_mutation is set to true. |
| --experiment_name | str | Specifies the name of the folder where stats are going to be stored. |
| --run | int | Specifies the run number. |
| --seed | float | Specifies the seed to be used by the random number generator. |
| --include_genotype | bool | Specifies if the genotype is to be included in the log files |
| --save_step | int | Specifies how often stats are saved. |
| --verbose | bool | Turns on the verbose output of the program. |

### Mutation

This code supports two types of mutations.

- The *standard mutation* consists in changing the values in the genotype according to the **PROB_MUTATION** parameter.
- The *adaptive facilitated mutation* can be enabled by setting the **ADAPTIVE_MUTATION** parameter to True. This mutation evolves different probabilities of mutation for each non-terminal of the grammar. Each individual contains a different array with probabilities of mutation for each non-terminal. The array starts with equal values for each non-terminal, pre-defined with the parameter **PROB_MUTATION**. They update each genaration based on the **PROB_MUTATION_PROBS** parameter, which defines the likelihood of the values suffering an alteration, and the **GAUSS_SD** parameter which defines the impact of those changes.
The Adaptive Facilitated Mutation was publised and presented in the EuroGP 2023 conference, you can read the full paper [here](https://jessicamegane.pt/files/eurogp_afm.pdf). If you use this mutation please cite our paper.


### Support

Any questions, comments or suggestion should be directed to Jessica Mégane ([jessicac@dei.uc.pt](mailto:jessicac@dei.uc.pt)) or Nuno Lourenço ([naml@dei.uc.pt](mailto:naml@dei.uc.pt)).


## References

O'Neill, M. and Ryan, C. "Grammatical Evolution: Evolutionary Automatic Programming in an Arbitrary Language", Kluwer Academic Publishers, 2003.

Fenton, M., McDermott, J., Fagan, D., Forstenlechner, S., Hemberg, E., and O'Neill, M. PonyGE2: Grammatical Evolution in Python. arXiv preprint, arXiv:1703.08535, 2017.

Lourenço, N., Assunção, F., Pereira, F. B., Costa, E., and Machado, P.. Structured Grammatical Evolution: A Dynamic Approach. In Handbook of Grammatical Evolution. Springer Int, 2018.

Mégane, J., Lourenço, N., and Machado, P.. Probabilistic Grammatical Evolution. In Genetic Programming, Ting Hu, Nuno Lourenço, and Eric Medvet (Eds.). Springer International Publishing, Cham, 198–213, 2021.

Carvalho, P., Mégane, J., Lourenço, N., Machado, P. (2023). Context Matters: Adaptive Mutation for Grammars. In: Pappa, G., Giacobini, M., Vasicek, Z. (eds) Genetic Programming. EuroGP 2023. Lecture Notes in Computer Science, vol 13986. Springer, Cham.