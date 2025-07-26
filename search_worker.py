# search_worker.py
from datetime import datetime

def search_and_collect(reddit, subreddit, term, limit=20):
    local_results = []
    print(f"Searching '{term}' in r/{subreddit}")
    try:
        for submission in reddit.subreddit(subreddit).search(term, sort='new', limit=limit):
            local_results.append({
                'id': submission.id,
                'subreddit': str(submission.subreddit),
                'title': submission.title,
                'selftext': submission.selftext,
                'author': str(submission.author) if submission.author else '[deleted]',
                'created_utc': datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                'score': submission.score,
                'num_comments': submission.num_comments,
                'url': submission.url
            })
    except Exception as e:
        print(f"Error searching '{term}' in r/{subreddit}: {e}")
    return local_results
