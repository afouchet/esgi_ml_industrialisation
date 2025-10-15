from flask import Flask, request, jsonify
import pandas as pd
from pathlib import Path
import os

import models
import features

PATH_CSV = "data/raw/db.csv"

def create_app(config=None):
    config = config or {}
    app = Flask(__name__)

    if "CSV_PATH" not in config:
        config["CSV_PATH"] = PATH_CSV

    app.config.update(config)

    models.sales.init_database(config)

    @app.route('/post_sales', methods=['POST'])
    def post_sales():
        data = request.json

        models.sales.add_weekly_sales(data)

        return jsonify({"status": "success"}), 200

    @app.route('/get_weekly_sales', methods=['GET'])
    def get_weekly_sales():
        df = models.sales.get_weekly_sales()
        return jsonify(df.to_dict(orient="records")), 200

    @app.route('/get_monthly_sales', methods=['GET'])
    def get_monthly_sales():
        df_weekly = models.sales.get_weekly_sales()
        df_monthly = features.compute_monthly_sales(df_weekly)

        return jsonify(df_monthly.to_dict(orient="records")), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=8000)
