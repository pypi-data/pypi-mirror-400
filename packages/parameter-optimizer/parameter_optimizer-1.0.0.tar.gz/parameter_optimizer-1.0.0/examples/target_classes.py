"""
Example target classes for parameter optimization testing.

This module provides various classes that demonstrate different parameter types
and optimization scenarios for the parameter optimizer.
"""

import math
import random
import time
from typing import List, Dict, Any, Optional


class SimpleMLModel:
    """
    A simple machine learning model simulator for parameter optimization.

    Demonstrates optimization of common ML hyperparameters like learning rate,
    batch size, and regularization parameters.
    """

    def __init__(self, learning_rate: float = 0.01, batch_size: int = 32,
                 epochs: int = 10, regularization: float = 0.001,
                 optimizer: str = "adam"):
        """
        Initialize the ML model with hyperparameters.

        Args:
            learning_rate: Learning rate for training (0.0001 to 1.0)
            batch_size: Batch size for training (1 to 512)
            epochs: Number of training epochs (1 to 100)
            regularization: L2 regularization strength (0.0 to 1.0)
            optimizer: Optimizer type ("adam", "sgd", "rmsprop")
        """
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.regularization = regularization
        self.optimizer = optimizer

        # Validate parameters
        if not 0.0001 <= learning_rate <= 1.0:
            raise ValueError(
                f"Learning rate must be between 0.0001 and 1.0, got {learning_rate}")
        if not 1 <= batch_size <= 512:
            raise ValueError(
                f"Batch size must be between 1 and 512, got {batch_size}")
        if not 1 <= epochs <= 100:
            raise ValueError(f"Epochs must be between 1 and 100, got {epochs}")
        if not 0.0 <= regularization <= 1.0:
            raise ValueError(
                f"Regularization must be between 0.0 and 1.0, got {regularization}")
        if optimizer not in ["adam", "sgd", "rmsprop"]:
            raise ValueError(
                f"Optimizer must be one of ['adam', 'sgd', 'rmsprop'], got {optimizer}")

        # Simulate training results
        self._accuracy = None
        self._loss = None
        self._training_time = None

    def train(self) -> Dict[str, float]:
        """
        Simulate model training and return performance metrics.

        Returns:
            Dict with accuracy, loss, and training time
        """
        # Simulate training time based on parameters
        base_time = 0.1  # Base training time
        time_factor = (self.epochs * self.batch_size) / 1000
        self._training_time = base_time + time_factor + random.uniform(0, 0.05)

        # Simulate accuracy based on hyperparameters
        # Optimal learning rate around 0.01, optimal batch size around 64
        lr_factor = 1.0 - \
            abs(math.log10(self.learning_rate) + 2) / 2  # Peak at 0.01
        batch_factor = 1.0 - abs(self.batch_size - 64) / 64  # Peak at 64
        # Diminishing returns after 20 epochs
        epoch_factor = min(self.epochs / 20, 1.0)
        reg_factor = 1.0 - self.regularization * 0.5  # Light regularization is good

        # Optimizer effects
        optimizer_bonus = {"adam": 0.05, "sgd": 0.0,
                           "rmsprop": 0.03}[self.optimizer]

        # Calculate accuracy with some randomness
        base_accuracy = 0.7
        accuracy_boost = (lr_factor + batch_factor +
                          epoch_factor + reg_factor) / 4 * 0.25
        noise = random.uniform(-0.02, 0.02)

        self._accuracy = base_accuracy + accuracy_boost + optimizer_bonus + noise
        self._accuracy = max(0.0, min(1.0, self._accuracy))  # Clamp to [0, 1]

        # Loss is inversely related to accuracy
        self._loss = 1.0 - self._accuracy + random.uniform(0, 0.1)

        return {
            'accuracy': self._accuracy,
            'loss': self._loss,
            'training_time': self._training_time
        }

    def get_accuracy(self) -> float:
        """Get model accuracy (higher is better)."""
        if self._accuracy is None:
            self.train()
        return self._accuracy

    def get_loss(self) -> float:
        """Get model loss (lower is better)."""
        if self._loss is None:
            self.train()
        return self._loss

    def get_training_time(self) -> float:
        """Get training time in seconds."""
        if self._training_time is None:
            self.train()
        return self._training_time


