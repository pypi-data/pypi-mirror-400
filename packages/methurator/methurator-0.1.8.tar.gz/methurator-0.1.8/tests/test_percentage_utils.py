import pytest
import rich_click as click
from methurator.config_utils.validation_utils import percentage_checker


def test_valid_percentages_adds_one():
    result = percentage_checker("0.5, 0.2, 0.2, 0.1")
    assert result == [0.5, 0.2, 0.2, 0.1, 1]


def test_valid_percentages_with_one_present():
    result = percentage_checker("0.7, 0.2, 0.1, 1")
    assert result == [0.7, 0.2, 0.1, 1]  # no extra 1 added


def test_fails_if_any_zero():
    with pytest.raises(click.UsageError):
        percentage_checker("0.5, 0, 0.3, 0.2")


def test_fails_if_less_than_four_values():
    with pytest.raises(click.UsageError):
        percentage_checker("0.5, 0.3, 0.2")


def test_strips_whitespace_correctly():
    result = percentage_checker(" 0.4 , 0.3 ,0.2 ,0.1 ")
    assert result == [0.4, 0.3, 0.2, 0.1, 1]
