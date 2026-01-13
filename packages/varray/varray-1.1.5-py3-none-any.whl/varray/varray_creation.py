# BSD 3-Clause License; see https://github.com/aaronm6/varray/blob/main/LICENSE

import numpy as np
from numbers import Number
from .varray_class import *
from .varray_class import _rowops_reduce

__all__ = [
    'empty',
    'ones',
    'zeros',
    'full',
    'empty_like',
    'ones_like',
    'zeros_like',
    'full_like',
    'expand_to_columns',
    'reduce_and_fill']

def empty(sarray, /, inner_shape=(), *, dtype=np.float64):
    """
    Create a new varray with the specified shape and dtype.  The data array is
    initialized via numpy.empty
    
    Parameters
    ----------
    sarray : 1d numpy array of dtype int
        The array of row lengths
    inner_shape : a tuple containing the inner dimensions.  For example, if each "row" of the
        varray (i.e. accessed by va_1[0,...]) is a 2d numpy array with 4 rows and N columns
        (where N is the 0th element of sarray), then inner_shape=(4,).  Put another way, it 
        is the shape of a row of the varray, but with the last element of the shape removed.
    dtype : data type, optional
        The data type of the data values contained in the varray.
    
    Returns
    -------
    new_varray : varray
        A new empty array of the specified shape and dtype.
    """
    if not isinstance(sarray, np.ndarray):
        sarray = np.array(sarray)
    if not all([np.issubdtype(type(item), np.integer) for item in inner_shape]):
        raise TypeError("All elements of inner_shape must be ints")
    if not isinstance(dtype, type):
        raise TypeError("Specified dtype must be a type instance")
    shape_tuple = inner_shape + (sarray.sum(),)
    darray = np.empty(shape_tuple, dtype=dtype)
    return varray(darray=darray, sarray=sarray, dtype=dtype)

def ones(sarray, /, inner_shape=(), *, dtype=np.float64):
    """
    Create a new varray with the specified shape and dtype.  The data array is
    initialized via numpy.ones
    
    Parameters
    ----------
    sarray : 1d numpy array of dtype int
        The array of row lengths
    inner_shape : a tuple containing the inner dimensions.  For example, if each "row" of the
        varray (i.e. accessed by va_1[0,...]) is a 2d numpy array with 4 rows and N columns
        (where N is the 0th element of sarray), then inner_shape=(4,).  Put another way, it 
        is the shape of a row of the varray, but with the last element of the shape removed.
    dtype : data type, optional
        The data type of the data values contained in the varray.
    
    Returns
    -------
    new_varray : varray
        A new ones array of the specified shape and dtype.
    """
    if not isinstance(sarray, np.ndarray):
        sarray = np.array(sarray)
    if not all([np.issubdtype(type(item), np.integer) for item in inner_shape]):
        raise TypeError("All elements of inner_shape must be ints")
    if not isinstance(dtype, type):
        raise TypeError("Specified dtype must be a type instance")
    shape_tuple = inner_shape + (sarray.sum(),)
    darray = np.ones(shape_tuple, dtype=dtype)
    return varray(darray=darray, sarray=sarray, dtype=dtype)

def zeros(sarray, /, inner_shape=(), *, dtype=np.float64):
    """
    Create a new varray with the specified shape and dtype.  The data array is
    initialized via numpy.zeros
    
    Parameters
    ----------
    sarray : 1d numpy array of dtype int
        The array of row lengths
    inner_shape : a tuple containing the inner dimensions.  For example, if each "row" of the
        varray (i.e. accessed by va_1[0,...]) is a 2d numpy array with 4 rows and N columns
        (where N is the 0th element of sarray), then inner_shape=(4,).  Put another way, it 
        is the shape of a row of the varray, but with the last element of the shape removed.
    dtype : data type, optional
        The data type of the data values contained in the varray.
    
    Returns
    -------
    new_varray : varray
        A new empty array of the specified shape and dtype.
    """
    if not isinstance(sarray, np.ndarray):
        sarray = np.array(sarray)
    if not all([np.issubdtype(type(item), np.integer) for item in inner_shape]):
        raise TypeError("All elements of inner_shape must be ints")
    if not isinstance(dtype, type):
        raise TypeError("Specified dtype must be a type instance")
    shape_tuple = inner_shape + (sarray.sum(),)
    darray = np.zeros(shape_tuple, dtype=dtype)
    return varray(darray=darray, sarray=sarray, dtype=dtype)