class DatabaseConnection:
    """
    A database connection simulator for optimizing connection parameters.

    Demonstrates optimization of database connection settings like pool size,
    timeout values, and connection strategies.
    """

    def __init__(self, pool_size: int = 10, connection_timeout: float = 5.0,
                 query_timeout: float = 30.0, retry_attempts: int = 3,
                 use_ssl: bool = True, compression: str = "none"):
        """
        Initialize database connection with parameters.

        Args:
            pool_size: Connection pool size (1 to 100)
            connection_timeout: Connection timeout in seconds (1.0 to 60.0)
            query_timeout: Query timeout in seconds (1.0 to 300.0)
            retry_attempts: Number of retry attempts (0 to 10)
            use_ssl: Whether to use SSL encryption
            compression: Compression type ("none", "gzip", "lz4")
        """
        self.pool_size = pool_size
        self.connection_timeout = connection_timeout
        self.query_timeout = query_timeout
        self.retry_attempts = retry_attempts
        self.use_ssl = use_ssl
        self.compression = compression

        # Validate parameters
        if not 1 <= pool_size <= 100:
            raise ValueError(
                f"Pool size must be between 1 and 100, got {pool_size}")
        if not 1.0 <= connection_timeout <= 60.0:
            raise ValueError(
                f"Connection timeout must be between 1.0 and 60.0, got {connection_timeout}")
        if not 1.0 <= query_timeout <= 300.0:
            raise ValueError(
                f"Query timeout must be between 1.0 and 300.0, got {query_timeout}")
        if not 0 <= retry_attempts <= 10:
            raise ValueError(
                f"Retry attempts must be between 0 and 10, got {retry_attempts}")
        if compression not in ["none", "gzip", "lz4"]:
            raise ValueError(
                f"Compression must be one of ['none', 'gzip', 'lz4'], got {compression}")

        # Simulate connection metrics
        self._throughput = None
        self._latency = None
        self._error_rate = None

    def benchmark(self) -> Dict[str, float]:
        """
        Run database benchmark and return performance metrics.

        Returns:
            Dict with throughput, latency, and error rate
        """
        # Simulate throughput based on pool size (optimal around 20-30)
        pool_factor = 1.0 - abs(self.pool_size - 25) / 25
        throughput_base = 1000  # Base queries per second

        # Connection timeout affects reliability
        timeout_factor = min(self.connection_timeout / 10, 1.0)

        # SSL adds security but reduces performance
        ssl_factor = 0.9 if self.use_ssl else 1.0

        # Compression effects
        compression_factors = {"none": 1.0, "gzip": 0.85, "lz4": 0.95}
        compression_factor = compression_factors[self.compression]

        # Calculate throughput
        self._throughput = (throughput_base * pool_factor * timeout_factor *
                            ssl_factor * compression_factor * random.uniform(0.9, 1.1))

        # Latency is inversely related to throughput
        base_latency = 10  # Base latency in ms
        latency_factor = 1.0 / max(pool_factor, 0.1)
        ssl_latency = 2 if self.use_ssl else 0

        self._latency = (base_latency * latency_factor + ssl_latency +
                         random.uniform(0, 5))

        # Error rate based on timeouts and retry attempts
        base_error_rate = 0.01  # 1% base error rate
        timeout_error_factor = max(
            0, (5.0 - self.connection_timeout) / 5.0) * 0.05
        retry_factor = max(0, (3 - self.retry_attempts) / 3) * 0.02

        self._error_rate = base_error_rate + timeout_error_factor + retry_factor
        self._error_rate = max(
            0.0, min(0.1, self._error_rate))  # Clamp to [0, 0.1]

        return {
            'throughput': self._throughput,
            'latency': self._latency,
            'error_rate': self._error_rate
        }

    def get_throughput(self) -> float:
        """Get queries per second (higher is better)."""
        if self._throughput is None:
            self.benchmark()
        return self._throughput

    def get_latency(self) -> float:
        """Get average latency in milliseconds (lower is better)."""
        if self._latency is None:
            self.benchmark()
        return self._latency

    def get_error_rate(self) -> float:
        """Get error rate as percentage (lower is better)."""
        if self._error_rate is None:
            self.benchmark()
        return self._error_rate


