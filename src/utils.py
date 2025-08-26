
import re
import math
import html
from datetime import datetime, timezone
from dateutil import parser

URL_RE = re.compile(r'https?://\S+')
MENTION_RE = re.compile(r'@\w+')
HASHTAG_RE = re.compile(r'#\w+')

STOPWORDS = set("""a an the and or but if then else when where while with without to from by for of on at into over under again further do does did doing have has had having be is are was were been being this that these those it its itself i me my we our you your he she they them his her their what which who whom why how not no nor very can will just""".split())

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = text.lower()
    text = URL_RE.sub(' ', text)
    text = MENTION_RE.sub(' ', text)
    text = re.sub(r'[^a-z0-9#\s]', ' ', text)
    tokens = [t for t in text.split() if t not in STOPWORDS and len(t) > 2]
    # light stemming: drop trailing 's' or 'ing'
    norm = []
    for t in tokens:
        if t.endswith('ing') and len(t) > 5:
            t = t[:-3]
        elif t.endswith('s') and len(t) > 3:
            t = t[:-1]
        norm.append(t)
    return ' '.join(norm)

def parse_time(ts):
    if isinstance(ts, datetime):
        return ts.astimezone(timezone.utc)
    try:
        return parser.isoparse(ts).astimezone(timezone.utc)
    except Exception:
        return None

def minute_bucket(ts):
    ts = parse_time(ts)
    if not ts: 
        return None
    return ts.replace(second=0, microsecond=0)

def safe_get(d, *keys, default=None):
    cur = d
    for k in keys:
        if cur is None:
            return default
        cur = cur.get(k)
    return cur if cur is not None else default
