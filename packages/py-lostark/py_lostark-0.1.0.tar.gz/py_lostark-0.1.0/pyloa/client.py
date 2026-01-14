"""LostArkAPI 클라이언트."""

import requests
from pyloa.rate_limiter import RateLimiter


class LostArkAPI:
    """로스트아크 API를 위한 메인 클라이언트."""

    def __init__(self, api_key: str):
        """API 클라이언트를 초기화합니다.

        Args:
            api_key: 인증을 위한 JWT 토큰
        """
        self._api_key = api_key
        self.base_url = "https://developer-lostark.game.onstove.com"

        # 세션 및 헤더 생성
        self.session = requests.Session()
        self.session.headers.update(
            {"authorization": f"bearer {api_key}", "accept": "application/json"}
        )

        # 속도 제한기 초기화
        self.rate_limiter = RateLimiter()

    @property
    def api_key(self) -> str:
        """API 키를 반환합니다 (읽기 전용)."""
        return self._api_key

    @property
    def news(self):
        """News 엔드포인트에 접근합니다."""
        if not hasattr(self, "_news"):
            from pyloa.endpoints.news import NewsEndpoint

            self._news = NewsEndpoint(self)
        return self._news

    @property
    def characters(self):
        """Characters 엔드포인트에 접근합니다."""
        if not hasattr(self, "_characters"):
            from pyloa.endpoints.characters import CharactersEndpoint

            self._characters = CharactersEndpoint(self)
        return self._characters

    @property
    def markets(self):
        """Markets 엔드포인트에 접근합니다."""
        if not hasattr(self, "_markets"):
            from pyloa.endpoints.markets import MarketsEndpoint

            self._markets = MarketsEndpoint(self)
        return self._markets

    @property
    def auctions(self):
        """Auctions 엔드포인트에 접근합니다."""
        if not hasattr(self, "_auctions"):
            from pyloa.endpoints.auctions import AuctionsEndpoint

            self._auctions = AuctionsEndpoint(self)
        return self._auctions

    @property
    def game_contents(self):
        """Game Contents 엔드포인트에 접근합니다."""
        if not hasattr(self, "_game_contents"):
            from pyloa.endpoints.game_contents import GameContentsEndpoint

            self._game_contents = GameContentsEndpoint(self)
        return self._game_contents

    @property
    def armories(self):
        """Armories 엔드포인트에 접근합니다."""
        if not hasattr(self, "_armories"):
            from pyloa.endpoints.armories import ArmoriesEndpoint

            self._armories = ArmoriesEndpoint(self)
        return self._armories
