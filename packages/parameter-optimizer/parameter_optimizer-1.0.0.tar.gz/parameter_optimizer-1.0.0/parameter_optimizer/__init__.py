"""
Parameter Optimizer Package

A reusable parameter optimization package that systematically tests different 
parameter combinations for a given class to find the optimal configuration 
based on a specified metric.
"""

from .core import ParameterOptimizer
from .data_models import TestResult, OptimizationSummary

__version__ = "1.0.0"
__all__ = ["ParameterOptimizer", "TestResult", "OptimizationSummary"]