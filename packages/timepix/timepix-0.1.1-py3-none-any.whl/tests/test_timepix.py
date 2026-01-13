import time

import pytest
from timepix.core import TimePix
from timepix.exceptions import (
    IncorrectPointTypeError,
    IncorrectPointValueError,
    LastPointNotSetError,
    PointNotFoundError,
)


def test_set_point_without_name():
    tp = TimePix()
    tp.set_point()

    # default point = 0
    assert 0 in tp._TimePix__points


def test_set_point_with_name():
    tp = TimePix()
    tp.set_point('start')

    assert 'start' in tp._TimePix__points


def test_from_point_returns_positive_diff():
    tp = TimePix()
    tp.set_point('a')
    time.sleep(0.01)

    diff = tp.from_point('a', verbose=False)

    assert diff > 0


def test_from_point_rounding():
    tp = TimePix()
    tp.set_point('a')
    time.sleep(0.01)

    diff = tp.from_point('a', round_nums=3, verbose=False)

    assert isinstance(diff, float)
    assert len(str(diff).split('.')[-1]) <= 3


@pytest.mark.parametrize('bad_name', [123, 1.5, [], {}, object()])
def test_set_point_invalid_name_type(bad_name):
    tp = TimePix()

    with pytest.raises(IncorrectPointTypeError):
        tp.set_point(bad_name)


def test_set_point_empty_string():
    tp = TimePix()

    with pytest.raises(IncorrectPointValueError):
        tp.set_point('')


def test_from_point_not_found():
    tp = TimePix()

    with pytest.raises(PointNotFoundError):
        tp.from_point('missing')


def test_from_point_invalid_type():
    tp = TimePix()

    with pytest.raises(IncorrectPointTypeError):
        tp.from_point(123)


def test_from_last_point_works():
    tp = TimePix()
    tp.set_point('a')
    time.sleep(0.01)

    diff = tp.from_last_point(verbose=False)

    assert diff > 0


def test_from_last_point_without_setting():
    tp = TimePix()

    with pytest.raises(LastPointNotSetError):
        tp.from_last_point()


def test_between_points():
    tp = TimePix()
    tp.set_point('a')
    time.sleep(0.01)
    tp.set_point('b')

    diff = tp.between_points('a', 'b', verbose=False)

    assert diff > 0


def test_between_points_not_found():
    tp = TimePix()
    tp.set_point('a')

    with pytest.raises(PointNotFoundError):
        tp.between_points('a', 'b')


@pytest.mark.parametrize('bad_round', [-1, 1.5, '3', None])
def test_invalid_round_nums(bad_round):
    tp = TimePix()
    tp.set_point('a')

    with pytest.raises(ValueError):
        tp.from_point('a', round_nums=bad_round)