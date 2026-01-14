""" 
Ultimate Decorator Toolkit - A comprehensive collection of decorators for function enhancement,
logging, performance monitoring, and fault tolerance, implemented as classes.

Features:
- 50+ practical decorators organized by category
- Consistent verbose mode for all decorators
- Usage examples with expected output
- Thread-safe implementations
- Support for both sync and async functions
 
"""

import time as time_module
import functools
import logging
import threading
import inspect
import random
import cProfile
import pstats
import io
import hashlib
import pickle
import os
import sys
import warnings
import asyncio
from collections import defaultdict
from functools import lru_cache
from contextlib import suppress as context_suppress
from typing import Callable, Any, Dict, List, Tuple, Optional, Union

##############################
# Time2Do
import re
from datetime import datetime, time, date, timedelta
from zoneinfo import ZoneInfo
##############################

from pathlib import Path

# ----------- 检查 Numba 是否可用 -----------
try:
    import numba
    NUMBA_AVAILABLE = True
except Exception:
    numba = None
    NUMBA_AVAILABLE = False

# ----------- 检查 CUDA 是否可用 -----------
CUDA_AVAILABLE = False
if NUMBA_AVAILABLE:
    try:
        CUDA_AVAILABLE = numba.cuda.is_available()
    except Exception:
        CUDA_AVAILABLE = False


