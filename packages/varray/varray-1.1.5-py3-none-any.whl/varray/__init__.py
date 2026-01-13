# BSD 3-Clause License; see https://github.com/aaronm6/varray/blob/main/LICENSE
"""
varray (variable array): 

A light-weight array type that supports numpy-like arrays in which the last dimension has
variable length.

Why reinvent the wheel, when awkward (awk) arrays exist?  awk arrays are efficient and versatile
and are an excellent tool when one's needs align with the features they provide.  However, I 
found myself avoiding them in my own work for two reasons:

    1: awk arrays are IMMUTABLE, and hence read-only.  This means they're great to read from,
       but tricky to use if you actually want to use them in a script or notebook.  For
       example, a common usage of numpy arrays is to initialize an empty 2d array with 
       np.empty(...) and then fill in the rows in a loop.  This is possible with numpy
       arrays because they are mutable.  But one cannot do this with awk arrays.  This used 
       to be possible in earlier versions of awk, but this important functionality has since 
       been removed.  This is my main motivation for creating varray: awk arrays' 
       immutability makes them unusable for the vast majority of my own use cases.
    2: awk is a large package that involves c++ code and all of its plethora of functionality
       might not always be needed.  Hence the desire for a light-weight alternative that
       involves python code only.

The focus here is on a simple and light-weight implementation of limited capabilities, 
rather than a breadth of many capabilities.  For example, numpy arrays and ak arrays support 
efficient slicing, where a slice of an array produces a new "view" to the underlying data, 
but does not copy the data.  So too does varray work with array "views".  Data are only 
copied when required.

In addition to creating a varray with the class constructor, one can create a varray with 
one of the numpy-inspired creation functions: empty, ones, and zeros (and 'empty_like', 
etc.), which allocated the space, and then fill in the values later.

Contents:

Class:
    varray : variable-array class. See its docstring for instantiation syntax

Functions:
    empty             : varray creation routine
    empty_like        : varray creation routine
    ones              : varray creation routine
    ones_like         : varray creation routine
    zeros             : varray creation routine
    zeros_like        : varray creation routine
    expand_to_columns : varray creation routine
    reduce_and_fill   : varray creation routine
    save              : save varrays, numpy arrays, numpy masked arrays to *.vrz file
    load              : load items from file that was created by varray.save
    row_concat        : concatenate multiple varrays along the 0th axis
    inner_concat      : concatenate multiple varrays along an inner axis (not 0th, not last)
    inner_stack       : stack multiple arrays along an inner axis (not 0th, not last)

Misc:
    version
    version_tuple
"""
from .varray_class import *
from .varray_creation import *
from .varray_manipulation import *
from ._version import __version__

del varray_class, varray_creation, varray_manipulation

version = __version__
version_tuple = __version_tuple__ = tuple([int(item) for item in __version__.split('.')])
