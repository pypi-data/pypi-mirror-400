import copy
import os
import tempfile
from collections.abc import Collection
from typing import TypeVar

import numpy as np
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

import pytnl._containers
import pytnl.containers

# ----------------------
# Configuration
# ----------------------

# Type variable constraining the array types
A = TypeVar(
    "A",
    pytnl._containers.Array_int,
    pytnl._containers.Array_float,
    pytnl._containers.Array_complex,
    pytnl._containers.Vector_int,
    pytnl._containers.Vector_float,
    pytnl._containers.Vector_complex,
)

# Type variable constraining the array view types
AV = TypeVar(
    "AV",
    pytnl._containers.ArrayView_int,
    pytnl._containers.ArrayView_float,
    pytnl._containers.ArrayView_complex,
    pytnl._containers.VectorView_int,
    pytnl._containers.VectorView_float,
    pytnl._containers.VectorView_complex,
)

# Type variable constraining the const array view types
CAV = TypeVar(
    "CAV",
    pytnl._containers.ArrayView_int_const,
    pytnl._containers.ArrayView_float_const,
    pytnl._containers.ArrayView_complex_const,
    pytnl._containers.VectorView_int_const,
    pytnl._containers.VectorView_float_const,
    pytnl._containers.VectorView_complex_const,
)

# List of array types to test
array_types = A.__constraints__
array_and_const_view_types = zip(array_types + array_types, AV.__constraints__ + CAV.__constraints__)


# ----------------------
# Helper Functions
# ----------------------


def create_array(data: Collection[int | float | complex], array_type: type[A]) -> A:
    """Create an array of the given type from a list of values."""
    v = array_type(len(data))
    for i, val in enumerate(data):
        v[i] = val  # type: ignore[assignment]
    return v


# ----------------------
# Hypothesis Strategies
# ----------------------


def element_strategy(array_type: type[A]) -> st.SearchStrategy[int | float | complex]:
    """Return appropriate data strategy for the given array type."""
    if array_type.ValueType is int:
        # lower limits because C++ uses int64_t for IndexType
        return st.integers(min_value=-(2**63), max_value=2**63 - 1)
    elif array_type.ValueType is float:
        return st.floats(allow_nan=False, allow_infinity=False)
    else:
        return st.complex_numbers(allow_nan=False, allow_infinity=False)


@st.composite
def array_strategy(draw: st.DrawFn, array_type: type[A]) -> A:
    """Generate an array of the given type."""
    data = draw(st.lists(element_strategy(array_type), max_size=20))
    return create_array(data, array_type)


@st.composite
def list_pair_strategy(draw: st.DrawFn, array_type: type[A]) -> tuple[list[int | float | complex], list[int | float | complex]]:
    """
    Generate two lists of the same size containing elements of the same type,
    ensuring that a pair of two identical lists is generated.
    """
    size = draw(st.integers(min_value=0, max_value=20))
    data1 = draw(st.lists(element_strategy(array_type), max_size=size))

    if draw(st.booleans()):
        return data1, data1

    data2 = draw(st.lists(element_strategy(array_type), min_size=size, max_size=size))
    return data1, data2


# ----------------------
# Constructors and basic properties
# ----------------------


def test_pythonization() -> None:
    assert pytnl.containers.Array[bool] is pytnl._containers.Array_bool
    assert pytnl.containers.Array[int] is pytnl._containers.Array_int
    assert pytnl.containers.Array[float] is pytnl._containers.Array_float
    assert pytnl.containers.Array[complex] is pytnl._containers.Array_complex
    assert pytnl.containers.Vector[int] is pytnl._containers.Vector_int
    assert pytnl.containers.Vector[float] is pytnl._containers.Vector_float
    assert pytnl.containers.Vector[complex] is pytnl._containers.Vector_complex


def test_typedefs() -> None:
    for array_type in array_types:
        assert array_type.IndexType is int

    assert pytnl.containers.Array[bool].ValueType is bool
    assert pytnl.containers.Array[int].ValueType is int
    assert pytnl.containers.Array[float].ValueType is float
    assert pytnl.containers.Array[complex].ValueType is complex

    assert pytnl.containers.Vector[int].ValueType is int
    assert pytnl.containers.Vector[float].ValueType is float
    assert pytnl.containers.Vector[complex].ValueType is complex


