from numpy import cos, sin, random
import torch
import pandas as pd
from sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv
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


class SymbolicRegression():
    def __init__(self, function="pagiepolynomial", has_test_set=False, invalid_fitness=9999999):
        self.__train_set = []
        self.__test_set = None
        self.__invalid_fitness = invalid_fitness
        self.partition_rng = random.uniform()
        self.function = function
        self.has_test_set = has_test_set
        self.readpolynomial()

    def read_fit_cases(self):
        f_in = open(self.__file_problem,'r')
        data = f_in.readlines()
        f_in.close()
        fit_cases_str = [ case[:-1].split() for case in data[1:]]
        self.__train_set = torch.tensor([[float(elem) for elem in case] for case in fit_cases_str], dtype=torch.float32, device=cur_dev)

    def readpolynomial(self):
        def quarticpolynomial(inp):
            return pow(inp,4) + pow(inp,3) + pow(inp,2) + inp

        def kozapolynomial(inp):
            return pow(inp,6) - (2 * pow(inp,4)) + pow(inp,2)

        def pagiepolynomial(inp1,inp2):
            return 1.0 / (1 + pow(inp1,-4.0)) + 1.0 / (1 + pow(inp2,-4))

        def keijzer6(inp):
            return sum([1.0/i for i in range(1,inp+1,1)])

        def keijzer9(inp):
            return _log_(inp + (inp**2 + 1)**0.5)

        if self.function in ["pagiepolynomial"]:
            function = eval(self.function)
            # two variables
            l = []
            for xx in drange(-5,5.4,0.4):
                for yy in drange(-5,5.4,0.4):
                    zz = pagiepolynomial(xx,yy)
                    l.append([xx,yy,zz])

            self.__train_set=l
            self.training_set_size = len(self.__train_set)
            if self.has_test_set:
                xx = list(drange(-5,5.0,.1))
                yy = list(drange(-5,5.0,.1))
                function = eval(self.function)
                zz = map(function, xx, yy)

                self.__test_set = [xx,yy,zz]
                self.test_set_size = len(self.__test_set)
        elif self.function in ["quarticpolynomial"]:
            function = eval(self.function)
            l = []
            for xx in drange(-1,1.1,0.1):
                yy = quarticpolynomial(xx)
                l.append([xx,yy])

            self.__train_set = l
            self.training_set_size = len(self.__train_set)
            if self.has_test_set:
                xx = list(drange(-1,1.1,0.1))
                function = eval(self.function)
                yy = map(function, xx)

                self.__test_set = [xx,yy]
                self.test_set_size = len(self.__test_set)
        else:
            if self.function == "keijzer6":
                xx = list(drange(1,51,1))
            elif self.function == "keijzer9":
                xx = list(drange(0,101,1))
            else:
                xx = list(drange(-1,1.1,.1))
            function = eval(self.function)
            yy = map(function,xx)
            self.__train_set = list(zip(xx, yy))
            self.__number_of_variables = 1
            self.training_set_size = len(self.__train_set)
            if self.has_test_set:
                if self.function == "keijzer6":
                    xx = list(drange(51,121,1))
                elif self.function == "keijzer9":
                    xx = list(drange(0,101,.1))
                yy = map(function,xx)
                self.__test_set = [xx, yy]
                self.test_set_size = len(self.__test_set)
        self.__train_set = torch.tensor(self.__train_set, dtype=torch.float32, device=cur_dev)

    def get_error(self, individual, dataset):
        # print(individual)
        # print(dataset)
        # input()
        code = compile('def corre(x): \n\t return %s' % individual, '<string>', 'exec')

        exec(code, globals())


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
            pred_error = RMSELoss()(predicted, dataset[:, -1])
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
        if individual is None:
            return None

        error = self.get_error(individual, self.__train_set)
        # error = _sqrt_( error /self.__RRSE_train_denominator)

        if error is None:
            error = self.__invalid_fitness

        if self.__test_set is not None:
            test_error = 0
            test_error = self.get_error(individual, self.__test_set)
            # test_error = _sqrt_( test_error / float(self.__RRSE_test_denominator))

        return (float(error.cpu().data.numpy()), {'generation': 0, "evals": 1, "test_error": 0.0})


if __name__ == "__main__":
    import sge
    eval_func = SymbolicRegression()
    sge.evolutionary_algorithm(evaluation_function=eval_func, parameters_file="parameters/standard.yml")
