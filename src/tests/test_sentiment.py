import unittest
import tempfile
import pandas as pd
from sentiment_analysis import analyze_sentiment

class TestAnalyzeSentiment(unittest.TestCase):

    def setUp(self):
        # Create a temporary CSV file with sample titles
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w+', newline='', suffix='.csv', delete=False)
        df = pd.DataFrame({
            'title': [
                'I love this product!',
                'This is terrible.',
                'Meh, it’s okay I guess.'
            ]
        })
        df.to_csv(self.temp_csv.name, index=False)
        self.temp_csv.flush()

    def tearDown(self):
        # Clean up temporary file
        self.temp_csv.close()

    def test_analyze_sentiment_output_columns(self):
        df_result = analyze_sentiment(self.temp_csv.name)
        
        # Check required columns exist
        expected_columns = {'title', 'compound', 'pos', 'neu', 'neg', 'statement'}
        self.assertTrue(expected_columns.issubset(df_result.columns))
    
    def test_sentiment_classification(self):
        df_result = analyze_sentiment(self.temp_csv.name)
        
        # Check statements based on thresholds
        # "I love this product!" should be Non-problematic
        self.assertIn('Non-problematic', df_result['statement'].values)
        # "This is terrible." should be Problematic
        self.assertIn('Problematic', df_result['statement'].values)
        # "Meh, it’s okay I guess." is likely Neutral
        self.assertIn('Neutral', df_result['statement'].values)

    def test_result_length_matches_input(self):
        df_result = analyze_sentiment(self.temp_csv.name)
        original_df = pd.read_csv(self.temp_csv.name)
        
        # Number of rows should match
        self.assertEqual(len(df_result), len(original_df))

if __name__ == '__main__':
    unittest.main()
