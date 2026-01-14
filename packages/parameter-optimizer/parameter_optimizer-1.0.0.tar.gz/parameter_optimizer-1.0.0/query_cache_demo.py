#!/usr/bin/env python3
"""
Cache Query Demonstration Script

This script demonstrates how to query the cache for specific parameter
combinations and check their performance results.
"""

import json
import tempfile
from pathlib import Path

from parameter_optimizer.config_manager import ConfigurationManager
from parameter_optimizer.test_runner import TestRunner
from parameter_optimizer.result_cache import ResultCache
from parameter_optimizer.metric_evaluator import MetricEvaluator


class DemoMLModel:
    """Demo machine learning model for cache query testing."""

    def __init__(self, learning_rate: float, batch_size: int, optimizer: str):
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.optimizer = optimizer

        # Simulate model performance based on parameters
        base_accuracy = 0.7

        # Learning rate impact
        if 0.001 <= learning_rate <= 0.01:
            base_accuracy += 0.1
        elif learning_rate > 0.1:
            base_accuracy -= 0.05

        # Batch size impact
        if 32 <= batch_size <= 64:
            base_accuracy += 0.05
        elif batch_size > 128:
            base_accuracy -= 0.03

        # Optimizer impact
        if optimizer == "adam":
            base_accuracy += 0.08
        elif optimizer == "sgd":
            base_accuracy += 0.03

        self.accuracy = max(0.0, min(1.0, base_accuracy))

    def evaluate(self):
        """Return model accuracy."""
        return self.accuracy


def accuracy_metric(model_instance):
    """Metric function that returns model accuracy."""
    return model_instance.evaluate()


def query_specific_parameters(cache, test_runner, param_combinations):
    """Query cache for specific parameter combinations."""
    print("Querying specific parameter combinations:")
    print("-" * 50)

    for i, params in enumerate(param_combinations, 1):
        print(f"\n{i}. Checking parameters: {params}")

        # Check if this combination was already tested
        cached_result = cache.get_cached_result(params)

        if cached_result:
            print("   ✓ Found in cache!")
            print(f"   Score: {cached_result.metric_score:.3f}")
            print(f"   Success: {cached_result.success}")
            print(f"   Execution time: {cached_result.execution_time:.3f}s")
            print(f"   Timestamp: {cached_result.timestamp}")
            if cached_result.error_message:
                print(f"   Error: {cached_result.error_message}")
        else:
            print("   ✗ Not found in cache")
            print("   Running test now...")

            # Run the test since it's not cached
            result = test_runner.run_test(params)

            # Cache the new result
            cache.cache_result(params, result, result.metric_score)

            print(f"   ✓ Test completed and cached")
            print(f"   Score: {result.metric_score:.3f}")
            print(f"   Success: {result.success}")
            print(f"   Execution time: {result.execution_time:.3f}s")
            if result.error_message:
                print(f"   Error: {result.error_message}")


def main():
    """Run cache query demonstration."""
    print("Parameter Optimizer Cache Query Demo")
    print("=" * 40)

    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Set up components
        print("1. Setting up components...")
        test_runner = TestRunner(DemoMLModel, accuracy_metric)
        cache = ResultCache(temp_dir, "DemoMLModel")

        # 2. Pre-populate cache with some results
        print("2. Pre-populating cache with some test results...")

        initial_params = [
            {"learning_rate": 0.01, "batch_size": 32, "optimizer": "adam"},
            {"learning_rate": 0.001, "batch_size": 64, "optimizer": "sgd"},
            {"learning_rate": 0.1, "batch_size": 16, "optimizer": "rmsprop"},
        ]

        for params in initial_params:
            result = test_runner.run_test(params)
            cache.cache_result(params, result, result.metric_score)
            print(f"   Cached: {params} -> Score: {result.metric_score:.3f}")

        # 3. Show cache stats
        print("\n3. Current cache statistics:")
        stats = cache.get_cache_stats()
        print(f"   Total cached results: {stats['total_cached']}")
        print(f"   Successful results: {stats['successful_cached']}")
        print(f"   Failed results: {stats['failed_cached']}")

        # 4. Query specific parameter combinations
        print("\n4. Querying specific parameter combinations...")

        # Mix of cached and non-cached parameters
        query_params = [
            # This should be in cache (from step 2)
            {"learning_rate": 0.01, "batch_size": 32, "optimizer": "adam"},

            # This should be in cache (from step 2)
            {"learning_rate": 0.001, "batch_size": 64, "optimizer": "sgd"},

            # This should NOT be in cache (new combination)
            {"learning_rate": 0.005, "batch_size": 128, "optimizer": "adam"},

            # This should NOT be in cache (new combination)
            {"learning_rate": 0.01, "batch_size": 64, "optimizer": "adam"},

            # This should be in cache (from step 2)
            {"learning_rate": 0.1, "batch_size": 16, "optimizer": "rmsprop"},
        ]

        query_specific_parameters(cache, test_runner, query_params)

        # 5. Show updated cache stats
        print("\n5. Updated cache statistics:")
        updated_stats = cache.get_cache_stats()
        print(f"   Total cached results: {updated_stats['total_cached']}")
        print(f"   Successful results: {updated_stats['successful_cached']}")
        print(f"   Failed results: {updated_stats['failed_cached']}")

        # 6. Query the same parameters again to show cache hits
        print("\n6. Querying the same parameters again (should all be cache hits):")
        query_specific_parameters(cache, test_runner, query_params)

        # 7. Demonstrate finding best cached result
        print("\n7. Finding best result from all cached tests:")
        evaluator = MetricEvaluator(accuracy_metric, maximize=True)

        # Get all cached results
        all_cached_results = []
        for params in query_params:
            cached_result = cache.get_cached_result(params)
            if cached_result:
                all_cached_results.append(cached_result)

        if all_cached_results:
            best_result = evaluator.compare_results(all_cached_results)
            print(f"   Best configuration: {best_result.parameters}")
            print(f"   Best score: {best_result.metric_score:.3f}")
            print(f"   Execution time: {best_result.execution_time:.3f}s")

        print("\n✓ Cache query demonstration completed!")


if __name__ == "__main__":
    main()
