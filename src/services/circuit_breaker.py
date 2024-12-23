import time
from enum import Enum
from functools import wraps
from typing import Callable, Any

from fastapi import HTTPException


class CircuitBreakerException(Exception):
    pass


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(
            self,
            failure_threshold: int = 3,
            recovery_timeout: int = 10
    ):
        """
        :param failure_threshold: кол-во подряд идущих неудач,
            после которых переключаемся в OPEN
        :param recovery_timeout: время (в секундах),
            через которое из OPEN переходим в HALF-OPEN
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Обёртка, которая вызывает `func(*args, **kwargs)`,
        но учитывает состояние Circuit Breaker.
        """
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerException(
                    "CircuitBreaker is OPEN. Rejecting call."
                )

        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            self._on_failure()
            raise e
        else:
            self._on_success()
            return result

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()

        if (self.state == CircuitBreakerState.CLOSED
                and self.failure_count >= self.failure_threshold):
            self.state = CircuitBreakerState.OPEN
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN

    def _on_success(self) -> None:
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0


def circuit_breaker(
        failure_threshold: int = 3,
        recovery_timeout: int = 120
) -> Callable:
    breakers = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if func not in breakers:
                breakers[func] = CircuitBreaker(
                    failure_threshold,
                    recovery_timeout
                )

            breaker = breakers[func]

            try:
                return await breaker.call(func, *args, **kwargs)
            except Exception:
                raise HTTPException(
                    status_code=503,
                    detail="The server was unable to complete your request. "
                           "Please try again later."
                )

        return wrapper

    return decorator
