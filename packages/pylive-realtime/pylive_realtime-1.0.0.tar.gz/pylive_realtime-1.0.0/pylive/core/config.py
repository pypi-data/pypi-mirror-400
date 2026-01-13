"""
Configuration management for PyLive server.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8080
    read_timeout: int = 30
    write_timeout: int = 30
    idle_timeout: int = 120
    shutdown_timeout: int = 30


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///pylive.db"
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class JWTConfig:
    """JWT configuration."""
    secret: str = "change-me-in-production"
    ttl_hours: int = 24
    issuer: str = "pylive"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None


@dataclass
class NamespaceConfig:
    """Configuration for a namespace."""
    max_clients: Optional[int] = None
    max_history: Optional[int] = None
    ttl: Optional[str] = None
    require_auth: Optional[bool] = None
    allow_publish: Optional[bool] = None
    allow_presence: Optional[bool] = None
    private: Optional[bool] = None
    allowed_roles: List[str] = field(default_factory=list)
    proxy_endpoint: Optional[str] = None


@dataclass
class ChannelConfig:
    """Configuration for a specific channel."""
    pattern: str = ""
    namespace: str = ""
    max_clients: Optional[int] = None
    max_history: Optional[int] = None
    ttl: Optional[str] = None
    require_auth: Optional[bool] = None
    allow_publish: Optional[bool] = None
    allow_presence: Optional[bool] = None
    private: Optional[bool] = None
    allowed_roles: List[str] = field(default_factory=list)
    allowed_users: List[str] = field(default_factory=list)
    proxy_endpoint: Optional[str] = None


@dataclass
class Config:
    """Main configuration class."""
    server: ServerConfig = field(default_factory=ServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    jwt: JWTConfig = field(default_factory=JWTConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    namespaces: Dict[str, NamespaceConfig] = field(default_factory=dict)
    channels: List[ChannelConfig] = field(default_factory=list)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load configuration from file or environment."""
        config = cls()

        # Load from file if provided
        if path and os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                config = cls._from_dict(data)

        # Override with environment variables
        config._load_env()

        return config

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        config = cls()

        if "server" in data:
            config.server = ServerConfig(**data["server"])
        if "database" in data:
            config.database = DatabaseConfig(**data["database"])
        if "jwt" in data:
            config.jwt = JWTConfig(**data["jwt"])
        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])
        if "namespaces" in data:
            config.namespaces = {
                k: NamespaceConfig(**v) for k, v in data["namespaces"].items()
            }
        if "channels" in data:
            config.channels = [ChannelConfig(**c) for c in data["channels"]]

        return config

    def _load_env(self) -> None:
        """Load configuration from environment variables."""
        # Server
        if host := os.getenv("PYLIVE_HOST"):
            self.server.host = host
        if port := os.getenv("PYLIVE_PORT"):
            self.server.port = int(port)

        # Database
        if db_url := os.getenv("DATABASE_URL"):
            self.database.url = db_url

        # JWT
        if secret := os.getenv("JWT_SECRET"):
            self.jwt.secret = secret
        if ttl := os.getenv("JWT_TTL_HOURS"):
            self.jwt.ttl_hours = int(ttl)

        # Logging
        if level := os.getenv("LOG_LEVEL"):
            self.logging.level = level

    def namespace_config(self, namespace: str) -> Optional[NamespaceConfig]:
        """Get configuration for a namespace."""
        return self.namespaces.get(namespace)

    def channel_config(self, channel_id: str, namespace: str) -> Optional[ChannelConfig]:
        """Get configuration for a specific channel."""
        for cfg in self.channels:
            if cfg.namespace == namespace:
                # Simple pattern matching
                if cfg.pattern == channel_id or cfg.pattern == "*":
                    return cfg
                if cfg.pattern.endswith("*"):
                    prefix = cfg.pattern[:-1]
                    if channel_id.startswith(prefix):
                        return cfg
        return None
