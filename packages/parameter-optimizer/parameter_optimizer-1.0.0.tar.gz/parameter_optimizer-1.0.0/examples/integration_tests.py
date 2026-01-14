"""
Integration tests for parameter optimizer examples.

This module provides comprehensive integration tests that validate the complete
parameter optimization workflows with realistic parameter spaces and classes.
"""

from examples.target_classes import (
    SimpleMLModel, DatabaseConnection, WebServerConfig,
    GameAI, CacheSystem
)
from parameter_optimizer import ParameterOptimizer
import os
import sys
import unittest
import tempfile
import shutil
import json
from pathlib import Path

# Add the parent directory to the path so we can import the parameter_optimizer
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestParameterOptimizerIntegration(unittest.TestCase):
    """Integration tests for the parameter optimizer with example classes."""

    def setUp(self):
        """Set up test environment with temporary directories and config files."""
        # Create temporary directory for test cache
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "test_cache")

        # Create temporary config files
        self.config_dir = os.path.join(self.temp_dir, "configs")
        os.makedirs(self.config_dir, exist_ok=True)

        # Create test configuration files
        self._create_test_configs()

    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_test_configs(self):
        """Create test configuration files."""
        # Small ML config for quick testing
        ml_config = {
            "learning_rate": [0.01, 0.1],
            "batch_size": [32, 64],
            "epochs": [10, 20],
            "optimizer": ["adam", "sgd"]
        }
        self.ml_config_path = os.path.join(self.config_dir, "ml_test.json")
        with open(self.ml_config_path, 'w') as f:
            json.dump(ml_config, f)

        # Database config
        db_config = {
            "pool_size": [10, 20],
            "connection_timeout": [5.0, 10.0],
            "query_timeout": [30.0, 60.0],
            "retry_attempts": [1, 3],
            "compression": ["none", "gzip"]
        }
        self.db_config_path = os.path.join(self.config_dir, "db_test.json")
        with open(self.db_config_path, 'w') as f:
            json.dump(db_config, f)

        # Web server config
        web_config = {
            "worker_processes": [2, 4],
            "max_connections": [500, 1000],
            "memory_limit_mb": [256, 512],
            "cache_size_mb": [64, 128]
        }
        self.web_config_path = os.path.join(self.config_dir, "web_test.json")
        with open(self.web_config_path, 'w') as f:
            json.dump(web_config, f)

    def test_ml_model_optimization_complete_workflow(self):
        """Test complete ML model optimization workflow."""
        def accuracy_metric(model_instance):
            return model_instance.get_accuracy()

        optimizer = ParameterOptimizer(
            target_class=SimpleMLModel,
            parameters_json_path=self.ml_config_path,
            metric_function=accuracy_metric,
            cache_dir=self.cache_dir
        )

        # Validate configuration
        validation = optimizer.validate_configuration()
        self.assertTrue(validation['valid'])
        self.assertEqual(validation['parameter_space_size'], 16)  # 2*2*2*2

        # Run optimization
        best_config = optimizer.optimize()

        # Validate results
        self.assertIsInstance(best_config, dict)
        self.assertIn('learning_rate', best_config)
        self.assertIn('batch_size', best_config)
        self.assertIn('epochs', best_config)
        self.assertIn('optimizer', best_config)

        # Test that best config can create a working model
        best_model = SimpleMLModel(**best_config)
        accuracy = best_model.get_accuracy()
        self.assertIsInstance(accuracy, float)
        self.assertGreaterEqual(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)

        # Check optimization summary
        summary = optimizer.get_optimization_summary()
        self.assertEqual(summary.completed_tests, 16)
        self.assertEqual(summary.failed_tests, 0)
        self.assertGreater(summary.best_score, 0.0)

        # Verify all results are available
        results = optimizer.get_results()
        self.assertEqual(len(results), 16)
        self.assertTrue(all(r.success for r in results))

    def test_database_optimization_with_fixed_parameters(self):
        """Test database optimization with fixed parameters."""
        def throughput_metric(db_instance):
            return db_instance.get_throughput()

        fixed_params = {
            "use_ssl": True,
            "retry_attempts": 3
        }

        optimizer = ParameterOptimizer(
            target_class=DatabaseConnection,
            parameters_json_path=self.db_config_path,
            metric_function=throughput_metric,
            fixed_parameters=fixed_params,
            cache_dir=self.cache_dir
        )

        # Validate configuration
        validation = optimizer.validate_configuration()
        self.assertTrue(validation['valid'])
        # Should be 2*2*2*2 = 16 combinations (retry_attempts is fixed)
        self.assertEqual(validation['parameter_space_size'], 16)

        # Run optimization
        best_config = optimizer.optimize()

        # Validate that fixed parameters are in the result
        self.assertEqual(best_config['use_ssl'], True)
        self.assertEqual(best_config['retry_attempts'], 3)

        # Test the best configuration
        best_db = DatabaseConnection(**best_config)
        throughput = best_db.get_throughput()
        self.assertIsInstance(throughput, float)
        self.assertGreater(throughput, 0.0)

        # Verify all results contain fixed parameters
        results = optimizer.get_results()
        for result in results:
            if result.success:
                self.assertEqual(result.parameters['use_ssl'], True)
                self.assertEqual(result.parameters['retry_attempts'], 3)

    def test_web_server_multi_objective_optimization(self):
        """Test web server optimization with composite metric."""
        def composite_metric(server_instance):
            metrics = server_instance.load_test()
            # Balance RPS and response time
            rps_score = min(metrics['requests_per_second'] / 1000, 1.0)
            response_score = max(0, 1.0 - metrics['response_time'] / 200)
            return (rps_score + response_score) / 2

        fixed_params = {
            "gzip_enabled": True,
            "log_level": "info",
            "keep_alive_timeout": 5.0
        }

        optimizer = ParameterOptimizer(
            target_class=WebServerConfig,
            parameters_json_path=self.web_config_path,
            metric_function=composite_metric,
            fixed_parameters=fixed_params,
            cache_dir=self.cache_dir
        )

        # Run optimization with limited combinations
        best_config = optimizer.optimize(max_combinations=10)

        # Validate results
        self.assertIsInstance(best_config, dict)
        self.assertEqual(best_config['gzip_enabled'], True)
        self.assertEqual(best_config['log_level'], "info")
        self.assertEqual(best_config['keep_alive_timeout'], 5.0)

        # Test the configuration works
        best_server = WebServerConfig(**best_config)
        metrics = best_server.load_test()
        self.assertIn('requests_per_second', metrics)
        self.assertIn('response_time', metrics)
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)

        # Verify optimization completed
        progress = optimizer.get_progress()
        self.assertEqual(progress['completed_tests'], 10)
        self.assertTrue(progress['is_complete'])

    def test_caching_functionality(self):
        """Test that caching works correctly across multiple optimization runs."""
        def simple_metric(model_instance):
            return model_instance.get_accuracy()

        # First optimization run
        optimizer1 = ParameterOptimizer(
            target_class=SimpleMLModel,
            parameters_json_path=self.ml_config_path,
            metric_function=simple_metric,
            cache_dir=self.cache_dir
        )

        best_config1 = optimizer1.optimize()
        summary1 = optimizer1.get_optimization_summary()

        # Second optimization run with same parameters (should use cache)
        optimizer2 = ParameterOptimizer(
            target_class=SimpleMLModel,
            parameters_json_path=self.ml_config_path,
            metric_function=simple_metric,
            cache_dir=self.cache_dir
        )

        best_config2 = optimizer2.optimize()
        summary2 = optimizer2.get_optimization_summary()

        # Results should be identical
        self.assertEqual(best_config1, best_config2)
        self.assertEqual(summary1.best_score, summary2.best_score)

        # Second run should have used cached results
        self.assertEqual(summary2.cached_results, 16)  # All results cached
        self.assertLess(summary2.execution_time, summary1.execution_time)

    def test_progress_tracking(self):
        """Test progress tracking functionality."""
        def simple_metric(model_instance):
            return model_instance.get_accuracy()

        optimizer = ParameterOptimizer(
            target_class=SimpleMLModel,
            parameters_json_path=self.ml_config_path,
            metric_function=simple_metric,
            cache_dir=self.cache_dir
        )

        progress_updates = []

        def progress_callback(completed, total, current_best):
            progress_updates.append({
                'completed': completed,
                'total': total,
                'current_best': current_best
            })

        # Run optimization with progress tracking
        best_config = optimizer.optimize(progress_callback=progress_callback)

        # Validate progress updates
        self.assertGreater(len(progress_updates), 0)
        self.assertEqual(progress_updates[-1]['completed'], 16)
        self.assertEqual(progress_updates[-1]['total'], 16)

        # Check that progress is monotonically increasing
        for i in range(1, len(progress_updates)):
            self.assertGreaterEqual(
                progress_updates[i]['completed'],
                progress_updates[i-1]['completed']
            )

        # Final progress should match optimization summary
        final_progress = optimizer.get_progress()
        self.assertEqual(final_progress['completed_tests'], 16)
        self.assertTrue(final_progress['is_complete'])
        self.assertEqual(final_progress['progress_percentage'], 100.0)

    def test_error_handling_and_validation(self):
        """Test error handling and input validation."""
        def simple_metric(model_instance):
            return model_instance.get_accuracy()

        # Test with invalid JSON file
        invalid_config_path = os.path.join(self.config_dir, "invalid.json")
        with open(invalid_config_path, 'w') as f:
            f.write("invalid json content")

        with self.assertRaises(Exception):
            optimizer = ParameterOptimizer(
                target_class=SimpleMLModel,
                parameters_json_path=invalid_config_path,
                metric_function=simple_metric,
                cache_dir=self.cache_dir
            )
            optimizer.optimize()

        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            ParameterOptimizer(
                target_class=SimpleMLModel,
                parameters_json_path="non_existent_file.json",
                metric_function=simple_metric,
                cache_dir=self.cache_dir
            )

        # Test with invalid target class
        with self.assertRaises(TypeError):
            ParameterOptimizer(
                target_class="not_a_class",
                parameters_json_path=self.ml_config_path,
                metric_function=simple_metric,
                cache_dir=self.cache_dir
            )

        # Test with invalid metric function
        with self.assertRaises(TypeError):
            ParameterOptimizer(
                target_class=SimpleMLModel,
                parameters_json_path=self.ml_config_path,
                metric_function="not_a_function",
                cache_dir=self.cache_dir
            )

    def test_resource_management(self):
        """Test resource management features."""
        def simple_metric(model_instance):
            return model_instance.get_accuracy()

        optimizer = ParameterOptimizer(
            target_class=SimpleMLModel,
            parameters_json_path=self.ml_config_path,
            metric_function=simple_metric,
            cache_dir=self.cache_dir
        )

        # Test memory limit setting
        optimizer.set_memory_limit(256)
        optimizer.set_batch_size(5)

        resource_info = optimizer.get_resource_usage()
        self.assertEqual(resource_info['memory_limit_mb'], 256)
        self.assertEqual(resource_info['batch_size'], 5)

        # Run optimization
        best_config = optimizer.optimize()

        # Check final resource usage
        final_resource_info = optimizer.get_resource_usage()
        self.assertEqual(final_resource_info['completed_tests'], 16)
        self.assertGreaterEqual(final_resource_info['results_in_memory'], 0)

    def test_game_ai_optimization_workflow(self):
        """Test game AI optimization with player satisfaction metric."""
        def satisfaction_metric(ai_instance):
            return ai_instance.get_player_satisfaction()

        # Create a small game AI config for testing
        game_config = {
            "aggression": [0.3, 0.7],
            "exploration_rate": [0.1, 0.2],
            "reaction_time": [0.2, 0.5],
            "memory_depth": [10, 20],
            "strategy": ["balanced", "aggressive"]
        }

        game_config_path = os.path.join(self.config_dir, "game_test.json")
        with open(game_config_path, 'w') as f:
            json.dump(game_config, f)

        fixed_params = {"difficulty": "medium"}

        optimizer = ParameterOptimizer(
            target_class=GameAI,
            parameters_json_path=game_config_path,
            metric_function=satisfaction_metric,
            fixed_parameters=fixed_params,
            cache_dir=self.cache_dir
        )

        # Run optimization
        best_config = optimizer.optimize(max_combinations=20)

        # Validate results
        self.assertEqual(best_config['difficulty'], "medium")
        self.assertIn('aggression', best_config)
        self.assertIn('exploration_rate', best_config)
        self.assertIn('reaction_time', best_config)
        self.assertIn('memory_depth', best_config)
        self.assertIn('strategy', best_config)

        # Test the best AI configuration
        best_ai = GameAI(**best_config)
        satisfaction = best_ai.get_player_satisfaction()
        self.assertIsInstance(satisfaction, float)
        self.assertGreaterEqual(satisfaction, 0.0)
        self.assertLessEqual(satisfaction, 1.0)

    def test_cache_system_optimization_workflow(self):
        """Test cache system optimization with efficiency metric."""
        def efficiency_metric(cache_instance):
            metrics = cache_instance.benchmark_cache()
            return (metrics['hit_rate'] * 0.6 +
                    (1.0 - metrics['average_latency'] / 5.0) * 0.2 +
                    metrics['memory_efficiency'] * 0.2)

        # Create a small cache config for testing
        cache_config = {
            "max_size_mb": [128, 256],
            "ttl_seconds": [1800, 3600],
            "eviction_policy": ["lru", "lfu"],
            "compression_enabled": [True, False]
        }

        cache_config_path = os.path.join(self.config_dir, "cache_test.json")
        with open(cache_config_path, 'w') as f:
            json.dump(cache_config, f)

        fixed_params = {
            "prefetch_enabled": True,
            "write_through": False
        }

        optimizer = ParameterOptimizer(
            target_class=CacheSystem,
            parameters_json_path=cache_config_path,
            metric_function=efficiency_metric,
            fixed_parameters=fixed_params,
            cache_dir=self.cache_dir
        )

        # Run optimization
        best_config = optimizer.optimize()

        # Validate results
        self.assertEqual(best_config['prefetch_enabled'], True)
        self.assertEqual(best_config['write_through'], False)
        self.assertIn('max_size_mb', best_config)
        self.assertIn('ttl_seconds', best_config)
        self.assertIn('eviction_policy', best_config)
        self.assertIn('compression_enabled', best_config)

        # Test the best cache configuration
        best_cache = CacheSystem(**best_config)
        efficiency = efficiency_metric(best_cache)
        self.assertIsInstance(efficiency, float)
        self.assertGreater(efficiency, 0.0)


class TestParameterOptimizerEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "test_cache")
        self.config_dir = os.path.join(self.temp_dir, "configs")
        os.makedirs(self.config_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_single_parameter_optimization(self):
        """Test optimization with only one parameter."""
        single_param_config = {
            "learning_rate": [0.01, 0.1, 0.5]
        }

        config_path = os.path.join(self.config_dir, "single_param.json")
        with open(config_path, 'w') as f:
            json.dump(single_param_config, f)

        def simple_metric(model_instance):
            return model_instance.get_accuracy()

        fixed_params = {
            "batch_size": 32,
            "epochs": 10,
            "regularization": 0.001,
            "optimizer": "adam"
        }

        optimizer = ParameterOptimizer(
            target_class=SimpleMLModel,
            parameters_json_path=config_path,
            metric_function=simple_metric,
            fixed_parameters=fixed_params,
            cache_dir=self.cache_dir
        )

        best_config = optimizer.optimize()

        # Should have all fixed parameters plus the optimized one
        self.assertEqual(len(best_config), 5)
        self.assertIn('learning_rate', best_config)
        self.assertEqual(best_config['batch_size'], 32)
        self.assertEqual(best_config['epochs'], 10)
        self.assertEqual(best_config['regularization'], 0.001)
        self.assertEqual(best_config['optimizer'], "adam")

    def test_empty_parameter_space(self):
        """Test handling of empty parameter configuration."""
        empty_config = {}

        config_path = os.path.join(self.config_dir, "empty.json")
        with open(config_path, 'w') as f:
            json.dump(empty_config, f)

        def simple_metric(model_instance):
            return model_instance.get_accuracy()

        fixed_params = {
            "learning_rate": 0.01,
            "batch_size": 32,
            "epochs": 10,
            "regularization": 0.001,
            "optimizer": "adam"
        }

        # Empty parameter configuration should raise an error
        with self.assertRaises(ValueError):
            optimizer = ParameterOptimizer(
                target_class=SimpleMLModel,
                parameters_json_path=config_path,
                metric_function=simple_metric,
                fixed_parameters=fixed_params,
                cache_dir=self.cache_dir
            )

    def test_large_parameter_space_handling(self):
        """Test handling of large parameter spaces with memory management."""
        # Create a moderately large parameter space
        large_config = {
            "learning_rate": [0.001, 0.01, 0.1, 0.5, 1.0],
            "batch_size": [16, 32, 64, 128, 256],
            "epochs": [5, 10, 20, 50],
            "regularization": [0.0, 0.001, 0.01, 0.1],
            "optimizer": ["adam", "sgd", "rmsprop"]
        }
        # Total: 5 * 5 * 4 * 4 * 3 = 1200 combinations

        config_path = os.path.join(self.config_dir, "large.json")
        with open(config_path, 'w') as f:
            json.dump(large_config, f)

        def simple_metric(model_instance):
            return model_instance.get_accuracy()

        optimizer = ParameterOptimizer(
            target_class=SimpleMLModel,
            parameters_json_path=config_path,
            metric_function=simple_metric,
            cache_dir=self.cache_dir
        )

        # Set small memory limit and batch size for testing
        optimizer.set_memory_limit(64)  # Very small limit
        optimizer.set_batch_size(10)

        # Run with limited combinations
        best_config = optimizer.optimize(max_combinations=50)

        # Should complete successfully
        self.assertIsInstance(best_config, dict)

        progress = optimizer.get_progress()
        self.assertEqual(progress['completed_tests'], 50)
        self.assertTrue(progress['is_complete'])


def run_integration_tests():
    """Run all integration tests."""
    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.makeSuite(TestParameterOptimizerIntegration))
    suite.addTest(unittest.makeSuite(TestParameterOptimizerEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Parameter Optimizer Integration Tests")
    print("=" * 60)

    success = run_integration_tests()

    if success:
        print("\n✓ All integration tests passed!")
    else:
        print("\n✗ Some integration tests failed!")
        sys.exit(1)
