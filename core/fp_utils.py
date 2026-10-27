from typing import Callable, Any, TypeVar, Generic, Union
import functools

T = TypeVar('T')
E = TypeVar('E')

# --- 1. HANDLING SIDE EFFECTS (Result Monad: Success / Failure) ---
class Result(Generic[T, E]):
    """
    FP Concept: Monad / Either pattern to encapsulate side-effectful I/O operations
    (like reading audio metadata or loading files) without throwing unhandled exceptions.
    """
    def __init__(self, value: Union[T, Exception], is_success: bool):
        self._value = value
        self._is_success = is_success

    @staticmethod
    def success(value: T) -> "Result[T, Any]":
        return Result(value, True)

    @staticmethod
    def failure(error: Exception) -> "Result[Any, Exception]":
        return Result(error, False)

    def is_ok(self) -> bool:
        return self._is_success

    def unwrap(self) -> T:
        if not self._is_success:
            raise self._value  # type: ignore
        return self._value  # type: ignore

    def map(self, fn: Callable[[T], Any]) -> "Result":
        """Applies transformation if successful, propagates error if failed."""
        if self._is_success:
            try:
                return Result.success(fn(self._value))  # type: ignore
            except Exception as ex:
                return Result.failure(ex)
        return self


def safe_io(fn: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """Decorator to convert risky I/O functions into pure Result monad returns."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs) -> Result[T, Exception]:
        try:
            return Result.success(fn(*args, **kwargs))
        except Exception as e:
            return Result.failure(e)
    return wrapper


# --- 2. FUNCTION COMPOSITION ---
def compose(*functions: Callable) -> Callable:
    """
    FP Concept: Function Composition pipeline.
    Combines functions right-to-left: compose(f, g)(x) == f(g(x))
    """
    return functools.reduce(lambda f, g: lambda x: f(g(x)), reversed(functions))


def pipe(value: Any, *functions: Callable) -> Any:
    """Passes a value through a sequence of functions left-to-right."""
    return functools.reduce(lambda acc, fn: fn(acc), functions, value)


# --- 3. CURRYING & PARTIAL APPLICATION ---
def partial_filter(predicate_builder: Callable[..., Callable[[Any], bool]], *args):
    """
    FP Concept: Partial Application / Currying helper.
    Pre-applies search parameters to generate filtering predicate functions.
    """
    return functools.partial(predicate_builder, *args)