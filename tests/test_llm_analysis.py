import unittest
from unittest.mock import patch, MagicMock
from llm_analysis import group_titles_by_user, query_gemini, analyze_users_with_llm

class TestLLMAnalysis(unittest.TestCase):

    def test_group_titles_by_user(self):
        enriched_list = [
            {'user_name': 'alice', 'title': 'Post A'},
            {'user_name': 'bob', 'title': 'Post B'},
            {'user_name': 'alice', 'title': 'Post C'},
            {'user_name': 'carol', 'title': None},  # ignored
            {'user_name': None, 'title': 'Post D'}  # ignored
        ]
        grouped = group_titles_by_user(enriched_list)
        self.assertEqual(set(grouped.keys()), {'alice', 'bob'})
        self.assertEqual(grouped['alice'], ['Post A', 'Post C'])
        self.assertEqual(grouped['bob'], ['Post B'])

    @patch('llm_analysis.requests.post')
    def test_query_gemini_success(self, mock_post):
        # Mock successful JSON response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": '{"username": "alice", "score": 2, "explanation": "Mild risk"}'}]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        response_text = query_gemini("alice", ["Some title"])
        self.assertIn('"username": "alice"', response_text)
        self.assertIn('"score": 2', response_text)

    @patch('llm_analysis.requests.post')
    def test_query_gemini_failure(self, mock_post):
        # Simulate HTTP error
        mock_post.side_effect = Exception("API error")
        response_text = query_gemini("bob", ["Some title"])
        self.assertIsNone(response_text)

    @patch('llm_analysis.query_gemini')
    def test_analyze_users_with_llm_valid_json(self, mock_query):
        # query_gemini returns valid JSON string
        mock_query.side_effect = [
            '{"username": "alice", "score": 2, "explanation": "Text"}',
            '{"username": "bob", "score": 5, "explanation": "Text"}'
        ]
        grouped = {'alice': ['Title1'], 'bob': ['Title2']}
        results = analyze_users_with_llm(grouped, max_workers=2)
        self.assertEqual(len(results), 2)
        usernames = set(item['username'] for item in results)
        self.assertEqual(usernames, {'alice', 'bob'})
        self.assertIn('score', results[0])
        self.assertIn('explanation', results[0])

    @patch('llm_analysis.query_gemini')
    def test_analyze_users_with_llm_invalid_json_extractable(self, mock_query):
        # query_gemini returns messy text containing JSON
        mock_query.return_value = 'Some intro... {"username": "carol", "score": 7, "explanation": "Risky"} ...footer'
        grouped = {'carol': ['Title']}
        results = analyze_users_with_llm(grouped, max_workers=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], 'carol')
        self.assertEqual(results[0]['score'], 7)

    @patch('llm_analysis.query_gemini')
    def test_analyze_users_with_llm_empty_response(self, mock_query):
        mock_query.return_value = None  # simulates failed API call
        grouped = {'dave': ['Title']}
        results = analyze_users_with_llm(grouped, max_workers=1)
        self.assertEqual(len(results), 1)
        self.assertIsNone(results[0]['username'])
        self.assertEqual(results[0]['explanation'], 'Empty response')

if __name__ == '__main__':
    unittest.main()
