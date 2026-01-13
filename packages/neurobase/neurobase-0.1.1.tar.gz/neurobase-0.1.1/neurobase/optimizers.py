import numpy as np

class GradientDescent:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.learning_rate = learning_rate
        self.iterations = iterations

    def optimize(self, X, y, weights, bias):
        n = X.shape[0]
        for _ in range(self.iterations):
            preds = X @ weights + bias
            err = preds - y
            dw = (1 / n) * (X.T @ err)
            db = (1 / n) * np.sum(err)
            weights -= self.learning_rate * dw
            bias -= self.learning_rate * db
        return weights, bias


class StochasticGradientDescent:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.learning_rate = learning_rate
        self.iterations = iterations

    def optimize(self, X, y, weights, bias):
        n = X.shape[0]
        for _ in range(self.iterations):
            for i in range(n):
                xi = X[i : i + 1]
                yi = y[i]
                pred = xi @ weights + bias
                err = pred - yi
                dw = xi.T @ err
                db = err
                weights -= self.learning_rate * dw.flatten()
                bias -= self.learning_rate * db
        return weights, bias
