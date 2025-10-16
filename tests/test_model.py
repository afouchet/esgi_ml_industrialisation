import pandas as pd
from sklearn.metrics import mean_squared_error
import pytest

import model


def test_model_prev_month():
    config = {
        "data": {
            "sales": "data/raw/sales.csv",
        },
        "start_test": "2023-07-01",
        "model": "PrevMonthSale",
    }

    prediction = model.make_predictions(config)

    df_expected = pd.read_csv("data/raw/prediction_prev_month.csv")

    pd.testing.assert_frame_equal(df_expected, prediction)


def test_model_same_month_last_year():
    config = {
        "data": {
            "sales": "data/raw/sales.csv",
        },
        "start_test": "2023-07-01",
        "model": "SameMonthLastYearSales",
    }

    df_pred = model.make_predictions(config)

    df_expected = pd.read_csv("data/raw/prediction_same_month_last_year.csv")

    pd.testing.assert_frame_equal(df_expected, df_pred)
    

def test_autoregressive_model():
    config = {
        "data": {
            "sales": "data/raw/sales.csv",
        },
        "start_test": "2023-07-01",
        "model": "Ridge",
        "features": ["past_sales"],
    }

    df_pred = model.make_predictions(config)

    df_true = pd.read_csv("data/raw/sales_to_predict.csv")

    mse = mean_squared_error(df_true["sales"], df_pred["prediction"])
    assert mse == pytest.approx(0.8019,rel=1e-3)


def test_compute_rolling_means():
    """
    Computing mean over 12 months, with a lag, etc
    is complicated and error-prone

    -> making a test with some data, where I can compute the result by myself
    and make sure we don't have an index error
    """
    df_train = pd.DataFrame(
        columns=["dates", "item_id", "sales"],
        data=[
            ["2019-01-01", "item_0", 1],
            ["2019-02-01", "item_0", 2],
            ["2019-03-01", "item_0", 3],
            ["2019-04-01", "item_0", 4],
            ["2019-05-01", "item_0", 5],
            ["2019-01-01", "item_10", 10],
            ["2019-02-01", "item_10", 20],
            ["2019-03-01", "item_10", 30],
            ["2019-04-01", "item_10", 40],
            ["2019-05-01", "item_10", 50],
        ],
    )

    df_expected = pd.DataFrame(
        columns=["dates", "item_id", "sales", "last_quarter"],
        data=[
            ["2019-01-01", "item_0", 1, None],
            ["2019-02-01", "item_0", 2, None],
            ["2019-03-01", "item_0", 3, None],
            ["2019-04-01", "item_0", 4, 2],
            ["2019-05-01", "item_0", 5, 3],
            ["2019-01-01", "item_10", 10, None],
            ["2019-02-01", "item_10", 20, None],
            ["2019-03-01", "item_10", 30, None],
            ["2019-04-01", "item_10", 40, 20],
            ["2019-05-01", "item_10", 50, 30],
        ],
    )

    df = model.compute_rolling_mean(df_train, nb_months=3, col_name="last_quarter")

    pd.testing.assert_frame_equal(df, df_expected)


def tst_marketing_model():
    config = {
        "data": {
            "sales": "data/raw/sales.csv",
            "marketing": "data/raw/marketing.csv",
        },
        "start_test": "2023-07-01",
        "model": "Ridge",
        "features": ["past_sales", "marketing"],
    }

    df_pred = model.make_predictions(config)

    df_true = pd.read_csv("data/raw/sales_to_predict.csv")

    mse = mean_squared_error(df_true["sales"], df_pred["prediction"])
    assert mse == pytest.approx(0.8019,rel=1e-3)


def tst_price_model():
    config = {
        "data": {
            "sales": "data/raw/sales.csv",
            "marketing": "data/raw/marketing.csv",
            "price": "data/raw/price.csv",
        },
        "start_test": "2023-07-01",
        "model": "Ridge",
        "features": ["past_sales", "marketing", "price"],
    }

    df_pred = model.make_predictions(config)

    df_true = pd.read_csv("data/raw/sales_to_predict.csv")

    mse = mean_squared_error(df_true["sales"], df_pred["prediction"])

    assert mse == pytest.approx(0.8446,rel=1e-3)


def tst_stock_model():
    config = {
        "data": {
            "sales": "data/raw/sales.csv",
            "marketing": "data/raw/marketing.csv",
            "price": "data/raw/price.csv",
            "stock": "data/raw/stock.csv",
        },
        "start_test": "2023-07-01",
        "model": "Ridge",
        "features": ["past_sales", "marketing", "price", "stock"],
    }

    df_pred = model.make_predictions(config)

    df_true = pd.read_csv("data/raw/sales_to_predict.csv")

    mse = mean_squared_error(df_true["sales"], df_pred["prediction"])

    assert mse == pytest.approx(0.8446,rel=1e-3)


def tst_model_with_objectives():
    config = {
        "data": {
            "sales": "data/raw/sales.csv",
            "marketing": "data/raw/marketing.csv",
            "price": "data/raw/price.csv",
            "stock": "data/raw/stock.csv",
            "objectives": "data/raw/objectives.csv",
        },
        "start_test": "2023-07-01",
        "model": "Ridge",
        "features": ["past_sales", "marketing", "price", "stock", "objectives"],
    }

    df_pred = model.make_predictions(config)

    df_true = pd.read_csv("data/raw/sales_to_predict.csv")

    mse = mean_squared_error(df_true["sales"], df_pred["prediction"])

    assert mse == pytest.approx(0.8446,rel=1e-3)

def tst_custom_model():
    config = {
        "data": {
            "sales": "data/raw/sales.csv",
            "marketing": "data/raw/marketing.csv",
            "price": "data/raw/price.csv",
            "stock": "data/raw/stock.csv",
            "objectives": "data/raw/objectives.csv",
        },
        "start_test": "2023-07-01",
        "model": "CustomModel",
        "features": ["past_sales", "marketing", "price", "stock", "objectives"],
    }

    df_pred = model.make_predictions(config)

    df_true = pd.read_csv("data/raw/sales_to_predict.csv")

    mse = mean_squared_error(df_true["sales"], df_pred["prediction"])

    assert mse == pytest.approx(0.8446,rel=1e-3)

