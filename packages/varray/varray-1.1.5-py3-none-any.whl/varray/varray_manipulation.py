# BSD 3-Clause License; see https://github.com/aaronm6/varray/blob/main/LICENSE

import numpy as np
from .varray_class import *

__all__ = [
    'row_concat',
    'inner_concat',
    'inner_stack']

def row_concat(varray_list, *, dtype=None, casting='same_kind'):
    """
    row_concatenate((va1, va2, ...), dtype=None, casting='same_kind')
    Concatenate two or more varrays along their first axis.
    
    Returns varray.
    
    For example, if
        va1 = varray([[1 2]
                      [3 4 5]], dtype=int64)
    and
        va2 = varray([[6]
                      [7 8]], dtype=int64)
    then
        row_concatenate((va1, va2)) is
           varray([[1 2]
                   [3 4 5]
                   [6]
                   [7 8]], dtype=int64)
    """
    inner_dims = [item.shape[1:-1] for item in varray_list]
    if len(set(inner_dims)) > 1:
        raise ValueError("All varrays must have compatible shapes for the concatenation along given axis")
    new_darray = np.concatenate([item.flatten() for item in varray_list], axis=-1, casting=casting)
    new_sarray = np.concatenate([item.sarray for item in varray_list], dtype=np.uint16)
    return varray(darray=new_darray, sarray=new_sarray, dtype=dtype)

def inner_concat(varray_list, /, axis=0, *, dtype=None, casting='same_kind'):
    """
    inner_concat((va1, va2, ...), axis=0, dtype=None, casting='same_kind')
    
    Concatenate the inner arrays along an axis.  The inner arrays are defined as the dimensions
    between the first last elements of va1.shape.  For example, 
    >>> va.zeros([4,6], inner_shape=(2,3))
    varray([[[[0. 0. 0. 0.]
              [0. 0. 0. 0.]
              [0. 0. 0. 0.]]
            
             [[0. 0. 0. 0.]
              [0. 0. 0. 0.]
              [0. 0. 0. 0.]]]
    
    
            [[[0. 0. 0. 0. 0. 0.]
              [0. 0. 0. 0. 0. 0.]
              [0. 0. 0. 0. 0. 0.]]
            
             [[0. 0. 0. 0. 0. 0.]
              [0. 0. 0. 0. 0. 0.]
              [0. 0. 0. 0. 0. 0.]]]], dtype=float64)
    This has two 'rows', with shape (2,3,4) and (2,3,6).  So the inner arrays are these two 3d 
    arrays.  
    
    ** Cannot concatenate along the last dimension, as this is the variable-length one. **
    
    This is most useful for example
    >>> va1 = va.zeros([4,6])
    >>> va1
    varray([[0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0.]], dtype=float64)
    >>> va2 = va.ones([4,6])
    >>> va2
    varray([[1. 1. 1. 1.]
            [1. 1. 1. 1. 1. 1.]], dtype=float64)
    >>> va12 = va.inner_concat([va1, va2])
    >>> va12
    varray([[[0. 0. 0. 0.]
             [1. 1. 1. 1.]]
    
            [[0. 0. 0. 0. 0. 0.]
             [1. 1. 1. 1. 1. 1.]]], dtype=float64)
    va1 could be recovered, for example, by slicing:
    >>> va12[:,0,:]
    varray([[0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0.]], dtype=float64)
    """
    if axis==0:
        raise ValueError("Axis must be one of the inner dimensions, not zero.  To concatenate " + \
            "along the zero'th axis, use row_concat")
    if not all([isinstance(item, varray) for item in varray_list]):
        raise TypeError("Items in list must be varray objects")
    if len(set([len(item) for item in varray_list])) != 1:
        raise ValueError("inner_concat can only be performed on varrays of the same length")
    ndims = np.array([item.ndim for item in varray_list])
    if axis >= ndims.min():
        raise ValueError("Axis must be one of the inner dimensions.")
    darray_shapes_2d = [item._darray.shape for item in varray_list]
    darray_shapes_2d = [list((1,)+item) if len(item)==1 else list(item) for item in darray_shapes_2d]
    for item in darray_shapes_2d:
        item.pop(index=-1)
    if len(set(darray_shapes_2d))>1:
        raise ValueError("varray inner dimensions must be compatible with requested concat")
    if not all([np.all(item._sarray == varray_list[0]._sarray) for item in varray_list[1:]]):
        raise ValueError("Items in list of varrays must have the same sarray")
    new_darray = np.concatenate([np.atleast_2d(item.flatten()) for item in varray_list], 
        axis=(axis-1), dtype=dtype, casting=casting)
    new_sarray = varray_list[0].sarray
    return varray(darray=new_darray, sarray=new_sarray)

def inner_stack(varray_list, /, axis=0, *, dtype=None, casting='same_kind'):
    """
    inner_stack((va1, va2, ...), axis=0, dtype=None, casting='same_kind')
    
    inner stack: stack two or more varrays along a new inner dimension.  In order to do
    an inner stack, the shapes and sarrays of all listed varrays must be the same.
    """
    # need to do error checking, but here is the code assuming things are valid
    if axis==0:
        raise ValueError("Axis must be one of the inner dimensions, not zero.")
    if len(set([item.shape for item in varray_list])) > 1:
        raise ValueError("All listed varrays must have the same shape")
    if not all([np.all(item.sarray==varray_list[0].sarray) for item in varray_list[1:]]):
        raise ValueError("All sarrays must be the same")
    new_darray = np.stack([item.flatten() for item in varray_list],
        axis=(axis-1), dtype=dtype, casting=casting)
    new_sarray = varray_list[0].sarray
    return varray(darray=new_darray, sarray=new_sarray)