@pytest.mark.parametrize("array_type", array_types)
def test_constructors(array_type: type[A]) -> None:
    v1 = array_type()
    assert v1.getSize() == 0

    v2 = array_type(10)
    assert v2.getSize() == 10

    value = 3.14 if array_type.ValueType is float else 3
    v3 = array_type(5, value)  # type: ignore[arg-type]
    assert v3.getSize() == 5
    for i in range(5):
        assert v3[i] == value

    with pytest.raises(ValueError):
        array_type(-1)


@pytest.mark.parametrize("array_type, view_type", array_and_const_view_types)
def test_view_constructors(array_type: type[A], view_type: type[CAV]) -> None:
    value = 3.14 if array_type.ValueType is float else 3
    v1 = array_type(5, value)  # type: ignore[arg-type]
    assert v1.getSize() == 5

    v2 = view_type(v1)  # type: ignore[call-overload]
    assert v2.getSize() == 5
    assert v2[0] == value

    v3 = view_type(v2)  # pyright: ignore[reportArgumentType,reportCallIssue]
    assert v3.getSize() == 5
    assert v3[0] == value


# ----------------------
# Size management
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
@given(size=st.integers(min_value=0, max_value=20))
def test_setSize(array_type: type[A], size: int) -> None:
    v = array_type()
    v.setSize(size)
    assert v.getSize() == size


@pytest.mark.parametrize("array_type", array_types)
@given(size=st.integers(min_value=-20, max_value=-1))
def test_setSize_negative(array_type: type[A], size: int) -> None:
    v = array_type()
    with pytest.raises(ValueError):
        v.setSize(size)


@pytest.mark.parametrize("array_type", array_types)
@given(size=st.integers(min_value=0, max_value=20))
def test_resize(array_type: type[A], size: int) -> None:
    v = array_type()
    v.resize(size)
    assert v.getSize() == size


@pytest.mark.parametrize("array_type", array_types)
@given(size=st.integers(min_value=-20, max_value=-1))
def test_resize_negative(array_type: type[A], size: int) -> None:
    v = array_type()
    with pytest.raises(ValueError):
        v.resize(size)


@pytest.mark.parametrize("array_type", array_types)
@given(size=st.integers(min_value=0, max_value=20), value=st.integers(min_value=-(2**63), max_value=2**63 - 1))
def test_resize_with_value(array_type: type[A], size: int, value: int | float | complex) -> None:
    if array_type.ValueType is float:
        assert not isinstance(value, complex)
        value = float(value)
    elif array_type.ValueType is complex:
        value = complex(value)
    v = array_type()
    v.resize(size, value)  # type: ignore[arg-type]
    assert v.getSize() == size
    for i in range(size):
        assert v[i] == value


@pytest.mark.parametrize("array_type", array_types)
def test_swap(array_type: type[A]) -> None:
    array1 = array_type(5, 1)
    view1 = array1.getView()
    array2 = array_type(10, 2)
    view2 = array2.getConstView()
    array1.swap(array2)
    # arrays are swapped
    assert array1.getSize() == 10
    assert array2.getSize() == 5
    # views are not swapped
    assert view1 == array2
    assert view1.getSize() == 5
    assert view2 == array1
    assert view2.getSize() == 10

    # swap views
    view3 = array1.getView()
    view3.swap(view1)  # pyright: ignore[reportArgumentType]
    assert view3 == array2
    assert view1 == array1

    # cannot swap const view with non-const
    const_view3 = array2.getConstView()
    with pytest.raises(TypeError):
        view3.swap(const_view3)  # type: ignore[arg-type]


@pytest.mark.parametrize("array_type", array_types)
def test_reset(array_type: type[A]) -> None:
    array = array_type(10)
    view = array.getView()
    assert view.getSize() == 10
    view.reset()
    assert view.getSize() == 0
    assert array.getSize() == 10
    array.reset()
    assert array.getSize() == 0


