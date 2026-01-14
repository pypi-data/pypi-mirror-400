import sys
import unittest
from src.pyruster import Result, Option


def create_some_result(v: int) -> Result[int]:
    if v == 0:
        return Result.Err("v is zero.")
    return Result.Ok(v)


class PyRustTest(unittest.TestCase):

    def setUp(self):
        print(f"python version: {sys.version}")

    @staticmethod
    def test_option():
        option_none = Option.None_()
        assert option_none.is_none()
        option_some = Option("some")
        assert option_some.is_some()

    @staticmethod
    def test_result():
        result_ok = Result.Ok("ok")
        assert result_ok.is_ok()
        assert result_ok.unwrap() == "ok"
        assert result_ok.ok().is_some()
        err_info = "err info"
        result_err = Result("err", err_info)
        assert result_err.is_err()
        assert result_err.unwrap_err() == err_info
        assert result_err.err().is_some()
        result_ok = create_some_result(v=2)
        assert result_ok.unwrap() == 2
        result_err = create_some_result(v=0)
        assert result_err.is_err()
        option_some = Option.Some("some")
        option_some_result = option_some.ok_or("is none")
        assert option_some_result.unwrap() == "some"


if __name__ == "__main__":
    unittest.main()
