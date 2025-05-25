from functools import cache
import numpy as np
import os
import pandas as pd
import pickle
import random

from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
# Global vars

_cache = {}

def _reload_features_cache():
    global _cache
    _cache = {}

def build_features(catalog, config, does_retrain=False):
    """Build features for click prediction"""
    if does_retrain:
        train_page_cluster_predictor(catalog, config)
        clusterize_users(catalog, config)
        save_feature_models(config)
    else:
        load_feature_models(config)

    p_clusters = config["features"]["pages"]["nb_clusters"]
    click_data = catalog.load("click")
    
    # Number of ad seen this day before this page
    click_data["date"] = click_data["timestamp"].apply(lambda txt: txt[:10])
    click_data["count"] = 1
    click_data["user_ads_seen"] = (
        click_data.groupby(["user_id", "date"])["count"]
        .cumsum()
    )


    click_data = click_data[["user_id", "page_id", "ad_id", "user_ads_seen", "clicked"]]

    user_clusters, _ = clusterize_users(catalog, config)
    page_clusters, _, _ = clusterize_pages(catalog, config)
    
    click_features = click_data.merge(user_clusters[['user_id', 'cluster']], on='user_id', how='left')
    click_features = click_features.rename(columns={'cluster': 'user_cluster'})
    
    cluster_probs = []
    page_to_cluster_prob = {
        page_id: get_page_cluster_probabilities(catalog, page_id, p_clusters)
        for page_id in click_features["page_id"].unique()
    }

    cluster_probs = [page_to_cluster_prob[page_id] for page_id in click_features["page_id"]]
    
    cluster_prob_df = pd.DataFrame(
        cluster_probs, 
        columns=[f'page_cluster_prob_{i}' for i in range(p_clusters)]
    )
    
    click_features = pd.concat(
        [click_features.reset_index(drop=True),  cluster_prob_df.reset_index(drop=True)],
        axis=1,
    )
    
    _cache["click_features"] = click_features
    
    return click_features


def gen_X_y(df):
    y = df.pop("clicked")
    X = df.drop(['user_id', 'page_id', 'ad_id'], axis=1)

    return X, y


def preprocess_text(text_series):
    text_series = text_series.fillna("")
    text_series = text_series.str.lower()
    return text_series

def clusterize_pages(catalog, config):
    if "page_clusters" in _cache:
        return _cache["page_clusters"], _cache["page_cluster_model"], _cache["page_vectorizer"]
    
    k = config["features"]["pages"]["nb_clusters"]
    seed = config["seed"]

    page_data = catalog.load("page")
    
    vect = TfidfVectorizer(max_features=1000, stop_words='english')
    X_pages = vect.fit_transform(preprocess_text(page_data['page_text']))
    
    km = KMeans(n_clusters=k, random_state=seed)
    page_clusters = km.fit_predict(X_pages)
    
    page_data['cluster'] = page_clusters
    
    _cache["page_clusters"] = page_data
    _cache["page_cluster_model"] = km
    _cache["page_vectorizer"] = vect
    
    return page_data, km, vect

def train_page_cluster_predictor(catalog, config):
    page_data, _, vect = clusterize_pages(catalog, config)
    
    X_pages = vect.transform(preprocess_text(page_data['page_text']))
    y = page_data['cluster']
    
    lr = LogisticRegression(max_iter=1000, random_state=config["seed"])
    lr.fit(X_pages, y)
    
    _cache["page_cluster_predictor"] = lr
    
    return lr

def process_user_data(catalog):
    """Process user data for clustering"""
    # Get data
    user_data = catalog.load("user")
    bid_data = catalog.load("bid")
    
    # One-hot encode user features
    user_processed = pd.get_dummies(user_data, columns=['sex', 'city', 'device'])
    
    # Join with bid data to get user-page interactions
    user_visits = (
        bid_data.groupby(["user_id", "page_id"])
        .size()
        .unstack(1)
        .fillna(0)
    )
    user_visits.columns = [str(c) for c in user_visits.columns]
    user_processed = user_processed.merge(user_visits, on='user_id', how='left')
    
    # Cache processed data
    _cache["processed_user_data"] = user_processed
    
    return user_processed

def clusterize_users(catalog, config):
    if "user_clusters" in _cache:
        return _cache["user_clusters"], _cache["user_cluster_model"]
    
    k = config["features"]["user"]["nb_clusters"]
    seed = config["seed"]

    user_processed = process_user_data(catalog)
    
    km = KMeans(n_clusters=k, random_state=seed)
    user_clusters = km.fit_predict(user_processed.drop('user_id', axis=1))
    
    user_processed['cluster'] = user_clusters
    
    _cache["user_clusters"] = user_processed
    _cache["user_cluster_model"] = km
    
    return user_processed, km

@cache
def get_page_cluster_probabilities(catalog, page_id, p_clusters):
    """Get probabilities of a page belonging to each cluster"""
    page_data, _, vect = clusterize_pages(catalog, p_clusters)

    lr = _cache.get("page_cluster_predictor")
    if not lr:
        lr = train_page_cluster_predictor()
    
    page_text = page_data[page_data['page_id'] == page_id]['page_text'].values[0]
    
    X = vect.transform([preprocess_text(pd.Series([page_text]))[0]])
    
    probs = lr.predict_proba(X)[0]
    
    return probs


def save_feature_models(config):
    if not os.path.exists("models"):
        os.makedirs("models")
    
    # Save page vectorizer
    with open(config["features"]["pages"]["vectorizer_path"], "wb") as f:
        pickle.dump(_cache["page_vectorizer"], f)
    
    # Save page cluster predictor
    with open(config["features"]["pages"]["model_path"], "wb") as f:
        pickle.dump(_cache["page_cluster_predictor"], f)
    
    # Save user cluster model
    with open(config["features"]["user"]["model_path"], "wb") as f:
        pickle.dump(_cache["user_cluster_model"], f)
    

def load_feature_models(config):
    # Load page vectorizer
    with open(config["features"]["pages"]["vectorizer_path"], "rb") as f:
        _cache["page_vectorizer"] = pickle.load(f)
    
    # Load page cluster predictor
    with open(config["features"]["pages"]["model_path"], "rb") as f:
        _cache["page_cluster_predictor"] = pickle.load(f)
    
    # Load user cluster model
    with open(config["features"]["user"]["model_path"], "rb") as f:
        _cache["user_cluster_model"] = pickle.load(f)
    
