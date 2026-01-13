"""
Tests for auth module
"""
import hmac
import hashlib
import time
from unittest.mock import patch

import pytest

from data_agent_tunnel_client.auth import generate_signature, create_auth_params


class TestGenerateSignature:
    """Tests for generate_signature function"""

    def test_generates_hmac_sha256_signature(self):
        """Should generate valid HMAC-SHA256 signature"""
        secret_key = "test-secret"
        timestamp = "1234567890"

        result = generate_signature(secret_key, timestamp)

        # Verify it's a valid hex string
        assert len(result) == 64  # SHA256 produces 64 hex characters
        assert all(c in "0123456789abcdef" for c in result)

    def test_signature_matches_expected_hmac(self):
        """Should match manually computed HMAC-SHA256"""
        secret_key = "my-secret-key"
        timestamp = "1609459200"

        expected = hmac.new(
            secret_key.encode(),
            timestamp.encode(),
            hashlib.sha256
        ).hexdigest()

        result = generate_signature(secret_key, timestamp)

        assert result == expected

    def test_different_keys_produce_different_signatures(self):
        """Different secret keys should produce different signatures"""
        timestamp = "1234567890"

        sig1 = generate_signature("key1", timestamp)
        sig2 = generate_signature("key2", timestamp)

        assert sig1 != sig2

    def test_different_timestamps_produce_different_signatures(self):
        """Different timestamps should produce different signatures"""
        secret_key = "test-key"

        sig1 = generate_signature(secret_key, "1234567890")
        sig2 = generate_signature(secret_key, "1234567891")

        assert sig1 != sig2

    def test_same_inputs_produce_same_signature(self):
        """Same inputs should always produce same signature"""
        secret_key = "test-key"
        timestamp = "1234567890"

        sig1 = generate_signature(secret_key, timestamp)
        sig2 = generate_signature(secret_key, timestamp)

        assert sig1 == sig2

    def test_empty_secret_key(self):
        """Empty secret key should still produce valid signature"""
        result = generate_signature("", "1234567890")

        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_unicode_secret_key(self):
        """Unicode characters in secret key should work"""
        result = generate_signature("密钥测试", "1234567890")

        assert len(result) == 64


class TestCreateAuthParams:
    """Tests for create_auth_params function"""

    def test_returns_dict_with_timestamp_and_signature(self):
        """Should return dict with timestamp and signature keys"""
        result = create_auth_params("test-secret")

        assert "timestamp" in result
        assert "signature" in result

    def test_timestamp_is_current_time(self):
        """Timestamp should be close to current time"""
        before = int(time.time())
        result = create_auth_params("test-secret")
        after = int(time.time())

        timestamp = int(result["timestamp"])

        assert before <= timestamp <= after

    def test_signature_matches_generated_signature(self):
        """Signature should match generate_signature output"""
        secret_key = "test-secret"

        with patch("data_agent_tunnel_client.auth.time") as mock_time:
            mock_time.time.return_value = 1609459200.123
            result = create_auth_params(secret_key)

        expected_sig = generate_signature(secret_key, "1609459200")

        assert result["signature"] == expected_sig

    def test_empty_secret_key_returns_empty_signature(self):
        """Empty secret key should return empty signature string"""
        result = create_auth_params("")

        assert result["signature"] == ""
        assert result["timestamp"] != ""

    def test_no_secret_key_returns_empty_signature(self):
        """No secret key (default) should return empty signature"""
        result = create_auth_params()

        assert result["signature"] == ""

    def test_timestamp_is_string(self):
        """Timestamp should be a string"""
        result = create_auth_params("test")

        assert isinstance(result["timestamp"], str)

    def test_signature_is_string(self):
        """Signature should be a string"""
        result = create_auth_params("test")

        assert isinstance(result["signature"], str)