def full(sarray, fill_value, /, inner_shape=(), *, dtype=np.float64):
    """
    Create a new varray with the specified shape and dtype.  The data array is
    initialized via numpy.empty
    
    Parameters
    ----------
    sarray : 1d numpy array of dtype int
        The array of row lengths
    fill_value : The value that will be initialized in every element of the array
    inner_shape : a tuple containing the inner dimensions.  For example, if each "row" of the
        varray (i.e. accessed by va_1[0,...]) is a 2d numpy array with 4 rows and N columns
        (where N is the 0th element of sarray), then inner_shape=(4,).  Put another way, it 
        is the shape of a row of the varray, but with the last element of the shape removed.
    dtype : data type, optional
        The data type of the data values contained in the varray.
    
    Returns
    -------
    new_varray : varray
        A new empty array of the specified shape and dtype.
    """
    if not isinstance(sarray, np.ndarray):
        sarray = np.array(sarray)
    if not isinstance(fill_value, Number):
        raise TypeError("Input 'fill_value' must be a valid number")
    if not all([np.issubdtype(type(item), np.integer) for item in inner_shape]):
        raise TypeError("All elements of inner_shape must be ints")
    if not isinstance(dtype, type):
        raise TypeError("Specified dtype must be a type instance")
    shape_tuple = inner_shape + (sarray.sum(),)
    darray = np.empty(shape_tuple, dtype=dtype)
    return varray(darray=darray, sarray=sarray, dtype=dtype)

def empty_like(v_obj, dtype=None):
    """
    Create a new varray with the same shape as the prototype provided
    
    Parameters
    ----------
    v_obj : varray
        A prototype varray object.  The new object that is created will have the
        same size and dtype (unless otherwise specified) as v_obj.
    dtype : data type, optional
    
    Returns
    -------
    new_varray : varray
        A new empty array of the same shape as the provided v_obj
    """
    if not isinstance(v_obj, varray):
        raise TypeError("Provided object must be a varray")
    if not (isinstance(dtype, type) or (dtype is None)):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.empty_like(v_obj.flatten(), dtype=dtype)
    return varray(darray=darray, sarray=v_obj.sarray)

def ones_like(v_obj, dtype=None):
    """
    Create a new varray with the same shape as the prototype provided
    
    Parameters
    ----------
    v_obj : varray
        A prototype varray object.  The new object that is created will have the
        same size and dtype (unless otherwise specified) as v_obj.
    dtype : data type, optional
    
    Returns
    -------
    new_varray : varray
        A new empty array of the same shape as the provided v_obj
    """
    if not isinstance(v_obj, varray):
        raise TypeError("Provided object must be a varray")
    if not (isinstance(dtype, type) or (dtype is None)):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.ones_like(v_obj.flatten(), dtype=dtype)
    return varray(darray=darray, sarray=v_obj.sarray)

def zeros_like(v_obj, dtype=None):
    """
    Create a new varray with the same shape as the prototype provided
    
    Parameters
    ----------
    v_obj : varray
        A prototype varray object.  The new object that is created will have the
        same size and dtype (unless otherwise specified) as v_obj.
    dtype : data type, optional
    
    Returns
    -------
    new_varray : varray
        A new empty array of the same shape as the provided v_obj
    """
    if not isinstance(v_obj, varray):
        raise TypeError("Provided object must be a varray")
    if not (isinstance(dtype, type) or (dtype is None)):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.zeros_like(v_obj.flatten(), dtype=dtype)
    return varray(darray=darray, sarray=v_obj.sarray)

def full_like(v_obj, fill_value, dtype=None):
    """
    Create a new varray with the same shape as the prototype provided
    
    Parameters
    ----------
    v_obj : varray
        A prototype varray object.  The new object that is created will have the
        same size and dtype (unless otherwise specified) as v_obj.
    fill_value : value to insert into each element of the new array
    dtype : data type, optional
    
    Returns
    -------
    new_varray : varray
        A new empty array of the same shape as the provided v_obj
    """
    if not isinstance(v_obj, varray):
        raise TypeError("Provided object must be a varray")
    if not isinstance(fill_value, Number):
        raise TypeError("fill_value must be a valid number")
    if not (isinstance(dtype, type) or (dtype is None)):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.full_like(v_obj.flatten(), fill_value, dtype=dtype)
    return varray(darray=darray, sarray=v_obj.sarray)

