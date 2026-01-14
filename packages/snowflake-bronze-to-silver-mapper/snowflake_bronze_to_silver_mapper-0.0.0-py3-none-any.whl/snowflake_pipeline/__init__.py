"""
Snowflake Pipeline Manager
A Docker-based data mapper transformation for Snowflake
"""

__version__ = "0.1.0"
__author__ = "Brunda V"
__email__ = "brunda8496@gmail.com"

from .docker_manager import DockerManager
from .config import Config

__all__ = ["DockerManager", "Config"]