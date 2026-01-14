"""
Usage examples demonstrating complete parameter optimization workflows.

This module provides end-to-end examples showing how to use the parameter
optimizer with different types of classes and optimization scenarios.
"""

from examples.target_classes import (
    SimpleMLModel, DatabaseConnection, WebServerConfig,
    GameAI, CacheSystem
)
from parameter_optimizer import ParameterOptimizer
import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import the parameter_optimizer
sys.path.insert(0, str(Path(__file__).parent.parent))


def example_1_ml_hyperparameter_optimization():
    """
    Example 1: Machine Learning Hyperparameter Optimization

    This example demonstrates optimizing ML model hyperparameters to maximize accuracy.
    """
    print("=" * 60)
    print("Example 1: ML Hyperparameter Optimization")
    print("=" * 60)

    def accuracy_metric(model_instance):
        """Metric function that returns model accuracy (higher is better)."""
        return model_instance.get_accuracy()

    # Create optimizer with small parameter space for quick demonstration
    optimizer = ParameterOptimizer(
        target_class=SimpleMLModel,
        parameters_json_path="examples/configs/ml_model_small.json",
        metric_function=accuracy_metric,
        cache_dir="./optimization_cache"
    )

    print("Configuration validation:")
    validation = optimizer.validate_configuration()
    print(f"Valid: {validation['valid']}")
    print(f"Parameter space size: {validation['parameter_space_size']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")

    print("\nStarting optimization...")
    start_time = time.time()

    def progress_callback(completed, total, current_best):
        """Progress callback to show optimization progress."""
        percentage = (completed / total) * 100
        print(f"Progress: {completed}/{total} ({percentage:.1f}%)")
        if current_best:
            print(
                f"Current best: {current_best} (accuracy: {accuracy_metric(SimpleMLModel(**current_best)):.3f})")

    # Run optimization
    best_config = optimizer.optimize(progress_callback=progress_callback)

    optimization_time = time.time() - start_time

    print(f"\nOptimization completed in {optimization_time:.2f} seconds")
    print(f"Best configuration: {best_config}")

    # Test the best configuration
    best_model = SimpleMLModel(**best_config)
    best_accuracy = best_model.get_accuracy()
    print(f"Best accuracy: {best_accuracy:.3f}")

    # Get optimization summary
    summary = optimizer.get_optimization_summary()
    print(f"\nOptimization Summary:")
    print(f"Total combinations tested: {summary.completed_tests}")
    print(f"Cached results used: {summary.cached_results}")
    print(f"Failed tests: {summary.failed_tests}")
    print(f"Best score: {summary.best_score:.3f}")

    return best_config, summary


def example_2_database_optimization_with_fixed_parameters():
    """
    Example 2: Database Connection Optimization with Fixed Parameters

    This example shows how to optimize database parameters while keeping
    certain parameters fixed (e.g., SSL enabled for security).
    """
    print("\n" + "=" * 60)
    print("Example 2: Database Optimization with Fixed Parameters")
    print("=" * 60)

    def throughput_metric(db_instance):
        """Metric function that returns database throughput (higher is better)."""
        return db_instance.get_throughput()

    # Fixed parameters for security and compliance requirements
    fixed_params = {
        "use_ssl": True,  # Always use SSL in production
        "compression": "gzip"  # Standard compression for bandwidth savings
    }

    optimizer = ParameterOptimizer(
        target_class=DatabaseConnection,
        parameters_json_path="examples/configs/database_fixed_ssl.json",
        metric_function=throughput_metric,
        fixed_parameters=fixed_params,
        cache_dir="./optimization_cache"
    )

    print(f"Fixed parameters: {fixed_params}")

    validation = optimizer.validate_configuration()
    print(f"Parameter space size: {validation['parameter_space_size']}")

    print("\nStarting optimization...")
    best_config = optimizer.optimize(max_combinations=50)  # Limit for demo

    print(f"Best configuration: {best_config}")

    # Test the best configuration
    best_db = DatabaseConnection(**best_config)
    metrics = best_db.benchmark()
    print(f"Performance metrics:")
    print(f"  Throughput: {metrics['throughput']:.1f} queries/sec")
    print(f"  Latency: {metrics['latency']:.2f} ms")
    print(f"  Error rate: {metrics['error_rate']:.3f}")

    return best_config


