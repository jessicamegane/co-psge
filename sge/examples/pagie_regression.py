import numpy as np
import sge
from sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv, _sin_, _cos_

class PagiePolynomialRegression():
    def __init__(self, invalid_fitness=9999999):
        self.invalid_fitness = invalid_fitness
        self.function = lambda x: 1.0 / (1 + np.power(x[0],-4.0)) + 1.0 / (1 + np.power(x[1],-4))
        interval = np.arange(-5,5.4,0.4)
        self.points = np.array([np.repeat(interval, interval.shape), np.tile(interval, interval.shape)]).T
        self.fitness_cases = self.points.shape[0]
        self.y_points = np.apply_along_axis(self.function, 1, self.points)
        y_points_mean = self.y_points.mean()
        self.rrse_train_denominator = np.square(self.y_points - y_points_mean).sum()
        self.outputs = np.empty(self.fitness_cases)

    def evaluate(self, individual):
        try:
            #print(individual)
            code = compile('result = lambda x: ' + individual, 'solution', 'exec')
            globals_code = {'_div_' : _div_, '_log_' : _log_, '_exp_' : _exp_, '_inv_' : _inv_, '_sqrt_':_sqrt_,'_sin_' : _sin_, '_cos_' : _cos_}
            locals_code = {}
            exec(code, globals_code, locals_code)
            func = locals_code['result']
            self.outputs = np.apply_along_axis(func, 1, self.points)
            cov_matrix = np.cov(np.vstack([self.y_points, self.outputs]))
            covariance_y_o = cov_matrix[0,1]
            variance_o = cov_matrix[1,1]
            if not np.isnan(variance_o):
                mse_a_b = self.invalid_fitness
                b = 0
                if variance_o != 0:
                    b = covariance_y_o / variance_o
                a = self.y_points.mean() - b * self.outputs.mean()
                mse = np.sqrt(np.mean(np.square(self.outputs - self.y_points)))
                rrse_a_b = np.sqrt( np.sum(np.square(self.y_points - (a + b * self.outputs))) / self.rrse_train_denominator)
                mse_a_b = np.mean(np.square(self.y_points - (a + b * self.outputs)))
            else:
                rrse_a_b = mse = mse_a_b = self.invalid_fitness
                b = a = None
            
        except (OverflowError, ValueError) as e:
            rrse_a_b = mse_a_b = mse = self.invalid_fitness
            b = a = None
        #if np.isnan(mse):
        #   rrse = mse_a_b=  mse = self.invalid_fitness
        #   b = a = None
        return rrse_a_b, {'generation': 0, "evals": 1, 'mse' : mse, 'rrse' : rrse_a_b,'a' : a, 'b' : b, 'mse_a_b' : mse_a_b}


if __name__ == "__main__":
    fitness = PagiePolynomialRegression()
    sge.evolutionary_algorithm(evaluation_function=fitness, parameters_file="parameters/standard.yml")
