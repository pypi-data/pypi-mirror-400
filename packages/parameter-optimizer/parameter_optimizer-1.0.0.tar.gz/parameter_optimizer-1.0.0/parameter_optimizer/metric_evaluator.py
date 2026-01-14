"""
Metric evaluation system for parameter optimization.

This module handles metric calculation and result comparison.
"""

from typing import Any, Callable, List, Optional
from .data_models import TestResult


class MetricEvaluator:
    """
    Handles metric calculation and result comparison.
    
    Supports custom metric functions and identifies optimal configurations
    based on metric scores. Handles both maximization and minimization
    optimization goals.
    """
    
    def __init__(self, metric_function: Callable[[Any], float], maximize: bool = True):
        """
        Initialize with custom metric function.
        
        Args:
            metric_function: Function that takes a class instance and returns a numeric score
            maximize: If True, higher scores are better. If False, lower scores are better.
        
        Raises:
            TypeError: If metric_function is not callable
        """
        if not callable(metric_function):
            raise TypeError("metric_function must be callable")
        
        self.metric_function = metric_function
        self.maximize = maximize
    
    def evaluate(self, class_instance: Any) -> float:
        """
        Calculate metric score for class instance.
        
        Args:
            class_instance: Instance of the target class to evaluate
            
        Returns:
            float: The metric score calculated by the metric function
            
        Raises:
            Exception: Re-raises any exception from the metric function with context
        """
        try:
            score = self.metric_function(class_instance)
            
            # Validate that the metric function returns a numeric value
            if not isinstance(score, (int, float)):
                raise ValueError(f"Metric function must return a numeric value, got {type(score)}")
            
            return float(score)
            
        except Exception as e:
            raise Exception(f"Metric evaluation failed: {str(e)}") from e
    
    def compare_results(self, results: List[TestResult]) -> Optional[TestResult]:
        """
        Find best result based on metric scores.
        
        Args:
            results: List of TestResult objects to compare
            
        Returns:
            TestResult: The result with the best metric score, or None if no successful results
        """
        if not results:
            return None
        
        # Filter to only successful results
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return None
        
        # Find the best result based on optimization direction
        if self.maximize:
            best_result = max(successful_results, key=lambda r: r.metric_score)
        else:
            best_result = min(successful_results, key=lambda r: r.metric_score)
        
        return best_result
    
    def get_best_configuration(self, results: List[TestResult]) -> Optional[dict]:
        """
        Get the parameter configuration that achieved the best score.
        
        Args:
            results: List of TestResult objects to analyze
            
        Returns:
            dict: The parameter configuration with the best score, or None if no successful results
        """
        best_result = self.compare_results(results)
        return best_result.parameters if best_result else None
    
    def get_best_score(self, results: List[TestResult]) -> Optional[float]:
        """
        Get the best metric score achieved.
        
        Args:
            results: List of TestResult objects to analyze
            
        Returns:
            float: The best metric score, or None if no successful results
        """
        best_result = self.compare_results(results)
        return best_result.metric_score if best_result else None