# Co-evolutionary Probabilistic Structured Grammatical Evolution python3 code

Co-evolutionary Probabilistic Structured Grammatical Evolution (Co-PSGE) is an extension to Structured Grammatical Evolution (SGE).

In Co-PSGE each individual in the population is composed by a grammar and a genotype, which is a list of dynamic lists, each corresponding to a non-terminal of the grammar containing real numbers that correspond to the probability of choosing a derivation rule. Each individual uses its own grammar to map the genotype into a program. During the evolutionary process both the grammar and the genotype are subject to variation operators.

A more in-depth explanation of the method and an analysis of its performance can be found in the article, soon to be publicly available. If you want a pre-print version you can send us an e-mail.


### Requirements
This code needs python3.5 or a newer version. More detail on the required libraries can be found in the `requirements.txt` file.

### Execution

The folder `examples/` contains the code for some benchmark problems used in GP. To run, for example, Symbolic Regression, you can use the following command:

```python3 -m examples.symreg --experiment_name dumps/example --seed 791021 --parameters parameters/standard.yml --grammars/regressiob.pybnf```



### Support

Any questions, comments or suggestion should be directed to Jessica Mégane ([naml@dei.uc.pt](mailto:naml@dei.uc.pt)) or Nuno Lourenço ([naml@dei.uc.pt](mailto:naml@dei.uc.pt)).


## References

O'Neill, M. and Ryan, C. "Grammatical Evolution: Evolutionary Automatic Programming in an Arbitrary Language", Kluwer Academic Publishers, 2003.

Fenton, M., McDermott, J., Fagan, D., Forstenlechner, S., Hemberg, E., and O'Neill, M. PonyGE2: Grammatical Evolution in Python. arXiv preprint, arXiv:1703.08535, 2017.

Lourenço, N., Assunção, F., Pereira, F. B., Costa, E., and Machado, P.. Structured Grammatical Evolution: A Dynamic Approach. In Handbook of Grammatical Evolution. Springer Int, 2018.

Mégane, J., Lourenço, N., and Machado, P.. Probabilistic Grammatical Evolution. In Genetic Programming, Ting Hu, Nuno Lourenço, and Eric Medvet (Eds.). Springer International Publishing, Cham, 198–213, 2021.