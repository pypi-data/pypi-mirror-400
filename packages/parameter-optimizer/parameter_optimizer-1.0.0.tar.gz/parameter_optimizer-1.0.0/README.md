# Parameter Optimizer

A reusable Python package that systematically tests different parameter combinations for a given class to find the optimal configuration based on a specified metric. Perfect for hyperparameter optimization, configuration tuning, and systematic testing.

## Features

- **🔧 Flexible Parameter Configuration**: Define parameter ranges in JSON format
- **💾 Intelligent Caching**: Avoid duplicate tests with persistent result caching
- **📌 Fixed Parameter Support**: Lock certain parameters while optimizing others
- **📊 Progress Tracking**: Monitor optimization progress and view detailed results
- **🛡️ Error Handling**: Graceful handling of test failures and invalid configurations
- **🔌 Universal Integration**: Works with any class that accepts keyword arguments
- **📈 Resource Management**: Built-in memory monitoring and batch processing
- **🎯 Multiple Metrics**: Support for custom metric functions and optimization goals

## Installation

### From PyPI (Recommended)

```bash
pip install parameter-optimizer
```

### For Development

```bash
git clone https://github.com/parameter-optimizer/parameter-optimizer.git
cd parameter-optimizer
pip install -e ".[dev]"
```

### With Optional Dependencies

```bash
# For testing
pip install parameter-optimizer[test]

# For development
pip install parameter-optimizer[dev]
```

## Quick Start

### 1. Basic Usage

```python
from parameter_optimizer import ParameterOptimizer

# Define your target class
class MyModel:
    def __init__(self, learning_rate, batch_size, epochs):
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        # Your model initialization here
    
    def train_and_evaluate(self):
        # Your training logic here
        # Return a performance metric (higher = better)
        return accuracy_score

# Define metric function
def metric_function(model_instance):
    return model_instance.train_and_evaluate()

# Create optimizer
optimizer = ParameterOptimizer(
    target_class=MyModel,
    parameters_json_path="parameters.json",
    metric_function=metric_function
)

# Run optimization
best_config = optimizer.optimize()
print(f"Best configuration: {best_config}")

# Get detailed results
results = optimizer.get_results()
summary = optimizer.get_optimization_summary()
```

### 2. Parameter Configuration

Create a JSON file (`parameters.json`) with parameter ranges:

```json
{
    "learning_rate": [0.001, 0.01, 0.1],
    "batch_size": [16, 32, 64],
    "epochs": [10, 20, 50]
}
```

### 3. Advanced Usage with Fixed Parameters

```python
# Fix some parameters while optimizing others
optimizer = ParameterOptimizer(
    target_class=MyModel,
    parameters_json_path="parameters.json",
    metric_function=metric_function,
    fixed_parameters={"epochs": 20},  # Fix epochs to 20
    cache_dir="./my_cache"
)

# Run optimization with progress tracking
def progress_callback(current, total, best_score, best_config):
    print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")
    if best_config:
        print(f"Current best: {best_config} (score: {best_score:.3f})")

best_config = optimizer.optimize(progress_callback=progress_callback)
```

## Examples

The package includes comprehensive examples for different use cases:

- **Machine Learning**: Hyperparameter optimization for ML models
- **Database Tuning**: Connection pool and query optimization
- **Web Server**: Multi-objective optimization for performance
- **Game AI**: Player satisfaction optimization
- **Cache Systems**: Memory and performance tuning

Run examples:

```bash
python examples/usage_examples.py
python examples/integration_tests.py
```

## API Reference

### ParameterOptimizer

Main class for parameter optimization.

```python
ParameterOptimizer(
    target_class,           # Class to optimize
    parameters_json_path,   # Path to parameter configuration
    metric_function,        # Function to evaluate performance
    cache_dir="./optimization_cache",  # Cache directory
    fixed_parameters=None   # Dict of fixed parameters
)
```

**Methods:**
- `optimize(max_combinations=None, progress_callback=None)`: Run optimization
- `get_results(sort_by_metric=True)`: Get all test results
- `get_progress()`: Get current progress information
- `get_optimization_summary()`: Get comprehensive summary

### Data Models

- **TestResult**: Individual test result with parameters, score, and metadata
- **OptimizationSummary**: Complete optimization summary with statistics

## Requirements

- Python 3.8+
- psutil (for resource monitoring)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=parameter_optimizer

# Run specific test categories
pytest tests/                    # Unit tests
pytest examples/integration_tests.py  # Integration tests
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial stable release
- Complete parameter optimization functionality
- Comprehensive caching system
- Resource management and monitoring
- Full test coverage and examples