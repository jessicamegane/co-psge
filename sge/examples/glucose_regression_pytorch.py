import re
import random
import pandas as pd
import torch
import numpy as np
from math import sin, cos, tan
from sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv, _pow_
from sge.utilities.pytorchtest import *

class RMSELoss(torch.nn.Module):
    def __init__(self):
        super(RMSELoss,self).__init__()

    def forward(self,x,y):
        criterion = torch.nn.MSELoss()
        loss = torch.sqrt(criterion(x, y))
        return loss

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


class GlucoseRegression():
    def __init__(self,
                 data_file=None,
                 apply_test_set=False,
                 invalid_fitness=9999999,
                 start_test_set=None):
        self.__train_set = None
        self.__test_set = None
        self.__start_test_set = start_test_set
        self.__apply_test_set = apply_test_set
        self.__invalid_fitness = invalid_fitness
        self.partition_rng = random.Random()
        self.read_data(data_file)

    def read_data(self, data_file):
        glucose_data = pd.read_csv(data_file, sep=";")
        self.__train_set = torch.tensor(glucose_data.iloc[
            0:self.__start_test_set, :].values, dtype=torch.float32, device=cur_dev)
        self.__test_set = torch.tensor(glucose_data.iloc[
            self.__start_test_set:, :].values, dtype=torch.float32, device=cur_dev)

    def get_error(self, individual, dataset):
        #print(individual)
        #print(dataset.size())
        code = compile('def corre(x): \n\t return %s' % individual, '<string>', 'exec')
        exec(code, globals())
        #print(globals())
        #function = eval("lambda x: %s" % individual)# 'node_add(x[2], x[4])')
        pred_error = 0.0
        try:
            # predicted = np.apply_along_axis(function, 1, dataset)
            predicted = torch.vmap(
                corre,
                0)(dataset)
            # print(predicted.size())
            # print(predicted)
            # input()
            # input()
            #pred_error = np.sum(np.power(predicted - dataset[:, 0], 2))
            pred_error = RMSELoss()(predicted, dataset[:, 0])
            if pred_error.isnan() or pred_error.isinf():
                 pred_error = torch.tensor(self.__invalid_fitness, device=cur_dev)
            #print(pred_error)
            #input()
        except (OverflowError, ValueError) as e:
            return torch.tensor(self.__invalid_fitness, device=cur_dev)
        #print(pred_error)
        return pred_error

    def evaluate(self, individual):
        error = 0.0
        test_error = 0.0
        if individual == None:
            return None

        error = self.get_error(individual, self.__train_set)
        #error = _sqrt_( error /self.__RRSE_train_denominator)
        #error = _sqrt_(error / len(self.__train_set))

        if error == None:
            error = self.__invalid_fitness

        if self.__apply_test_set != None:
            test_error = 0
            test_error = self.get_error(individual, self.__test_set)
            #test_error = _sqrt_( test_error / float(self.__RRSE_test_denominator))
            #test_error = _sqrt_(test_error / float(len(self.__test_set)))
        return (float(error.cpu().data.numpy()), {'generation': 0, "evals": 1, "test_error": float(test_error.cpu().data.numpy())})

    def setup(self, *args):
        self.random_number_generator = args[0]


if __name__ == "__main__":
    import sge.grammar as grammar
    import sge
    import sys
    run = sys.argv[1]
    file_name = sys.argv[2]
    start_test_set = int(sys.argv[3])
    evaluation_function = GlucoseRegression(
        data_file="resources/glucose/%s.csv" % file_name,
        apply_test_set=True,
        start_test_set=start_test_set)
    sge.evolutionary_algorithm(
        evaluation_function=evaluation_function,
        parameters_file="parameters/glucose19.yml",
        file_name=file_name,
        run=run)
