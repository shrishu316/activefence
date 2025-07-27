# main.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from reddit_client import get_reddit_client
from resources.dev.config import TARGET_SUBREDDITS, SEARCH_TERMS, DATA_DAYS_LOOKBACK
from search_worker import search_and_collect
from sentiment_analysis import analyze_sentiment
from save_csv import save_posts_to_csv, save_problematic_posts, save_user_data
from user_data_worker import collect_all_users_data
import pandas as pd
import json
from llm_analysis import group_titles_by_user, analyze_users_with_llm
from save_csv import save_llm_results
import glob
import os


def main():
    reddit = get_reddit_client()
    collected_posts = []

    # -------------------------
    # 1. Collect posts in parallel
    # -------------------------
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = []
        for subreddit in TARGET_SUBREDDITS:
            for term in SEARCH_TERMS:
                futures.append(
                    executor.submit(search_and_collect, reddit, subreddit, term, limit=20)
                )

        for future in as_completed(futures):
            collected_posts.extend(future.result())

    print(f"Collected {len(collected_posts)} posts.")

    save_posts_to_csv(collected_posts, base_filename='harmful_posts.csv')

    # Dynamically find the latest saved harmful_posts.csv_* file

    csv_matches = glob.glob("harmful_posts.csv_*")
    if not csv_matches:
        print("No saved CSV found for sentiment analysis.")
        return
    latest_csv = max(csv_matches, key=os.path.getctime)
    print(f"Using latest CSV for sentiment analysis: {latest_csv}")

    # -------------------------
    # 2. Sentiment analysis
    # -------------------------
    df_final = analyze_sentiment(latest_csv)
    save_problematic_posts(df_final, base_filename='problematic_users.csv')
    

    csv_matches = glob.glob("problematic_users.csv_*")
    if not csv_matches:
        print("No saved CSV found for problematic_users.")
        return
    latest_csv = max(csv_matches, key=os.path.getctime)
    print(f"Using latest CSV for problematic_users: {latest_csv}")


    # -------------------------
    # 3. Load problematic users
    # -------------------------
    users_df = pd.read_csv(latest_csv)
    print(f"Loaded {len(users_df)} problematic users")

    # -------------------------
    # 4. Collect user data (last 2 months)
    # -------------------------
    user_data_df = collect_all_users_data(reddit, users_df, lookback_days=DATA_DAYS_LOOKBACK)
    save_user_data(user_data_df, base_filename='user_data_last_2_months.csv')

    csv_matches = glob.glob("user_data_last_2_months.csv_*")
    if not csv_matches:
        print("No saved CSV found for user_data_last_2_months.")
        return
    latest_csv = max(csv_matches, key=os.path.getctime)
    print(f"Using latest CSV for user_data_last_2_months: {latest_csv}")



    # -------------------------
    # 5. Prepare data for LLM
    # -------------------------
    input_file = latest_csv
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} items from {input_file}")

    # Drop empty titles & unneeded columns
    df = df.dropna(subset=['title'])
    df = df.drop(['user_id', 'type', 'subreddit', 'body_or_selftext', 'score', 'num_comments', 'url'], axis=1)

    # Convert to JSON lines
    json_file = 'enriched_data.json'
    df.to_json(json_file, orient='records', lines=True)
    print(f"Saved to {json_file}")

    # Load JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        enriched_list = [json.loads(line) for line in f if line.strip()]

    # Group titles by user
    grouped = group_titles_by_user(enriched_list)
    print(f"Grouped data for {len(grouped)} users")

    # -------------------------
    # 6. Run LLM analysis
    # -------------------------
    llm_results = analyze_users_with_llm(grouped)
    save_llm_results(llm_results, base_filename='llm_analysis_results.csv')


if __name__ == '__main__':
    main()
