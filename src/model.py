import pandas as pd
from sklearn.linear_model import Ridge

def make_predictions(config):
    df_sales = pd.read_csv(config["data"]["sales"])

    df = make_features(df_sales, config)

    df_train = df.query("dates < @config['start_test']")
    y_train = df_train.pop("sales")

    df_test = df.query("dates >= @config['start_test']")
    y_test = df_test.pop("sales")

    model = build_model(config)

    model.fit(df_train, y_train)

    pred = model.predict(df_test)

    df_test["prediction"] = pred

    return df_test["prediction"].reset_index()


def make_features(df_sales, config):
    df = df_sales.copy()

    df["sales_last_month"] = df.groupby("item_id")["sales"].shift(1)
    df["sales_last_year"] = df.groupby("item_id")["sales"].shift(12)

    return df.set_index(["dates", "item_id"]).dropna()


def build_model(config):
    if config["model"] == "PrevMonthSale":
        return PredictPrevMonthSale()
    elif config["model"] == "SameMonthLastYearSales":
        return PredictLastYearSale()
    elif config["model"] == "Ridge":
        return Ridge()

    raise ValueError(f"Unknown model {config['model']}")


class PredictPrevMonthSale():
    def fit(self, X, y):
        return self

    def predict(self, X):
        return X["sales_last_month"]



class PredictLastYearSale():
    def fit(self, X, y):
        return self

    def predict(self, X):
        return X["sales_last_year"]


def compute_rolling_mean(df, nb_months, col_name):
    sales_quarter = df.groupby(["item_id"])["sales"].shift(1).rolling(3).mean()

    df[col_name] = sales_quarter

    return df
