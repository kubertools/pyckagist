from pyckagist.storage.entity.base import BaseEntity
from pyckagist.storage.entity.reference import ReferenceEntity


class TestReferenceEntity:
    def test_serialize_deserialize_valid_data(self):
        entity = ReferenceEntity(namespace="test_namespace", package="test_package")
        serialized = entity.serialize()
        deserialized = ReferenceEntity.deserialize(serialized)
        assert deserialized == entity

    def test_equality_operator_identifies_identical_instances(self):
        entity1 = ReferenceEntity(namespace="test_namespace", package="test_package")
        entity2 = ReferenceEntity(namespace="test_namespace", package="test_package")

        assert entity1 == entity2

    def test_instantiate_with_valid_namespace_and_package(self):
        entity = ReferenceEntity(namespace="valid_namespace", package="valid_package")

        assert entity.namespace == "valid_namespace"
        assert entity.package == "valid_package"

    def test_serialize_deserialize_json_data(self):
        entity = ReferenceEntity(namespace="test_namespace", package="test_package")

        serialized = entity.serialize_json()
        deserialized = ReferenceEntity.deserialize_json(serialized)

        assert deserialized == entity

    def test_eq_identical_instance(self):
        entity1 = ReferenceEntity(namespace="namespace1", package="package1")
        entity2 = ReferenceEntity(namespace="namespace1", package="package1")

        assert entity1 == entity2

    def test_eq_different_class_instance(self):
        class DifferentEntity(BaseEntity):
            namespace: str
            package: str

        entity1 = ReferenceEntity(namespace="namespace1", package="package1")
        different_entity = DifferentEntity(namespace="namespace1", package="package1")

        assert entity1 != different_entity

    def test_returns_false_with_different_namespace(self):
        entity1 = ReferenceEntity(namespace="namespace1", package="package1")
        entity2 = ReferenceEntity(namespace="namespace2", package="package1")

        assert entity1 != entity2

    def test_returns_false_with_different_package(self):
        entity1 = ReferenceEntity(namespace="namespace1", package="package1")
        entity2 = ReferenceEntity(namespace="namespace1", package="package2")

        assert entity1 != entity2
