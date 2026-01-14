"""뉴스/공지 관련 엔드포인트."""

from typing import List, Optional
from pyloa.endpoints.base import BaseEndpoint
from pyloa.models.news import NoticeList, Event, OpenAPIUserAlarm


class NewsEndpoint(BaseEndpoint):
    """뉴스/공지 endpoint."""

    def __init__(self, client):
        """NewsEndpoint를 초기화합니다.

        Args:
            client: LostArkAPI 인스턴스
        """
        super().__init__(client)
        self.base_path = "/news"

    def get_notices(
        self, searchText: Optional[str] = None, type: Optional[str] = None
    ) -> List[NoticeList]:
        """공지사항 목록 조회.

        Args:
            searchText: 제목 검색 키워드 (선택 사항)
            type: 공지 타입 - 공지/점검/상점/이벤트 (선택 사항)

        Returns:
            List[NoticeList]: 공지사항 정보 객체 리스트
        """
        params = {}
        if searchText is not None:
            params["searchText"] = searchText
        if type is not None:
            params["type"] = type

        data = self._request("GET", "/notices", params=params)
        return [NoticeList.from_dict(item) for item in data]

    def get_events(self) -> List[Event]:
        """진행 중인 이벤트 목록 조회.

        Returns:
            List[Event]: 이벤트 정보 객체 리스트
        """
        data = self._request("GET", "/events")
        return [Event.from_dict(item) for item in data]

    def get_alarms(self) -> OpenAPIUserAlarm:
        """알람 목록 조회.

        Returns:
            OpenAPIUserAlarm: 유저 알람 정보 객체
        """

        data = self._request("GET", "/alarms")
        return OpenAPIUserAlarm.from_dict(data)
