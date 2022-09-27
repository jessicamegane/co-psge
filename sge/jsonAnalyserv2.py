"""
Code from Francisco Miranda (Github @FMiranda97)
"""

import os
import json
from typing import Dict, List, Union
import numpy as np
from parse import parse
import pandas as pd
import sqlite3
import scipy.stats as st
import seaborn as sn
import matplotlib.pyplot as plt


def get_parameters():
    parameters_file = open('parameters.json')
    return json.loads(parameters_file.readline())


def get_generation(generation_file_name):
    generation_file = open(generation_file_name)
    return json.loads(generation_file.readline())


def push_params(data: Dict[str, List], params: Dict[str, Union[str, int, float]]):
    for k, v in params.items():
        data.setdefault(k, [])
        data[k].append(str(v) if type(v) is list else v)


def extract_info(individual):
    info = {k: v for k, v in individual.items()}
    other_info = {k: v for k, v in individual['other_info'].items()}
    info.update(other_info)
    info.pop('other_info')
    return info


def digest_population(gen: List[Dict[str, Union[str, int, float]]]):
    population = [{k: v for k, v in extract_info(individual).items() if type(v) is float} for individual in gen]
    pop_digest = {
        ('population_%s' % k):
            np.mean([x[k] for x in population])
        for k in population[0].keys()
    }
    return pop_digest


def analyse_generations(data: Dict[str, List], params: Dict[str, Union[str, int, float]]):
    files = os.listdir()
    if len(files) < params['generations'] + 1:
        print("\t\t>>>> Skipping incomplete run")
        return
    for file in filter(lambda x: x.startswith('iteration'), files):
        generation = int(parse('iteration_{}.json', file)[0])
        if generation > params['generations']:
            continue
        print("\t\t\t%s" % file)
        gen_data = get_generation(file)
        info_best_individual = extract_info(gen_data[0])
        pop_digest = digest_population(gen_data)
        pop_digest['generation'] = int(parse('iteration_{}.json', file)[0])
        push_params(data, params)
        push_params(data, info_best_individual)
        push_params(data, pop_digest)


def load_dumps_to_db(strategy='replace', runs=None):
    if runs is None:
        runs = os.listdir()
    data = {}
    os.chdir('dumps')
    for experiment in os.listdir():
        print("%s" % experiment)
        os.chdir(experiment)
        for run in runs:
            print("\t\t%s" % run)
            os.chdir(run)
            params = get_parameters()
            analyse_generations(data, params)
            os.chdir('..')
        os.chdir('..')
    os.chdir('..')
    df = pd.DataFrame(data)
    con = sqlite3.connect('dumps.db')
    df.to_sql('dumps', con, if_exists=strategy, index=False)


def analyse_dumps(conn):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)

    relevant_cols = ['fitness', 'accuracy', 'f1', 'precision', 'recall']
    population_cols = ['population_%s' % x for x in relevant_cols if x != 'generations']

    df = pd.read_sql("select * from dumps where experiment_name == 'dumps/tie_breaks/accuracy'", conn)
    df['fitness'] = 1 - df['fitness']
    df['population_fitness'] = 1 - df['population_fitness']

    print("Best individuals at each generation")
    print(df[relevant_cols].describe())

    print("\nPopulation's average")
    print(df[population_cols].describe())

    for metric in relevant_cols:
        ax = sn.lineplot(
            data=df,
            x='generation',
            y=metric,
            hue=['Best Individual' for _ in range(len(df[metric]))],
            palette=['r']
        )
        if metric == 'fitness':
            ax = sn.lineplot(
                data=df,
                x='generation',
                y='population_%s' % metric,
                hue=['Population Average' for _ in range(len(df[metric]))],
                palette=['g'],
                linestyle='dashed'
            )
            ax.legend().get_lines()[1].set_linestyle('--')
            plt.title('Average %s over the generations for all runs' % metric.capitalize())
        else:
            plt.title('Average %s of the best individual over the generations for all runs' % metric.capitalize())
            plt.legend([],[], frameon=False)
        plt.show()

    pd.set_option('display.float_format', lambda x: '& %.3f' % x)

    df = pd.read_sql("select max(1 - fitness) as fitness, accuracy, f1, precision, recall, n_nodes from dumps group by run", conn)
    df['depth_estimate'] = np.log2(df["n_nodes"]) + 1
    print("\nBest individuals at each run")
    print(df.describe())
    for col in relevant_cols + ["n_nodes", "depth_estimate"]:
        a = df[col]
        interval = st.t.interval(0.95, len(a) - 1, loc=np.mean(a), scale=st.sem(a))
        # print("\n%s: %s" % (col, interval))
        print("& [%0.3f; %0.3f]" % (interval[0], interval[1]), end=" ")


if __name__ == '__main__':
    # load_dumps_to_db()
    conn = sqlite3.connect('dumps.db')
    analyse_dumps(conn)
