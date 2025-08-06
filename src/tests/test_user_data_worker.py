import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from search_worker import search_and_collect

class TestSearchWorker(unittest.TestCase):

    def setUp(self):
        # Mock submission object
        self.mock_submission = MagicMock()
        self.mock_submission.id = 'abc123'
        self.mock_submission.subreddit = 'testsub'
        self.mock_submission.title = 'Test Title'
        self.mock_submission.selftext = 'Test content'
        self.mock_submission.author = 'test_author'
        self.mock_submission.created_utc = 1620000000
        self.mock_submission.score = 100
        self.mock_submission.num_comments = 42
        self.mock_submission.url = 'http://example.com'

        # Expected result structure
        self.expected_result = [{
            'id': 'abc123',
            'subreddit': 'testsub',
            'title': 'Test Title',
            'selftext': 'Test content',
            'author': 'test_author',
            'created_utc': datetime.utcfromtimestamp(1620000000).isoformat(),
            'score': 100,
            'num_comments': 42,
            'url': 'http://example.com'
        }]

    def test_search_success(self):
        # Mock reddit API
        mock_reddit = MagicMock()
        mock_reddit.subreddit.return_value.search.return_value = [self.mock_submission]

        result = search_and_collect(mock_reddit, 'testsub', 'test_term', limit=1)
        self.assertEqual(result, self.expected_result)

    def test_deleted_author(self):
        self.mock_submission.author = None
        self.expected_result[0]['author'] = '[deleted]'

        mock_reddit = MagicMock()
        mock_reddit.subreddit.return_value.search.return_value = [self.mock_submission]

        result = search_and_collect(mock_reddit, 'testsub', 'test_term', limit=1)
        self.assertEqual(result, self.expected_result)

    @patch('search_worker.logger')
    def test_search_exception(self, mock_logger):
        mock_reddit = MagicMock()
        mock_reddit.subreddit.side_effect = Exception("API Error")

        result = search_and_collect(mock_reddit, 'testsub', 'test_term')
        self.assertEqual(result, [])
        mock_logger.info.assert_called_with("Error searching 'test_term' in r/testsub: API Error")

if __name__ == '__main__':
    unittest.main()
