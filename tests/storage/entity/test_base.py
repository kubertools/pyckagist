import pytest
from pydantic import ValidationError

from pyckagist.storage.entity.base import BaseEntity


class TestBaseEntity:
    def test_serialize_returns_dict_representation(self):
        class SampleEntity(BaseEntity):
            field1: int
            field2: str

        entity = SampleEntity(field1=1, field2="test")
        expected_output = {"field1": 1, "field2": "test"}
        assert entity.serialize() == expected_output

    def test_serialize_json_returns_json_representation(self):
        class SampleEntity(BaseEntity):
            field1: int
            field2: str

        entity = SampleEntity(field1=1, field2="test")
        expected_output = '{"field1":1,"field2":"test"}'
        assert entity.serialize_json() == expected_output

    def test_deserialize_with_empty_dict(self):
        class SampleEntity(BaseEntity):
            field1: int = 0
            field2: str = ""

        data: dict[str, object] = {}

        entity = SampleEntity.deserialize(data)
        assert entity.field1 == 0
        assert entity.field2 == ""

    def test_deserialize_creates_instance(self):
        class SampleEntity(BaseEntity):
            field1: int
            field2: str

        data = {"field1": 1, "field2": "test"}
        entity = SampleEntity.deserialize(data)

        assert entity.field1 == 1
        assert entity.field2 == "test"

    def test_deserialize_json_creates_instance(self):
        json_data = '{"field1": 1, "field2": "test"}'

        class SampleEntity(BaseEntity):
            field1: int
            field2: str

        entity = SampleEntity.deserialize_json(json_data)

        assert isinstance(entity, BaseEntity)

    def test_deserialize_json_with_empty_string(self):
        class SampleEntity(BaseEntity):
            field1: int
            field2: str

        with pytest.raises(ValidationError):
            SampleEntity.deserialize_json("")

    def test_deserialize_missing_required_fields(self):
        class SampleEntity(BaseEntity):
            field1: int
            field2: str

        with pytest.raises(ValidationError):
            SampleEntity.deserialize({})

    def test_deserialize_json_with_malformed_json(self):
        class SampleEntity(BaseEntity):
            field1: int
            field2: str

        with pytest.raises(ValidationError):
            SampleEntity.deserialize_json('{"field1": 1, "field2": "test"')
