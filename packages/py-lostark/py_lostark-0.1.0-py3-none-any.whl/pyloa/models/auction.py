"""경매장 관련 모델."""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from pyloa.models.base import BaseModel


@dataclass
class ItemOption(BaseModel):
    """경매장 아이템 옵션 모델."""

    type: str
    option_name: str
    option_name_tripod: Optional[str] = None
    value: Optional[float] = None
    is_penalty: bool = False
    class_name: Optional[str] = None
    is_value_percentage: bool = False


@dataclass
class AuctionInfo(BaseModel):
    """경매 정보 모델."""

    start_price: int
    end_date: str
    bid_count: int
    bid_start_price: int
    is_competitive: bool
    trade_allow_count: int
    buy_price: Optional[int] = None
    bid_price: Optional[int] = None
    upgrade_level: Optional[int] = None


@dataclass
class AuctionItem(BaseModel):
    """경매장 아이템 모델."""

    name: str
    grade: str
    tier: int
    icon: str
    auction_info: AuctionInfo
    options: List[ItemOption] = field(default_factory=list)
    level: Optional[int] = None
    grade_quality: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuctionItem":
        """딕셔너리에서 객체 생성 (중첩 객체 처리)."""
        auction_info_data = data.get("AuctionInfo")
        auction_info = (
            AuctionInfo.from_dict(auction_info_data) if auction_info_data else None
        )

        options = []
        if "Options" in data and data["Options"]:
            for opt_data in data["Options"]:
                options.append(ItemOption.from_dict(opt_data))

        # API 응답 필드 매핑
        return cls(
            name=data.get("Name", ""),
            grade=data.get("Grade", ""),
            tier=data.get("Tier", 0),
            level=data.get("Level"),
            icon=data.get("Icon", ""),
            grade_quality=data.get("GradeQuality"),
            auction_info=auction_info,
            options=options,
        )

    def to_dict(self) -> Dict[str, Any]:
        """객체를 딕셔너리로 변환 (중첩 객체 처리)."""
        return {
            "name": self.name,
            "grade": self.grade,
            "tier": self.tier,
            "level": self.level,
            "icon": self.icon,
            "grade_quality": self.grade_quality,
            "auction_info": self.auction_info.to_dict() if self.auction_info else None,
            "options": [opt.to_dict() for opt in self.options],
        }


@dataclass
class Auction(BaseModel):
    """경매장 검색 결과 모델."""

    page_no: int
    page_size: int
    total_count: int
    items: List[AuctionItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Auction":
        """딕셔너리에서 객체 생성."""
        items = []
        if "Items" in data and data["Items"]:
            for item_data in data["Items"]:
                items.append(AuctionItem.from_dict(item_data))

        return cls(
            page_no=data.get("PageNo", 1),
            page_size=data.get("PageSize", 10),
            total_count=data.get("TotalCount", 0),
            items=items,
        )