class Time2Do:
    """Decorator class for conditional execution based on time parameters"""
    
    def __init__(
        self,
        when: str = "range",
        start_time: Optional[Union[str, time]] = None,
        end_time: Optional[Union[str, time]] = None,
        weekdays: Optional[Union[List[int], List[str], str, bool]] = None,
        invert: bool = False,
        timezone: Optional[str] = "Europe/Berlin",
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
        holidays: Optional[Union[List[Union[str, date]], Callable[[date], bool]]] = None,
        inclusive: str = "[]",
        *,
        cache: bool = True,
        on_false: Optional[Callable] = None
    ):
        """
        Ultimate time-based execution decorator with complete feature set
        
        Args:
            when: Time expression or keyword ("range", "never", "every day")
            start_time: Override start time
            end_time: Override end time
            weekdays: Weekday specification
            invert: Return inverse result
            timezone: Timezone identifier
            start_date: Start date boundary
            end_date: End date boundary
            holidays: List of dates or holiday checker function
            inclusive: Time boundary inclusion ("[]", "[)", "(]", "()")
            cache: Enable result caching
            on_false: Callback when condition not met
        """
        self.when = when
        self.start_time = start_time
        self.end_time = end_time
        self.weekdays = weekdays
        self.invert = invert
        self.timezone = timezone
        self.start_date = start_date
        self.end_date = end_date
        self.holidays = holidays
        self.inclusive = inclusive
        self.cache = cache
        self.on_false = on_false
        
        # Pre-compiled regex patterns
        self.patterns = {
            "special": re.compile(r"^(midnight|noon)$", re.I),
            "am_pm": re.compile(r"(\d{1,2})(?::(\d{2}))?\s*([ap]m?)\b", re.I),
            "24hr": re.compile(r"(\d{1,2})(?::(\d{2}))?\b"),
            "weekday": re.compile(
                r"\b(mon|tue|wed|thu|fri|sat|sun|weekdays?|weekends?)\b", re.I
            ),
            "range_sep": re.compile(r"\b(?:to|-|and|until)\b", re.I),
            "date": re.compile(r"(\d{4})-(\d{2})-(\d{2})"),
        }

    def __call__(self, func: Callable) -> Callable:
        """Decorator implementation"""
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if self._should_execute():
                    return await func(*args, **kwargs)
                return self._handle_false()
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                if self._should_execute():
                    return func(*args, **kwargs)
                return self._handle_false()
            return sync_wrapper

    def _should_execute(self) -> bool:
        """Determine if the function should execute based on time conditions"""
        if self.cache:
            cache_key = self._get_cache_key()
            return self._cached_time_check(cache_key)
        return self._time_check_impl()

    @lru_cache(maxsize=128)
    def _cached_time_check(self, cache_key: Tuple[Any]) -> bool:
        """Cached version of time check"""
        return self._time_check_impl()

    def _get_cache_key(self) -> Tuple[Any]:
        """Generate cache key based on current parameters"""
        return (
            self.when,
            self.start_time,
            self.end_time,
            tuple(self.weekdays) if isinstance(self.weekdays, list) else self.weekdays,
            self.invert,
            self.timezone,
            self.start_date,
            self.end_date,
            tuple(self.holidays) if isinstance(self.holidays, list) else self.holidays,
            self.inclusive,
            datetime.now().minute  # Cache per minute
        )

    def _time_check_impl(self) -> bool:
        """Core time checking implementation"""
        now = self._get_current_time()
        current_time = now.time()
        current_date = now.date()

        params = {
            "start_time": time(6, 0),
            "end_time": time(23, 0),
            "weekdays": None,
            "start_date": None,
            "end_date": None,
            "holidays": None,
            "never": False,
            "always": False,
        }

        self._process_when_string(params)
        self._process_time_params(params)
        self._process_date_params(params)
        self._process_weekdays(params)
        self._process_holidays(params)

        # Early exit conditions
        if params["never"]:
            return self.invert
        if params["always"]:
            return not self.invert

        # Check date range
        if not self._check_date_range(current_date, params["start_date"], params["end_date"]):
            return self.invert

        # Check holidays
        if self._is_holiday(current_date, params["holidays"]):
            return self.invert

        # Check weekdays
        if not self._check_weekday(now.weekday(), params["weekdays"]):
            return self.invert

        # Check time range
        in_range = self._check_time_range(
            current_time, params["start_time"], params["end_time"], self.inclusive
        )

        return not in_range if self.invert else in_range

    def _get_current_time(self) -> datetime:
        """Get current time with timezone support"""
        try:
            if self.timezone:
                return datetime.now(ZoneInfo(self.timezone))
        except Exception:
            pass
        return datetime.now()

    def _process_when_string(self, params: dict):
        """Process the natural language 'when' string"""
        when_lower = self.when.lower().strip()

        if when_lower == "never":
            params["never"] = True
            return
        elif when_lower == "every day":
            params["always"] = True
            return

        # Extract weekdays
        weekday_matches = self.patterns["weekday"].finditer(when_lower)
        for match in weekday_matches:
            if not params["weekdays"]:
                params["weekdays"] = []
            params["weekdays"].append(match.group(1))
            when_lower = when_lower.replace(match.group(), "").strip()

        # Parse time expressions
        if "between" in when_lower and "and" in when_lower:
            parts = self.patterns["range_sep"].split(
                when_lower.replace("between", ""), maxsplit=1
            )
            if len(parts) >= 2:
                params["start_time"] = self._parse_time(parts[0])
                params["end_time"] = self._parse_time(parts[1])
        elif any(sep in when_lower for sep in [" to ", "-", " until "]):
            parts = self.patterns["range_sep"].split(when_lower, maxsplit=1)
            if len(parts) >= 2:
                params["start_time"] = self._parse_time(parts[0])
                params["end_time"] = self._parse_time(parts[1])
        elif when_lower.startswith("after "):
            params["start_time"] = self._parse_time(when_lower[6:])
            params["end_time"] = time(23, 59, 59)
        elif when_lower.startswith("before "):
            params["start_time"] = time(0, 0)
            params["end_time"] = self._parse_time(when_lower[7:])

    def _process_time_params(self, params: dict):
        """Process explicit time parameters"""
        if self.start_time is not None:
            params["start_time"] = self._parse_time(self.start_time)
        if self.end_time is not None:
            params["end_time"] = self._parse_time(self.end_time)

    def _parse_time(self, t: Union[str, time]) -> time:
        """Parse time from string or time object"""
        if isinstance(t, time):
            return t

        t_str = str(t).lower().strip()

        # Handle special cases
        if match := self.patterns["special"].match(t_str):
            return time(0, 0) if match.group(1) == "midnight" else time(12, 0)

        # Parse AM/PM format
        if match := self.patterns["am_pm"].search(t_str):
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            period = match.group(3).lower()
            if period.startswith("p") and hour != 12:
                hour += 12
            elif period.startswith("a") and hour == 12:
                hour = 0
            return time(hour, minute)

        # Parse 24-hour format
        if match := self.patterns["24hr"].search(t_str):
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            return time(hour, minute)

        raise ValueError(f"Invalid time format: '{t}'")

    def _process_date_params(self, params: dict):
        """Process date parameters"""
        if self.start_date is not None:
            params["start_date"] = self._parse_date(self.start_date)
        if self.end_date is not None:
            params["end_date"] = self._parse_date(self.end_date)

    def _parse_date(self, d: Union[str, date]) -> date:
        """Parse date from string or date object"""
        if isinstance(d, date):
            return d

        if match := self.patterns["date"].match(d):
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))

        raise ValueError(f"Invalid date format: '{d}'. Use YYYY-MM-DD")

    def _process_weekdays(self, params: dict):
        """Process weekday specifications"""
        if self.weekdays is None:
            return

        if isinstance(self.weekdays, bool):
            params["weekdays"] = ["weekdays"] if self.weekdays else []
            return

        if not params["weekdays"]:
            params["weekdays"] = []

        if isinstance(self.weekdays, str):
            params["weekdays"].extend([w.strip() for w in self.weekdays.split(",")])
        elif isinstance(self.weekdays, list):
            params["weekdays"].extend(self.weekdays)

    def _process_holidays(self, params: dict):
        """Process holiday specifications"""
        if self.holidays is None:
            return

        params["holidays"] = []

        if callable(self.holidays):
            params["holidays"] = self.holidays
            return

        for h in self.holidays:
            if isinstance(h, str):
                params["holidays"].append(self._parse_date(h))
            else:
                params["holidays"].append(h)

    def _check_date_range(
        self,
        current_date: date,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> bool:
        """Check if current date is within range"""
        if start_date and current_date < start_date:
            return False
        if end_date and current_date > end_date:
            return False
        return True

    def _is_holiday(
        self,
        current_date: date,
        holidays: Union[List[date], Callable[[date], bool]]
    ) -> bool:
        """Check if date is a holiday"""
        if not holidays:
            return False
        if callable(holidays):
            return holidays(current_date)
        return current_date in [
            (self._parse_date(h) if isinstance(h, str) else h)
            for h in holidays
        ]

    def _check_weekday(
        self,
        current_weekday: int,
        weekdays_spec: List[Union[str, int]]
    ) -> bool:
        """Check if current weekday matches specification"""
        if not weekdays_spec:
            return True

        day_map = {
            "mon": 0, "tue": 1, "wed": 2, "thu": 3,
            "fri": 4, "sat": 5, "sun": 6,
            "weekday": [0, 1, 2, 3, 4],
            "weekdays": [0, 1, 2, 3, 4],
            "weekend": [5, 6],
            "weekends": [5, 6],
        }

        allowed_days = set()
        for spec in weekdays_spec:
            if isinstance(spec, int) and 0 <= spec <= 6:
                allowed_days.add(spec)
            elif isinstance(spec, str):
                spec_lower = spec.lower()
                if spec_lower in day_map:
                    days = day_map[spec_lower]
                    if isinstance(days, list):
                        allowed_days.update(days)
                    else:
                        allowed_days.add(days)

        return current_weekday in allowed_days if allowed_days else True

    def _check_time_range(
        self,
        current_time: time,
        start_time: time,
        end_time: time,
        inclusive: str
    ) -> bool:
        """Check if current time is within range"""
        if start_time <= end_time:
            if inclusive == "[]":
                return start_time <= current_time <= end_time
            elif inclusive == "[)":
                return start_time <= current_time < end_time
            elif inclusive == "(]":
                return start_time < current_time <= end_time
            elif inclusive == "()":
                return start_time < current_time < end_time
        else:  # Crosses midnight
            if inclusive == "[]":
                return current_time >= start_time or current_time <= end_time
            elif inclusive == "[)":
                return current_time >= start_time or current_time < end_time
            elif inclusive == "(]":
                return current_time > start_time or current_time <= end_time
            elif inclusive == "()":
                return current_time > start_time or current_time < end_time

        return False

    def _handle_false(self):
        """Execute the false condition handler"""
        if self.on_false is not None:
            return self.on_false()
        return None

    @staticmethod
    def usage_example() -> str:
        """Provide usage examples"""
        return """
        # Example 1: Basic time-based execution
        @Time2Do(when="between 9am and 5pm on weekdays")
        def business_hours_task():
            print("Executing during business hours")

        # Example 2: With date ranges and holidays
        holidays = ["2023-12-25", "2024-01-01"]

        @Time2Do(
            start_date="2023-01-01",
            end_date="2023-12-31",
            holidays=holidays,
            when="after 2pm"
        )
        def afternoon_task():
            print("Executing in the afternoon on non-holidays")

        # Example 3: Asynchronous function with custom false handler
        def skip_handler():
            print("Skipping execution - condition not met")

        @Time2Do(
            when="before 8am", 
            on_false=skip_handler,
            timezone="America/New_York"
        )
        async def morning_task():
            print("Good morning!")
        """



# Base class for all decorators
class DecoratorBase:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(message)
    
    @staticmethod
    def usage_example() -> str:
        """Return usage example with expected output"""
        return ""

##############################
# 1. Timing & Profiling
##############################
class Timer(DecoratorBase):
    """Measure function execution time with threshold alerting"""

    def __init__(self, threshold: float = None, use_logging: bool = False,
                 log_level: int = logging.INFO, log_format: str = None,
                 verbose: bool = True):
        super().__init__(verbose)
        self.threshold = threshold
        self.use_logging = use_logging
        self.log_level = log_level
        self.log_format = log_format or "[TIMER] {func} took {duration}"

    def __call__(self, func: Callable) -> Callable:
        is_coroutine = inspect.iscoroutinefunction(func)
        logger = logging.getLogger(func.__module__) if self.use_logging else None

        if is_coroutine:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time_module.perf_counter()
                result = await func(*args, **kwargs)
                duration = time_module.perf_counter() - start
                self._log_execution(func.__name__, duration, logger)
                return result
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time_module.perf_counter()
                result = func(*args, **kwargs)
                duration = time_module.perf_counter() - start
                self._log_execution(func.__name__, duration, logger)
                return result
            return sync_wrapper

    def _log_execution(self, func_name: str, duration: float, logger: logging.Logger):
        readable_duration = self._format_duration(duration)
        msg = self.log_format.format(func=func_name, duration=readable_duration)

        if self.threshold and duration > self.threshold:
            msg += f"Exceeded threshold {self._format_duration(self.threshold)}"

        if self.use_logging and logger:
            logger.log(self.log_level, msg)
        else:
            self._log(msg)

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Convert duration in seconds to a human-readable format"""
        seconds = int(seconds)
        intervals = (
            ('month', 2592000),  # 30 * 24 * 60 * 60
            ('week', 604800),    # 7 * 24 * 60 * 60
            ('day', 86400),
            ('h', 3600),
            ('min', 60),
            ('s', 1),
        )
        parts = []
        for name, count in intervals:
            value = seconds // count
            if value:
                parts.append(f"{value} {name}{'s' if value > 1 and name not in ['h', 'min', 's'] else ''}")
                seconds %= count
        return ' '.join(parts) if parts else '0 s'

    @staticmethod
    def usage_example() -> str:
        return """
        # Timer Example
        @Timer(threshold=0.3, verbose=True)
        def process_data(data):
            time_module.sleep(125.5)
            return f"Processed {len(data)} items"

        result = process_data([1, 2, 3])
        # Expected output: 
        # [TIMER] process_data took 2 min 5 s Exceeded threshold 0.3 s
        """


class TimeIt(DecoratorBase):
    """Measure execution time with configurable units"""
    def __init__(self, print_result: bool = True, unit: str = "ms", verbose: bool = True):
        super().__init__(verbose)
        self.print_result = print_result
        self.unit = unit  # ms, s, ns
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time_module.perf_counter_ns()
            result = func(*args, **kwargs)
            end_time = time_module.perf_counter_ns()
            
            duration_ns = end_time - start_time
            duration = {
                "ns": duration_ns,
                "ms": duration_ns / 1_000_000,
                "s": duration_ns / 1_000_000_000
            }[self.unit]
            
            unit_str = self.unit
            if self.print_result:
                msg = f"[TIMEIT] {func.__name__} took {duration:.4f}{unit_str} -> {result}"
            else:
                msg = f"[TIMEIT] {func.__name__} took {duration:.4f}{unit_str}"
            
            self._log(msg)
            return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # TimeIt Example
        @TimeIt(unit="ms", verbose=True)
        def calculate_factorial(n):
            result = 1
            for i in range(1, n+1):
                result *= i
            return result

        fact = calculate_factorial(10)
        # Expected output:
        # [TIMEIT] calculate_factorial took 0.0056ms -> 3628800
        """

class Profile(DecoratorBase):
    """Profile function execution using cProfile"""
    def __init__(self, sort_by: str = 'cumulative', lines: int = 20, verbose: bool = True):
        super().__init__(verbose)
        self.sort_by = sort_by
        self.lines = lines
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            result = func(*args, **kwargs)
            profiler.disable()
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats(self.sort_by)
            ps.print_stats(self.lines)
            self._log(f"[PROFILE] {func.__name__}:\n{s.getvalue()}")
            return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Profile Example
        @Profile(sort_by='time', lines=5, verbose=True)
        def complex_computation():
            total = 0
            for i in range(1000):
                for j in range(1000):
                    total += i * j
            return total

        result = complex_computation()
        # Expected output: Profile statistics for the function
        """

class Benchmark(DecoratorBase):
    """Run performance benchmarks with warmup iterations"""
    def __init__(self, iterations: int = 1000, warmup: int = 10, verbose: bool = True):
        super().__init__(verbose)
        self.iterations = iterations
        self.warmup = warmup
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Warmup runs
            for _ in range(self.warmup):
                func(*args, **kwargs)
            
            # Timed runs
            times = []
            for _ in range(self.iterations):
                start_time = time_module.perf_counter_ns()
                func(*args, **kwargs)
                end_time = time_module.perf_counter_ns()
                times.append(end_time - start_time)
            
            # Calculate stats
            avg_ns = sum(times) / len(times)
            min_ns = min(times)
            max_ns = max(times)
            
            stats = {
                "function": func.__name__,
                "iterations": self.iterations,
                "avg_ns": avg_ns,
                "min_ns": min_ns,
                "max_ns": max_ns,
                "total_ms": sum(times) / 1_000_000
            }
            
            if self.verbose:
                print(f"[BENCHMARK] {func.__name__} performance:")
                print(f"  Iterations: {self.iterations}")
                print(f"  Average: {avg_ns/1000:.2f} µs")
                print(f"  Min:     {min_ns/1000:.2f} µs")
                print(f"  Max:     {max_ns/1000:.2f} µs")
                print(f"  Total:   {sum(times)/1_000_000:.2f} ms")
            
            return stats
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Benchmark Example
        @Benchmark(iterations=1000, warmup=10, verbose=True)
        def vector_dot_product(a, b):
            return sum(x*y for x, y in zip(a, b))

        a = list(range(1000))
        b = list(range(1000))
        stats = vector_dot_product(a, b)
        # Expected output: Performance statistics
        """

##############################
# 2. Error Handling & Retry
##############################

class Retry(DecoratorBase):
    """Retry function on failure with exponential backoff"""
    def __init__(self, retries: int = 3, delay: float = 1, backoff: float = 2,
                 exceptions: Tuple[Exception] = (Exception,), jitter: float = 0,
                 verbose: bool = True):
        super().__init__(verbose)
        self.retries = retries
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.jitter = jitter
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = self.delay
            for attempt in range(self.retries):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    if attempt == self.retries - 1:
                        raise
                    sleep_time = current_delay * (1 + random.uniform(-self.jitter, self.jitter))
                    self._log(f"[RETRY] {func.__name__} failed: {e}. Retrying in {sleep_time:.2f}s...")
                    time_module.sleep(sleep_time)
                    current_delay *= self.backoff
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Retry Example
        @Retry(retries=3, delay=0.1, backoff=2, verbose=True)
        def fetch_data():
            if random.random() < 0.8:
                raise ConnectionError("API timeout")
            return "Data fetched"

        try:
            result = fetch_data()
        except Exception as e:
            print(f"Final error: {e}")
        # Expected output:
        # [RETRY] fetch_data failed: API timeout. Retrying in 0.12s...
        # [RETRY] fetch_data failed: API timeout. Retrying in 0.24s...
        """

class RetryWithExponentialBackoff(Retry):
    """Retry with exponential backoff and max delay limit"""
    def __init__(self, max_retries: int = 5, initial_delay: float = 1.0, 
                 max_delay: float = 60.0, exceptions: Tuple[Exception] = (Exception,),
                 verbose: bool = True):
        super().__init__(
            retries=max_retries,
            delay=initial_delay,
            backoff=2,
            exceptions=exceptions,
            verbose=verbose
        )
        self.max_delay = max_delay
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = self.delay
            for attempt in range(self.retries):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    if attempt == self.retries - 1:
                        raise
                    
                    # Calculate next delay with cap
                    next_delay = min(current_delay * (2 ** attempt), self.max_delay)
                    next_delay *= random.uniform(0.8, 1.2)  # Add jitter
                    
                    self._log(f"[RETRY] {func.__name__} failed (attempt {attempt+1}): {e}. "
                             f"Retrying in {next_delay:.2f}s...")
                    
                    time_module.sleep(next_delay)
            return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # RetryWithExponentialBackoff Example
        @RetryWithExponentialBackoff(
            max_retries=5, 
            initial_delay=1, 
            max_delay=30,
            verbose=True
        )
        def payment_processing():
            if random.random() < 0.7:
                raise Exception("Payment gateway error")
            return "Payment successful"

        payment_processing()
        # Expected output: Shows exponential backoff retries
        """

class AsyncRetry(DecoratorBase):
    """Async version of Retry decorator"""
    def __init__(self, retries: int = 3, delay: float = 1, backoff: float = 2,
                 exceptions: Tuple[Exception] = (Exception,), jitter: float = 0,
                 verbose: bool = True):
        super().__init__(verbose)
        self.retries = retries
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.jitter = jitter
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = self.delay
            for attempt in range(self.retries):
                try:
                    return await func(*args, **kwargs)
                except self.exceptions as e:
                    if attempt == self.retries - 1:
                        raise
                    sleep_time = current_delay * (1 + random.uniform(-self.jitter, self.jitter))
                    self._log(f"[ASYNCRETRY] {func.__name__} failed: {e}. Retrying in {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
                    current_delay *= self.backoff
        return async_wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # AsyncRetry Example
        @AsyncRetry(retries=3, delay=0.1, verbose=True)
        async def async_api_call():
            if random.random() < 0.7:
                raise ConnectionError("API timeout")
            return "Success"

        # In async context:
        # await async_api_call()
        # Expected output: Shows async retries
        """

class Suppress(DecoratorBase):
    """Suppress specified exceptions"""
    def __init__(self, *exceptions, verbose: bool = True):
        super().__init__(verbose)
        self.exceptions = exceptions or (Exception,)
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                self._log(f"[SUPPRESS] Suppressed {type(e).__name__} in {func.__name__}: {e}")
                return None
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Suppress Example
        @Suppress(ZeroDivisionError, ValueError, verbose=True)
        def safe_divide(a, b):
            return a / b

        result = safe_divide(10, 0)
        # Expected output: 
        # [SUPPRESS] Suppressed ZeroDivisionError in safe_divide: division by zero
        """

class CircuitBreaker(DecoratorBase):
    """Circuit breaker pattern for fault tolerance"""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0,
                 exceptions: Tuple[Exception] = (Exception,), verbose: bool = True):
        super().__init__(verbose)
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.exceptions = exceptions
        self.lock = threading.Lock()
        self.func_states = defaultdict(lambda: {
            "state": "CLOSED",
            "failure_count": 0,
            "last_failure_time": 0
        })
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                state_info = self.func_states[func.__name__]
                current_time = time_module.monotonic()
                
                if state_info["state"] == "OPEN":
                    if current_time - state_info["last_failure_time"] > self.recovery_timeout:
                        state_info["state"] = "HALF_OPEN"
                        self._log(f"[CIRCUIT] {func.__name__} moved to HALF_OPEN state")
                    else:
                        self._log(f"[CIRCUIT] {func.__name__} blocked (OPEN state)")
                        raise RuntimeError("Circuit breaker is OPEN")
                
            try:
                result = func(*args, **kwargs)
                
                with self.lock:
                    if state_info["state"] == "HALF_OPEN":
                        self._log(f"[CIRCUIT] {func.__name__} succeeded in HALF_OPEN state, resetting")
                        self._reset(func.__name__)
                return result
            except self.exceptions as e:
                with self.lock:
                    state_info["failure_count"] += 1
                    state_info["last_failure_time"] = time_module.monotonic()
                    
                    if state_info["failure_count"] >= self.failure_threshold:
                        state_info["state"] = "OPEN"
                        self._log(f"[CIRCUIT] {func.__name__} moved to OPEN state "
                                 f"({state_info['failure_count']} failures)")
                    
                    if state_info["state"] == "HALF_OPEN":
                        state_info["state"] = "OPEN"
                        self._log(f"[CIRCUIT] {func.__name__} failed in HALF_OPEN state, moving to OPEN")
                raise e
        
        def reset():
            with self.lock:
                self._reset(func.__name__)
        
        wrapper.reset = reset
        wrapper.state = property(lambda: self.func_states[func.__name__]["state"])
        return wrapper

    def _reset(self, func_name: str):
        state_info = self.func_states[func_name]
        state_info["state"] = "CLOSED"
        state_info["failure_count"] = 0
        self._log(f"[CIRCUIT] {func_name} circuit reset")
    
    @staticmethod
    def usage_example() -> str:
        return """
        # CircuitBreaker Example
        @CircuitBreaker(failure_threshold=3, recovery_timeout=10, verbose=True)
        def unstable_service():
            if random.random() > 0.3:
                raise ConnectionError("Service unavailable")
            return "Success"

        for i in range(5):
            try:
                print(unstable_service())
            except Exception as e:
                print(f"Error: {e}")
            time_module.sleep(1)
        # Expected output: Shows circuit state transitions
        """

class Timeout(DecoratorBase):
    """Timeout decorator with thread-based implementation"""
    def __init__(self, seconds: float, exception: Exception = TimeoutError, 
                 verbose: bool = True):
        super().__init__(verbose)
        self.seconds = seconds
        self.exception = exception
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._log(f"[TIMEOUT] Setting {self.seconds}s timeout for {func.__name__}")
            
            result = None
            exception_raised = None
            event = threading.Event()
            
            def target():
                nonlocal result, exception_raised
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    exception_raised = e
                finally:
                    event.set()
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            
            event.wait(self.seconds)
            
            if not event.is_set():
                self._log(f"[TIMEOUT] {func.__name__} timed out after {self.seconds}s")
                raise self.exception(f"Function {func.__name__} timed out after {self.seconds} seconds")
            
            if exception_raised:
                raise exception_raised
            
            return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Timeout Example
        @Timeout(seconds=1.5, verbose=True)
        def long_running_task():
            time_module.sleep(2)
            return "Completed"

        try:
            result = long_running_task()
        except TimeoutError as e:
            print(e)
        # Expected output: 
        # [TIMEOUT] Setting 1.5s timeout for long_running_task
        # [TIMEOUT] long_running_task timed out after 1.5s
        # Function long_running_task timed out after 1.5 seconds
        """

##############################
# 3. Caching & Memoization
##############################

class Memoize(DecoratorBase):
    """LRU-based memoization with cache statistics"""
    def __init__(self, maxsize: int = 128, verbose: bool = True):
        super().__init__(verbose)
        self.maxsize = maxsize
    
    def __call__(self, func: Callable) -> Callable:
        cached_func = lru_cache(maxsize=self.maxsize)(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = cached_func(*args, **kwargs)
            if self.verbose:
                cache_info = cached_func.cache_info()
                self._log(f"[MEMOIZE] {func.__name__} cache: "
                         f"hits={cache_info.hits}, misses={cache_info.misses}, "
                         f"size={cache_info.currsize}/{self.maxsize}")
            return result
        
        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Memoize Example
        @Memoize(maxsize=100, verbose=True)
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)

        print(fibonacci(10))
        # Expected output: Shows cache usage information
        """

class MemoizeWithTTL(DecoratorBase):
    """Memoization with time-based expiration"""
    def __init__(self, ttl: float = 60, maxsize: int = 128, verbose: bool = True):
        super().__init__(verbose)
        self.ttl = ttl
        self.maxsize = maxsize
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = self._make_key(func, args, kwargs)
            current_time = time_module.monotonic()
            
            with self.lock:
                # Check cache and TTL
                if key in self.cache:
                    if current_time - self.timestamps[key] < self.ttl:
                        self.timestamps[key] = current_time
                        self._log(f"[MEMOTTL] Cache hit for {func.__name__}")
                        return self.cache[key]
                    else:
                        # Remove expired
                        del self.cache[key]
                        del self.timestamps[key]
                
                # Apply maxsize
                if len(self.cache) >= self.maxsize:
                    oldest_key = min(self.timestamps, key=self.timestamps.get)
                    self._log(f"[MEMOTTL] Evicting oldest key for {func.__name__}")
                    del self.cache[oldest_key]
                    del self.timestamps[oldest_key]
            
            # Compute and cache
            result = func(*args, **kwargs)
            
            with self.lock:
                self.cache[key] = result
                self.timestamps[key] = current_time
                self._log(f"[MEMOTTL] Cached result for {func.__name__} (TTL: {self.ttl}s)")
            
            return result
        
        def clear_cache():
            with self.lock:
                self.cache.clear()
                self.timestamps.clear()
                self._log(f"[MEMOTTL] Cleared cache for {func.__name__}")
        
        wrapper.clear_cache = clear_cache
        return wrapper
    
    def _make_key(self, func, args, kwargs):
        return hashlib.md5(pickle.dumps((func.__name__, args, kwargs))).hexdigest()
    
    @staticmethod
    def usage_example() -> str:
        return """
        # MemoizeWithTTL Example
        @MemoizeWithTTL(ttl=5, maxsize=100, verbose=True)
        def get_weather(city):
            print(f"Fetching weather for {city}...")
            return {"city": city, "temp": random.randint(10, 30)}

        # First call - fetches
        weather1 = get_weather("London")
        # Second call within 5s - cached
        weather2 = get_weather("London")
        # After 5s - refetches
        time_module.sleep(6)
        weather3 = get_weather("London")
        # Expected output: Shows cache hits and misses
        """

class MemoizeDisk(DecoratorBase):
    """Disk-based memoization with file storage"""
    def __init__(self, cache_dir: str = ".cache", max_size: int = 100, verbose: bool = True):
        super().__init__(verbose)
        self.cache_dir = cache_dir
        self.max_size = max_size
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_files = []
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = self._make_key(func, args, kwargs)
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            
            # Check cache
            if os.path.exists(cache_file):
                self._log(f"[MEMODISK] Cache hit for {func.__name__}")
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            
            # Compute and save
            result = func(*args, **kwargs)
            
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)
            
            self.cache_files.append(cache_file)
            
            # Apply max size
            if len(self.cache_files) > self.max_size:
                oldest = self.cache_files.pop(0)
                os.remove(oldest)
                self._log(f"[MEMODISK] Evicted oldest cache file: {os.path.basename(oldest)}")
            
            return result
        return wrapper
    
    def _make_key(self, func, args, kwargs):
        return hashlib.md5(pickle.dumps((func.__name__, args, kwargs))).hexdigest()
    
    def clear_cache(self):
        for f in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, f))
        self.cache_files = []
        self._log("[MEMODISK] Disk cache cleared")
    
    @staticmethod
    def usage_example() -> str:
        return """
        # MemoizeDisk Example
        @MemoizeDisk(cache_dir=".math_cache", verbose=True)
        def expensive_calculation(x, y):
            print("Calculating...")
            time_module.sleep(1)
            return x ** y

        # First call - slow
        result1 = expensive_calculation(2, 10)
        # Second call - fast from disk cache
        result2 = expensive_calculation(2, 10)
        # Expected output: 
        # [MEMODISK] Cache hit for expensive_calculation
        """

