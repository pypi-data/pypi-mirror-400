# timber/common/config/__init__.py
"""
Configuration Module

Provides configuration management and model loading capabilities.
"""

from common.utils.config import config, Config
from .model_loader import model_loader, ModelConfigLoader

__all__ = [
    'config',
    'Config',
    'model_loader',
    'ModelConfigLoader',
]