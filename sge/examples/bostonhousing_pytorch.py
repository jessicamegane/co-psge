from numpy import cos, sin
from sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv
import torch
from sge.utilities.pytorchtest import *


def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


class RMSE():
    def __init__(self, train_set, test_set):
        self.criterion = torch.nn.MSELoss()
        
    def calculate(self, predicted, dataset):
        pred_error = torch.sqrt(self.criterion(predicted, dataset.target))
        return pred_error


class RRSE():

    def __init__(self, train_set, test_set):
        self.criterion = torch.nn.MSELoss(reduction='sum')
        train_output_mean = torch.mean(train_set.target)
        self.__RRSE_train_denominator = self.criterion(train_set.target, train_output_mean)
        if test_set:
            test_output_mean = torch.mean(test_set.target)
            self.__RRSE_test_denominator = self.criterion(test_set.target, test_output_mean)

    def calculate(self, predicted, dataset):
        pred_error = self.criterion(predicted, dataset.target)

        if dataset.type == "test":
            error = torch.sqrt(torch.div(pred_error, self.__RRSE_test_denominator))
        else:
            error = torch.sqrt(torch.div(pred_error, self.__RRSE_train_denominator))
        return error

class Dataset():
    def __init__(self, dataset, type):
        dataset = torch.tensor(dataset, dtype=torch.float32, device=cur_dev)
        self.values = dataset[:, :-1]
        self.target = dataset[:, -1]
        self.type = type


class BostonHousing():
    def __init__(self, run=0, has_test_set=True, invalid_fitness=9999999):
        self.__train_set = []
        self.__test_set = None
        self.__invalid_fitness = invalid_fitness
        self.run = run
        self.has_test_set = has_test_set
        self.read_dataset()
        self.__loss_function = RRSE(self.__train_set, self.__test_set)

    def read_dataset(self):
        dataset = []
        trn_ind = []
        tst_ind = []
        with open('resources/BostonHousing/housing.data', 'r') as dataset_file:
            for line in dataset_file:
                dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])

        with open('resources/BostonHousing/housing.folds', 'r') as folds_file:
            for _ in range(self.run - 1): folds_file.readline()
            tst_ind = folds_file.readline()
            tst_ind = [int(value.strip(" ")) - 1 for value in tst_ind.split(" ") if value != ""]
            trn_ind = filter(lambda x: x not in tst_ind, range(len(dataset)))
        self.__train_set = Dataset([dataset[i] for i in trn_ind], "train")
        self.__test_set = Dataset([dataset[i] for i in tst_ind], "test")


    def get_error(self, dataset):
        pred_error = 0.0
        try:
            predicted = torch.vmap(
                corre,
                0)(dataset.values)

            pred_error = self.__loss_function.calculate(predicted, dataset)
            if pred_error.isnan() or pred_error.isinf():
                pred_error = torch.tensor(self.__invalid_fitness, device=cur_dev)

        except (OverflowError, ValueError) as e:
            return torch.tensor(self.__invalid_fitness, device=cur_dev)
        
        return pred_error


    def evaluate(self, individual):
        error = 0.0
        test_error = 0.0
        if individual is None:
            return None
        
        code = compile('def corre(x): \n\t return %s' % individual, '<string>', 'exec')
        exec(code, globals())

        error = self.get_error(self.__train_set)

        if self.__test_set:
            test_error = self.get_error(self.__test_set)
            return (float(error.cpu().data.numpy()), {'generation': 0, "evals": 1, "test_error": float(test_error.cpu().data.numpy())})

        return (float(error.cpu().data.numpy()), {'generation': 0, "evals": 1, "test_error": test_error})


if __name__ == "__main__":
    import sge
    sge.setup("parameters/standard.yml")
    eval_func = BostonHousing(sge.params['RUN'])
    sge.evolutionary_algorithm(evaluation_function=eval_func, parameters_file="parameters/standard.yml")
