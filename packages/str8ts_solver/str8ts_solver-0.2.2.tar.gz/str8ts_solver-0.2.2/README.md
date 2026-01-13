# About `str8ts_solver`

[![PyPI version](https://badge.fury.io/py/str8ts_solver.svg)](https://pypi.org/project/str8ts_solver/)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=vil02_str8ts_solver&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=vil02_str8ts_solver)
[![codecov](https://codecov.io/gh/vil02/str8ts_solver/graph/badge.svg?token=SWO6HG0D91)](https://codecov.io/gh/vil02/str8ts_solver)
[![CodeFactor](https://www.codefactor.io/repository/github/vil02/str8ts_solver/badge)](https://www.codefactor.io/repository/github/vil02/str8ts_solver)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/446f49b571ab4797a29039fbb8a6bfbe)](https://app.codacy.com/gh/vil02/str8ts_solver/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/vil02/str8ts_solver/badge)](https://securityscorecards.dev/viewer/?uri=github.com/vil02/str8ts_solver)

[Str8ts](https://en.wikipedia.org/wiki/Str8ts) solver using [z3](https://github.com/Z3Prover/z3).

## Getting started

This package is available at [PyPI](https://pypi.org/project/str8ts_solver/).
It can be installed using the command

```shell
pip install str8ts_solver
```
The [`examples`](./examples) directory contains scripts showing basic usage of this package.

## Information for developers

This project is setup using [`uv`](https://docs.astral.sh/uv/).
In order to create a _development environment_,
after cloning this repository, run the command like:

```shell
uv pip install --editable .
```

[`tests`](./tests) are expressed using [`pytest`](https://docs.pytest.org/).

## References

- [Str8ts](https://www.str8ts.com/)
- [Z3 Theorem Prover](https://en.wikipedia.org/wiki/Z3_Theorem_Prover)
