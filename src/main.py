
import os, json, argparse, pathlib
import pandas as pd

from .fetch import fetch_recent
from .analyze import build_dataframe, timeseries, similarity_clusters, build_interaction_network, summarize
from .visualize import plot_timeseries, plot_network

def load_config() -> dict:
    cfg_path = pathlib.Path("config.json")
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    sample = pathlib.Path("config.sample.json")
    if sample.exists():
        with open(sample, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_sample(path: str):
    tweets = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            tweets.append(json.loads(line))
    return tweets

def ensure_outdir(path: str):
    os.makedirs(path, exist_ok=True)
    return path

def main():
    p = argparse.ArgumentParser(description="Twitter/X Campaign Detector")
    p.add_argument("--query", type=str, help="Search query (Twitter API v2 Recent Search syntax)")
    p.add_argument("--minutes", type=int, default=None, help="How many minutes back to consider (local filter)")
    p.add_argument("--max-results", type=int, default=None, help="Max tweets to fetch (<= 100 per API page)")
    p.add_argument("--similarity-threshold", type=float, default=None, help="Cosine similarity threshold for clustering [0..1]")
    p.add_argument("--out", type=str, default="output", help="Output directory")
    p.add_argument("--sample", type=str, help="Path to JSONL with tweet-like rows for offline analysis")
    args = p.parse_args()

    cfg = load_config()

    query = args.query or cfg.get("query")
    minutes = args.minutes or int(cfg.get("minutes", 180))
    max_results = args.max_results or int(cfg.get("max_results", 200))
    sim_thr = args.similarity_threshold or float(cfg.get("similarity_threshold", 0.8))
    outdir = ensure_outdir(args.out)

    if args.sample:
        tweets = load_sample(args.sample)
    else:
        if not query:
            raise SystemExit("Provide --query or set it in config.json")
        tweets = fetch_recent(query, max_results=max_results, minutes=minutes, config=cfg)

    # -------- Analysis pipeline --------
    df = build_dataframe(tweets)
    ts = timeseries(df)
    cdf, clusters = similarity_clusters(df, threshold=sim_thr)
    g = build_interaction_network(df)
    summary = summarize(df, ts, cdf, g)

    # -------- Save outputs --------
    df.to_csv(os.path.join(outdir, "tweets.csv"), index=False)
    ts.to_csv(os.path.join(outdir, "timeseries.csv"), index=False)
    cdf.to_csv(os.path.join(outdir, "similarity_clusters.csv"), index=False)
    summary.to_csv(os.path.join(outdir, "summary.csv"), index=False)

    # -------- Visuals --------
    plot_timeseries(ts, os.path.join(outdir, "timeseries.png"))
    plot_network(g, os.path.join(outdir, "network.png"))

    print("Done. Outputs in:", outdir)

if __name__ == "__main__":
    main()
