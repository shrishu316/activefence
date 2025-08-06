# user_data_worker.py
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from loguru import logger

def collect_user_data(reddit, user_row, lookback_days=60):
    user_name = user_row['author']
    user_id = user_row['id']
    collected = []

    now = datetime.utcnow()
    cutoff = now - timedelta(days=lookback_days)

    try:
        redditor = reddit.redditor(user_name)
        _ = redditor.link_karma  # force fetch, will raise if not found

        # Fetch submissions
        for submission in redditor.submissions.new(limit=50):
            created = datetime.utcfromtimestamp(submission.created_utc)
            if created >= cutoff:
                collected.append({
                    'user_id': user_id,
                    'user_name': user_name,
                    'type': 'submission',
                    'created_utc': created.isoformat(),
                    'subreddit': str(submission.subreddit),
                    'title': submission.title,
                    'body_or_selftext': submission.selftext,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'url': submission.url
                })

        # Fetch comments
        for comment in redditor.comments.new(limit=50):
            created = datetime.utcfromtimestamp(comment.created_utc)
            if created >= cutoff:
                collected.append({
                    'user_id': user_id,
                    'user_name': user_name,
                    'type': 'comment',
                    'created_utc': created.isoformat(),
                    'subreddit': str(comment.subreddit),
                    'title': '',
                    'body_or_selftext': comment.body,
                    'score': comment.score,
                    'num_comments': None,
                    'url': f"https://www.reddit.com{comment.permalink}"
                })

    except Exception as e:
        # print(f"❌ Error fetching data for user '{user_name}': {e}")
        collected.append({
            'user_id': user_id,
            'user_name': user_name,
            'type': 'error',
            'created_utc': '',
            'subreddit': '',
            'title': '',
            'body_or_selftext': f"Error: {e}",
            'score': '',
            'num_comments': '',
            'url': ''
        })

    return collected

def collect_all_users_data(reddit, users_df, lookback_days=60, max_workers=6):
    all_results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(collect_user_data, reddit, row, lookback_days)
            for _, row in users_df.iterrows()
        ]

        for future in as_completed(futures):
            all_results.extend(future.result())

    logger.info(f"✅ Collected data for {len(all_results)} items (posts, comments, or errors)")
    return pd.DataFrame(all_results)
