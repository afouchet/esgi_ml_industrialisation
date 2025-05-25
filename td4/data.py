from pathlib import Path
import pandas as pd


def get_data_catalog():
    return DataCatalog()


class DataCatalog:
    folder = Path("data") / "raw"/ "td4"

    def __init__(self):
        self.dataset_to_filename = {
            "user": "user_data.csv",
            "page": "page_data.csv",
            "bid": "bid_requests_train.csv",
            "click": "click_data_train.csv",
        }

    def load(self, name):
        filename = self.dataset_to_filename[name]
        return pd.read_csv(self.folder / filename)

