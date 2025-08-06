# # save_csv.py

import csv
from loguru import logger
import pandas as pd
from datetime import datetime
import os

def save_posts_to_csv(posts, base_filename='harmful_posts.csv'):
    """Append post data to a single CSV file."""
    fields = ['id', 'subreddit', 'title', 'selftext', 'author',
              'created_utc', 'score', 'num_comments', 'url']

    file_exists = os.path.exists(base_filename)

    with open(base_filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        for post in posts:
            writer.writerow(post)

    logger.info(f"✅ Appended {len(posts)} posts to {base_filename}")

def save_problematic_posts(df_final, base_filename='problematic_users.csv'):
    """Append problematic posts (marked 'Problematic') to one CSV."""
    problematic = df_final[df_final['statement'] == 'Problematic']
    enrichdf = problematic[['id', 'author', 'title', 'created_utc', 'statement']]

    file_exists = os.path.exists(base_filename)
    enrichdf.to_csv(base_filename, mode='a', index=False, header=not file_exists, encoding='utf-8')

    logger.info(f"✅ Appended {len(enrichdf)} problematic posts to {base_filename}")

def save_user_data(df, base_filename='user_data_last_2_months.csv'):
    """Append user data to fixed CSV."""
    file_exists = os.path.exists(base_filename)
    df.to_csv(base_filename, mode='a', index=False, header=not file_exists, encoding='utf-8')
    logger.info(f"✅ Appended user data to {base_filename}")

def save_llm_results(results, base_filename='llm_analysis_results.csv'):
    """Append LLM results to one CSV."""
    df = pd.DataFrame(results)
    file_exists = os.path.exists(base_filename)
    df.to_csv(base_filename, mode='a', index=False, header=not file_exists, encoding='utf-8')
    logger.info(f"✅ Appended LLM analysis results to {base_filename}")