@pytest.mark.parametrize("array_type, view_type", array_and_const_view_types)
def test_empty(array_type: type[A], view_type: type[CAV]) -> None:
    array = array_type()
    assert array.empty()
    array.setSize(1)
    assert not array.empty()

    view = view_type()
    assert view.empty()
    view.bind(array)  # type: ignore[arg-type]
    assert not view.empty()


# ----------------------
# Data access
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
@given(data=st.data())
def test_set_get_element(array_type: type[A], data: st.DataObject) -> None:
    elements = data.draw(st.lists(element_strategy(array_type), min_size=0, max_size=20))
    array = create_array(elements, array_type)
    view = array.getView()
    const_view = array.getConstView()

    for i in range(len(elements)):
        assert array[i] == elements[i]
        assert array.getElement(i) == elements[i]
        assert view[i] == elements[i]
        assert view.getElement(i) == elements[i]
        assert const_view[i] == elements[i]
        assert const_view.getElement(i) == elements[i]

        array.setElement(i, 1)
        assert array[i] == 1
        assert array.getElement(i) == 1
        assert view[i] == 1
        assert view.getElement(i) == 1
        assert const_view[i] == 1
        assert const_view.getElement(i) == 1

        array[i] = 2
        assert array[i] == 2
        assert array.getElement(i) == 2
        assert view[i] == 2
        assert view.getElement(i) == 2
        assert const_view[i] == 2
        assert const_view.getElement(i) == 2

        view.setElement(i, 3)
        assert array[i] == 3
        assert array.getElement(i) == 3
        assert view[i] == 3
        assert view.getElement(i) == 3
        assert const_view[i] == 3
        assert const_view.getElement(i) == 3

        view[i] = 4
        assert array[i] == 4
        assert array.getElement(i) == 4
        assert view[i] == 4
        assert view.getElement(i) == 4
        assert const_view[i] == 4
        assert const_view.getElement(i) == 4

        with pytest.raises(TypeError):
            const_view.setElement(i, 5)
        with pytest.raises(TypeError):
            const_view[i] = 5


@pytest.mark.parametrize("array_type", array_types)
def test_out_of_bounds_access(array_type: type[A]) -> None:
    v = array_type(1)
    with pytest.raises(IndexError):
        v[-1]
    with pytest.raises(IndexError):
        v.getElement(-1)
    with pytest.raises(IndexError):
        v.setElement(-1, 0)
    with pytest.raises(IndexError):
        v[1]
    with pytest.raises(IndexError):
        v.getElement(1)
    with pytest.raises(IndexError):
        v.setElement(1, 0)


@pytest.mark.parametrize("array_type", array_types)
@given(
    data=st.data(),
    size=st.integers(min_value=0, max_value=20),
    start=st.integers(min_value=0, max_value=10),
    stop=st.integers(min_value=0, max_value=20),
    step=st.integers(min_value=1, max_value=5),
)
def test_slicing(array_type: type[A], data: st.DataObject, size: int, start: int, stop: int, step: int) -> None:
    assume(start < stop)
    elements = data.draw(st.lists(element_strategy(array_type), min_size=size, max_size=size))
    array = create_array(elements, array_type)
    slice_ = slice(start, stop, step)
    expected = elements[slice_]

    result = array[slice_]
    assert result.getSize() == len(expected)
    for i in range(result.getSize()):
        assert result[i] == expected[i]

    # TODO: slicing is not implemented for views yet
    # view = array.getView()
    # result_view = view[slice_]
    # assert result_view.getSize() == len(expected)
    # for i in range(result_view.getSize()):
    #    assert result_view[i] == expected[i]


# ----------------------
# Assignment
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
@given(data=st.data())
def test_assign(array_type: type[A], data: st.DataObject) -> None:
    array1 = data.draw(array_strategy(array_type))
    array2 = array_type()
    array2.assign(array1)
    assert array2.getSize() == array1.getSize()
    for i in range(array1.getSize()):
        assert array2[i] == array1[i]

    # assign to view
    array3 = array_type(array1.getSize())
    view3 = array3.getView()
    view3.assign(array1)  # type: ignore[arg-type]
    assert view3.getSize() == array1.getSize()
    for i in range(array1.getSize()):
        assert view3[i] == array1[i]

    # cannot assign to const view
    const_view = array3.getConstView()
    with pytest.raises(TypeError):
        const_view.assign(array1)  # type: ignore[arg-type]


