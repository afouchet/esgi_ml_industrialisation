import numpy as np
from sklearn.metrics import accuracy_score
import pickle
import random
import time
import warnings

from td4.data import get_data_catalog
from td4.features import build_features, _reload_features_cache
from td4.models import get_model, save_prediction_model, load_prediction_model

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

    save_prediction_model(model)


def predict(df_test):
    catalog = get_data_catalog()
    df = build_features(catalog, does_retrain=False)
    df.pop("clicked")

    df = df_test.merge(df)
    X = df.drop(['user_id', 'page_id', 'ad_id'], axis=1)

    model = load_prediction_model()

    return model.predict_proba(X)


def _reload_cache():
    _reload_features_cache()


def evaluate_model(catalog):
    click_features = build_click_features(catalog)
    
    msk = np.random.rand(len(click_features)) < 0.8
    train = click_features[msk]
    test = click_features[~msk]
    
    X_train = train.drop(['user_id', 'page_id', 'ad_id', 'clicked'], axis=1)
    y_train = train['clicked']
    
    lr = get_model()
    lr.fit(X_train, y_train)
    
    X_test = test.drop(['user_id', 'page_id', 'ad_id', 'clicked'], axis=1)
    y_test = test['clicked']
    
    y_pred = lr.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    main()
