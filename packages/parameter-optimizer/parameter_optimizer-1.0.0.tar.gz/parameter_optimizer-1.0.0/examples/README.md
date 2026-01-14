# Parameter Optimizer Examples

This directory contains comprehensive examples and integration tests demonstrating how to use the Parameter Optimizer package. The examples cover various optimization scenarios, from simple hyperparameter tuning to complex multi-objective optimization.

## Directory Structure

```
examples/
├── target_classes.py          # Example classes for optimization
├── usage_examples.py          # Complete usage examples
├── integration_tests.py       # Comprehensive integration tests
├── configs/                   # Parameter configuration files
│   ├── README.md             # Configuration documentation
│   ├── ml_model_config.json  # ML hyperparameter configs
│   ├── database_config.json  # Database connection configs
│   ├── webserver_config.json # Web server configs
│   ├── game_ai_config.json   # Game AI behavior configs
│   ├── cache_config.json     # Cache system configs
│   └── ...                   # Additional specialized configs
└── README.md                 # This file
```

## Quick Start

### 1. Basic Usage Example

```python
from parameter_optimizer import ParameterOptimizer
from examples.target_classes import SimpleMLModel

def accuracy_metric(model_instance):
    return model_instance.get_accuracy()

optimizer = ParameterOptimizer(
    target_class=SimpleMLModel,
    parameters_json_path="examples/configs/ml_model_small.json",
    metric_function=accuracy_metric
)

best_config = optimizer.optimize()
print(f"Best configuration: {best_config}")
```

### 2. Run All Examples

```bash
cd examples
python usage_examples.py
```

### 3. Run Integration Tests

```bash
cd examples
python integration_tests.py
```

## Example Classes

The `target_classes.py` module provides six different classes that demonstrate various optimization scenarios:

### 1. SimpleMLModel
**Use Case**: Machine learning hyperparameter optimization
**Parameters**: learning_rate, batch_size, epochs, regularization, optimizer
**Metrics**: accuracy, loss, training_time
**Optimization Goal**: Maximize model accuracy

```python
model = SimpleMLModel(learning_rate=0.01, batch_size=64, epochs=20, 
                     regularization=0.001, optimizer="adam")
accuracy = model.get_accuracy()  # Higher is better
```

### 2. DatabaseConnection
**Use Case**: Database connection parameter tuning
**Parameters**: pool_size, connection_timeout, query_timeout, retry_attempts, use_ssl, compression
**Metrics**: throughput, latency, error_rate
**Optimization Goal**: Maximize throughput, minimize latency and errors

```python
db = DatabaseConnection(pool_size=20, connection_timeout=10.0, use_ssl=True)
throughput = db.get_throughput()  # Higher is better
```

### 3. WebServerConfig
**Use Case**: Web server performance optimization
**Parameters**: worker_processes, max_connections, memory_limit_mb, cache_size_mb, keep_alive_timeout, gzip_enabled, log_level
**Metrics**: requests_per_second, response_time, cpu_usage, memory_usage
**Optimization Goal**: Balance throughput, response time, and resource usage

```python
server = WebServerConfig(worker_processes=8, max_connections=2000, gzip_enabled=True)
rps = server.get_requests_per_second()  # Higher is better
```

### 4. GameAI
**Use Case**: Game AI behavior optimization for player satisfaction
**Parameters**: aggression, exploration_rate, reaction_time, memory_depth, strategy, difficulty
**Metrics**: win_rate, average_score, player_satisfaction
**Optimization Goal**: Maximize player satisfaction while maintaining competitive gameplay

```python
ai = GameAI(aggression=0.6, exploration_rate=0.15, strategy="balanced")
satisfaction = ai.get_player_satisfaction()  # Higher is better
```

### 5. CacheSystem
**Use Case**: Caching system performance optimization
**Parameters**: max_size_mb, ttl_seconds, eviction_policy, compression_enabled, prefetch_enabled, write_through
**Metrics**: hit_rate, average_latency, memory_efficiency
**Optimization Goal**: Maximize cache efficiency and hit rate

```python
cache = CacheSystem(max_size_mb=256, eviction_policy="lru", compression_enabled=True)
hit_rate = cache.get_hit_rate()  # Higher is better
```

## Usage Examples

