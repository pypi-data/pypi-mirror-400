"""Comprehensive tests for Configuration system."""

import os
from pathlib import Path

import pytest

from indusagi import AgentConfig

# Note: Config and LLMConfig classes no longer exist
# AgentConfig is the replacement configuration class


class TestConfig:
    """Test suite for Config class."""

    def test_config_defaults(self):
        """Test that Config has correct default values."""
        config = Config()

        assert config.default_model == "gpt-4"
        assert config.default_temperature == 0.7
        assert config.max_tokens is None
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.enable_history is True
        assert config.max_history_length == 100

    def test_config_custom_values(self):
        """Test Config with custom values."""
        config = Config(
            openai_api_key="custom-key",
            default_model="gpt-3.5-turbo",
            default_temperature=0.5,
            max_tokens=2000,
            log_level="DEBUG",
            enable_history=False,
            max_history_length=50,
        )

        assert config.openai_api_key == "custom-key"
        assert config.default_model == "gpt-3.5-turbo"
        assert config.default_temperature == 0.5
        assert config.max_tokens == 2000
        assert config.log_level == "DEBUG"
        assert config.enable_history is False
        assert config.max_history_length == 50

    def test_config_api_key_validation(self):
        """Test API key validation."""
        # No API key
        config1 = Config()
        assert config1.validate_api_key() is False

        # Empty API key
        config2 = Config(openai_api_key="")
        assert config2.validate_api_key() is False

        # Valid API key
        config3 = Config(openai_api_key="sk-test123")
        assert config3.validate_api_key() is True

    def test_config_temperature_validation(self):
        """Test temperature validation."""
        # Valid temperatures
        config1 = Config(default_temperature=0.0)
        assert config1.default_temperature == 0.0

        config2 = Config(default_temperature=2.0)
        assert config2.default_temperature == 2.0

        config3 = Config(default_temperature=0.7)
        assert config3.default_temperature == 0.7

        # Invalid temperatures should raise error
        with pytest.raises(Exception):
            Config(default_temperature=-0.1)

        with pytest.raises(Exception):
            Config(default_temperature=2.1)

    def test_config_from_env(self, mock_api_key):
        """Test loading config from environment variables."""
        config = Config()

        # API key from environment
        assert config.openai_api_key == "test-key-123456789"

    def test_config_load_method(self):
        """Test Config.load() class method."""
        config = Config.load()

        assert isinstance(config, Config)
        assert config.default_model == "gpt-4"

    def test_config_organization_id(self):
        """Test OpenAI organization ID configuration."""
        config = Config(openai_org_id="org-123456")

        assert config.openai_org_id == "org-123456"

    def test_config_log_file_path(self, tmp_path):
        """Test log file path configuration."""
        log_file = tmp_path / "test.log"

        config = Config(log_file=log_file)

        assert config.log_file == log_file
        assert isinstance(config.log_file, Path)

    def test_config_extra_fields_allowed(self):
        """Test that Config allows extra fields."""
        # Config is set with extra="allow"
        config = Config(custom_field="custom_value")

        assert hasattr(config, "custom_field")