# ----------------------
# Comparison operators
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
@given(data=st.data())
def test_comparison_operators(array_type: type[A], data: st.DataObject) -> None:
    elements1, elements2 = data.draw(list_pair_strategy(array_type))

    # array vs array
    array1 = create_array(elements1, array_type)
    array2 = create_array(elements2, array_type)
    assert (array1 == array2) == (elements1 == elements2)
    assert (array1 != array2) == (elements1 != elements2)

    # view vs view
    view1 = array1.getView()
    view2 = array2.getView()
    assert (view1 == view2) == (elements1 == elements2)
    assert (view1 != view2) == (elements1 != elements2)

    # const view vs const view
    const_view1 = view1.getConstView()
    const_view2 = view2.getConstView()
    assert (const_view1 == const_view2) == (elements1 == elements2)
    assert (const_view1 != const_view2) == (elements1 != elements2)

    # array vs view
    assert (array1 == view2) == (elements1 == elements2)
    assert (array1 != view2) == (elements1 != elements2)
    assert (view1 == array2) == (elements1 == elements2)
    assert (view1 != array2) == (elements1 != elements2)

    # array vs const view
    assert (array1 == const_view2) == (elements1 == elements2)
    assert (array1 != const_view2) == (elements1 != elements2)
    assert (const_view1 == array2) == (elements1 == elements2)
    assert (const_view1 != array2) == (elements1 != elements2)

    # view vs const view
    # FIXME: nanobind *returns* the NotImplemented value from `nb::self == nb::self`
    # assert (view1 == const_view2) == (elements1 == elements2)
    # assert (view1 != const_view2) == (elements1 != elements2)
    # assert (const_view1 == view2) == (elements1 == elements2)
    # assert (const_view1 != view2) == (elements1 != elements2)


# ----------------------
# Fill (setValue)
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
@given(
    data=st.data(),
    size=st.integers(min_value=0, max_value=20),
    begin=st.integers(min_value=0, max_value=20),
    end=st.integers(min_value=0, max_value=20),
)
def test_setValue(array_type: type[A], data: st.DataObject, size: int, begin: int, end: int) -> None:
    assume(begin <= end <= size)
    elements = data.draw(st.lists(element_strategy(array_type), min_size=size, max_size=size))
    value = data.draw(element_strategy(array_type))

    array = create_array(elements, array_type)
    array.setValue(value, begin, end)  # type: ignore[arg-type]
    # adjust according to C++ behavior
    if end == 0:
        end = size
    for i in range(size):
        if begin <= i < end:
            assert array[i] == value
        else:
            assert array[i] == elements[i]

    # set through view
    value = data.draw(element_strategy(array_type))
    view = array.getView()
    view.setValue(value, begin, end)  # type: ignore[arg-type]
    for i in range(size):
        if begin <= i < end:
            assert array[i] == value
        else:
            assert array[i] == elements[i]

    # cannot set through const view
    const_view = view.getConstView()
    with pytest.raises(TypeError):
        const_view.setValue(value, begin, end)  # type: ignore[arg-type]


# ----------------------
# File I/O
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
def test_serialization_type(array_type: type[A]) -> None:
    assert array_type.getSerializationType().startswith("TNL::Containers::Array<")


@pytest.mark.parametrize("array_type", array_types)
@given(data=st.data())
def test_save_load(array_type: type[A], data: st.DataObject) -> None:
    # Unfortunately functions-scoped fixtures like tmp_path do not work with Hypothesis
    # https://hypothesis.readthedocs.io/en/latest/reference/api.html#hypothesis.HealthCheck.function_scoped_fixture
    # Create a temporary file that will not be deleted automatically
    with tempfile.NamedTemporaryFile(mode="w+b", delete=False) as tmpfile:
        filename = tmpfile.name

    try:
        v1 = data.draw(array_strategy(array_type))
        v1.save(str(filename))
        v2 = array_type()
        v2.load(str(filename))
        assert v2.getSize() == v1.getSize()
        for i in range(v1.getSize()):
            assert v2[i] == v1[i]

    finally:
        # Ensure the file is deleted after the test
        os.unlink(filename)


