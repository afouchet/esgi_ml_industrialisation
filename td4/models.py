import pickle
import os

from sklearn.linear_model import LogisticRegression


seed = 42

def get_model(config):
    return LogisticRegression(max_iter=1000, random_state=config["seed"])


def save_prediction_model(model, config):
    # Save click predictor
    with open(config["model"]["path"], "wb") as f:
        pickle.dump(model, f)

def load_prediction_model(config):
    # Load click predictor
    with open(config["model"]["path"], "rb") as f:
        return pickle.load(f)
