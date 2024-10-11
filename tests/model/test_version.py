import pytest

from pyckagist.model.version import PackageVersion


class TestPackageVersion:
    def test_create_package_version_instance(self):
        version = PackageVersion(1, 2, 3)

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

        assert str(version) == "1.2.3"

    def test_parse_version_string_with_non_numeric_characters(self):
        version = PackageVersion.parse("v1.2.3")

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

        assert str(version) == "1.2.3"

    def test_compare_different_versions(self):
        version_1 = PackageVersion(1, 2, 3)
        version_2 = PackageVersion(2, 1, 4)

        assert version_1 < version_2
        assert version_1 <= version_2
        assert version_2 > version_1
        assert version_2 >= version_1

    def test_parsing_version_with_negative_numbers(self):
        version = PackageVersion.parse("1.-2.3")

        assert version.major == 1
        assert version.minor == -2
        assert version.patch == 3

        assert str(version) == "1.-2.3"

    def test_parse_version_string_with_more_than_three_components(self):
        with pytest.raises(ValueError):
            PackageVersion.parse("1.2.3.4")

    def test_parsing_valid_version_string_with_one_component(self):
        version = PackageVersion.parse("1")

        assert version.major == 1
        assert version.minor == 0
        assert version.patch == 0

        assert str(version) == "1.0.0"

    def test_parsing_empty_version_string(self):
        with pytest.raises(ValueError):
            PackageVersion.parse("")

    def test_parsing_valid_version_string(self):
        version = PackageVersion.parse("1.2.3")

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

        assert str(version) == "1.2.3"

    def test_parsing_valid_version_string_with_two_components(self):
        version = PackageVersion.parse("1.2")

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 0

        assert str(version) == "1.2.0"

    def test_compare_greater_than_or_equal_to(self):
        version_1 = PackageVersion(1, 2, 3)
        version_2 = PackageVersion(1, 2, 2)
        version_3 = PackageVersion(1, 1, 3)

        assert version_1 >= version_2
        assert version_1 >= version_3
        assert version_2 >= version_3

    def test_compare_less_than_or_equal_to(self):
        version_1 = PackageVersion(1, 2, 3)
        version_2 = PackageVersion(1, 2, 4)

        assert version_1 <= version_2
        assert version_2 > version_1

    def test_compare_greater_than(self):
        version_1 = PackageVersion(2, 1, 1)
        version_2 = PackageVersion(1, 2, 1)
        version_3 = PackageVersion(1, 1, 2)
        version_4 = PackageVersion(1, 1, 1)

        assert version_1 > version_2
        assert version_2 > version_3
        assert version_3 > version_4

        assert not version_4 > version_1

    def test_compare_package_version_less_than(self):
        version_1 = PackageVersion(1, 1, 1)
        version_2 = PackageVersion(1, 1, 2)
        version_3 = PackageVersion(1, 2, 1)
        version_4 = PackageVersion(2, 1, 1)

        assert version_1 < version_2
        assert version_2 < version_3
        assert version_3 < version_4

        assert not version_4 < version_1

    def test_convert_package_version_to_string(self):
        version = PackageVersion(1, 2, 3)

        assert str(version) == "1.2.3"

    def test_compare_package_versions_equality(self):
        version1 = PackageVersion(1, 2, 3)
        version2 = PackageVersion(1, 2, 3)

        assert version1 == version2

    def test_equality_check_with_str(self):
        version1 = PackageVersion(1, 2, 3)
        version2 = "1.2.3"

        assert version1 == version2

    def test_equality_check_with_different_types(self):
        version1 = PackageVersion(1, 2, 3)
        version2 = b"test_bytes"

        assert version1 != version2

    def test_type_check_with_different_types(self):
        version1 = PackageVersion(1, 2, 3)
        version2 = b"test_bytes"

        with pytest.raises(ValueError):
            version1._type_check(version2)
