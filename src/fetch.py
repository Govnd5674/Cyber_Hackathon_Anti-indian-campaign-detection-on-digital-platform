
import os, time, requests
from typing import List, Dict, Optional

API_URL = "https://api.twitter.com/2/tweets/search/recent"

FIELDS = {
    "tweet.fields": "id,text,author_id,created_at,public_metrics,entities,referenced_tweets,lang",
    "user.fields": "id,username,created_at,public_metrics,verified",
    "expansions": "author_id,referenced_tweets.id.author_id,entities.mentions.username",
}

def bearer_token_from_env_or_config(config: Dict) -> str:
    token = os.environ.get("TWITTER_BEARER_TOKEN") or config.get("bearer_token")
    if not token:
        raise RuntimeError("Missing bearer token. Set TWITTER_BEARER_TOKEN or add it to config.json.")
    return token

def fetch_recent(query: str, max_results: int, minutes: int, config: Dict) -> List[Dict]:
    token = bearer_token_from_env_or_config(config)
    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "query": query,
        "max_results": min(max_results, 100),
        **FIELDS
    }
    # Twitter/X recent search is last ~7 days by default; we limit locally after fetch
    out, total = [], 0
    next_token = None
    earliest_ts = time.time() - minutes * 60

    while True:
        if next_token:
            params["next_token"] = next_token
        resp = requests.get(API_URL, headers=headers, params=params, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
        payload = resp.json()
        data = payload.get("data", [])
        includes = payload.get("includes", {})
        users = {u["id"]: u for u in includes.get("users", [])}

        for t in data:
            t["_user"] = users.get(t.get("author_id"))
            out.append(t)
            total += 1
            if total >= max_results:
                break

        if total >= max_results:
            break

        next_token = payload.get("meta", {}).get("next_token")
        if not next_token:
            break

        time.sleep(1.0)  # simple rate limiting

    return out
