#!/usr/bin/env python3
"""
Interactive Cache Query Tool

This script allows you to interactively query the cache for specific
parameter combinations and see their performance.
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


def setup_demo_cache(cache, test_runner):
    """Set up a demo cache with some pre-existing results."""
    print("Setting up demo cache with some pre-existing results...")

    demo_params = [
        {"learning_rate": 0.01, "batch_size": 32, "optimizer": "adam"},
        {"learning_rate": 0.001, "batch_size": 64, "optimizer": "sgd"},
        {"learning_rate": 0.1, "batch_size": 16, "optimizer": "rmsprop"},
        {"learning_rate": 0.01, "batch_size": 64, "optimizer": "adam"},
        {"learning_rate": 0.001, "batch_size": 32, "optimizer": "adam"},
        {"learning_rate": 0.1, "batch_size": 128, "optimizer": "sgd"},
    ]

    for params in demo_params:
        result = test_runner.run_test(params)
        cache.cache_result(params, result, result.metric_score)
        print(f"   Cached: {params} -> Score: {result.metric_score:.3f}")

    print(f"\nDemo cache populated with {len(demo_params)} results!")
    return demo_params


def query_parameters(cache, test_runner, params):
    """Query cache for specific parameters and show results."""
    print(f"\nQuerying parameters: {params}")
    print("-" * 60)

    # Check if this combination was already tested
    cached_result = cache.get_cached_result(params)

    if cached_result:
        print("✓ FOUND IN CACHE!")
        print(f"   Score: {cached_result.metric_score:.3f}")
        print(f"   Success: {'Yes' if cached_result.success else 'No'}")
        print(f"   Execution time: {cached_result.execution_time:.4f} seconds")
        print(
            f"   Tested on: {cached_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        if cached_result.error_message:
            print(f"   Error: {cached_result.error_message}")

        return cached_result
    else:
        print("✗ NOT FOUND IN CACHE")
        response = input(
            "   Would you like to run this test now? (y/n): ").lower().strip()

        if response == 'y' or response == 'yes':
            print("   Running test...")
            result = test_runner.run_test(params)
            cache.cache_result(params, result, result.metric_score)

            print("   ✓ Test completed and cached!")
            print(f"   Score: {result.metric_score:.3f}")
            print(f"   Success: {'Yes' if result.success else 'No'}")
            print(f"   Execution time: {result.execution_time:.4f} seconds")
            if result.error_message:
                print(f"   Error: {result.error_message}")

            return result
        else:
            print("   Test skipped.")
            return None


def main():
    """Run interactive cache query tool."""
    print("Interactive Parameter Cache Query Tool")
    print("=" * 40)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up components
        test_runner = TestRunner(DemoMLModel, accuracy_metric)
        cache = ResultCache(temp_dir, "DemoMLModel")
        evaluator = MetricEvaluator(accuracy_metric, maximize=True)

        # Set up demo cache
        demo_params = setup_demo_cache(cache, test_runner)

        print("\nAvailable parameters in demo cache:")
        for i, params in enumerate(demo_params, 1):
            print(f"   {i}. {params}")

        print("\nYou can now query specific parameter combinations!")
        print("Examples of parameter formats:")
        print('   {"learning_rate": 0.01, "batch_size": 32, "optimizer": "adam"}')
        print('   {"learning_rate": 0.001, "batch_size": 64, "optimizer": "sgd"}')
        print("\nSupported values:")
        print("   learning_rate: any float (e.g., 0.001, 0.01, 0.1)")
        print("   batch_size: any integer (e.g., 16, 32, 64, 128)")
        print('   optimizer: "adam", "sgd", or "rmsprop"')

        while True:
            print("\n" + "="*60)
            print("Enter parameter combination to query (or 'quit' to exit):")
            user_input = input("> ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            if user_input.lower() == 'stats':
                stats = cache.get_cache_stats()
                print(f"\nCache Statistics:")
                print(f"   Total cached results: {stats['total_cached']}")
                print(f"   Successful results: {stats['successful_cached']}")
                print(f"   Failed results: {stats['failed_cached']}")
                continue

            if user_input.lower() == 'best':
                # Find best result from cache
                all_results = []
                for params in demo_params:
                    cached_result = cache.get_cached_result(params)
                    if cached_result:
                        all_results.append(cached_result)

                if all_results:
                    best_result = evaluator.compare_results(all_results)
                    print(f"\nBest cached result:")
                    print(f"   Configuration: {best_result.parameters}")
                    print(f"   Score: {best_result.metric_score:.3f}")
                    print(
                        f"   Tested on: {best_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print("\nNo cached results found.")
                continue

            try:
                # Parse the JSON input
                params = json.loads(user_input)

                # Validate required parameters
                required_params = ['learning_rate', 'batch_size', 'optimizer']
                missing_params = [
                    p for p in required_params if p not in params]

                if missing_params:
                    print(
                        f"Error: Missing required parameters: {missing_params}")
                    continue

                # Validate parameter types
                if not isinstance(params['learning_rate'], (int, float)):
                    print("Error: learning_rate must be a number")
                    continue

                if not isinstance(params['batch_size'], int):
                    print("Error: batch_size must be an integer")
                    continue

                if params['optimizer'] not in ['adam', 'sgd', 'rmsprop']:
                    print("Error: optimizer must be 'adam', 'sgd', or 'rmsprop'")
                    continue

                # Query the parameters
                query_parameters(cache, test_runner, params)

            except json.JSONDecodeError:
                print("Error: Invalid JSON format. Please use proper JSON syntax.")
                print(
                    'Example: {"learning_rate": 0.01, "batch_size": 32, "optimizer": "adam"}')
            except Exception as e:
                print(f"Error: {e}")

        print("\nThanks for using the Interactive Cache Query Tool!")


if __name__ == "__main__":
    main()
