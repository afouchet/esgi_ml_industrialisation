from flask import Flask, request, jsonify
import pandas as pd
from pathlib import Path
import os

import features

PATH_CSV = "data/raw/db.csv"

def create_app(config=None):
    config = config or {}
    app = Flask(__name__)

    if "CSV_PATH" not in config:
        config["CSV_PATH"] = PATH_CSV

    app.config.update(config)

    @app.route('/post_sales', methods=['POST'])
    def post_sales():
        data = request.json
        df_new = pd.DataFrame(data)

        if os.path.isfile(app.config['CSV_PATH']) and os.path.getsize(app.config['CSV_PATH']) > 0:
            df = pd.read_csv(app.config['CSV_PATH'])
            df = pd.concat([df, df_new])
        else:
            df = df_new

        df = df.drop_duplicates(subset=["vegetable", "year_week"], keep="last")
        df.to_csv(app.config['CSV_PATH'], index=False)

        return jsonify({"status": "success"}), 200

    @app.route('/get_weekly_sales', methods=['GET'])
    def get_weekly_sales():
        df = models.sales.get_weekly_sales()
        return jsonify(df.to_dict(orient="records")), 200

    @app.route('/get_monthly_sales', methods=['GET'])
    def get_monthly_sales():
        df = pd.read_csv(config["CSV_PATH"]
        df_monthly = features.compute_monthly_sales(df_weekly)

        return jsonify(df_monthly.to_dict(orient="records")), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=8000)
