import os
from dataclasses import dataclass
from typing import Literal, Optional

Environment = Literal["dev", "staging", "prod"]
Mode = Literal["raise", "log", "silent"]

@dataclass
class Config:
    env: Environment = "dev"
    sample_size: float = 1.0
    mode: Mode = "raise"
    enable_metrics: bool = True
    max_metrics_history: int = 1000

    def __post_init__(self):
        """Validating config values"""
        if not 0.0 <= self.sample_size <= 1.0:
            raise ValueError("Sample must be between 0.0 and 1.0")
        if self.env not in ["dev", "staging", "prod"]:
            raise ValueError("Environment must be 'dev', 'staging', or 'prod'")
        if self.mode not in ["raise", "log", "silent"]:
            raise ValueError("Mode must be 'raise', 'log', or 'silent'")
        if self.max_metrics_history < 0:
            raise ValueError("max_metrics_history must be non-negative")

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            env=os.getenv("PY_FLOWCHECK_ENV", "dev"),
            sample_size=float(os.getenv("PY_FLOWCHECK_SAMPLE_SIZE", "1.0")),
            mode=os.getenv("PY_FLOWCHECK_MODE", "raise"),
            enable_metrics=os.getenv("PY_FLOWCHECK_ENABLE_METRICS", "true").lower() == "true",
            max_metrics_history=int(os.getenv("PY_FLOWCHECK_MAX_METRICS_HISTORY", "1000"))
        )

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env == "prod"

    def should_validate(self, sample_rate: Optional[float] = None) -> bool:
        """Determine if validation should run based on sampling."""
        if not self.is_production():
            return True
        
        effective_rate = sample_rate if sample_rate is not None else self.sample_size
        if effective_rate >= 1.0:
            return True
        
        import random
        return random.random() <= effective_rate

# Initialize global config from environment
_config = Config.from_env()

def configure(
    env: Optional[Environment] = None,
    sample_size: Optional[float] = None,
    mode: Optional[Mode] = None,
    enable_metrics: Optional[bool] = None,
    max_metrics_history: Optional[int] = None
) -> None:
    """Configure the global settings for py_flowcheck."""
    global _config
    
    # Update only provided values
    updates = {}
    if env is not None:
        updates['env'] = env
    if sample_size is not None:
        updates['sample_size'] = sample_size
    if mode is not None:
        updates['mode'] = mode
    if enable_metrics is not None:
        updates['enable_metrics'] = enable_metrics
    if max_metrics_history is not None:
        updates['max_metrics_history'] = max_metrics_history
    
    # Create new config with updates
    current_dict = {
        'env': _config.env,
        'sample_size': _config.sample_size,
        'mode': _config.mode,
        'enable_metrics': _config.enable_metrics,
        'max_metrics_history': _config.max_metrics_history
    }
    current_dict.update(updates)
    
    _config = Config(**current_dict)

def get_config() -> Config:
    """Getting the current global configuration for the py_flowcheck."""
    return _config

def reset_config() -> None:
    """Reset configuration to environment defaults."""
    global _config
    _config = Config.from_env()
