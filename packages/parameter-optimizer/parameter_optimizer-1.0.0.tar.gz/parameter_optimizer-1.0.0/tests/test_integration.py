"""
Integration tests for parameter optimizer core components.

This module tests that all core components work together correctly
with mock classes and realistic scenarios.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from parameter_optimizer.config_manager import ConfigurationManager
from parameter_optimizer.test_runner import TestRunner
from parameter_optimizer.result_cache import ResultCache
from parameter_optimizer.metric_evaluator import MetricEvaluator
from parameter_optimizer.data_models import TestResult, OptimizationSummary
from parameter_optimizer import ParameterOptimizer


class MockSimpleClass:
    """Simple mock class for testing basic functionality."""

    def __init__(self, learning_rate: float, batch_size: int):
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.accuracy = 0.8 + (learning_rate * 0.1) - (batch_size * 0.001)

    def get_accuracy(self):
        return max(0.0, min(1.0, self.accuracy))


class MockComplexClass:
    """More complex mock class with various parameter types."""

    def __init__(self, optimizer: str, dropout_rate: float,
                 use_batch_norm: bool, hidden_layers: int):
        self.optimizer = optimizer
        self.dropout_rate = dropout_rate
        self.use_batch_norm = use_batch_norm
        self.hidden_layers = hidden_layers

        # Simulate performance calculation
        base_score = 0.7
        if optimizer == "adam":
            base_score += 0.1
        elif optimizer == "sgd":
            base_score += 0.05

        base_score -= dropout_rate * 0.2

        if use_batch_norm:
            base_score += 0.05

        base_score += min(hidden_layers * 0.02, 0.1)

        self.performance = max(0.0, min(1.0, base_score))

    def evaluate(self):
        return self.performance


class MockFailingClass:
    """Mock class that fails with certain parameter combinations."""

    def __init__(self, param1: int, param2: str):
        if param1 < 0:
            raise ValueError("param1 must be non-negative")
        if param2 == "invalid":
            raise RuntimeError("param2 cannot be 'invalid'")

        self.param1 = param1
        self.param2 = param2
        self.score = param1 * 0.1

    def get_score(self):
        return self.score


def simple_metric(instance):
    """Simple metric function for MockSimpleClass."""
    return instance.get_accuracy()


def complex_metric(instance):
    """Complex metric function for MockComplexClass."""
    return instance.evaluate()


def failing_metric(instance):
    """Metric function for MockFailingClass."""
    return instance.get_score()


def test_configuration_manager_integration():
    """Test ConfigurationManager with realistic parameter files."""
    # Create temporary parameter file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        params = {
            "learning_rate": [0.001, 0.01, 0.1],
            "batch_size": [16, 32, 64]
        }
        json.dump(params, f)
        temp_file = f.name

    try:
        # Test basic functionality
        config_manager = ConfigurationManager(temp_file)
        loaded_params = config_manager.load_parameters()

        assert "learning_rate" in loaded_params
        assert "batch_size" in loaded_params
        assert loaded_params["learning_rate"] == [0.001, 0.01, 0.1]
        assert loaded_params["batch_size"] == [16, 32, 64]

        # Test combination generation
        combinations = list(config_manager.generate_combinations())
        assert len(combinations) == 9  # 3 * 3 combinations

        # Verify all combinations are present
        expected_combinations = [
            {"learning_rate": 0.001, "batch_size": 16},
            {"learning_rate": 0.001, "batch_size": 32},
            {"learning_rate": 0.001, "batch_size": 64},
            {"learning_rate": 0.01, "batch_size": 16},
            {"learning_rate": 0.01, "batch_size": 32},
            {"learning_rate": 0.01, "batch_size": 64},
            {"learning_rate": 0.1, "batch_size": 16},
            {"learning_rate": 0.1, "batch_size": 32},
            {"learning_rate": 0.1, "batch_size": 64},
        ]

        for expected in expected_combinations:
            assert expected in combinations

        print("✓ ConfigurationManager integration test passed")

    finally:
        Path(temp_file).unlink()


def test_configuration_manager_with_fixed_parameters():
    """Test ConfigurationManager with fixed parameters."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        params = {
            "learning_rate": [0.001, 0.01],
            "batch_size": [16, 32],
            "optimizer": ["adam", "sgd"]
        }
        json.dump(params, f)
        temp_file = f.name

    try:
        # Test with fixed parameters
        fixed_params = {"optimizer": "adam"}
        config_manager = ConfigurationManager(temp_file, fixed_params)

        combinations = list(config_manager.generate_combinations())
        # 2 * 2 combinations (optimizer is fixed)
        assert len(combinations) == 4

        # Verify all combinations have fixed optimizer
        for combo in combinations:
            assert combo["optimizer"] == "adam"
            assert "learning_rate" in combo
            assert "batch_size" in combo

        print("✓ ConfigurationManager fixed parameters test passed")

    finally:
        Path(temp_file).unlink()


