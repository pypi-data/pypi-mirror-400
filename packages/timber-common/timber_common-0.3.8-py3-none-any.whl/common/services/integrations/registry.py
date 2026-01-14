# common/services/integrations/registry.py
"""
Integration Registry

Singleton registry for loading, storing, and managing integration definitions
and credentials. Loads from YAML files on startup and provides lookup methods.
"""

from __future__ import annotations
import os
import re
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .models import (
    IntegrationDefinition, 
    Credential, 
    AuthType,
    CircuitBreakerState,
    CircuitState,
)

logger = logging.getLogger(__name__)


class IntegrationRegistry:
    """
    Singleton registry for integrations and credentials.
    
    Provides:
    - YAML loading with environment variable substitution
    - Credential lookup (with security isolation)
    - Integration definition lookup
    - Circuit breaker state management
    - Hot-reload capabilities
    """
    
    _instance: Optional['IntegrationRegistry'] = None
    
    # Storage
    _credentials: Dict[str, Credential] = {}
    _credential_groups: Dict[str, List[str]] = {}
    _integrations: Dict[str, IntegrationDefinition] = {}
    _circuit_breakers: Dict[str, CircuitBreakerState] = {}
    
    # Metadata
    _loaded_credential_files: Set[str] = set()
    _loaded_integration_files: Set[str] = set()
    _initialized: bool = False
    _last_reload: Optional[datetime] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IntegrationRegistry, cls).__new__(cls)
            cls._instance._init_instance()
        return cls._instance
    
    def _init_instance(self):
        """Initialize instance variables."""
        self._credentials = {}
        self._credential_groups = {}
        self._integrations = {}
        self._circuit_breakers = {}
        self._loaded_credential_files = set()
        self._loaded_integration_files = set()
        self._initialized = False
        self._last_reload = None
        logger.info("IntegrationRegistry instance created")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def initialize(
        self,
        credential_paths: Optional[List[str]] = None,
        integration_paths: Optional[List[str]] = None,
        config_path: Optional[str] = None,
        base_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initialize the registry by loading configuration files.
        
        Args:
            credential_paths: List of paths to credential YAML files
            integration_paths: List of paths to integration definition YAML files
            config_path: Path to main integration_config.yaml (overrides other paths)
            base_dir: Base directory for relative paths
            
        Returns:
            Summary of loaded items
        """
        base_dir = base_dir or os.getcwd()
        
        # If config path provided, load paths from it
        if config_path:
            config = self._load_yaml_file(config_path, base_dir)
            if config and 'integration_factory' in config:
                paths = config['integration_factory'].get('paths', {})
                credential_paths = credential_paths or paths.get('credentials', [])
                integration_paths = integration_paths or paths.get('definitions', [])
        
        # Default paths if none provided
        credential_paths = credential_paths or ['config/integrations/credentials/']
        integration_paths = integration_paths or ['config/integrations/definitions/']
        
        summary = {
            'credentials_loaded': 0,
            'credential_groups_loaded': 0,
            'integrations_loaded': 0,
            'errors': [],
        }
        
        # Load credentials first (integrations depend on them)
        for path in credential_paths:
            try:
                count = self._load_credentials_from_path(path, base_dir)
                summary['credentials_loaded'] += count
            except Exception as e:
                error_msg = f"Failed to load credentials from {path}: {e}"
                logger.error(error_msg)
                summary['errors'].append(error_msg)
        
        # Load integrations
        for path in integration_paths:
            try:
                count = self._load_integrations_from_path(path, base_dir)
                summary['integrations_loaded'] += count
            except Exception as e:
                error_msg = f"Failed to load integrations from {path}: {e}"
                logger.error(error_msg)
                summary['errors'].append(error_msg)
        
        summary['credential_groups_loaded'] = len(self._credential_groups)
        
        self._initialized = True
        self._last_reload = datetime.utcnow()
        
        logger.info(
            f"IntegrationRegistry initialized: "
            f"{summary['credentials_loaded']} credentials, "
            f"{summary['integrations_loaded']} integrations"
        )
        
        return summary
    
    def reload(self) -> Dict[str, Any]:
        """Reload all configurations from previously loaded files."""
        # Store current circuit breaker states
        saved_breakers = self._circuit_breakers.copy()
        
        # Clear and reinitialize
        self._credentials.clear()
        self._credential_groups.clear()
        self._integrations.clear()
        
        credential_files = list(self._loaded_credential_files)
        integration_files = list(self._loaded_integration_files)
        
        self._loaded_credential_files.clear()
        self._loaded_integration_files.clear()
        
        summary = {
            'credentials_loaded': 0,
            'integrations_loaded': 0,
            'errors': [],
        }
        
        # Reload credential files
        for file_path in credential_files:
            try:
                count = self._load_credentials_file(file_path)
                summary['credentials_loaded'] += count
            except Exception as e:
                summary['errors'].append(f"Failed to reload {file_path}: {e}")
        
        # Reload integration files
        for file_path in integration_files:
            try:
                count = self._load_integrations_file(file_path)
                summary['integrations_loaded'] += count
            except Exception as e:
                summary['errors'].append(f"Failed to reload {file_path}: {e}")
        
        # Restore circuit breaker states
        self._circuit_breakers = saved_breakers
        self._last_reload = datetime.utcnow()
        
        logger.info(f"Registry reloaded: {summary}")
        return summary
    
    # =========================================================================
    # YAML LOADING
    # =========================================================================
    
    def _load_yaml_file(self, path: str, base_dir: str = "") -> Optional[Dict]:
        """Load a YAML file with environment variable substitution."""
        full_path = Path(base_dir) / path if base_dir else Path(path)
        
        if not full_path.exists():
            logger.debug(f"YAML file not found: {full_path}")
            return None
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Substitute environment variables: ${VAR_NAME} or ${VAR_NAME:default}
            content = self._substitute_env_vars(content)
            
            return yaml.safe_load(content)
        except Exception as e:
            logger.error(f"Failed to load YAML file {full_path}: {e}")
            raise
    
    def _substitute_env_vars(self, content: str) -> str:
        """
        Substitute environment variables in content.
        
        Supports:
        - ${VAR_NAME} - Required, raises if not found
        - ${VAR_NAME:default} - With default value
        - ${VAR_NAME:} - Empty string default
        """
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        
        def replace(match):
            var_name = match.group(1)
            default = match.group(2)
            
            value = os.environ.get(var_name)
            
            if value is not None:
                return value
            elif default is not None:
                return default
            else:
                # Keep the placeholder for later resolution or error
                logger.warning(f"Environment variable not found: {var_name}")
                return match.group(0)
        
        return re.sub(pattern, replace, content)
    
    def _load_credentials_from_path(self, path: str, base_dir: str) -> int:
        """Load credentials from a path (file or directory)."""
        full_path = Path(base_dir) / path
        count = 0
        
        if full_path.is_file():
            count = self._load_credentials_file(str(full_path))
        elif full_path.is_dir():
            for yaml_file in full_path.glob("*.yaml"):
                count += self._load_credentials_file(str(yaml_file))
            for yml_file in full_path.glob("*.yml"):
                count += self._load_credentials_file(str(yml_file))
        else:
            logger.debug(f"Credentials path not found: {full_path}")
        
        return count
    
    def _load_credentials_file(self, file_path: str) -> int:
        """Load credentials from a single YAML file."""
        data = self._load_yaml_file(file_path)
        if not data:
            return 0
        
        count = 0
        
        # Load credentials
        for cred_data in data.get('credentials', []):
            try:
                credential = Credential(**cred_data)
                self._credentials[credential.id] = credential
                count += 1
                logger.debug(f"Loaded credential: {credential.id}")
            except Exception as e:
                logger.error(f"Failed to parse credential in {file_path}: {e}")
        
        # Load credential groups
        for group in data.get('credential_groups', []):
            group_id = group.get('id')
            cred_ids = group.get('credentials', [])
            if group_id:
                self._credential_groups[group_id] = cred_ids
                logger.debug(f"Loaded credential group: {group_id}")
        
        self._loaded_credential_files.add(file_path)
        return count
    
    def _load_integrations_from_path(self, path: str, base_dir: str) -> int:
        """Load integrations from a path (file or directory)."""
        full_path = Path(base_dir) / path
        count = 0
        
        if full_path.is_file():
            count = self._load_integrations_file(str(full_path))
        elif full_path.is_dir():
            for yaml_file in full_path.glob("*.yaml"):
                count += self._load_integrations_file(str(yaml_file))
            for yml_file in full_path.glob("*.yml"):
                count += self._load_integrations_file(str(yml_file))
        else:
            logger.debug(f"Integrations path not found: {full_path}")
        
        return count
    
    def _load_integrations_file(self, file_path: str) -> int:
        """Load integrations from a single YAML file."""
        data = self._load_yaml_file(file_path)
        if not data:
            return 0
        
        count = 0
        
        for int_data in data.get('integrations', []):
            try:
                integration = IntegrationDefinition(**int_data)
                
                # Validate credential reference exists
                if integration.authentication:
                    cred_ref = integration.authentication.credential_ref
                    if cred_ref not in self._credentials:
                        logger.warning(
                            f"Integration {integration.id} references "
                            f"unknown credential: {cred_ref}"
                        )
                
                self._integrations[integration.id] = integration
                count += 1
                logger.debug(f"Loaded integration: {integration.id}")
                
            except Exception as e:
                logger.error(f"Failed to parse integration in {file_path}: {e}")
        
        self._loaded_integration_files.add(file_path)
        return count
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    def get_credential(self, credential_id: str) -> Optional[Credential]:
        """Get a credential by ID."""
        return self._credentials.get(credential_id)
    
    def get_credentials_for_group(self, group_id: str) -> List[Credential]:
        """Get all credentials in a group."""
        cred_ids = self._credential_groups.get(group_id, [])
        return [
            self._credentials[cid] 
            for cid in cred_ids 
            if cid in self._credentials
        ]
    
    def get_integration(self, integration_id: str) -> Optional[IntegrationDefinition]:
        """Get an integration by ID."""
        return self._integrations.get(integration_id)
    
    def get_integration_credential(
        self, 
        integration_id: str
    ) -> Optional[Credential]:
        """Get the credential for an integration."""
        integration = self.get_integration(integration_id)
        if not integration or not integration.authentication:
            return None
        return self.get_credential(integration.authentication.credential_ref)
    
    def list_integrations(
        self, 
        enabled_only: bool = True,
        tags: Optional[List[str]] = None,
    ) -> List[IntegrationDefinition]:
        """List integrations with optional filtering."""
        integrations = list(self._integrations.values())
        
        if enabled_only:
            integrations = [i for i in integrations if i.enabled]
        
        if tags:
            integrations = [
                i for i in integrations 
                if any(t in i.tags for t in tags)
            ]
        
        return integrations
    
    def list_credentials(self) -> List[str]:
        """List credential IDs (not the credentials themselves for security)."""
        return list(self._credentials.keys())
    
    # =========================================================================
    # CIRCUIT BREAKER
    # =========================================================================
    
    def get_circuit_breaker(
        self, 
        integration_id: str
    ) -> CircuitBreakerState:
        """Get or create circuit breaker state for an integration."""
        if integration_id not in self._circuit_breakers:
            self._circuit_breakers[integration_id] = CircuitBreakerState(
                integration_id=integration_id
            )
        return self._circuit_breakers[integration_id]
    
    def record_success(self, integration_id: str) -> CircuitBreakerState:
        """Record a successful call for circuit breaker."""
        cb = self.get_circuit_breaker(integration_id)
        cb.last_success_time = datetime.utcnow()
        cb.success_count += 1
        cb.failure_count = 0
        
        if cb.state == CircuitState.HALF_OPEN:
            if cb.success_count >= cb.success_threshold:
                cb.state = CircuitState.CLOSED
                cb.success_count = 0
                logger.info(f"Circuit breaker CLOSED for {integration_id}")
        
        return cb
    
    def record_failure(self, integration_id: str) -> CircuitBreakerState:
        """Record a failed call for circuit breaker."""
        cb = self.get_circuit_breaker(integration_id)
        cb.last_failure_time = datetime.utcnow()
        cb.failure_count += 1
        cb.success_count = 0
        
        if cb.state == CircuitState.CLOSED:
            if cb.failure_count >= cb.failure_threshold:
                cb.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker OPEN for {integration_id}")
        elif cb.state == CircuitState.HALF_OPEN:
            cb.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker re-OPEN for {integration_id}")
        
        return cb
    
    def is_circuit_open(self, integration_id: str) -> bool:
        """Check if circuit breaker is open (blocking calls)."""
        cb = self.get_circuit_breaker(integration_id)
        
        if cb.state == CircuitState.CLOSED:
            return False
        
        if cb.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if cb.last_failure_time:
                from datetime import timedelta
                elapsed = datetime.utcnow() - cb.last_failure_time
                if elapsed > timedelta(seconds=cb.timeout_seconds):
                    cb.state = CircuitState.HALF_OPEN
                    cb.success_count = 0
                    logger.info(f"Circuit breaker HALF_OPEN for {integration_id}")
                    return False
            return True
        
        return False  # HALF_OPEN allows calls
    
    # =========================================================================
    # STATUS & METADATA
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get registry status."""
        return {
            'initialized': self._initialized,
            'last_reload': self._last_reload.isoformat() if self._last_reload else None,
            'credentials_count': len(self._credentials),
            'credential_groups_count': len(self._credential_groups),
            'integrations_count': len(self._integrations),
            'enabled_integrations': len([i for i in self._integrations.values() if i.enabled]),
            'circuit_breakers': {
                k: v.state.value 
                for k, v in self._circuit_breakers.items()
            },
            'loaded_files': {
                'credentials': list(self._loaded_credential_files),
                'integrations': list(self._loaded_integration_files),
            }
        }
    
    def has_integration(self, integration_id: str) -> bool:
        """Check if an integration exists."""
        return integration_id in self._integrations
    
    def is_initialized(self) -> bool:
        """Check if registry is initialized."""
        return self._initialized


# Singleton instance
integration_registry = IntegrationRegistry()


# Convenience functions
def get_integration(integration_id: str) -> Optional[IntegrationDefinition]:
    """Get an integration from the registry."""
    return integration_registry.get_integration(integration_id)


def get_credential(credential_id: str) -> Optional[Credential]:
    """Get a credential from the registry."""
    return integration_registry.get_credential(credential_id)


def list_integrations(**kwargs) -> List[IntegrationDefinition]:
    """List integrations from the registry."""
    return integration_registry.list_integrations(**kwargs)
