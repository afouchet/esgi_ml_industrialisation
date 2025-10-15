import os
import pandas as pd
import pytest
import tempfile

from app import create_app

@pytest.fixture
def app():
    temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    temp_csv.close()

    config = {"TESTING": True, "CSV_PATH": temp_csv.name}

    app = create_app(config)

    yield app

    os.remove(temp_csv.name)


def test_post_sales(app):
    with app.test_client() as client:
        response = client.post(
            "post_sales",
            json=[{"year_week": 202001, "vegetable": "tomato", "sales": 100}],
        )
        response = client.post(
            "post_sales",
            json=[{"year_week": 202001, "vegetable": "tomato", "sales": 100}],
        )

        assert response.status_code == 200

        response = client.get(
            "get_weekly_sales",
        )
        assert response.status_code == 200

    assert response.json == [{"year_week": 202001, "vegetable": "tomato", "sales": 100}]

def test_get_monthly_sales(app):
    with app.test_client() as client:
        response = client.post(
            "post_sales",
            json=[{"year_week": 202001, "vegetable": "tomato", "sales": 100}],
        )
        response = client.post(
            "post_sales",
            json=[{"year_week": 202002, "vegetable": "tomato", "sales": 50}],
        )

        assert response.status_code == 200

        response = client.get(
            "get_monthly_sales",
        )
        assert response.status_code == 200

    assert response.json == [{"year_month": 202001, "vegetable": "tomato", "sales": 150}]