class TestLLMConfig:
    """Test suite for LLMConfig class."""

    def test_llm_config_defaults(self):
        """Test LLMConfig default values."""
        config = LLMConfig()

        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0
        assert config.stop is None

    def test_llm_config_custom_values(self):
        """Test LLMConfig with custom values."""
        config = LLMConfig(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=1000,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.3,
            stop=["STOP", "END"],
        )

        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.5
        assert config.presence_penalty == 0.3
        assert config.stop == ["STOP", "END"]

    def test_llm_config_temperature_validation(self):
        """Test temperature validation for LLMConfig."""
        # Valid
        config1 = LLMConfig(temperature=0.0)
        assert config1.temperature == 0.0

        config2 = LLMConfig(temperature=2.0)
        assert config2.temperature == 2.0

        # Invalid
        with pytest.raises(Exception):
            LLMConfig(temperature=-0.1)

        with pytest.raises(Exception):
            LLMConfig(temperature=2.1)

    def test_llm_config_top_p_validation(self):
        """Test top_p validation."""
        # Valid
        config1 = LLMConfig(top_p=0.0)
        assert config1.top_p == 0.0

        config2 = LLMConfig(top_p=1.0)
        assert config2.top_p == 1.0

        # Invalid
        with pytest.raises(Exception):
            LLMConfig(top_p=-0.1)

        with pytest.raises(Exception):
            LLMConfig(top_p=1.1)

    def test_llm_config_frequency_penalty_validation(self):
        """Test frequency_penalty validation."""
        # Valid
        config1 = LLMConfig(frequency_penalty=-2.0)
        assert config1.frequency_penalty == -2.0

        config2 = LLMConfig(frequency_penalty=2.0)
        assert config2.frequency_penalty == 2.0

        # Invalid
        with pytest.raises(Exception):
            LLMConfig(frequency_penalty=-2.1)

        with pytest.raises(Exception):
            LLMConfig(frequency_penalty=2.1)

    def test_llm_config_presence_penalty_validation(self):
        """Test presence_penalty validation."""
        # Valid
        config1 = LLMConfig(presence_penalty=-2.0)
        assert config1.presence_penalty == -2.0

        config2 = LLMConfig(presence_penalty=2.0)
        assert config2.presence_penalty == 2.0

        # Invalid
        with pytest.raises(Exception):
            LLMConfig(presence_penalty=-2.1)

        with pytest.raises(Exception):
            LLMConfig(presence_penalty=2.1)

    def test_llm_config_stop_sequences(self):
        """Test stop sequences configuration."""
        # Single stop sequence
        config1 = LLMConfig(stop=["STOP"])
        assert config1.stop == ["STOP"]

        # Multiple stop sequences
        config2 = LLMConfig(stop=["STOP", "END", "DONE"])
        assert len(config2.stop) == 3

        # No stop sequences
        config3 = LLMConfig()
        assert config3.stop is None


class TestConfigEnvironment:
    """Test suite for environment variable handling."""

    def test_config_from_env_file(self, tmp_path, monkeypatch):
        """Test loading config from .env file."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text(
            """
