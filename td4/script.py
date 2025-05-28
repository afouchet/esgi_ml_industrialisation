import numpy as np
from sklearn.metrics import accuracy_score
import pickle
import random
import time
import warnings
import yaml

from td4.data import get_data_catalog
from td4.features import build_features, gen_X_y, train_feature_store
from td4.models import get_model, save_prediction_model, load_prediction_model

warnings.filterwarnings('ignore')

CONF = yaml.safe_load(open("td4/conf.yaml"))

def main():
    """Main function"""
    train_model(CONF)
    
    print("\n== Evaluating model ==")
    catalog = get_data_catalog(CONF)
    evaluate_model(catalog, CONF)


def train_model(config):
    catalog = get_data_catalog(config)

    train_feature_store(catalog, config)
    df = build_features(catalog, config)
    
    X, y = gen_X_y(df)

    model = get_model(config)
    model.fit(X, y)

    save_prediction_model(model, config)


def predict(df_test, config):
    catalog = get_data_catalog(config)
    df = build_features(catalog, config)
    df = df_test.merge(df)

    X, y = gen_X_y(df)

    model = load_prediction_model(config)

    return model.predict_proba(X)


def evaluate_model(catalog, config):
    df = build_features(catalog, config, does_retrain=False)
    
    msk = np.random.rand(len(df)) < 0.8
    df_train = df[msk]
    df_test = df[~msk]
    
    X_train, y_train = gen_X_y(df_train)
    
    model = get_model(config)
    model.fit(X_train, y_train)
    
    X_test, y_test= gen_X_y(df_test)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    main()
