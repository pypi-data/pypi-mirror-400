"""
Configuration management for parameter optimization.

This module handles parameter configuration parsing and combination generation.
"""

import json
import itertools
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Iterator, Union


class ConfigurationManager:
    """
    Handles parameter configuration parsing and combination generation.
    """

    def __init__(self, json_path: str,
                 fixed_parameters: Optional[Dict[str, Any]] = None):
        """Initialize with parameter configuration."""
        # Validate inputs
        if not isinstance(json_path, str):
            raise TypeError(f"json_path must be a string, got {type(json_path)}")
        
        if not json_path.strip():
            raise ValueError("json_path cannot be empty or whitespace")
        
        if fixed_parameters is not None and not isinstance(fixed_parameters, dict):
            raise TypeError(f"fixed_parameters must be a dictionary or None, got {type(fixed_parameters)}")
        
        self.json_path = json_path
        self.fixed_parameters = fixed_parameters or {}
        self._parameters = None
        
        # Validate fixed parameters
        self._validate_fixed_parameters()

    def _validate_fixed_parameters(self) -> None:
        """Validate fixed parameters have valid names and values."""
        for param_name, param_value in self.fixed_parameters.items():
            if not isinstance(param_name, str):
                raise TypeError(f"Fixed parameter name must be string: {param_name}")
            
            if not param_name.strip():
                raise ValueError("Fixed parameter name cannot be empty or whitespace")
            
            # Validate parameter name format (basic Python identifier rules)
            if not param_name.replace('_', '').replace('-', '').isalnum():
                raise ValueError(f"Invalid parameter name format: {param_name}")
            
            # Validate parameter value type
            if not isinstance(param_value, (int, float, str, bool, type(None))):
                raise ValueError(
                    f"Unsupported fixed parameter type for {param_name}: "
                    f"{type(param_value)}. Supported types: int, float, str, bool, None"
                )

    def load_parameters(self) -> Dict[str, List[Any]]:
        """Load and validate parameter ranges from JSON."""
        try:
            path = Path(self.json_path)
            
            # Enhanced file validation
            if not path.exists():
                raise FileNotFoundError(
                    f"Parameter file not found: {self.json_path}")
            
            if not path.is_file():
                raise ValueError(
                    f"Path is not a file: {self.json_path}")
            
            if path.stat().st_size == 0:
                raise ValueError(
                    f"Parameter file is empty: {self.json_path}")
            
            # Check file permissions
            if not os.access(path, os.R_OK):
                raise PermissionError(
                    f"Cannot read parameter file: {self.json_path}")

            with open(path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid JSON format in {self.json_path}: {e}")

            # Enhanced data validation
            if not isinstance(data, dict):
                raise ValueError(
                    f"JSON must contain a dictionary of parameters, got {type(data)}")
            
            if not data:
                raise ValueError(
                    "Parameter configuration cannot be empty")

            # Validate and convert parameter values
            validated_params = {}
            for param_name, param_values in data.items():
                self._validate_parameter_entry(param_name, param_values)
                validated_params[param_name] = param_values

            # Check for conflicts with fixed parameters
            self._check_parameter_conflicts(validated_params)

            self._parameters = validated_params
            return validated_params

        except (FileNotFoundError, PermissionError, ValueError) as e:
            # Re-raise known errors with context
            raise type(e)(f"Configuration loading failed: {e}")
        except Exception as e:
            # Wrap unexpected errors
            raise ValueError(f"Unexpected error loading parameters: {e}")

    def _validate_parameter_entry(self, param_name: str, param_values: Any) -> None:
        """Validate a single parameter entry from JSON."""
        if not isinstance(param_name, str):
            raise ValueError(
                f"Parameter name must be string: {param_name}")
        
        if not param_name.strip():
            raise ValueError(
                "Parameter name cannot be empty or whitespace")
        
        # Validate parameter name format
        if not param_name.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid parameter name format: {param_name}")

        if not isinstance(param_values, list):
            raise ValueError(
                f"Parameter values must be a list for {param_name}, got {type(param_values)}")

        if not param_values:
            raise ValueError(
                f"Parameter list cannot be empty for {param_name}")

        # Validate data types (int, float, str, bool)
        for i, value in enumerate(param_values):
            if not isinstance(value, (int, float, str, bool, type(None))):
                raise ValueError(
                    f"Unsupported parameter type for {param_name}[{i}]: "
                    f"{type(value)}. Supported types: int, float, str, bool, None"
                )
        
        # Check for duplicate values
        if len(param_values) != len(set(str(v) for v in param_values)):
            raise ValueError(
                f"Duplicate values found in parameter list for {param_name}")

    def _check_parameter_conflicts(self, json_params: Dict[str, List[Any]]) -> None:
        """Check for conflicts between JSON parameters and fixed parameters."""
        json_param_names = set(json_params.keys())
        fixed_param_names = set(self.fixed_parameters.keys())
        
        # Warn about overlapping parameters (fixed takes precedence)
        overlapping = json_param_names & fixed_param_names
        if overlapping:
            # This is a warning, not an error - fixed parameters override JSON
            pass

    def generate_combinations(self) -> Iterator[Dict[str, Any]]:
        """Generate all parameter combinations using itertools.product."""
        if self._parameters is None:
            self.load_parameters()

        # Validate that we have parameters to work with
        if not self._parameters and not self.fixed_parameters:
            raise ValueError("No parameters available for combination generation")

        # Separate fixed parameters from variable parameters
        variable_params = {}
        for param_name, param_values in self._parameters.items():
            if param_name not in self.fixed_parameters:
                variable_params[param_name] = param_values

        if not variable_params:
            # If all parameters are fixed, return single combination
            if self.fixed_parameters:
                yield self.fixed_parameters.copy()
            else:
                raise ValueError("No variable parameters available for optimization")
            return

        # Validate combination space size
        total_combinations = 1
        for param_values in variable_params.values():
            total_combinations *= len(param_values)
            if total_combinations > 1_000_000:  # Reasonable limit
                raise ValueError(
                    f"Parameter space too large: {total_combinations} combinations. "
                    "Consider reducing parameter ranges or using fixed parameters."
                )

        # Generate all combinations of variable parameters
        param_names = list(variable_params.keys())
        param_value_lists = [variable_params[name] for name in param_names]

        try:
            for combination_values in itertools.product(*param_value_lists):
                combination = dict(zip(param_names, combination_values))
                # Apply fixed parameters to each combination
                combination.update(self.fixed_parameters)
                yield combination
        except MemoryError:
            raise ValueError(
                "Parameter space too large for available memory. "
                "Consider reducing parameter ranges."
            )

    def apply_fixed_parameters(self,
                               combination: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fixed parameter values to a combination."""
        if not isinstance(combination, dict):
            raise TypeError(f"combination must be a dictionary, got {type(combination)}")
        
        result = combination.copy()
        result.update(self.fixed_parameters)
        return result
    
    def get_parameter_space_size(self) -> int:
        """Calculate the total number of parameter combinations."""
        if self._parameters is None:
            self.load_parameters()
        
        if not self._parameters and not self.fixed_parameters:
            return 0
        
        # Calculate size of variable parameter space
        variable_params = {
            name: values for name, values in self._parameters.items()
            if name not in self.fixed_parameters
        }
        
        if not variable_params:
            return 1  # Only fixed parameters
        
        total_combinations = 1
        for param_values in variable_params.values():
            total_combinations *= len(param_values)
        
        return total_combinations
    
    def validate_parameter_compatibility(self, target_class) -> List[str]:
        """
        Validate that parameters are compatible with target class constructor.
        
        Returns:
            List[str]: List of validation warnings/issues
        """
        warnings = []
        
        if self._parameters is None:
            self.load_parameters()
        
        try:
            import inspect
            constructor_sig = inspect.signature(target_class.__init__)
            constructor_params = set(constructor_sig.parameters.keys())
            constructor_params.discard('self')
            
            # Check all parameters (JSON + fixed)
            all_params = set(self._parameters.keys()) | set(self.fixed_parameters.keys())
            
            # Check for parameters not accepted by constructor
            has_var_keyword = any(
                param.kind == inspect.Parameter.VAR_KEYWORD
                for param in constructor_sig.parameters.values()
            )
            
            if not has_var_keyword:
                invalid_params = all_params - constructor_params
                if invalid_params:
                    warnings.append(
                        f"Parameters not accepted by {target_class.__name__}: "
                        f"{list(invalid_params)}"
                    )
            
            # Check for required parameters not provided
            required_params = set()
            for param_name, param in constructor_sig.parameters.items():
                if (param_name != 'self' and 
                    param.default == inspect.Parameter.empty):
                    required_params.add(param_name)
            
            missing_required = required_params - all_params
            if missing_required:
                warnings.append(
                    f"Required parameters missing: {list(missing_required)}"
                )
                
        except Exception as e:
            warnings.append(f"Could not validate parameter compatibility: {e}")
        
        return warnings