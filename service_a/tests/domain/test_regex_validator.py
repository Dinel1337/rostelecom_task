import pytest
from src.domain.regex_validator import SerialRegex

def test_valid_serial():
    sn = SerialRegex("ABC123")
    assert sn.value == "ABC123"

def test_valid_serial_lowercase():
    sn = SerialRegex("abcdef")
    assert sn.value == "abcdef"

def test_valid_serial_mixed():
    sn = SerialRegex("aB1cD2")
    assert sn.value == "aB1cD2"

def test_invalid_serial_too_short():
    with pytest.raises(ValueError, match="Неверное серийное что-то: AB12"):
        SerialRegex("AB12")

def test_invalid_serial_with_dash():
    with pytest.raises(ValueError):
        SerialRegex("ABC-123")

def test_invalid_serial_with_space():
    with pytest.raises(ValueError):
        SerialRegex("ABC 123")

def test_invalid_serial_cyrillic():
    with pytest.raises(ValueError):
        SerialRegex("АБС123")