def example_3_multi_objective_optimization():
    """
    Example 3: Multi-Objective Optimization

    This example demonstrates optimizing for multiple objectives by creating
    a composite metric that balances different performance aspects.
    """
    print("\n" + "=" * 60)
    print("Example 3: Multi-Objective Web Server Optimization")
    print("=" * 60)

    def composite_metric(server_instance):
        """
        Composite metric that balances multiple objectives:
        - Maximize requests per second
        - Minimize response time
        - Keep CPU usage reasonable (not too high, not too low)
        """
        metrics = server_instance.load_test()

        # Normalize metrics to 0-1 scale
        # Max expected: 1000 RPS
        rps_score = min(metrics['requests_per_second'] / 1000, 1.0)
        # Max acceptable: 200ms
        response_score = max(0, 1.0 - metrics['response_time'] / 200)

        # CPU usage: optimal around 60-80%
        cpu_optimal = 70
        cpu_score = 1.0 - abs(metrics['cpu_usage'] - cpu_optimal) / cpu_optimal
        cpu_score = max(0, cpu_score)

        # Weighted composite score
        composite_score = (rps_score * 0.4 +
                           response_score * 0.4 + cpu_score * 0.2)

        return composite_score

    # Production constraints
    fixed_params = {
        "gzip_enabled": True,
        "log_level": "warning"
    }

    optimizer = ParameterOptimizer(
        target_class=WebServerConfig,
        parameters_json_path="examples/configs/webserver_production.json",
        metric_function=composite_metric,
        fixed_parameters=fixed_params,
        cache_dir="./optimization_cache"
    )

    print("Optimizing for composite metric (RPS + Response Time + CPU Usage)")

    best_config = optimizer.optimize(max_combinations=30)

    print(f"Best configuration: {best_config}")

    # Analyze the best configuration
    best_server = WebServerConfig(**best_config)
    metrics = best_server.load_test()
    composite_score = composite_metric(best_server)

    print(f"Performance analysis:")
    print(f"  Requests/sec: {metrics['requests_per_second']:.1f}")
    print(f"  Response time: {metrics['response_time']:.1f} ms")
    print(f"  CPU usage: {metrics['cpu_usage']:.1f}%")
    print(f"  Memory usage: {metrics['memory_usage']:.1f} MB")
    print(f"  Composite score: {composite_score:.3f}")

    return best_config


def example_4_game_ai_optimization():
    """
    Example 4: Game AI Optimization for Player Satisfaction

    This example shows optimizing game AI parameters to maximize player
    satisfaction while maintaining competitive gameplay.
    """
    print("\n" + "=" * 60)
    print("Example 4: Game AI Optimization for Player Satisfaction")
    print("=" * 60)

    def player_satisfaction_metric(ai_instance):
        """Metric function that returns player satisfaction (higher is better)."""
        return ai_instance.get_player_satisfaction()

    # Fix difficulty level for this optimization
    fixed_params = {
        "difficulty": "medium"  # Target medium difficulty for broad appeal
    }

    optimizer = ParameterOptimizer(
        target_class=GameAI,
        parameters_json_path="examples/configs/game_ai_config.json",
        metric_function=player_satisfaction_metric,
        fixed_parameters=fixed_params,
        cache_dir="./optimization_cache"
    )

    print("Optimizing AI parameters for maximum player satisfaction")

    best_config = optimizer.optimize(max_combinations=40)

    print(f"Best AI configuration: {best_config}")

    # Analyze the best AI
    best_ai = GameAI(**best_config)
    ai_metrics = best_ai.simulate_games()

    print(f"AI Performance Analysis:")
    print(f"  Win rate: {ai_metrics['win_rate']:.1%}")
    print(f"  Average score: {ai_metrics['average_score']:.0f}")
    print(f"  Player satisfaction: {ai_metrics['player_satisfaction']:.3f}")

    # Show how different metrics compare
    results = optimizer.get_results()
    print(f"\nTop 3 configurations by player satisfaction:")
    for i, result in enumerate(results[:3]):
        if result.success:
            ai = GameAI(**result.parameters)
            metrics = ai.simulate_games()
            print(f"  {i+1}. Satisfaction: {metrics['player_satisfaction']:.3f}, "
                  f"Win rate: {metrics['win_rate']:.1%}, "
                  f"Config: {result.parameters}")

    return best_config


