#!/usr/bin/env python
"""
Testes de autenticação e headers da API GitHub.
"""

import os


def test_get_github_headers_uses_bearer(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_testtoken123")

    from config.settings import Settings

    headers = Settings.get_github_headers()

    assert headers["Authorization"] == "Bearer ghp_testtoken123"
    assert headers["Accept"] == "application/vnd.github.v3+json"
    assert "User-Agent" in headers


def test_github_api_client_includes_authorization_header(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_testtoken456")

    import infrastructure.github_api as github_api

    captured = {}

    def fake_request(method, url, params, headers, timeout, **kwargs):
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers

        class DummyResponse:
            status_code = 200
            headers = {}
            text = '{"items": [{"full_name": "repo/example", "stargazers_count": 123, "forks_count": 10, "description": "Example repo", "html_url": "https://github.com/repo/example", "updated_at": "2026-05-03T00:00:00Z"}]}'

            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "items": [
                        {
                            "full_name": "repo/example",
                            "stargazers_count": 123,
                            "forks_count": 10,
                            "description": "Example repo",
                            "html_url": "https://github.com/repo/example",
                            "updated_at": "2026-05-03T00:00:00Z"
                        }
                    ]
                }

        return DummyResponse()

    # Mock the session request method
    client = github_api.GitHubApiClient("ghp_testtoken456")
    monkeypatch.setattr(client.session, "request", fake_request)

    repos = client.fetch_repos(query="language:python", page=1, per_page=1)

    assert repos["status"] == "success"
    assert repos["data"]["items"][0]["full_name"] == "repo/example"
    assert captured["headers"]["Authorization"] == "token ghp_testtoken456"
    assert captured["params"]["page"] == 1


def test_fetch_multiple_pages_limits_pages(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_testtoken789")

    import infrastructure.github_api as github_api

    call_pages = []

    def fake_request(method, url, params, headers, timeout, **kwargs):
        call_pages.append(params["page"])

        class DummyResponse:
            status_code = 200
            headers = {}
            text = '{"items": [{"full_name": "repo/test", "stargazers_count": 1}]}'  # Return 1 item to continue pagination

            def raise_for_status(self):
                return None

            def json(self):
                return {"items": [{"full_name": "repo/test", "stargazers_count": 1}]}

        return DummyResponse()

    # Mock the session request method
    client = github_api.GitHubApiClient("ghp_testtoken789")
    monkeypatch.setattr(client.session, "request", fake_request)

    result = client.fetch_multiple_pages(query="language:python", max_pages=10, per_page=1)

    assert result["status"] == "success"
    assert result["total_pages_fetched"] == 10  # Should fetch all pages since we return empty items
    assert call_pages == list(range(1, 11))  # pages 1-10
