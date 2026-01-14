"""
Data models for the parameter optimizer package.

This module defines the core data structures used throughout the optimization process.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class TestResult:
    """
    Represents the result of a single parameter combination test.
    
    Attributes:
        parameters: The parameter combination that was tested
        metric_score: The performance score calculated by the metric function
        execution_time: Time taken to execute the test in seconds
        timestamp: When the test was executed
        success: Whether the test completed successfully
        error_message: Error details if the test failed
    """
    parameters: Dict[str, Any]
    metric_score: float
    execution_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


@dataclass
class OptimizationSummary:
    """
    Summary of a complete optimization run.
    
    Attributes:
        best_configuration: The parameter combination that achieved the best score
        best_score: The best metric score achieved
        total_combinations: Total number of parameter combinations to test
        completed_tests: Number of tests that have been completed
        cached_results: Number of results retrieved from cache
        failed_tests: Number of tests that failed during execution
        execution_time: Total time taken for the optimization run
    """
    best_configuration: Dict[str, Any]
    best_score: float
    total_combinations: int
    completed_tests: int
    cached_results: int
    failed_tests: int
    execution_time: float