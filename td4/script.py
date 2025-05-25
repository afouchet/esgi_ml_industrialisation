import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle
import random
import time
import warnings

from td4.data import get_data_catalog
from td4.features import build_features, _reload_features_cache

warnings.filterwarnings('ignore')

seed = 42

def main():
    """Main function"""
    train_model()
    
    print("\n== Evaluating model ==")
    evaluate_model()


def train_model():
    catalog = get_data_catalog()

    df = build_features(catalog, does_retrain=True)
    
    y = df.pop("clicked")
    X = df.drop(['user_id', 'page_id', 'ad_id'], axis=1)

    model = get_model()
    model.fit(X, y)

    _cache["click_predictor"] = model

    save_models()


def predict(df_test):
    load_models()

    catalog = get_data_catalog()
    df = build_features(catalog, does_retrain=False)
    df.pop("clicked")

    df = df_test.merge(df)
    X = df.drop(['user_id', 'page_id', 'ad_id'], axis=1)

    model = _cache["click_predictor"]

    return model.predict_proba(X)


_cache = {}

def get_model():
    return LogisticRegression(max_iter=1000, random_state=seed)


def _reload_cache():
    global _cache
    _cache = {}
    _reload_features_cache()


def evaluate_model(catalog):
    click_features = build_click_features(catalog)
    
    msk = np.random.rand(len(click_features)) < 0.8
    train = click_features[msk]
    test = click_features[~msk]
    
    X_train = train.drop(['user_id', 'page_id', 'ad_id', 'clicked'], axis=1)
    y_train = train['clicked']
    
    lr = LogisticRegression(max_iter=1000, random_state=seed)
    lr.fit(X_train, y_train)
    
    X_test = test.drop(['user_id', 'page_id', 'ad_id', 'clicked'], axis=1)
    y_test = test['clicked']
    
    y_pred = lr.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model accuracy: {accuracy:.4f}")

def get_recommendations(user_id, page_id, ad_ids):
    load_models()
    predictions = []
    for ad_id in ad_ids:
        prob = predict_click(user_id, page_id, ad_id)
        predictions.append((ad_id, prob))
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    return predictions

def save_models():
    # Save click predictor
    with open("models/click_predictor.pkl", "wb") as f:
        pickle.dump(_cache["click_predictor"], f)

def load_models():
    # Load click predictor
    with open("models/click_predictor.pkl", "rb") as f:
        _cache["click_predictor"] = pickle.load(f)

if __name__ == "__main__":
    main()
