# Twitter/X Campaign Detector

Detect coordinated campaigns (hashtag pushes, astroturfing, bot-like boosting) using the Twitter/X API v2 and lightweight analytics.

## Features
- Recent search data collection from Twitter/X API v2 (requires Bearer Token).
- Time-series spike detection for hashtags/keywords.
- Near-duplicate & high-similarity tweet clustering (TF‑IDF + cosine).
- User/account heuristics (age, follower ratio, posting density if accessible).
- Retweet/mention network construction and cluster scoring.
- Simple visualizations saved to `output/` (PNG figures + CSV summaries).

> Can't call the API here, but the code is fully runnable on your machine. A small synthetic dataset is provided at `data/sample_tweets.jsonl` so you can test analysis and charts without credentials.

## Quickstart

1. **Create a virtual env & install requirements**
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set your Twitter/X API bearer token**
- Option A (env var):
```bash
export TWITTER_BEARER_TOKEN=YOUR_TOKEN   # Windows PowerShell: $Env:TWITTER_BEARER_TOKEN="YOUR_TOKEN"
```
- Option B (config file): copy `config.sample.json` to `config.json` and fill in the token + defaults.

3. **Run with live API (recent search)**
```bash
python src/main.py --query "#SaveTheEarth lang:en -is:retweet" --minutes 180 --max-results 200
```

4. **Run ONLY the analysis on the provided sample data** (offline demo):
```bash
python src/main.py --sample data/sample_tweets.jsonl
```

5. **Outputs**
- `output/timeseries.png` – minute-level tweet volume.
- `output/similarity_clusters.csv` – clusters of near-duplicate tweets.
- `output/network.png` – retweet/mention network.
- `output/summary.csv` – key metrics and indicators.

## Common Queries
- Hashtag campaign: `"#YourHashtag lang:en -is:retweet"`
- Keyword push: `"Your Brand OR 'Your Product' lang:en -is:retweet"`
- Event hype: `"EventName (lang:en OR lang:hi) -is:retweet"`

## How it works (high level)
- **Fetch**: Recent tweets via `/2/tweets/search/recent` (fields: author_id, created_at, public_metrics, entities).
- **Normalize**: Lowercase, drop URLs/mentions/stopwords, simple lemmatization-like stemming.
- **Similarity**: TF‑IDF vectorization → cosine similarity → connected components for clusters above a threshold.
- **Time spikes**: Median absolute deviation (MAD) to flag anomalous minutes.
- **Network**: Nodes = users; edges for retweet/reply/mention; communities ≈ coordination pockets.

## Notes
- Free tiers may restrict fields/rate limits. Code degrades gracefully if some fields are missing.
- For large pulls, script batches through pages until `--max-results` is reached.
- This is a research/education starter, **not** a definitive bot/campaign labeling tool.