# ----------------------
# String representation
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
def test_str(array_type: type[A]) -> None:
    array = array_type(5)
    for i in range(5):
        array[i] = i
    s = str(array)
    assert isinstance(s, str)
    assert len(s) > 0
    for i in range(5):
        assert str(i) in s

    view = array.getView()
    s_view = str(view)
    assert s_view == s


# ----------------------
# Deepcopy support
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
@given(data=st.data())
def test_copy(array_type: type[A], data: st.DataObject) -> None:
    v = data.draw(array_strategy(array_type))
    v_copy = copy.copy(v)
    assert v == v_copy
    if v.getSize() > 0:
        if array_type.ValueType is int:
            v_copy[0] = -v_copy[0] - 1  # pyright: ignore[reportArgumentType, reportCallIssue]
        else:
            v_copy[0] = -v_copy[0] or 1  # pyright: ignore[reportArgumentType, reportCallIssue]
        assert v_copy != v


@pytest.mark.parametrize("array_type", array_types)
@given(data=st.data())
def test_deepcopy(array_type: type[A], data: st.DataObject) -> None:
    v = data.draw(array_strategy(array_type))
    v_copy = copy.deepcopy(v)
    assert v == v_copy
    if v.getSize() > 0:
        if array_type.ValueType is int:
            v_copy[0] = -v_copy[0] - 1  # pyright: ignore[reportArgumentType, reportCallIssue]
        else:
            v_copy[0] = -v_copy[0] or 1  # pyright: ignore[reportArgumentType, reportCallIssue]
        assert v_copy != v


# ----------------------
# DLPack protocol (NumPy interoperability)
# ----------------------


@pytest.mark.parametrize("array_type", array_types)
@given(data=st.data())
def test_dlpack(array_type: type[A], data: st.DataObject) -> None:
    """
    Tests interoperability with NumPy using the DLPack API.

    Verifies:
    - The returned NumPy array has the correct shape and dtype.
    - The array contains the same data as the Array.
    - The underlying memory is shared.
    - Changes in NumPy are reflected in the Array and vice versa.
    """

    # Create and initialize the Array
    array = data.draw(array_strategy(array_type))
    assume(array.getSize() > 1)
    dims = (array.getSize(),)

    # Convert to NumPy array
    array_np = np.from_dlpack(array)

    # Check that the array is writable
    assert array_np.flags.writeable

    # Check shape
    assert array_np.shape == dims, f"Expected shape {dims}, got {array_np.shape}"

    # Check data type
    if array_type.ValueType is int:
        assert array_np.dtype == np.int_, f"Expected dtype {np.int_}, got {array_np.dtype}"
    elif array_type.ValueType is float:
        assert array_np.dtype == np.float64, f"Expected dtype {np.float64}, got {array_np.dtype}"
    else:
        assert array_np.dtype == np.complex128, f"Expected dtype {np.complex128}, got {array_np.dtype}"

    # Check element-wise equality
    assert np.all(array_np == list(array)), "Data mismatch in NumPy array"

    # Modify NumPy array and verify Array reflects the change
    array_np.flat[0] = 99
    assert array[0] == 99, "NumPy array modification not reflected in Array"

    # Modify Array and verify NumPy array reflects the change
    array[1] = 77
    assert array_np.flat[1] == 77, "Array modification not reflected in NumPy array"

    # Check that memory is shared
    assert np.shares_memory(array_np, np.from_dlpack(array)), "Memory should be shared between two NumPy arrays"

    # Get NumPy array from view
    view = array.getView()
    view_np = np.from_dlpack(view)
    assert view_np.flags.writeable
    assert view_np.shape == dims, f"Expected shape {dims}, got {view_np.shape}"
    assert view_np.dtype == array_np.dtype
    assert np.all(view_np == list(array)), "Data mismatch in NumPy array from view"

    # Get NumPy array from const view
    const_view = array.getConstView()
    const_view_np = np.from_dlpack(const_view)
    assert not const_view_np.flags.writeable
    assert const_view_np.shape == dims, f"Expected shape {dims}, got {const_view_np.shape}"
    assert const_view_np.dtype == array_np.dtype
    assert np.all(const_view_np == list(array)), "Data mismatch in NumPy array from const view"
