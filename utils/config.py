"""
Configuration utilities for the Finance Assistant.
"""

import os
import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for the application.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config = {}
        
        # Default configuration
        self.config = {
            "api": {
                "base_url": "http://localhost:8000",
                "timeout": 30
            },
            "voice": {
                "model": "whisper-1",
                "voice": "onyx",
                "max_length": 4096
            },
            "retriever": {
                "top_k": 5,
                "similarity_threshold": 0.7
            },
            "log_level": "INFO"
        }
        
        # Load from config file if provided
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)
            
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_file(self, config_file: str) -> None:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                
            # Update config with file values
            self._update_config(file_config)
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_file}: {str(e)}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        try:
            # API settings
            if os.environ.get("API_BASE_URL"):
                self.config["api"]["base_url"] = os.environ.get("API_BASE_URL")
                
            if os.environ.get("API_TIMEOUT"):
                self.config["api"]["timeout"] = int(os.environ.get("API_TIMEOUT"))
                
            # Voice settings
            if os.environ.get("VOICE_MODEL"):
                self.config["voice"]["model"] = os.environ.get("VOICE_MODEL")
                
            if os.environ.get("VOICE_VOICE"):
                self.config["voice"]["voice"] = os.environ.get("VOICE_VOICE")
                
            # Retriever settings
            if os.environ.get("RETRIEVER_TOP_K"):
                self.config["retriever"]["top_k"] = int(os.environ.get("RETRIEVER_TOP_K"))
                
            if os.environ.get("RETRIEVER_SIMILARITY_THRESHOLD"):
                self.config["retriever"]["similarity_threshold"] = float(os.environ.get("RETRIEVER_SIMILARITY_THRESHOLD"))
                
            # Log level
            if os.environ.get("LOG_LEVEL"):
                self.config["log_level"] = os.environ.get("LOG_LEVEL")
                
            logger.info("Applied environment variable overrides to configuration")
        except Exception as e:
            logger.error(f"Error loading configuration from environment: {str(e)}")
    
    def _update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            new_config: New configuration values
        """
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    update_dict(d[k], v)
                else:
                    d[k] = v
        
        update_dict(self.config, new_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        try:
            keys = key.split(".")
            value = self.config
            
            for k in keys:
                value = value[k]
                
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Configuration value
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config

# Global config instance
config = Config()