def example_5_cache_optimization_comparison():
    """
    Example 5: Cache System Optimization with Performance Comparison

    This example demonstrates optimizing cache parameters and comparing
    different optimization strategies.
    """
    print("\n" + "=" * 60)
    print("Example 5: Cache System Optimization Comparison")
    print("=" * 60)

    def cache_efficiency_metric(cache_instance):
        """
        Composite metric for cache efficiency:
        - High hit rate (most important)
        - Low latency
        - High memory efficiency
        """
        metrics = cache_instance.benchmark_cache()

        # Weighted score emphasizing hit rate
        efficiency_score = (metrics['hit_rate'] * 0.6 +
                            # Normalize latency
                            (1.0 - metrics['average_latency'] / 5.0) * 0.2 +
                            metrics['memory_efficiency'] * 0.2)

        return max(0, efficiency_score)

    optimizer = ParameterOptimizer(
        target_class=CacheSystem,
        parameters_json_path="examples/configs/cache_config.json",
        metric_function=cache_efficiency_metric,
        cache_dir="./optimization_cache"
    )

    print("Optimizing cache parameters for maximum efficiency")

    # Run optimization with progress tracking
    progress_data = []

    def detailed_progress_callback(completed, total, current_best):
        progress_data.append({
            'completed': completed,
            'total': total,
            'current_best': current_best
        })
        if completed % 20 == 0 or completed == total:  # Report every 20 tests
            percentage = (completed / total) * 100
            print(f"Progress: {completed}/{total} ({percentage:.1f}%)")

    best_config = optimizer.optimize(
        max_combinations=60,
        progress_callback=detailed_progress_callback
    )

    print(f"Best cache configuration: {best_config}")

    # Detailed analysis of the best configuration
    best_cache = CacheSystem(**best_config)
    cache_metrics = best_cache.benchmark_cache()

    print(f"Cache Performance Analysis:")
    print(f"  Hit rate: {cache_metrics['hit_rate']:.1%}")
    print(f"  Average latency: {cache_metrics['average_latency']:.2f} ms")
    print(f"  Memory efficiency: {cache_metrics['memory_efficiency']:.1%}")
    print(f"  Efficiency score: {cache_efficiency_metric(best_cache):.3f}")

    # Compare with default configuration
    default_cache = CacheSystem()  # Use default parameters
    default_metrics = default_cache.benchmark_cache()
    default_score = cache_efficiency_metric(default_cache)

    print(f"\nComparison with default configuration:")
    print(f"  Default efficiency score: {default_score:.3f}")
    print(
        f"  Improvement: {((cache_efficiency_metric(best_cache) - default_score) / default_score * 100):+.1f}%")

    # Show optimization progress
    print(f"\nOptimization progress:")
    print(f"  Total tests run: {len(progress_data)}")
    if len(progress_data) > 1:
        first_best = progress_data[1]['current_best'] if progress_data[1]['current_best'] else {
        }
        if first_best:
            first_cache = CacheSystem(**first_best)
            first_score = cache_efficiency_metric(first_cache)
            final_score = cache_efficiency_metric(best_cache)
            print(
                f"  Score improvement during optimization: {((final_score - first_score) / first_score * 100):+.1f}%")

    return best_config, progress_data


def example_6_resource_management():
    """
    Example 6: Resource Management and Memory Monitoring

    This example demonstrates the optimizer's resource management capabilities
    and shows how to monitor memory usage during optimization.
    """
    print("\n" + "=" * 60)
    print("Example 6: Resource Management and Memory Monitoring")
    print("=" * 60)

    def simple_metric(model_instance):
        return model_instance.get_accuracy()

    optimizer = ParameterOptimizer(
        target_class=SimpleMLModel,
        parameters_json_path="examples/configs/ml_model_config.json",
        metric_function=simple_metric,
        cache_dir="./optimization_cache"
    )

    # Configure resource limits
    optimizer.set_memory_limit(512)  # 512 MB limit
    optimizer.set_batch_size(50)     # Process in batches of 50

    print("Resource configuration:")
    resource_info = optimizer.get_resource_usage()
    print(f"  Memory limit: {resource_info['memory_limit_mb']} MB")
    print(f"  Batch size: {resource_info['batch_size']}")

    # Monitor resource usage during optimization
    def resource_monitoring_callback(completed, total, current_best):
        if completed % 50 == 0:  # Check every 50 tests
            resource_info = optimizer.get_resource_usage()
            print(f"Progress: {completed}/{total}")
            print(
                f"  Memory usage: {resource_info.get('current_memory_mb', 'N/A')} MB")
            print(f"  Results in memory: {resource_info['results_in_memory']}")
            print(f"  Cache hits: {resource_info['cached_results']}")

    print("\nStarting optimization with resource monitoring...")
    best_config = optimizer.optimize(
        max_combinations=200,
        progress_callback=resource_monitoring_callback
    )

    print(f"Best configuration: {best_config}")

    # Final resource usage report
    final_resource_info = optimizer.get_resource_usage()
    print(f"\nFinal resource usage:")
    print(
        f"  Peak memory: {final_resource_info.get('current_memory_mb', 'N/A')} MB")
    print(f"  Total tests: {final_resource_info['completed_tests']}")
    print(
        f"  Cache efficiency: {final_resource_info['cached_results']}/{final_resource_info['completed_tests']}")

    return best_config


def run_all_examples():
    """Run all usage examples in sequence."""
    print("Parameter Optimizer - Usage Examples")
    print("=" * 60)
    print("Running comprehensive examples demonstrating various optimization scenarios...")

    examples = [
        example_1_ml_hyperparameter_optimization,
        example_2_database_optimization_with_fixed_parameters,
        example_3_multi_objective_optimization,
        example_4_game_ai_optimization,
        example_5_cache_optimization_comparison,
        example_6_resource_management
    ]

    results = {}

    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\n{'='*20} Running Example {i} {'='*20}")
            result = example_func()
            results[example_func.__name__] = result
            print(f"✓ Example {i} completed successfully")
        except Exception as e:
            print(f"✗ Example {i} failed: {e}")
            results[example_func.__name__] = None

    print("\n" + "=" * 60)
    print("All Examples Summary")
    print("=" * 60)

    for example_name, result in results.items():
        status = "✓ Success" if result is not None else "✗ Failed"
        print(f"{example_name}: {status}")

    return results


if __name__ == "__main__":
    # Ensure the examples directory exists
    os.makedirs("examples/configs", exist_ok=True)

    # Run all examples
    results = run_all_examples()

    print(f"\nExamples completed. Check the './optimization_cache' directory for cached results.")
