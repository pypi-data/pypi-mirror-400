#!/usr/bin/env python3
"""
Integration demonstration script for parameter optimizer.

This script demonstrates that all core components work together
by running a simple optimization scenario.
"""

import json
import tempfile
from pathlib import Path

from parameter_optimizer.config_manager import ConfigurationManager
from parameter_optimizer.test_runner import TestRunner
from parameter_optimizer.result_cache import ResultCache
from parameter_optimizer.metric_evaluator import MetricEvaluator


class DemoMLModel:
    """Demo machine learning model for optimization testing."""

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


def main():
    """Run integration demonstration."""
    print("Parameter Optimizer Integration Demo")
    print("=" * 40)

    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Create parameter configuration
        print("1. Setting up parameter configuration...")
        param_file = Path(temp_dir) / "demo_params.json"
        parameters = {
            "learning_rate": [0.001, 0.01, 0.1],
            "batch_size": [16, 32, 64, 128],
            "optimizer": ["adam", "sgd", "rmsprop"]
        }

        with open(param_file, 'w') as f:
            json.dump(parameters, f, indent=2)

        print(
            f"   Created parameter file with {len(parameters)} parameter types")

        # 2. Initialize components
        print("2. Initializing core components...")
        config_manager = ConfigurationManager(str(param_file))
        test_runner = TestRunner(DemoMLModel, accuracy_metric)
        cache = ResultCache(temp_dir, "DemoMLModel")
        evaluator = MetricEvaluator(accuracy_metric, maximize=True)

        print("   ✓ ConfigurationManager initialized")
        print("   ✓ TestRunner initialized")
        print("   ✓ ResultCache initialized")
        print("   ✓ MetricEvaluator initialized")

        # 3. Generate parameter combinations
        print("3. Generating parameter combinations...")
        combinations = list(config_manager.generate_combinations())
        total_combinations = len(combinations)
        print(f"   Generated {total_combinations} parameter combinations")

        # 4. Run optimization
        print("4. Running optimization tests...")
        results = []

        for i, params in enumerate(combinations, 1):
            # Check cache first
            cached_result = cache.get_cached_result(params)

            if cached_result:
                results.append(cached_result)
                print(f"   [{i:2d}/{total_combinations}] Cached: {params}")
            else:
                # Run test
                result = test_runner.run_test(params)
                results.append(result)

                # Cache the result
                cache.cache_result(params, result, result.metric_score)

                status = "✓" if result.success else "✗"
                score = f"{result.metric_score:.3f}" if result.success else "FAILED"
                print(
                    f"   [{i:2d}/{total_combinations}] {status} Score: {score} | {params}")

        # 5. Analyze results
        print("5. Analyzing results...")
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        print(f"   Total tests: {len(results)}")
        print(f"   Successful: {len(successful_results)}")
        print(f"   Failed: {len(failed_results)}")

        if successful_results:
            best_result = evaluator.compare_results(results)
            print(f"   Best score: {best_result.metric_score:.3f}")
            print(f"   Best config: {best_result.parameters}")

        # 6. Test caching
        print("6. Testing cache functionality...")
        cache_stats = cache.get_cache_stats()
        print(f"   Cached results: {cache_stats['total_cached']}")

        # Run same optimization again to test cache hits
        print("   Running optimization again to test caching...")
        cached_count = 0
        for params in combinations[:3]:  # Test first 3 combinations
            cached_result = cache.get_cached_result(params)
            if cached_result:
                cached_count += 1

        print(f"   Cache hits: {cached_count}/3")

        print("\n✓ Integration demonstration completed successfully!")
        print("✓ All core components are working together correctly!")


if __name__ == "__main__":
    main()
