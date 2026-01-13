import math
import random
import time

import numpy as np

from pytnl.containers import Vector

SIZE_ADD = 1000000
SIZE_DOT = 1000
SIZE_NORM = 100


def get_random_float() -> float:
    return float(random.randint(1, 100))


def create_random_list(size: int) -> list[float]:
    a = [float(i) for i in range(size)]
    for i in range(size):
        a[i] = get_random_float()
    return a


# -----------------------------------
# Comparison of adding of two vectors
# -----------------------------------


def add_comparison(size: int) -> None:
    print("\n" + 50 * "*")
    a = create_random_list(size)
    b = create_random_list(size)

    a_tnl = Vector[float](size)
    b_tnl = Vector[float](size)

    for i in range(size):
        a_tnl.setElement(i, a[i])
        b_tnl.setElement(i, a[i])

    print(f"\nAdding vectors of size {size}:")
    print("Using the same vectors for each approach")

    before_time: float
    result_time: float
    result_times: list[float]

    print("\nIn vanilla python:")
    # adding in python using a for-loop
    c_py = [float(i) for i in range(size)]
    before_time = time.time()
    for i in range(size):
        c_py[i] = a[i] + b[i]
    result_time = time.time() - before_time
    print(f"TIME: {result_time} seconds")

    print("\nUsing TNL library (best time of three):")
    # using inbuilt __add__ method, best of three times
    result_times = []
    for _ in range(3):
        before_time = time.time()
        c_tnl = a_tnl + b_tnl  # noqa: F841
        result_times.append(time.time() - before_time)
    print(f"TIME: {min(result_times)} seconds")

    print("\nUsing numpy (best time of three):")
    # using inbuilt .add method
    result_times = []
    a_np = np.array(a)
    b_np = np.array(b)
    for _ in range(3):
        before_time = time.time()
        c_np = np.add(a_np, b_np)  # noqa: F841
        result_times.append(time.time() - before_time)
    print(f"TIME: {min(result_times)} seconds")
    print("\n" + 50 * "*" + "\n")


# ---------------------------------------
# Comparison of dotproduct of two vectors
# ---------------------------------------


def dot_comparison(size: int) -> None:
    print("\n" + 50 * "*")
    a = create_random_list(size)
    b = create_random_list(size)

    a_tnl = Vector[float](size)
    b_tnl = Vector[float](size)

    for i in range(size):
        a_tnl.setElement(i, a[i])
        b_tnl.setElement(i, a[i])

    print(f"\nDot product vectors of size {size}:")
    print("Using the same vectors for each approach")

    before_time: float
    result_time: float
    result_times: list[float]

    print("\nIn vanilla python:")
    c: float = 0
    before_time = time.time()
    for i in range(size):
        c += a[i] * b[i]
    result_time = time.time() - before_time
    print(f"TIME: {result_time} seconds")

    # TODO update once python implementation of TNL vector dot product is available
    print("\nUsing TNL library (best time of three):")
    # using TNL representation as numpy arrays
    result_times = []
    a_tnl_np = np.from_dlpack(a_tnl)
    b_tnl_np = np.from_dlpack(b_tnl)
    for _ in range(3):
        before_time = time.time()
        np.vecdot(a_tnl_np, b_tnl_np)
        result_times.append(time.time() - before_time)
    print(f"TIME: {min(result_times)} seconds")

    print("\nUsing numpy (best time of three):")
    # using inbuilt .vecdot method
    result_times = []
    a_np = np.array(a)
    b_np = np.array(b)
    for _ in range(3):
        before_time = time.time()
        np.vecdot(a_np, b_np)
        result_times.append(time.time() - before_time)
    print(f"TIME: {min(result_times)} seconds")
    print("\n" + 50 * "*" + "\n")


# ------------------------------------------
# Comparison of normalisation of two vectors
# ------------------------------------------


def norm_comparison(size: int) -> None:
    print("\n" + 50 * "*")
    a = create_random_list(size)
    b = create_random_list(size)

    a_tnl = Vector[float](size)
    b_tnl = Vector[float](size)

    for i in range(size):
        a_tnl.setElement(i, a[i])
        b_tnl.setElement(i, a[i])

    print(f"\nNormalisation of two vectors of size {size}:")
    print("Using the same vectors for each approach")

    before_time: float
    result_time: float
    result_times: list[float]

    print("\nIn vanilla python:")
    before_time = time.time()
    for i in range(size):
        c_res: float = math.sqrt(sum(i * i for i in a))  # noqa: F841
        d_res: float = math.sqrt(sum(i * i for i in b))  # noqa: F841
    result_time = time.time() - before_time
    print(f"TIME: {result_time} seconds")

    # TODO update once python implementation of TNL vector norm is available
    print("\nUsing TNL library (best time of three):")
    # using TNL representation as numpy arrays
    a_tnl_np = np.from_dlpack(a_tnl)
    b_tnl_np = np.from_dlpack(b_tnl)
    result_times = []
    for _ in range(3):
        before_time = time.time()
        np.linalg.vector_norm(a_tnl_np)
        np.linalg.vector_norm(b_tnl_np)
        result_times.append(time.time() - before_time)
    print(f"TIME: {min(result_times)} seconds")

    print("\nUsing numpy (best time of three):")
    # using inbuilt .vector_norm method
    result_times = []
    a_np = np.array(a)
    b_np = np.array(b)
    for _ in range(3):
        before_time = time.time()
        np.linalg.vector_norm(a_np)
        np.linalg.vector_norm(b_np)
        result_times.append(time.time() - before_time)
    print(f"TIME: {min(result_times)} seconds")
    print("\n" + 50 * "*" + "\n")


if __name__ == "__main__":
    print("\nSelect which vector operation you would like to test:")
    oper: str = "start"
    size: int = 0
    while oper != "q":
        oper = input("add(a), dotproduct(d), norm(n), all(A), quit(q): ")
        if oper == "add" or oper == "a":
            size = SIZE_ADD
            size_inp = input(f"Select vector size (enter for default: {SIZE_ADD}): ")
            if size_inp != "":
                size = int(size_inp)
            add_comparison(size)
        elif oper == "dotproduct" or oper == "d":
            size = SIZE_DOT
            size_inp = input(f"Select vector size (enter for default: {SIZE_DOT}): ")
            if size_inp != "":
                size = int(size_inp)
            dot_comparison(size)
        elif oper == "norm" or oper == "n":
            size = SIZE_NORM
            size_inp = input(f"Select vector size (enter for default: {SIZE_NORM}): ")
            if size_inp != "":
                size = int(size_inp)
            norm_comparison(size)
        elif oper == "all" or oper == "A":
            add_comparison(SIZE_ADD)
            dot_comparison(SIZE_DOT)
            norm_comparison(SIZE_NORM)
            break
        elif oper == "quit" or oper == "q":
            break
