import numpy as np
import pandas as pd

from script import train_model, predict, CONF

def test_end_to_end():
    df_test = pd.read_csv("data/test_ids.csv")
    pred_expected = np.load("data/test_pred.npy")

    train_model(CONF)
    pred = predict(df_test, CONF)

    np.testing.assert_almost_equal(pred_expected, pred)
    
