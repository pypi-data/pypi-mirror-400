# Welcome to PyTNL

**PyTNL** provides Python bindings for the [Template Numerical Library (TNL)](
https://tnl-project.org/) — a modern C++ library for building efficient
numerical solvers and HPC algorithms.

TNL targets **multicore CPUs**, **GPUs** (CUDA and ROCm/HIP) and
**distributed-memory systems** (MPI) behind a unified programming model.
PyTNL exposes selected TNL building blocks to Python, enabling Python-driven
workflows while keeping performance-critical kernels in compiled backends.

## Scope

PyTNL is intended for:

- interoperability with TNL components where Python bindings are available,
- prototyping and orchestration of numerical solvers or HPC workflows,
- combining Python ergonomics with native code performance characteristics.

The exact set of exported classes and functions may evolve over time.
