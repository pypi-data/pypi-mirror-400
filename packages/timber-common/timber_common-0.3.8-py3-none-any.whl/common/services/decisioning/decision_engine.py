# common/services/decisioning/decision_engine.py
"""
DMN-Inspired Decision Engine

A comprehensive decisioning service supporting:
- Decision Tables with multiple hit policies
- FEEL-like expression evaluation
- Decision Requirement Graphs (DRG)
- Business Knowledge Models

Supports multiple input formats:
- YAML (native format)
- DMN XML (standard OMG format)
- CSV (simple decision tables)

All formats are converted to internal YAML representation for consistent execution.

Configuration (via environment or config):
    DECISION_CONFIG_DIRS: Comma-separated directories to scan for decision files
                          Default: config/decisioning,data/decisions
    DECISION_AUTO_LOAD: Auto-load decisions on initialization (default: True)
    DECISION_CACHE_ENABLED: Enable caching of evaluation results (default: True)
    DECISION_CACHE_TTL_SECONDS: Cache TTL in seconds (default: 300)
    DECISION_TRACE_ENABLED: Enable evaluation tracing (default: False)
    DECISION_LOG_EVALUATIONS: Log evaluations to database (default: False)

Usage:
    from common.services.decisioning import decision_engine
    
    # Initialize and auto-load from configured directories
    await decision_engine.initialize()
    
    # Or load manually
    await decision_engine.load_from_file("config/decisioning/pricing.yaml")
    
    # Evaluate
    result = await decision_engine.evaluate(
        decision_id="loan_approval",
        inputs={
            'applicant_age': 35,
            'credit_score': 720,
            'annual_income': 85000,
            'loan_amount': 250000,
        }
    )

Architecture:
    External Formats (DMN, CSV) → Converters → YAML Format → Decision Engine → Result
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timezone
import uuid

from .models import (
    HitPolicy, DecisionType, ComparisonOperator,
    InputDefinition, OutputDefinition, RuleCondition, Rule,
    DecisionTable, Expression, DecisionNode, DecisionGraph,
    EvaluationResult,
)
from .expression_engine import ExpressionEngine
from .table_evaluator import DecisionTableEvaluator
from .graph_evaluator import DecisionGraphEvaluator

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Main decision engine service.
    
    Manages decision definitions and provides evaluation API.
    Integrates with Timber config for directory and settings management.
    """
    
    def __init__(self):
        self._decisions: Dict[str, Union[DecisionTable, Expression, DecisionGraph]] = {}
        self._expression_engine = ExpressionEngine()
        self._table_evaluator = DecisionTableEvaluator(self._expression_engine)
        self._graph_evaluator = DecisionGraphEvaluator(
            self._table_evaluator, self._expression_engine
        )
        self._db = None
        self._config = None
        self._initialized = False
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        logger.info("⚖️ DecisionEngine initialized")
    
    @property
    def config(self):
        """Lazy-load Timber config."""
        if self._config is None:
            try:
                from common.utils.config import config
                self._config = config
            except ImportError:
                # Config not available, use defaults
                self._config = None
        return self._config
    
    # =========================================================================
    # CONFIGURATION PROPERTIES
    # =========================================================================
    
    @property
    def auto_load_enabled(self) -> bool:
        """Check if auto-loading is enabled."""
        if self.config:
            return self.config.DECISION_AUTO_LOAD
        return os.getenv("DECISION_AUTO_LOAD", "True").lower() == "true"
    
    @property
    def cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        if self.config:
            return self.config.DECISION_CACHE_ENABLED
        return os.getenv("DECISION_CACHE_ENABLED", "True").lower() == "true"
    
    @property
    def cache_ttl_seconds(self) -> int:
        """Get cache TTL in seconds."""
        if self.config:
            return self.config.DECISION_CACHE_TTL_SECONDS
        return int(os.getenv("DECISION_CACHE_TTL_SECONDS", "300"))
    
    @property
    def trace_enabled(self) -> bool:
        """Check if tracing is enabled globally."""
        if self.config:
            return self.config.DECISION_TRACE_ENABLED
        return os.getenv("DECISION_TRACE_ENABLED", "False").lower() == "true"
    
    @property
    def log_evaluations(self) -> bool:
        """Check if evaluation logging is enabled."""
        if self.config:
            return self.config.DECISION_LOG_EVALUATIONS
        return os.getenv("DECISION_LOG_EVALUATIONS", "False").lower() == "true"
    
    def get_config_dirs(self) -> List[Path]:
        """Get list of directories to scan for decision files."""
        if self.config:
            return self.config.get_decision_config_dirs()
        
        # Fallback: parse from environment
        dirs_str = os.getenv("DECISION_CONFIG_DIRS", "config/decisioning,data/decisions")
        dirs = []
        for dir_str in dirs_str.split(','):
            dir_path = Path(dir_str.strip())
            if dir_path.exists():
                dirs.append(dir_path)
        return dirs
    
    def get_config_paths(self, pattern: str = "*.yaml") -> List[Path]:
        """Get list of decision file paths from all configured directories."""
        if self.config:
            return self.config.get_decision_config_paths(pattern)
        
        # Fallback: manual scan
        paths = []
        for config_dir in self.get_config_dirs():
            if config_dir.exists():
                paths.extend(config_dir.glob(f'**/{pattern}'))
        return sorted(paths)
    
    @property
    def db(self):
        """Lazy-load database service for logging."""
        if self._db is None and self.log_evaluations:
            try:
                from common.services import db_service
                self._db = db_service
            except ImportError:
                pass
        return self._db
    
    @property
    def expression_engine(self) -> ExpressionEngine:
        """Access to expression engine for custom functions."""
        return self._expression_engine
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    async def initialize(self, auto_load: Optional[bool] = None) -> Dict[str, Any]:
        """
        Initialize the decision engine.
        
        Optionally auto-loads decisions from all configured directories.
        
        Args:
            auto_load: Override auto-load setting (None uses config)
            
        Returns:
            Dict with initialization status and loaded decisions
        """
        if self._initialized:
            return {
                "status": "already_initialized",
                "decisions_loaded": len(self._decisions),
            }
        
        should_auto_load = auto_load if auto_load is not None else self.auto_load_enabled
        
        result = {
            "status": "initialized",
            "auto_load": should_auto_load,
            "config_dirs": [str(p) for p in self.get_config_dirs()],
            "decisions_loaded": [],
            "errors": [],
        }
        
        if should_auto_load:
            loaded = await self.load_from_config_dirs()
            result["decisions_loaded"] = loaded["decisions"]
            result["errors"] = loaded["errors"]
        
        self._initialized = True
        logger.info(f"⚖️ DecisionEngine initialized: {len(result['decisions_loaded'])} decisions loaded")
        
        return result
    
    async def load_from_config_dirs(
        self,
        yaml_pattern: str = "*.yaml",
        dmn_pattern: str = "*.dmn",
        csv_pattern: str = "*.csv",
    ) -> Dict[str, Any]:
        """
        Load all decision files from configured directories.
        
        Scans all directories specified in DECISION_CONFIG_DIRS and loads:
        - YAML files (*.yaml)
        - DMN files (*.dmn) 
        - CSV files (*.csv)
        
        Args:
            yaml_pattern: Glob pattern for YAML files
            dmn_pattern: Glob pattern for DMN files
            csv_pattern: Glob pattern for CSV files
            
        Returns:
            Dict with lists of loaded decisions and errors
        """
        result = {
            "decisions": [],
            "errors": [],
            "by_directory": {},
        }
        
        for config_dir in self.get_config_dirs():
            dir_result = {
                "yaml": [],
                "dmn": [],
                "csv": [],
                "errors": [],
            }
            
            # Load YAML files
            for file_path in config_dir.glob(f'**/{yaml_pattern}'):
                try:
                    decision_ids = await self.load_from_file(str(file_path))
                    dir_result["yaml"].extend(decision_ids)
                    result["decisions"].extend(decision_ids)
                except Exception as e:
                    error = f"Failed to load {file_path}: {e}"
                    logger.error(error)
                    dir_result["errors"].append(error)
                    result["errors"].append(error)
            
            # Load DMN files
            for file_path in config_dir.glob(f'**/{dmn_pattern}'):
                try:
                    decision_ids = await self.load_from_dmn(str(file_path))
                    dir_result["dmn"].extend(decision_ids)
                    result["decisions"].extend(decision_ids)
                except Exception as e:
                    error = f"Failed to load DMN {file_path}: {e}"
                    logger.error(error)
                    dir_result["errors"].append(error)
                    result["errors"].append(error)
            
            # Load CSV files (need to derive decision_id from filename)
            for file_path in config_dir.glob(f'**/{csv_pattern}'):
                try:
                    decision_id = file_path.stem  # filename without extension
                    loaded_id = await self.load_from_csv(str(file_path), decision_id)
                    dir_result["csv"].append(loaded_id)
                    result["decisions"].append(loaded_id)
                except Exception as e:
                    error = f"Failed to load CSV {file_path}: {e}"
                    logger.error(error)
                    dir_result["errors"].append(error)
                    result["errors"].append(error)
            
            result["by_directory"][str(config_dir)] = dir_result
        
        logger.info(
            f"Loaded {len(result['decisions'])} decisions from "
            f"{len(self.get_config_dirs())} directories"
        )
        
        return result
    
    # =========================================================================
    # PUBLIC API - EVALUATION
    # =========================================================================
    
    async def evaluate(
        self,
        decision_id: str,
        inputs: Dict[str, Any],
        trace: Optional[bool] = None,
        use_cache: Optional[bool] = None,
    ) -> EvaluationResult:
        """
        Evaluate a loaded decision.
        
        Args:
            decision_id: ID of the decision to evaluate
            inputs: Input values
            trace: Whether to include execution trace (None uses config)
            use_cache: Whether to use cached results (None uses config)
            
        Returns:
            EvaluationResult
        """
        # Use config defaults if not specified
        should_trace = trace if trace is not None else self.trace_enabled
        should_cache = use_cache if use_cache is not None else self.cache_enabled
        
        # Check cache
        if should_cache:
            cache_key = self._make_cache_key(decision_id, inputs)
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached
        
        if decision_id not in self._decisions:
            return EvaluationResult(
                decision_id=decision_id,
                success=False,
                errors=[f"Decision not found: {decision_id}"],
            )
        
        decision = self._decisions[decision_id]
        
        if isinstance(decision, DecisionTable):
            result = self._table_evaluator.evaluate(decision, inputs, should_trace)
        elif isinstance(decision, Expression):
            try:
                value = self._expression_engine.evaluate(decision.expression, inputs)
                output_name = decision.output.name if decision.output else 'result'
                result = EvaluationResult(
                    decision_id=decision_id,
                    success=True,
                    outputs={output_name: value},
                )
            except Exception as e:
                result = EvaluationResult(
                    decision_id=decision_id,
                    success=False,
                    errors=[str(e)],
                )
        elif isinstance(decision, DecisionGraph):
            # For graphs, find root decisions (not depended on by others)
            root_decisions = [
                d for d in decision.decisions.values()
                if not any(d.id in other.dependencies for other in decision.decisions.values())
            ]
            if root_decisions:
                result = self._graph_evaluator.evaluate(
                    decision, root_decisions[0].id, inputs, should_trace
                )
            else:
                result = EvaluationResult(
                    decision_id=decision_id,
                    success=False,
                    errors=["No root decision found in graph"],
                )
        else:
            result = EvaluationResult(
                decision_id=decision_id,
                success=False,
                errors=[f"Unknown decision type"],
            )
        
        # Cache successful results
        if should_cache and result.success:
            self._set_cached(cache_key, result)
        
        # Log evaluation
        if self.log_evaluations:
            await self._log_evaluation(decision_id, inputs, result)
        
        return result
    
    async def evaluate_decision_in_graph(
        self,
        graph_id: str,
        decision_id: str,
        inputs: Dict[str, Any],
        trace: bool = False,
    ) -> EvaluationResult:
        """
        Evaluate a specific decision within a graph.
        
        Args:
            graph_id: ID of the decision graph
            decision_id: ID of the specific decision to evaluate
            inputs: Input values
            trace: Whether to include execution trace
            
        Returns:
            EvaluationResult
        """
        if graph_id not in self._decisions:
            return EvaluationResult(
                decision_id=decision_id,
                success=False,
                errors=[f"Decision graph not found: {graph_id}"],
            )
        
        graph = self._decisions[graph_id]
        if not isinstance(graph, DecisionGraph):
            return EvaluationResult(
                decision_id=decision_id,
                success=False,
                errors=[f"{graph_id} is not a decision graph"],
            )
        
        return self._graph_evaluator.evaluate(graph, decision_id, inputs, trace)
    
    def evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """
        Evaluate a standalone expression.
        
        Args:
            expression: Expression string
            context: Variable context
            
        Returns:
            Evaluated result
        """
        return self._expression_engine.evaluate(expression, context)
    
    # =========================================================================
    # PUBLIC API - MANAGEMENT
    # =========================================================================
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a custom function for use in expressions."""
        self._expression_engine.register_function(name, func)
    
    def get_decision(self, decision_id: str) -> Optional[Union[DecisionTable, Expression, DecisionGraph]]:
        """Get a loaded decision by ID."""
        return self._decisions.get(decision_id)
    
    def list_decisions(self) -> List[Dict[str, Any]]:
        """List all loaded decisions."""
        return [
            {
                'id': d.id,
                'name': d.name,
                'type': type(d).__name__,
                'description': getattr(d, 'description', None),
            }
            for d in self._decisions.values()
        ]
    
    def unload_decision(self, decision_id: str) -> bool:
        """Unload a decision."""
        if decision_id in self._decisions:
            del self._decisions[decision_id]
            return True
        return False
    
    def clear(self) -> None:
        """Unload all decisions."""
        self._decisions.clear()
    
    # =========================================================================
    # LOADING
    # =========================================================================
    
    async def load_from_file(self, path: str) -> List[str]:
        """
        Load decisions from a YAML file.
        
        Args:
            path: Path to YAML file
            
        Returns:
            List of loaded decision IDs
        """
        from common.utils.decisioning import yaml_parser
        
        decisions = yaml_parser.parse_file(path)
        loaded = []
        
        for decision in decisions:
            self._decisions[decision.id] = decision
            loaded.append(decision.id)
            logger.info(f"Loaded decision: {decision.id} ({type(decision).__name__})")
        
        return loaded
    
    async def load_from_dmn(self, path: str) -> List[str]:
        """
        Load decisions from a DMN XML file.
        
        Args:
            path: Path to DMN file
            
        Returns:
            List of loaded decision IDs
        """
        from common.utils.decisioning import dmn_parser
        
        decisions = dmn_parser.parse_file(path)
        loaded = []
        
        for decision in decisions:
            self._decisions[decision.id] = decision
            loaded.append(decision.id)
            logger.info(f"Loaded decision from DMN: {decision.id}")
        
        return loaded
    
    async def load_from_csv(
        self,
        path: str,
        decision_id: str,
        decision_name: Optional[str] = None,
        hit_policy: HitPolicy = HitPolicy.FIRST,
    ) -> str:
        """
        Load a decision table from CSV.
        
        Args:
            path: Path to CSV file
            decision_id: ID to assign to the decision
            decision_name: Name for the decision
            hit_policy: Hit policy to use
            
        Returns:
            Decision ID
        """
        from common.utils.decisioning import csv_parser
        
        table = csv_parser.parse_file(path, decision_id, decision_name, hit_policy)
        self._decisions[table.id] = table
        logger.info(f"Loaded decision from CSV: {table.id}")
        
        return table.id
    
    async def load_from_dict(self, data: Dict[str, Any]) -> List[str]:
        """
        Load decisions from a dictionary (parsed YAML).
        
        Args:
            data: Dictionary with decision definitions
            
        Returns:
            List of loaded decision IDs
        """
        from common.utils.decisioning import yaml_parser
        
        decisions = yaml_parser.parse_dict(data)
        loaded = []
        
        for decision in decisions:
            self._decisions[decision.id] = decision
            loaded.append(decision.id)
        
        return loaded
    
    async def load_directory(self, directory: str, pattern: str = "*.yaml") -> List[str]:
        """
        Load all decision files from a directory.
        
        Args:
            directory: Directory path
            pattern: File pattern to match
            
        Returns:
            List of loaded decision IDs
        """
        loaded = []
        path = Path(directory)
        
        for file_path in path.glob(pattern):
            try:
                decision_ids = await self.load_from_file(str(file_path))
                loaded.extend(decision_ids)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        return loaded
    
    # =========================================================================
    # EXPORT
    # =========================================================================
    
    def export_to_yaml(self, decision_id: str) -> str:
        """
        Export a decision to YAML format.
        
        Args:
            decision_id: Decision to export
            
        Returns:
            YAML string
        """
        from common.utils.decisioning import yaml_exporter
        
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")
        
        return yaml_exporter.export_decision(decision)
    
    # =========================================================================
    # LOGGING
    # =========================================================================
    
    async def _log_evaluation(
        self,
        decision_id: str,
        inputs: Dict[str, Any],
        result: EvaluationResult,
    ) -> None:
        """Log decision evaluation to database."""
        if not self.db:
            return
        
        try:
            self.db.create('DecisionLog', {
                'id': str(uuid.uuid4()),
                'decision_id': decision_id,
                'inputs': inputs,
                'outputs': result.outputs,
                'matched_rules': result.matched_rules,
                'success': result.success,
                'errors': result.errors,
                'execution_time_ms': result.execution_time_ms,
                'evaluated_at': datetime.now(timezone.utc),
            })
        except Exception as e:
            logger.debug(f"Failed to log decision evaluation: {e}")
    
    # =========================================================================
    # STATUS
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        return {
            'initialized': self._initialized,
            'decisions_loaded': len(self._decisions),
            'decision_ids': list(self._decisions.keys()),
            'custom_functions': len(self._expression_engine._functions),
            'config': {
                'auto_load': self.auto_load_enabled,
                'cache_enabled': self.cache_enabled,
                'cache_ttl_seconds': self.cache_ttl_seconds,
                'trace_enabled': self.trace_enabled,
                'log_evaluations': self.log_evaluations,
                'config_dirs': [str(p) for p in self.get_config_dirs()],
            },
            'cache': {
                'entries': len(self._cache),
            },
        }
    
    # =========================================================================
    # RELOAD / REFRESH
    # =========================================================================
    
    async def reload(self) -> Dict[str, Any]:
        """
        Reload all decisions from configured directories.
        
        Clears existing decisions and reloads from config.
        
        Returns:
            Dict with reload status
        """
        self.clear()
        self._initialized = False
        return await self.initialize(auto_load=True)
    
    async def reload_file(self, path: str) -> List[str]:
        """
        Reload a specific decision file.
        
        Unloads any decisions from that file and reloads.
        
        Args:
            path: Path to decision file
            
        Returns:
            List of loaded decision IDs
        """
        # For now, just reload the file (decisions will be replaced)
        return await self.load_from_file(path)
    
    # =========================================================================
    # CACHING
    # =========================================================================
    
    def _make_cache_key(self, decision_id: str, inputs: Dict[str, Any]) -> str:
        """Create cache key from decision ID and inputs."""
        import hashlib
        import json
        
        # Sort inputs for consistent hashing
        sorted_inputs = json.dumps(inputs, sort_keys=True, default=str)
        content = f"{decision_id}:{sorted_inputs}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def _get_cached(self, cache_key: str) -> Optional[EvaluationResult]:
        """Get cached result if valid."""
        if cache_key not in self._cache:
            return None
        
        timestamp = self._cache_timestamps.get(cache_key)
        if timestamp:
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()
            if age > self.cache_ttl_seconds:
                # Expired
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
                return None
        
        return self._cache[cache_key]
    
    def _set_cached(self, cache_key: str, result: EvaluationResult) -> None:
        """Cache an evaluation result."""
        self._cache[cache_key] = result
        self._cache_timestamps[cache_key] = datetime.now(timezone.utc)
    
    def clear_cache(self) -> int:
        """
        Clear evaluation cache.
        
        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        self._cache_timestamps.clear()
        return count
    
    def invalidate_decision_cache(self, decision_id: str) -> int:
        """
        Invalidate cache entries for a specific decision.
        
        Args:
            decision_id: Decision ID to invalidate
            
        Returns:
            Number of entries invalidated
        """
        # Since cache keys are hashed, we need to track decision_id -> keys
        # For now, clear all cache when a decision is invalidated
        # In production, maintain a reverse index
        return self.clear_cache()


# =============================================================================
# SINGLETON
# =============================================================================

_service_instance: Optional[DecisionEngine] = None


def get_decision_engine() -> DecisionEngine:
    """Get the singleton DecisionEngine instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = DecisionEngine()
    return _service_instance


async def initialize_decision_engine(auto_load: Optional[bool] = None) -> DecisionEngine:
    """
    Initialize the decision engine with auto-loading.
    
    Convenience function for application startup.
    
    Args:
        auto_load: Override auto-load setting (None uses config)
        
    Returns:
        Initialized DecisionEngine
    """
    engine = get_decision_engine()
    await engine.initialize(auto_load=auto_load)
    return engine


# Module-level singleton
decision_engine = get_decision_engine()
