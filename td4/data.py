from pathlib import Path
import pandas as pd
import pickle


def get_data_catalog(config):
    return DataCatalog(config)


class DataCatalog:
    folder = Path("data") / "raw"/ "td4"

    def __init__(self, config):
        self.dataset_to_filename = config["data"]
        self.model_to_filename = {
            model: Path(info["model_path"]) for model, info in config["features"].items()
        }
        self.model_to_filename["predictor"] = Path(config["model"]["path"])

        self.vectorizer_to_filename = {
            model: Path(info["vectorizer_path"])
            for model, info in config["features"].items()
            if info.get("vectorizer_path")
        }

    def load(self, name):
        filename = self.dataset_to_filename[name]
        return pd.read_csv(self.folder / filename)

    def load_model(self, name):
        path = self.model_to_filename[name]
        with open(path, "rb") as f:
            return pickle.load(f)

    def save_model(self, name, model):
        path = self.model_to_filename[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(model, f)

    def load_vectorizer(self, name):
        path = self.vectorizer_to_filename[name]
        with open(path, "rb") as f:
            return pickle.load(f)

    def save_vectorizer(self, name, model):
        path = self.vectorizer_to_filename[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(model, f)
