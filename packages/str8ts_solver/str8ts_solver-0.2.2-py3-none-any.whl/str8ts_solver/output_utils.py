def _bottom_row_to_string(
    in_row_num: int, row_size: int, blocked: set[tuple[int, int]]
) -> str:
    res = []
    for x_pos in range(row_size):
        if (x_pos, in_row_num) in blocked:
            res.append("###")
        else:
            res.append("   ")
    return "|" + "|".join(res) + "|"


def _top_row_to_string(
    in_row_num: int,
    row_size: int,
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
) -> str:
    res = []
    for x_pos in range(row_size):
        cur_pos = (x_pos, in_row_num)
        if cur_pos in blocked:
            res.append("###")
        elif cur_pos in known:
            res.append("  !")
        else:
            res.append("   ")
    return "|" + "|".join(res) + "|"


def _mid_row_to_string(
    in_row_num: int,
    row_size: int,
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
    solved: dict[tuple[int, int], int],
) -> str:
    res = []
    for x_pos in range(row_size):
        cur_pos = (x_pos, in_row_num)
        if cur_pos in blocked:
            if cur_pos in known:
                res.append(f"#{known[cur_pos]}#")
            else:
                res.append("###")
        else:
            if cur_pos in known:
                res.append(f" {known[cur_pos]} ")
            else:
                res.append(f" {solved.get(cur_pos, ' ')} ")
    return "|" + "|".join(res) + "|"


def _row_to_string(
    in_row_num: int,
    row_size: int,
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
    solved: dict[tuple[int, int], int],
) -> str:
    top_row = _top_row_to_string(in_row_num, row_size, blocked, known)
    mid_row = _mid_row_to_string(in_row_num, row_size, blocked, known, solved)
    bottom_row = _bottom_row_to_string(in_row_num, row_size, blocked)
    return "\n".join((top_row, mid_row, bottom_row))


def _row_separator(in_row_size: int) -> str:
    return str("+---" * in_row_size) + "+"


def to_string(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
    solved: dict[tuple[int, int], int],
) -> str:
    row_separator = _row_separator(size[0])
    res = [row_separator]
    for y_pos in range(size[1]):
        res.append(_row_to_string(y_pos, size[0], blocked, known, solved))
        res.append(row_separator)
    return "\n".join(res)
