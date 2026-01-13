import pytest
import rich_click as click
from methurator.config_utils.validation_utils import mincoverage_checker


def test_valid_coverages():
    assert mincoverage_checker("10,5,3") == [10, 5, 3]


def test_values_with_spaces():
    assert mincoverage_checker(" 8 , 4 , 2 ") == [8, 4, 2]


def test_zero_values_are_ignored(monkeypatch):
    # Capture verbose warning output
    messages = []

    def fake_vprint(msg, verbose):
        messages.append(msg)

    monkeypatch.setattr("methurator.config_utils.verbose_utils.vprint", fake_vprint)

    result = mincoverage_checker("5,0,3,0,2")
    assert result == [5, 3, 2]


@pytest.mark.parametrize("bad_value", ["a", "3.5", "-2", "abc"])
def test_invalid_values_raise_exception(bad_value):
    with pytest.raises(click.UsageError):
        mincoverage_checker(f"5,{bad_value},3")


def test_only_zero_values_returns_empty_list(monkeypatch):
    monkeypatch.setattr(
        "methurator.config_utils.verbose_utils.vprint", lambda *args, **kwargs: None
    )
    assert mincoverage_checker("0,0,0") == []
