"""캐릭터 관련 모델."""

from dataclasses import dataclass
from pyloa.models.base import BaseModel


@dataclass
class CharacterInfo(BaseModel):
    """캐릭터 기본 정보 모델."""

    server_name: str
    character_name: str
    character_level: int
    character_class_name: str
    item_avg_level: str
