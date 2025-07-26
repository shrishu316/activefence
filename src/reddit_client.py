# reddit_client.py
import praw
from resources.dev.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, USER_AGENT

def get_reddit_client():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    return reddit
