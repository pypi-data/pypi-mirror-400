from typing import Any, TypeVar, Generic, Optional, Callable, cast

E = TypeVar("E")
T = TypeVar("T")
U = TypeVar("U")
_E = TypeVar("_E")
_T = TypeVar("_T")



class Result(Generic[T, E]):

    def __init__(self, val: Optional[T] = None, err: Optional[E] = None):
        self.__val = val
        self.__err = err

    @staticmethod
    def Ok(val: _T) -> "Result[_T, Any]":
        return Result(val=val)

    @staticmethod
    def Err(err: _E) -> 'Result[Any, _E]':
        return Result(err=err)

    def is_ok(self) -> bool:
        return self.__err is None

    def is_ok_and(self, f: Callable[[T], bool]) -> bool:
        if self.is_ok():
            return f(cast(T, self.__val))
        else:
            return False

    def is_err(self) -> bool:
        return not self.is_ok()

    def is_err_and(self, f: Callable[[E], bool]) -> bool:
        if self.is_ok():
            return False
        return f(cast(E, self.__err))

    def ok(self):
        from .rust_option import Option
        if self.is_ok():
            return Option[T](val=cast(T, self.__val))
        else:
            return Option[T](val=None)

    def err(self):
        from .rust_option import Option
        if self.is_err():
            return Option[E](val=cast(E, self.__err))
        else:
            return Option[E](val=None)

    def map(self, op: Callable[[T], U]) -> 'Result[U, E]':
        if self.is_ok():
            return Result[U, E](val=op(cast(T, self.__val)))
        else:
            return Result[U, E](err=cast(E, self.__err))

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        if self.is_ok():
            return f(cast(T, self.__val))
        else:
            return default

    def map_or_else(self, default: Callable[[E], U], f: Callable[[T], U]) -> U:
        if self.is_ok():
            return f(cast(T, self.__val))
        else:
            return default(cast(E, self.__err))

    def map_err(self, op: Callable[[E], U]) -> 'Result[T, U]':
        if self.is_ok():
            return Result[T, U](val=cast(T, self.__val))
        else:
            return Result[T, U](err=op(cast(E, self.__err)))

    def inspect(self, f: Callable[[T], None]) -> 'Result[T, E]':
        if self.is_ok():
            f(cast(T, self.__val))
        return self

    def inspect_err(self, f: Callable[[E], None]) -> 'Result[T, E]':
        if self.is_err():
            f(cast(E, self.__err))
        return self

    def expect(self, msg: str) -> T:
        if self.is_ok():
            return cast(T, self.__val)
        else:
            raise ValueError(msg)

    def expect_err(self, msg: str) -> E:
        if self.is_err():
            return cast(E, self.__err)
        else:
            raise ValueError(msg)

    def unwrap(self) -> T:
        if self.is_ok():
            return cast(T, self.__val)
        else:
            raise ValueError(f"Result is Err: {str(self.__err)}")

    def unwrap_or(self, default: T) -> T:
        if self.is_ok():
            return cast(T, self.__val)
        else:
            return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        if self.is_ok():
            return cast(T, self.__val)
        else:
            return op(cast(E, self.__err))

    def unwrap_err(self) -> E:
        if self.is_err():
            return cast(E, self.__err)
        else:
            raise ValueError(f"Result is Ok: {str(self.__val)}")

    def and_(self, res: 'Result[U, E]') -> 'Result[U, E]':
        if self.is_ok():
            return res
        else:
            return Result[U, E](err=cast(E, self.__err))

    def and_then(self, op: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        if self.is_ok():
            return op(cast(T, self.__val))
        else:
            return Result[U, E](err=cast(E, self.__err))

    def or_(self, res: 'Result[T, E]') -> 'Result[T, E]':
        if self.is_ok():
            return Result[T, E](val=cast(T, self.__val))
        else:
            return res

    def or_else(self, op: Callable[[E], 'Result[T, E]']) -> 'Result[T, E]':
        if self.is_ok():
            return Result[T, E](val=cast(T, self.__val))
        else:
            return op(cast(E, self.__err))
