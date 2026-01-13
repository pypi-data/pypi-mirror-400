import itertools
import typing


def gen_positions_in_row(
    row_num: int, col_len: int, blocked: set[tuple[int, int]]
) -> typing.Iterator[tuple[int, int]]:
    return ((_, row_num) for _ in range(col_len) if (_, row_num) not in blocked)


def gen_positions_in_col(
    col_num: int, row_len: int, blocked: set[tuple[int, int]]
) -> typing.Iterator[tuple[int, int]]:
    return ((col_num, _) for _ in range(row_len) if (col_num, _) not in blocked)


def gen_position_in_this_col_row(
    pos: tuple[int, int], size: tuple[int, int], blocked: set[tuple[int, int]]
):
    return itertools.chain(
        gen_positions_in_row(pos[1], size[0], blocked),
        gen_positions_in_col(pos[0], size[1], blocked),
    )
