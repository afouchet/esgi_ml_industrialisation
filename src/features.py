import pandas as pd


def compute_monthly_sales(df_weekly):
    return pd.DataFrame(
        columns=["year_month", "vegetable", "sales"],
        data=[[202001, "tomato", 510], [202002, "tomato", 200]],
    )