class WebServerConfig:
    """
    A web server configuration simulator for optimizing server parameters.

    Demonstrates optimization of web server settings like worker processes,
    memory limits, and caching strategies.
    """

    def __init__(self, worker_processes: int = 4, max_connections: int = 1000,
                 memory_limit_mb: int = 512, cache_size_mb: int = 128,
                 keep_alive_timeout: float = 5.0, gzip_enabled: bool = True,
                 log_level: str = "info"):
        """
        Initialize web server configuration.

        Args:
            worker_processes: Number of worker processes (1 to 32)
            max_connections: Maximum concurrent connections (100 to 10000)
            memory_limit_mb: Memory limit per worker in MB (64 to 2048)
            cache_size_mb: Cache size in MB (0 to 1024)
            keep_alive_timeout: Keep-alive timeout in seconds (1.0 to 60.0)
            gzip_enabled: Whether to enable gzip compression
            log_level: Logging level ("debug", "info", "warning", "error")
        """
        self.worker_processes = worker_processes
        self.max_connections = max_connections
        self.memory_limit_mb = memory_limit_mb
        self.cache_size_mb = cache_size_mb
        self.keep_alive_timeout = keep_alive_timeout
        self.gzip_enabled = gzip_enabled
        self.log_level = log_level

        # Validate parameters
        if not 1 <= worker_processes <= 32:
            raise ValueError(
                f"Worker processes must be between 1 and 32, got {worker_processes}")
        if not 100 <= max_connections <= 10000:
            raise ValueError(
                f"Max connections must be between 100 and 10000, got {max_connections}")
        if not 64 <= memory_limit_mb <= 2048:
            raise ValueError(
                f"Memory limit must be between 64 and 2048 MB, got {memory_limit_mb}")
        if not 0 <= cache_size_mb <= 1024:
            raise ValueError(
                f"Cache size must be between 0 and 1024 MB, got {cache_size_mb}")
        if not 1.0 <= keep_alive_timeout <= 60.0:
            raise ValueError(
                f"Keep-alive timeout must be between 1.0 and 60.0, got {keep_alive_timeout}")
        if log_level not in ["debug", "info", "warning", "error"]:
            raise ValueError(
                f"Log level must be one of ['debug', 'info', 'warning', 'error'], got {log_level}")

        # Simulate server metrics
        self._requests_per_second = None
        self._response_time = None
        self._cpu_usage = None
        self._memory_usage = None

    def load_test(self) -> Dict[str, float]:
        """
        Simulate server load test and return performance metrics.

        Returns:
            Dict with requests per second, response time, CPU usage, and memory usage
        """
        # Requests per second based on worker processes and connections
        # Optimal around 8 workers
        worker_factor = min(self.worker_processes / 8, 1.0)
        connection_factor = min(self.max_connections /
                                2000, 1.0)  # Optimal around 2000

        base_rps = 500  # Base requests per second
        self._requests_per_second = (base_rps * worker_factor * connection_factor *
                                     random.uniform(0.8, 1.2))

        # Response time affected by various factors
        base_response_time = 50  # Base response time in ms

        # More workers can reduce response time up to a point
        worker_response_factor = max(
            0.5, 1.0 - (self.worker_processes - 1) * 0.1)

        # Cache improves response time
        cache_factor = max(0.7, 1.0 - self.cache_size_mb / 500)

        # Gzip adds slight overhead but usually worth it
        gzip_factor = 1.1 if self.gzip_enabled else 1.0

        # Keep-alive helps with response time
        keepalive_factor = max(0.8, 1.0 - self.keep_alive_timeout / 30)

        self._response_time = (base_response_time * worker_response_factor *
                               cache_factor * gzip_factor * keepalive_factor *
                               random.uniform(0.9, 1.1))

        # CPU usage based on worker processes and logging
        base_cpu = 20  # Base CPU usage percentage
        worker_cpu = self.worker_processes * 5  # Each worker adds CPU usage

        # Logging overhead
        log_cpu_overhead = {"debug": 10, "info": 5,
                            "warning": 2, "error": 1}[self.log_level]

        # Gzip uses more CPU
        gzip_cpu = 5 if self.gzip_enabled else 0

        self._cpu_usage = min(95, base_cpu + worker_cpu + log_cpu_overhead + gzip_cpu +
                              random.uniform(-5, 5))

        # Memory usage based on limits and cache
        base_memory = 100  # Base memory usage in MB
        worker_memory = self.worker_processes * \
            self.memory_limit_mb * 0.7  # Workers use 70% of limit
        cache_memory = self.cache_size_mb

        self._memory_usage = base_memory + worker_memory + cache_memory

        return {
            'requests_per_second': self._requests_per_second,
            'response_time': self._response_time,
            'cpu_usage': self._cpu_usage,
            'memory_usage': self._memory_usage
        }

    def get_requests_per_second(self) -> float:
        """Get requests per second (higher is better)."""
        if self._requests_per_second is None:
            self.load_test()
        return self._requests_per_second

    def get_response_time(self) -> float:
        """Get average response time in milliseconds (lower is better)."""
        if self._response_time is None:
            self.load_test()
        return self._response_time

    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage (lower is better, but not too low)."""
        if self._cpu_usage is None:
            self.load_test()
        return self._cpu_usage

    def get_memory_usage(self) -> float:
        """Get memory usage in MB."""
        if self._memory_usage is None:
            self.load_test()
        return self._memory_usage


class GameAI:
    """
    A game AI simulator for optimizing AI behavior parameters.

    Demonstrates optimization of game AI parameters like aggression level,
    exploration rate, and decision-making strategies.
    """

    def __init__(self, aggression: float = 0.5, exploration_rate: float = 0.1,
                 reaction_time: float = 0.2, memory_depth: int = 10,
                 strategy: str = "balanced", difficulty: str = "medium"):
        """
        Initialize game AI with behavior parameters.

        Args:
            aggression: Aggression level (0.0 to 1.0)
            exploration_rate: Exploration vs exploitation rate (0.0 to 1.0)
            reaction_time: Reaction time in seconds (0.1 to 2.0)
            memory_depth: Number of past moves to remember (1 to 50)
            strategy: AI strategy ("aggressive", "defensive", "balanced")
            difficulty: Difficulty level ("easy", "medium", "hard", "expert")
        """
        self.aggression = aggression
        self.exploration_rate = exploration_rate
        self.reaction_time = reaction_time
        self.memory_depth = memory_depth
        self.strategy = strategy
        self.difficulty = difficulty

        # Validate parameters
        if not 0.0 <= aggression <= 1.0:
            raise ValueError(
                f"Aggression must be between 0.0 and 1.0, got {aggression}")
        if not 0.0 <= exploration_rate <= 1.0:
            raise ValueError(
                f"Exploration rate must be between 0.0 and 1.0, got {exploration_rate}")
        if not 0.1 <= reaction_time <= 2.0:
            raise ValueError(
                f"Reaction time must be between 0.1 and 2.0, got {reaction_time}")
        if not 1 <= memory_depth <= 50:
            raise ValueError(
                f"Memory depth must be between 1 and 50, got {memory_depth}")
        if strategy not in ["aggressive", "defensive", "balanced"]:
            raise ValueError(
                f"Strategy must be one of ['aggressive', 'defensive', 'balanced'], got {strategy}")
        if difficulty not in ["easy", "medium", "hard", "expert"]:
            raise ValueError(
                f"Difficulty must be one of ['easy', 'medium', 'hard', 'expert'], got {difficulty}")

        # Simulate AI performance metrics
        self._win_rate = None
        self._average_score = None
        self._player_satisfaction = None

    def simulate_games(self, num_games: int = 100) -> Dict[str, float]:
        """
        Simulate AI performance over multiple games.

        Args:
            num_games: Number of games to simulate

        Returns:
            Dict with win rate, average score, and player satisfaction
        """
        # Win rate based on difficulty and strategy balance
        difficulty_factors = {"easy": 0.3,
                              "medium": 0.5, "hard": 0.7, "expert": 0.9}
        base_win_rate = difficulty_factors[self.difficulty]

        # Strategy affects win rate
        strategy_bonus = {"aggressive": 0.1, "defensive": -
                          0.05, "balanced": 0.05}[self.strategy]

        # Aggression and exploration balance
        aggression_factor = 1.0 - \
            abs(self.aggression - 0.6) * 0.5  # Optimal around 0.6
        exploration_factor = 1.0 - \
            abs(self.exploration_rate - 0.15) * 2  # Optimal around 0.15

        # Reaction time affects performance
        reaction_factor = max(0.5, 1.0 - (self.reaction_time - 0.2) * 0.3)

        # Memory helps up to a point
        memory_factor = min(1.0, self.memory_depth / 20)

        self._win_rate = (base_win_rate + strategy_bonus +
                          (aggression_factor + exploration_factor + reaction_factor + memory_factor) * 0.1 +
                          random.uniform(-0.05, 0.05))
        self._win_rate = max(0.0, min(1.0, self._win_rate))

        # Average score correlates with win rate but has other factors
        base_score = 1000
        score_multiplier = 1.0 + self._win_rate

        # Aggressive strategy gets higher scores when winning
        if self.strategy == "aggressive":
            score_multiplier *= 1.2
        elif self.strategy == "defensive":
            score_multiplier *= 0.9

        self._average_score = base_score * \
            score_multiplier * random.uniform(0.8, 1.2)

        # Player satisfaction based on balanced gameplay
        # Too easy or too hard reduces satisfaction
        # Optimal around 60% win rate
        difficulty_satisfaction = 1.0 - abs(self._win_rate - 0.6) * 1.5

        # Reaction time affects player experience
        reaction_satisfaction = max(
            0.5, 1.0 - abs(self.reaction_time - 0.3) * 2)

        # Strategy variety affects satisfaction
        strategy_satisfaction = {"aggressive": 0.8,
                                 "defensive": 0.7, "balanced": 0.9}[self.strategy]

        self._player_satisfaction = ((difficulty_satisfaction + reaction_satisfaction + strategy_satisfaction) / 3 *
                                     random.uniform(0.9, 1.1))
        self._player_satisfaction = max(
            0.0, min(1.0, self._player_satisfaction))

        return {
            'win_rate': self._win_rate,
            'average_score': self._average_score,
            'player_satisfaction': self._player_satisfaction
        }

    def get_win_rate(self) -> float:
        """Get AI win rate (balanced around 0.6 is often optimal)."""
        if self._win_rate is None:
            self.simulate_games()
        return self._win_rate

    def get_average_score(self) -> float:
        """Get average score per game (higher is better)."""
        if self._average_score is None:
            self.simulate_games()
        return self._average_score

    def get_player_satisfaction(self) -> float:
        """Get player satisfaction rating (higher is better)."""
        if self._player_satisfaction is None:
            self.simulate_games()
        return self._player_satisfaction


class CacheSystem:
    """
    A caching system simulator for optimizing cache parameters.

    Demonstrates optimization of cache settings like size limits,
    eviction policies, and TTL values.
    """

    def __init__(self, max_size_mb: int = 256, ttl_seconds: int = 3600,
                 eviction_policy: str = "lru", compression_enabled: bool = False,
                 prefetch_enabled: bool = True, write_through: bool = False):
        """
        Initialize cache system with parameters.

        Args:
            max_size_mb: Maximum cache size in MB (16 to 4096)
            ttl_seconds: Time to live in seconds (60 to 86400)
            eviction_policy: Eviction policy ("lru", "lfu", "fifo", "random")
            compression_enabled: Whether to enable compression
            prefetch_enabled: Whether to enable prefetching
            write_through: Whether to use write-through caching
        """
        self.max_size_mb = max_size_mb
        self.ttl_seconds = ttl_seconds
        self.eviction_policy = eviction_policy
        self.compression_enabled = compression_enabled
        self.prefetch_enabled = prefetch_enabled
        self.write_through = write_through

        # Validate parameters
        if not 16 <= max_size_mb <= 4096:
            raise ValueError(
                f"Max size must be between 16 and 4096 MB, got {max_size_mb}")
        if not 60 <= ttl_seconds <= 86400:
            raise ValueError(
                f"TTL must be between 60 and 86400 seconds, got {ttl_seconds}")
        if eviction_policy not in ["lru", "lfu", "fifo", "random"]:
            raise ValueError(
                f"Eviction policy must be one of ['lru', 'lfu', 'fifo', 'random'], got {eviction_policy}")

        # Simulate cache metrics
        self._hit_rate = None
        self._average_latency = None
        self._memory_efficiency = None

    def benchmark_cache(self) -> Dict[str, float]:
        """
        Simulate cache performance benchmark.

        Returns:
            Dict with hit rate, average latency, and memory efficiency
        """
        # Hit rate based on cache size and eviction policy
        # Diminishing returns after 512MB
        size_factor = min(1.0, self.max_size_mb / 512)

        # Eviction policy effectiveness
        policy_factors = {"lru": 1.0, "lfu": 0.95, "fifo": 0.8, "random": 0.6}
        policy_factor = policy_factors[self.eviction_policy]

        # TTL affects hit rate (too short reduces hits, too long may serve stale data)
        optimal_ttl = 1800  # 30 minutes
        ttl_factor = 1.0 - abs(self.ttl_seconds -
                               optimal_ttl) / optimal_ttl * 0.3

        # Prefetching improves hit rate
        prefetch_bonus = 0.1 if self.prefetch_enabled else 0.0

        base_hit_rate = 0.6
        self._hit_rate = (base_hit_rate + size_factor * 0.3 * policy_factor * ttl_factor +
                          prefetch_bonus + random.uniform(-0.05, 0.05))
        self._hit_rate = max(0.0, min(1.0, self._hit_rate))

        # Average latency
        base_latency = 1.0  # 1ms base latency

        # Larger cache may have slightly higher latency
        size_latency = self.max_size_mb / 1000  # Small increase with size

        # Compression adds latency but saves space
        compression_latency = 0.5 if self.compression_enabled else 0.0

        # Write-through adds latency for writes
        write_latency = 0.3 if self.write_through else 0.0

        self._average_latency = (base_latency + size_latency + compression_latency +
                                 write_latency + random.uniform(0, 0.2))

        # Memory efficiency (how well cache uses allocated memory)
        base_efficiency = 0.8

        # Compression improves efficiency
        compression_bonus = 0.15 if self.compression_enabled else 0.0

        # LRU and LFU are more efficient than FIFO and random
        efficiency_factors = {"lru": 1.0,
                              "lfu": 1.0, "fifo": 0.9, "random": 0.8}
        efficiency_factor = efficiency_factors[self.eviction_policy]

        self._memory_efficiency = ((base_efficiency + compression_bonus) * efficiency_factor +
                                   random.uniform(-0.05, 0.05))
        self._memory_efficiency = max(0.0, min(1.0, self._memory_efficiency))

        return {
            'hit_rate': self._hit_rate,
            'average_latency': self._average_latency,
            'memory_efficiency': self._memory_efficiency
        }

    def get_hit_rate(self) -> float:
        """Get cache hit rate (higher is better)."""
        if self._hit_rate is None:
            self.benchmark_cache()
        return self._hit_rate

    def get_average_latency(self) -> float:
        """Get average latency in milliseconds (lower is better)."""
        if self._average_latency is None:
            self.benchmark_cache()
        return self._average_latency

    def get_memory_efficiency(self) -> float:
        """Get memory efficiency ratio (higher is better)."""
        if self._memory_efficiency is None:
            self.benchmark_cache()
        return self._memory_efficiency