The `usage_examples.py` file contains six comprehensive examples:

### Example 1: ML Hyperparameter Optimization
- Demonstrates basic optimization workflow
- Shows progress tracking and result analysis
- Uses accuracy as the optimization metric

### Example 2: Database Optimization with Fixed Parameters
- Shows how to use fixed parameters for security/compliance requirements
- Optimizes performance while keeping SSL enabled
- Demonstrates throughput optimization

### Example 3: Multi-Objective Web Server Optimization
- Creates composite metrics balancing multiple objectives
- Shows production-focused optimization with constraints
- Balances requests per second, response time, and CPU usage

### Example 4: Game AI Optimization for Player Satisfaction
- Optimizes for player experience rather than AI performance
- Demonstrates domain-specific metric design
- Shows how to balance competitiveness with enjoyment

### Example 5: Cache System Optimization with Performance Comparison
- Compares optimized vs default configurations
- Shows detailed performance analysis
- Demonstrates efficiency improvements

### Example 6: Resource Management and Memory Monitoring
- Shows memory limit configuration
- Demonstrates batch processing for large parameter spaces
- Includes resource usage monitoring

## Integration Tests

The `integration_tests.py` file provides comprehensive test coverage:

### TestParameterOptimizerIntegration
- **test_ml_model_optimization_complete_workflow**: End-to-end ML optimization
- **test_database_optimization_with_fixed_parameters**: Fixed parameter handling
- **test_web_server_multi_objective_optimization**: Composite metric optimization
- **test_caching_functionality**: Cache persistence and reuse
- **test_progress_tracking**: Progress callback functionality
- **test_error_handling_and_validation**: Input validation and error handling
- **test_resource_management**: Memory limits and batch processing
- **test_game_ai_optimization_workflow**: Game AI optimization workflow
- **test_cache_system_optimization_workflow**: Cache system optimization

### TestParameterOptimizerEdgeCases
- **test_single_parameter_optimization**: Single parameter optimization
- **test_empty_parameter_space**: Only fixed parameters
- **test_large_parameter_space_handling**: Memory management with large spaces

## Configuration Files

The `configs/` directory contains example JSON configuration files for different scenarios:

### Standard Configurations
- `ml_model_config.json`: Complete ML hyperparameter space (576 combinations)
- `database_config.json`: Full database optimization (960 combinations)
- `webserver_config.json`: Complete web server tuning (2,304 combinations)
- `game_ai_config.json`: Game AI behavior optimization (1,200 combinations)
- `cache_config.json`: Cache system optimization (600 combinations)

### Specialized Configurations
- `ml_model_small.json`: Reduced parameter space for quick testing (16 combinations)
- `ml_model_fixed_optimizer.json`: For use with fixed optimizer parameter
- `database_fixed_ssl.json`: For use with SSL always enabled
- `webserver_production.json`: Production-focused parameter ranges

## Running the Examples

### Prerequisites
```bash
# Install the parameter optimizer package
pip install -e .

# Or if running from the repository root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Run Individual Examples
```python
# Run a specific example
from examples.usage_examples import example_1_ml_hyperparameter_optimization
result = example_1_ml_hyperparameter_optimization()
```

### Run All Examples
```bash
cd examples
python usage_examples.py
```

### Run Integration Tests
```bash
cd examples
python integration_tests.py
```

### Run with Custom Parameters
```python
from examples.usage_examples import run_all_examples
import os

# Set custom cache directory
os.environ['OPTIMIZATION_CACHE_DIR'] = '/path/to/custom/cache'
results = run_all_examples()
```

## Expected Output

When running the examples, you should see output similar to:

```
Parameter Optimizer - Usage Examples
============================================================
Running comprehensive examples demonstrating various optimization scenarios...

====================  Running Example 1  ====================
Example 1: ML Hyperparameter Optimization
============================================================
Configuration validation:
Valid: True
Parameter space size: 16
Warnings: []

Starting optimization...
Progress: 4/16 (25.0%)
Current best: {'learning_rate': 0.1, 'batch_size': 64, 'epochs': 20, 'optimizer': 'adam'} (accuracy: 0.847)
Progress: 8/16 (50.0%)
...
Optimization completed in 0.15 seconds
Best configuration: {'learning_rate': 0.1, 'batch_size': 64, 'epochs': 20, 'optimizer': 'adam'}
Best accuracy: 0.847

