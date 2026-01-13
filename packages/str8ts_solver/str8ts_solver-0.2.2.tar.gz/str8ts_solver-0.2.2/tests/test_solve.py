import pytest

from str8ts_solver.solver import solve

from . import samples


def _extract_test_case(
    sample: samples.Sample,
) -> tuple[
    tuple[int, int],
    set[tuple[int, int]],
    dict[tuple[int, int], int],
    dict[tuple[int, int], int] | None,
]:
    return sample.size, sample.blocked, sample.known, sample.solved


@pytest.mark.parametrize(
    ("size", "blocked", "known", "expected"),
    [
        _extract_test_case(samples.SAMPLE_1),
        _extract_test_case(samples.SAMPLE_2),
        _extract_test_case(samples.SAMPLE_3),
        _extract_test_case(samples.NO_SOLUTION),
        _extract_test_case(samples.SAMPLE_3_BY_2),
        _extract_test_case(samples.FULLY_BLOCKED_COLUMN),
        _extract_test_case(samples.FULLY_BLOCKED),
    ],
)
def test_solve(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
    expected: dict[tuple[int, int], int] | None,
) -> None:
    assert solve(size, blocked, known) == expected


@pytest.mark.parametrize(
    ("size", "blocked", "known"),
    [
        ((-1, 5), set(), {}),
        ((3, 4), {(100, 1)}, {}),
        ((3, 4), set(), {(3, 0): 1}),
        ((3, 4), set(), {(0, 0): 1000}),
        ((3, 4), set(), {(0, 0): 0}),
    ],
)
def test_solve_raises_for_wrong_input(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
) -> None:
    with pytest.raises(ValueError, match="Invalid input"):
        solve(size, blocked, known)
