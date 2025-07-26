import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pandas as pd
from user_data_worker import collect_user_data, collect_all_users_data

class TestUserDataWorker(unittest.TestCase):
    def setUp(self):
        # Fake user row
        self.user_row = pd.Series({'author': 'testuser', 'id': 'u123'})
        
        # Fixed date for created_utc so it’s always recent
        now = datetime.utcnow()
        self.recent_timestamp = (now - timedelta(days=1)).timestamp()
        
        # Mock reddit.redditor
        self.mock_reddit = MagicMock()
        self.mock_redditor = MagicMock()
        self.mock_reddit.redditor.return_value = self.mock_redditor
        
        # Force fetch works (mock link_karma)
        self.mock_redditor.link_karma = 100
        
        # Mock submissions
        mock_submission = MagicMock()
        mock_submission.created_utc = self.recent_timestamp
        mock_submission.subreddit = 'testsub'
        mock_submission.title = 'Test Submission'
        mock_submission.selftext = 'Submission text'
        mock_submission.score = 10
        mock_submission.num_comments = 2
        mock_submission.url = 'http://test.url'
        
        self.mock_redditor.submissions.new.return_value = [mock_submission]
        
        # Mock comments
        mock_comment = MagicMock()
        mock_comment.created_utc = self.recent_timestamp
        mock_comment.subreddit = 'testsub'
        mock_comment.body = 'Test comment'
        mock_comment.score = 3
        mock_comment.permalink = '/r/testsub/comments/1/test_comment'
        
        self.mock_redditor.comments.new.return_value = [mock_comment]

    def test_collect_user_data_success(self):
        results = collect_user_data(self.mock_reddit, self.user_row)
        
        # Should collect both submission and comment
        types = set(item['type'] for item in results)
        self.assertIn('submission', types)
        self.assertIn('comment', types)
        
        # Check fields
        for item in results:
            self.assertEqual(item['user_id'], 'u123')
            self.assertEqual(item['user_name'], 'testuser')
            self.assertTrue(item['created_utc'])  # should have timestamp

    def test_collect_user_data_handles_exception(self):
        # reddit.redditor() raises exception
        self.mock_reddit.redditor.side_effect = Exception("User not found")
        
        results = collect_user_data(self.mock_reddit, self.user_row)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'error')
        self.assertIn('User not found', results[0]['body_or_selftext'])

    def test_collect_all_users_data_combines_results(self):
        # Create users_df with two rows
        users_df = pd.DataFrame([
            {'author': 'testuser1', 'id': 'u1'},
            {'author': 'testuser2', 'id': 'u2'}
        ])
        
        # Patch collect_user_data to always return fake data
        with patch('user_data_worker.collect_user_data') as mock_collect:
            mock_collect.side_effect = [
                [{'user_id': 'u1', 'user_name': 'testuser1', 'type': 'submission', 'created_utc': '2024-07-26T00:00:00', 'subreddit': 'testsub', 'title': 'Title1', 'body_or_selftext': 'Text1', 'score': 1, 'num_comments': 0, 'url': 'url1'}],
                [{'user_id': 'u2', 'user_name': 'testuser2', 'type': 'comment', 'created_utc': '2024-07-26T00:00:00', 'subreddit': 'testsub', 'title': '', 'body_or_selftext': 'Comment2', 'score': 2, 'num_comments': None, 'url': 'url2'}]
            ]
            
            df_result = collect_all_users_data(self.mock_reddit, users_df)
            
            self.assertIsInstance(df_result, pd.DataFrame)
            self.assertEqual(len(df_result), 2)
            self.assertIn('user_id', df_result.columns)
            self.assertIn('type', df_result.columns)
            self.assertSetEqual(set(df_result['user_id']), {'u1', 'u2'})

if __name__ == '__main__':
    unittest.main()
