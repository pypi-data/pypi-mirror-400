"""API 요청 속도 제한기."""

from datetime import datetime
from typing import Dict, Optional


class RateLimiter:
    """응답 헤더를 기반으로 API 속도 제한을 관리합니다."""

    def __init__(self):
        """속도 제한기를 기본값으로 초기화합니다."""
        self.limit: int = 100  # 기본값: 분당 100회 요청
        self.remaining: int = 100
        self.reset_time: Optional[datetime] = None

    def get_wait_duration(self) -> float:
        """다음 요청 전 대기해야 할 시간을 반환합니다.

        Returns:
            float: 대기할 시간(초). 대기가 필요 없으면 0.0 반환.
        """
        if self.remaining <= 0 and self.reset_time:
            now = datetime.now()
            if now < self.reset_time:
                return (self.reset_time - now).total_seconds()
        return 0.0

    def update(self, headers: Dict[str, str]) -> None:
        """응답 헤더에서 속도 제한 정보를 업데이트합니다."""
        if "X-RateLimit-Limit" in headers:
            self.limit = int(headers["X-RateLimit-Limit"])
        if "X-RateLimit-Remaining" in headers:
            self.remaining = int(headers["X-RateLimit-Remaining"])
        if "X-RateLimit-Reset" in headers:
            reset_epoch = int(headers["X-RateLimit-Reset"])
            self.reset_time = datetime.fromtimestamp(reset_epoch)
