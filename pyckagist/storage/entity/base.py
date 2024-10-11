from abc import ABC

from typing_extensions import Self

from pydantic import BaseModel


class BaseEntity(BaseModel, ABC):
    def serialize(self) -> dict:
        return self.model_dump()

    def serialize_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def deserialize(cls, data: dict) -> Self:
        return cls.model_validate(data)

    @classmethod
    def deserialize_json(cls, data: str) -> Self:
        return cls.model_validate_json(data)