def expand_to_columns(init_array, sarray=None, dtype=None):
    """
    Take a numpy array whose elements represent the first value in each row of a
    varray and expands that value to all elements of the row.  For example, if one
    wanted to produce the varray
    
    varray([[8, 8, 8]
            [3, 3]
            [2, 2, 2, 2]], dtype=int64)
    
    then this can be produced with this function, by:
    
    >>> init_array = np.array([8, 3, 2], dtype=np.int64)
    >>> sarray = np.array([3, 2, 4])
    >>> v_new = expand_to_columns(init_array, sarray=sarray)
    
    This works as well for varrays with more than 2 dimensions.  In those cases,
    the init_array given must have the same number of dimensions as the flattened
    varray.  The last dimension of init_array must be the same length as the sarray,
    and the preceding N-1 dimensions must be the same size as the same N-1 dimensions
    of the flattened array.  For example, if one has a 4d varray, va4, of shape 
    (4, 2, 3, None) and shape array [2, 3, 1, 4], then then va4.flatten() will have
    shape (2, 3, 10).  To reproduce an array of the same shape with expand_to_columns
    one needs to give it an init_array of shape (2, 3, 4) -- (2, 3, ...) because 
    those are the inner dimensions of the to-be-created varray, and (..., 4) because
    the sarray has 4 elements, and hence the varray will have 4 rows.
    
    This function is vaguely analogous to np.broadcast_to for regular arrays (though
    usage is of course different).  In principle, this could be generalized to allow
    init_array to be broadcast up to larger dimensions if needed, by that's a level
    of complexity that I don't feel like implementing at the moment.
    
    This function will not work if any elements in init_array are equal to the maximum
    possible value for the desired dtype.
    """
    init_array = np.asarray(init_array) # if asarray throws an exception, this will propagate here
    if sarray is None:
        raise ValueError("sarray must be given as a numpy array or sequence that can be cast as a numpy array")
    new_sarray = np.asarray(sarray, np.uint16)
    if new_sarray.ndim != 1:
        raise ValueError("The given sarray must be 1d")
    init_shape = init_array.shape
    if (init_shape[-1] != len(new_sarray)):
        raise ValueError("The last dimension of init_array must have the same length as sarray")
    
    num_cols = new_sarray.sum()
    if dtype is None:
        dtype = init_array.dtype
    
    max_val = 10
    if np.issubdtype(dtype, np.integer):
        max_val = np.iinfo(dtype).max
    elif np.issubdtype(dtype, np.floating):
        max_val = np.finfo(dtype).max
    if max_val == 10:
        raise TypeError("The provided dtype is neither integer nor floating and this won't work")
    
    ufill_func = np.frompyfunc(lambda x, y: x if y==max_val else y, 2, 1)
    
    tag_array = np.full(init_array.shape[:-1] + (num_cols,), max_val, dtype=dtype)
    csarray = np.r_[0, new_sarray[:-1].astype(np.uint32)].cumsum()
    csarray = csarray[csarray<tag_array.shape[-1]]
    tag_array[..., csarray] = init_array[...,:len(csarray)]
    new_darray = ufill_func.accumulate(tag_array, axis=-1).astype(dtype)
    
    return varray(darray=new_darray, sarray=new_sarray)

def reduce_and_fill(va_in, func_name='max', dtype=None):
    """
    Apply a reduction function (like max or sum) to the last axis of a varray, then
    expand that result to the full size of the varray.  For example, if one started
    with the varray:
    
    >>> va1
    varray([[6 7]
            [8 0 5]
            [5]
            [6 9 7 2]], dtype=int64)
    
    then the max applied to the last dimension is [7, 8, 5, 9].  This function expands
    that as
    
    >>> va.reduce_and_fill(va1, func_name='max')
    varray([[7 7]
        [8 8 8]
        [5]
        [9 9 9 9]], dtype=int64)
    
    Positional argument 'va_in' must be a varray.  Keyword argument 'func_name' must be
    a valid reduction function.
    """
    if not isinstance(va_in, varray):
        raise TypeError("Positional argument 'va_in' must be an intance of varray")
    if func_name not in _rowops_reduce:
        from pprint import pformat
        err_str = "func_name must be a str and a valid reduce function.  The available reduce functions are:\n"
        err_str += pformat(_rowops_reduce)
        raise ValueError(err_str)
    
    reduced_varr = getattr(va_in, func_name)(axis=-1)
    ndim = reduced_varr.ndim
    r_dims = tuple(range(ndim))
    transpose_tup = r_dims[1:] + (r_dims[0],)
    return expand_to_columns(reduced_varr.transpose(transpose_tup), sarray=va_in.sarray, dtype=dtype)





















