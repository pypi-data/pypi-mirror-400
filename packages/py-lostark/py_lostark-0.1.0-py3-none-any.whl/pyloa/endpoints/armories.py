"""Armories 관련 엔드포인트."""

from typing import List, Optional, Dict, Any
from pyloa.endpoints.base import BaseEndpoint
from pyloa.models.armory import (
    ArmoryProfile,
    ArmoryEquipment,
    ArmoryAvatar,
    ArmorySkill,
    ArmoryEngraving,
    ArmoryCard,
    ArmoryGem,
    ColosseumInfo,
    Collectible,
    ArkPassive,
)


class ArmoriesEndpoint(BaseEndpoint):
    """캐릭터 정보(Armories) endpoint."""

    def __init__(self, client):
        """ArmoriesEndpoint를 초기화합니다.

        Args:
            client: LostArkAPI 인스턴스
        """
        super().__init__(client)
        self.base_path = "/armories/characters"

    def get_profile(self, character_name: str) -> ArmoryProfile:
        """캐릭터 프로필 조회."""
        data = self._request("GET", f"/{character_name}/profiles")
        return ArmoryProfile.from_dict(data)

    def get_equipment(self, character_name: str) -> List[ArmoryEquipment]:
        """장비 정보 조회."""
        data = self._request("GET", f"/{character_name}/equipment")
        return [ArmoryEquipment.from_dict(item) for item in data]

    def get_avatars(self, character_name: str) -> List[ArmoryAvatar]:
        """아바타 정보 조회."""
        data = self._request("GET", f"/{character_name}/avatars")
        if not data:
            return []
        return [ArmoryAvatar.from_dict(item) for item in data]

    def get_combat_skills(self, character_name: str) -> List[ArmorySkill]:
        """전투 스킬 정보 조회."""
        data = self._request("GET", f"/{character_name}/combat-skills")
        if not data:
            return []
        return [ArmorySkill.from_dict(item) for item in data]

    def get_engravings(self, character_name: str) -> Optional[ArmoryEngraving]:
        """각인 정보 조회."""
        data = self._request("GET", f"/{character_name}/engravings")
        if not data:
            return None
        return ArmoryEngraving.from_dict(data)

    def get_cards(self, character_name: str) -> Optional[ArmoryCard]:
        """카드 정보 조회."""
        data = self._request("GET", f"/{character_name}/cards")
        if not data:
            return None
        return ArmoryCard.from_dict(data)

    def get_gems(self, character_name: str) -> Optional[ArmoryGem]:
        """보석 정보 조회."""
        data = self._request("GET", f"/{character_name}/gems")
        if not data:
            return None
        return ArmoryGem.from_dict(data)

    def get_colosseums(self, character_name: str) -> Optional[ColosseumInfo]:
        """투기장 정보 조회."""
        data = self._request("GET", f"/{character_name}/colosseums")
        if not data:
            return None
        return ColosseumInfo.from_dict(data)

    def get_collectibles(self, character_name: str) -> List[Collectible]:
        """수집품 정보 조회."""
        data = self._request("GET", f"/{character_name}/collectibles")
        if not data:
            return []
        return [Collectible.from_dict(item) for item in data]

    def get_ark_passive(self, character_name: str) -> Optional[ArkPassive]:
        """아크 패시브 정보 조회."""
        data = self._request("GET", f"/{character_name}/arkpassive")
        if not data:
            return None
        return ArkPassive.from_dict(data)

    def get_ark_grid(self, character_name: str) -> Optional["ArkGrid"]:
        """아크 그리드 정보 조회."""
        from pyloa.models.armory import ArkGrid

        data = self._request("GET", f"/{character_name}/arkgrid")
        if not data:
            return None
        return ArkGrid.from_dict(data)

    def get_total_info(
        self, character_name: str, filters: Optional[List[str]] = None
    ) -> Optional["ArmoryTotal"]:
        """Armory 종합 정보 조회.

        Args:
            character_name: 조회할 캐릭터 이름
            filters: 조회할 항목 리스트 (예: ['profiles', 'equipment'])
                     None이면 전체 조회
        """
        from pyloa.models.armory import ArmoryTotal

        params = {}
        if filters:
            # 로스트아크 API는 필터를 쉼표로 구분된 문자열로 받습니다.
            params["filters"] = ",".join(filters)

        data = self._request("GET", f"/{character_name}", params=params)
        if not data:
            return None
        return ArmoryTotal.from_dict(data)
