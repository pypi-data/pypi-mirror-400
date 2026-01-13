# SuiteSparse-AMD

[![Build and upload to PyPI](https://github.com/Marius-Juston/SuiteSparse/actions/workflows/wheels.yml/badge.svg?event=release)](https://github.com/Marius-Juston/SuiteSparse/actions/workflows/wheels.yml) [![Super-Linter](https://github.com/Marius-Juston/SuiteSparse/actions/workflows/lint.yml/badge.svg)](https://github.com/marketplace/actions/super-linter) [![Python Testing package](https://github.com/Marius-Juston/SuiteSparse/actions/workflows/tests.yml/badge.svg)](https://github.com/Marius-Juston/SuiteSparse/actions/workflows/tests.yml)

This package is the port of the SuiteSparse AMD (Approximate Minimum Degree) function. This is a Python C wrapper of the library from [SuiteSparse](https://github.com/DrTimothyAldenDavis/SuiteSparse).

This package currently only works with Numpy arrays, 2D lists and PyTorch Tensors in the CPU.

## Installation

### PyPi

```bash
pip install suitesparse-amd
```

### Source Installation

```bash
pip install git+https://github.com/Marius-Juston/SuiteSparse.git
```

### Compile Source

```bash
python3 -m build --wheel --sdist
```

## Publish

```bash
bumpver update --tag-commit --patch --push
```
