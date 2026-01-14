"""사용자 정의 예외 테스트."""

import pytest
from pyloa.exceptions import (
    PyLoaException,
    APIError,
    RateLimitError,
    AuthenticationError,
)


def test_pyloa_exception_is_exception():
    """PyLoaException은 Exception을 상속해야 합니다."""
    assert issubclass(PyLoaException, Exception)


def test_pyloa_exception_instantiation():
    """PyLoaException은 메시지와 함께 인스턴스화 가능해야 합니다."""
    exc = PyLoaException("Test error")
    assert str(exc) == "Test error"


def test_api_error_inheritance():
    """APIError는 PyLoaException을 상속해야 합니다."""
    assert issubclass(APIError, PyLoaException)


def test_rate_limit_error_inheritance():
    """RateLimitError는 PyLoaException을 상속해야 합니다."""
    assert issubclass(RateLimitError, PyLoaException)


def test_authentication_error_inheritance():
    """AuthenticationError는 PyLoaException을 상속해야 합니다."""
    assert issubclass(AuthenticationError, PyLoaException)


def test_exceptions_can_be_raised():
    """모든 사용자 정의 예외는 발생시킬 수 있어야 합니다."""
    with pytest.raises(PyLoaException):
        raise PyLoaException("base error")

    with pytest.raises(APIError):
        raise APIError("api error")

    with pytest.raises(RateLimitError):
        raise RateLimitError("rate limit error")

    with pytest.raises(AuthenticationError):
        raise AuthenticationError("auth error")
