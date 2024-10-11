from pyckagist.model.platform import PackagePlatform
from pyckagist.model.remote import RemotePackageDefinition, RemotePackage


class TestRemotePackageDefinition:
    def test_create_with_valid_name_and_source(self):
        from pyckagist.model.remote import RemotePackageDefinition

        name = "valid_name"
        source = "valid_source"
        package = RemotePackageDefinition(name, source)

        assert package.name() == name
        assert package.source() == source
        assert hash(package) == hash(str(package))

    def test_create_with_empty_name(self):
        from pyckagist.model.remote import RemotePackageDefinition

        name = ""
        source = "valid_source"
        package = RemotePackageDefinition(name, source)

        assert package.name() == name
        assert package.source() == source

    def test_retrieving_name(self):
        from pyckagist.model.remote import RemotePackageDefinition

        name = "test_name"
        source = "valid_source"
        package = RemotePackageDefinition(name, source)

        assert package.name() == name

    def test_converting_to_string_representation(self):
        from pyckagist.model.remote import RemotePackageDefinition

        name = "test_package"
        source = "valid_source"
        package = RemotePackageDefinition(name, source)

        expected_result = f"{source}/{name}"
        assert str(package) == expected_result

    def test_retrieving_source(self):
        from pyckagist.model.remote import RemotePackageDefinition

        name = "test_package"
        source = "valid_source"
        package = RemotePackageDefinition(name, source)

        assert package.source() == source

    def test_comparing_identical_instances_for_equality(self):
        from pyckagist.model.remote import RemotePackageDefinition

        name = "test_name"
        source = "valid_source"

        package1 = RemotePackageDefinition(name, source)
        package2 = RemotePackageDefinition(name, source)

        assert package1 == package2

    def test_compare_with_different_class(self):
        from pyckagist.model.remote import RemotePackageDefinition

        name = "test_name"
        source = "valid_source"
        package = RemotePackageDefinition(name, source)

        class DifferentClass:
            def __init__(self, name_, source_) -> None:
                self.name = name_
                self.source = source_

        different_package = DifferentClass(name, source)

        assert package != different_package

    def test_compare_different_names(self):
        from pyckagist.model.remote import RemotePackageDefinition

        name1 = "name1"
        name2 = "name2"
        source = "valid_source"

        package1 = RemotePackageDefinition(name1, source)
        package2 = RemotePackageDefinition(name2, source)

        assert package1 != package2

    def test_comparing_instances_with_different_sources(self, mocker):
        from pyckagist.model.remote import RemotePackageDefinition

        source1 = "source1"
        source2 = "source2"

        package1 = RemotePackageDefinition("name", source1)
        package2 = RemotePackageDefinition("name", source2)

        assert package1 != package2


class TestRemotePackage:
    def test_initialization_with_valid_parameters(self):
        source = "valid_source"

        remote_package = RemotePackage(
            definition=RemotePackageDefinition("example_package", source),
            version="v1.0.0",
            platforms=[PackagePlatform("linux", "x86_64")],
        )

        assert remote_package.definition() == RemotePackageDefinition(
            "example_package", source
        )
        assert remote_package.name() == remote_package.definition().name()
        assert remote_package.version() == "v1.0.0"
        assert remote_package.supported_platforms() == [
            PackagePlatform("linux", "x86_64")
        ]

    def test_initialization_with_empty_platforms_list(self):
        source = "valid_source"

        remote_package = RemotePackage(
            definition=RemotePackageDefinition("example_package", source),
            version="v1.0.0",
            platforms=[],
        )

        assert remote_package.definition() == RemotePackageDefinition(
            "example_package", source
        )
        assert remote_package.version() == "v1.0.0"
        assert remote_package.supported_platforms() == []

    def test_equality_check_with_identical_instances(self):
        source = "valid_source"

        definition = RemotePackageDefinition("example_package", source)
        version = "1.0.0"
        platforms = [PackagePlatform("linux", "x86_64")]

        remote_package1 = RemotePackage(definition, version, platforms)
        remote_package2 = RemotePackage(definition, version, platforms)

        assert remote_package1 == remote_package2

    def test_string_representation_with_valid_attributes(self):
        source = "valid_source"

        definition = RemotePackageDefinition("example_package", source)
        version = "1.0.0"
        platforms = [PackagePlatform("linux", "x86_64")]

        remote_package = RemotePackage(definition, version, platforms)

        expected_output = f"{definition} ({version})"

        assert str(remote_package) == expected_output

    def test_equality_check_with_different_types(self):
        source = "valid_source"

        definition = RemotePackageDefinition("example_package", source)
        version = "1.0.0"
        platforms = [PackagePlatform("linux", "x86_64")]

        remote_package = RemotePackage(definition, version, platforms)
        different_type_object = "This is a string"

        assert remote_package != different_type_object

    def test_equality_check_with_different_definitions(self):
        source1 = "source1"

        definition1 = RemotePackageDefinition("example_package1", source1)
        version1 = "version1"
        platforms1 = [PackagePlatform("system1", "architecture1")]

        source2 = "source2"

        definition2 = RemotePackageDefinition("example_package1", source2)
        version2 = "version1"
        platforms2 = [PackagePlatform("system2", "architecture2")]

        remote_package_1 = RemotePackage(definition1, version1, platforms1)
        remote_package_1_1 = RemotePackage(definition1, version1, platforms1)

        remote_package_2 = RemotePackage(definition2, version2, platforms2)

        assert remote_package_1 == remote_package_1_1
        assert remote_package_1 != remote_package_2

    def test_equality_check_with_different_versions(self):
        source = "valid_source"

        definition = RemotePackageDefinition("example_package", source)
        platforms = [PackagePlatform("linux", "x86_64")]

        remote_package_1 = RemotePackage(definition, "1.0.0", platforms)
        remote_package_2 = RemotePackage(definition, "2.0.0", platforms)

        assert remote_package_1 != remote_package_2

    def test_equality_check_with_different_platforms(self):
        source = "valid_source"

        definition = RemotePackageDefinition("example_package", source)
        version = "1.0.0"

        platforms_1 = [PackagePlatform("linux", "x86_64")]
        platforms_2 = [PackagePlatform("windows", "x86")]

        remote_package_1 = RemotePackage(definition, version, platforms_1)
        remote_package_2 = RemotePackage(definition, version, platforms_2)

        assert remote_package_1 != remote_package_2
