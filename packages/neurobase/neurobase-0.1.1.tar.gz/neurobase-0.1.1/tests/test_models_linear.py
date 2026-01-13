import numpy as np
from neurobase import SimpleLinearRegression

def test_simple_linear_regression():
    X = [0, 1, 2]
    y = [1, 3, 5]   # y = 2x + 1
    model = SimpleLinearRegression()
    model.fit(X, y)
    pred = model.predict([3])
    assert np.isclose(pred, 7.0, atol=1e-6)
