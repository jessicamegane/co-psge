import numpy as np
import sge

class SimpleSymbolicRegression():
    def __init__(self, num_fitness_cases=20, invalid_fitness=9999999):
        self.invalid_fitness = invalid_fitness
        self.function = lambda x: (x**2 + 1) * (x - 3)
        self.fitness_cases = num_fitness_cases
        self.x_points = np.asarray([x for x in range(self.fitness_cases)])
        self.y_points = np.asarray([self.function(x) for x in self.x_points])
        self.outputs = np.empty(self.fitness_cases)
        self.rrse_train_denominator = self.y_points.mean()

    def evaluate(self, individual):
        try:
            # print(individual)
            code = compile('result = lambda x: ' + individual, 'solution', 'exec')
            globals_code = {}
            locals_code = {}
            exec(code, globals_code, locals_code)
            func = locals_code['result']
            self.outputs = np.apply_along_axis(func, 0, self.x_points)
            cov_matrix = np.cov(np.vstack([self.y_points, self.outputs]))
            covariance_y_o = cov_matrix[0,1]
            variance_o = cov_matrix[1,1]
            b = 0
            if variance_o != 0:
                b = covariance_y_o / variance_o
            a = self.y_points.mean() - b * self.outputs.mean()
            # print("y = ", ",".join(np.char.mod('%.2f', self.y_points)))
            # print("o = ", ",".join(np.char.mod('%.2f', self.outputs)))
            # print(np.cov([self.y_points, self.outputs], bias=True))
            # print("b = ", b)
            # print("variance_o = ", variance_o)
            # print("a =", a)
            
            mse = np.sqrt(np.mean(np.square(self.outputs - self.y_points)))
            rrse = np.sqrt( np.sum(np.square(self.outputs - self.y_points)) / self.rrse_train_denominator)
            mse_a_b = np.mean(np.square(self.y_points - (a + b * self.outputs)))
        except (OverflowError, ValueError) as e:
            rrse = mse_a_b = mse = self.invalid_fitness
            b = a = None
        if np.isnan(mse):
           rrse = mse_a_b=  mse = self.invalid_fitness
           b = a = None
        return mse_a_b, {'generation': 0, "evals": 1, 'mse' : mse, 'rrse' : rrse,'a' : a, 'b' : b}


if __name__ == "__main__":
    fitness = SimpleSymbolicRegression()
    sge.evolutionary_algorithm(evaluation_function=fitness, parameters_file="parameters/standard.yml")
