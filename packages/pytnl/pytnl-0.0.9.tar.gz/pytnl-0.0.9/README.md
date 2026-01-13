# PyTNL

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

## Highlights

TNL (and therefore PyTNL where bindings exist) provides building blocks such as:

- CPU/GPU-aware data structures and memory utilities
- parallel primitives (iteration patterns, reductions, scans)
- linear algebra foundations (templated vectors, dense and sparse matrices,
  sparse data formats (segments))
- iterative linear solvers and preconditioners (CG, BiCGStab, GMRES, Jacobi, etc.)
- ODE solvers (Euler, Fehlberg, Kutta, Heun, Runge-Kutta-Merson, Matlab, etc.)
- structured grid and unstructured mesh data structures (including distributed)
  and utilities, including import from FPMA, Netgen, VTK, VTU and PVTU formats

## Documentation

PyTNL documentation (including installation instructions) is hosted on GitLab
Pages: <https://tnl-project.gitlab.io/pytnl/>

## License

PyTNL is provided under the terms of the [MIT License](./LICENSE).
