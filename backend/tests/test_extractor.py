import pytest

from extractor import extract_text


def test_extract_txt(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello World")
    assert extract_text(str(f)) == "Hello World"


def test_extract_txt_encoding(tmp_path):
    f = tmp_path / "test.txt"
    f.write_bytes("Héllo".encode("utf-8"))
    result = extract_text(str(f))
    assert "llo" in result


def test_unsupported_format(tmp_path):
    f = tmp_path / "test.xyz"
    f.write_text("data")
    with pytest.raises(ValueError, match="Unsupported"):
        extract_text(str(f))


def test_unsupported_no_extension(tmp_path):
    f = tmp_path / "noext"
    f.write_text("data")
    with pytest.raises(ValueError):
        extract_text(str(f))
