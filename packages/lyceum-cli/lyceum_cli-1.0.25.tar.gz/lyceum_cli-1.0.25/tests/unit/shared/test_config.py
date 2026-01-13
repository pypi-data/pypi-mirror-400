"""Tests for authentication config."""

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import jwt
import pytest
from click.exceptions import Exit as ClickExit


class TestConfigLoad:
    """Tests for Config.load() method."""

    def test_load_existing_config(self, tmp_path):
        config_dir = tmp_path / ".lyceum"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_data = {
            "api_key": "test-api-key",
            "refresh_token": "test-refresh-token",
            "base_url": "https://api.test.dev",
        }
        config_file.write_text(json.dumps(config_data))

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()

            assert config.api_key == "test-api-key"
            assert config.refresh_token == "test-refresh-token"
            assert config.base_url == "https://api.test.dev"

    def test_load_missing_file(self, tmp_path):
        missing_path = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", missing_path):
            from lyceum.shared.config import Config

            config = Config()

            assert config.api_key is None
            assert config.refresh_token is None

    def test_load_partial_config(self, tmp_path):
        config_dir = tmp_path / ".lyceum"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_data = {"api_key": "only-api-key"}
        config_file.write_text(json.dumps(config_data))

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()

            assert config.api_key == "only-api-key"
            assert config.refresh_token is None

    def test_load_malformed_json(self, tmp_path):
        config_dir = tmp_path / ".lyceum"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_file.write_text("not valid json {{{")

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()
            # Should not crash, just use defaults
            assert config.api_key is None


class TestConfigSave:
    """Tests for Config.save() method."""

    def test_save_creates_directory(self, tmp_path):
        config_dir = tmp_path / ".lyceum"
        config_file = config_dir / "config.json"

        with (
            patch("lyceum.shared.config.CONFIG_DIR", config_dir),
            patch("lyceum.shared.config.CONFIG_FILE", config_file),
        ):
            from lyceum.shared.config import Config

            config = Config()
            config.api_key = "new-api-key"
            config.refresh_token = "new-refresh-token"
            config.save()

            assert config_dir.exists()
            assert config_file.exists()

            saved_data = json.loads(config_file.read_text())
            assert saved_data["api_key"] == "new-api-key"
            assert saved_data["refresh_token"] == "new-refresh-token"


class TestConfigIsTokenExpired:
    """Tests for Config.is_token_expired() method."""

    def test_valid_token_not_expired(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            # Create token expiring in 1 hour
            future_exp = int(time.time()) + 3600
            token = jwt.encode({"exp": future_exp}, "secret", algorithm="HS256")

            config = Config()
            config.api_key = token

            assert config.is_token_expired() is False

    def test_expired_token(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            # Create token that expired 1 hour ago
            past_exp = int(time.time()) - 3600
            token = jwt.encode({"exp": past_exp}, "secret", algorithm="HS256")

            config = Config()
            config.api_key = token

            assert config.is_token_expired() is True

    def test_grace_period(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            # Create token expiring in 3 minutes (within 5-min grace period)
            near_exp = int(time.time()) + 180
            token = jwt.encode({"exp": near_exp}, "secret", algorithm="HS256")

            config = Config()
            config.api_key = token

            assert config.is_token_expired() is True

    def test_legacy_api_key_never_expired(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()
            config.api_key = "lk_test_api_key_12345"

            assert config.is_token_expired() is False

    def test_missing_token(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()
            config.api_key = None

            assert config.is_token_expired() is True

    def test_invalid_jwt_token(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()
            config.api_key = "not-a-valid-jwt-token"

            # Invalid JWT should be treated as expired
            assert config.is_token_expired() is True


class TestConfigRefreshToken:
    """Tests for Config.refresh_access_token() method."""

    def test_refresh_success(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"
        config_dir = tmp_path / ".lyceum"

        with (
            patch("lyceum.shared.config.CONFIG_FILE", config_file),
            patch("lyceum.shared.config.CONFIG_DIR", config_dir),
            patch("lyceum.shared.config.create_client") as mock_create_client,
        ):
            mock_session = MagicMock()
            mock_session.access_token = "new-access-token"
            mock_session.refresh_token = "new-refresh-token"

            mock_response = MagicMock()
            mock_response.session = mock_session

            mock_auth = MagicMock()
            mock_auth.refresh_session.return_value = mock_response

            mock_client = MagicMock()
            mock_client.auth = mock_auth
            mock_create_client.return_value = mock_client

            from lyceum.shared.config import Config

            config = Config()
            config.refresh_token = "old-refresh-token"

            result = config.refresh_access_token()

            assert result is True
            assert config.api_key == "new-access-token"
            assert config.refresh_token == "new-refresh-token"

    def test_refresh_failure_no_session(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with (
            patch("lyceum.shared.config.CONFIG_FILE", config_file),
            patch("lyceum.shared.config.create_client") as mock_create_client,
        ):
            mock_response = MagicMock()
            mock_response.session = None

            mock_auth = MagicMock()
            mock_auth.refresh_session.return_value = mock_response

            mock_client = MagicMock()
            mock_client.auth = mock_auth
            mock_create_client.return_value = mock_client

            from lyceum.shared.config import Config

            config = Config()
            config.refresh_token = "invalid-token"

            result = config.refresh_access_token()

            assert result is False

    def test_refresh_failure_no_refresh_token(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()
            config.refresh_token = None

            result = config.refresh_access_token()

            assert result is False

    def test_refresh_skipped_for_legacy_key(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()
            config.api_key = "lk_test_api_key"
            config.refresh_token = "some-refresh-token"

            result = config.refresh_access_token()

            assert result is False

    def test_refresh_exception_handling(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with (
            patch("lyceum.shared.config.CONFIG_FILE", config_file),
            patch("lyceum.shared.config.create_client") as mock_create_client,
        ):
            mock_create_client.side_effect = Exception("Connection error")

            from lyceum.shared.config import Config

            config = Config()
            config.refresh_token = "some-token"

            result = config.refresh_access_token()

            assert result is False


class TestConfigGetClient:
    """Tests for Config.get_client() method."""

    def test_get_client_no_api_key(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            config = Config()
            config.api_key = None

            with pytest.raises(ClickExit):
                config.get_client()

    def test_get_client_expired_token_refresh_fails(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            # Create expired token
            past_exp = int(time.time()) - 3600
            token = jwt.encode({"exp": past_exp}, "secret", algorithm="HS256")

            config = Config()
            config.api_key = token
            config.refresh_token = None  # No refresh token

            with pytest.raises(ClickExit):
                config.get_client()

    def test_get_client_valid_token(self, tmp_path):
        config_file = tmp_path / ".lyceum" / "config.json"

        with patch("lyceum.shared.config.CONFIG_FILE", config_file):
            from lyceum.shared.config import Config

            # Create token expiring in 1 hour
            future_exp = int(time.time()) + 3600
            token = jwt.encode({"exp": future_exp}, "secret", algorithm="HS256")

            config = Config()
            config.api_key = token

            result = config.get_client()

            assert result is config
