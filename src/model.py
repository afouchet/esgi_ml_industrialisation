import pandas as pd
from sklearn.linear_model import Ridge

def make_predictions(config):
    data_dict: dict[str, pd.DataFrame] = make_data_catalog(config)

    df = make_features(data_dict, config)

    model = build_model(config)

    X_train, X_test, y_train, y_test = split_train_test(df, config)

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    # For output convienence, I'd rather have a full df with pred
    df_test = X_test
    df_test["prediction"] = pred

    return df_test["prediction"].reset_index()


def make_data_catalog(config):
    return {
        source: pd.read_csv(path) for source, path in config["data"].items()
    }


def make_features(data_dict, config):
    dfs = []
    features = config.get("features", [])

    if (
            "past_sales" in features
            or config["model"] in ["PrevMonthSale", "SameMonthLastYearSales"]
    ):
        df_sales = _build_sales_features(data_dict["sales"], config)
        dfs.append(df_sales)

    if "marketing" in features:
        df_marketing = data_dict["marketing"]
        dfs.append(df_marketing)
    
    df = None
    for a_df in dfs:
        if df is None:
            df = a_df
        else:
            df = df.merge(a_df)

    return df.set_index(["dates", "item_id"]).dropna()


def _build_sales_features(df_sales, config):
    df = df_sales.copy()

    df["sales_last_month"] = df.groupby("item_id")["sales"].shift(1)
    df["sales_last_year"] = df.groupby("item_id")["sales"].shift(12)
    df["sales_mean_last_year"] = compute_rolling_mean(df, nb_months=12)
    df["growth"] = compute_growth(df).clip(lower=0.7, upper=1.3)

    return df

def build_model(config):
    if config["model"] == "PrevMonthSale":
        return PredictPrevMonthSale()
    elif config["model"] == "SameMonthLastYearSales":
        return PredictLastYearSale()
    elif config["model"] == "Ridge":
        return Ridge()

    raise ValueError(f"Unknown model {config['model']}")


def split_train_test(df, config):
    X_train = df.query("dates < @config['start_test']")
    y_train = X_train.pop("sales")

    X_test = df.query("dates >= @config['start_test']")
    y_test = X_test.pop("sales")

    return X_train, X_test, y_train, y_test


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


def compute_rolling_mean(df, nb_months):
    sales_rolling = df.groupby(["item_id"])["sales"].shift(1).rolling(nb_months).mean()

    return sales_rolling

def compute_growth(df):
    df = df.copy()
    df["past_quarter"] = compute_rolling_mean(df, nb_months=3)
    df["last_year_past_quarter"] = df.groupby("item_id")["past_quarter"].shift(12)

    return df["past_quarter"] / df["last_year_past_quarter"]
    
