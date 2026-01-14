#!/usr/bin/env python3
"""
Parameter Query Utility

This module provides utility functions for querying specific parameter
combinations and their cached results.
"""

from typing import Dict, Any, Optional, List
from parameter_optimizer.result_cache import ResultCache
from parameter_optimizer.test_runner import TestRunner
from parameter_optimizer.data_models import TestResult


class ParameterQueryUtility:
    """
    Utility class for querying parameter combinations and their results.
    """

    def __init__(self, cache: ResultCache, test_runner: TestRunner):
        """
        Initialize the query utility.

        Args:
            cache: ResultCache instance for querying cached results
            test_runner: TestRunner instance for running new tests if needed
        """
        self.cache = cache
        self.test_runner = test_runner

    def query_parameters(self, parameters: Dict[str, Any],
                         run_if_missing: bool = False) -> Optional[TestResult]:
        """
        Query specific parameter combination.

        Args:
            parameters: Dictionary of parameter values to query
            run_if_missing: If True, run the test if not found in cache

        Returns:
            TestResult if found in cache or run_if_missing=True, None otherwise
        """
        # First check cache
        cached_result = self.cache.get_cached_result(parameters)

        if cached_result:
            return cached_result

        # If not in cache and run_if_missing is True, run the test
        if run_if_missing:
            result = self.test_runner.run_test(parameters)
            self.cache.cache_result(parameters, result, result.metric_score)
            return result

        return None

    def is_parameters_tested(self, parameters: Dict[str, Any]) -> bool:
        """
        Check if specific parameter combination has been tested.

        Args:
            parameters: Dictionary of parameter values to check

        Returns:
            True if parameters have been tested, False otherwise
        """
        cached_result = self.cache.get_cached_result(parameters)
        return cached_result is not None

    def get_parameter_performance(self, parameters: Dict[str, Any]) -> Optional[float]:
        """
        Get the performance score for specific parameter combination.

        Args:
            parameters: Dictionary of parameter values to query

        Returns:
            Performance score if found, None if not tested
        """
        cached_result = self.cache.get_cached_result(parameters)
        return cached_result.metric_score if cached_result else None

    def batch_query_parameters(self, parameter_list: List[Dict[str, Any]],
                               run_missing: bool = False) -> List[Optional[TestResult]]:
        """
        Query multiple parameter combinations at once.

        Args:
            parameter_list: List of parameter dictionaries to query
            run_missing: If True, run tests for parameters not in cache

        Returns:
            List of TestResult objects (None for untested parameters if run_missing=False)
        """
        results = []

        for parameters in parameter_list:
            result = self.query_parameters(
                parameters, run_if_missing=run_missing)
            results.append(result)

        return results

    def get_cache_summary(self) -> Dict[str, Any]:
        """
        Get a summary of cached results.

        Returns:
            Dictionary with cache statistics and summary information
        """
        stats = self.cache.get_cache_stats()

        return {
            'total_cached': stats['total_cached'],
            'successful_cached': stats['successful_cached'],
            'failed_cached': stats['failed_cached'],
            'success_rate': (stats['successful_cached'] / stats['total_cached']
                             if stats['total_cached'] > 0 else 0.0)
        }

    def find_similar_parameters(self, target_parameters: Dict[str, Any],
                                tolerance: Dict[str, float] = None) -> List[TestResult]:
        """
        Find cached results with similar parameter values.

        Args:
            target_parameters: Target parameter values to find similar results for
            tolerance: Dictionary specifying tolerance for each numeric parameter

        Returns:
            List of TestResult objects with similar parameter values
        """
        # This is a simplified implementation - in a real system you might
        # want to implement more sophisticated similarity matching

        # For now, we'll just return an empty list as this would require
        # iterating through all cached results, which isn't directly supported
        # by the current cache implementation

        return []


def demo_parameter_query():
    """Demonstrate the parameter query utility."""
    import tempfile
    from parameter_optimizer.metric_evaluator import MetricEvaluator

    # Mock class for demonstration
    class MockModel:
        def __init__(self, param1: float, param2: int):
            self.param1 = param1
            self.param2 = param2
            self.score = param1 * param2 * 0.1

        def get_score(self):
            return self.score

    def mock_metric(instance):
        return instance.get_score()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up components
        cache = ResultCache(temp_dir, "MockModel")
        test_runner = TestRunner(MockModel, mock_metric)
        query_util = ParameterQueryUtility(cache, test_runner)

        print("Parameter Query Utility Demo")
        print("=" * 30)

        # Test parameters
        test_params = [
            {"param1": 1.0, "param2": 10},
            {"param1": 2.0, "param2": 20},
            {"param1": 3.0, "param2": 30},
        ]

        # 1. Check if parameters are tested (should be False initially)
        print("1. Checking if parameters are tested (initially):")
        for params in test_params:
            is_tested = query_util.is_parameters_tested(params)
            print(f"   {params}: {'Tested' if is_tested else 'Not tested'}")

        # 2. Query parameters (will run tests since run_if_missing=True)
        print("\n2. Querying parameters (running tests):")
        for params in test_params:
            result = query_util.query_parameters(params, run_if_missing=True)
            if result:
                print(f"   {params}: Score = {result.metric_score:.2f}")

        # 3. Check if parameters are tested (should be True now)
        print("\n3. Checking if parameters are tested (after running):")
        for params in test_params:
            is_tested = query_util.is_parameters_tested(params)
            score = query_util.get_parameter_performance(params)
            print(
                f"   {params}: {'Tested' if is_tested else 'Not tested'}, Score = {score:.2f}")

        # 4. Batch query (should all be cache hits now)
        print("\n4. Batch querying parameters (cache hits):")
        batch_results = query_util.batch_query_parameters(test_params)
        for params, result in zip(test_params, batch_results):
            if result:
                print(f"   {params}: Score = {result.metric_score:.2f} (cached)")

        # 5. Cache summary
        print("\n5. Cache summary:")
        summary = query_util.get_cache_summary()
        print(f"   Total cached: {summary['total_cached']}")
        print(f"   Successful: {summary['successful_cached']}")
        print(f"   Success rate: {summary['success_rate']:.1%}")

        print("\n✓ Parameter query utility demo completed!")


if __name__ == "__main__":
    demo_parameter_query()
