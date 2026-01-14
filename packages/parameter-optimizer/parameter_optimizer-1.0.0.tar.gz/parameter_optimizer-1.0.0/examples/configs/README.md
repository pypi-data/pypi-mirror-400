# Parameter Configuration Examples

This directory contains example JSON configuration files for different optimization scenarios. These files demonstrate how to define parameter ranges for various types of classes and use cases.

## Configuration Files

### Machine Learning Model Configurations

- **`ml_model_config.json`** - Complete ML hyperparameter optimization
  - Optimizes learning rate, batch size, epochs, regularization, and optimizer
  - Total combinations: 4 × 4 × 3 × 4 × 3 = 576 combinations

- **`ml_model_small.json`** - Smaller parameter space for quick testing
  - Reduced parameter ranges for faster optimization
  - Total combinations: 2 × 2 × 2 × 2 = 16 combinations

- **`ml_model_fixed_optimizer.json`** - Optimize with fixed optimizer
  - Use with `fixed_parameters={"optimizer": "adam"}` to fix optimizer choice
  - Focuses optimization on numerical hyperparameters only

### Database Connection Configurations

- **`database_config.json`** - Complete database connection optimization
  - Optimizes pool size, timeouts, retry attempts, SSL, and compression
  - Total combinations: 5 × 4 × 4 × 4 × 2 × 3 = 960 combinations

- **`database_fixed_ssl.json`** - Optimize with SSL enabled
  - Use with `fixed_parameters={"use_ssl": True}` for security-required environments
  - Focuses on performance parameters while maintaining security

### Web Server Configurations

- **`webserver_config.json`** - Complete web server optimization
  - Optimizes worker processes, connections, memory, cache, timeouts, and logging
  - Total combinations: 4 × 4 × 3 × 4 × 4 × 2 × 3 = 2,304 combinations

- **`webserver_production.json`** - Production-focused optimization
  - Use with fixed parameters for production constraints:
    ```python
    fixed_parameters={
        "gzip_enabled": True,
        "log_level": "warning",
        "keep_alive_timeout": 5.0
    }
    ```

### Game AI Configurations

- **`game_ai_config.json`** - Game AI behavior optimization
  - Optimizes aggression, exploration, reaction time, memory, strategy, and difficulty
  - Total combinations: 4 × 5 × 4 × 5 × 3 × 2 = 1,200 combinations

### Cache System Configurations

- **`cache_config.json`** - Cache system optimization
  - Optimizes size, TTL, eviction policy, compression, prefetch, and write-through
  - Total combinations: 5 × 5 × 3 × 2 × 2 × 2 = 600 combinations

## Usage Examples

### Basic Usage
```python
from parameter_optimizer import ParameterOptimizer
from examples.target_classes import SimpleMLModel

def accuracy_metric(model_instance):
    return model_instance.get_accuracy()

optimizer = ParameterOptimizer(
    target_class=SimpleMLModel,
    parameters_json_path="examples/configs/ml_model_config.json",
    metric_function=accuracy_metric
)

best_config = optimizer.optimize()
```

### With Fixed Parameters
```python
# Fix the optimizer to "adam" and only optimize other parameters
optimizer = ParameterOptimizer(
    target_class=SimpleMLModel,
    parameters_json_path="examples/configs/ml_model_fixed_optimizer.json",
    metric_function=accuracy_metric,
    fixed_parameters={"optimizer": "adam"}
)

best_config = optimizer.optimize()
```

### Production Web Server Example
```python
from examples.target_classes import WebServerConfig

def performance_metric(server_instance):
    metrics = server_instance.load_test()
    # Composite metric: balance RPS and response time
    return metrics['requests_per_second'] / (metrics['response_time'] / 100)

optimizer = ParameterOptimizer(
    target_class=WebServerConfig,
    parameters_json_path="examples/configs/webserver_production.json",
    metric_function=performance_metric,
    fixed_parameters={
        "gzip_enabled": True,      # Always use compression in production
        "log_level": "warning",    # Reduce logging overhead
        "keep_alive_timeout": 5.0  # Standard keep-alive setting
    }
)

best_config = optimizer.optimize(max_combinations=100)
```

## Parameter Types Supported

The configuration files demonstrate all supported parameter types:

- **Integers**: `"batch_size": [16, 32, 64, 128]`
- **Floats**: `"learning_rate": [0.001, 0.01, 0.1]`
- **Strings**: `"optimizer": ["adam", "sgd", "rmsprop"]`
- **Booleans**: `"use_ssl": [true, false]`

## Best Practices

1. **Start Small**: Use smaller parameter spaces (like `ml_model_small.json`) for initial testing
2. **Use Fixed Parameters**: Fix parameters that are constrained by your environment or requirements
3. **Consider Combinations**: Be mindful of the total number of combinations (multiply all list lengths)
4. **Meaningful Ranges**: Choose parameter ranges that make sense for your specific use case
5. **Incremental Optimization**: Start with coarse ranges, then refine around optimal values

## Creating Custom Configurations

To create your own configuration file:

1. Identify the parameters your target class accepts in its `__init__` method
2. Define reasonable ranges for each parameter based on your domain knowledge
3. Consider which parameters might need to be fixed for your specific use case
4. Test with a small parameter space first to validate your setup

Example template:
```json
{
  "parameter1": [value1, value2, value3],
  "parameter2": [min_val, mid_val, max_val],
  "parameter3": ["option1", "option2"],
  "parameter4": [true, false]
}
```