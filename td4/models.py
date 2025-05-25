import pickle
import os

from sklearn.linear_model import LogisticRegression


seed = 42

def get_model():
    return LogisticRegression(max_iter=1000, random_state=seed)


def save_prediction_model(model):
    # Save click predictor
    with open("models/click_predictor.pkl", "wb") as f:
        pickle.dump(model, f)

def load_prediction_model():
    # Load click predictor
    with open("models/click_predictor.pkl", "rb") as f:
        return pickle.load(f)
