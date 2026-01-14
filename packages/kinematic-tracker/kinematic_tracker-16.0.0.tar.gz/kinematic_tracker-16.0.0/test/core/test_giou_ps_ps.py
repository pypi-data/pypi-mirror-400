"""."""

import pytest

from kinematic_tracker.core.giou_1d import giou_ps_ps


def test_full_overlap() -> None:
    assert giou_ps_ps((0, 2), (0, 2)) == pytest.approx(1.0)


def test_symmetrical() -> None:
    assert giou_ps_ps((0, 2), (0, 4)) == pytest.approx(0.75)
    assert giou_ps_ps((0, 4), (0, 2)) == pytest.approx(0.75)


def test_zero_len_non_diff_loc() -> None:
    assert giou_ps_ps((1, 0), (2, 0)) == pytest.approx(0.0)


def test_no_overlap_unit_len() -> None:
    assert giou_ps_ps((1.5, 1.0), (3.5, 1.0)) == pytest.approx(0.3333333333333333)


def test_no_overlap_len_1_0() -> None:
    assert giou_ps_ps((1.5, 1), (3, 0)) == pytest.approx(0.25)
