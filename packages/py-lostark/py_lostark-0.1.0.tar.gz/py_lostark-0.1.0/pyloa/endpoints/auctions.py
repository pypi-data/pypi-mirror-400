"""경매장 관련 엔드포인트."""

from typing import Dict, Any
from pyloa.endpoints.base import BaseEndpoint
from pyloa.models.auction import Auction


class AuctionsEndpoint(BaseEndpoint):
    """경매장 endpoint."""

    def __init__(self, client):
        """AuctionsEndpoint를 초기화합니다.

        Args:
            client: LostArkAPI 인스턴스
        """
        super().__init__(client)
        self.base_path = "/auctions"

    def get_options(self) -> Dict[str, Any]:
        """경매장 검색 옵션 조회.

        Returns:
            Dict: 카테고리, 아이템 등급 등의 정보를 포함하는 딕셔너리
        """
        return self._request("GET", "/options")

    def get_items(self, **kwargs) -> Auction:
        """경매장 아이템 검색.

        Args:
            **kwargs: 검색 파라미터
                ItemLevelMin, ItemLevelMax, ItemGradeQuality,
                SkillOptions, EtcOptions, Sort, CategoryCode,
                CharacterClass, ItemTier, ItemGrade, ItemName,
                PageNo, SortCondition

        Returns:
            Auction: 경매장 검색 결과 객체
        """

        data = self._request("POST", "/items", json=kwargs)
        return Auction.from_dict(data)
