import itertools

from . import _active_cells_utils as au
from . import _str8ts_utils as su


def _non_blocked_known_are_same_as_in_solved(
    known: dict[tuple[int, int], int], solved: dict[tuple[int, int], int]
) -> bool:
    return all(solved[_] == known[_] for _ in solved if _ in known)


def _is_valid_str8ts_block(values: list[int]) -> bool:
    values_set = set(values)
    return len(values_set) == len(values) and values_set == set(
        range(min(values), max(values) + 1)
    )


def _elements_in_blocks_are_distinct_and_consecutive(
    size: tuple[int, int],
    solved: dict[tuple[int, int], int],
) -> bool:
    return all(
        _is_valid_str8ts_block([solved[_] for _ in cur_block])
        for cur_block in itertools.chain(
            su.gen_horizontal_blocks(size, solved), su.gen_vertical_blocks(size, solved)
        )
    )


def _elements_in_row_are_distinct(
    row_num: int,
    row_len: int,
    blocked: set[tuple[int, int]],
    solved: dict[tuple[int, int], int],
) -> bool:
    values = [solved[_] for _ in au.gen_positions_in_row(row_num, row_len, blocked)]
    return len(set(values)) == len(values)


def _elements_in_every_row_are_distinct(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    solved: dict[tuple[int, int], int],
) -> bool:
    return all(
        _elements_in_row_are_distinct(_, size[0], blocked, solved)
        for _ in range(size[1])
    )


def _elements_in_column_are_distinct(
    col_num: int,
    col_len: int,
    blocked: set[tuple[int, int]],
    solved: dict[tuple[int, int], int],
) -> bool:
    values = [solved[_] for _ in au.gen_positions_in_col(col_num, col_len, blocked)]
    return len(set(values)) == len(values)


def _elements_in_every_column_are_distinct(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    solved: dict[tuple[int, int], int],
) -> bool:
    return all(
        _elements_in_column_are_distinct(_, size[1], blocked, solved)
        for _ in range(size[0])
    )


def _solved_are_different_than_known_blocked(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
    solved: dict[tuple[int, int], int],
) -> bool:
    return all(
        all(
            solved[_] != known[blocked_pos]
            for _ in au.gen_position_in_this_col_row(blocked_pos, size, blocked)
        )
        for blocked_pos in blocked & set(known)
    )


def _all_values_are_in_range(size: tuple[int, int], solved: dict[tuple[int, int], int]):
    return all(0 < _ <= max(size) for _ in solved.values())


def _all_unknowns_are_solved(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    solved: dict[tuple[int, int], int],
) -> bool:
    return all(_ in solved for _ in su.gen_unknowns_positions(size, blocked))


def is_solution_valid(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
    solved: dict[tuple[int, int], int],
) -> bool:
    return (
        _non_blocked_known_are_same_as_in_solved(known, solved)
        and _all_values_are_in_range(size, solved)
        and _all_unknowns_are_solved(size, blocked, solved)
        and _solved_are_different_than_known_blocked(size, blocked, known, solved)
        and _elements_in_blocks_are_distinct_and_consecutive(size, solved)
        and _elements_in_every_column_are_distinct(size, blocked, solved)
        and _elements_in_every_row_are_distinct(size, blocked, solved)
    )
