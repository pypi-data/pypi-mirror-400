"""."""

import pytest

from kinematic_tracker.core.giou_1d import giou_lr_lr


def test_fully_overlap_and_symmetrical() -> None:
    assert giou_lr_lr((-1, 1), (-1, 1)) == pytest.approx(1.0)
    assert giou_lr_lr((-1, 1), (-2, 2)) == pytest.approx(0.75)
    assert giou_lr_lr((-2, 2), (-1, 1)) == pytest.approx(0.75)


def test_zero_len_non_diff_loc() -> None:
    assert giou_lr_lr((1, 1), (2, 2)) == pytest.approx(0.0)


def test_no_overlap_unit_len() -> None:
    assert giou_lr_lr((1, 2), (3, 4)) == pytest.approx(0.3333333333333333)


def test_no_overlap_len_1_0() -> None:
    assert giou_lr_lr((1, 2), (3, 3)) == pytest.approx(0.25)


def test_no_overlap() -> None:
    assert giou_lr_lr((2, 1), (4, 3)) == pytest.approx(0.0)
