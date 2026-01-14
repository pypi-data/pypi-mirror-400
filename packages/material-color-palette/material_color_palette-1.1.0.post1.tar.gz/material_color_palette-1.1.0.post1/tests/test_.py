"""The tests module."""

import pytest

from material_color_palette import Color


def test_construct_color() -> None:
    """`Color` can be constructed from `name` and `shade` string."""
    # arrange
    # act
    c = Color("red", "700")
    # assert
    assert c.rgb == (211, 47, 47)
    assert c.name == "red"
    assert c.shade == 700
    assert c.hex == "#d32f2f"


def test_construct_color__int_shade() -> None:
    """`Color` can be constructed from `name` and `shade` int."""
    # arrange
    # act
    c = Color("pink", 900)
    # assert
    assert c.rgb == (136, 14, 79)
    assert c.name == "pink"
    assert c.shade == 900
    assert c.hex == "#880e4f"


def test_construct_color__spaces_in_name() -> None:
    """`Color` can be constructed from `name` including spaces."""
    # arrange
    # act
    c0 = Color("deep purple", 300)
    c1 = Color("deep_purple", 300)

    # assert
    assert c0 == c1


def test_construct_color__color_only() -> None:
    """`Color` can be constructed from `name` alone for some values."""
    # arrange
    # act
    c0 = Color("black")
    c1 = Color("white")
    # assert
    assert c0.rgb == (0, 0, 0)
    assert c0.name == "black"
    assert c0.shade is None
    assert c0.hex == "#000000"
    assert c1.rgb == (255, 255, 255)
    assert c1.name == "white"
    assert c1.shade is None
    assert c1.hex == "#ffffff"


def test_construct_color__missing_shade_raises_exception() -> None:
    """When `Color` can't be constructed from `name` alone, exception is raised."""
    # arrange
    # act, assert
    with pytest.raises(
        ValueError, match=r"Shade must be specified for Material color 'lime'."
    ):
        Color("lime")


def test_construct_color__incorrect_name_raises_exception() -> None:
    """When `name` isn't valid, exception is raised."""
    # arrange
    # act, assert
    with pytest.raises(
        ValueError, match=r"'dark_blue' isn't a valid Material color name."
    ):
        Color("dark_blue", "300")


def test_construct_color__incorrect_shade_raises_exception() -> None:
    """When `shade` isn't valid for `name`, exception is raised."""
    # arrange
    # act, assert
    with pytest.raises(
        ValueError, match=r"'250' isn't a valid shade for Material color 'blue_gray'."
    ):
        Color("blue_gray", "250")
