# # save_csv.py

import csv
import pandas as pd
from datetime import datetime

def timestamped_filename(base_name, ext='csv'):
    """Generate filename with current timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{timestamp}.{ext}"

def save_posts_to_csv(posts, base_filename='harmful_posts'):
    filename = timestamped_filename(base_filename)
    fields = ['id', 'subreddit', 'title', 'selftext', 'author',
              'created_utc', 'score', 'num_comments', 'url']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for post in posts:
            writer.writerow(post)
    print(f"✅ Saved {len(posts)} posts to {filename}")

def save_problematic_posts(df_final, base_filename='problematic_users'):
    filename = timestamped_filename(base_filename)
    problematic = df_final[df_final['statement'] == 'Problematic']
    enrichdf = problematic[['id', 'author', 'title', 'created_utc', 'statement']]
    enrichdf.to_csv(filename, index=False, encoding='utf-8')
    print(f"✅ Saved {len(enrichdf)} problematic posts to {filename}")

def save_user_data(df, base_filename='src/data/user_data_last_2_months'):
    filename = timestamped_filename(base_filename)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"✅ Saved user data to {filename}")

def save_llm_results(results, base_filename='llm_analysis_results'):
    print("CSV....>", base_filename)
    filename = timestamped_filename(base_filename)
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"✅ Saved LLM analysis results to {filename}")