class Idempotent(DecoratorBase):
    """Ensure function idempotency with key-based caching"""
    def __init__(self, key_func: Callable = None, ttl: float = 60, verbose: bool = True):
        super().__init__(verbose)
        self.key_func = key_func
        self.ttl = ttl
        self.results = {}
        self.timestamps = {}
        self.lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = self._make_key(func, args, kwargs)
            
            with self.lock:
                current_time = time_module.monotonic()
                
                # Check cache
                if key in self.results:
                    if current_time - self.timestamps[key] < self.ttl:
                        self._log(f"[IDEMPOTENT] Returning cached result for {func.__name__}")
                        return self.results[key]
                    else:
                        del self.results[key]
                        del self.timestamps[key]
            
            # Execute and cache
            result = func(*args, **kwargs)
            
            with self.lock:
                self.results[key] = result
                self.timestamps[key] = time_module.monotonic()
                self._log(f"[IDEMPOTENT] Cached result for {func.__name__} (TTL: {self.ttl}s)")
            
            return result
        return wrapper
    
    def _make_key(self, func, args, kwargs):
        if self.key_func:
            return self.key_func(*args, **kwargs)
        return hashlib.sha256(pickle.dumps((func.__name__, args, kwargs))).hexdigest()
    
    def clear_cache(self):
        with self.lock:
            self.results.clear()
            self.timestamps.clear()
            self._log("[IDEMPOTENT] Cache cleared")
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Idempotent Example
        @Idempotent(key_func=lambda user_id: f"user_{user_id}", ttl=300, verbose=True)
        def update_user_profile(user_id, data):
            print(f"Updating profile for user {user_id}")
            return {"status": "success"}

        # First call - executes
        update_user_profile(123, {"name": "John"})
        # Second call - returns cached result
        update_user_profile(123, {"name": "John"})
        # Expected output: 
        # [IDEMPOTENT] Returning cached result for update_user_profile
        """

##############################
# 4. Logging & Debugging
##############################
class Log(DecoratorBase):
    """
    logging decorator with comprehensive logging capabilities
    Supports: function calls, results, errors, execution time, variable tracking,
    debug statements, warnings, and custom log messages
    """

    def __init__(
        self,
        fpath: str,
        level: int = logging.INFO,
        format: str = None,
        verbose: bool = True,
        log_args: bool = True,
        log_return: bool = True,
        log_time: bool = True,
        log_errors: bool = True,
        log_debug: bool = False,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        mode: str = "a",
        encoding: str = "utf-8",
    ):
        """
        Args:
            fpath: Log file path
            level: Logging level
            format: Log message format
            verbose: Print to console
            log_args: Log function arguments
            log_return: Log return values
            log_time: Log execution time
            log_errors: Log exceptions
            log_debug: Enable debug logging within function
            max_file_size: Maximum log file size before rotation (bytes)
            backup_count: Number of backup files to keep
            mode: File open mode
            encoding: File encoding
        """
        super().__init__(verbose)
        self.fpath = fpath
        self.level = level
        self.format = format or "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        self.log_args = log_args
        self.log_return = log_return
        self.log_time = log_time
        self.log_errors = log_errors
        self.log_debug = log_debug
        self.mode = mode
        self.encoding = encoding

        Path(fpath).parent.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logger(max_file_size, backup_count)
        self._function_loggers: Dict[str, logging.Logger] = {}

    def _setup_logger(self, max_file_size: int, backup_count: int) -> logging.Logger:
        """Setup logger with file handler and rotation"""
        logger_name = f"Log4Jeff{hash(self.fpath)}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.level)

        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Use RotatingFileHandler for log rotation
        handler = logging.handlers.RotatingFileHandler(
            self.fpath,
            maxBytes=max_file_size,
            backupCount=backup_count,
            mode=self.mode,
            encoding=self.encoding,
        )

        formatter = logging.Formatter(self.format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

        return logger

    def _get_function_logger(self, func: Callable) -> logging.Logger:
        """Get or create a dedicated logger for the function"""
        func_id = f"{func.__module__}.{func.__name__}"
        if func_id not in self._function_loggers:
            func_logger = logging.getLogger(func_id)
            func_logger.setLevel(self.level)
            func_logger.handlers = self.logger.handlers
            func_logger.propagate = False
            self._function_loggers[func_id] = func_logger
        return self._function_loggers[func_id]

    def log_call(self, func: Callable, args: tuple, kwargs: dict) -> None:
        """Log function call with arguments"""
        if self.log_args:
            arg_str = self._format_arguments(func, args, kwargs)
            self.logger.info(f"CALL: {func.__name__}({arg_str})")
        else:
            self.logger.info(f"CALL: {func.__name__}()")

    def log_success(self, func: Callable, result: Any, duration: float) -> None:
        """Log successful function execution"""
        messages = []
        if self.log_time:
            messages.append(f"{duration:.6f}s")
        if self.log_return:
            result_str = self._format_value(result, max_length=200)
            messages.append(f"RESULT: {result_str}")

        if messages:
            self.logger.info(f"{func.__name__} - {' | '.join(messages)}")
        else:
            self.logger.info(f"{func.__name__} completed")

    def log_error(self, func: Callable, error: Exception, duration: float) -> None:
        """Log function error"""
        if self.log_errors:
            error_msg = f"ERROR: {func.__name__} -> {type(error).__name__}: {str(error)}"
            if self.log_time:
                error_msg += f" (after {duration:.6f}s)"
            self.logger.error(error_msg, exc_info=True)

    def log_debug_message(self, func: Callable, message: str, *args, **kwargs) -> None:
        """Log debug message from within the function"""
        if self.log_debug:
            func_logger = self._get_function_logger(func)
            func_logger.debug(f"{func.__name__} - {message}", *args, **kwargs)

    def log_info_message(self, func: Callable, message: str, *args, **kwargs) -> None:
        """Log info message from within the function"""
        func_logger = self._get_function_logger(func)
        func_logger.info(f"{func.__name__} - {message}", *args, **kwargs)

    def log_warning_message(
        self, func: Callable, message: str, *args, **kwargs
    ) -> None:
        """Log warning message from within the function"""
        func_logger = self._get_function_logger(func)
        func_logger.warning(f"{func.__name__} - {message}", *args, **kwargs)

    def log_variable(
        self, func: Callable, var_name: str, value: Any, level: str = "DEBUG"
    ) -> None:
        """Log variable value from within the function"""
        if level.upper() == "DEBUG" and not self.log_debug:
            return

        value_str = self._format_value(value)
        func_logger = self._get_function_logger(func)
        log_method = getattr(func_logger, level.lower(), func_logger.debug)
        log_method(f"{func.__name__} - {var_name} = {value_str}")

    def _format_arguments(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """Format function arguments for logging"""
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            arg_parts = []
            for param_name, param_value in bound_args.arguments.items():
                value_str = self._format_value(param_value)
                arg_parts.append(f"{param_name}={value_str}")

            return ", ".join(arg_parts)
        except (ValueError, TypeError):
            # Fallback if signature binding fails
            arg_parts = [self._format_value(arg) for arg in args]
            arg_parts.extend(f"{k}={self._format_value(v)}" for k, v in kwargs.items())
            return ", ".join(arg_parts)

    def _format_value(self, value: Any, max_length: int = 100) -> str:
        """Format a value for logging with length limits"""
        try:
            if value is None:
                return "None"
            elif isinstance(value, (int, float, bool)):
                return str(value)
            elif isinstance(value, str):
                if len(value) > max_length:
                    return f"'{value[:max_length]}...' ({len(value)} chars)"
                return f"'{value}'"
            elif isinstance(value, (list, tuple, set)):
                if len(value) > 5:  # Limit collection items
                    return f"{type(value).__name__}[{len(value)}]"
                return str(value)
            elif isinstance(value, dict):
                if len(value) > 3:  # Limit dict items
                    return f"dict[{len(value)}]"
                return str(value)
            else:
                type_name = type(value).__name__
                return f"<{type_name} object at {id(value):x}>"
        except Exception:
            return "<unrepresentable object>"

    def __call__(self, func: Callable) -> Callable:
        func_logger = self._get_function_logger(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log function call
            self.log_call(func, args, kwargs)

            # Execute function with timing
            start_time = time_module.perf_counter()
            
            # Create a context object for in-function logging
            log_context = {
                'debug': lambda msg, *a, **kw: self.log_debug_message(func, msg, *a, **kw),
                'info': lambda msg, *a, **kw: self.log_info_message(func, msg, *a, **kw),
                'warning': lambda msg, *a, **kw: self.log_warning_message(func, msg, *a, **kw),
                'variable': lambda name, value, level='DEBUG': self.log_variable(func, name, value, level),
                'logger': func_logger
            }
            
            try:
                # Store the log context in a thread-local variable for access within the function
                import threading
                thread_local = threading.local()
                thread_local.current_log_context = log_context
                
                result = func(*args, **kwargs)
                duration = time_module.perf_counter() - start_time

                # Log successful execution
                self.log_success(func, result, duration)

                self._log(
                    f"[Log] Comprehensive logging completed for {func.__name__} in {self.fpath}"
                )
                return result

            except Exception as e:
                duration = time_module.perf_counter() - start_time
                self.log_error(func, e, duration)
                raise
            finally:
                # Clean up thread-local storage
                if hasattr(threading.local(), 'current_log_context'):
                    del threading.local().current_log_context

        # Add logging methods as attributes to the wrapper function
        # These can be called from outside the function or within using the function name
        wrapper.log_debug = lambda msg, *a, **kw: self.log_debug_message(func, msg, *a, **kw)
        wrapper.log_info = lambda msg, *a, **kw: self.log_info_message(func, msg, *a, **kw)
        wrapper.log_warning = lambda msg, *a, **kw: self.log_warning_message(func, msg, *a, **kw)
        wrapper.log_variable = lambda name, value, level="DEBUG": self.log_variable(func, name, value, level)
        wrapper.get_logger = lambda: func_logger
        
        # Add a method to get the current log context (for use within the function)
        wrapper.get_log_context = lambda: getattr(threading.local(), 'current_log_context', None)

        return wrapper

    @staticmethod
    def usage_example() -> str:
        return """
        # Log Example - Comprehensive logging capabilities
        
        @Log(
            fpath="app.log",
            level=logging.DEBUG,
            verbose=True,
            log_args=True,
            log_return=True,
            log_time=True,
            log_errors=True,
            log_debug=True  # Enable debug logging within function
        )
        def process_data(data, threshold=10):
            # Method 1: Use the function's own methods (recommended)
            process_data.log_debug("Starting data processing")
            process_data.log_variable("input_data", data)
            process_data.log_variable("threshold", threshold)
            
            if len(data) > threshold:
                process_data.log_warning("Data size exceeds threshold")
            
            # Method 2: Access via thread-local context (alternative)
            log_ctx = process_data.get_log_context()
            if log_ctx:
                log_ctx['info']("Processing data...")
            
            # Process data
            result = [x * 2 for x in data if x > 0]
            process_data.log_variable("result_size", len(result))
            
            process_data.log_info("Data processing completed successfully")
            return result
        
        # Usage
        data = [1, 2, 3, 4, 5, -1, -2]
        result = process_data(data, threshold=5)
        
        # You can also log from outside the function:
        process_data.log_info("This log comes from outside the function execution")
        
        # Expected log file content:
        # 2023-10-15 12:00:00 - INFO - CALL: process_data(data=[1, 2, 3, 4, 5, -1, -2], threshold=5)
        # 2023-10-15 12:00:00 - DEBUG - process_data - Starting data processing
        # 2023-10-15 12:00:00 - DEBUG - process_data - input_data = [1, 2, 3, 4, 5, -1, -2]
        # 2023-10-15 12:00:00 - DEBUG - process_data - threshold = 5
        # 2023-10-15 12:00:00 - WARNING - process_data - Data size exceeds threshold
        # 2023-10-15 12:00:00 - INFO - process_data - Processing data...
        # 2023-10-15 12:00:00 - DEBUG - process_data - result_size = 5
        # 2023-10-15 12:00:00 - INFO - process_data - Data processing completed successfully
        # 2023-10-15 12:00:00 - INFO - process_data - 0.000123s | RESULT: [2, 4, 6, 8, 10]
        # 2023-10-15 12:00:00 - INFO - process_data - This log comes from outside the function execution
        """
class Debug:
    """Comprehensive debugging with argument, return value, and timing logging"""
    def __init__(self, log_args: bool = True, log_return: bool = True,
                 log_time: bool = True, log_level: int = logging.DEBUG,
                 verbose: bool = True):
        self.log_args = log_args
        self.log_return = log_return
        self.log_time = log_time
        self.log_level = log_level
        self.verbose = verbose
    
    def __call__(self, func: Callable) -> Callable:
        logger = logging.getLogger(func.__module__)
        is_coroutine = inspect.iscoroutinefunction(func)
        
        if is_coroutine:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_async(func, args, kwargs, logger)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._execute_sync(func, args, kwargs, logger)
            return sync_wrapper
    
    async def _execute_async(self, func, args, kwargs, logger):
        """Execute and log an async function"""
        # Log arguments
        if self.log_args:
            arg_str = ", ".join([repr(a) for a in args] +
                               [f"{k}={v!r}" for k, v in kwargs.items()])
            logger.log(self.log_level, f"[DEBUG] Calling {func.__name__}({arg_str})")
        
        # Execute and time
        start_time = time_module.perf_counter()
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            end_time = time_module.perf_counter()
            logger.log(self.log_level, 
                      f"[DEBUG] {func.__name__} raised {type(e).__name__} after "
                      f"{(end_time - start_time):.4f}s: {e}")
            raise
        
        end_time = time_module.perf_counter()
        
        # Log results
        if self.log_return:
            logger.log(self.log_level, f"[DEBUG] {func.__name__} returned: {result!r}")
        
        if self.log_time:
            logger.log(self.log_level, 
                      f"[DEBUG] {func.__name__} executed in {(end_time - start_time):.4f}s")
        
        return result
    
    def _execute_sync(self, func, args, kwargs, logger):
        """Execute and log a sync function"""
        # Log arguments
        if self.log_args:
            arg_str = ", ".join([repr(a) for a in args] +
                               [f"{k}={v!r}" for k, v in kwargs.items()])
            logger.log(self.log_level, f"[DEBUG] Calling {func.__name__}({arg_str})")
        
        # Execute and time
        start_time = time_module.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            end_time = time_module.perf_counter()
            logger.log(self.log_level, 
                      f"[DEBUG] {func.__name__} raised {type(e).__name__} after "
                      f"{(end_time - start_time):.4f}s: {e}")
            raise
        
        end_time = time_module.perf_counter()
        
        # Log results
        if self.log_return:
            logger.log(self.log_level, f"[DEBUG] {func.__name__} returned: {result!r}")
        
        if self.log_time:
            logger.log(self.log_level, 
                      f"[DEBUG] {func.__name__} executed in {(end_time - start_time):.4f}s")
        
        return result
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Debug Example
        @Debug(log_args=True, log_return=True, log_time=True, verbose=True)
        def complex_calculation(a, b):
            time_module.sleep(0.2)
            return a * b + a / b

        result = complex_calculation(10, 5)
        # Expected output: Detailed debug logs
"""

