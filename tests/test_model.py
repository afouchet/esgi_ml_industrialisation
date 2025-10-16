import pandas as pd
from sklearn.metrics import r2_score
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

    r2 = r2_score(df_true["sales"], df_pred["prediction"])

    assert r2 >= 0.8019


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

    sales_last_quarter = model.compute_rolling_mean(df_train, nb_months=3)
    df_train["last_quarter"] = sales_last_quarter

    pd.testing.assert_frame_equal(df_train, df_expected)


def test_compute_growth_factor():
    """
    Computing Growth between quarter M-1...M-3 and quarter M-13..M-15
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
            ["2019-06-01", "item_0", 6],
            ["2019-07-01", "item_0", 7],
            ["2019-08-01", "item_0", 8],
            ["2019-09-01", "item_0", 9],
            ["2019-10-01", "item_0", 10],
            ["2019-11-01", "item_0", 11],
            ["2019-12-01", "item_0", 12],
            ["2020-01-01", "item_0", 13],
            ["2020-02-01", "item_0", 14],
            ["2020-03-01", "item_0", 15],
            ["2020-04-01", "item_0", 16],
            ["2020-05-01", "item_0", 17],
            ["2019-01-01", "item_10", 10],
            ["2019-02-01", "item_10", 20],
            ["2019-03-01", "item_10", 30],
            ["2019-04-01", "item_10", 40],
            ["2019-05-01", "item_10", 50],
            ["2019-06-01", "item_10", 60],
            ["2019-07-01", "item_10", 70],
            ["2019-08-01", "item_10", 80],
            ["2019-09-01", "item_10", 90],
            ["2019-10-01", "item_10", 100],
            ["2019-11-01", "item_10", 110],
            ["2019-12-01", "item_10", 120],
            ["2020-01-01", "item_10", 130],
            ["2020-02-01", "item_10", 140],
            ["2020-03-01", "item_10", 150],
            ["2020-04-01", "item_10", 160],
            ["2020-05-01", "item_10", 170],
        ],
    )

    df_expected = pd.DataFrame(
        columns=["dates", "item_id", "sales", "growth"],
        data=[
            ["2019-01-01", "item_0", 1, None],
            ["2019-02-01", "item_0", 2, None],
            ["2019-03-01", "item_0", 3, None],
            ["2019-04-01", "item_0", 4, None],
            ["2019-05-01", "item_0", 5, None],
            ["2019-06-01", "item_0", 6, None],
            ["2019-07-01", "item_0", 7, None],
            ["2019-08-01", "item_0", 8, None],
            ["2019-09-01", "item_0", 9, None],
            ["2019-10-01", "item_0", 10, None],
            ["2019-11-01", "item_0", 11, None],
            ["2019-12-01", "item_0", 12, None],
            ["2020-01-01", "item_0", 13, None],
            ["2020-02-01", "item_0", 14, None],
            ["2020-03-01", "item_0", 15, None],
            ["2020-04-01", "item_0", 16, 14 / 2],
            ["2020-05-01", "item_0", 17, 15 / 3],
            ["2019-01-01", "item_10", 10, None],
            ["2019-02-01", "item_10", 20, None],
            ["2019-03-01", "item_10", 30, None],
            ["2019-04-01", "item_10", 40, None],
            ["2019-05-01", "item_10", 50, None],
            ["2019-06-01", "item_10", 60, None],
            ["2019-07-01", "item_10", 70, None],
            ["2019-08-01", "item_10", 80, None],
            ["2019-09-01", "item_10", 90, None],
            ["2019-10-01", "item_10", 100, None],
            ["2019-11-01", "item_10", 110, None],
            ["2019-12-01", "item_10", 120, None],
            ["2020-01-01", "item_10", 130, None],
            ["2020-02-01", "item_10", 140, None],
            ["2020-03-01", "item_10", 150, None],
            ["2020-04-01", "item_10", 160, 140 / 20],
            ["2020-05-01", "item_10", 170, 150 / 30],
        ],
    )

    serie_growth = model.compute_growth(df_train)
    df_train["growth"] = serie_growth

    pd.testing.assert_frame_equal(df_train, df_expected)


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

