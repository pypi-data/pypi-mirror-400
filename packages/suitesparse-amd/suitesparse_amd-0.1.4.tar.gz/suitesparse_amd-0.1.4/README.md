# SuiteSparse-AMD

[![Build and upload to PyPI](https://github.com/Marius-Juston/SuiteSparse/actions/workflows/wheels.yml/badge.svg?event=release)](https://github.com/Marius-Juston/SuiteSparse/actions/workflows/wheels.yml)

This package is the port of the SuiteSparse AMD (Approximate Minimum Degree) function. This is a Python C wrapper of the library from [SuiteSparse](https://github.com/DrTimothyAldenDavis/SuiteSparse).

This package currently only works with Numpy arrays and 2D lists.

## Future

- Work with PyTorch CPU Tensors

# Installation

## PyPi

```bash
pip install suitesparse-amd
```

## Source Installation

```bash
pip install git+https://github.com/Marius-Juston/SuiteSparse.git
```

## Compile Source

```bash
python3 -m build --wheel --sdist
```

# Publish

```bash
bumpver update --tag-commit --patch --push
```