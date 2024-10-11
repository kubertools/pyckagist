from pyckagist import main, PackageManagerBuilder


def test_builder():
    assert isinstance(main.builder(), PackageManagerBuilder)
