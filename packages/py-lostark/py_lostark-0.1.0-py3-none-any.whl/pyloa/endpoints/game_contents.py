"""게임 콘텐츠 관련 엔드포인트."""

from typing import List
from pyloa.endpoints.base import BaseEndpoint
from pyloa.models.game_content import ContentsCalendar


class GameContentsEndpoint(BaseEndpoint):
    """게임 컨텐츠 endpoint."""

    def __init__(self, client):
        """GameContentsEndpoint를 초기화합니다.

        Args:
            client: LostArkAPI 인스턴스
        """
        super().__init__(client)
        self.base_path = "/gamecontents"

    def get_calendar(self) -> List[ContentsCalendar]:
        """주간 캘린더 조회 (도전 가디언 등).

        Returns:
            List[ContentsCalendar]: 주간 캘린더 정보 객체 리스트
        """

        data = self._request("GET", "/calendar")
        return [ContentsCalendar.from_dict(item) for item in data]
