import pytest

from termcolours.lib.m_utils.printing import num_to_fg_ansi


def test_hex_string_with_hash():
    result = num_to_fg_ansi("#ff0000")
    assert result == "\x1b[38;2;255;0;0m"


def test_hex_string_without_hash():
    result = num_to_fg_ansi("00ff00")
    assert result == "\x1b[38;2;0;255;0m"


def test_hex_string_with_0x():
    result = num_to_fg_ansi("0x0000ff")
    assert result == "\x1b[38;2;0;0;255m"


def test_int_input():
    result = num_to_fg_ansi(0xff00ff)
    assert result == "\x1b[38;2;255;0;255m"


def test_with_rgb_dec_true():
    result, rgb = num_to_fg_ansi("#112233", with_rgb_dec=True)
    assert result == "\x1b[38;2;17;34;51m"
    assert rgb == (17, 34, 51)


def test_background_code():
    result = num_to_fg_ansi("#ffffff", fgbg=48)
    assert result == "\x1b[48;2;255;255;255m"


@pytest.mark.parametrize(
    "color",
    [
        "fff",
        "12345",
        "1234567",
        "gg0000",
        "",
        "red",
    ],
)
def test_invalid_hex_inputs(color):
    with pytest.raises(ValueError):
        num_to_fg_ansi("gg0000")


def test_invalid_type_raises_type_error():
    with pytest.raises(TypeError):
        num_to_fg_ansi(["ff0000"])
