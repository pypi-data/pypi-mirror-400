"""RateLimiter 테스트."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from pyloa.rate_limiter import RateLimiter


def test_rate_limiter_initialization():
    """RateLimiter는 기본값으로 초기화되어야 합니다."""
    limiter = RateLimiter()
    assert limiter.limit == 100
    assert limiter.remaining == 100
    assert limiter.reset_time is None


def test_update_from_headers():
    """RateLimiter는 응답 헤더에서 업데이트되어야 합니다."""
    limiter = RateLimiter()

    # Simulate response headers
    future_time = datetime.now() + timedelta(seconds=60)
    headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "95",
        "X-RateLimit-Reset": str(int(future_time.timestamp())),
    }

    limiter.update(headers)

    assert limiter.limit == 100
    assert limiter.remaining == 95
    assert limiter.reset_time is not None


def test_get_wait_duration_returns_zero_when_remaining():
    """요청 잔여량이 있을 때 get_wait_duration은 0.0을 반환해야 합니다."""
    limiter = RateLimiter()
    limiter.remaining = 50
    limiter.reset_time = datetime.now() + timedelta(seconds=60)

    assert limiter.get_wait_duration() == 0.0


def test_get_wait_duration_returns_seconds_when_limited():
    """제한 초과 시 get_wait_duration은 남은 초를 반환해야 합니다."""
    limiter = RateLimiter()
    limiter.remaining = 0
    # Set reset time to 5 seconds in the future
    limiter.reset_time = datetime.now() + timedelta(seconds=5)

    duration = limiter.get_wait_duration()
    assert 4.0 < duration <= 5.0


def test_get_wait_duration_returns_zero_after_reset():
    """재설정 시간이 지났으면 get_wait_duration은 0.0을 반환해야 합니다."""
    limiter = RateLimiter()
    limiter.remaining = 0
    limiter.reset_time = datetime.now() - timedelta(seconds=10)  # Past time

    assert limiter.get_wait_duration() == 0.0


def test_get_wait_duration_returns_zero_without_reset_time():
    """reset_time이 설정되지 않은 경우 get_wait_duration은 0.0을 반환해야 합니다."""
    limiter = RateLimiter()
    limiter.remaining = 0
    limiter.reset_time = None

    assert limiter.get_wait_duration() == 0.0