def test_test_runner_integration():
    """Test TestRunner with mock classes."""
    # Test with simple class
    test_runner = TestRunner(MockSimpleClass, simple_metric)

    # Test successful execution
    params = {"learning_rate": 0.01, "batch_size": 32}
    result = test_runner.run_test(params)

    assert isinstance(result, TestResult)
    assert result.success is True
    assert result.parameters == params
    assert isinstance(result.metric_score, float)
    assert result.metric_score > 0
    assert result.error_message is None

    # Test parameter validation
    validation_result = test_runner.validate_parameters(params)
    assert validation_result['valid'] is True
    assert validation_result['error'] is None

    # Test invalid parameters
    invalid_params = {"invalid_param": 123}
    validation_result = test_runner.validate_parameters(invalid_params)
    assert validation_result['valid'] is False
    assert validation_result['error'] is not None

    print("✓ TestRunner integration test passed")


def test_test_runner_with_failures():
    """Test TestRunner handles failures gracefully."""
    test_runner = TestRunner(MockFailingClass, failing_metric)

    # Test with valid parameters
    valid_params = {"param1": 5, "param2": "valid"}
    result = test_runner.run_test(valid_params)
    assert result.success is True
    assert result.metric_score == 0.5  # 5 * 0.1

    # Test with failing parameters
    failing_params = {"param1": -1, "param2": "valid"}
    result = test_runner.run_test(failing_params)
    assert result.success is False
    assert "param1 must be non-negative" in result.error_message
    assert result.metric_score == 0.0  # Default for failed tests

    print("✓ TestRunner failure handling test passed")


def test_result_cache_integration():
    """Test ResultCache with realistic scenarios."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = ResultCache(temp_dir, "MockSimpleClass")

        # Test cache miss
        params = {"learning_rate": 0.01, "batch_size": 32}
        cached_result = cache.get_cached_result(params)
        assert cached_result is None

        # Create and cache a result
        test_result = TestResult(
            parameters=params,
            metric_score=0.85,
            execution_time=0.1,
            timestamp=datetime.now(),
            success=True
        )

        cache.cache_result(params, test_result, test_result.metric_score)

        # Test cache hit
        cached_result = cache.get_cached_result(params)
        assert cached_result is not None
        assert cached_result.parameters == params
        assert cached_result.metric_score == 0.85
        assert cached_result.success is True

        # Test cache stats
        stats = cache.get_cache_stats()
        assert stats["total_cached"] == 1
        assert stats["successful_cached"] == 1
        assert stats["failed_cached"] == 0

        print("✓ ResultCache integration test passed")


def test_metric_evaluator_integration():
    """Test MetricEvaluator with different optimization goals."""
    # Test maximization (default)
    evaluator_max = MetricEvaluator(complex_metric, maximize=True)

    # Create test instances
    instance1 = MockComplexClass("adam", 0.1, True, 3)
    instance2 = MockComplexClass("sgd", 0.2, False, 2)

    score1 = evaluator_max.evaluate(instance1)
    score2 = evaluator_max.evaluate(instance2)

    assert isinstance(score1, float)
    assert isinstance(score2, float)
    assert 0.0 <= score1 <= 1.0
    assert 0.0 <= score2 <= 1.0

    # Create test results
    result1 = TestResult(
        parameters={"optimizer": "adam", "dropout_rate": 0.1,
                    "use_batch_norm": True, "hidden_layers": 3},
        metric_score=score1,
        execution_time=0.1,
        timestamp=datetime.now(),
        success=True
    )

    result2 = TestResult(
        parameters={"optimizer": "sgd", "dropout_rate": 0.2,
                    "use_batch_norm": False, "hidden_layers": 2},
        metric_score=score2,
        execution_time=0.1,
        timestamp=datetime.now(),
        success=True
    )

    results = [result1, result2]

    # Test finding best result
    best_result = evaluator_max.compare_results(results)
    assert best_result is not None
    assert best_result in results

    # Test minimization
    evaluator_min = MetricEvaluator(complex_metric, maximize=False)
    best_result_min = evaluator_min.compare_results(results)
    assert best_result_min is not None

    # Best result should be different for max vs min (unless scores are equal)
    if score1 != score2:
        assert best_result != best_result_min

    print("✓ MetricEvaluator integration test passed")


def test_full_component_integration():
    """Test all components working together in a realistic scenario."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create parameter configuration
        param_file = Path(temp_dir) / "params.json"
        params = {
            "optimizer": ["adam", "sgd"],
            "dropout_rate": [0.1, 0.2],
            "use_batch_norm": [True, False],
            "hidden_layers": [2, 3]
        }

        with open(param_file, 'w') as f:
            json.dump(params, f)

        # Initialize all components
        config_manager = ConfigurationManager(str(param_file))
        test_runner = TestRunner(MockComplexClass, complex_metric)
        cache = ResultCache(temp_dir, "MockComplexClass")
        evaluator = MetricEvaluator(complex_metric, maximize=True)

        # Run optimization simulation
        all_results = []
        combinations = list(config_manager.generate_combinations())

        assert len(combinations) == 16  # 2 * 2 * 2 * 2

        for params in combinations:
            # Check cache first
            cached_result = cache.get_cached_result(params)

            if cached_result:
                all_results.append(cached_result)
            else:
                # Run test
                result = test_runner.run_test(params)
                all_results.append(result)

                # Cache result
                cache.cache_result(params, result, result.metric_score)

        # Verify all tests completed
        assert len(all_results) == 16

        # Find best configuration
        best_result = evaluator.compare_results(all_results)
        assert best_result is not None
        assert best_result.success is True

        # Verify cache is working (run again and check cache hits)
        cached_results = []
        for params in combinations:
            cached_result = cache.get_cached_result(params)
            assert cached_result is not None  # Should all be cached now
            cached_results.append(cached_result)

        assert len(cached_results) == 16

        # Verify cached results match original results
        for original, cached in zip(all_results, cached_results):
            assert original.parameters == cached.parameters
            assert original.metric_score == cached.metric_score
            assert original.success == cached.success

        print("✓ Full component integration test passed")


