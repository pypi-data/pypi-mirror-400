"""
Core parameter optimizer implementation.

This module contains the main ParameterOptimizer class that orchestrates
the optimization process.
"""

import inspect
import time
import os
import gc
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Iterator

# Optional psutil import for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .config_manager import ConfigurationManager
from .test_runner import TestRunner
from .result_cache import ResultCache
from .metric_evaluator import MetricEvaluator
from .data_models import TestResult, OptimizationSummary


class ParameterOptimizer:
    """
    Main interface for the parameter optimization system.
    
    This class coordinates all components to perform systematic parameter
    optimization for any given class.
    """
    
    def __init__(self, target_class, parameters_json_path: str, metric_function: Callable,
                 cache_dir: str = "./optimization_cache", fixed_parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize the parameter optimizer.
        
        Args:
            target_class: Class to optimize parameters for
            parameters_json_path: Path to JSON file with parameter ranges
            metric_function: Function that takes class instance and returns score
            cache_dir: Directory for caching results
            fixed_parameters: Dict of parameters to keep constant
            
        Raises:
            TypeError: If arguments have incorrect types
            ValueError: If arguments have invalid values
            FileNotFoundError: If parameter file doesn't exist
        """
        # Comprehensive input validation
        self._validate_initialization_inputs(
            target_class, parameters_json_path, metric_function, cache_dir, fixed_parameters
        )
        
        self.target_class = target_class
        self.parameters_json_path = parameters_json_path
        self.metric_function = metric_function
        self.cache_dir = cache_dir
        self.fixed_parameters = fixed_parameters or {}
        
        # Validate cache directory
        self._validate_and_setup_cache_dir()
        
        # Initialize component classes with validation
        try:
            self.config_manager = ConfigurationManager(
                json_path=parameters_json_path,
                fixed_parameters=fixed_parameters
            )
            
            self.test_runner = TestRunner(
                target_class=target_class,
                metric_function=metric_function
            )
            
            self.result_cache = ResultCache(
                cache_dir=cache_dir,
                target_class_name=target_class.__name__
            )
            
            self.metric_evaluator = MetricEvaluator(
                metric_function=metric_function,
                maximize=True  # Default to maximization, could be made configurable
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize optimizer components: {e}")
        
        # Validate parameter compatibility early
        compatibility_warnings = self.config_manager.validate_parameter_compatibility(target_class)
        if compatibility_warnings:
            # For now, we'll store warnings but not fail initialization
            # In production, you might want to log these warnings
            self._compatibility_warnings = compatibility_warnings
        else:
            self._compatibility_warnings = []
        
        # Initialize state tracking
        self._results: List[TestResult] = []
        self._total_combinations = 0
        self._completed_tests = 0
        self._cached_results = 0
        self._failed_tests = 0
        self._start_time = None
        self._memory_limit_mb = 1024  # Default 1GB memory limit
        self._batch_size = 100  # Process results in batches
        
        # Generate class signature for cache validation
        self._class_signature = self._generate_class_signature()

    def _validate_initialization_inputs(self, target_class, parameters_json_path: str, 
                                      metric_function: Callable, cache_dir: str, 
                                      fixed_parameters: Optional[Dict[str, Any]]) -> None:
        """Validate all initialization inputs comprehensively."""
        # Validate target_class
        if not inspect.isclass(target_class):
            raise TypeError(f"target_class must be a class, got {type(target_class)}")
        
        # Check if class can be instantiated (has __init__)
        if not hasattr(target_class, '__init__'):
            raise ValueError(f"target_class {target_class.__name__} must have __init__ method")
        
        # Validate parameters_json_path
        if not isinstance(parameters_json_path, str):
            raise TypeError(f"parameters_json_path must be a string, got {type(parameters_json_path)}")
        
        if not parameters_json_path.strip():
            raise ValueError("parameters_json_path cannot be empty or whitespace")
        
        # Check if file exists and is readable
        path = Path(parameters_json_path)
        if not path.exists():
            raise FileNotFoundError(f"Parameter file not found: {parameters_json_path}")
        
        if not path.is_file():
            raise ValueError(f"parameters_json_path must be a file: {parameters_json_path}")
        
        if not os.access(path, os.R_OK):
            raise PermissionError(f"Cannot read parameter file: {parameters_json_path}")
        
        # Validate metric_function
        if not callable(metric_function):
            raise TypeError(f"metric_function must be callable, got {type(metric_function)}")
        
        # Try to get function signature for validation
        try:
            sig = inspect.signature(metric_function)
            if len(sig.parameters) == 0:
                raise ValueError("metric_function must accept at least one parameter (class instance)")
        except (ValueError, TypeError) as e:
            # Some built-in functions might not have inspectable signatures
            # We'll allow them but warn
            pass
        
        # Validate cache_dir
        if not isinstance(cache_dir, str):
            raise TypeError(f"cache_dir must be a string, got {type(cache_dir)}")
        
        if not cache_dir.strip():
            raise ValueError("cache_dir cannot be empty or whitespace")
        
        # Validate fixed_parameters
        if fixed_parameters is not None:
            if not isinstance(fixed_parameters, dict):
                raise TypeError(f"fixed_parameters must be a dictionary or None, got {type(fixed_parameters)}")
            
            for key, value in fixed_parameters.items():
                if not isinstance(key, str):
                    raise TypeError(f"Fixed parameter keys must be strings, got {type(key)} for key {key}")
                
                if not key.strip():
                    raise ValueError("Fixed parameter keys cannot be empty or whitespace")

    def _validate_and_setup_cache_dir(self) -> None:
        """Validate and set up the cache directory."""
        cache_path = Path(self.cache_dir)
        
        try:
            # Create directory if it doesn't exist
            cache_path.mkdir(parents=True, exist_ok=True)
            
            # Check if we can write to the directory
            test_file = cache_path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
            except (PermissionError, OSError) as e:
                raise PermissionError(f"Cannot write to cache directory {self.cache_dir}: {e}")
                
        except Exception as e:
            raise ValueError(f"Failed to set up cache directory {self.cache_dir}: {e}")
        
    def _generate_class_signature(self) -> str:
        """Generate a signature for the target class to validate cache compatibility."""
        try:
            # Get class name and constructor signature
            class_name = self.target_class.__name__
            constructor_sig = str(inspect.signature(self.target_class.__init__))
            
            # Include module name if available
            module_name = getattr(self.target_class, '__module__', 'unknown')
            
            return f"{module_name}.{class_name}{constructor_sig}"
        except Exception:
            # Fallback to just class name if signature generation fails
            return self.target_class.__name__
    
    def optimize(self, max_combinations: Optional[int] = None, progress_callback: Optional[Callable] = None,
                 memory_limit_mb: Optional[int] = None):
        """
        Run optimization and return best configuration.
        
        Args:
            max_combinations: Maximum number of combinations to test (None for all)
            progress_callback: Optional callback function for progress updates
            memory_limit_mb: Memory limit in MB (None for default)
            
        Returns:
            Dict[str, Any]: The best parameter configuration found
            
        Raises:
            ValueError: If optimization parameters are invalid
            RuntimeError: If optimization fails due to system issues
        """
        # Validate inputs
        if max_combinations is not None:
            if not isinstance(max_combinations, int):
                raise TypeError(f"max_combinations must be an integer or None, got {type(max_combinations)}")
            if max_combinations <= 0:
                raise ValueError(f"max_combinations must be positive, got {max_combinations}")
        
        if progress_callback is not None:
            if not callable(progress_callback):
                raise TypeError(f"progress_callback must be callable or None, got {type(progress_callback)}")
        
        if memory_limit_mb is not None:
            if not isinstance(memory_limit_mb, int) or memory_limit_mb <= 0:
                raise ValueError(f"memory_limit_mb must be a positive integer, got {memory_limit_mb}")
            self._memory_limit_mb = memory_limit_mb
        
        self._start_time = time.time()
        self._results = []
        self._completed_tests = 0
        self._cached_results = 0
        self._failed_tests = 0
        
        try:
            # Load parameters and generate combinations
            self.config_manager.load_parameters()
            
            # Check parameter space size before generating combinations
            total_space_size = self.config_manager.get_parameter_space_size()
            if total_space_size == 0:
                raise ValueError("No parameter combinations available for optimization")
            
            # Use iterator for memory efficiency with large parameter spaces
            combinations_iter = self.config_manager.generate_combinations()
            
            # Convert to list only if needed and within reasonable limits
            if total_space_size <= 10000:  # Small enough to fit in memory
                combinations = list(combinations_iter)
                self._total_combinations = len(combinations)
            else:
                # For large spaces, we'll process iteratively
                combinations = combinations_iter
                self._total_combinations = total_space_size
            
            if self._total_combinations == 0:
                raise ValueError("No parameter combinations generated")
            
            # Limit combinations if max_combinations is specified
            if max_combinations is not None and max_combinations > 0:
                if isinstance(combinations, list):
                    combinations = combinations[:max_combinations]
                    self._total_combinations = len(combinations)
                else:
                    # For iterators, we'll limit during processing
                    self._total_combinations = min(max_combinations, self._total_combinations)
            
            # Report initial progress
            if progress_callback:
                try:
                    progress_callback(0, self._total_combinations, None)
                except Exception as e:
                    # Don't fail optimization due to callback errors
                    pass
            
            # Process combinations with memory management
            self._process_combinations_with_memory_management(
                combinations, max_combinations, progress_callback
            )
            
            # Validate we have some successful results
            successful_results = [r for r in self._results if r.success]
            if not successful_results:
                raise RuntimeError(
                    f"All {self._completed_tests} optimization tests failed. "
                    "Check your target class, parameters, and metric function."
                )
            
            # Find and return best configuration
            best_config = self.metric_evaluator.get_best_configuration(self._results)
            if best_config is None:
                raise RuntimeError("Failed to identify best configuration")
            
            return best_config
            
        except (ValueError, TypeError) as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Ensure we have some tracking even if optimization fails
            if self._start_time is None:
                self._start_time = time.time()
            raise RuntimeError(f"Optimization failed: {str(e)}") from e
        finally:
            # Cleanup resources
            self._cleanup_resources()

    def _process_combinations_with_memory_management(self, combinations, max_combinations, progress_callback):
        """Process parameter combinations with memory monitoring and management."""
        processed_count = 0
        
        # Convert iterator to batched processing for memory efficiency
        if hasattr(combinations, '__iter__') and not isinstance(combinations, list):
            # Process iterator in batches
            batch = []
            for i, parameters in enumerate(combinations):
                if max_combinations and i >= max_combinations:
                    break
                    
                batch.append(parameters)
                
                if len(batch) >= self._batch_size:
                    self._process_batch(batch, progress_callback)
                    processed_count += len(batch)
                    batch = []
                    
                    # Check memory usage
                    if self._check_memory_usage():
                        self._manage_memory()
            
            # Process remaining batch
            if batch:
                self._process_batch(batch, progress_callback)
                processed_count += len(batch)
        else:
            # Process list in batches
            for i in range(0, len(combinations), self._batch_size):
                batch = combinations[i:i + self._batch_size]
                self._process_batch(batch, progress_callback)
                processed_count += len(batch)
                
                # Check memory usage
                if self._check_memory_usage():
                    self._manage_memory()

    def _process_batch(self, batch: List[Dict[str, Any]], progress_callback: Optional[Callable]):
        """Process a batch of parameter combinations."""
        for parameters in batch:
            try:
                # Check cache first
                cached_result = self.result_cache.get_cached_result(
                    parameters, self._class_signature
                )
                
                if cached_result is not None:
                    # Use cached result
                    self._results.append(cached_result)
                    self._cached_results += 1
                    if not cached_result.success:
                        self._failed_tests += 1
                else:
                    # Run new test
                    test_result = self.test_runner.run_test(parameters)
                    self._results.append(test_result)
                    
                    # Cache the result
                    self.result_cache.cache_result(
                        parameters, test_result, test_result.metric_score, self._class_signature
                    )
                    
                    if not test_result.success:
                        self._failed_tests += 1
                
                self._completed_tests += 1
                
                # Report progress
                if progress_callback:
                    try:
                        current_best = self.metric_evaluator.get_best_configuration(self._results)
                        progress_callback(self._completed_tests, self._total_combinations, current_best)
                    except Exception as e:
                        # Don't fail optimization due to callback errors
                        pass
                        
            except Exception as e:
                # Log individual test failure but continue optimization
                self._failed_tests += 1
                self._completed_tests += 1
                # Could log the error here in production
                continue

    def _check_memory_usage(self) -> bool:
        """Check if memory usage exceeds the limit."""
        if not PSUTIL_AVAILABLE:
            return False  # Can't check memory without psutil
        
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            return memory_mb > self._memory_limit_mb
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # If we can't check memory, assume it's fine
            return False

    def _manage_memory(self) -> None:
        """Manage memory by cleaning up and garbage collecting."""
        # Force garbage collection
        gc.collect()
        
        # If we still have too many results in memory, keep only the best ones
        if len(self._results) > 1000:  # Keep reasonable number of results
            # Sort by metric score and keep best results
            sorted_results = sorted(
                self._results, 
                key=lambda r: r.metric_score if r.success else float('-inf'),
                reverse=self.metric_evaluator.maximize
            )
            self._results = sorted_results[:500]  # Keep top 500 results

    def _cleanup_resources(self) -> None:
        """Clean up resources after optimization."""
        try:
            # Clean up cache resources
            if hasattr(self.result_cache, 'cleanup'):
                self.result_cache.cleanup()
            
            # Force garbage collection
            gc.collect()
            
        except Exception:
            # Don't raise exceptions during cleanup
            pass
    
    def get_results(self, sort_by_metric: bool = True):
        """
        Get all test results.
        
        Args:
            sort_by_metric: If True, sort results by metric score (best first)
            
        Returns:
            List[TestResult]: List of all test results
        """
        if not sort_by_metric:
            return self._results.copy()
        
        # Sort results by metric score (best first based on optimization direction)
        if self.metric_evaluator.maximize:
            return sorted(self._results, key=lambda r: r.metric_score if r.success else float('-inf'), reverse=True)
        else:
            return sorted(self._results, key=lambda r: r.metric_score if r.success else float('inf'))
    
    def get_progress(self):
        """
        Get current optimization progress.
        
        Returns:
            Dict[str, Any]: Progress information including completion status and statistics
        """
        execution_time = 0.0
        if self._start_time is not None:
            execution_time = time.time() - self._start_time
        
        # Calculate success rate
        successful_tests = len([r for r in self._results if r.success])
        success_rate = successful_tests / max(self._completed_tests, 1)
        
        # Get current best result
        best_result = self.metric_evaluator.compare_results(self._results)
        current_best_config = best_result.parameters if best_result else None
        current_best_score = best_result.metric_score if best_result else None
        
        return {
            'total_combinations': self._total_combinations,
            'completed_tests': self._completed_tests,
            'cached_results': self._cached_results,
            'failed_tests': self._failed_tests,
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'execution_time': execution_time,
            'is_complete': self._completed_tests >= self._total_combinations,
            'progress_percentage': (self._completed_tests / max(self._total_combinations, 1)) * 100,
            'current_best_config': current_best_config,
            'current_best_score': current_best_score
        }
    
    def get_optimization_summary(self) -> OptimizationSummary:
        """
        Create comprehensive optimization summary.
        
        Returns:
            OptimizationSummary: Complete summary of the optimization run
        """
        execution_time = 0.0
        if self._start_time is not None:
            execution_time = time.time() - self._start_time
        
        # Get best configuration and score
        best_result = self.metric_evaluator.compare_results(self._results)
        best_configuration = best_result.parameters if best_result else {}
        best_score = best_result.metric_score if best_result else 0.0
        
        return OptimizationSummary(
            best_configuration=best_configuration,
            best_score=best_score,
            total_combinations=self._total_combinations,
            completed_tests=self._completed_tests,
            cached_results=self._cached_results,
            failed_tests=self._failed_tests,
            execution_time=execution_time
        )
    
    def get_compatibility_warnings(self) -> List[str]:
        """
        Get parameter compatibility warnings identified during initialization.
        
        Returns:
            List[str]: List of compatibility warnings
        """
        return self._compatibility_warnings.copy()
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Perform comprehensive validation of the current configuration.
        
        Returns:
            Dict[str, Any]: Validation results including warnings and errors
        """
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'parameter_space_size': 0,
            'compatibility_warnings': self._compatibility_warnings.copy()
        }
        
        try:
            # Validate parameter loading
            self.config_manager.load_parameters()
            validation_results['parameter_space_size'] = self.config_manager.get_parameter_space_size()
            
            # Check parameter space size
            if validation_results['parameter_space_size'] == 0:
                validation_results['errors'].append("No parameter combinations available")
                validation_results['valid'] = False
            elif validation_results['parameter_space_size'] > 100_000:
                validation_results['warnings'].append(
                    f"Large parameter space: {validation_results['parameter_space_size']} combinations"
                )
            
            # Test metric function with a dummy instance if possible
            try:
                # Try to create a test instance with fixed parameters only
                if self.fixed_parameters:
                    test_instance = self.target_class(**self.fixed_parameters)
                    test_score = self.metric_function(test_instance)
                    if not isinstance(test_score, (int, float)):
                        validation_results['errors'].append(
                            f"Metric function returns non-numeric value: {type(test_score)}"
                        )
                        validation_results['valid'] = False
            except Exception as e:
                validation_results['warnings'].append(
                    f"Could not test metric function: {e}"
                )
            
            # Check cache directory
            cache_path = Path(self.cache_dir)
            if not cache_path.exists():
                validation_results['warnings'].append(f"Cache directory will be created: {self.cache_dir}")
            elif not os.access(cache_path, os.W_OK):
                validation_results['errors'].append(f"Cannot write to cache directory: {self.cache_dir}")
                validation_results['valid'] = False
                
        except Exception as e:
            validation_results['errors'].append(f"Configuration validation failed: {e}")
            validation_results['valid'] = False
        
        return validation_results
    
    def set_memory_limit(self, memory_limit_mb: int) -> None:
        """
        Set memory limit for optimization process.
        
        Args:
            memory_limit_mb: Memory limit in megabytes
        """
        if not isinstance(memory_limit_mb, int) or memory_limit_mb <= 0:
            raise ValueError(f"memory_limit_mb must be a positive integer, got {memory_limit_mb}")
        
        self._memory_limit_mb = memory_limit_mb
    
    def set_batch_size(self, batch_size: int) -> None:
        """
        Set batch size for processing parameter combinations.
        
        Args:
            batch_size: Number of combinations to process in each batch
        """
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError(f"batch_size must be a positive integer, got {batch_size}")
        
        self._batch_size = batch_size
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get current resource usage information.
        
        Returns:
            Dict with memory usage, cache info, and other resource metrics
        """
        resource_info = {
            'memory_limit_mb': self._memory_limit_mb,
            'batch_size': self._batch_size,
            'results_in_memory': len(self._results),
            'completed_tests': self._completed_tests,
            'failed_tests': self._failed_tests,
            'cached_results': self._cached_results
        }
        
        try:
            # Get current memory usage
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                memory_info = process.memory_info()
                resource_info.update({
                    'current_memory_mb': round(memory_info.rss / (1024 * 1024), 2),
                    'memory_percent': round(process.memory_percent(), 2)
                })
            else:
                resource_info.update({
                    'current_memory_mb': 0.0,
                    'memory_percent': 0.0,
                    'psutil_available': False
                })
        except Exception:
            resource_info.update({
                'current_memory_mb': 0.0,
                'memory_percent': 0.0
            })
        
        # Get cache size info
        try:
            cache_info = self.result_cache.get_cache_size_info()
            resource_info['cache_info'] = cache_info
        except Exception:
            resource_info['cache_info'] = {}
        
        return resource_info
    
    def cleanup(self) -> None:
        """Clean up all resources used by the optimizer."""
        self._cleanup_resources()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()