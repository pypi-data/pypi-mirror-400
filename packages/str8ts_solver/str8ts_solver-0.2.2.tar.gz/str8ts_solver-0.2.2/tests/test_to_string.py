import pytest

from str8ts_solver.output_utils import to_string

from . import samples


def _extract_test_case_blank(
    sample: samples.Sample,
) -> tuple[
    tuple[int, int],
    set[tuple[int, int]],
    dict[tuple[int, int], int],
    str,
]:
    return sample.size, sample.blocked, sample.known, sample.blank_str


@pytest.mark.parametrize(
    ("size", "blocked", "known", "expected"),
    [
        _extract_test_case_blank(samples.SAMPLE_1),
        _extract_test_case_blank(samples.SAMPLE_2),
        _extract_test_case_blank(samples.SAMPLE_3),
        _extract_test_case_blank(samples.NO_SOLUTION),
        _extract_test_case_blank(samples.SAMPLE_3_BY_2),
        _extract_test_case_blank(samples.FULLY_BLOCKED_COLUMN),
        _extract_test_case_blank(samples.FULLY_BLOCKED),
    ],
)
def test_to_string_with_blank(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
    expected: str,
) -> None:
    assert to_string(size, blocked, known, {}) == expected


def _extract_test_case_solved(
    sample: samples.Sample,
) -> tuple[
    tuple[int, int],
    set[tuple[int, int]],
    dict[tuple[int, int], int],
    dict[tuple[int, int], int],
    str,
]:
    assert sample.solved is not None
    assert sample.solved_str is not None
    return sample.size, sample.blocked, sample.known, sample.solved, sample.solved_str


@pytest.mark.parametrize(
    ("size", "blocked", "known", "solved", "expected"),
    [
        _extract_test_case_solved(samples.SAMPLE_1),
        _extract_test_case_solved(samples.SAMPLE_2),
        _extract_test_case_solved(samples.SAMPLE_3),
        _extract_test_case_solved(samples.SAMPLE_3_BY_2),
        _extract_test_case_solved(samples.FULLY_BLOCKED_COLUMN),
        _extract_test_case_solved(samples.FULLY_BLOCKED),
    ],
)
def test_to_string_with_solved(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
    solved: dict[tuple[int, int], int],
    expected: str,
) -> None:
    assert to_string(size, blocked, known, solved) == expected