Optimization Summary:
Total combinations tested: 16
Cached results used: 0
Failed tests: 0
Best score: 0.847
✓ Example 1 completed successfully
```

## Performance Considerations

### Parameter Space Size
- Small spaces (< 100 combinations): Run all combinations
- Medium spaces (100-1000 combinations): Consider using `max_combinations`
- Large spaces (> 1000 combinations): Use batch processing and memory limits

### Memory Management
```python
# For large parameter spaces
optimizer.set_memory_limit(512)  # 512 MB limit
optimizer.set_batch_size(50)     # Process in batches of 50
```

### Caching
- Results are automatically cached to avoid re-running identical tests
- Cache is persistent across sessions
- Cache validation ensures compatibility with class/metric changes

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure the package is installed or PYTHONPATH is set
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Configuration File Not Found**
   ```python
   # Use absolute paths or ensure working directory is correct
   config_path = os.path.abspath("examples/configs/ml_model_config.json")
   ```

3. **Memory Issues with Large Parameter Spaces**
   ```python
   # Use memory limits and batch processing
   optimizer.set_memory_limit(256)
   optimizer.set_batch_size(25)
   best_config = optimizer.optimize(max_combinations=100)
   ```

4. **Slow Optimization**
   ```python
   # Start with smaller parameter spaces for testing
   # Use caching to avoid re-running tests
   # Consider using max_combinations to limit search space
   ```

### Debug Mode
```python
# Enable detailed logging (if implemented)
import logging
logging.basicConfig(level=logging.DEBUG)

# Check validation results
validation = optimizer.validate_configuration()
print(f"Validation: {validation}")

# Monitor resource usage
resource_info = optimizer.get_resource_usage()
print(f"Resource usage: {resource_info}")
```

## Extending the Examples

### Creating Custom Target Classes
```python
class MyCustomClass:
    def __init__(self, param1: float, param2: int, param3: str):
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        # Initialize your class
    
    def get_performance_metric(self) -> float:
        # Implement your performance calculation
        return some_performance_value

# Create configuration file
config = {
    "param1": [0.1, 0.5, 1.0],
    "param2": [10, 20, 50],
    "param3": ["option1", "option2", "option3"]
}

# Use with optimizer
def my_metric(instance):
    return instance.get_performance_metric()

optimizer = ParameterOptimizer(
    target_class=MyCustomClass,
    parameters_json_path="my_config.json",
    metric_function=my_metric
)
```

### Custom Metric Functions
```python
# Single objective
def accuracy_metric(model):
    return model.get_accuracy()

# Multi-objective with weights
def composite_metric(instance):
    metrics = instance.get_all_metrics()
    return (metrics['accuracy'] * 0.6 + 
            metrics['speed'] * 0.3 + 
            metrics['efficiency'] * 0.1)

# Minimize instead of maximize
def error_rate_metric(instance):
    error_rate = instance.get_error_rate()
    return -error_rate  # Negative to minimize

# Complex domain-specific metric
def business_value_metric(instance):
    performance = instance.get_performance()
    cost = instance.get_cost()
    reliability = instance.get_reliability()
    
    # Business value calculation
    return (performance * reliability) / cost
```

## Best Practices

1. **Start Small**: Begin with small parameter spaces to validate your setup
2. **Use Fixed Parameters**: Fix parameters that are constrained by your environment
3. **Design Good Metrics**: Ensure your metric function reflects your actual optimization goals
4. **Monitor Progress**: Use progress callbacks to track optimization
5. **Validate Results**: Always test your best configuration in your actual environment
6. **Cache Results**: Take advantage of caching for iterative optimization
7. **Consider Resources**: Set appropriate memory limits for large parameter spaces
8. **Document Assumptions**: Clearly document the assumptions behind your parameter ranges and metrics

## Contributing

To add new examples:

1. Create new target classes in `target_classes.py`
2. Add corresponding configuration files in `configs/`
3. Create usage examples in `usage_examples.py`
4. Add integration tests in `integration_tests.py`
5. Update this README with documentation

Follow the existing patterns and ensure all examples are well-documented and tested.