import itertools
import typing


def gen_unknowns_positions(
    size: tuple[int, int], blocked: set[tuple[int, int]]
) -> typing.Iterable[tuple[int, int]]:
    for _ in itertools.product(range(size[0]), range(size[1])):
        if _ not in blocked:
            yield _


def _shift(pos: tuple[int, int], shift: tuple[int, int]) -> tuple[int, int]:
    r_x, r_y = tuple(sum(_) for _ in zip(pos, shift, strict=True))
    return r_x, r_y


def _extract_block(
    unknowns, pos: tuple[int, int], direction: tuple[int, int]
) -> list[tuple[int, int]]:
    res = []
    cur_pos = pos
    while cur_pos in unknowns:
        res.append(cur_pos)
        cur_pos = _shift(cur_pos, direction)
    return res


def gen_horizontal_blocks(
    size: tuple[int, int], unknowns
) -> typing.Iterable[list[tuple[int, int]]]:
    for y_pos in range(size[1]):
        x_pos = 0
        while x_pos < size[0]:
            if (x_pos, y_pos) in unknowns:
                cur_block = _extract_block(unknowns, (x_pos, y_pos), (1, 0))
                if len(cur_block) > 1:
                    yield cur_block
                x_pos += len(cur_block)
            else:
                x_pos += 1


def gen_vertical_blocks(
    size: tuple[int, int], unknowns
) -> typing.Iterable[list[tuple[int, int]]]:
    for x_pos in range(size[0]):
        y_pos = 0
        while y_pos < size[1]:
            if (x_pos, y_pos) in unknowns:
                cur_block = _extract_block(unknowns, (x_pos, y_pos), (0, 1))
                if len(cur_block) > 1:
                    yield cur_block
                y_pos += len(cur_block)
            else:
                y_pos += 1
