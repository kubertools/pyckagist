from pyckagist import PackagePlatform
from pyckagist.model.package import PackageDefinition, ExecutablePackage
from pyckagist.storage.entity.package import PackagePlatformEntity, PackageEntity


class TestPackageEntity:
    def test_to_executable_package_conversion(self):
        platform_entity = PackagePlatformEntity(system="linux", architecture="x86_64")
        package_entity = PackageEntity(
            name="test_package",
            version="1.0.0",
            platform=platform_entity,
            executable_path="/path/to/executable",
            executable_hash="dummyhash",
        )
        executable_package = package_entity.to_executable_package()

        assert executable_package.definition().name() == "test_package"
        assert executable_package.definition().version() == "1.0.0"
        assert executable_package.definition().platform().system() == "linux"
        assert executable_package.definition().platform().architecture() == "x86_64"
        assert executable_package.executable_path() == "/path/to/executable"
        assert executable_package.executable_hash() == "dummyhash"

    def test_equality_comparison_for_identical_instances(self):
        platform_entity = PackagePlatformEntity(system="linux", architecture="x86_64")
        package_entity1 = PackageEntity(
            name="test_package",
            version="1.0.0",
            platform=platform_entity,
            executable_path="/path/to/executable",
            executable_hash="dummyhash",
        )
        package_entity2 = PackageEntity(
            name="test_package",
            version="1.0.0",
            platform=platform_entity,
            executable_path="/path/to/executable",
            executable_hash="dummyhash",
        )

        assert package_entity1 == package_entity2

    def test_different_versions_expect_inequality(self):
        platform = PackagePlatformEntity(system="Linux", architecture="x86_64")
        package1 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform,
            executable_path="/path/to/executable",
            executable_hash="abc123",
        )
        package2 = PackageEntity(
            name="TestPackage",
            version="2.0.0",
            platform=platform,
            executable_path="/different/path/to/executable",
            executable_hash="def456",
        )
        assert package1 != package2

    def test_different_names_expect_inequality(self):
        platform = PackagePlatformEntity(system="Linux", architecture="x86_64")
        package1 = PackageEntity(
            name="TestPackage1",
            version="1.0.0",
            platform=platform,
            executable_path="/path/to/executable",
            executable_hash="abc123",
        )
        package2 = PackageEntity(
            name="TestPackage2",
            version="1.0.0",
            platform=platform,
            executable_path="/path/to/executable",
            executable_hash="abc123",
        )
        assert package1 != package2

    def test_different_platform_systems_expect_inequality(self):
        platform1 = PackagePlatformEntity(system="Linux", architecture="x86_64")
        platform2 = PackagePlatformEntity(system="Windows", architecture="x86_64")
        package1 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform1,
            executable_path="/path/to/executable",
            executable_hash="abc123",
        )
        package2 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform2,
            executable_path="/path/to/executable",
            executable_hash="abc123",
        )
        assert package1 != package2

    def test_different_platform_architectures_inequality(self):
        platform1 = PackagePlatformEntity(system="Windows", architecture="x86_64")
        platform2 = PackagePlatformEntity(system="Windows", architecture="arm64")
        package1 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform1,
            executable_path="/path/to/executable",
            executable_hash="abc123",
        )
        package2 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform2,
            executable_path="/path/to/executable",
            executable_hash="abc123",
        )
        assert package1 != package2

    def test_different_executable_paths_inequality(self):
        platform = PackagePlatformEntity(system="Linux", architecture="x86_64")
        package1 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform,
            executable_path="/path/to/executable1",
            executable_hash="abc123",
        )
        package2 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform,
            executable_path="/path/to/executable2",
            executable_hash="abc123",
        )
        assert package1 != package2

    def test_different_executable_hashes_inequality(self):
        platform = PackagePlatformEntity(system="Linux", architecture="x86_64")
        package1 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform,
            executable_path="/path/to/executable",
            executable_hash="abc123",
        )
        package2 = PackageEntity(
            name="TestPackage",
            version="1.0.0",
            platform=platform,
            executable_path="/path/to/executable",
            executable_hash="different_hash",
        )
        assert package1 != package2

    def test_serialize_to_dictionary_correctly(self):
        platform_entity = PackagePlatformEntity(system="linux", architecture="x86_64")
        package_entity = PackageEntity(
            name="test_package",
            version="1.0.0",
            platform=platform_entity,
            executable_path="/path/to/executable",
            executable_hash="dummyhash",
        )
        serialized_package = package_entity.serialize()

        expected_result = {
            "name": "test_package",
            "version": "1.0.0",
            "platform": {"system": "linux", "architecture": "x86_64"},
            "executable_path": "/path/to/executable",
            "executable_hash": "dummyhash",
        }

        assert serialized_package == expected_result

    def test_convert_from_executable_package(self):
        executable_package = ExecutablePackage(
            definition=PackageDefinition(
                name="test_package",
                version="1.0.0",
                platform=PackagePlatform(system="linux", architecture="x86_64"),
            ),
            executable_path="/path/to/executable",
            executable_hash="dummyhash",
        )
        package_entity = PackageEntity.from_executable_package(executable_package)

        assert package_entity.name == "test_package"
        assert package_entity.version == "1.0.0"
        assert package_entity.platform.system == "linux"
        assert package_entity.platform.architecture == "x86_64"
        assert package_entity.executable_path == "/path/to/executable"
        assert package_entity.executable_hash == "dummyhash"

    def test_handle_equality_comparison_with_different_types(self):
        platform_entity = PackagePlatformEntity(system="linux", architecture="x86_64")
        package_entity = PackageEntity(
            name="test_package",
            version="1.0.0",
            platform=platform_entity,
            executable_path="/path/to/executable",
            executable_hash="dummyhash",
        )

        assert package_entity != "not_a_package_entity"

    def test_deserialize_to_package_entity(self):
        # Define a sample dictionary representing PackageEntity data
        data = {
            "name": "test_package",
            "version": "1.0.0",
            "platform": {"system": "linux", "architecture": "x86_64"},
            "executable_path": "/path/to/executable",
            "executable_hash": "dummyhash",
        }

        # Deserialize the dictionary to PackageEntity
        package_entity = PackageEntity.deserialize(data)

        # Assertions to verify the deserialized PackageEntity
        assert package_entity.name == "test_package"
        assert package_entity.version == "1.0.0"
        assert package_entity.platform.system == "linux"
        assert package_entity.platform.architecture == "x86_64"
        assert package_entity.executable_path == "/path/to/executable"
        assert package_entity.executable_hash == "dummyhash"
