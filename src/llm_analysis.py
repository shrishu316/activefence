import json
import time
import re
import csv
import requests
from loguru import logger
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from resources.dev.config import GOOGLE_API_KEY, GEMINI_ENDPOINT
from ratelimit import limits, sleep_and_retry
from requests.exceptions import RequestException


def group_titles_by_user(enriched_list):
    user_titles = defaultdict(list)
    for item in enriched_list:
        user = item.get('user_name')
        title = item.get('title')
        if user and title:
            user_titles[user].append(title)
    return dict(user_titles)

@sleep_and_retry
@limits(calls=60, period=60)
def query_gemini(username, activity_list):
    prompt = f"""
You are an expert in hate speech detection and social media analysis.

You will be given a list of Reddit post titles made by a user over the past 2 months. Your task is to analyze the content for signs of anti-Semitic behavior.

Rate the user's activity with:
- A score from 0 (no anti-Semitism) to 10 (severe anti-Semitic behavior)
- A brief explanation justifying your score (2–4 sentences)

IMPORTANT: Return ONLY the JSON output. Do not include any explanations, greetings, or markdown formatting like ```json.

The output must be valid JSON in this format:
{{
  "username": "{username}",
  "score": SCORE_HERE,
  "explanation": "Your explanation here"
}}

Reddit post titles for user "{username}":
{json.dumps(activity_list, indent=2)}
"""

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GOOGLE_API_KEY
    }

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    for attempt in range(3): 
        try:
            response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]

            if text.strip().startswith("```json"):
                text = text.strip().lstrip("```json").rstrip("```").strip()

            logger.info(f"✅ LLM response OK for user: {username}")
            return text

        except RequestException as e:
            logger.warning(f"❌ Attempt {attempt + 1}: LLM request failed for {username}: {e}")
            time.sleep(2 ** attempt)

    logger.error(f"⛔ Final failure for user {username} after 3 attempts.")
    return None

def safe_parse_response(response, username):
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        logger.info(f"Invalid JSON for {username}, trying to extract JSON block...")

        match = re.search(r'\{[\s\S]*?\}', response)
        if match:
            json_part = match.group(0).strip()

            
            if '"explanation":' in json_part and not json_part.endswith('"}'):
                if not json_part.endswith('"'):
                    json_part += '"'
                json_part += '}'

            try:
                return json.loads(json_part)
            except Exception as e2:
                logger.info(f"Failed to parse extracted JSON for {username}: {e2}")
                return {
                    "username": username,
                    "score": None,
                    "explanation": response[:300]  
                }
        else:
            return {
                "username": username,
                "score": None,
                "explanation": "No JSON found in response"
            }

def analyze_users_with_llm(grouped_users):
    results = []

    for username, titles in grouped_users.items():
        response = query_gemini(username, titles)

        if response:
            parsed = safe_parse_response(response, username)
            results.append({
                "username": parsed.get("username", username),
                "score": parsed.get("score"),
                "explanation": parsed.get("explanation", response)
            })
        else:
            logger.info(f"Empty response for user {username}")
            results.append({
                "username": username,
                "score": None,
                "explanation": "Rate Limit Exceeded"
            })

    return results

if __name__ == "__main__":

    grouped_users = {
        "alice": ["The world is changing", "Stop the media manipulation"],
        "bob": ["Jewish bankers run everything", "Woke nonsense again"],
    }

    results = analyze_users_with_llm(grouped_users)

    output_csv = "llm_results.csv"
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'score', 'explanation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in results:
            writer.writerow({
                "username": item.get("username", "Unknown"),
                "score": item.get("score", ""),
                "explanation": item.get("explanation", "")
            })

    logger.info(f"Saved LLM results to {output_csv}")

