# sentiment_analysis.py
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import nltk

def analyze_sentiment(csv_file):
    nltk.download('vader_lexicon')
    
    df = pd.read_csv(csv_file)
    titles = df['title']
    
    sia = SIA()
    results = []
    
    for line in titles:
        pol_score = sia.polarity_scores(line)
        pol_score['title'] = line
        results.append(pol_score)
    
    df_results = pd.DataFrame(results)
    
    # Add statement column based on thresholds
    df_results['statement'] = 'Neutral'
    df_results.loc[df_results['compound'] > 0.2, 'statement'] = 'Non-problematic'
    df_results.loc[df_results['compound'] < -0.2, 'statement'] = 'Problematic'
    
    # Combine with original dataframe
    df_final = pd.concat(
        [df.reset_index(drop=True), df_results[['compound', 'pos', 'neu', 'neg', 'statement']].reset_index(drop=True)],
        axis=1
    )
    
    return df_final
