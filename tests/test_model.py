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


def test_marketing_model():
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


def test_price_model():
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


def test_stock_model():
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


def test_model_with_objectives():
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

def test_custom_model():
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

