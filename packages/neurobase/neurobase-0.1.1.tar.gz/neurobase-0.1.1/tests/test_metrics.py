import numpy as np
from neurobase.metrics import mean_squared_error

def test_mean_squared_error():
    y_true = np.array([1, 2, 3])
    y_pred = np.array([1, 2, 4])
    mse = mean_squared_error(y_true, y_pred)
    assert mse == 1/3
