import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from search_worker import search_and_collect

class TestSearchAndCollect(unittest.TestCase):
    def setUp(self):
        # Mock reddit object and subreddit.search method
        self.mock_reddit = MagicMock()
        self.mock_subreddit = self.mock_reddit.subreddit.return_value
    
    def create_mock_submission(self, **kwargs):
        # Helper to create a mock submission with attributes
        mock_submission = MagicMock()
        mock_submission.id = kwargs.get('id', 'abc123')
        mock_submission.subreddit = kwargs.get('subreddit', 'testsub')
        mock_submission.title = kwargs.get('title', 'Test Title')
        mock_submission.selftext = kwargs.get('selftext', 'Test selftext')
        mock_submission.author = kwargs.get('author', 'testauthor')
        mock_submission.created_utc = kwargs.get('created_utc', 1650000000)
        mock_submission.score = kwargs.get('score', 10)
        mock_submission.num_comments = kwargs.get('num_comments', 5)
        mock_submission.url = kwargs.get('url', 'http://test.url')
        return mock_submission

    def test_search_returns_results(self):
        # Setup mock search to return a list of mock submissions
        mock_submissions = [
            self.create_mock_submission(id='1'),
            self.create_mock_submission(id='2', author=None),  # author deleted
        ]
        self.mock_subreddit.search.return_value = mock_submissions

        results = search_and_collect(self.mock_reddit, 'testsub', 'testterm', limit=2)

        self.mock_reddit.subreddit.assert_called_once_with('testsub')
        self.mock_subreddit.search.assert_called_once_with('testterm', sort='new', limit=2)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], '1')
        self.assertEqual(results[0]['author'], 'testauthor')
        self.assertEqual(results[1]['author'], '[deleted]')
        self.assertEqual(results[1]['subreddit'], 'testsub')
        self.assertIn('created_utc', results[0])
    
    def test_search_handles_exception(self):
        # Simulate exception in reddit search
        self.mock_subreddit.search.side_effect = Exception("API error")

        results = search_and_collect(self.mock_reddit, 'testsub', 'testterm')

        self.assertEqual(results, [])  # should return empty list on error
    
    def test_search_with_default_limit(self):
        # Test that default limit of 20 is used if not specified
        mock_submissions = [self.create_mock_submission(id=str(i)) for i in range(3)]
        self.mock_subreddit.search.return_value = mock_submissions
        
        results = search_and_collect(self.mock_reddit, 'testsub', 'testterm')
        
        self.mock_subreddit.search.assert_called_once_with('testterm', sort='new', limit=20)
        self.assertEqual(len(results), 3)

if __name__ == '__main__':
    unittest.main()
