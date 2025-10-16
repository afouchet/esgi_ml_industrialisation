from flask import Flask, request, jsonify
import pandas as pd
from pathlib import Path
import os

import services
import features

def create_app(config=None):
    config = config or {}
    app = Flask(__name__)

    app.config.update(config)

    services.sales.init_database(app)

    @app.route('/post_sales', methods=['POST'])
    def post_sales():
        data = request.json

        services.sales.add_weekly_sales(data)

        return jsonify({"status": "success"}), 200

    @app.route('/get_weekly_sales', methods=['GET'])
    def get_weekly_sales():
        df = services.sales.get_weekly_sales()
        return jsonify(df.to_dict(orient="records")), 200

    @app.route('/get_monthly_sales', methods=['GET'])
    def get_monthly_sales():
        df_monthly = services.sales.get_monthly_sales()

        return jsonify(df_monthly.to_dict(orient="records")), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=8000)
