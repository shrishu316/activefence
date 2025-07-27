
---

# Reddit Anti-Semitism Analysis Project

This project collects Reddit posts from targeted subreddits containing potentially sensitive or problematic terms, performs sentiment analysis, collects detailed user activity, and uses a Large Language Model (LLM) to score users for anti-Semitic behavior.

---

## Features

* **Reddit Data Collection:** Searches recent posts in specific subreddits for defined keywords.
* **Sentiment Analysis:** Uses NLTK's VADER sentiment analyzer to classify posts as *Problematic*, *Non-problematic*, or *Neutral* based on post titles.
* **User Activity Aggregation:** Collects recent submissions and comments by users flagged for problematic content.
* **LLM-based Behavior Scoring:** Sends user post titles to a Google Gemini-powered LLM to score the likelihood of anti-Semitic behavior.
* **CSV Export:** Saves all collected and processed data with timestamped filenames for audit and further analysis.

---

## Project Structure

* `config.py`
  Configuration constants including Reddit API credentials, Google API key, target subreddits, search terms, and data lookback period.

* `reddit_client.py`
  Initializes the PRAW Reddit client with provided credentials.

* `search_worker.py`
  Searches Reddit posts for specific terms within target subreddits.

* `user_data_worker.py`
  Collects user submissions and comments for a given timeframe, using concurrent threads for efficiency.

* `sentiment_analysis.py`
  Performs sentiment analysis on post titles using VADER, classifying the sentiment into three categories.

* `llm_analysis.py`
  Groups user post titles and queries the Gemini LLM for anti-Semitism scoring and explanations.

* `save_csv.py`
  Contains functions to save collected posts, user data, problematic posts, and LLM results into CSV files with timestamped filenames.

* `main.py`
  The orchestrator script executing the pipeline from Reddit data collection, sentiment analysis, user data aggregation, LLM analysis, and saving results.

---

## Setup and Requirements

1. **Python Version:**
   Tested with Python 3.8+.

Folder 'Shubham' is a virtual environment you can connect to it by below command.

```bash
source path/Shubham/bin/activate
```
if you are using python3 please 
run the below command 
```bash
export PYTHONPATH=/your/path/to main folder /python_assignment
```
pip install all the dependencies given in the requirements.txt file. 


2. **Dependencies:**
   Install required packages with:

   ```bash
   pip install praw pandas nltk requests
   ```

3. **NLTK Data:**
   The script downloads the VADER lexicon automatically, but you can manually download it with:

   ```python
   import nltk
   nltk.download('vader_lexicon')
   ```

4. **API Credentials:**

   * Obtain Reddit API credentials by creating an app on [Reddit's developer portal](https://www.reddit.com/prefs/apps).
   * Obtain a Google API key with access to the Gemini generative language model.
   * Place these credentials in the `config.py` file.

---

## Usage

Run the main script:

```bash
python main.py
```

This executes the following steps:

1. **Collect Reddit posts** from the configured subreddits for the defined search terms.
2. **Perform sentiment analysis** to identify problematic posts.
3. **Extract users** associated with problematic posts.
4. **Collect user submissions and comments** over the last 60 days (configurable).
5. **Query the Gemini LLM** to score each user for anti-Semitic behavior.
6. **Save all datasets** into timestamped CSV files for further review.

---

## Output Files

* `harmful_posts_YYYYMMDD_HHMMSS.csv` — All posts collected matching search criteria.
* `problematic_users_YYYYMMDD_HHMMSS.csv` — Posts classified as problematic.
* `user_data_last_2_months_YYYYMMDD_HHMMSS.csv` — User submission and comment data.
* `llm_analysis_results_YYYYMMDD_HHMMSS.csv` — Gemini LLM scores and explanations for each user.

---

## Notes and Considerations

* **Rate Limits:**
  The code uses thread pools with small delays to respect Reddit and Google API rate limits. Adjust `max_workers` and delays as needed.

* **Data Privacy:**
  Handle collected data responsibly and ensure compliance with Reddit’s terms of service and privacy policies.

* **Model Responses:**
  The LLM response parser handles malformed JSON, but occasional manual inspection may be necessary.

---

## Future Improvements

* Integrate more sophisticated NLP models or custom-trained classifiers.
* Add a database backend for scalable storage and querying.
* Build a dashboard for visualizing user behavior and flagged content.
* Implement real-time monitoring with alerting.

---


