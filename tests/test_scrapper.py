import pytest
from src.search_worker import search_and_collect

def test_search_and_collect_returns_list(monkeypatch):
    class MockSubmission:
        id = "abc123"
        subreddit = "testsub"
        title = "fake title"
        selftext = "fake text"
        author = "testuser"
        created_utc = 1719820000
        score = 10
        num_comments = 2
        url = "http://example.com"

    class MockReddit:
        def subreddit(self, name):
            class Subreddit:
                def search(self, term, sort, limit):
                    return [MockSubmission()]
            return Subreddit()
    
    monkeypatch.setattr("search_worker.reddit", MockReddit())

    results = search_and_collect("testsub", "testterm", limit=1)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "fake title"
