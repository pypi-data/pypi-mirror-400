# timber/common/config/model_loader.py
"""
Model Configuration Loader - ENHANCED VERSION

Loads model definitions from YAML configuration files with dependency resolution.
Supports 'depends' attribute to control loading order.
"""

import yaml
from pathlib import Path
from typing import List, Optional, Dict, Set
import logging

from ..models.factory import model_factory
from ..models.registry import model_registry

logger = logging.getLogger(__name__)


class ModelConfigLoader:
    """
    Loads and creates models from YAML configuration files.
    
    Supports dependency-based loading order via 'depends' attribute in YAML files.
    
    Example YAML with dependencies:
        version: "1.0.0"
        depends: ["00_association_tables.yaml"]  # Load this first
        models:
          - name: MyModel
            ...
    """
    
    def __init__(self):
        self.loaded_configs: List[str] = []
        self.loaded_models: List[str] = []
    
    def load_from_file(self, config_path: str) -> List:
        """
        Load models from a single YAML config file.
        
        Args:
            config_path: Path to YAML configuration file
        
        Returns:
            List of created model classes
        """
        logger.info(f"Loading models from: {config_path}")
        
        try:
            models = model_factory.create_model_from_config_file(config_path)
            
            self.loaded_configs.append(config_path)
            self.loaded_models.extend([m.__name__ for m in models])
            
            logger.info(f"Loaded {len(models)} models from {config_path}")
            return models
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise
    
    def _get_file_dependencies(self, config_file: Path) -> List[str]:
        """
        Get dependencies from a YAML config file.
        
        Args:
            config_file: Path to config file
        
        Returns:
            List of dependency filenames (not full paths)
        """
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                return []
            
            # Check for 'depends' or 'dependencies' key
            depends = config_data.get('depends', config_data.get('dependencies', []))
            
            if isinstance(depends, str):
                depends = [depends]
            
            return depends if isinstance(depends, list) else []
            
        except Exception as e:
            logger.warning(f"Could not read dependencies from {config_file}: {e}")
            return []
    
    def _topological_sort(
        self,
        files: List[Path],
        config_dir: Path
    ) -> List[Path]:
        """
        Sort config files based on dependencies using topological sort.
        
        Args:
            files: List of config file paths
            config_dir: Base directory for resolving relative dependencies
        
        Returns:
            Sorted list of config files
        """
        # Build dependency graph
        file_deps: Dict[str, List[str]] = {}
        file_map: Dict[str, Path] = {}
        
        for file_path in files:
            filename = file_path.name
            file_map[filename] = file_path
            file_deps[filename] = self._get_file_dependencies(file_path)
        
        # Topological sort using Kahn's algorithm
        in_degree: Dict[str, int] = {name: 0 for name in file_map.keys()}
        
        for filename, deps in file_deps.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[filename] += 1
        
        # Queue of files with no dependencies
        queue = [name for name, degree in in_degree.items() if degree == 0]
        sorted_files = []
        
        while queue:
            # Sort queue alphabetically for deterministic ordering
            queue.sort()
            
            filename = queue.pop(0)
            sorted_files.append(file_map[filename])
            
            # Reduce in-degree for files that depend on this one
            for other_file, deps in file_deps.items():
                if filename in deps:
                    in_degree[other_file] -= 1
                    if in_degree[other_file] == 0:
                        queue.append(other_file)
        
        # Check for circular dependencies
        if len(sorted_files) != len(files):
            remaining = set(file_map.keys()) - {f.name for f in sorted_files}
            logger.error(f"Circular dependency detected in files: {remaining}")
            # Fall back to alphabetical sort
            logger.warning("Falling back to alphabetical sort")
            return sorted(files)
        
        logger.debug(f"File load order (dependency-sorted): {[f.name for f in sorted_files]}")
        return sorted_files
    
    def load_from_directory(
        self,
        directory_path: str,
        pattern: str = "*.yaml",
        recursive: bool = False,
        use_dependencies: bool = True
    ) -> List:
        """
        Load all model configs from a directory.
        
        Args:
            directory_path: Path to directory containing config files
            pattern: Glob pattern for config files (default: *.yaml)
            recursive: If True, search subdirectories
            use_dependencies: If True, sort files by dependencies (default: True)
        
        Returns:
            List of all created model classes
        """
        config_dir = Path(directory_path)
        
        if not config_dir.exists():
            logger.warning(f"Config directory does not exist: {directory_path}")
            return []
        
        logger.info(f"Loading models from directory: {directory_path}")
        
        all_models = []
        
        # Find all config files
        if recursive:
            config_files = list(config_dir.rglob(pattern))
        else:
            config_files = list(config_dir.glob(pattern))
        
        if not config_files:
            logger.warning(f"No config files found in {directory_path}")
            return []
        
        # Sort files by dependencies or alphabetically
        if use_dependencies:
            sorted_files = self._topological_sort(config_files, config_dir)
        else:
            sorted_files = sorted(config_files)
        
        logger.info(f"Loading {len(sorted_files)} config files in order:")
        for idx, file_path in enumerate(sorted_files, 1):
            logger.info(f"  {idx}. {file_path.name}")
        
        # Load each config file in order
        for config_file in sorted_files:
            try:
                models = self.load_from_file(str(config_file))
                all_models.extend(models)
            except Exception as e:
                logger.error(f"Error loading {config_file}: {e}")
                # Continue loading other files rather than stopping
                continue
        
        logger.info(f"Loaded {len(all_models)} total models from {directory_path}")
        return all_models
    
    def load_from_multiple_directories(self, directories: List[str]) -> List:
        """
        Load models from multiple directories.
        
        Args:
            directories: List of directory paths
        
        Returns:
            List of all created model classes
        """
        all_models = []
        
        for directory in directories:
            models = self.load_from_directory(directory)
            all_models.extend(models)
        
        return all_models
    
    def get_loaded_configs(self) -> List[str]:
        """Get list of loaded configuration file paths."""
        return self.loaded_configs
    
    def get_loaded_models(self) -> List[str]:
        """Get list of loaded model names."""
        return self.loaded_models
    
    def reload(self, config_path: str):
        """
        Reload models from a configuration file.
        
        Args:
            config_path: Path to config file to reload
        """
        logger.info(f"Reloading models from {config_path}")
        
        # Load the config again
        models = self.load_from_file(config_path)
        
        logger.info(f"Reloaded {len(models)} models from {config_path}")
        return models


# Singleton instance
model_loader = ModelConfigLoader()