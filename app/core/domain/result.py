"""
Result monad for explicit error handling without exceptions.
"""

from dataclasses import dataclass
from typing import TypeVar, Generic, Union

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    is_ok: bool = True
    is_err: bool = False


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E
    message: str = ""
    is_ok: bool = False
    is_err: bool = True


Result = Union[Ok[T], Err[E]]