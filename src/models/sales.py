import os
import pandas as pd
from pathlib import Path


PATH_CSV = None


def init_database(config):
    global PATH_CSV
    PATH_CSV = Path(config["CSV_PATH"])


def get_weekly_sales():
    if PATH_CSV is None:
        raise ValueError("Initiate dabase first")

    if PATH_CSV.exists() and os.path.getsize(PATH_CSV) > 0:
        return pd.read_csv(PATH_CSV)
    else:
        return pd.DataFrame([])


