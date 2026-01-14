"""모든 API 엔드포인트의 기본 클래스."""

import time
from typing import Dict, TYPE_CHECKING
from requests import HTTPError
from pyloa.exceptions import APIError, RateLimitError, AuthenticationError

if TYPE_CHECKING:
    from pyloa.client import LostArkAPI


class BaseEndpoint:
    """모든 API 엔드포인트의 기본 클래스."""

    def __init__(self, client: "LostArkAPI"):
        """클라이언트와 함께 엔드포인트를 초기화합니다.

        Args:
            client: LostArkAPI 인스턴스
        """
        self.client = client
        self.base_path = ""  # Subclasses should override

    def _request(self, method: str, path: str, **kwargs) -> Dict:
        """속도 제한 및 오류 처리를 포함하여 HTTP 요청을 수행합니다.

        Args:
            method: HTTP 메서드 (GET, POST 등)
            path: 엔드포인트 경로
            **kwargs: requests 요청을 위한 추가 인자

        Returns:
            Dict: JSON 응답 딕셔너리

        Raises:
            AuthenticationError: 401 Unauthorized 발생 시
            RateLimitError: 429 Too Many Requests 발생 시
            APIError: 기타 HTTP 오류 발생 시
        """
        # 속도 제한 초과 시 대기 (RateLimiter는 상태만 제공, 제어는 여기서)
        wait_duration = self.client.rate_limiter.get_wait_duration()
        if wait_duration > 0:
            time.sleep(wait_duration)

        # 전체 URL 생성
        url = f"{self.client.base_url}{self.base_path}{path}"

        # 요청 수행
        response = self.client.session.request(method, url, **kwargs)

        # 헤더에서 속도 제한 정보 업데이트
        self.client.rate_limiter.update(response.headers)

        # 오류 처리
        try:
            response.raise_for_status()
        except HTTPError:
            if response.status_code == 401:
                raise AuthenticationError(f"Unauthorized: {response.text}")
            elif response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {response.text}")
            else:
                raise APIError(f"API error ({response.status_code}): {response.text}")

        return response.json()
