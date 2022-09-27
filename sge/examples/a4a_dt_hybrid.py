"""
Code from Francisco Miranda (Github @FMiranda97)
"""
import math
import os
import random
import sqlite3
import sys

import numpy as np
import pandas as pd
import scipy.optimize
import sklearn.metrics as mt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from jsonAnalyserv2 import load_dumps_to_db
from sge.parameters import params
from sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv
from numpy import cos, sin

from tree_visualization import decision_tree_to_pdf


def _add_(x, y):
    return x + y


def _sub_(x, y):
    return x - y


def _mul_(x, y):
    return x * y


def is_positive(x):
    return 1 if x > 0 else 0


def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


def sig(x):
    return 1 / (1 + math.exp(-x))


saved_errors = {'count': 0}


def diff_evo_fit(parameters, *args):
    new_indiv = args[0] % tuple(parameters)
    error = saved_errors.get(new_indiv)
    if error is None:
        error = get_error(new_indiv, args[1], args[2], metric=args[3])
        saved_errors[new_indiv] = error
    else:
        saved_errors['count'] += 1
    return error


def get_error(individual, X, y, metric="f1"):
    indiv_lambda = eval('lambda x:' + individual)
    predicted = np.apply_along_axis(indiv_lambda, 1, X)

    if metric == "accuracy":
        return 1 - mt.accuracy_score(y, predicted)
    elif metric == "f1":
        return 1 - mt.f1_score(y, predicted)


def get_test_error(individual, X, y):
    indiv_lambda = eval('lambda x:' + individual)
    predicted = np.apply_along_axis(indiv_lambda, 1, X)

    accuracy = mt.accuracy_score(y, predicted)
    precision = mt.precision_score(y, predicted, zero_division=0)
    recall = mt.recall_score(y, predicted, zero_division=0)
    f1 = mt.f1_score(y, predicted, zero_division=0)
    auc = mt.roc_auc_score(y, predicted)

    return accuracy, f1, precision, recall, auc


def balanced_dataset_extraction(X, y, n):
    idx = []
    y_idx = np.arange(len(y))
    for c in np.unique(y):
        idx.extend(np.random.choice(y_idx[y == c], n, replace=False))
    remaining_idx = list(set(y_idx) - set(idx))
    X_out = X[idx]
    y_out = y[idx]
    X_rem = X[remaining_idx]
    y_rem = y[remaining_idx]

    return X_out, X_rem, y_out, y_rem


class A4A:
    def __init__(self, seed=42, has_test_set=True, invalid_fitness=9999999, metric="f1"):
        self.__train_set_X = []
        self.__train_set_y = []
        self.__val_set_X = []
        self.__val_set_y = []
        self.__test_set_X = []
        self.__test_set_y = []
        self.__invalid_fitness = invalid_fitness
        self.has_test_set = has_test_set
        self.metric = metric
        self.read_dataset(seed)

    def read_dataset(self, seed):
        import pandas as pd
        df = pd.read_csv('resources/Audiology/a4a_reduced_dataset.csv')
        X = df.drop('corrected_diagnosed_hl', axis=1).iloc[:, 1:].values.tolist()
        y = np.array(df['corrected_diagnosed_hl'])

        X = StandardScaler().fit_transform(X, y)

        if self.metric == "accuracy":
            X_val, X_remaining, y_val, y_remaining = balanced_dataset_extraction(X, y, 2500)
            X_test, X_train, y_test, y_train = balanced_dataset_extraction(X_remaining, y_remaining, 2500)
        else:
            X_remaining, X_test, y_remaining, y_test = train_test_split(X, y, test_size=5000)
            X_val, X_train, y_val, y_train = train_test_split(X_remaining, y_remaining, train_size=5000)
        self.__train_set_X = X_train
        self.__train_set_y = y_train
        self.__val_set_X = X_val
        self.__val_set_y = y_val
        self.__test_set_X = X_test
        self.__test_set_y = y_test
        self.X = self.y = []
        self.generation = -1

    def get_training_set(self, n_samples, generation):
        if self.generation < generation:
            self.X, _, self.y, _ = balanced_dataset_extraction(self.__train_set_X, self.__train_set_y, n_samples//2)
            self.generation = generation
        return self.X, self.y

    def evaluate(self, individual, generation):
        if individual is None:
            return None

        n_param = individual.count('%f')

        X, y = self.get_training_set(1000, generation)
        if n_param > 0:
            bounds = [(-3, 3) for _ in range(n_param)]
            global saved_errors
            saved_errors = {'count': 0}
            res = scipy.optimize.differential_evolution(diff_evo_fit, bounds, args=(individual, X, y, self.metric), polish=True, mutation=(0.01, 0.2), maxiter=20, popsize=len(bounds))
            # error = res['fun'] # ignore DE error during SGE, validation set error is considered instead
            weights = tuple(res['x'])
            individual = individual % weights
            error = get_error(individual, self.__val_set_X, self.__val_set_y, metric=self.metric)
        else:
            weights = ()
            error = get_error(individual, self.__val_set_X, self.__val_set_y, metric=self.metric)

        if self.__test_set_X is not None:
            accuracy, f1, precision, recall, auc = get_test_error(individual, self.__test_set_X, self.__test_set_y)
        else:
            accuracy, f1, precision, recall, auc = -1, -1, -1, -1, -1

        return error, {'accuracy': accuracy, 'f1': f1, 'precision': precision, 'recall': recall, 'auc': auc, 'weights': weights, 'n_nodes': individual.count('if')}


if __name__ == "__main__":
    import sge
    metric = 'accuracy'

    sge.setup("parameters/standard_a4a.yml")
    seed = params['RUN']
    eval_func = A4A(seed=seed, metric=metric)
    sge.evolutionary_algorithm(evaluation_function=eval_func)

    load_dumps_to_db(strategy='append', runs=['run_%d' % seed])


    conn = sqlite3.connect('dumps.db')
    df = pd.read_sql("select phenotype, weights, max(accuracy) as accuracy from dumps where seed = ? group by seed", conn, params=(seed,))
    print('Obtained accuracy of: %.1f%%' % (df['accuracy'][0] * 100))
    print('Visualization available in file tree_graphs/tree_%d.gv.pdf' % seed)
    decision_tree_to_pdf(df['phenotype'][0] % tuple(eval(df['weights'][0])), 'tree_%d' % seed)
