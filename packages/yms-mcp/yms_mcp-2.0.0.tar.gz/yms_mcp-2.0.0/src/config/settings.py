#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Settings Module
Loads configuration from YAML file with environment variable overrides
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class YMSBackendConfig(BaseModel):
    """YMS Backend Configuration"""
    url: str = Field(default="https://yms-staging.item.com/api/yms")
    login_path: str = Field(default="/auth/yms/login-by-password")
    tenant_id: str = Field(default="LT")
    yard_id: str = Field(default="LT_F3")
    timezone: str = Field(default="America/Los_Angeles")
    token_expire_seconds: int = Field(default=3000)


class CameraConfig(BaseModel):
    """Camera Configuration"""
    name: str
    host: str
    port: int = 80
    username: str
    password: str
    location: Optional[str] = None
    enabled: bool = True


class Settings(BaseSettings):
    """Application Settings"""

    # YMS Backend
    yms_backend_url: str = Field(default="https://yms-staging.item.com/api/yms")
    yms_login_path: str = Field(default="/auth/yms/login-by-password")
    yms_tenant_id: str = Field(default="LT")
    yms_yard_id: str = Field(default="LT_F3")
    yms_timezone: str = Field(default="America/Los_Angeles")
    yms_username: str = Field(default="ymsdemo")
    yms_password: str = Field(default="ymsdemo")
    yms_token_expire_seconds: int = Field(default=3000)

    # Server
    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=8020)

    # Cameras
    cameras: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @classmethod
    def load_from_yaml(cls, config_path: Optional[str] = None) -> "Settings":
        """Load settings from YAML file with environment variable overrides"""
        if config_path is None:
            # Look for config.yaml in src/config directory
            config_path = Path(__file__).parent / "config.yaml"

        config_data = {}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f) or {}

            # Extract YMS backend configuration
            if 'yms_backend' in yaml_data:
                yms_backend = yaml_data['yms_backend']
                if 'url' in yms_backend:
                    config_data['yms_backend_url'] = yms_backend['url']
                if 'login_path' in yms_backend:
                    config_data['yms_login_path'] = yms_backend['login_path']

                # Extract headers
                if 'headers' in yms_backend:
                    headers = yms_backend['headers']
                    if 'tenant_id' in headers:
                        config_data['yms_tenant_id'] = headers['tenant_id']
                    if 'yard_id' in headers:
                        config_data['yms_yard_id'] = headers['yard_id']
                    if 'timezone' in headers:
                        config_data['yms_timezone'] = headers['timezone']
                    if 'token_expire_seconds' in headers:
                        config_data['yms_token_expire_seconds'] = headers['token_expire_seconds']

            # Extract server configuration
            if 'server' in yaml_data:
                server = yaml_data['server']
                if 'host' in server:
                    config_data['server_host'] = server['host']
                if 'port' in server:
                    config_data['server_port'] = server['port']

            # Extract cameras configuration
            if 'cameras' in yaml_data:
                config_data['cameras'] = yaml_data['cameras']

        # Create settings instance with YAML data
        # Environment variables will override YAML values
        return cls(**config_data)


# Global settings instance
settings = Settings.load_from_yaml()
