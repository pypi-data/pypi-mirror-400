import itertools

import z3  # type: ignore

from . import _active_cells_utils as au
from . import _check_solution as cs
from . import _str8ts_utils as su


def _define_unknowns(size: tuple[int, int], blocked: set[tuple[int, int]]):
    return {
        (x_pos, y_pos): z3.Int(f"u_{x_pos}_{y_pos}")
        for x_pos, y_pos in su.gen_unknowns_positions(size, blocked)
    }


def _add_basic_constrains(solver, unknowns, known, value_limit) -> None:
    for pos, unknown in unknowns.items():
        if pos in known:
            solver.add(unknown == known[pos])
        else:
            solver.add(0 < unknown)
            solver.add(unknown <= value_limit)


def _add_constrains_from_blocked(
    solver,
    unknowns,
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
) -> None:
    for blocked_pos in blocked:
        if blocked_pos in known:
            for _ in au.gen_position_in_this_col_row(blocked_pos, size, blocked):
                solver.add(unknowns[_] != known[blocked_pos])


def _add_distinct(solver, values) -> None:
    if len(values) > 1:
        solver.add(z3.Distinct(*values))


def _add_block_constrain(
    solver, unknowns, block: list[tuple[int, int]], block_id: str
) -> None:
    cur_limit = z3.Int(block_id)
    solver.add(cur_limit > 0)
    for _ in block:
        solver.add(cur_limit <= unknowns[_])
        solver.add(unknowns[_] < cur_limit + len(block))
    _add_distinct(solver, [unknowns[_] for _ in block])


def _add_all_block_constrains(solver, unknowns, size: tuple[int, int]) -> None:
    for block_num, cur_block in enumerate(su.gen_horizontal_blocks(size, unknowns)):
        _add_block_constrain(solver, unknowns, cur_block, f"h_{block_num}")

    for block_num, cur_block in enumerate(su.gen_vertical_blocks(size, unknowns)):
        _add_block_constrain(solver, unknowns, cur_block, f"v_{block_num}")


def _add_entries_in_all_rows_are_unique_constrains(
    solver, unknowns, size: tuple[int, int], blocked: set[tuple[int, int]]
):
    for y_pos in range(size[1]):
        _add_distinct(
            solver,
            [unknowns[_] for _ in au.gen_positions_in_row(y_pos, size[0], blocked)],
        )


def _add_entries_in_all_cols_are_unique_constrains(
    solver, unknowns, size: tuple[int, int], blocked: set[tuple[int, int]]
):
    for x_pos in range(size[0]):
        _add_distinct(
            solver,
            [unknowns[_] for _ in au.gen_positions_in_col(x_pos, size[1], blocked)],
        )


def _create_solver(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
):
    solver = z3.Solver()
    unknowns = _define_unknowns(size, blocked)
    _add_basic_constrains(solver, unknowns, known, max(size))
    _add_constrains_from_blocked(solver, unknowns, size, blocked, known)
    _add_all_block_constrains(solver, unknowns, size)
    _add_entries_in_all_cols_are_unique_constrains(solver, unknowns, size, blocked)
    _add_entries_in_all_rows_are_unique_constrains(solver, unknowns, size, blocked)

    return unknowns, solver


def _read_solution(unknowns, solver) -> dict[tuple[int, int], int]:
    model = solver.model()
    return {_: model[unknowns[_]].as_long() for _ in unknowns}


def _is_position_valid(pos: tuple[int, int], size: tuple[int, int]) -> bool:
    return all(0 <= _p < _s for _p, _s in zip(pos, size, strict=True))


def _is_input_valid(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
) -> bool:
    if min(size) <= 0:
        return False
    if not all(_is_position_valid(_, size) for _ in itertools.chain(blocked, known)):
        return False
    if not all(0 < _ <= max(size) for _ in known.values()):
        return False
    return True


def solve(
    size: tuple[int, int],
    blocked: set[tuple[int, int]],
    known: dict[tuple[int, int], int],
) -> dict[tuple[int, int], int] | None:
    if not _is_input_valid(size, blocked, known):
        raise ValueError("Invalid input")
    unknowns, solver = _create_solver(size, blocked, known)
    if solver.check() != z3.sat:
        return None
    solved = _read_solution(unknowns, solver)
    if not cs.is_solution_valid(size, blocked, known, solved):
        raise RuntimeError("Result is incorrect")
    return solved
