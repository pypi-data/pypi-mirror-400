"""
Configuration for Analytics SDK.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from .default_config import (
    DEFAULT_SUPABASE_URL,
    DEFAULT_SUPABASE_KEY,
    DEFAULT_TABLE_NAME,
    DEFAULT_ENABLED,
    DEFAULT_TIMEOUT,
)

# Try to load .env file (optional - defaults are baked in)
_package_dir = Path(__file__).parent.parent
_env_paths = [
    _package_dir / ".env",  # analytics-sdk/.env (source directory)
    Path.cwd() / ".env",  # Current directory
    Path.cwd().parent / "analytics-sdk" / ".env",  # Parent/analytics-sdk/.env
    Path.home() / ".analytics-sdk" / ".env",  # Home directory
]

for _env_path in _env_paths:
    if _env_path.exists():
        load_dotenv(_env_path, override=True)
        break
else:
    # Fallback: try to find .env in current or parent directories
    load_dotenv()


@dataclass(frozen=True)
class AnalyticsConfig:
    """Configuration for Supabase analytics."""
    
    supabase_url: str
    supabase_key: str
    table_name: str = "analytics_events"
    enabled: bool = True
    timeout: int = 10
    
    @property
    def is_configured(self) -> bool:
        """Check if analytics is properly configured."""
        return bool(self.supabase_url) and bool(self.supabase_key) and self.enabled
    
    @classmethod
    def from_env(cls) -> "AnalyticsConfig":
        """
        Load configuration from environment variables or use baked-in defaults.
        
        Environment variables (optional, will override defaults):
            SUPABASE_URL: Your Supabase project URL
            SUPABASE_KEY: Your Supabase anon/service role key
            ANALYTICS_TABLE_NAME: Table name
            ANALYTICS_ENABLED: Enable/disable
            ANALYTICS_TIMEOUT: Request timeout in seconds
        
        If env vars are not set, uses baked-in default values.
        """
        # Use environment variables if set, otherwise use baked-in defaults
        supabase_url = os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL)
        supabase_key = os.getenv("SUPABASE_KEY", DEFAULT_SUPABASE_KEY)
        table_name = os.getenv("ANALYTICS_TABLE_NAME", DEFAULT_TABLE_NAME)
        enabled_str = os.getenv("ANALYTICS_ENABLED", str(DEFAULT_ENABLED))
        timeout_str = os.getenv("ANALYTICS_TIMEOUT", str(DEFAULT_TIMEOUT))
        
        return cls(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            table_name=table_name,
            enabled=enabled_str.lower() == "true" if isinstance(enabled_str, str) else DEFAULT_ENABLED,
            timeout=int(timeout_str) if timeout_str.isdigit() else DEFAULT_TIMEOUT,
        )