OPENAI_API_KEY=test-key-from-file
DEFAULT_MODEL=gpt-3.5-turbo
DEFAULT_TEMPERATURE=0.5
"""
        )

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Load config
        config = Config()

        # Should load from .env file
        assert config.default_model == "gpt-3.5-turbo"

    def test_config_env_precedence(self, monkeypatch):
        """Test that environment variables take precedence."""
        # Set environment variable
        monkeypatch.setenv("OPENAI_API_KEY", "env-key")

        config = Config(openai_api_key="code-key")

        # Code value should take precedence over environment
        assert config.openai_api_key == "code-key"

    def test_config_missing_env_file(self):
        """Test config works without .env file."""
        # Should not raise an error
        config = Config()

        assert isinstance(config, Config)

    def test_config_case_insensitive_env(self, monkeypatch):
        """Test that environment variable names are case insensitive."""
        monkeypatch.setenv("openai_api_key", "test-key")

        config = Config()

        assert config.openai_api_key == "test-key"


class TestConfigEdgeCases:
    """Test suite for config edge cases."""

    def test_config_empty_string_api_key(self):
        """Test config with empty string API key."""
        config = Config(openai_api_key="")

        assert config.validate_api_key() is False

    def test_config_none_api_key(self):
        """Test config with None API key."""
        config = Config(openai_api_key=None)

        assert config.validate_api_key() is False

    def test_config_whitespace_api_key(self):
        """Test config with whitespace API key."""
        config = Config(openai_api_key="   ")

        # Whitespace is still a string, so technically valid but probably not useful
        assert config.openai_api_key == "   "

    def test_config_zero_max_tokens(self):
        """Test config with max_tokens set to zero."""
        config = Config(max_tokens=0)

        assert config.max_tokens == 0

    def test_config_negative_max_tokens(self):
        """Test config with negative max_tokens."""
        # Should be allowed (validation happens at API level)
        config = Config(max_tokens=-1)

        assert config.max_tokens == -1

    def test_config_very_large_max_tokens(self):
        """Test config with very large max_tokens."""
        config = Config(max_tokens=1000000)

        assert config.max_tokens == 1000000

    def test_config_zero_max_history_length(self):
        """Test config with zero max_history_length."""
        config = Config(max_history_length=0)

        assert config.max_history_length == 0

    def test_config_negative_max_history_length(self):
        """Test config with negative max_history_length."""
        config = Config(max_history_length=-1)

        assert config.max_history_length == -1

    def test_llm_config_empty_stop_list(self):
        """Test LLMConfig with empty stop list."""
        config = LLMConfig(stop=[])

        assert config.stop == []

    def test_llm_config_duplicate_stop_sequences(self):
        """Test LLMConfig with duplicate stop sequences."""
        config = LLMConfig(stop=["STOP", "STOP", "END"])

        assert config.stop == ["STOP", "STOP", "END"]


class TestConfigSerialization:
    """Test suite for config serialization."""

    def test_config_to_dict(self):
        """Test converting Config to dictionary."""
        config = Config(
            openai_api_key="test-key",
            default_model="gpt-4",
            default_temperature=0.7,
        )

        config_dict = config.model_dump()

        assert config_dict["openai_api_key"] == "test-key"
        assert config_dict["default_model"] == "gpt-4"
        assert config_dict["default_temperature"] == 0.7

    def test_llm_config_to_dict(self):
        """Test converting LLMConfig to dictionary."""
        config = LLMConfig(
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
        )

        config_dict = config.model_dump()

        assert config_dict["model"] == "gpt-4"
        assert config_dict["temperature"] == 0.7
        assert config_dict["max_tokens"] == 1000

    def test_config_from_dict(self):
        """Test creating Config from dictionary."""
        config_dict = {
            "openai_api_key": "test-key",
            "default_model": "gpt-4",
            "default_temperature": 0.7,
        }

        config = Config(**config_dict)

        assert config.openai_api_key == "test-key"
        assert config.default_model == "gpt-4"
        assert config.default_temperature == 0.7

    def test_llm_config_from_dict(self):
        """Test creating LLMConfig from dictionary."""
        config_dict = {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        config = LLMConfig(**config_dict)

        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000


class TestConfigIntegration:
    """Integration tests for configuration."""

    @pytest.mark.integration
    def test_config_with_agent(self, sample_config):
        """Test using Config with Agent."""
        from indusagi.core.agent import Agent
        from indusagi.agent.base import AgentConfig

        agent_config = AgentConfig(
            model=sample_config.default_model,
            temperature=sample_config.default_temperature,
            max_tokens=sample_config.max_tokens,
        )

        agent = Agent(agent_config)

        assert agent.config.model == sample_config.default_model
        assert agent.config.temperature == sample_config.default_temperature

    @pytest.mark.integration
    def test_config_lifecycle(self):
        """Test complete config lifecycle."""
        # Create config
        config = Config(
            openai_api_key="test-key",
            default_model="gpt-4",
            enable_history=True,
        )

        # Validate
        assert config.validate_api_key() is True

        # Convert to dict
        config_dict = config.model_dump()
        assert config_dict["openai_api_key"] == "test-key"

        # Create new config from dict
        new_config = Config(**config_dict)
        assert new_config.openai_api_key == "test-key"

    @pytest.mark.integration
    def test_config_and_llm_config_together(self):
        """Test using Config and LLMConfig together."""
        config = Config(
            openai_api_key="test-key",
            default_model="gpt-4",
            default_temperature=0.7,
        )

        llm_config = LLMConfig(
            model=config.default_model,
            temperature=config.default_temperature,
            max_tokens=config.max_tokens,
        )

        assert llm_config.model == config.default_model
        assert llm_config.temperature == config.default_temperature

    @pytest.mark.integration
    def test_config_environment_override(self, monkeypatch):
        """Test environment variable override behavior."""
        # Set environment
        monkeypatch.setenv("OPENAI_API_KEY", "env-key")
        monkeypatch.setenv("DEFAULT_MODEL", "gpt-3.5-turbo")

        # Create config
        config = Config()

        # Environment values should be used
        assert config.openai_api_key == "env-key"
        assert config.default_model == "gpt-3.5-turbo"

        # Override with code
        config2 = Config(openai_api_key="code-key")
        assert config2.openai_api_key == "code-key"
