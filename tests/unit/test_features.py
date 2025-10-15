import pandas as pd

from features import compute_monthly_sales

def test_compute_monthly_sales():
    """
    Compute monthly sales

    Edge case:
    - The 202004 year_week has 5 days in January and 2 in February
    -> The 700 sales in year_week 202004 mean 500 sales for January 2020
    and 200 sales for February 2020
    """
    df = pd.DataFrame(
        columns=["year_week", "vegetable", "sales"],
        data=[
            [202003, "tomato", 10],
            [202004, "tomato", 700],
        ],
    )

    df_expected = pd.DataFrame(
        columns=["year_month", "vegetable", "sales"],
        data=[[202001, "tomato", 510], [202002, "tomato", 200]],
    )

    df_res = compute_monthly_sales(df)

    pd.testing.assert_frame_equal(df_res, df_expected, check_dtype=False)
