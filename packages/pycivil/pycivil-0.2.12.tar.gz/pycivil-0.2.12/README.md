# pycivil

A project that aims to make structural engineers free as possible from commercial software.

## Features

1. Solver (package *RCRecSolver*) for check rectangular reinforced concrete section under bending,
    axial and shear forces.
2. Solver (package *RCGenSolver*) for check generic reinforced concrete section under bending,
    axial and shear forcee.
3. Solver and checker are compliant with codes:
    1. European EC2
    2. Italian NTC2008, NTC2018
4. Code base for codes (package *lawcodes*) with rules, strenght formulas, loads and materials
5. Section shapes object models for calculations (*RectangularShape*, *TShape*, ...) with
6. Report system LaTex based, for cheat sheets and solvers
7. Agnostic Finite Element Modeler (package *EXAStructuralModel*)

## Prerequisites

1. LaTex installation (if you need build reports)
2. Docker Engine (useful if you need generate thermal map)

## News

### Version 0.2.6

1. New features in FEAModel as support on frames and load combinations

### Version 0.2.0

1. You can use pip install pycivil
2. Module xstrumodeler for generic shape RC section is a requirement
3. Start to remove sws-mind backend to separate module
4. Added new tool (post-processor) for Strand7

## Docs

You can run `task docs` and will start a local server with documentation. 
Sorry, but most of it is still being written. I suggest you start with the tests

## Development

- Install [task](https://taskfile.dev/installation/)
- run `task init` do initialize the python environment and install the pre-commit hooks
- before committing code changes, you can run `task` to perform automated checks. You can also run them separately:
    - `task lint` fixes and checks the code and documentation
    - `task mypy` performs type checking
    - `task test` runs the tests with `pytest`
    - `task security` scans the dependencies for known vulnerabilities

> **NOTE**: the `lint` task is executed automatically when you commit the changes to ensure that only good quality code is added to the repository.


### Docker container

If you're a docker-compose guy, you can run the [docker-compose.yml](docker-compose.yml) file with:

```shell
docker-compose up --build
```

This will also create Code_Aster containers and you will be able to use Code_Aster as FEM solver.

#### Remove all volumes

This remove all volumes and data. Next relaunch the volumes will be build

```shell
docker-compose down -v
```
