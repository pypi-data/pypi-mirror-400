"""Tests for authentication classes."""

import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

import httpx

from producthunt_sdk import BearerAuth, OAuth2, TokenCache


class TestBearerAuth:
    """Tests for BearerAuth."""

    def test_adds_authorization_header(self):
        """BearerAuth adds Bearer token to request headers."""
        import httpx

        auth = BearerAuth("test_token_123")
        request = httpx.Request("GET", "https://api.example.com")

        # Run auth flow
        flow = auth.auth_flow(request)
        modified_request = next(flow)

        assert modified_request.headers["Authorization"] == "Bearer test_token_123"


class TestTokenCache:
    """Tests for TokenCache."""

    def test_get_set(self):
        """TokenCache stores and retrieves tokens."""
        cache = TokenCache()
        cache.set("key1", "token1")
        cache.set("key2", "token2")

        assert cache.get("key1") == "token1"
        assert cache.get("key2") == "token2"
        assert cache.get("nonexistent") is None

    def test_clear_specific_key(self):
        """TokenCache.clear(key) removes only that key."""
        cache = TokenCache()
        cache.set("key1", "token1")
        cache.set("key2", "token2")

        cache.clear("key1")

        assert cache.get("key1") is None
        assert cache.get("key2") == "token2"

    def test_clear_all(self):
        """TokenCache.clear() removes all tokens."""
        cache = TokenCache()
        cache.set("key1", "token1")
        cache.set("key2", "token2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_thread_safe(self):
        """TokenCache is thread-safe for concurrent access."""
        cache = TokenCache()
        results = []

        def writer(key, value):
            for _ in range(100):
                cache.set(key, value)
                time.sleep(0.001)

        def reader(key):
            for _ in range(100):
                results.append(cache.get(key))
                time.sleep(0.001)

        threads = [
            threading.Thread(target=writer, args=("k1", "v1")),
            threading.Thread(target=writer, args=("k1", "v2")),
            threading.Thread(target=reader, args=("k1",)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No exceptions = thread-safe
        # Values should be either None, "v1", or "v2"
        assert all(r in (None, "v1", "v2") for r in results)


class TestOAuth2:
    """Tests for OAuth2."""

    def test_cache_key_based_on_credentials(self):
        """Different credentials produce different cache keys."""
        auth1 = OAuth2(client_id="id1", client_secret="secret1")
        auth2 = OAuth2(client_id="id2", client_secret="secret2")
        auth3 = OAuth2(client_id="id1", client_secret="secret1")

        assert auth1._cache_key != auth2._cache_key
        assert auth1._cache_key == auth3._cache_key  # Same credentials = same key

    def test_cache_key_includes_scope(self):
        """Different scopes produce different cache keys."""
        auth1 = OAuth2(client_id="id", client_secret="secret", scope="public")
        auth2 = OAuth2(client_id="id", client_secret="secret", scope="public private")

        assert auth1._cache_key != auth2._cache_key

    def test_uses_cached_token(self):
        """OAuth2 returns cached token without running OAuth flow."""
        # Pre-cache a token
        auth = OAuth2(client_id="test", client_secret="test")
        OAuth2.token_cache.set(auth._cache_key, "cached_token")

        try:
            with patch.object(OAuth2, "_run_oauth_flow") as mock_flow:
                token = auth._ensure_token()

                assert token == "cached_token"
                mock_flow.assert_not_called()
        finally:
            OAuth2.token_cache.clear()

    def test_clear_token(self):
        """clear_token() removes token from cache."""
        auth = OAuth2(client_id="test", client_secret="test")
        OAuth2.token_cache.set(auth._cache_key, "test_token")

        auth.clear_token()

        assert OAuth2.token_cache.get(auth._cache_key) is None

    def test_thread_safety_single_oauth_flow(self):
        """Only one OAuth flow runs even with multiple concurrent threads."""
        flow_call_count = 0
        flow_call_lock = threading.Lock()

        def mock_oauth_flow(self):
            nonlocal flow_call_count
            with flow_call_lock:
                flow_call_count += 1

            # Simulate browser/callback delay
            time.sleep(0.1)

            # Cache the token (like the real method does)
            token = "mock_token_12345"
            self._cache_token(token)
            return token

        # Clear any cached tokens
        OAuth2.token_cache.clear()

        try:
            with patch.object(OAuth2, "_run_oauth_flow", mock_oauth_flow):
                results = {}
                errors = {}

                def worker(name):
                    try:
                        auth = OAuth2(client_id="test_id", client_secret="test_secret")
                        token = auth._ensure_token()
                        results[name] = token
                    except Exception as e:
                        errors[name] = str(e)

                # Start 5 threads simultaneously
                threads = []
                for i in range(5):
                    t = threading.Thread(target=worker, args=(f"T{i+1}",))
                    threads.append(t)

                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

                # Verify results
                assert flow_call_count == 1, f"OAuth flow ran {flow_call_count} times, expected 1"
                assert len(results) == 5, f"Only {len(results)} threads completed"
                assert len(errors) == 0, f"Errors occurred: {errors}"
                assert all(t == "mock_token_12345" for t in results.values())
        finally:
            OAuth2.token_cache.clear()

    def test_different_credentials_separate_flows(self):
        """Different credentials run separate OAuth flows."""
        flow_calls = []
        flow_call_lock = threading.Lock()

        def mock_oauth_flow(self):
            with flow_call_lock:
                flow_calls.append(self._cache_key)

            time.sleep(0.05)
            token = f"token_for_{self._cache_key}"
            self._cache_token(token)
            return token

        OAuth2.token_cache.clear()

        try:
            with patch.object(OAuth2, "_run_oauth_flow", mock_oauth_flow):
                results = {}

                def worker(client_id):
                    auth = OAuth2(client_id=client_id, client_secret="secret")
                    token = auth._ensure_token()
                    results[client_id] = token

                threads = [
                    threading.Thread(target=worker, args=("client_a",)),
                    threading.Thread(target=worker, args=("client_b",)),
                ]

                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

                # Each unique credential set should have its own flow
                assert len(flow_calls) == 2
                assert len(set(flow_calls)) == 2  # Different cache keys
        finally:
            OAuth2.token_cache.clear()


class TestTokenCacheFilePersistence:
    """Tests for TokenCache file persistence."""

    def test_saves_to_file(self):
        """TokenCache saves tokens to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tokens.json"
            cache = TokenCache(file_path)

            cache.set("key1", "token1")

            assert file_path.exists()
            # Create new cache instance to verify persistence
            cache2 = TokenCache(file_path)
            assert cache2.get("key1") == "token1"

    def test_loads_from_existing_file(self):
        """TokenCache loads tokens from existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tokens.json"
            # Write directly to file
            file_path.write_text('{"key1": "token1"}')

            cache = TokenCache(file_path)

            assert cache.get("key1") == "token1"

    def test_handles_corrupted_file(self):
        """TokenCache handles corrupted JSON gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "tokens.json"
            file_path.write_text("not valid json")

            cache = TokenCache(file_path)

            # Should not raise, just have empty cache
            assert cache.get("key1") is None

    def test_creates_parent_directories(self):
        """TokenCache creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "subdir" / "nested" / "tokens.json"
            cache = TokenCache(file_path)

            cache.set("key1", "token1")

            assert file_path.exists()


class TestBearerAuthEdgeCases:
    """Edge case tests for BearerAuth."""

    def test_empty_token_raises(self):
        """BearerAuth raises ValueError for empty token."""
        import pytest

        with pytest.raises(ValueError, match="Token cannot be None or empty"):
            BearerAuth("")

    def test_none_token_raises(self):
        """BearerAuth raises ValueError for None token."""
        import pytest

        with pytest.raises(ValueError, match="Token cannot be None or empty"):
            BearerAuth(None)

    def test_token_with_special_characters(self):
        """BearerAuth handles tokens with special characters."""
        auth = BearerAuth("token_with-special.chars_123")
        request = httpx.Request("GET", "https://api.example.com")

        flow = auth.auth_flow(request)
        modified_request = next(flow)

        assert modified_request.headers["Authorization"] == "Bearer token_with-special.chars_123"
