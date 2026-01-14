"""게임 콘텐츠 모델 (캘린더 등)."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pyloa.models.base import BaseModel


@dataclass
class RewardItem(BaseModel):
    """컨텐츠 보상 아이템 모델."""

    name: str
    icon: str
    grade: str
    start_times: Optional[List[str]] = None


@dataclass
class LevelRewardItems(BaseModel):
    """레벨별 보상 아이템 그룹 모델."""

    item_level: int
    items: List[RewardItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LevelRewardItems":
        """딕셔너리에서 객체 생성."""
        item_level = data.get("ItemLevel", 0)
        items = []
        if "Items" in data and data["Items"]:
            for item_data in data["Items"]:
                items.append(RewardItem.from_dict(item_data))
        return cls(item_level=item_level, items=items)


@dataclass
class ContentsCalendar(BaseModel):
    """게임 컨텐츠 캘린더 모델."""

    category_name: str
    contents_name: str
    contents_icon: str
    min_item_level: int
    start_times: List[str] = field(default_factory=list)
    location: Optional[str] = None
    reward_items: List[LevelRewardItems] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentsCalendar":
        """딕셔너리에서 객체 생성 (중첩 객체 처리)."""
        category_name = data.get("CategoryName", "")
        contents_name = data.get("ContentsName", "")
        contents_icon = data.get("ContentsIcon", "")
        min_item_level = data.get("MinItemLevel", 0)
        start_times = data.get("StartTimes", []) or []
        location = data.get("Location")

        reward_items = []
        if "RewardItems" in data and data["RewardItems"]:
            for item in data["RewardItems"]:
                reward_items.append(LevelRewardItems.from_dict(item))

        return cls(
            category_name=category_name,
            contents_name=contents_name,
            contents_icon=contents_icon,
            min_item_level=min_item_level,
            start_times=start_times,
            location=location,
            reward_items=reward_items,
        )

    def to_dict(self) -> Dict[str, Any]:
        """객체를 딕셔너리로 변환 (중첩 객체 처리)."""
        return {
            "category_name": self.category_name,
            "contents_name": self.contents_name,
            "contents_icon": self.contents_icon,
            "min_item_level": self.min_item_level,
            "start_times": self.start_times,
            "location": self.location,
            "reward_items": [
                {"item_level": ri.item_level, "items": [i.to_dict() for i in ri.items]}
                for ri in self.reward_items
            ],
        }
