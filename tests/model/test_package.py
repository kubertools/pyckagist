from pyckagist import Package, PackagePlatform
from pyckagist.model.package import PackageDefinition, ExecutablePackage


class TestPackage:
    def test_create_package_with_valid_name_and_version(self):
        package = Package(name="TestPackage", version="1.0.0")

        assert package.name() == "TestPackage"
        assert package.version() == "1.0.0"

    def test_compare_package_with_non_package_object(self):
        package = Package(name="TestPackage", version="1.0.0")

        assert package != "NotAPackage"

    def test_retrieving_name(self):
        package = Package(name="TestPackage", version="1.0.0")

        assert package.name() == "TestPackage"

    def test_generate_string_representation(self):
        package = Package(name="TestPackage", version="1.0.0")

        assert str(package) == "TestPackage (1.0.0)"

    def test_compare_identical_packages(self):
        package1 = Package(name="TestPackage", version="1.0.0")
        package2 = Package(name="TestPackage", version="1.0.0")

        assert package1 == package2

    def test_retrieving_version(self):
        package = Package(name="TestPackage", version="1.0.0")

        assert package.version() == "1.0.0"

    def test_generating_hash_of_package_instance(self):
        package = Package(name="TestPackage", version="1.0.0")

        assert hash(package) == hash(str(package))

    def test_create_package_with_empty_name_and_version(self):
        package = Package(name="", version="")

        assert package.name() == ""
        assert package.version() == ""

    def test_comparing_different_names(self):
        package1 = Package(name="Package1", version="1.0.0")
        package2 = Package(name="Package2", version="1.0.0")

        assert package1 != package2

    def test_compare_different_versions(self):
        package1 = Package(name="PackageA", version="1.0.0")
        package2 = Package(name="PackageA", version="2.0.0")

        assert package1 != package2


class TestPackageDefinition:
    def test_create_package_definition_with_valid_data(self):
        platform = PackagePlatform("linux", "x86_64")
        package = PackageDefinition("test_package", "1.0.0", platform)

        assert package.name() == "test_package"
        assert package.version() == "1.0.0"
        assert package.platform() == platform

    def test_compare_with_non_package_definition_object(self):
        platform = PackagePlatform("linux", "x86_64")
        package = PackageDefinition("test_package", "1.0.0", platform)

        assert package != "not_a_package"

    def test_compare_identical_package_definitions_for_equality(self):
        platform = PackagePlatform("linux", "x86_64")

        package1 = PackageDefinition("test_package", "1.0.0", platform)
        package2 = PackageDefinition("test_package", "1.0.0", platform)

        assert package1 == package2

    def test_retrieve_name_version_platform(self):
        platform = PackagePlatform("windows", "x86")
        package = PackageDefinition("example_package", "2.0.0", platform)

        assert package.name() == "example_package"
        assert package.version() == "2.0.0"
        assert package.platform() == platform

    def test_converting_to_string_representation(self):
        platform = PackagePlatform("linux", "x86_64")
        package = PackageDefinition("test_package", "1.0.0", platform)

        assert str(package) == "test_package@linux/x86_64 (1.0.0)"

    def test_create_package_definition_with_empty_strings(self):
        platform = PackagePlatform.current_platform()
        package = PackageDefinition("", "", platform)

        assert package.name() == ""
        assert package.version() == ""
        assert package.platform() == platform

    def test_comparing_different_names(self):
        platform = PackagePlatform("linux", "x86_64")

        package1 = PackageDefinition("package_1", "1.0.0", platform)
        package2 = PackageDefinition("package_2", "1.0.0", platform)

        assert package1 != package2

    def test_comparing_different_versions(self):
        platform_1 = PackagePlatform("linux", "x86_64")
        platform_2 = PackagePlatform("windows", "x86")

        package_1 = PackageDefinition("test_package", "1.0.0", platform_1)
        package_2 = PackageDefinition("test_package", "2.0.0", platform_2)

        assert package_1 != package_2

    def test_compare_different_platforms(self):
        platform_1 = PackagePlatform("linux", "x86_64")
        platform_2 = PackagePlatform("windows", "x86_64")

        package_1 = PackageDefinition("test_package", "1.0.0", platform_1)
        package_2 = PackageDefinition("test_package", "1.0.0", platform_2)

        assert package_1 != package_2


