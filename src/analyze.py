
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from datetime import timedelta
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import normalize_text, minute_bucket, safe_get

def build_dataframe(tweets: List[Dict]) -> pd.DataFrame:
    rows = []
    for t in tweets:
        rows.append({
            "id": t.get("id"),
            "text": t.get("text", ""),
            "created_at": t.get("created_at"),
            "author_id": t.get("author_id"),
            "retweet_count": safe_get(t, "public_metrics", "retweet_count", default=0),
            "reply_count": safe_get(t, "public_metrics", "reply_count", default=0),
            "like_count": safe_get(t, "public_metrics", "like_count", default=0),
            "quote_count": safe_get(t, "public_metrics", "quote_count", default=0),
            "lang": t.get("lang"),
            "normalized": normalize_text(t.get("text", "")),
            "bucket": minute_bucket(t.get("created_at")),
            "mentions": [m.get("username") for m in safe_get(t, "entities", "mentions", default=[])],
            "hashtags": [h.get("tag") for h in safe_get(t, "entities", "hashtags", default=[])],
            "referenced": t.get("referenced_tweets", []),
            "username": safe_get(t, "_user", "username", default=None),
        })
    df = pd.DataFrame(rows)
    return df

def timeseries(df: pd.DataFrame) -> pd.DataFrame:
    ts = df.groupby("bucket")["id"].count().rename("count").reset_index()
    ts = ts.sort_values("bucket")
    if ts["count"].empty:
        ts["zscore"] = []
        ts["anomaly"] = []
        return ts
    # anomaly via MAD
    x = ts["count"].values.astype(float)
    med = np.median(x)
    mad = np.median(np.abs(x - med)) or 1.0
    z = 0.6745 * (x - med) / mad
    ts["zscore"] = z
    ts["anomaly"] = np.abs(z) > 3.5
    return ts

def similarity_clusters(df: pd.DataFrame, threshold: float = 0.8) -> Tuple[pd.DataFrame, Dict[int, list]]:
    texts = df["normalized"].fillna("").tolist()
    if len(texts) == 0:
        return pd.DataFrame(columns=["cluster_id","tweet_id","username","text"]), {}

    vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1,2))
    X = vectorizer.fit_transform(texts)
    sims = cosine_similarity(X)
    n = sims.shape[0]

    # build graph where edges = similarity >= threshold
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i+1, n):
            if sims[i, j] >= threshold:
                g.add_edge(i, j)

    components = list(nx.connected_components(g))
    cluster_map = {}
    rows = []
    for cid, comp in enumerate(components):
        for idx in comp:
            cluster_map[idx] = cid
    for i, row in df.reset_index().iterrows():
        rows.append({
            "cluster_id": cluster_map.get(i, i),
            "tweet_id": row["id"],
            "username": row["username"],
            "text": row["text"]
        })
    cdf = pd.DataFrame(rows).sort_values(["cluster_id", "tweet_id"])
    return cdf, {cid: list(comp) for cid, comp in enumerate(components)}

def build_interaction_network(df: pd.DataFrame) -> nx.Graph:
    g = nx.DiGraph()
    for _, r in df.iterrows():
        u = r["username"] or r["author_id"]
        if not u: 
            continue
        g.add_node(u)
        # mentions
        for m in r.get("mentions", []) or []:
            g.add_node(m)
            g.add_edge(u, m, kind="mention")
        # referenced tweets (retweet/reply/quote)
        for ref in r.get("referenced", []) or []:
            # We don't have the target username reliably in all tiers; use placeholder id
            target = ref.get("id")
            if target:
                g.add_node(target)
                g.add_edge(u, target, kind=ref.get("type", "ref"))
    return g

def summarize(df: pd.DataFrame, ts: pd.DataFrame, cdf: pd.DataFrame, g: nx.Graph) -> pd.DataFrame:
    total = len(df)
    anomalies = int(ts["anomaly"].sum()) if "anomaly" in ts.columns else 0
    largest_cluster = cdf["cluster_id"].value_counts().head(1).to_dict()
    components = nx.number_weakly_connected_components(g.to_undirected())
    density = nx.density(g.to_undirected()) if g.number_of_nodes() > 1 else 0.0

    summary = {
        "total_tweets": total,
        "unique_users": df["username"].nunique(),
        "anomalous_minutes": anomalies,
        "largest_cluster_size": list(largest_cluster.values())[0] if largest_cluster else 0,
        "network_nodes": g.number_of_nodes(),
        "network_edges": g.number_of_edges(),
        "network_density": round(density, 5),
        "connected_components": components,
    }
    return pd.DataFrame([summary])
