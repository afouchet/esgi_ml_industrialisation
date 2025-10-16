from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from pathlib import Path

import features

DB = SQLAlchemy()


def init_database(app):
    DB.init_app(app)


def get_weekly_sales():
    entries = DB.session.query(SaleWeeklyRaw)

    return pd.DataFrame([e.json() for e in entries])


def get_monthly_sales():
    df_weekly = get_weekly_sales()
    return features.compute_monthly_sales(df_weekly)


def add_weekly_sales(data):
    for row in data:
        entry = SaleWeeklyRaw.query.filter_by(
            year_week=row["year_week"], vegetable=row["vegetable"]
        ).first()

        if entry:
            entry.sales = row["sales"]
        else:
            entry = SaleWeeklyRaw(**row)
            DB.session.add(entry)

    DB.session.commit()


class SaleWeeklyRaw(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    year_week = DB.Column(DB.Integer, nullable=False)
    vegetable = DB.Column(DB.String(80), nullable=False)
    sales = DB.Column(DB.Float, nullable=False)

    def json(self):
        return {
            "year_week": self.year_week,
            "vegetable": self.vegetable,
            "sales": self.sales,
    }