class TestExecutablePackage:
    def test_validate_correct_executable_path_and_hash(self, mocker):
        mocker.patch("os.path.exists", return_value=True)

        mock_open = mocker.patch(
            "builtins.open", mocker.mock_open(read_data=b"correct data")
        )
        mocker.patch(
            "hashlib.sha256", return_value=mocker.Mock(hexdigest=lambda: "correcthash")
        )

        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_package = ExecutablePackage(
            definition, "/path/to/executable", "correcthash"
        )

        assert executable_package.validate()

        mock_open.assert_called_once_with("/path/to/executable", "rb")

    def test_validate_empty_executable_path(self, mocker):
        mocker.patch("os.path.exists", return_value=False)

        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_package = ExecutablePackage(definition, "", "somehash")

        assert not executable_package.validate()

    def test_validate_non_existent_executable_path(self, mocker):
        mocker.patch("os.path.exists", return_value=False)

        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_package = ExecutablePackage(
            definition, "/non_existent_path", "correcthash"
        )

        assert not executable_package.validate()

    def test_string_representation_matches_expected_format(self):
        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_package = ExecutablePackage(
            definition, "/path/to/executable", "correcthash"
        )

        assert (
            str(executable_package)
            == "test_package@test_system/test_architecture (1.0)"
        )

    def test_equality_for_identical_objects(self):
        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )

        executable_package1 = ExecutablePackage(
            definition, "/path/to/executable", "hash1"
        )
        executable_package2 = ExecutablePackage(
            definition, "/path/to/executable", "hash1"
        )

        assert executable_package1 == executable_package2

    def test_static_hash_method_correctly_computes_sha256_hash(self):
        data = b"test data"
        expected_hash = (
            "916f0027a575074ce72a331777c3478d6513f786a591bd892da1a577bf2335f9"
        )

        assert ExecutablePackage.hash(data) == expected_hash

    def test_validate_incorrect_hash_value(self, mocker):
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("builtins.open", mocker.mock_open(read_data=b"correct data"))
        mocker.patch(
            "hashlib.sha256", return_value=mocker.Mock(hexdigest=lambda: "correcthash")
        )

        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_package = ExecutablePackage(
            definition, "/path/to/executable", "incorrecthash"
        )

        assert not executable_package.validate()

    def test_equality_check_with_non_executable_package_returns_false(self):
        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )

        executable_package = ExecutablePackage(
            definition, "/path/to/executable", "correcthash"
        )

        assert executable_package != "non_executable_package"

    def test_executable_package_equality_with_identical_attributes(self):
        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_path = "/path/to/executable"
        executable_hash = "dummyhash"

        package1 = ExecutablePackage(definition, executable_path, executable_hash)
        package2 = ExecutablePackage(definition, executable_path, executable_hash)

        assert package1 == package2

    def test_executable_package_inequality_with_different_definitions(self):
        definition1 = PackageDefinition(
            "test_package1", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        definition2 = PackageDefinition(
            "test_package2", "2.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_path = "/path/to/executable"
        executable_hash = "dummyhash"

        package1 = ExecutablePackage(definition1, executable_path, executable_hash)
        package2 = ExecutablePackage(definition2, executable_path, executable_hash)

        assert package1 != package2

    def test_executable_package_inequality_with_different_paths(self):
        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_path1 = "/path/to/executable1"
        executable_path2 = "/path/to/executable2"
        executable_hash = "dummyhash"

        package1 = ExecutablePackage(definition, executable_path1, executable_hash)
        package2 = ExecutablePackage(definition, executable_path2, executable_hash)

        assert package1 != package2

    def test_executable_package_inequality_with_different_hashes(self):
        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_path = "/path/to/executable"
        executable_hash1 = "dummyhash1"
        executable_hash2 = "dummyhash2"

        package1 = ExecutablePackage(definition, executable_path, executable_hash1)
        package2 = ExecutablePackage(definition, executable_path, executable_hash2)

        assert package1 != package2

    def test_validate_handles_file_read_errors_gracefully(self, mocker):
        mocker.patch("os.path.exists", return_value=False)

        definition = PackageDefinition(
            "test_package", "1.0", PackagePlatform("test_system", "test_architecture")
        )
        executable_package = ExecutablePackage(
            definition, "/path/to/non_existent_executable", "correcthash"
        )

        assert not executable_package.validate()
