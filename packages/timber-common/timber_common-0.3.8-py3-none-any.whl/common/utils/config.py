# timber/common/utils/config.py
"""
Unified Configuration Management for Timber Common Library

This is the SINGLE source of truth for all configuration.
Combines database, API, encryption, vector, cache, decisioning, communication,
and integration factory settings.

Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv()


class Config:
    """
    Singleton class to manage and access environment variables and application settings.
    This centralizes ALL configuration management for Timber Common.
    
    Usage:
        from common.utils.config import config
        
        # Database
        db_url = config.get_db_url()
        
        # API Keys
        av_config = config.get_alpha_vantage_config()
        
        # Decisioning
        decision_paths = config.get_decision_config_paths()
        
        # Communication
        email_config = config.get_email_config()
        
        # Integration Factory
        integration_config = config.get_integration_config()
    """
    _instance: Optional['Config'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Loads configuration from environment variables."""
        
        # ===== Environment =====
        self.APP_ENV = os.getenv("APP_ENV", "development")
        self.OAK_ENV = os.getenv("OAK_ENV", "development")  # Alias for compatibility
        
        # ===== Database Settings - PostgreSQL =====
        # Primary way: Individual env vars (POSTGRES_*)
        self.DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
        self.DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))
        self.DB_USER = os.getenv("POSTGRES_USER", "postgres")
        self.DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        self.DB_NAME = os.getenv("POSTGRES_DB", "timber")
        self.DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"
        
        # Alternative: Full DATABASE_URL (overrides individual settings if present)
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            # Build from individual components
            self.DATABASE_URL = self.get_db_url()
        
        # Connection Pool Settings
        self.DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
        self.DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
        self.DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # ===== Encryption =====
        self.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
        self.MASTER_ENCRYPTION_KEY = os.getenv("MASTER_ENCRYPTION_KEY")
        self.ENCRYPTION_ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM", "fernet")
        
        # ===== Vector Database =====
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5")
        self.EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
        self.VECTOR_INDEX_TYPE = os.getenv("VECTOR_INDEX_TYPE", "ivfflat")
        self.VECTOR_INDEX_LISTS = int(os.getenv("VECTOR_INDEX_LISTS", "100"))
        
        # ===== Cache =====
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
        self.CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))
        
        # Redis Cache
        self.REDIS_ENABLED = os.getenv("REDIS_ENABLED", "False").lower() == "true"
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        
        # ===== Logging =====
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # ===== Features =====
        self.ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "False").lower() == "true"
        self.ENABLE_AUTO_VECTOR_INGESTION = os.getenv("ENABLE_AUTO_VECTOR_INGESTION", "False").lower() == "true"
        self.ENABLE_GDPR = os.getenv("ENABLE_GDPR", "True").lower() == "true"
        
        # ===== Performance =====
        self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
        self.MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
        
        # ===== API Keys - External Data Sources =====
        self.ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.POLYGON_API_KEY: Optional[str] = os.getenv("POLYGON_API_KEY")
        self.FINNHUB_API_KEY: Optional[str] = os.getenv("FINNHUB_API_KEY")
        
        # ===== LLM Service Configuration =====
        # Multi-Provider LLM Service API Keys
        self.GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
        self.PERPLEXITY_API_KEY: Optional[str] = os.getenv("PERPLEXITY_API_KEY")
        self.GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        
        # LLM Service Settings
        # DEFAULT_LLM is an alias for LLM_DEFAULT_PROVIDER (backward compatibility)
        self.DEFAULT_LLM: str = os.getenv("DEFAULT_LLM") or os.getenv("LLM_DEFAULT_PROVIDER", "groq")
        self.LLM_DEFAULT_PROVIDER: str = self.DEFAULT_LLM  # Use same value
        self.LLM_ENABLE_FALLBACK: bool = os.getenv("LLM_ENABLE_FALLBACK", "true").lower() == "true"
        self.LLM_FALLBACK_ORDER: str = os.getenv("LLM_FALLBACK_ORDER", "groq,gemini,perplexity,claude")
        self.LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
        self.LLM_COOLDOWN_MINUTES: int = int(os.getenv("LLM_COOLDOWN_MINUTES", "5"))
        
        # LLM Default Parameters
        self.LLM_DEFAULT_MAX_TOKENS: int = int(os.getenv("LLM_DEFAULT_MAX_TOKENS", "1000"))
        self.LLM_DEFAULT_TEMPERATURE: float = float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.7"))
        
        # Default Models per Provider (configurable via environment)
        # These override provider hardcoded defaults
        self.GROQ_DEFAULT_MODEL: str = os.getenv("GROQ_DEFAULT_MODEL", "llama-3.3-70b-versatile")
        self.GEMINI_DEFAULT_MODEL: str = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.0-flash-exp")
        self.PERPLEXITY_DEFAULT_MODEL: str = os.getenv("PERPLEXITY_DEFAULT_MODEL", "llama-3.1-sonar-large-128k-online")
        self.CLAUDE_DEFAULT_MODEL: str = os.getenv("CLAUDE_DEFAULT_MODEL", "claude-sonnet-4-20250514")
        
        # Legacy LLM Configuration (deprecated - use multi-provider service)
        self.LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
        self.LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash")
        
        # API Base URLs
        self.ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
        self.POLYGON_BASE_URL: str = "https://api.massive.com"
        self.FINNHUB_BASE_URL: str = "https://finnhub.io/api/v1"
        
        # ===== Data Storage Paths =====
        CURRENT_FILE_DIR = Path(__file__).resolve().parent
        PROJECT_ROOT = CURRENT_FILE_DIR.parents[1]  # From common/utils/config.py to timber/
        self.PROJECT_ROOT: Path = PROJECT_ROOT
        self.DATA_DIR: Path = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
        self.CONFIG_DIR: Path = Path(os.getenv("CONFIG_DIR", PROJECT_ROOT / "config"))
        # MODEL_CONFIG_DIR uses PROJECT_ROOT directly for backward compatibility
        self.MODEL_CONFIG_DIR: Path = Path(os.getenv("MODEL_CONFIG_DIR", PROJECT_ROOT / "config" / "models"))
        self.CURATED_COMPANIES_DIR: Path = self.DATA_DIR / "curated_companies"
        self.CACHE_DIR: Path = self.DATA_DIR / "cache"
        
        # ===== Decisioning Engine Configuration =====
        # Multiple directories can be specified, comma-separated
        # Default: config/decisioning for business rules, data/decisions for runtime decisions
        self.DECISION_CONFIG_DIRS: str = os.getenv(
            "DECISION_CONFIG_DIRS",
            f"{self.CONFIG_DIR / 'decisioning'},{self.DATA_DIR / 'decisions'}"
        )
        self.DECISION_AUTO_LOAD: bool = os.getenv("DECISION_AUTO_LOAD", "True").lower() == "true"
        self.DECISION_CACHE_ENABLED: bool = os.getenv("DECISION_CACHE_ENABLED", "True").lower() == "true"
        self.DECISION_CACHE_TTL_SECONDS: int = int(os.getenv("DECISION_CACHE_TTL_SECONDS", "300"))
        self.DECISION_TRACE_ENABLED: bool = os.getenv("DECISION_TRACE_ENABLED", "False").lower() == "true"
        self.DECISION_LOG_EVALUATIONS: bool = os.getenv("DECISION_LOG_EVALUATIONS", "False").lower() == "true"
        self.DECISION_DEFAULT_HIT_POLICY: str = os.getenv("DECISION_DEFAULT_HIT_POLICY", "FIRST")
        
        # ===== Scheduler Configuration =====
        self.SCHEDULER_CONFIG_DIR: Path = Path(os.getenv("SCHEDULER_CONFIG_DIR", self.CONFIG_DIR / "scheduler"))
        self.SCHEDULER_AUTO_DISCOVER: bool = os.getenv("SCHEDULER_AUTO_DISCOVER", "True").lower() == "true"
        
        # ===== Integration Factory Configuration =====
        # Credential directories - comma-separated list of paths
        # Default: config/integrations/credentials
        self.INTEGRATION_CREDENTIALS_DIRS: str = os.getenv(
            "INTEGRATION_CREDENTIALS_DIRS",
            str(self.CONFIG_DIR / "integrations" / "credentials")
        )
        
        # Integration definition directories - comma-separated list of paths
        # Default: config/integrations/definitions
        self.INTEGRATION_DEFINITIONS_DIRS: str = os.getenv(
            "INTEGRATION_DEFINITIONS_DIRS",
            str(self.CONFIG_DIR / "integrations" / "definitions")
        )
        
        # Main integration config file (optional - if not set, uses directory scanning)
        self.INTEGRATION_CONFIG_FILE: Optional[str] = os.getenv("INTEGRATION_CONFIG_FILE")
        
        # Integration auto-load on startup
        self.INTEGRATION_AUTO_LOAD: bool = os.getenv("INTEGRATION_AUTO_LOAD", "True").lower() == "true"
        
        # Response caching
        self.INTEGRATION_CACHE_ENABLED: bool = os.getenv("INTEGRATION_CACHE_ENABLED", "True").lower() == "true"
        self.INTEGRATION_CACHE_BACKEND: str = os.getenv("INTEGRATION_CACHE_BACKEND", "memory")  # memory, redis
        self.INTEGRATION_CACHE_TTL_SECONDS: int = int(os.getenv("INTEGRATION_CACHE_TTL_SECONDS", "300"))
        
        # Retry configuration
        self.INTEGRATION_RETRY_ENABLED: bool = os.getenv("INTEGRATION_RETRY_ENABLED", "True").lower() == "true"
        self.INTEGRATION_RETRY_MAX_ATTEMPTS: int = int(os.getenv("INTEGRATION_RETRY_MAX_ATTEMPTS", "3"))
        self.INTEGRATION_RETRY_INITIAL_DELAY_MS: int = int(os.getenv("INTEGRATION_RETRY_INITIAL_DELAY_MS", "1000"))
        self.INTEGRATION_RETRY_BACKOFF_MULTIPLIER: float = float(os.getenv("INTEGRATION_RETRY_BACKOFF_MULTIPLIER", "2.0"))
        self.INTEGRATION_RETRY_MAX_DELAY_MS: int = int(os.getenv("INTEGRATION_RETRY_MAX_DELAY_MS", "30000"))
        
        # Circuit breaker
        self.INTEGRATION_CIRCUIT_BREAKER_ENABLED: bool = os.getenv("INTEGRATION_CIRCUIT_BREAKER_ENABLED", "True").lower() == "true"
        self.INTEGRATION_CIRCUIT_FAILURE_THRESHOLD: int = int(os.getenv("INTEGRATION_CIRCUIT_FAILURE_THRESHOLD", "5"))
        self.INTEGRATION_CIRCUIT_SUCCESS_THRESHOLD: int = int(os.getenv("INTEGRATION_CIRCUIT_SUCCESS_THRESHOLD", "2"))
        self.INTEGRATION_CIRCUIT_TIMEOUT_SECONDS: int = int(os.getenv("INTEGRATION_CIRCUIT_TIMEOUT_SECONDS", "60"))
        
        # HTTP client settings
        self.INTEGRATION_HTTP_TIMEOUT_SECONDS: int = int(os.getenv("INTEGRATION_HTTP_TIMEOUT_SECONDS", "30"))
        self.INTEGRATION_HTTP_CONNECT_TIMEOUT_SECONDS: int = int(os.getenv("INTEGRATION_HTTP_CONNECT_TIMEOUT_SECONDS", "10"))
        self.INTEGRATION_HTTP_MAX_CONNECTIONS: int = int(os.getenv("INTEGRATION_HTTP_MAX_CONNECTIONS", "100"))
        self.INTEGRATION_HTTP_MAX_KEEPALIVE: int = int(os.getenv("INTEGRATION_HTTP_MAX_KEEPALIVE", "20"))
        
        # OAuth token caching
        self.INTEGRATION_OAUTH_CACHE_BACKEND: str = os.getenv("INTEGRATION_OAUTH_CACHE_BACKEND", "memory")  # memory, redis, database
        self.INTEGRATION_OAUTH_TOKEN_BUFFER_SECONDS: int = int(os.getenv("INTEGRATION_OAUTH_TOKEN_BUFFER_SECONDS", "300"))
        
        # Logging and tracing
        self.INTEGRATION_LOG_REQUESTS: bool = os.getenv("INTEGRATION_LOG_REQUESTS", "True").lower() == "true"
        self.INTEGRATION_LOG_RESPONSES: bool = os.getenv("INTEGRATION_LOG_RESPONSES", "True").lower() == "true"
        self.INTEGRATION_LOG_HEADERS: bool = os.getenv("INTEGRATION_LOG_HEADERS", "False").lower() == "true"
        self.INTEGRATION_LOG_BODY: bool = os.getenv("INTEGRATION_LOG_BODY", "False").lower() == "true"
        self.INTEGRATION_TRACE_ENABLED: bool = os.getenv("INTEGRATION_TRACE_ENABLED", "False").lower() == "true"
        
        # Credential encryption key (for encrypting credentials at rest)
        self.INTEGRATION_ENCRYPTION_KEY: Optional[str] = os.getenv("INTEGRATION_ENCRYPTION_KEY")
        
        # ===== Communication Services Configuration =====
        # Email Service
        self.EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "sendgrid")  # sendgrid, ses, smtp
        self.EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "noreply@oakquant.com")
        self.EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "OakQuant")
        self.EMAIL_REPLY_TO: Optional[str] = os.getenv("EMAIL_REPLY_TO")
        
        # SendGrid
        self.SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
        
        # AWS SES
        self.AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
        self.SES_CONFIGURATION_SET: Optional[str] = os.getenv("SES_CONFIGURATION_SET")
        
        # SMTP
        self.SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
        self.SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
        self.SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
        
        # SMS Service
        self.SMS_PROVIDER: str = os.getenv("SMS_PROVIDER", "twilio")  # twilio, sns, vonage
        self.SMS_FROM_NUMBER: Optional[str] = os.getenv("SMS_FROM_NUMBER")
        
        # Twilio
        self.TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_MESSAGING_SERVICE_SID: Optional[str] = os.getenv("TWILIO_MESSAGING_SERVICE_SID")
        
        # Vonage
        self.VONAGE_API_KEY: Optional[str] = os.getenv("VONAGE_API_KEY")
        self.VONAGE_API_SECRET: Optional[str] = os.getenv("VONAGE_API_SECRET")
        
        # Push Notifications
        self.PUSH_PROVIDER: str = os.getenv("PUSH_PROVIDER", "firebase")  # firebase, onesignal
        self.FIREBASE_CREDENTIALS_PATH: Optional[str] = os.getenv("FIREBASE_CREDENTIALS_PATH")
        self.ONESIGNAL_APP_ID: Optional[str] = os.getenv("ONESIGNAL_APP_ID")
        self.ONESIGNAL_API_KEY: Optional[str] = os.getenv("ONESIGNAL_API_KEY")
        
        # Email Templates
        self.EMAIL_TEMPLATE_DIR: Path = Path(os.getenv("EMAIL_TEMPLATE_DIR", self.CONFIG_DIR / "templates" / "email"))
        
        # ===== Rate Limiting =====
        self.API_REQUEST_TIMEOUT: int = int(os.getenv("API_REQUEST_TIMEOUT", "20"))
        self.MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # ========================================================================
    # Database Methods
    # ========================================================================
    
    def get_db_url(self) -> str:
        """
        Constructs the SQLAlchemy database connection URL.
        
        Returns:
            Database connection string
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def validate_database_config(self) -> bool:
        """
        Validate that database configuration is complete.
        
        Returns:
            True if all required fields are present
        """
        required = [self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME]
        return all(required)
    
    def get_pool_config(self) -> Dict[str, int]:
        """
        Returns database connection pool configuration.
        
        Returns:
            Dictionary with pool settings
        """
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
        }
    
    # ========================================================================
    # API Configuration Methods
    # ========================================================================
    
    def get_alpha_vantage_config(self) -> Dict[str, Any]:
        """Returns Alpha Vantage API configuration."""
        return {
            "api_key": self.ALPHA_VANTAGE_API_KEY,
            "base_url": self.ALPHA_VANTAGE_BASE_URL,
            "timeout": self.API_REQUEST_TIMEOUT,
        }
    
    def get_polygon_config(self) -> Dict[str, Any]:
        """Returns Polygon API configuration."""
        return {
            "api_key": self.POLYGON_API_KEY,
            "base_url": self.POLYGON_BASE_URL,
            "timeout": self.API_REQUEST_TIMEOUT,
        }
    
    def get_finnhub_config(self) -> Dict[str, Any]:
        """Returns Finnhub API configuration."""
        return {
            "api_key": self.FINNHUB_API_KEY,
            "base_url": self.FINNHUB_BASE_URL,
            "timeout": self.API_REQUEST_TIMEOUT,
        }
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate which API keys are configured.
        
        Returns:
            Dictionary mapping service to configuration status
        """
        return {
            "alpha_vantage": bool(self.ALPHA_VANTAGE_API_KEY and 'use_env' not in str(self.ALPHA_VANTAGE_API_KEY)),
            "polygon": bool(self.POLYGON_API_KEY and 'use_env' not in str(self.POLYGON_API_KEY)),
            "finnhub": bool(self.FINNHUB_API_KEY and 'use_env' not in str(self.FINNHUB_API_KEY)),
            "groq": bool(self.GROQ_API_KEY),
            "perplexity": bool(self.PERPLEXITY_API_KEY),
            "gemini": bool(self.GEMINI_API_KEY),
            "anthropic": bool(self.ANTHROPIC_API_KEY),
        }
    
    # ========================================================================
    # LLM Service Configuration Methods
    # ========================================================================
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Returns complete LLM service configuration.
        
        Returns:
            Dictionary with all LLM service settings
        """
        return {
            "groq_api_key": self.GROQ_API_KEY,
            "perplexity_api_key": self.PERPLEXITY_API_KEY,
            "gemini_api_key": self.GEMINI_API_KEY,
            "claude_api_key": self.ANTHROPIC_API_KEY,
            "default_provider": self.LLM_DEFAULT_PROVIDER,
            "enable_fallback": self.LLM_ENABLE_FALLBACK,
            "fallback_order": self.get_llm_fallback_order(),
            "max_retries": self.LLM_MAX_RETRIES,
            "cooldown_minutes": self.LLM_COOLDOWN_MINUTES,
            "default_max_tokens": self.LLM_DEFAULT_MAX_TOKENS,
            "default_temperature": self.LLM_DEFAULT_TEMPERATURE,
        }
    
    def get_llm_fallback_order(self) -> list:
        """
        Parse and return LLM fallback order as list of provider enums.
        
        Returns:
            List of LLMProvider enums in fallback order
        """
        try:
            from common.services.llm import LLMProvider
            
            order_str = self.LLM_FALLBACK_ORDER.split(',')
            order = []
            
            for provider_str in order_str:
                provider_str = provider_str.strip().lower()
                try:
                    provider = LLMProvider(provider_str)
                    order.append(provider)
                except ValueError:
                    # Skip invalid providers
                    pass
            
            return order
        except ImportError:
            # LLM service not available, return empty list
            return []
    
    def validate_llm_config(self) -> Dict[str, bool]:
        """
        Validate which LLM providers are configured.
        
        Returns:
            Dictionary mapping provider name to configuration status
        """
        return {
            'groq': bool(self.GROQ_API_KEY),
            'perplexity': bool(self.PERPLEXITY_API_KEY),
            'gemini': bool(self.GEMINI_API_KEY),
            'claude': bool(self.ANTHROPIC_API_KEY),
        }
    
    def get_configured_llm_providers(self) -> list:
        """
        Get list of configured LLM provider names.
        
        Returns:
            List of provider names that have API keys configured
        """
        validation = self.validate_llm_config()
        return [provider for provider, configured in validation.items() if configured]
    
    def has_any_llm_provider(self) -> bool:
        """
        Check if at least one LLM provider is configured.
        
        Returns:
            True if any LLM provider has an API key configured
        """
        return any(self.validate_llm_config().values())
    
    # ========================================================================
    # Decisioning Engine Configuration Methods
    # ========================================================================
    
    def get_decision_config_dirs(self) -> List[Path]:
        """
        Get list of directories to scan for decision files.
        
        Returns:
            List of Path objects for decision configuration directories
        """
        dirs = []
        for dir_str in self.DECISION_CONFIG_DIRS.split(','):
            dir_path = Path(dir_str.strip())
            if dir_path.exists():
                dirs.append(dir_path)
        return dirs
    
    def get_decision_config_paths(self, pattern: str = "*.yaml") -> List[Path]:
        """
        Get list of decision configuration file paths.
        
        Scans all configured decision directories for matching files.
        
        Args:
            pattern: Glob pattern for files (default: *.yaml)
            
        Returns:
            List of Path objects for decision config files
        """
        paths = []
        for config_dir in self.get_decision_config_dirs():
            if config_dir.exists():
                # Include subdirectories
                paths.extend(config_dir.glob(f'**/{pattern}'))
        return sorted(paths)
    
    def get_decision_config(self) -> Dict[str, Any]:
        """
        Returns complete decisioning engine configuration.
        
        Returns:
            Dictionary with all decisioning settings
        """
        return {
            "config_dirs": [str(p) for p in self.get_decision_config_dirs()],
            "auto_load": self.DECISION_AUTO_LOAD,
            "cache_enabled": self.DECISION_CACHE_ENABLED,
            "cache_ttl_seconds": self.DECISION_CACHE_TTL_SECONDS,
            "trace_enabled": self.DECISION_TRACE_ENABLED,
            "log_evaluations": self.DECISION_LOG_EVALUATIONS,
            "default_hit_policy": self.DECISION_DEFAULT_HIT_POLICY,
        }
    
    def add_decision_config_dir(self, path: str | Path) -> None:
        """
        Add a directory to the decision configuration search paths.
        
        Args:
            path: Directory path to add
        """
        path = Path(path)
        current_dirs = self.DECISION_CONFIG_DIRS.split(',')
        if str(path) not in current_dirs:
            current_dirs.append(str(path))
            self.DECISION_CONFIG_DIRS = ','.join(current_dirs)
    
    # ========================================================================
    # Integration Factory Configuration Methods
    # ========================================================================
    
    def get_integration_credentials_dirs(self) -> List[Path]:
        """
        Get list of directories to scan for credential files.
        
        Returns:
            List of Path objects for credential directories
        """
        dirs = []
        for dir_str in self.INTEGRATION_CREDENTIALS_DIRS.split(','):
            dir_path = Path(dir_str.strip())
            dirs.append(dir_path)
        return dirs
    
    def get_integration_definitions_dirs(self) -> List[Path]:
        """
        Get list of directories to scan for integration definition files.
        
        Returns:
            List of Path objects for integration definition directories
        """
        dirs = []
        for dir_str in self.INTEGRATION_DEFINITIONS_DIRS.split(','):
            dir_path = Path(dir_str.strip())
            dirs.append(dir_path)
        return dirs
    
    def get_integration_credentials_paths(self, pattern: str = "*.yaml") -> List[Path]:
        """
        Get list of credential configuration file paths.
        
        Args:
            pattern: Glob pattern for files (default: *.yaml)
            
        Returns:
            List of Path objects for credential config files
        """
        paths = []
        for config_dir in self.get_integration_credentials_dirs():
            if config_dir.exists():
                paths.extend(config_dir.glob(f'**/{pattern}'))
        return sorted(paths)
    
    def get_integration_definitions_paths(self, pattern: str = "*.yaml") -> List[Path]:
        """
        Get list of integration definition file paths.
        
        Args:
            pattern: Glob pattern for files (default: *.yaml)
            
        Returns:
            List of Path objects for integration definition files
        """
        paths = []
        for config_dir in self.get_integration_definitions_dirs():
            if config_dir.exists():
                paths.extend(config_dir.glob(f'**/{pattern}'))
        return sorted(paths)
    
    def get_integration_retry_config(self) -> Dict[str, Any]:
        """
        Returns retry configuration for integrations.
        
        Returns:
            Dictionary with retry settings
        """
        return {
            "enabled": self.INTEGRATION_RETRY_ENABLED,
            "max_attempts": self.INTEGRATION_RETRY_MAX_ATTEMPTS,
            "initial_delay_ms": self.INTEGRATION_RETRY_INITIAL_DELAY_MS,
            "backoff_multiplier": self.INTEGRATION_RETRY_BACKOFF_MULTIPLIER,
            "max_delay_ms": self.INTEGRATION_RETRY_MAX_DELAY_MS,
        }
    
    def get_integration_circuit_breaker_config(self) -> Dict[str, Any]:
        """
        Returns circuit breaker configuration for integrations.
        
        Returns:
            Dictionary with circuit breaker settings
        """
        return {
            "enabled": self.INTEGRATION_CIRCUIT_BREAKER_ENABLED,
            "failure_threshold": self.INTEGRATION_CIRCUIT_FAILURE_THRESHOLD,
            "success_threshold": self.INTEGRATION_CIRCUIT_SUCCESS_THRESHOLD,
            "timeout_seconds": self.INTEGRATION_CIRCUIT_TIMEOUT_SECONDS,
        }
    
    def get_integration_http_config(self) -> Dict[str, Any]:
        """
        Returns HTTP client configuration for integrations.
        
        Returns:
            Dictionary with HTTP client settings
        """
        return {
            "timeout_seconds": self.INTEGRATION_HTTP_TIMEOUT_SECONDS,
            "connect_timeout_seconds": self.INTEGRATION_HTTP_CONNECT_TIMEOUT_SECONDS,
            "max_connections": self.INTEGRATION_HTTP_MAX_CONNECTIONS,
            "max_keepalive_connections": self.INTEGRATION_HTTP_MAX_KEEPALIVE,
        }
    
    def get_integration_cache_config(self) -> Dict[str, Any]:
        """
        Returns cache configuration for integrations.
        
        Returns:
            Dictionary with cache settings
        """
        return {
            "enabled": self.INTEGRATION_CACHE_ENABLED,
            "backend": self.INTEGRATION_CACHE_BACKEND,
            "ttl_seconds": self.INTEGRATION_CACHE_TTL_SECONDS,
        }
    
    def get_integration_oauth_config(self) -> Dict[str, Any]:
        """
        Returns OAuth configuration for integrations.
        
        Returns:
            Dictionary with OAuth settings
        """
        return {
            "cache_backend": self.INTEGRATION_OAUTH_CACHE_BACKEND,
            "token_buffer_seconds": self.INTEGRATION_OAUTH_TOKEN_BUFFER_SECONDS,
        }
    
    def get_integration_logging_config(self) -> Dict[str, Any]:
        """
        Returns logging configuration for integrations.
        
        Returns:
            Dictionary with logging settings
        """
        return {
            "log_requests": self.INTEGRATION_LOG_REQUESTS,
            "log_responses": self.INTEGRATION_LOG_RESPONSES,
            "log_headers": self.INTEGRATION_LOG_HEADERS,
            "log_body": self.INTEGRATION_LOG_BODY,
            "trace_enabled": self.INTEGRATION_TRACE_ENABLED,
        }
    
    def get_integration_config(self) -> Dict[str, Any]:
        """
        Returns complete integration factory configuration.
        
        Returns:
            Dictionary with all integration factory settings
        """
        return {
            # Paths
            "credentials_dirs": [str(p) for p in self.get_integration_credentials_dirs()],
            "definitions_dirs": [str(p) for p in self.get_integration_definitions_dirs()],
            "config_file": self.INTEGRATION_CONFIG_FILE,
            "base_dir": str(self.PROJECT_ROOT),
            
            # Auto-load
            "auto_load": self.INTEGRATION_AUTO_LOAD,
            
            # Sub-configurations
            "cache": self.get_integration_cache_config(),
            "retry": self.get_integration_retry_config(),
            "circuit_breaker": self.get_integration_circuit_breaker_config(),
            "http": self.get_integration_http_config(),
            "oauth": self.get_integration_oauth_config(),
            "logging": self.get_integration_logging_config(),
            
            # Encryption
            "encryption_key": self.INTEGRATION_ENCRYPTION_KEY,
        }
    
    def add_integration_credentials_dir(self, path: str | Path) -> None:
        """
        Add a directory to the integration credentials search paths.
        
        Args:
            path: Directory path to add
        """
        path = Path(path)
        current_dirs = self.INTEGRATION_CREDENTIALS_DIRS.split(',')
        if str(path) not in current_dirs:
            current_dirs.append(str(path))
            self.INTEGRATION_CREDENTIALS_DIRS = ','.join(current_dirs)
    
    def add_integration_definitions_dir(self, path: str | Path) -> None:
        """
        Add a directory to the integration definitions search paths.
        
        Args:
            path: Directory path to add
        """
        path = Path(path)
        current_dirs = self.INTEGRATION_DEFINITIONS_DIRS.split(',')
        if str(path) not in current_dirs:
            current_dirs.append(str(path))
            self.INTEGRATION_DEFINITIONS_DIRS = ','.join(current_dirs)
    
    def validate_integration_config(self) -> Dict[str, bool]:
        """
        Validate integration factory configuration.
        
        Returns:
            Dictionary with validation status for each component
        """
        credentials_dirs_exist = any(
            Path(d).exists() 
            for d in self.INTEGRATION_CREDENTIALS_DIRS.split(',')
        )
        definitions_dirs_exist = any(
            Path(d).exists() 
            for d in self.INTEGRATION_DEFINITIONS_DIRS.split(',')
        )
        
        return {
            "credentials_dirs_exist": credentials_dirs_exist,
            "definitions_dirs_exist": definitions_dirs_exist,
            "config_file_exists": (
                Path(self.INTEGRATION_CONFIG_FILE).exists() 
                if self.INTEGRATION_CONFIG_FILE else True
            ),
            "cache_enabled": self.INTEGRATION_CACHE_ENABLED,
            "circuit_breaker_enabled": self.INTEGRATION_CIRCUIT_BREAKER_ENABLED,
            "encryption_configured": bool(self.INTEGRATION_ENCRYPTION_KEY),
        }
    
    # ========================================================================
    # Communication Services Configuration Methods
    # ========================================================================
    
    def get_email_config(self) -> Dict[str, Any]:
        """
        Returns email service configuration.
        
        Returns:
            Dictionary with email settings for configured provider
        """
        base_config = {
            "provider": self.EMAIL_PROVIDER,
            "from_address": self.EMAIL_FROM_ADDRESS,
            "from_name": self.EMAIL_FROM_NAME,
            "reply_to": self.EMAIL_REPLY_TO,
            "template_dir": str(self.EMAIL_TEMPLATE_DIR),
        }
        
        if self.EMAIL_PROVIDER == "sendgrid":
            base_config.update({
                "api_key": self.SENDGRID_API_KEY,
            })
        elif self.EMAIL_PROVIDER == "ses":
            base_config.update({
                "aws_access_key_id": self.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": self.AWS_SECRET_ACCESS_KEY,
                "aws_region": self.AWS_REGION,
                "configuration_set": self.SES_CONFIGURATION_SET,
            })
        elif self.EMAIL_PROVIDER == "smtp":
            base_config.update({
                "host": self.SMTP_HOST,
                "port": self.SMTP_PORT,
                "username": self.SMTP_USERNAME,
                "password": self.SMTP_PASSWORD,
                "use_tls": self.SMTP_USE_TLS,
            })
        
        return base_config
    
    def get_sms_config(self) -> Dict[str, Any]:
        """
        Returns SMS service configuration.
        
        Returns:
            Dictionary with SMS settings for configured provider
        """
        base_config = {
            "provider": self.SMS_PROVIDER,
            "from_number": self.SMS_FROM_NUMBER,
        }
        
        if self.SMS_PROVIDER == "twilio":
            base_config.update({
                "account_sid": self.TWILIO_ACCOUNT_SID,
                "auth_token": self.TWILIO_AUTH_TOKEN,
                "messaging_service_sid": self.TWILIO_MESSAGING_SERVICE_SID,
            })
        elif self.SMS_PROVIDER == "sns":
            base_config.update({
                "aws_access_key_id": self.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": self.AWS_SECRET_ACCESS_KEY,
                "aws_region": self.AWS_REGION,
            })
        elif self.SMS_PROVIDER == "vonage":
            base_config.update({
                "api_key": self.VONAGE_API_KEY,
                "api_secret": self.VONAGE_API_SECRET,
            })
        
        return base_config
    
    def get_push_config(self) -> Dict[str, Any]:
        """
        Returns push notification service configuration.
        
        Returns:
            Dictionary with push notification settings
        """
        base_config = {
            "provider": self.PUSH_PROVIDER,
        }
        
        if self.PUSH_PROVIDER == "firebase":
            base_config.update({
                "credentials_path": self.FIREBASE_CREDENTIALS_PATH,
            })
        elif self.PUSH_PROVIDER == "onesignal":
            base_config.update({
                "app_id": self.ONESIGNAL_APP_ID,
                "api_key": self.ONESIGNAL_API_KEY,
            })
        
        return base_config
    
    def validate_email_config(self) -> bool:
        """
        Validate that email configuration is complete.
        
        Returns:
            True if email provider is properly configured
        """
        if self.EMAIL_PROVIDER == "sendgrid":
            return bool(self.SENDGRID_API_KEY)
        elif self.EMAIL_PROVIDER == "ses":
            return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY)
        elif self.EMAIL_PROVIDER == "smtp":
            return bool(self.SMTP_HOST and self.SMTP_USERNAME)
        return False
    
    def validate_sms_config(self) -> bool:
        """
        Validate that SMS configuration is complete.
        
        Returns:
            True if SMS provider is properly configured
        """
        if self.SMS_PROVIDER == "twilio":
            return bool(self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN)
        elif self.SMS_PROVIDER == "sns":
            return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY)
        elif self.SMS_PROVIDER == "vonage":
            return bool(self.VONAGE_API_KEY and self.VONAGE_API_SECRET)
        return False
    
    def get_communication_status(self) -> Dict[str, bool]:
        """
        Get status of all communication services.
        
        Returns:
            Dictionary with configuration status for each service
        """
        return {
            "email": self.validate_email_config(),
            "sms": self.validate_sms_config(),
            "push": bool(
                (self.PUSH_PROVIDER == "firebase" and self.FIREBASE_CREDENTIALS_PATH) or
                (self.PUSH_PROVIDER == "onesignal" and self.ONESIGNAL_APP_ID)
            ),
        }
    
    # ========================================================================
    # Scheduler Configuration Methods
    # ========================================================================
    
    def get_scheduler_config_paths(self, pattern: str = "*.yaml") -> List[Path]:
        """
        Get list of scheduler configuration file paths.
        
        Args:
            pattern: Glob pattern for files (default: *.yaml)
            
        Returns:
            List of Path objects for scheduler config files
        """
        if not self.SCHEDULER_CONFIG_DIR.exists():
            return []
        
        return sorted(self.SCHEDULER_CONFIG_DIR.glob(f'**/{pattern}'))
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """
        Returns scheduler configuration.
        
        Returns:
            Dictionary with scheduler settings
        """
        return {
            "config_dir": str(self.SCHEDULER_CONFIG_DIR),
            "auto_discover": self.SCHEDULER_AUTO_DISCOVER,
            "config_files": [str(p) for p in self.get_scheduler_config_paths()],
        }
    
    # ========================================================================
    # Path Management
    # ========================================================================
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.CURATED_COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.MODEL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.SCHEDULER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.EMAIL_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Ensure decision directories exist
        for dir_path in self.get_decision_config_dirs():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure integration directories exist
        for dir_path in self.get_integration_credentials_dirs():
            dir_path.mkdir(parents=True, exist_ok=True)
        for dir_path in self.get_integration_definitions_dirs():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_model_config_paths(self) -> list:
        """
        Get list of model configuration file paths.
        
        Returns:
            List of Path objects for YAML config files
        """
        if not self.MODEL_CONFIG_DIR.exists():
            return []
        
        return list(self.MODEL_CONFIG_DIR.glob('**/*.yaml'))
    
    # ========================================================================
    # Validation
    # ========================================================================
    
    def validate(self) -> None:
        """
        Validate required configuration.
        
        Raises:
            ValueError: If required configuration is missing
        """
        errors = []
        
        # Check required fields
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL not set and cannot be constructed from individual settings")
        
        if self.ENABLE_ENCRYPTION and not self.ENCRYPTION_KEY:
            errors.append("ENCRYPTION_KEY required when encryption is enabled")
        
        # Validate database URL format
        if self.DATABASE_URL and not self.DATABASE_URL.startswith(('postgresql://', 'sqlite://')):
            errors.append("DATABASE_URL must be PostgreSQL or SQLite")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.OAK_ENV.lower() == 'production' or self.APP_ENV.lower() == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.OAK_ENV.lower() == 'development' or self.APP_ENV.lower() == 'development'
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary (excludes sensitive values)
        """
        return {
            # Environment
            'app_env': self.APP_ENV,
            'oak_env': self.OAK_ENV,
            
            # Database
            'database_url': self.DATABASE_URL.split('@')[-1] if '@' in self.DATABASE_URL else self.DATABASE_URL,
            'database_echo': self.DATABASE_ECHO,
            'db_host': self.DB_HOST,
            'db_port': self.DB_PORT,
            'db_name': self.DB_NAME,
            
            # Vector
            'embedding_model': self.EMBEDDING_MODEL,
            'embedding_dimension': self.EMBEDDING_DIMENSION,
            
            # Cache
            'cache_enabled': self.CACHE_ENABLED,
            'cache_ttl_hours': self.CACHE_TTL_HOURS,
            'redis_enabled': self.REDIS_ENABLED,
            
            # Features
            'enable_encryption': self.ENABLE_ENCRYPTION,
            'enable_auto_vector_ingestion': self.ENABLE_AUTO_VECTOR_INGESTION,
            'enable_gdpr': self.ENABLE_GDPR,
            
            # Logging
            'log_level': self.LOG_LEVEL,
            
            # API Keys
            'api_keys_configured': self.validate_api_keys(),
            
            # LLM Service Configuration
            'llm_default_provider': self.LLM_DEFAULT_PROVIDER,
            'llm_enable_fallback': self.LLM_ENABLE_FALLBACK,
            'llm_fallback_order': self.LLM_FALLBACK_ORDER,
            'llm_configured_providers': self.get_configured_llm_providers(),
            'llm_has_any_provider': self.has_any_llm_provider(),
            'llm_default_max_tokens': self.LLM_DEFAULT_MAX_TOKENS,
            'llm_default_temperature': self.LLM_DEFAULT_TEMPERATURE,
            
            # Decisioning
            'decision_config_dirs': [str(p) for p in self.get_decision_config_dirs()],
            'decision_auto_load': self.DECISION_AUTO_LOAD,
            'decision_cache_enabled': self.DECISION_CACHE_ENABLED,
            'decision_trace_enabled': self.DECISION_TRACE_ENABLED,
            
            # Scheduler
            'scheduler_config_dir': str(self.SCHEDULER_CONFIG_DIR),
            'scheduler_auto_discover': self.SCHEDULER_AUTO_DISCOVER,
            
            # Integration Factory
            'integration_credentials_dirs': [str(p) for p in self.get_integration_credentials_dirs()],
            'integration_definitions_dirs': [str(p) for p in self.get_integration_definitions_dirs()],
            'integration_auto_load': self.INTEGRATION_AUTO_LOAD,
            'integration_cache_enabled': self.INTEGRATION_CACHE_ENABLED,
            'integration_circuit_breaker_enabled': self.INTEGRATION_CIRCUIT_BREAKER_ENABLED,
            'integration_status': self.validate_integration_config(),
            
            # Communication
            'email_provider': self.EMAIL_PROVIDER,
            'sms_provider': self.SMS_PROVIDER,
            'push_provider': self.PUSH_PROVIDER,
            'communication_status': self.get_communication_status(),
        }


# Create singleton instance
config = Config()