def test_parameter_optimizer_main_class():
    """Test the main ParameterOptimizer class integration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create parameter configuration
        param_file = Path(temp_dir) / "params.json"
        params = {
            "learning_rate": [0.001, 0.01],
            "batch_size": [16, 32]
        }

        with open(param_file, 'w') as f:
            json.dump(params, f)

        # Create optimizer
        optimizer = ParameterOptimizer(
            target_class=MockSimpleClass,
            parameters_json_path=str(param_file),
            metric_function=simple_metric,
            cache_dir=temp_dir
        )

        # Test optimization
        best_config = optimizer.optimize()
        assert best_config is not None
        assert "learning_rate" in best_config
        assert "batch_size" in best_config

        # Test results retrieval
        results = optimizer.get_results()
        assert len(results) == 4  # 2 * 2 combinations
        assert all(isinstance(r, TestResult) for r in results)

        # Test progress tracking
        progress = optimizer.get_progress()
        assert progress["total_combinations"] == 4
        assert progress["completed_tests"] == 4
        assert progress["is_complete"] is True
        assert progress["progress_percentage"] == 100.0

        # Test optimization summary
        summary = optimizer.get_optimization_summary()
        assert isinstance(summary, OptimizationSummary)
        assert summary.total_combinations == 4
        assert summary.completed_tests == 4
        assert summary.best_configuration == best_config

        # Test with fixed parameters
        optimizer_fixed = ParameterOptimizer(
            target_class=MockSimpleClass,
            parameters_json_path=str(param_file),
            metric_function=simple_metric,
            cache_dir=temp_dir,
            fixed_parameters={"batch_size": 64}
        )

        best_config_fixed = optimizer_fixed.optimize()
        assert best_config_fixed["batch_size"] == 64

        results_fixed = optimizer_fixed.get_results()
        assert len(results_fixed) == 2  # Only learning_rate varies
        assert all(r.parameters["batch_size"] == 64 for r in results_fixed)

        print("✓ ParameterOptimizer main class integration test passed")


def test_error_handling_integration():
    """Test error handling across all components."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test invalid JSON file
        invalid_json_file = Path(temp_dir) / "invalid.json"
        with open(invalid_json_file, 'w') as f:
            f.write("{ invalid json }")

        try:
            config_manager = ConfigurationManager(str(invalid_json_file))
            config_manager.load_parameters()
            assert False, "Should have raised ValueError for invalid JSON"
        except ValueError as e:
            assert "Invalid JSON format" in str(e)

        # Test missing file
        try:
            config_manager = ConfigurationManager("nonexistent.json")
            config_manager.load_parameters()
            assert False, "Should have raised FileNotFoundError for missing file"
        except FileNotFoundError as e:
            assert "Parameter file not found" in str(e)

        # Test invalid metric function
        try:
            evaluator = MetricEvaluator("not_a_function")
            assert False, "Should have raised TypeError"
        except TypeError as e:
            assert "must be callable" in str(e)

        print("✓ Error handling integration test passed")


def run_all_integration_tests():
    """Run all integration tests."""
    print("Running parameter optimizer integration tests...")
    print()

    test_configuration_manager_integration()
    test_configuration_manager_with_fixed_parameters()
    test_test_runner_integration()
    test_test_runner_with_failures()
    test_result_cache_integration()
    test_metric_evaluator_integration()
    test_full_component_integration()
    test_parameter_optimizer_main_class()
    test_error_handling_integration()

    print()
    print("✓ All integration tests passed successfully!")
    print("✓ Core components are working together correctly")


if __name__ == "__main__":
    run_all_integration_tests()
