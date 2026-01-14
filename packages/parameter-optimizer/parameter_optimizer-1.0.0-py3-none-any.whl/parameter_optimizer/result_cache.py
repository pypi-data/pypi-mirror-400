"""
Result caching system for parameter optimization.

This module manages caching of test results to avoid duplicate runs.
"""

import json
import hashlib
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from .data_models import TestResult


class ResultCache:
    """
    Manages caching of test results to avoid duplicate runs.
    """

    def __init__(self, cache_dir: str, target_class_name: str):
        """Initialize cache with directory and class identifier."""
        if not isinstance(cache_dir, str) or not cache_dir.strip():
            raise ValueError("cache_dir must be a non-empty string")
        
        if not isinstance(target_class_name, str) or not target_class_name.strip():
            raise ValueError("target_class_name must be a non-empty string")
        
        self.cache_dir = Path(cache_dir)
        self.target_class_name = target_class_name
        self.cache_file = self.cache_dir / f"{target_class_name}_cache.json"
        self._temp_file = None  # For atomic writes

        # Create cache directory if it doesn't exist
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f"Cannot create cache directory {cache_dir}: {e}")

        # Validate cache directory is writable
        if not os.access(self.cache_dir, os.W_OK):
            raise PermissionError(f"Cache directory is not writable: {cache_dir}")

        # Load existing cache or initialize empty cache
        self._cache = self._load_cache()
        self._cache_modified = False

    def _generate_cache_key(self, parameters: Dict[str, Any],
                           class_signature: str = None) -> str:
        """Generate a unique cache key based on parameters and class signature."""
        # Sort parameters to ensure consistent key generation
        sorted_params = json.dumps(parameters, sort_keys=True, default=str)

        # Include class signature if provided
        if class_signature:
            key_data = f"{sorted_params}:{class_signature}"
        else:
            key_data = sorted_params

        # Generate hash for the key
        return hashlib.md5(key_data.encode()).hexdigest()

    def _load_cache(self) -> Dict[str, Dict]:
        """Load cache from disk with error recovery."""
        if not self.cache_file.exists():
            return {}
        
        # Check if file is readable
        if not os.access(self.cache_file, os.R_OK):
            return {}
        
        try:
            # Check file size to avoid loading huge files
            file_size = self.cache_file.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                # Cache file too large, start fresh
                self._backup_and_clear_cache("Cache file too large")
                return {}
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, dict):
                self._backup_and_clear_cache("Invalid cache format")
                return {}
                
            return data
            
        except json.JSONDecodeError:
            # Cache is corrupted, backup and start fresh
            self._backup_and_clear_cache("JSON decode error")
            return {}
        except (IOError, OSError):
            # File system error, start with empty cache
            return {}

    def _backup_and_clear_cache(self, reason: str) -> None:
        """Backup corrupted cache file and start fresh."""
        try:
            if self.cache_file.exists():
                backup_file = self.cache_file.with_suffix('.json.backup')
                shutil.copy2(self.cache_file, backup_file)
                self.cache_file.unlink()
        except (IOError, OSError):
            # If backup fails, just continue
            pass

    def _save_cache(self) -> None:
        """Save cache to disk atomically."""
        if not self._cache_modified:
            return
        
        try:
            # Use atomic write to prevent corruption
            with tempfile.NamedTemporaryFile(
                mode='w', 
                dir=self.cache_dir, 
                delete=False,
                suffix='.tmp',
                encoding='utf-8'
            ) as temp_file:
                json.dump(self._cache, temp_file, indent=2, default=str)
                temp_file.flush()
                os.fsync(temp_file.fileno())  # Force write to disk
                self._temp_file = temp_file.name
            
            # Atomic move
            if os.name == 'nt':  # Windows
                if self.cache_file.exists():
                    self.cache_file.unlink()
            shutil.move(self._temp_file, self.cache_file)
            self._temp_file = None
            self._cache_modified = False
            
        except (IOError, OSError) as e:
            # Clean up temp file if it exists
            if self._temp_file and os.path.exists(self._temp_file):
                try:
                    os.unlink(self._temp_file)
                except OSError:
                    pass
            # Don't raise exception - caching is not critical
            pass

    def get_cached_result(self, parameters: Dict[str, Any],
                         class_signature: str = None) -> Optional[TestResult]:
        """Retrieve cached result for parameter combination."""
        cache_key = self._generate_cache_key(parameters, class_signature)

        if cache_key in self._cache:
            cached_data = self._cache[cache_key]

            # Validate cache entry has required fields
            if self._is_valid_cache_entry(cached_data):
                # Convert cached data back to TestResult
                return self._deserialize_test_result(cached_data)

        return None

    def cache_result(self, parameters: Dict[str, Any], result: TestResult,
                    metric_score: float, class_signature: str = None) -> None:
        """Store test result in cache."""
        try:
            cache_key = self._generate_cache_key(parameters, class_signature)

            # Serialize TestResult for storage
            cached_data = self._serialize_test_result(result, class_signature)

            # Store in memory cache
            self._cache[cache_key] = cached_data
            self._cache_modified = True

            # Persist to disk (with size limit check)
            if len(self._cache) % 10 == 0:  # Check every 10 entries
                self._check_cache_size_limit()
            
            self._save_cache()
            
        except Exception:
            # Don't fail the optimization if caching fails
            pass

    def _check_cache_size_limit(self) -> None:
        """Check and enforce cache size limits."""
        max_entries = 10000  # Maximum number of cache entries
        
        if len(self._cache) > max_entries:
            # Remove oldest entries (simple LRU approximation)
            # Sort by timestamp and keep newest entries
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1].get('timestamp', ''),
                reverse=True
            )
            
            # Keep only the newest max_entries
            self._cache = dict(sorted_items[:max_entries])
            self._cache_modified = True

    def _is_valid_cache_entry(self, cached_data: Dict) -> bool:
        """Validate that cached entry has all required fields."""
        required_fields = ['parameters', 'metric_score', 'execution_time',
                          'timestamp', 'success', 'class_signature']
        return all(field in cached_data for field in required_fields)

    def _serialize_test_result(self, result: TestResult,
                              class_signature: str = None) -> Dict:
        """Convert TestResult to dictionary for caching."""
        return {
            'parameters': result.parameters,
            'metric_score': result.metric_score,
            'execution_time': result.execution_time,
            'timestamp': result.timestamp.isoformat(),
            'success': result.success,
            'error_message': result.error_message,
            'class_signature': class_signature
        }

    def _deserialize_test_result(self, cached_data: Dict) -> TestResult:
        """Convert cached dictionary back to TestResult."""
        from datetime import datetime

        return TestResult(
            parameters=cached_data['parameters'],
            metric_score=cached_data['metric_score'],
            execution_time=cached_data['execution_time'],
            timestamp=datetime.fromisoformat(cached_data['timestamp']),
            success=cached_data['success'],
            error_message=cached_data.get('error_message')
        )

    def is_cache_valid(self, current_class_signature: str,
                      current_metric_signature: str) -> bool:
        """Validate that cached results match current class and metric function."""
        # Check if any cached entries exist
        if not self._cache:
            return True

        # Check a sample of cached entries for signature compatibility
        for cached_data in list(self._cache.values())[:5]:  # Check first 5
            if 'class_signature' in cached_data:
                if cached_data['class_signature'] != current_class_signature:
                    return False
            if 'metric_signature' in cached_data:
                if (cached_data['metric_signature'] !=
                        current_metric_signature):
                    return False

        return True

    def invalidate_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
        self._cache_modified = True
        self._save_cache()

    def cleanup(self) -> None:
        """Clean up resources and temporary files."""
        try:
            # Save any pending changes
            if self._cache_modified:
                self._save_cache()
            
            # Clean up any temporary files
            if self._temp_file and os.path.exists(self._temp_file):
                try:
                    os.unlink(self._temp_file)
                except OSError:
                    pass
                self._temp_file = None
                
        except Exception:
            # Don't raise exceptions during cleanup
            pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def get_cache_size_info(self) -> Dict[str, Any]:
        """Get information about cache size and disk usage."""
        try:
            cache_entries = len(self._cache)
            
            if self.cache_file.exists():
                file_size = self.cache_file.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
            else:
                file_size = 0
                file_size_mb = 0.0
            
            # Check available disk space
            disk_usage = shutil.disk_usage(self.cache_dir)
            available_space_mb = disk_usage.free / (1024 * 1024)
            
            return {
                'cache_entries': cache_entries,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size_mb, 2),
                'available_space_mb': round(available_space_mb, 2),
                'cache_file_exists': self.cache_file.exists()
            }
            
        except Exception:
            return {
                'cache_entries': len(self._cache),
                'file_size_bytes': 0,
                'file_size_mb': 0.0,
                'available_space_mb': 0.0,
                'cache_file_exists': False
            }

    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about cached vs new tests."""
        total_cached = len(self._cache)
        successful_cached = sum(1 for entry in self._cache.values()
                               if entry.get('success', False))
        failed_cached = total_cached - successful_cached

        return {
            'total_cached': total_cached,
            'successful_cached': successful_cached,
            'failed_cached': failed_cached
        }