from pathlib import Path
import pandas as pd


def get_data_catalog(config):
    return DataCatalog(config)


class DataCatalog:
    folder = Path("data") / "raw"/ "td4"

    def __init__(self, config):
        self.dataset_to_filename = config["data"]

    def load(self, name):
        filename = self.dataset_to_filename[name]
        return pd.read_csv(self.folder / filename)

