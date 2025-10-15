import pandas as pd


def compute_monthly_sales(df_weekly):
    df_days_in_month = _get_df_days_per_year_month(df_weekly["year_week"])
    df = df_weekly.merge(df_days_in_month)

    df["sales_daily"] = df["sales"] / 7
    df["sales"] = df["sales_daily"] * df["nb_days"]

    df = df.groupby(["year_month", "vegetable"], as_index=False)["sales"].sum()

    return df


def _get_df_days_per_year_month(serie_year_week):
    last_day = pd.to_datetime(serie_year_week.apply(str) + "7", format="%G%V%u")

    # If last day of week W is 2nd of February
    # there were 2 days in February and 5 in January
    days_in_prev_month = (7 - last_day.dt.day).clip(lower=0)

    df = pd.DataFrame([])
    df["year_week"] = last_day.dt.strftime("%G%V").astype(int)
    df["year_month"] = last_day.dt.strftime("%G%m").astype(int)
    df["nb_days"] = last_day.dt.day.clip(upper=7)

    df_prev_month = pd.DataFrame([])
    df_prev_month["year_week"] = last_day.dt.strftime("%G%V").astype(int)
    df_prev_month["year_month"] = (last_day - pd.Timedelta(days=7)).dt.strftime("%G%m").astype(int)
    df_prev_month["nb_days"] = days_in_prev_month

    df_prev_month = df_prev_month[df_prev_month["nb_days"] > 0]

    return pd.concat([df, df_prev_month])