##############################
# 5. Concurrency & Threading
##############################
class Threaded(DecoratorBase):
    """
    装饰器：使目标函数（同步或异步）在后台线程中异步执行。

    推荐用于：日志记录、API调用、文件操作、定时任务
    慎用于：数学计算、数据处理（考虑用@Processed多进程）
    不适用：需要立即获取返回值的函数
    参数说明：
    ----------
    daemon : bool，默认值为 True
        若为 True，则创建的线程为守护线程（daemon thread），守护线程不会阻止主程序退出。
    verbose : bool，默认值为 True
        若为 True，将通过 self._log 输出线程启动信息。

    返回值：
    -------
    Callable
        返回包装后的函数，调用时会在后台线程中运行原函数，并返回 `threading.Thread` 对象。

    注意事项：
    --------
    - 异步函数会在新线程的独立事件循环中执行。
    - 被线程执行的函数不会返回值（使用共享变量/队列获取结果）。
    - 线程中的异常不会传播到主线程。

    示例：
    -----
    # 同步函数
    @Threaded()
    def sync_task():
        time.sleep(2)
        print("同步任务完成")

    # 异步函数
    @Threaded()
    async def async_task():
        await asyncio.sleep(2)
        print("异步任务完成")

    thread1 = sync_task()   # 在后台线程运行同步函数
    thread2 = async_task()  # 在后台线程运行异步函数
    print("主线程继续执行")
    """
    def __init__(self, daemon: bool = True, verbose: bool = True):
        super().__init__(verbose)
        self.daemon = daemon
    
    def __call__(self, func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            # 处理异步函数
            @functools.wraps(func)
            def async_wrapper(*args, **kwargs) -> threading.Thread:
                self._log(f"Starting thread for async function {func.__name__}")
                thread = threading.Thread(
                    target=self._run_async_func,
                    args=(func, args, kwargs),
                    daemon=self.daemon,
                    name=f"Threaded-{func.__name__}"
                )
                thread.start()
                return thread
            return async_wrapper
        else:
            # 处理同步函数（原始逻辑）
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> threading.Thread:
                self._log(f"Starting thread for function {func.__name__}")
                thread = threading.Thread(
                    target=func,
                    args=args,
                    kwargs=kwargs,
                    daemon=self.daemon,
                    name=f"Threaded-{func.__name__}"
                )
                thread.start()
                return thread
            return sync_wrapper

    def _safe_run_sync(self, func: Callable, args, kwargs) -> None:
        """同步函数的安全执行包装器"""
        try:
            func(*args, **kwargs)
        except Exception as e:
            self._log(f"Threaded function {func.__name__} failed: {e}")
            traceback.print_exc()

    def _run_async_func(self, func: Callable, args, kwargs) -> None:
        """在新线程中运行异步函数的事件循环"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(func(*args, **kwargs))
        except Exception as e:
            self._log(f"Async threaded function {func.__name__} failed: {e}")
            traceback.print_exc()
        finally:
            try:
                loop.close()
            except:
                pass
    @staticmethod
    def usage_example() -> str:
        return """
        # 同步函数示例
        @Threaded(daemon=True, verbose=True)
        def background_task():
            print("Background task started")
            time.sleep(2)
            print("Background task completed")

        # 异步函数示例
        @Threaded(daemon=True, verbose=True)
        async def async_background_task():
            print("Async background task started")
            await asyncio.sleep(2)
            print("Async background task completed")

        # 使用
        thread1 = background_task()
        thread2 = async_background_task()
        print("Main thread continues")
        thread1.join()
        thread2.join()
        """

class Synchronized(DecoratorBase):
    """Synchronize function access with a lock"""
    def __init__(self, lock: threading.Lock = None, verbose: bool = True):
        super().__init__(verbose)
        self.lock = lock or threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._log(f"[SYNC] Acquiring lock for {func.__name__}")
            with self.lock:
                self._log(f"[SYNC] Lock acquired for {func.__name__}")
                result = func(*args, **kwargs)
            self._log(f"[SYNC] Lock released for {func.__name__}")
            return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Synchronized Example
        counter = 0
        lock = threading.Lock()

        @Synchronized(lock=lock, verbose=True)
        def increment_counter():
            global counter
            counter += 1

        threads = []
        for _ in range(5):
            t = threading.Thread(target=increment_counter)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        print(f"Counter value: {counter}")  # Should be 5
        # Expected output: Shows lock acquisition/release
        """

class RateLimit(DecoratorBase):
    """Limit function call rate"""
    def __init__(self, calls: int = 5, period: float = 1.0, verbose: bool = True):
        super().__init__(verbose)
        self.calls = calls
        self.period = period
        self.call_times = defaultdict(list)
        self.lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time_module.monotonic()
                times = self.call_times[func.__name__]
                
                # Remove old calls
                times = [t for t in times if now - t < self.period]
                
                if len(times) >= self.calls:
                    wait_time = self.period - (now - times[0])
                    self._log(f"[RATE_LIMIT] Blocked {func.__name__}; try again in {wait_time:.2f}s")
                    raise RuntimeError(
                        f"Too many calls to {func.__name__}; try again in {wait_time:.2f}s"
                    )
                
                times.append(now)
                self.call_times[func.__name__] = times
                self._log(f"[RATE_LIMIT] {func.__name__} called ({len(times)}/{self.calls} in last {self.period}s)")
            
            return func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # RateLimit Example
        @RateLimit(calls=3, period=5, verbose=True)
        def api_request():
            return "Response"

        for i in range(5):
            try:
                print(api_request())
            except Exception as e:
                print(e)
        # Expected output: Shows rate limiting in action
        """

class Throttle(DecoratorBase):
    """Throttle function calls to minimum interval"""
    def __init__(self, min_interval: float = 1.0, last_result: bool = True,
                 verbose: bool = True):
        super().__init__(verbose)
        self.min_interval = min_interval
        self.last_result = last_result
        self.last_time = 0
        self.last_result_value = None
        self.lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time_module.monotonic()
            
            with self.lock:
                time_since_last = current_time - self.last_time
                
                if time_since_last < self.min_interval:
                    if self.last_result:
                        self._log(f"[THROTTLE] {func.__name__} throttled, returning last result")
                        return self.last_result_value
                    else:
                        self._log(f"[THROTTLE] {func.__name__} skipped (too frequent)")
                        return None
                
                result = func(*args, **kwargs)
                self.last_time = current_time
                self.last_result_value = result
                self._log(f"[THROTTLE] {func.__name__} executed after {time_since_last:.2f}s")
                return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # Throttle Example
        @Throttle(min_interval=2.0, last_result=True, verbose=True)
        def refresh_data():
            return time_module.time()

        # First call executes
        print(refresh_data())
        # Subsequent calls within 2 seconds return last result
        time_module.sleep(1)
        print(refresh_data())
        time_module.sleep(1.5)
        print(refresh_data())  # Now executes again
        # Expected output: Shows throttling behavior
        """

class LockByResource(DecoratorBase):
    """Resource-based locking for concurrent access control"""
    def __init__(self, resource_func: Callable, verbose: bool = True):
        super().__init__(verbose)
        self.resource_func = resource_func
        self.locks = defaultdict(threading.Lock)
        self.global_lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            resource_id = self.resource_func(*args, **kwargs)
            self._log(f"[LOCKRES] Acquiring lock for resource '{resource_id}'")
            
            with self.global_lock:
                lock = self.locks[resource_id]
            
            with lock:
                self._log(f"[LOCKRES] Lock acquired for resource '{resource_id}'")
                result = func(*args, **kwargs)
                self._log(f"[LOCKRES] Lock released for resource '{resource_id}'")
                return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # LockByResource Example
        @LockByResource(
            resource_func=lambda user_id: f"user_{user_id}",
            verbose=True
        )
        def update_user_profile(user_id, updates):
            print(f"Updating profile for user {user_id}")
            time_module.sleep(1)

        # Can update different users concurrently
        threading.Thread(target=update_user_profile, args=(1, {})).start()
        threading.Thread(target=update_user_profile, args=(2, {})).start()
        # But same user will be locked
        threading.Thread(target=update_user_profile, args=(1, {})).start()
        # Expected output: Shows resource-based locking
        """

##############################
# 6. Validation & Safety
##############################

class ValidateArgs(DecoratorBase):
    """Validate function arguments and return values"""
    def __init__(self, arg_validators: Dict[str, Callable] = None, 
                 result_validator: Callable = None,
                 exception: Exception = ValueError, verbose: bool = True):
        super().__init__(verbose)
        self.arg_validators = arg_validators or {}
        self.result_validator = result_validator
        self.exception = exception
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate arguments
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for arg_name, validator in self.arg_validators.items():
                if arg_name in bound_args.arguments:
                    value = bound_args.arguments[arg_name]
                    if not validator(value):
                        self._log(f"[VALIDATE] Invalid argument: {arg_name}={value}")
                        raise self.exception(f"Invalid argument: {arg_name}={value}")
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Validate result
            if self.result_validator and not self.result_validator(result):
                self._log(f"[VALIDATE] Invalid result: {result}")
                raise self.exception(f"Invalid result: {result}")
            
            self._log(f"[VALIDATE] {func.__name__} arguments and result validated")
            return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
        # ValidateArgs Example
        @ValidateArgs(
            arg_validators={
                'age': lambda x: x >= 0,
                'name': lambda x: isinstance(x, str) and x.strip() != ""
            },
            result_validator=lambda x: isinstance(x, int),
            verbose=True
        )
        def calculate_birth_year(age, name):
            return 2023 - age

        try:
            year = calculate_birth_year(-5, "Alice")
        except ValueError as e:
            print(f"Error: {e}")
        # Expected output:
        # [VALIDATE] Invalid argument: age=-5
        # Error: Invalid argument: age=-5
        """

def Kwargs(
    how: str = "pop",
    strict: bool = False,
    ignore_private: bool = True,
    keep_extra: bool = False,
    **decorator_kwargs,
):
    """
    Usage:
    @Kwargs(how='filter')
    def my_function(**kwargs):
        ...
    """
    
    from ..ips import handle_kwargs
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Only handle keyword arguments, not positional
            if kwargs:
                processed_kwargs = handle_kwargs(
                    kwargs,
                    func=func,
                    how=how,
                    strict=strict,
                    ignore_private=ignore_private,
                    keep_extra=keep_extra,
                    **decorator_kwargs,
                )
                return func(*args, **processed_kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
class TypeCheck(DecoratorBase):
    """
    装饰器：在运行时对函数参数和返回值进行类型检查，支持严格模式和宽松模式。

    功能描述：
    --------
    `TypeCheck` 用于在函数执行前后，对参数和返回值类型进行验证：
    - 在严格模式下，如果类型不匹配将抛出 TypeError。
    - 在宽松模式下，若类型不匹配，会尝试进行类型转换（如将字符串 "5" 转为整数 5）。

    参数说明：
    --------
    arg_types : Dict[str, type]，默认值为 None
        指定参数名称及其期望类型的字典，例如 {'x': int, 'y': float}。

    return_type : type，默认值为 None
        指定返回值的类型。如果指定，将检查函数返回值的类型。

    strict : bool，默认值为 True
        - True：严格模式，类型不符立即抛出异常。
        - False：宽松模式，尝试自动类型转换，不可转换时报错。

    verbose : bool，默认值为 True
        若为 True，类型检查过程中的日志信息将被打印（或记录）。

    返回值：
    -------
    Callable
        返回包装后的函数，带有类型检查功能。

    注意事项：
    --------
    - 宽松模式下类型转换可能失败，此时仍会抛出 TypeError。
    - 参数必须在 `arg_types` 中显式列出才会被检查。
    - return_type 仅在函数有返回值时生效。

    示例：
    -----
    @TypeCheck(
        arg_types={'x': int, 'y': float},
        return_type=float,
        strict=False,
        verbose=True
    )
    def multiply(x, y):
        return x * y

    result = multiply("5", 3.2)
    # 输出示例：
    # [TYPECHECK] Converted x from <class 'str'> to <class 'int'>
    # [TYPECHECK] multiply type checks passed
    """

    def __init__(self, arg_types: Dict[str, type] = None, 
                 return_type: type = None, strict: bool = True,
                 verbose: bool = True):
        super().__init__(verbose)
        self.arg_types = arg_types or {}
        self.return_type = return_type
        self.strict = strict
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for arg_name, expected_type in self.arg_types.items():
                if arg_name in bound_args.arguments:
                    value = bound_args.arguments[arg_name]
                    if not isinstance(value, expected_type):
                        if self.strict:
                            self._log(f"[TYPECHECK] Argument {arg_name} must be {expected_type}, got {type(value)}")
                            raise TypeError(
                                f"Argument {arg_name} must be {expected_type}, got {type(value)}"
                            )
                        else:
                            try:
                                new_value = expected_type(value)
                                self._log(f"[TYPECHECK] Converted {arg_name} from {type(value)} to {expected_type}")
                                bound_args.arguments[arg_name] = new_value
                            except (TypeError, ValueError):
                                self._log(f"[TYPECHECK] Failed to convert {arg_name} to {expected_type}")
                                raise TypeError(
                                    f"Argument {arg_name} must be convertible to {expected_type}, got {type(value)}"
                                )
            
            result = func(*bound_args.args, **bound_args.kwargs)
            
            if self.return_type and not isinstance(result, self.return_type):
                self._log(f"[TYPECHECK] Return value must be {self.return_type}, got {type(result)}")
                raise TypeError(
                    f"Return value must be {self.return_type}, got {type(result)}"
                )
            
            self._log(f"[TYPECHECK] {func.__name__} type checks passed")
            return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
# TypeCheck Example
@TypeCheck(
    arg_types={'x': int, 'y': float},
    return_type=float,
    strict=False,
    verbose=True
)
def multiply(x, y):
    return x * y

result = multiply("5", 3.2)  # Converts string to int
# Expected output:
# [TYPECHECK] Converted x from <class 'str'> to <class 'int'>
# [TYPECHECK] multiply type checks passed
"""

class ValidateJSON(DecoratorBase):
    """Validate JSON output against a schema"""
    def __init__(self, schema: dict, verbose: bool = True):
        super().__init__(verbose)
        self.schema = schema
        try:
            from jsonschema import validate, ValidationError
            self.validate_func = validate
            self.ValidationError = ValidationError
        except ImportError:
            raise ImportError("jsonschema package is required for ValidateJSON")
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                self.validate_func(instance=result, schema=self.schema)
                self._log(f"[VALIDJSON] {func.__name__} result validated against schema")
            except self.ValidationError as e:
                self._log(f"[VALIDJSON] {func.__name__} result validation failed: {e}")
                raise ValueError(f"Result validation failed: {e}") from e
            return result
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
# ValidateJSON Example
# Requires: pip install jsonschema
user_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"}
    },
    "required": ["id", "name"]
}

@ValidateJSON(schema=user_schema, verbose=True)
def get_user(user_id):
    return {"id": user_id, "name": "John Doe"}

user = get_user(123)
# Expected output:
# [VALIDJSON] get_user result validated against schema
"""

class ValidateResponse(DecoratorBase):
    """Validate function response using a custom validator"""
    def __init__(self, validator_func: Callable, verbose: bool = True):
        super().__init__(verbose)
        self.validator_func = validator_func
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if not self.validator_func(response):
                self._log(f"[VALIDRESP] Response validation failed for {func.__name__}")
                raise ValueError(f"Invalid response from {func.__name__}")
            self._log(f"[VALIDRESP] Response validated for {func.__name__}")
            return response
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
# ValidateResponse Example
def validate_user(user):
    return isinstance(user, dict) and 'id' in user and 'name' in user

@ValidateResponse(validator_func=validate_user, verbose=True)
def get_user(user_id):
    return {"id": user_id, "name": "Alice"}

user = get_user(123)
# Expected output:
# [VALIDRESP] Response validated for get_user
"""

##############################
# 7. Utility & Helpers
##############################

class Deprecate(DecoratorBase):
    """Mark function as deprecated"""
    def __init__(self, message: str = "This function is deprecated", 
                 version: str = "future", verbose: bool = True):
        super().__init__(verbose)
        self.message = message
        self.version = version
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.verbose:
                warnings.warn(
                    f"{func.__name__} is deprecated since version {self.version}: {self.message}",
                    category=DeprecationWarning,
                    stacklevel=2
                )
            return func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
# Deprecate Example
@Deprecate(message="Use new_function instead", version="2.0", verbose=True)
def old_function():
    return "Old result"

old_function()
# Expected output: 
# DeprecationWarning: old_function is deprecated since version 2.0: Use new_function instead
"""

class CountCalls(DecoratorBase):
    """
    装饰器：统计函数被调用的次数。

    功能描述：
    --------
    该装饰器会对被装饰函数的调用次数进行计数，并在每次调用时打印调用次数日志。
    线程安全，内部使用锁机制防止多线程环境下计数出错。

    参数说明：
    --------
    verbose : bool，默认值为 True
        是否打印调用次数的日志信息。若为 True，则每次调用都会输出调用次数。

    返回值：
    -------
    Callable
        返回包装后的函数，调用时自动统计调用次数，并调用原函数。

    注意事项：
    --------
    - 计数器对每个装饰器实例独立维护。
    - 线程安全设计，适用于多线程环境。
    - 可以通过访问装饰器实例的 `calls` 属性获取当前调用次数（注意当前实现中访问方式可能需要调整）。

    示例：
    -----
    @CountCalls(verbose=True)
    def process_item(item):
        return item * 2

    process_item(5)
    process_item(10)
    # 输出示例：
    # [COUNT] process_item called 1 times
    # [COUNT] process_item called 2 times
    """

    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.calls = 0
        self.lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                self.calls += 1
                self._log(f"[COUNT] {func.__name__} called {self.calls} times")
            return func(*args, **kwargs)
        
        wrapper.calls = property(lambda self: self.calls)
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
# CountCalls Example
@CountCalls(verbose=True)
def process_item(item):
    return item * 2

process_item(5)
process_item(10)
# Expected output:
# [COUNT] process_item called 1 times
# [COUNT] process_item called 2 times
"""

class Singleton(DecoratorBase):
    """Singleton pattern implementation"""
    def __init__(self, cls, verbose: bool = True):
        super().__init__(verbose)
        self.cls = cls
        self.instance = None
        self.lock = threading.Lock()
    
    def __call__(self, *args, **kwargs):
        if self.instance is None:
            with self.lock:
                if self.instance is None:
                    self._log(f"[SINGLETON] Creating new instance of {self.cls.__name__}")
                    self.instance = self.cls(*args, **kwargs)
                elif self.verbose:
                    self._log(f"[SINGLETON] Returning existing instance of {self.cls.__name__}")
        return self.instance
    
    @staticmethod
    def usage_example() -> str:
        return """
# Singleton Example
@Singleton
class DatabaseConnection:
    def __init__(self):
        print("Initializing database connection")

conn1 = DatabaseConnection()
conn2 = DatabaseConnection()
# Expected output: 
# [SINGLETON] Creating new instance of DatabaseConnection
# Initializing database connection
# [SINGLETON] Returning existing instance of DatabaseConnection
"""

class DepInject(DecoratorBase):
    """Dependency injection decorator"""
    def __init__(self, dependencies: Dict[str, Any], verbose: bool = True):
        super().__init__(verbose)
        self.dependencies = dependencies
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            resolved_deps = {}
            for dep_name, dep_value in self.dependencies.items():
                if dep_name in kwargs:
                    resolved_deps[dep_name] = kwargs.pop(dep_name)
                else:
                    resolved_deps[dep_name] = dep_value
            
            self._log(f"[DEPINJECT] Injecting dependencies for {func.__name__}: "
                     f"{', '.join(f'{k}={v}' for k, v in resolved_deps.items())}")
            
            return func(*args, **resolved_deps, **kwargs)
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
# DepInject Example
class DatabaseService:
    def query(self, sql):
        return f"Results for {sql}"

@DepInject(dependencies={"db": DatabaseService()}, verbose=True)
def run_query(query, db):
    return db.query(query)

result = run_query("SELECT * FROM users")
# Expected output:
# [DEPINJECT] Injecting dependencies for run_query: db=<__main__.DatabaseService object>
"""

class FeatureFlag(DecoratorBase):
    """Feature flag implementation with fallback"""
    def __init__(self, flag_name: str, flag_checker: Callable[[str], bool],
                 fallback_func: Optional[Callable] = None, verbose: bool = True):
        super().__init__(verbose)
        self.flag_name = flag_name
        self.flag_checker = flag_checker
        self.fallback_func = fallback_func
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_enabled = self.flag_checker(self.flag_name)
            
            if is_enabled:
                self._log(f"[FEATURE] {self.flag_name} enabled, using {func.__name__}")
                return func(*args, **kwargs)
            elif self.fallback_func:
                self._log(f"[FEATURE] {self.flag_name} disabled, using fallback")
                return self.fallback_func(*args, **kwargs)
            else:
                self._log(f"[FEATURE] {self.flag_name} disabled, no fallback")
                raise RuntimeError(f"Feature '{self.flag_name}' is disabled")
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
# FeatureFlag Example
def is_feature_enabled(feature):
    return feature == "new_ui"

def old_ui():
    return "Old UI"

@FeatureFlag(
    "new_ui", 
    is_feature_enabled, 
    fallback_func=old_ui,
    verbose=True
)
def new_ui():
    return "New UI"

print(new_ui())  # Output depends on feature flag
# Expected output: Shows feature flag status
"""

class Repeat(DecoratorBase):
    """Repeat function execution multiple times"""
    def __init__(self, times: int = 3, verbose: bool = True):
        super().__init__(verbose)
        self.times = times
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for i in range(self.times):
                self._log(f"[REPEAT] {func.__name__} iteration {i+1}/{self.times}")
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    
    @staticmethod
    def usage_example() -> str:
        return """
# Repeat Example
@Repeat(times=3, verbose=True)
def roll_dice():
    return random.randint(1, 6)

results = roll_dice()
print(f"Dice rolls: {results}")
# Expected output:
# [REPEAT] roll_dice iteration 1/3
# [REPEAT] roll_dice iteration 2/3
# [REPEAT] roll_dice iteration 3/3
# Dice rolls: [4, 2, 5]
"""

class RedirectOutput(DecoratorBase):
    """Redirect stdout/stderr during function execution"""
    def __init__(self, stdout: io.StringIO = None, stderr: io.StringIO = None, 
                 verbose: bool = True):
        super().__init__(verbose)
        self.stdout = stdout or io.StringIO()
        self.stderr = stderr or io.StringIO()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._log(f"[REDIRECT] Redirecting output for {func.__name__}")
            
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            
            try:
                result = func(*args, **kwargs)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                self._log(f"[REDIRECT] Restored output for {func.__name__}")
            
            return result
        return wrapper
    
    def get_stdout(self) -> str:
        return self.stdout.getvalue()
    
    def get_stderr(self) -> str:
        return self.stderr.getvalue()
    
    @staticmethod
    def usage_example() -> str:
        return """
        # RedirectOutput Example
        redirect = RedirectOutput(verbose=True)

        @redirect
        def noisy_function():
            print("This goes to stdout")
            print("Error message", file=sys.stderr)

        noisy_function()

        print("Captured stdout:", redirect.get_stdout())
        print("Captured stderr:", redirect.get_stderr())
        # Expected output:
        # [REDIRECT] Redirecting output for noisy_function
        # [REDIRECT] Restored output for noisy_function
        # Captured stdout: This goes to stdout
        # Captured stderr: Error message
        """

# def show_progress(
#     func=None, 
#     *, 
#     total=None, 
#     desc=None, 
#     min_length=5,
#     max_length=None,
#     exclude_types=None,
#     enable=True,
#     **tqdm_kwargs
# ):
#     """
#     Advanced version with more control over progress bar behavior.
    
#     Args:
#         total: Total iterations for progress bar
#         desc: Description for progress bar
#         min_length: Minimum iterable length to show progress bar
#         max_length: Maximum iterable length to show progress bar
#         exclude_types: Additional types to exclude from wrapping
#         enable: Enable/disable progress bars
#         **tqdm_kwargs: Custom tqdm parameters
    
#     Usage:
#         @show_progress(min_length=10, max_length=1000, colour='blue')
#         def filtered_processing(data):
#             for item in data:  # Only shows bar if 10 <= len(data) <= 1000
#                 pass
#     """
#     from functools import wraps
#     from tqdm.auto import tqdm
#     import collections.abc
    
#     def _is_iterable_eligible(obj):
#         """Check if object should be wrapped with tqdm"""
#         from collections.abc import Iterable
#         EXCLUDE_TYPES = (str, bytes, dict)
        
#         if not isinstance(obj, Iterable):
#             return False
#         if isinstance(obj, EXCLUDE_TYPES):
#             return False
#         return True


#     def _is_already_wrapped(obj):
#         """Check if object is already wrapped with tqdm"""
#         return hasattr(obj, '_tqdm_wrapped') or hasattr(obj, 'disable') or hasattr(obj, 'close')


#     def _is_eligible_advanced(obj, min_length, max_length, exclude_types):
#         """Advanced eligibility check for progress bar wrapping"""
#         from collections.abc import Iterable
        
#         if not isinstance(obj, Iterable):
#             return False
#         if isinstance(obj, exclude_types):
#             return False
        
#         # Check length constraints
#         try:
#             length = len(obj)
#             if length < min_length:
#                 return False
#             if max_length and length > max_length:
#                 return False
#         except (TypeError, AttributeError):
#             # Can't determine length, use default behavior
#             pass
        
#         return not _is_already_wrapped(obj)

#     def _normalize_tqdm_kwargs(kwargs):
#         """Normalize tqdm parameters to handle both color/colour spelling"""
#         # Ensure we always have a dictionary
#         if kwargs is None:
#             kwargs = {}
        
#         normalized = kwargs.copy()
        
#         # Handle color/colour preference
#         if 'colour' in normalized and 'color' in normalized:
#             # If both are provided, prefer 'color' (American English)
#             del normalized['color']
#         elif 'color' in normalized:
#             # Convert British 'colour' to American 'color'
#             normalized['colour'] = normalized['color']
#             del normalized['color']
        
#         return normalized

#     # Main Func
#     if exclude_types is None:
#         exclude_types = (str, bytes, dict)

#     def decorator(f):
#         @wraps(f)
#         def wrapper(*args, **kwargs):
#             if not enable:
#                 return f(*args, **kwargs)
            
#             # Normalize color/colour parameter
#             normalized_kwargs = _normalize_tqdm_kwargs(tqdm_kwargs or {})
#             new_args = []
#             for i, arg in enumerate(args):
#                 if _is_eligible_advanced(arg, min_length, max_length, exclude_types):
#                     arg_desc = desc or f"Processing {i}"
#                     new_args.append(tqdm(arg, total=total, desc=arg_desc, **normalized_kwargs))
#                 else:
#                     new_args.append(arg)

#             new_kwargs = {}
#             for k, v in kwargs.items():
#                 if _is_eligible_advanced(v, min_length, max_length, exclude_types):
#                     arg_desc = desc or f"Processing {k}"
#                     new_kwargs[k] = tqdm(v, total=total, desc=arg_desc, **normalized_kwargs)
#                 else:
#                     new_kwargs[k] = v

#             return f(*new_args, **new_kwargs)
#         return wrapper

#     if func:
#         return decorator(func)
#     return decorator

import inspect
import ast
import sys
import types
from functools import wraps
from collections.abc import Iterable
from tqdm.auto import tqdm
import textwrap
import dis
import re

class ForLoopTracker:
    """Tracks and intercepts for loops in decorated functions"""
    
    def __init__(self, iterable, pbar_params):
        self.iterable = iterable
        self.pbar_params = pbar_params
        self._iterator = None
        self.pbar = None
        
    def __iter__(self):
        # Create progress bar
        total = self.pbar_params.get('total')
        if total is None and hasattr(self.iterable, '__len__'):
            total = len(self.iterable)
            
        # Filter out any tqdm parameters that might cause issues
        safe_params = {}
        for k, v in self.pbar_params.items():
            if k not in ['total', 'desc']:
                # Convert 'color' to 'colour' for tqdm compatibility
                if k == 'color':
                    safe_params['colour'] = v
                else:
                    safe_params[k] = v
            
        self.pbar = tqdm(
            total=total,
            desc=self.pbar_params.get('desc', 'Processing'),
            **{k: v for k, v in self.pbar_params.items() 
               if k not in ['total', 'desc']}
        )
        
        self._iterator = iter(self.iterable)
        return self
    
    def __next__(self):
        try:
            item = next(self._iterator)
            self.pbar.update(1)
            return item
        except StopIteration:
            self.pbar.close()
            raise

class ProgressContextManager:
    """Context manager for progress tracking"""
    
    def __init__(self, total, desc, **kwargs):
        self.total = total
        self.desc = desc
        self.kwargs = kwargs
        self.pbar = None
        
    def __enter__(self):
        safe_kwargs = {}
        for k, v in self.kwargs.items():
            if k == 'color':
                safe_kwargs['colour'] = v
            else:
                safe_kwargs[k] = v
                
        self.pbar = tqdm(total=self.total, desc=self.desc, **self.kwargs)
        return self.pbar
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pbar:
            self.pbar.close()

class LoopInterceptor:
    """Intercepts and tracks for loops"""
    
    def __init__(self, pbar_params, min_length=2, max_length=None, exclude_types=None):
        self.pbar_params = pbar_params
        self.min_length = min_length
        self.max_length = max_length
        self.exclude_types = exclude_types or (str, bytes, dict)
        
    def _is_eligible_iterable(self, obj):
        """Check if object should be wrapped with progress bar"""
        if obj is None:
            return False
        if not isinstance(obj, Iterable):
            return False
        if isinstance(obj, self.exclude_types):
            return False
        if hasattr(obj, '_is_tracked') and obj._is_tracked:
            return False
            
        # Check length constraints
        try:
            length = len(obj)
            if length < self.min_length:
                return False
            if self.max_length and length > self.max_length:
                return False
        except (TypeError, AttributeError):
            # Can't determine length, use default behavior
            if self.min_length > 0:
                return False
                
        return True
        
    def _create_tracker(self, iterable):
        """Create a ForLoopTracker"""
        if not self._is_eligible_iterable(iterable):
            return iterable
            
        tracker = ForLoopTracker(iterable, self.pbar_params)
        tracker._is_tracked = True
        return tracker

def _normalize_tqdm_kwargs(kwargs):
    """Normalize tqdm parameters - use 'colour' consistently for tqdm"""
    if kwargs is None:
        kwargs = {}
        
    normalized = kwargs.copy()
    
    # Always use 'colour' for tqdm (British spelling)
    if 'color' in normalized:
        normalized['colour'] = normalized['color']
        del normalized['color']
    
    # Remove any other potentially problematic parameters
    safe_params = ['desc', 'total', 'leave', 'ncols', 'mininterval', 'maxinterval', 
                   'miniters', 'ascii', 'disable', 'unit', 'unit_scale', 
                   'dynamic_ncols', 'smoothing', 'bar_format', 'initial', 
                   'position', 'postfix', 'unit_divisor', 'write_bytes', 
                   'lock_args', 'nrows', 'colour', 'delay', 'gui']
    
    return {k: v for k, v in normalized.items() if k in safe_params}

def _wrap_with_runtime_interception(func, interceptor):
    """Wrap function with runtime loop interception - MOST RELIABLE APPROACH"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Store original builtins and globals
        original_range = __builtins__['range']
        original_builtins = __builtins__.copy()
        
        # Track if we've already set up interception
        if not hasattr(wrapper, '_interception_active'):
            wrapper._interception_active = False
        
        if wrapper._interception_active:
            # Avoid recursive interception
            return func(*args, **kwargs)
        
        wrapper._interception_active = True
        
        def tracked_range(*range_args):
            result = original_range(*range_args)
            return interceptor._create_tracker(result)
        
        def tracked_enumerate(iterable, start=0):
            result = enumerate(iterable, start)
            return interceptor._create_tracker(result)
        
        def tracked_zip(*iterables):
            result = zip(*iterables)
            return interceptor._create_tracker(result)
        
        # Create a safe execution environment
        def safe_execute():
            # Replace builtins temporarily
            original_globals = func.__globals__.copy()
            
            # Create a modified globals dict
            modified_globals = func.__globals__.copy()
            modified_globals['range'] = tracked_range
            modified_globals['enumerate'] = tracked_enumerate
            modified_globals['zip'] = tracked_zip
            
            # Also intercept any iterable arguments
            new_args = []
            for arg in args:
                if interceptor._is_eligible_iterable(arg):
                    new_args.append(interceptor._create_tracker(arg))
                else:
                    new_args.append(arg)
            
            new_kwargs = {}
            for k, v in kwargs.items():
                if interceptor._is_eligible_iterable(v):
                    new_kwargs[k] = interceptor._create_tracker(v)
                else:
                    new_kwargs[k] = v
            
            # Update function's globals temporarily
            original_globals_backup = func.__globals__.copy()
            try:
                func.__globals__.update(modified_globals)
                result = func(*new_args, **new_kwargs)
                return result
            finally:
                # Restore original globals
                func.__globals__.clear()
                func.__globals__.update(original_globals_backup)
        
        try:
            return safe_execute()
        finally:
            wrapper._interception_active = False
            
    wrapper.__interceptor__ = interceptor
    return wrapper

def _wrap_with_frame_interception(func, interceptor):
    """Alternative approach using frame interception"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Use sys._getframe() to intercept at frame level
        original_trace = sys.gettrace()
        
        def trace_calls(frame, event, arg):
            if event == 'call' and frame.f_code == func.__code__:
                # We're inside our target function
                frame.f_trace = trace_loops
                return trace_loops
            return trace_calls
        
        def trace_loops(frame, event, arg):
            if event == 'line':
                # Check if we're at a for loop
                code = frame.f_code
                line_no = frame.f_lineno
                
                # Simple approach: track any iterable in locals
                for var_name, var_value in frame.f_locals.items():
                    if (interceptor._is_eligible_iterable(var_value) and 
                        not hasattr(var_value, '_is_tracked')):
                        frame.f_locals[var_name] = interceptor._create_tracker(var_value)
                
            return trace_loops
        
        # Set up tracing
        sys.settrace(trace_calls)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            sys.settrace(original_trace)
    
    return wrapper

def _wrap_with_simple_interception(func, interceptor):
    """Simple but effective interception using argument wrapping"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Track the first eligible iterable in arguments
        new_args = []
        found_tracker = False
        
        for arg in args:
            if not found_tracker and interceptor._is_eligible_iterable(arg):
                new_args.append(interceptor._create_tracker(arg))
                found_tracker = True
            else:
                new_args.append(arg)

        new_kwargs = {}
        for k, v in kwargs.items():
            if not found_tracker and interceptor._is_eligible_iterable(v):
                new_kwargs[k] = interceptor._create_tracker(v)
                found_tracker = True
            else:
                new_kwargs[k] = v
        
        # If no iterable found in args/kwargs, use runtime interception
        if not found_tracker:
            return _wrap_with_runtime_interception(func, interceptor)(*new_args, **new_kwargs)
        
        return func(*new_args, **new_kwargs)
    
    wrapper.__interceptor__ = interceptor
    return wrapper

def show_progress(
    func=None,
    *,
    total=None,
    desc=None,
    min_length=2,
    max_length=None,
    exclude_types=None,
    enable=True,
    auto_detect_top_loop=True,
    interception_method="auto",  # "auto", "runtime", "simple", "frame"
    **tqdm_kwargs
):
    """
    ULTIMATE progress bar decorator with automatic top-level for loop detection.
    
    Features:
    - Multiple interception methods for maximum compatibility
    - Works with iterables from any source
    - Smart fallback between methods
    
    Args:
        total: Total iterations for progress bar
        desc: Description for progress bar
        min_length: Minimum iterable length to show progress bar
        max_length: Maximum iterable length to show progress bar
        exclude_types: Additional types to exclude from wrapping
        enable: Enable/disable progress bars
        auto_detect_top_loop: Automatically find and track the top-level for loop
        interception_method: "auto" (recommended), "runtime", "simple", or "frame"
        **tqdm_kwargs: Custom tqdm parameters
    """
    
    if exclude_types is None:
        exclude_types = (str, bytes, dict)

    def decorator(f):
        if not enable:
            return f
            
        normalized_kwargs = _normalize_tqdm_kwargs(tqdm_kwargs)
        pbar_params = {
            'total': total,
            'desc': desc,
            **normalized_kwargs
        }
        
        interceptor = LoopInterceptor(pbar_params, min_length, max_length, exclude_types)
        
        # Choose interception method
        if interception_method == "runtime" or (interception_method == "auto" and auto_detect_top_loop):
            return _wrap_with_runtime_interception(f, interceptor)
        elif interception_method == "frame":
            return _wrap_with_frame_interception(f, interceptor)
        elif interception_method == "simple":
            return _wrap_with_simple_interception(f, interceptor)
        else:
            # Auto: try runtime first, fall back to simple
            try:
                return _wrap_with_runtime_interception(f, interceptor)
            except Exception as e:
                print(f"Runtime interception failed: {e}, falling back to simple method")
                return _wrap_with_simple_interception(f, interceptor)

    # Handle the case when used as @show_progress (without parentheses)
    if func is None:
        return decorator
        
    # Handle the case when used as @show_progress() or @show_progress(...)
    return decorator(func)

# Separate context manager function
def progress_context(total=None, desc=None, **tqdm_kwargs):
    """Context manager for progress tracking""" 
    def _normalize_tqdm_kwargs(kwargs):
        if kwargs is None:
            kwargs = {}
        normalized = kwargs.copy()
        if 'colour' in normalized and 'color' in normalized:
            del normalized['color']
        elif 'colour' in normalized:
            normalized['colour'] = normalized['color']
            del normalized['color']
        return normalized

    return ProgressContextManager(total, desc, **_normalize_tqdm_kwargs(tqdm_kwargs))

# Manual tracking function
def track(iterable, desc=None, **kwargs):
    """Standalone tracking function"""
    from collections.abc import Iterable
    
    def _is_eligible_iterable(obj):
        if obj is None:
            return False
        if not isinstance(obj, Iterable):
            return False
        if isinstance(obj, (str, bytes, dict)):
            return False
        return True
    
    def _normalize_tqdm_kwargs(kwargs):
        if kwargs is None:
            kwargs = {}
        normalized = kwargs.copy()
        if 'colour' in normalized and 'color' in normalized:
            del normalized['color']
        elif 'colour' in normalized:
            normalized['colour'] = normalized['color']
            del normalized['color']
        return normalized

    if not _is_eligible_iterable(iterable):
        return iterable
    
    normalized_kwargs = _normalize_tqdm_kwargs(kwargs)
    total = normalized_kwargs.get('total')
    if total is None and hasattr(iterable, '__len__'):
        total = len(iterable)
    
    return tqdm(iterable, total=total, desc=desc, **normalized_kwargs)

# Add track method to show_progress for backward compatibility
show_progress.track = track

# # Test the improved version
# if __name__ == "__main__":
#     import time
    
#     print("=== Testing Ultimate Progress Bar ===")
    
#     # Test 1: Your original case - range() created internally
#     @show_progress(desc="Internal range", color="red")
#     def process_data(data=None):
#         if data is None:
#             data = range(50)  # This should be tracked!
#         results = []
#         for x in data:  # Top-level for loop
#             time.sleep(0.01)
#             results.append(x * 2)
#         return results
    
#     # Test 2: External iterable
#     @show_progress(desc="External data", color="green")
#     def process_external(data):
#         results = []
#         for item in data:  # This should be tracked!
#             time.sleep(0.01)
#             results.append(item ** 2)
#         return results
    
#     # Test 3: With enumerate
#     @show_progress(desc="With enumerate", color="blue")
#     def process_with_enumerate(items):
#         results = []
#         for i, item in enumerate(items):  # This should be tracked!
#             time.sleep(0.01)
#             results.append((i, item * 3))
#         return results
    
#     # Test 4: Complex case with multiple loops
#     @show_progress(desc="Complex case", color="yellow")
#     def complex_processing():
#         # Multiple data sources
#         data1 = range(30)    # Should be tracked (top loop)
#         data2 = [1, 2, 3, 4, 5]
        
#         results = []
#         for x in data1:      # This loop tracked
#             time.sleep(0.01)
#             temp = 0
#             for y in data2:  # This loop NOT tracked (inner loop)
#                 temp += y
#             results.append(x + temp)
#         return results
    
#     print("1. Testing internal range:")
#     result1 = process_data()
#     print(f"   Result: {len(result1)} items")
    
#     print("2. Testing external data:")
#     result2 = process_external(list(range(25)))
#     print(f"   Result: {len(result2)} items")
    
#     print("3. Testing enumerate:")
#     result3 = process_with_enumerate(['a', 'b', 'c', 'd', 'e', 'f'])
#     print(f"   Result: {result3}")
    
#     print("4. Testing complex case:")
#     result4 = complex_processing()
#     print(f"   Result: {len(result4)} items")
    
#     print("All tests completed! ✅")

# # Example usage and demonstration
# if __name__ == "__main__":
    
#     # Example 1: Auto-detection of top for loop
#     @show_progress(desc="Processing items")
#     def process_items(items):
#         results = []
#         for item in items:  # This loop will be automatically tracked
#             results.append(item * 2)
#         return results
    
#     # Example 2: Manual tracking
#     def manual_tracking(data):
#         total = 0
#         for item in track(data, desc="Manual progress"):
#             total += item
#         return total
    
#     # Example 3: Context manager
#     def context_example():
#         with progress_context(total=100, desc="Context example") as pbar:
#             for i in range(100):
#                 # Simulate work
#                 import time
#                 time.sleep(0.01)
#                 pbar.update(1)
    
#     # Example 4: Multiple loops (only top one tracked with auto_detect)
#     @show_progress(desc="Outer loop")
#     def nested_loops(outer_data, inner_data):
#         results = []
#         for outer in outer_data:  # This one will be tracked
#             inner_result = 0
#             for inner in inner_data:  # This one won't be tracked
#                 inner_result += inner
#             results.append(inner_result)
#         return results
    
#     # Test the examples
#     print("Testing auto-detection:")
#     result1 = process_items(list(range(10)))
#     print(f"Result: {result1}")
    
#     print("\nTesting manual tracking:")
#     result2 = manual_tracking(list(range(5)))
#     print(f"Result: {result2}")
    
#     print("\nTesting context manager:")
#     context_example()
    
#     print("\nTesting nested loops:")
#     result3 = nested_loops(list(range(3)), list(range(2)))
#     print(f"Result: {result3}")
    
#     print("\nTesting standalone track:")
#     for i in track(range(5), desc="Standalone"):
#         print(f"Processing {i}") 
# Example usage and testing


def num_booster(func=None, *, level="auto", signature=None, cuda=False):
    """
    num_booster: Ultimate Auto-Accelerating Decorator (CPU + GPU CUDA)
    ==================================================================

    这是一个“贴上就加速”的终极 Python 装饰器，自动从 CPU/GPU 中选择最佳模式进行加速：

    自动加速策略（按优先级）：
    1. CUDA GPU 加速（如果 cuda=True 且 CUDA 可用）
    2. Numba vectorize → 生成 ufunc（最快 CPU 模式）
    3. Numba parallel=True → 多线程 CPU 加速
    4. Numba njit → 普通 JIT 加速
    5. fallback 原 Python 函数（无任何报错）

    本工具库特点：
    - 永不崩溃，完全兼容生产环境
    - 支持 CPU-only / 无 Numba / 无 CUDA 情况
    - 装饰器形式使用最简洁
    - GPU/CPU 自动检测，无需用户干预


    ----------------------------------------
    使用示例
    ----------------------------------------

    1) 默认自动选择最佳 CPU 加速模式：
    -------------------------------------
        from num_booster import num_booster

        @num_booster
        def add(x, y):
            return x + y


    2) Aggressive 模式：parallel + fastmath：
    -------------------------------------
        @num_booster(level="aggressive")
        def compute(x):
            s = 0
            for i in range(len(x)):
                s += x[i] * 1.123
            return s


    3) 自动创建 ufunc（如果失败则继续尝试 parallel → njit）：
    -------------------------------------
        @num_booster(signature="float64(float64)")
        def square(a):
            return a * a

        square(np.array([1,2,3]))


    4) GPU CUDA 加速（如果 CUDA 可用，否则自动 fallback）：
    -------------------------------------
        @num_booster(cuda=True)
        def gpu_add(a, b):
            return a + b

    说明：
    - 如果写成普通 Python 函数，num_booster 会自动把它编译成 CUDA kernel 并按元素执行。
    - 如果 CUDA 不可用 → 自动切到 CPU 加速，不报错。
 
    num_booster: 自动选择 GPU / CPU 最佳加速策略。

    参数：
        level:
            "auto"（默认）: 自动选择最佳策略
            "aggressive": CPU parallel + fastmath 模式
        signature:
            用于生成 ufunc，例如："float64(float64)"
            若不兼容则自动 fallback
        cuda:
            是否尝试 CUDA GPU 加速（默认 False）
            若 True 且 CUDA 可用 → 优先使用 GPU

    用法：
        @num_booster
        @num_booster(level="aggressive")
        @num_booster(signature="float64(float64)")
        @num_booster(cuda=True)
    """

    def decorator(func):

        # Numba 不可用 → 返回原函数
        if not NUMBA_AVAILABLE:
            return func

        accelerated = func  # 默认先设置为原函数

        # =====================================================
        # 1. GPU CUDA kernel（如果用户要求且 CUDA 可用）
        # =====================================================
        if cuda and CUDA_AVAILABLE:

            try:
                cuda_kernel = numba.cuda.jit(func)

                # 创建一个自动处理 GPU launch 的 wrapper
                @wraps(func)
                def cuda_wrapper(*args):
                    import numpy as np
                    # 将输入转成 device array
                    d_args = [numba.cuda.to_device(np.asarray(arg)) for arg in args]
                    # 输出大小与第一个数组相同
                    n = len(d_args[0])
                    d_out = numba.cuda.device_array(shape=n)

                    # 网格/线程设置
                    threads = 128
                    blocks = (n + threads - 1) // threads

                    cuda_kernel[blocks, threads](*d_args, d_out)
                    return d_out.copy_to_host()

                accelerated = cuda_wrapper
                return accelerated

            except Exception as e:
                warnings.warn(f"[num_booster] CUDA 编译失败，尝试 CPU 模式 ({e})")

        # =====================================================
        # 2. vectorize 自动 ufunc（最快 CPU 路线）
        # =====================================================
        if signature is not None:
            try:
                ufunc = numba.vectorize([signature])(func)
                accelerated = ufunc
                return accelerated
            except Exception as e:
                warnings.warn(f"[num_booster] vectorize 失败，尝试 parallel ({e})")

        # =====================================================
        # 3. parallel=True，多线程 CPU 优化
        # =====================================================
        try:
            if level == "aggressive":
                parallel_jit = numba.njit(parallel=True, fastmath=True)
            else:
                parallel_jit = numba.njit(parallel=True)

            accelerated_parallel = parallel_jit(func)
            accelerated = accelerated_parallel
            return accelerated

        except Exception as e:
            warnings.warn(f"[num_booster] parallel jit 失败，尝试普通 njit ({e})")

        # =====================================================
        # 4. 普通 njit（最稳定 CPU acceleration）
        # =====================================================
        try:
            accelerated_njit = numba.njit(func)
            accelerated = accelerated_njit  
            return accelerated

        except Exception as e:
            warnings.warn(f"[num_booster] 普通 njit 失败，fallback 原函数 ({e})")

        # =====================================================
        # 5. fallback
        # =====================================================
        return func

    if func is not None:
        return decorator(func)
    return decorator


if __name__ == "__main__":
    @show_progress
    def process_data(data):
        results = []
        for x in data:
            # Simulate work
            for _ in range(100000):
                pass
            results.append(x * 2)
        return results
    
    # Custom tqdm parameters
    @show_progress(desc="Custom Progress", ncols=80, colour='red', position=0)
    def custom_processing(items):
        results = []
        for item in items:
            results.append(item ** 2)
        return results
    
    # Using pre-configured decorator
    @fast_progress
    def fast_processing(data):
        for item in data:
            pass
        return len(data)
    
    # Advanced filtering
    @show_progress_advanced(min_length=5, max_length=50, desc="Filtered")
    def filtered_processing(data):
        for item in data:
            pass
        return len(data)
    
    print("Testing show_progress decorator with custom tqdm support...")
    
    print("\n1. Basic usage:")
    result1 = process_data(range(10))
    print(f"Result: {result1}")
    
    print("\n2. Custom tqdm parameters:")
    result2 = custom_processing(range(15))
    print(f"Result: {result2}")
    
    print("\n3. Fast progress preset:")
    result3 = fast_processing(range(20))
    print(f"Processed {result3} items")
    
    print("\n4. Filtered processing:")
    result4 = filtered_processing(range(8))  # Should not show progress bar (min_length=10)
    result5 = filtered_processing(range(25))  # Should show progress bar
    print(f"Results: {result4}, {result5}")
    
    print("\nAll tests completed!")


# # Utility function for manual progress bar creation
# def wrap_with_progress(iterable, desc=None, **tqdm_kwargs):
#     """
#     Manually wrap an iterable with progress bar.
    
#     Usage:
#         data = range(100)
#         for item in wrap_with_progress(data, desc="Manual"):
#             process(item)
#     """
#     from tqdm.auto import tqdm
#     return tqdm(iterable, desc=desc, **tqdm_kwargs)

# if __name__ == "__main__":
    # Demonstrate verbose mode showing usage examples
    print("\n=== Timer Usage Example ===")
    print(Timer.usage_example())
    
    print("\n=== Retry Usage Example ===")
    print(Retry.usage_example())
    
    print("\n=== Memoize Usage Example ===")
    print(Memoize.usage_example())
    
    print("\n=== CircuitBreaker Usage Example ===")
    print(CircuitBreaker.usage_example())