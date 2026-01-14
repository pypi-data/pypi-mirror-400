"""
Test execution engine for parameter optimization.

This module handles the execution of tests with different parameter
combinations.
"""

import inspect
import time
from datetime import datetime
from typing import Any, Callable, Dict
from .data_models import TestResult


class TestRunner:
    """
    Executes tests with different parameter combinations.
    """

    def __init__(self, target_class, metric_function: Callable):
        """Initialize test runner with target class and metric function."""
        # Validate inputs
        if not inspect.isclass(target_class):
            raise TypeError(f"target_class must be a class, got {type(target_class)}")
        
        if not callable(metric_function):
            raise TypeError(f"metric_function must be callable, got {type(metric_function)}")
        
        self.target_class = target_class
        self.metric_function = metric_function

        # Get constructor signature for parameter validation
        try:
            self.constructor_signature = inspect.signature(target_class.__init__)
            self.constructor_params = set(
                self.constructor_signature.parameters.keys()
            )
            # Remove 'self' parameter from validation
            self.constructor_params.discard('self')
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot inspect target class constructor: {e}")

        # Check if constructor accepts **kwargs
        self.accepts_var_keyword = any(
            param.kind == inspect.Parameter.VAR_KEYWORD
            for param in self.constructor_signature.parameters.values()
        )

    def run_test(self, parameters: Dict[str, Any]) -> TestResult:
        """Execute single test with given parameters."""
        # Validate input parameters
        if not isinstance(parameters, dict):
            raise TypeError(f"parameters must be a dictionary, got {type(parameters)}")
        
        if not parameters:
            raise ValueError("parameters dictionary cannot be empty")
        
        start_time = time.time()
        timestamp = datetime.now()

        try:
            # Validate parameters before attempting instantiation
            validation_result = self.validate_parameters(parameters)
            if not validation_result['valid']:
                raise ValueError(
                    f"Invalid parameters for {self.target_class.__name__}: "
                    f"{validation_result['error']}"
                )

            # Instantiate the target class with the given parameters
            try:
                instance = self.target_class(**parameters)
            except Exception as e:
                raise RuntimeError(f"Failed to instantiate {self.target_class.__name__}: {e}")

            # Calculate metric score using the provided metric function
            try:
                metric_score = self.metric_function(instance)
            except Exception as e:
                raise RuntimeError(f"Metric function failed: {e}")

            # Validate that metric score is a number
            if not isinstance(metric_score, (int, float)):
                raise ValueError(
                    f"Metric function returned non-numeric value: "
                    f"{type(metric_score)} (value: {metric_score})"
                )
            
            # Check for invalid numeric values
            if not (float('-inf') < metric_score < float('inf')):
                raise ValueError(f"Metric function returned invalid numeric value: {metric_score}")

            execution_time = time.time() - start_time

            return TestResult(
                parameters=parameters,
                metric_score=float(metric_score),
                execution_time=execution_time,
                timestamp=timestamp,
                success=True,
                error_message=None
            )

        except Exception as e:
            execution_time = time.time() - start_time

            # Create detailed error message with context
            error_msg = f"{type(e).__name__}: {str(e)}"
            if hasattr(e, '__cause__') and e.__cause__:
                error_msg += f" (caused by: {type(e.__cause__).__name__}: {e.__cause__})"

            return TestResult(
                parameters=parameters,
                metric_score=0.0,  # Default score for failed tests
                execution_time=execution_time,
                timestamp=timestamp,
                success=False,
                error_message=error_msg
            )

    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters match class constructor.
        
        Returns:
            Dict with 'valid' (bool) and 'error' (str) keys
        """
        if not isinstance(parameters, dict):
            return {
                'valid': False,
                'error': f"Parameters must be a dictionary, got {type(parameters)}"
            }
        
        # Check if all provided parameters are accepted by the constructor
        provided_params = set(parameters.keys())

        # Get required parameters (those without default values)
        required_params = set()
        for param_name, param in self.constructor_signature.parameters.items():
            if (param_name != 'self' and
                    param.default == inspect.Parameter.empty):
                required_params.add(param_name)

        # Check if all required parameters are provided
        missing_required = required_params - provided_params
        if missing_required:
            return {
                'valid': False,
                'error': f"Missing required parameters: {list(missing_required)}"
            }

        # Check if any provided parameters are not accepted by constructor
        # Allow extra parameters if constructor accepts **kwargs
        if not self.accepts_var_keyword:
            invalid_params = provided_params - self.constructor_params
            if invalid_params:
                return {
                    'valid': False,
                    'error': f"Invalid parameters: {list(invalid_params)}. "
                           f"Expected: {list(self.constructor_params)}"
                }

        # Validate parameter values
        for param_name, param_value in parameters.items():
            if param_name in self.constructor_signature.parameters:
                param_info = self.constructor_signature.parameters[param_name]
                
                # Check type hints if available
                if param_info.annotation != inspect.Parameter.empty:
                    try:
                        # Basic type checking for common types
                        if param_info.annotation in (int, float, str, bool):
                            if not isinstance(param_value, param_info.annotation):
                                return {
                                    'valid': False,
                                    'error': f"Parameter {param_name} expected {param_info.annotation.__name__}, "
                                           f"got {type(param_value).__name__}"
                                }
                    except Exception:
                        # Skip type checking if annotation is complex
                        pass

        return {'valid': True, 'error': None}

    def get_error_summary(self, test_results: list) -> Dict[str, Any]:
        """Get summary of errors from test results."""
        failed_results = [r for r in test_results if not r.success]

        if not failed_results:
            return {"total_failures": 0, "error_types": {}}

        error_types = {}
        for result in failed_results:
            if result.error_message:
                # Extract error type from error message
                error_type = result.error_message.split(':')[0]
                if error_type not in error_types:
                    error_types[error_type] = []
                error_types[error_type].append({
                    'parameters': result.parameters,
                    'message': result.error_message
                })

        return {
            "total_failures": len(failed_results),
            "error_types": error_types,
            "failure_rate": len(failed_results) / len(test_results)
        }