from typing import Any, TypeVar, Generic, Optional, Callable, cast

S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")
_T = TypeVar("_T")
_S = TypeVar("_S")



class Result(Generic[T, S]):

    def __init__(self, val: Optional[T] = None, err: Optional[S] = None):
        self.__val = val
        self.__err = err

    @staticmethod
    def Ok(val: _T) -> "Result[_T, Any]":
        return Result(val=val)

    @staticmethod
    def Err(err: _S) -> 'Result[Any, _S]':
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

    def is_err_and(self, f: Callable[[str], bool]) -> bool:
        if self.is_ok():
            return False
        return f(cast(str, self.__err))

    def ok(self):
        from .rust_option import Option
        if self.is_ok():
            return Option[T](val=cast(T, self.__val))
        else:
            return Option[T](val=None)

    def err(self):
        from .rust_option import Option
        if self.is_err():
            return Option[S](val=cast(S, self.__err))
        else:
            return Option[S](val=None)

    def map(self, op: Callable[[T], U]) -> 'Result[U, S]':
        if self.is_ok():
            return Result[U, S](val=op(cast(T, self.__val)))
        else:
            return Result[U, S](err=cast(S, self.__err))

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        if self.is_ok():
            return f(cast(T, self.__val))
        else:
            return default

    def map_or_else(self, default: Callable[[S], U], f: Callable[[T], U]) -> U:
        if self.is_ok():
            return f(cast(T, self.__val))
        else:
            return default(cast(S, self.__err))

    def map_err(self, op: Callable[[S], U]) -> 'Result[T, U]':
        if self.is_ok():
            return Result[T, U](val=cast(T, self.__val))
        else:
            return Result[T, U](err=op(cast(S, self.__err)))

    def inspect(self, f: Callable[[T], None]) -> 'Result[T, S]':
        if self.is_ok():
            f(cast(T, self.__val))
        return self

    def inspect_err(self, f: Callable[[S], None]) -> 'Result[T, S]':
        if self.is_err():
            f(cast(S, self.__err))
        return self

    def expect(self, msg: str) -> T:
        if self.is_ok():
            return cast(T, self.__val)
        else:
            raise ValueError(msg)

    def expect_err(self, msg: str) -> S:
        if self.is_err():
            return cast(S, self.__err)
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

    def unwrap_or_else(self, op: Callable[[str], T]) -> T:
        if self.is_ok():
            return cast(T, self.__val)
        else:
            return op(cast(str, self.__err))

    def unwrap_err(self) -> S:
        if self.is_err():
            return cast(S, self.__err)
        else:
            raise ValueError(f"Result is Ok: {str(self.__val)}")

    def and_(self, res: 'Result[U, S]') -> 'Result[U, S]':
        if self.is_ok():
            return res
        else:
            return Result[U, S](err=cast(S, self.__err))

    def and_then(self, op: Callable[[T], 'Result[U, S]']) -> 'Result[U, S]':
        if self.is_ok():
            return op(cast(T, self.__val))
        else:
            return Result[U, S](err=cast(S, self.__err))

    def or_(self, res: 'Result[T, S]') -> 'Result[T, S]':
        if self.is_ok():
            return Result[T, S](val=cast(T, self.__val))
        else:
            return res

    def or_else(self, op: Callable[[S], 'Result[T, S]']) -> 'Result[T, S]':
        if self.is_ok():
            return Result[T, S](val=cast(T, self.__val))
        else:
            return op(cast(S, self.__err))
