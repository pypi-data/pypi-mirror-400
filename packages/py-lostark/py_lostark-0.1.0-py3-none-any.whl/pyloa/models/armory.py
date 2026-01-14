"""Armory 관련 모델."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pyloa.models.base import BaseModel


@dataclass
class Stat(BaseModel):
    """프로필 스탯 모델."""

    type: str
    value: str
    tooltip: List[str] = field(default_factory=list)


@dataclass
class Tendency(BaseModel):
    """성향 모델."""

    type: str
    point: int
    max_point: int


@dataclass
class Decoration(BaseModel):
    """장식 모델."""

    symbol: str
    emblems: List[str] = field(default_factory=list)


@dataclass
class ArmoryProfile(BaseModel):
    """캐릭터 프로필 모델."""

    server_name: str
    character_name: str
    character_level: int
    character_class_name: str
    item_avg_level: str
    character_image: Optional[str] = None
    expedition_level: int = 0
    town_level: Optional[int] = None
    town_name: Optional[str] = None
    title: Optional[str] = None
    guild_member_grade: Optional[str] = None
    guild_name: Optional[str] = None
    using_skill_point: int = 0
    total_skill_point: int = 0
    stats: List[Stat] = field(default_factory=list)
    tendencies: List[Tendency] = field(default_factory=list)
    combat_power: Optional[str] = None
    decorations: Optional[Decoration] = None
    honor_point: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmoryProfile":
        """딕셔너리에서 인스턴스를 생성합니다."""
        stats = [Stat.from_dict(s) for s in (data.get("Stats") or [])]
        tendencies = [Tendency.from_dict(t) for t in (data.get("Tendencies") or [])]
        decorations_data = data.get("Decorations")
        decorations = (
            Decoration.from_dict(decorations_data) if decorations_data else None
        )

        return cls(
            server_name=data.get("ServerName", ""),
            character_name=data.get("CharacterName", ""),
            character_level=data.get("CharacterLevel", 0),
            character_class_name=data.get("CharacterClassName", ""),
            item_avg_level=data.get("ItemAvgLevel", ""),
            character_image=data.get("CharacterImage"),
            expedition_level=data.get("ExpeditionLevel", 0),
            town_level=data.get("TownLevel"),
            town_name=data.get("TownName"),
            title=data.get("Title"),
            guild_member_grade=data.get("GuildMemberGrade"),
            guild_name=data.get("GuildName"),
            using_skill_point=data.get("UsingSkillPoint", 0),
            total_skill_point=data.get("TotalSkillPoint", 0),
            stats=stats,
            tendencies=tendencies,
            combat_power=data.get("CombatPower"),
            decorations=decorations,
            honor_point=data.get("HonorPoint"),
        )


@dataclass
class ArmoryEquipment(BaseModel):
    """장비 정보 모델."""

    type: str
    name: str
    icon: str
    grade: str
    tooltip: str


@dataclass
class ArmoryAvatar(BaseModel):
    """아바타 모델."""

    type: str
    name: str
    icon: str
    grade: str
    is_set: bool
    is_inner: bool
    tooltip: str


@dataclass
class SkillTripod(BaseModel):
    """스킬 트라이포드 모델."""

    tier: int
    slot: int
    name: str
    icon: str
    is_selected: bool
    tooltip: str


@dataclass
class SkillRune(BaseModel):
    """스킬 룬 모델."""

    name: str
    icon: str
    grade: str
    tooltip: str


@dataclass
class ArmorySkill(BaseModel):
    """스킬 모델."""

    name: str
    icon: str
    level: int
    type: str
    skill_type: int
    tooltip: str
    is_awake: bool = False
    tripods: List[SkillTripod] = field(default_factory=list)
    rune: Optional[SkillRune] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmorySkill":
        """딕셔너리에서 인스턴스를 생성합니다."""
        tripods = [SkillTripod.from_dict(t) for t in (data.get("Tripods") or [])]
        rune_data = data.get("Rune")
        rune = SkillRune.from_dict(rune_data) if rune_data else None
        return cls(
            name=data.get("Name", ""),
            icon=data.get("Icon", ""),
            level=data.get("Level", 0),
            type=data.get("Type", ""),
            skill_type=data.get("SkillType", 0),
            tooltip=data.get("Tooltip", ""),
            is_awake=data.get("IsAwake", False),
            tripods=tripods,
            rune=rune,
        )


@dataclass
class Engraving(BaseModel):
    """각인 슬롯 모델."""

    slot: int
    name: str
    icon: str
    tooltip: str


@dataclass
class EngravingEffect(BaseModel):
    """각인 효과 모델."""

    icon: str
    name: str
    description: str


@dataclass
class ArkPassiveEffect(BaseModel):
    """아크 패시브 효과 모델."""

    grade: str
    level: int
    name: str
    description: str
    ability_stone_level: Optional[int] = None


@dataclass
class ArmoryEngraving(BaseModel):
    """캐릭터 각인 정보 모델."""

    engravings: List[Engraving] = field(default_factory=list)
    effects: List[EngravingEffect] = field(default_factory=list)
    ark_passive_effects: List[ArkPassiveEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmoryEngraving":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            engravings=[Engraving.from_dict(e) for e in (data.get("Engravings") or [])],
            effects=[EngravingEffect.from_dict(e) for e in (data.get("Effects") or [])],
            ark_passive_effects=[
                ArkPassiveEffect.from_dict(e)
                for e in (data.get("ArkPassiveEffects") or [])
            ],
        )


@dataclass
class Card(BaseModel):
    """카드 단일 모델."""

    slot: int
    name: str
    icon: str
    awake_count: int
    awake_total: int
    grade: str
    tooltip: str


@dataclass
class Effect(BaseModel):
    """효과 상세 모델."""

    name: str
    description: str


@dataclass
class CardEffect(BaseModel):
    """카드 세트 효과 모델."""

    index: int
    card_slots: List[int] = field(default_factory=list)
    items: List[Effect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CardEffect":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            index=data.get("Index", 0),
            card_slots=(data.get("CardSlots") or []),
            items=[Effect.from_dict(i) for i in (data.get("Items") or [])],
        )


@dataclass
class ArmoryCard(BaseModel):
    """캐릭터 카드 정보 모델."""

    cards: List[Card] = field(default_factory=list)
    effects: List[CardEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmoryCard":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            cards=[Card.from_dict(c) for c in (data.get("Cards") or [])],
            effects=[CardEffect.from_dict(e) for e in (data.get("Effects") or [])],
        )


@dataclass
class Gem(BaseModel):
    """보석 단일 모델."""

    slot: int
    name: str
    icon: str
    level: int
    grade: str
    tooltip: str


@dataclass
class GemEffect(BaseModel):
    """보석 효과 상세 모델."""

    gem_slot: int
    name: str
    description: List[str] = field(default_factory=list)
    option: str = ""
    icon: str = ""
    tooltip: str = ""


@dataclass
class ArmoryGemEffect(BaseModel):
    """보석 효과 그룹 모델."""

    description: str
    skills: List[GemEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmoryGemEffect":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            description=data.get("Description", ""),
            skills=[GemEffect.from_dict(s) for s in (data.get("Skills") or [])],
        )


@dataclass
class ArmoryGem(BaseModel):
    """캐릭터 보석 정보 모델."""

    gems: List[Gem] = field(default_factory=list)
    effects: Optional[ArmoryGemEffect] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmoryGem":
        """딕셔너리에서 인스턴스를 생성합니다."""
        effects_data = data.get("Effects")
        effects = ArmoryGemEffect.from_dict(effects_data) if effects_data else None
        return cls(
            gems=[Gem.from_dict(g) for g in (data.get("Gems") or [])], effects=effects
        )


@dataclass
class Aggregation(BaseModel):
    """통계 기본 모델."""

    play_count: int
    victory_count: int
    lose_count: int
    tie_count: int
    kill_count: int
    ace_count: int
    death_count: int


@dataclass
class AggregationTeamDeathMatchRank(Aggregation):
    """경쟁전 통계 모델."""

    rank: int
    rank_name: str
    rank_icon: str
    rank_last_mmr: int


@dataclass
class AggregationTeamDeathMatch(Aggregation):
    """팀 데스매치 통계 모델."""

    assist_count: int


@dataclass
class AggregationElimination(Aggregation):
    """대장전 통계 모델."""

    first_win_count: int
    second_win_count: int
    third_win_count: int
    first_play_count: int
    second_play_count: int
    third_play_count: int
    all_kill_count: int


@dataclass
class AggregationOneDeathmatch(BaseModel):
    """1:1 데스매치 통계 모델."""

    kill_count: int
    death_count: int
    all_kill_count: int
    out_damage: int
    in_damage: int
    first_win_count: int
    second_win_count: int
    third_win_count: int
    first_play_count: int
    second_play_count: int
    third_play_count: int


@dataclass
class Colosseum(BaseModel):
    """투기장 시즌 정보 모델."""

    season_name: str
    competitive: Optional[AggregationTeamDeathMatchRank] = None
    team_deathmatch: Optional[AggregationTeamDeathMatch] = None
    team_elimination: Optional[AggregationElimination] = None
    co_op_battle: Optional[Aggregation] = None
    one_deathmatch: Optional[AggregationOneDeathmatch] = None
    one_deathmatch_rank: Optional[AggregationOneDeathmatch] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Colosseum":
        """딕셔너리에서 인스턴스를 생성합니다."""
        competitive_data = data.get("Competitive")
        team_dm_data = data.get("TeamDeathmatch")
        team_el_data = data.get("TeamElimination")
        coop_data = data.get("CoOpBattle")
        one_dm_data = data.get("OneDeathmatch")
        one_dm_rank_data = data.get("OneDeathmatchRank")

        return cls(
            season_name=data.get("SeasonName", ""),
            competitive=(
                AggregationTeamDeathMatchRank.from_dict(competitive_data)
                if competitive_data
                else None
            ),
            team_deathmatch=(
                AggregationTeamDeathMatch.from_dict(team_dm_data)
                if team_dm_data
                else None
            ),
            team_elimination=(
                AggregationElimination.from_dict(team_el_data) if team_el_data else None
            ),
            co_op_battle=Aggregation.from_dict(coop_data) if coop_data else None,
            one_deathmatch=(
                AggregationOneDeathmatch.from_dict(one_dm_data) if one_dm_data else None
            ),
            one_deathmatch_rank=(
                AggregationOneDeathmatch.from_dict(one_dm_rank_data)
                if one_dm_rank_data
                else None
            ),
        )


@dataclass
class ColosseumInfo(BaseModel):
    """전체 투기장 정보 모델."""

    rank: int
    pre_rank: int
    exp: int
    colosseums: List[Colosseum] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColosseumInfo":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            rank=data.get("Rank", 0),
            pre_rank=data.get("PreRank", 0),
            exp=data.get("Exp", 0),
            colosseums=[Colosseum.from_dict(c) for c in (data.get("Colosseums") or [])],
        )


@dataclass
class CollectiblePoint(BaseModel):
    """수집품 포인트 모델."""

    point_name: str
    point: int
    max_point: int


@dataclass
class Collectible(BaseModel):
    """수집품 상세 모델."""

    type: str
    icon: str
    point: int
    max_point: int
    collectible_points: List[CollectiblePoint] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Collectible":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            type=data.get("Type", ""),
            icon=data.get("Icon", ""),
            point=data.get("Point", 0),
            max_point=data.get("MaxPoint", 0),
            collectible_points=[
                CollectiblePoint.from_dict(p)
                for p in (data.get("CollectiblePoints") or [])
            ],
        )


@dataclass
class ArkPassivePoint(BaseModel):
    """아크 패시브 포인트 모델."""

    name: str
    value: int
    tooltip: str
    description: str


@dataclass
class ArkPassiveEffectSkill(BaseModel):
    """아크 패시브 효과 스킬 모델."""

    name: str
    description: str
    icon: str
    tooltip: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArkPassiveEffectSkill":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            name=data.get("Name", ""),
            description=data.get("Description", ""),
            icon=data.get("Icon", ""),
            tooltip=data.get("ToolTip", "") or data.get("Tooltip", ""),
        )


@dataclass
class ArkPassive(BaseModel):
    """아크 패시브 정보 모델."""

    is_ark_passive: bool
    points: List[ArkPassivePoint] = field(default_factory=list)
    effects: List[ArkPassiveEffectSkill] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArkPassive":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            is_ark_passive=data.get("IsArkPassive", False),
            points=[ArkPassivePoint.from_dict(p) for p in (data.get("Points") or [])],
            effects=[
                ArkPassiveEffectSkill.from_dict(e) for e in (data.get("Effects") or [])
            ],
        )


@dataclass
class ArkGridGem(BaseModel):
    """아크 그리드 보석 모델."""

    index: int
    icon: str
    is_active: bool
    grade: str
    tooltip: str


@dataclass
class ArkGridEffect(BaseModel):
    """아크 그리드 효과 모델."""

    name: str
    level: int
    tooltip: str


@dataclass
class ArkGridSlot(BaseModel):
    """아크 그리드 슬롯 모델."""

    index: int
    icon: str
    name: str
    point: int
    grade: str
    tooltip: str
    gems: List[ArkGridGem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArkGridSlot":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            index=data.get("Index", 0),
            icon=data.get("Icon", ""),
            name=data.get("Name", ""),
            point=data.get("Point", 0),
            grade=data.get("Grade", ""),
            tooltip=data.get("Tooltip", ""),
            gems=[ArkGridGem.from_dict(g) for g in (data.get("Gems") or [])],
        )


@dataclass
class ArkGrid(BaseModel):
    """아크 그리드 정보 모델."""

    slots: List[ArkGridSlot] = field(default_factory=list)
    effects: List[ArkGridEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArkGrid":
        """딕셔너리에서 인스턴스를 생성합니다."""
        return cls(
            slots=[ArkGridSlot.from_dict(s) for s in (data.get("Slots") or [])],
            effects=[ArkGridEffect.from_dict(e) for e in (data.get("Effects") or [])],
        )


@dataclass
class ArmoryTotal(BaseModel):
    """Armory 종합 정보 모델."""

    armory_profile: Optional[ArmoryProfile] = None
    armory_equipment: List[ArmoryEquipment] = field(default_factory=list)
    armory_avatars: List[ArmoryAvatar] = field(default_factory=list)
    armory_skills: List[ArmorySkill] = field(default_factory=list)
    armory_engraving: Optional[ArmoryEngraving] = None
    armory_card: Optional[ArmoryCard] = None
    armory_gem: Optional[ArmoryGem] = None
    colosseum_info: Optional[ColosseumInfo] = None
    collectibles: List[Collectible] = field(default_factory=list)
    ark_passive: Optional[ArkPassive] = None
    ark_grid: Optional[ArkGrid] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmoryTotal":
        """딕셔너리에서 인스턴스를 생성합니다."""
        # 각 하위 객체들을 딕셔너리 키 존재 여부에 따라 처리
        profile_data = data.get("ArmoryProfile")
        armory_profile = ArmoryProfile.from_dict(profile_data) if profile_data else None

        equipment = [
            ArmoryEquipment.from_dict(item)
            for item in (data.get("ArmoryEquipment") or [])
        ]
        avatars = [
            ArmoryAvatar.from_dict(item) for item in (data.get("ArmoryAvatars") or [])
        ]
        skills = [
            ArmorySkill.from_dict(item) for item in (data.get("ArmorySkills") or [])
        ]

        engraving_data = data.get("ArmoryEngraving")
        armory_engraving = (
            ArmoryEngraving.from_dict(engraving_data) if engraving_data else None
        )

        card_data = data.get("ArmoryCard")
        armory_card = ArmoryCard.from_dict(card_data) if card_data else None

        gem_data = data.get("ArmoryGem")
        armory_gem = ArmoryGem.from_dict(gem_data) if gem_data else None

        colosseum_data = data.get("ColosseumInfo")
        colosseum_info = (
            ColosseumInfo.from_dict(colosseum_data) if colosseum_data else None
        )

        collectibles = [
            Collectible.from_dict(item) for item in (data.get("Collectibles") or [])
        ]

        ark_passive_data = data.get("ArkPassive")
        ark_passive = (
            ArkPassive.from_dict(ark_passive_data) if ark_passive_data else None
        )

        ark_grid_data = data.get("ArkGrid")
        ark_grid = ArkGrid.from_dict(ark_grid_data) if ark_grid_data else None

        return cls(
            armory_profile=armory_profile,
            armory_equipment=equipment,
            armory_avatars=avatars,
            armory_skills=skills,
            armory_engraving=armory_engraving,
            armory_card=armory_card,
            armory_gem=armory_gem,
            colosseum_info=colosseum_info,
            collectibles=collectibles,
            ark_passive=ark_passive,
            ark_grid=ark_grid,
        )
