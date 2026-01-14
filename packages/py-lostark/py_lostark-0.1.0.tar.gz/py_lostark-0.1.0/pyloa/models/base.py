"""API 응답 객체를 위한 기본 모델."""

from dataclasses import asdict
from typing import Dict, TypeVar, Type
import re


T = TypeVar("T", bound="BaseModel")


class BaseModel:
    """모든 API 응답 모델의 기본 클래스."""

    @classmethod
    def _pascal_to_snake(cls, name: str) -> str:
        """PascalCase를 snake_case로 변환합니다."""
        # Insert underscore before uppercase letters
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @classmethod
    def _snake_to_pascal(cls, name: str) -> str:
        """snake_case를 PascalCase로 변환합니다."""
        components = name.split("_")
        return "".join(x.title() for x in components)

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> T:
        """딕셔너리에서 모델 인스턴스를 생성합니다.

        PascalCase(API 형식)와 snake_case(Python 형식)를 모두 지원합니다.
        """
        # Get field names from dataclass
        import dataclasses

        if not dataclasses.is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be a dataclass")

        fields = {f.name for f in dataclasses.fields(cls)}
        kwargs = {}

        for key, value in data.items():
            # Try snake_case first (direct match)
            snake_key = key if "_" in key else cls._pascal_to_snake(key)

            if snake_key in fields:
                kwargs[snake_key] = value

        return cls(**kwargs)

    def to_dict(self) -> Dict:
        """모델 인스턴스를 딕셔너리로 변환합니다."""
        return asdict(self)
