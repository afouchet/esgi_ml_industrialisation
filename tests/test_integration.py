import os
import pandas as pd
import pytest
import tempfile

from app import create_app
from services.sales import DB, SaleWeeklyRaw

@pytest.fixture
def app():
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    }

    app = create_app(config)

    yield app

    with app.app_context():
        DB.drop_all()



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
            json=[{"year_week": 202002, "vegetable": "tomato", "sales": 100}],
        )
        response = client.post(
            "post_sales",
            json=[{"year_week": 202003, "vegetable": "tomato", "sales": 50}],
        )

        assert response.status_code == 200

        response = client.get(
            "get_monthly_sales",
        )
        assert response.status_code == 200

    assert response.json == [{"year_month": 202001, "vegetable": "tomato", "sales": 150}]
