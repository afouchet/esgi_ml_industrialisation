import requests
import pytest

URL = "http://127.0.0.1:8000/"

def tst_idempotency():
    response_init_db = requests.get(URL + "init_database")
    assert response_init_db.status_code == 200
    
    for _ in range(2):
        requests.post(
            URL + "post_sales",
            json=[{"year_week": 202002, "vegetable": "tomato", "sales": 100}],
        )

    response = requests.get(
        URL + "get_weekly_sales",
    )

    assert response.status_code == 200

    assert response.json() == [{"year_week": 202002, "vegetable": "tomato", "sales": 100}]


def tst_get_monthly_sales():
    response_init_db = requests.get(URL + "init_database")
    assert response_init_db.status_code == 200

    requests.post(
        URL + "post_sales",
        json=[{"year_week": 202005, "vegetable": "tomato", "sales": 70}],
    )

    response = requests.get(
        URL + "get_monthly_sales",
    )

    assert response.status_code == 200

    assert response.json() == [
        {"year_month": 202001, "vegetable": "tomato", "sales": 50},
        {"year_month": 202002, "vegetable": "tomato", "sales": 20},
    ]
