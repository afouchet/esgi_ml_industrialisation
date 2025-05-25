from functools import cache
import numpy as np
import pandas as pd
import random

from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer


def build_features(catalog, config):
    """Build features for click prediction"""
    df = get_click_features(catalog)

    df = add_user_features(df, catalog, config)

    df = add_cluster_features(df, catalog, config)
    
    return df


def train_feature_store(catalog, config):
    train_page_cluster_predictor(catalog, config)
    clusterize_users(catalog, config)


def gen_X_y(df):
    y = df.pop("clicked")
    X = df.drop(['user_id', 'page_id', 'ad_id'], axis=1)

    return X, y


def get_click_features(catalog):
    click_data = catalog.load("click")
    
    # Number of ad seen this day before this page
    click_data["date"] = click_data["timestamp"].apply(lambda txt: txt[:10])
    click_data["count"] = 1
    click_data["user_ads_seen"] = (
        click_data.groupby(["user_id", "date"])["count"]
        .cumsum()
    )


    return click_data[["user_id", "page_id", "ad_id", "user_ads_seen", "clicked"]]


def add_user_features(df, catalog, config):
    user_clusters, _ = clusterize_users(catalog, config)
    df = df.merge(
        user_clusters[['user_id', 'cluster']], on='user_id', how='left',
    )
    return df.rename(columns={'cluster': 'user_cluster'})
    

def add_cluster_features(df, catalog, config):
    p_clusters = config["features"]["pages"]["nb_clusters"]

    page_data = catalog.load("pages")
    page_id_to_text = {row.page_id: row.page_text for _, row in page_data.iterrows()}

    cluster_probs = []
    page_to_cluster_prob = {
        page_id: get_page_cluster_probabilities(catalog, page_id_to_text[page_id])
        for page_id in df["page_id"].unique()
    }

    cluster_probs = [page_to_cluster_prob[page_id] for page_id in df["page_id"]]
    
    cluster_prob_df = pd.DataFrame(
        cluster_probs, 
        columns=[f'page_cluster_prob_{i}' for i in range(p_clusters)]
    )
    
    return pd.concat(
        [df.reset_index(drop=True),  cluster_prob_df.reset_index(drop=True)],
        axis=1,
    )


def preprocess_text(text_series):
    text_series = text_series.fillna("")
    text_series = text_series.str.lower()
    return text_series

def clusterize_pages(catalog, config):
    k = config["features"]["pages"]["nb_clusters"]
    seed = config["seed"]

    page_data = catalog.load("pages")
    
    vect = TfidfVectorizer(max_features=1000, stop_words='english')
    X_pages = vect.fit_transform(preprocess_text(page_data['page_text']))
    
    km = KMeans(n_clusters=k, random_state=seed)
    page_clusters = km.fit_predict(X_pages)
    
    page_data['cluster'] = page_clusters

    catalog.save_vectorizer("pages", vect)
    
    return page_data, km, vect


def train_page_cluster_predictor(catalog, config):
    page_data, _, vect = clusterize_pages(catalog, config)
    
    X_pages = vect.transform(preprocess_text(page_data['page_text']))
    y = page_data['cluster']
    
    lr = LogisticRegression(max_iter=1000, random_state=config["seed"])
    lr.fit(X_pages, y)
    
    catalog.save_model("pages", lr)
    
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
    
    
    return user_processed

def clusterize_users(catalog, config):
    k = config["features"]["user"]["nb_clusters"]
    seed = config["seed"]

    user_processed = process_user_data(catalog)
    
    km = KMeans(n_clusters=k, random_state=seed)
    user_clusters = km.fit_predict(user_processed.drop('user_id', axis=1))
    
    user_processed['cluster'] = user_clusters
    
    catalog.save_model("user", km)
    
    return user_processed, km

@cache
def get_page_cluster_probabilities(catalog, page_text):
    """Get probabilities of a page belonging to each cluster"""
    vect = catalog.load_vectorizer("pages")
    lr = catalog.load_model("pages")
    
    X = vect.transform([preprocess_text(pd.Series([page_text]))[0]])
    
    probs = lr.predict_proba(X)[0]
    
    return probs
