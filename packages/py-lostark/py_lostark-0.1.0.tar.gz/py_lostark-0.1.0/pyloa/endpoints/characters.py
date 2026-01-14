"""캐릭터 정보 관련 엔드포인트."""

from typing import List
from pyloa.endpoints.base import BaseEndpoint
from pyloa.models.character import CharacterInfo


class CharactersEndpoint(BaseEndpoint):
    """캐릭터 정보 endpoint."""

    def __init__(self, client):
        """CharactersEndpoint를 초기화합니다.

        Args:
            client: LostArkAPI 인스턴스
        """
        super().__init__(client)
        self.base_path = "/characters"

    def get_siblings(self, character_name: str) -> List[CharacterInfo]:
        """계정의 모든 캐릭터 목록 조회.

        Args:
            character_name: 조회할 캐릭터 이름

        Returns:
            List[CharacterInfo]: 캐릭터 정보 객체 리스트
        """

        data = self._request("GET", f"/{character_name}/siblings")
        return [CharacterInfo.from_dict(item) for item in data]
