"""pyLoa 라이브러리를 위한 사용자 정의 예외."""


class PyLoaException(Exception):
    """pyLoa 라이브러리의 기본 예외 클래스."""

    pass


class APIError(PyLoaException):
    """일반적인 API 오류."""

    pass


class RateLimitError(PyLoaException):
    """API 요청 속도 제한 초과 오류."""

    pass


class AuthenticationError(PyLoaException):
    """인증 오류 (401 Unauthorized)."""

    pass
