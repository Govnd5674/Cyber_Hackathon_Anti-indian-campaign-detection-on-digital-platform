import pandas as pd
import numpy as np 
import tweepy
import praw

from googleapiclient.discovery import build



## TWITER API

# Replace with your Bearer Token
BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"

# Initialize the Tweepy Client
client = tweepy.Client(BEARER_TOKEN)

# Define your search query
# You can use operators like -is:retweet to exclude retweets
# and lang:en to get only English tweets.
query = "#MachineLearning -is:retweet lang:en"

# Use the search_recent_tweets method
# max_results can be between 10 and 100
response = client.search_recent_tweets(query=query, max_results=100, tweet_fields=["created_at", "lang", "public_metrics"])

# The response object contains the data
tweets = response.data

# Create a list of dictionaries to store tweet info
tweet_data = []
if tweets:
    for tweet in tweets:
        tweet_info = {
            'id': tweet.id,
            'text': tweet.text,
            'created_at': tweet.created_at,
            'retweet_count': tweet.public_metrics['retweet_count'],
            'like_count': tweet.public_metrics['like_count']
        }
        tweet_data.append(tweet_info)

print(f"Collected {len(tweet_data)} tweets.")

# You can now proceed to save this data (see Step 4)



# Create a class to handle the stream
class MyStreamingClient(tweepy.StreamingClient):
    # This function is called when a tweet is received
    def on_tweet(self, tweet):
        print(f"ID: {tweet.id} | Text: {tweet.text}")
        print("-" * 20)
        # Here you would add code to save the tweet to a file or database

# Initialize your streaming client
streaming_client = MyStreamingClient(BEARER_TOKEN)

# Before you start the stream, clear any existing rules
rules = streaming_client.get_rules().data
if rules:
    rule_ids = [rule.id for rule in rules]
    streaming_client.delete_rules(rule_ids)

# Add a rule to the stream (e.g., track the keyword "python")
streaming_client.add_rules(tweepy.StreamRule("python lang:en"))

# Start the stream
print("Starting stream to collect tweets with the keyword 'python'...")
streaming_client.filter()


if tweet_data:
    # Create a pandas DataFrame
    df = pd.DataFrame(tweet_data)

    # Save the DataFrame to a CSV file
    df.to_csv("twitter_data.csv", index=False)

    print("Data successfully saved to twitter_data.csv")
else:
    print("No tweets were collected to save.")


## REDIT API

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="script:my-data-scraper:v1.0 (by /u/your_username)",
)

print(reddit.read_only)

subreddit = reddit.subreddit("AskReddit")

print(f"Fetching top 5 posts from r/{subreddit.display_name}...\n")

# .hot(), .new(), .top() are available methods
# The limit parameter specifies how many posts to fetch
for submission in subreddit.hot(limit=5):
    print(f"Title: {submission.title}")
    print(f"Score: {submission.score}")
    print(f"URL: {submission.url}")
    print("-" * 20)

url = "https://www.reddit.com/r/learnpython/comments/101sxx2/daily_general_discussion_and_questions_thread/"

submission = reddit.submission(url=url)

# The comments are in a tree structure
# .list() flattens the tree to get all comments
submission.comments.replace_more(limit=0) # Removes "MoreComments" objects

print(f"Fetching comments for: '{submission.title}'\n")

# Iterate through the top-level comments
for top_level_comment in submission.comments:
    print(f"Author: {top_level_comment.author} | Body: {top_level_comment.body[:80]}...")

subreddit = reddit.subreddit("dataisbeautiful")

for submission in subreddit.search("population", sort="relevance", time_filter="year"):
    print(f"Found post: {submission.title}")


## YOUTUBE API

# Your API key
API_KEY = "YOUR_API_KEY_HERE"  ## AIzaSyB_CTK63eADS1ZPM1f-9LQchJ8beuDd3Lo
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Create a YouTube resource object
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

# Call the search.list method to retrieve results
search_response = youtube.search().list(
    q="machine learning basics",  # The search query
    part="snippet",             # Specifies the resource properties to return
    maxResults=5                # The maximum number of results
).execute()

print("Found Videos:\n")

# Process the search results
for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
        title = search_result["snippet"]["title"]
        video_id = search_result["id"]["videoId"]
        print(f"Title: {title}")
        print(f"Video ID: {video_id}")
        print(f"Link: https://www.youtube.com/watch?v={video_id}\n")