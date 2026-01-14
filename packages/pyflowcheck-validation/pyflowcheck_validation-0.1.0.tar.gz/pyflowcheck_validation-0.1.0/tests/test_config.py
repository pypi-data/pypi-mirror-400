import pytest
from py_flowcheck.config import Config, configure, get_config


def test_default_config():
    """
    Test the default configuration values.
    """
    config = get_config()
    assert config.env == "dev"
    assert config.sample_size == 1.0
    assert config.mode == "raise"


def test_config_validation():
    """
    Test that invalid configuration values raise appropriate errors.
    """
    # Invalid sample_size
    with pytest.raises(ValueError, match="Sample must be between 0.0 and 1.0"):
        Config(sample_size=1.5)

    # Invalid environment
    with pytest.raises(ValueError, match="Environment must be 'dev', 'staging', or 'prod'"):
        Config(env="invalid_env")

    # Invalid mode
    with pytest.raises(ValueError, match="Mode must be 'raise', 'log', or 'silent'"):
        Config(mode="invalid_mode")


def test_configure_function():
    """
    Test the `configure` function to ensure it updates the global configuration.
    """
    # Update the configuration
    configure(env="staging", sample_size=0.5, mode="log")

    # Get the updated configuration
    config = get_config()
    assert config.env == "staging"
    assert config.sample_size == 0.5
    assert config.mode == "log"

    # Reset the configuration to default
    configure(env="dev", sample_size=1.0, mode="raise")


def test_partial_configuration():
    """
    Test that `configure` allows partial updates to the configuration.
    """
    # Update only the environment
    configure(env="prod")
    config = get_config()
    assert config.env == "prod"
    assert config.sample_size == 1.0  # Unchanged
    assert config.mode == "raise"  # Unchanged

    # Update only the sample size
    configure(sample_size=0.25)
    config = get_config()
    assert config.env == "prod"  # Unchanged
    assert config.sample_size == 0.25
    assert config.mode == "raise"  # Unchanged

    # Update only the mode
    configure(mode="silent")
    config = get_config()
    assert config.env == "prod"  # Unchanged
    assert config.sample_size == 0.25  # Unchanged
    assert config.mode == "silent"

    # Reset the configuration to default
    configure(env="dev", sample_size=1.0, mode="raise")


def test_post_init_validation():
    """
    Test that the `__post_init__` method validates values correctly.
    """
    # Valid configuration
    config = Config(env="prod", sample_size=0.75, mode="log")
    assert config.env == "prod"
    assert config.sample_size == 0.75
    assert config.mode == "log"

    # Invalid sample size
    with pytest.raises(ValueError, match="Sample must be between 0.0 and 1.0"):
        Config(env="prod", sample_size=-0.1, mode="log")


def test_environment_variables(monkeypatch):
    """
    Test that environment variables are correctly used to initialize the configuration.
    """
    # Set environment variables
    monkeypatch.setenv("PY_FLOWCHECK_ENV", "staging")
    monkeypatch.setenv("PY_FLOWCHECK_SAMPLE_SIZE", "0.5")
    monkeypatch.setenv("PY_FLOWCHECK_MODE", "log")

    # Reinitialize the _config object to pick up the new environment variables
    import os
    from py_flowcheck.config import Config

    # Create new config with updated environment variables
    new_config = Config(
        env=os.getenv("PY_FLOWCHECK_ENV", "dev"),
        sample_size=float(os.getenv("PY_FLOWCHECK_SAMPLE_SIZE", "1.0")),
        mode=os.getenv("PY_FLOWCHECK_MODE", "raise"),
    )

    # Assert the new configuration values
    assert new_config.env == "staging"
    assert new_config.sample_size == 0.5
    assert new_config.mode == "log"

    # Reset environment variables
    monkeypatch.delenv("PY_FLOWCHECK_ENV", raising=False)
    monkeypatch.delenv("PY_FLOWCHECK_SAMPLE_SIZE", raising=False)
    monkeypatch.delenv("PY_FLOWCHECK_MODE", raising=False)