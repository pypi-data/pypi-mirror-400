"""거래소 관련 모델."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pyloa.models.base import BaseModel


@dataclass
class CategoryItem(BaseModel):
    """카테고리 아이템 모델."""

    code: int
    code_name: str


@dataclass
class Category(BaseModel):
    """카테고리 모델."""

    code: int
    code_name: str
    subs: List[CategoryItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        """딕셔너리에서 객체 생성."""
        code = data.get("Code", 0)
        code_name = data.get("CodeName", "")
        subs = []
        if "Subs" in data and data["Subs"]:
            for item in data["Subs"]:
                subs.append(CategoryItem.from_dict(item))
        return cls(code=code, code_name=code_name, subs=subs)


@dataclass
class MarketItem(BaseModel):
    """거래소 아이템 정보 모델."""

    id: int
    name: str
    grade: str
    icon: str
    bundle_count: int
    trade_remain_count: Optional[int] = None
    y_day_avg_price: Optional[float] = None
    recent_price: Optional[int] = None
    current_min_price: Optional[int] = None


@dataclass
class TradeMarketItem(BaseModel):
    """거래 내역 아이템 모델."""

    id: int
    name: str
    grade: str
    icon: str
    bundle_count: int
    trade_remain_count: Optional[int] = None
    y_day_avg_price: Optional[float] = None
    recent_price: Optional[int] = None


@dataclass
class MarketStatsInfo(BaseModel):
    """거래소 통계 정보 모델."""

    date: str
    avg_price: float
    trade_count: int


@dataclass
class MarketItemStats(BaseModel):
    """거래소 아이템 상세 통계 모델."""

    name: str
    bundle_count: int
    stats: List[MarketStatsInfo] = field(default_factory=list)
    trade_remain_count: Optional[int] = None
    tooltip: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketItemStats":
        """딕셔너리에서 객체 생성."""
        stats = []
        if "Stats" in data and data["Stats"]:
            for item in data["Stats"]:
                stats.append(MarketStatsInfo.from_dict(item))
        return cls(
            name=data.get("Name", ""),
            bundle_count=data.get("BundleCount", 0),
            trade_remain_count=data.get("TradeRemainCount"),
            stats=stats,
            tooltip=data.get("ToolTip"),
        )


@dataclass
class Market(BaseModel):
    """거래소 검색 결과 모델."""

    page_no: int
    page_size: int
    total_count: int
    items: List[MarketItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Market":
        """딕셔너리에서 객체 생성."""
        items = []
        if "Items" in data and data["Items"]:
            for item_data in data["Items"]:
                items.append(MarketItem.from_dict(item_data))

        return cls(
            page_no=data.get("PageNo", 1),
            page_size=data.get("PageSize", 10),
            total_count=data.get("TotalCount", 0),
            items=items,
        )


@dataclass
class TradeMarket(BaseModel):
    """거래소 최근 거래 내역 결과 모델."""

    page_no: int
    page_size: int
    total_count: int
    items: List[TradeMarketItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeMarket":
        """딕셔너리에서 객체 생성."""
        items = []
        if "Items" in data and data["Items"]:
            for item_data in data["Items"]:
                items.append(TradeMarketItem.from_dict(item_data))

        return cls(
            page_no=data.get("PageNo", 1),
            page_size=data.get("PageSize", 10),
            total_count=data.get("TotalCount", 0),
            items=items,
        )
