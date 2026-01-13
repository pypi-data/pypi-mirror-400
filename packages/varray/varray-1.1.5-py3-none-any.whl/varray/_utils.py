# BSD 3-Clause License; see https://github.com/aaronm6/varray/blob/main/LICENSE

import numpy as np

__all__ = [
    'r_explore_nesting',
    'unpack_nested_list',
    'unpack_masked_array',
    'expand_slices',
    'repr_precision_context']

def r_explore_nesting(nested_list, depth=0):
    """
    Check that the nesting of an iterable is good, i.e. the depth is the same for all elements
    
    If nesting is good: returns depth.  
    If nesting is bad: raises ValueError
    
        A non-nested list (i.e. [1,2,3]) has depth of 1.
        A singly-nested list (i.e. [[1,2],[3],[4,5,6]]) has depth of 2
        etc.
    If nesting is bad: raises ValueError
        Bad nesting means that all elements are not the same depth. For example,
        [ [1,2], [[3,4],[5,6]] ] is bad because the first element is a non-nested list,
        but the second element is a singly-nested list.
        [[1,2],3,[4,5,6]] is bad nesting
    This function uses recursion; in order to prevent runaway recursion, the function
    raises a RecursionError if the depth of recursion is more than 10.
    """
    if depth > 10:
        raise RecursionError("Depth is too big; recursion is going nuts")
    if hasattr(nested_list, '__len__'):
        if len(nested_list) == 0:
            return None
        depths = [r_explore_nesting(item, depth=depth+1) for item in nested_list]
        if len(set((item for item in depths if item))) > 1:
            raise ValueError("Nesting is bad")
        else:
            return depths[0]
    else:
        return depth

def unpack_nested_list(nested_list):
    """
    Take a nested list and return a [possibly multidimensional] darray and sarray
    """
    darray = np.array([item for sublist in nested_list for item in sublist])
    darray_ndim = darray.ndim
    re_pose = [(item+1)%darray_ndim for item in range(darray_ndim)]
    darray = darray.transpose(*re_pose)
    sarray = np.array([len(item) for item in nested_list], dtype=np.int16)
    return darray, sarray

def unpack_masked_array(ma_obj):
    """
    Take a masked array and turn it into a darray and sarray
    """
    ndim = ma_obj.ndim
    ma_shape = ma_obj.shape
    final_init_dims = ma_shape[1:-1]
    transpose_list = [(item+1)%(ndim-1) for item in range(ndim-1)] + [ndim-1]
    transpose_tuple = tuple(transpose_list)
    ma_manipulated = ma_obj.transpose(transpose_tuple).reshape(*final_init_dims,-1)
    ma_notmask = ~ma_manipulated.mask
    final_slice = (0,)*(ma_manipulated.ndim-1) + (slice(None,None,None),)
    d_array = ma_manipulated.data[...,ma_notmask[final_slice]]
    s_array_item = (slice(None,None,None),)+(0,)*(ndim-2)+(slice(None,None,None),)
    s_array = (~ma_obj.mask[(slice(None,None,None),)+(0,)*(ndim-2)+(slice(None,None,None),)]).sum(axis=-1)
    if not np.issubdtype(s_array.dtype, np.dtype('int16')):
        s_array = s_array.astype(np.int16)
    return d_array, s_array

def expand_slices(item, varray_dims):
    """
    Takes an item passed to __getitem__ and expands it to be a full tuple of indices.
    
    For example, if the varray has 4 dimensions and [...,1,:] is given,
    this needs to be expanded to [:,:,1,:]
    or if [0] is given, this needs to be expanded to [0,:,:,:]
    This function does that.
    
    Inputs:
               item: raw item received in __getitem__
        varray_dims: the number of dimensions of the varray, which will be one more than
                     the number of dimensions of its darray.
    Output:
           new_item: A drop-in replacement that has expanded the raw item.
    """
    s_full = slice(None, None, None) # full slice
    if not isinstance(item, tuple):
        item = (item,)
    if len(item) > varray_dims:
        raise IndexError("Too many indices given")
    #if item.count(Ellipsis) > 1: # <-- doesn't work if numpy array in item
    Ellipsis_count = [1 for el in item if el is Ellipsis]
    if len(Ellipsis_count) > 1:
        raise IndexError("An index can only have a single ellipsis ('...')")
    if Ellipsis_count:
        #idx = item.index(Ellipsis) # <-- doesn't work if numpy array in item
        idx, = [yy for xx,yy in zip(item,range(len(item))) if xx is Ellipsis]
        return item[:idx] + (s_full,)*(varray_dims-len(item)+1) + item[(idx+1):]
    if len(item) == varray_dims:
        return item
    return item + (s_full,)*(varray_dims-len(item))

class repr_precision_context:
    def __init__(self, **kwargs):
        self.current_settings = np.get_printoptions()
        self.new_settings = kwargs
        for item in kwargs:
            if item not in self.current_settings:
                raise KeyError(f"Setting '{item}' not listed in np.get_printoptions")
    def __enter__(self):
        np.set_printoptions(**self.new_settings)
    def __exit__(self, thetype, thevalue, thetraceback):
        modified_originals = {key:self.current_settings[key] for key in self.new_settings}
        np.set_printoptions(**modified_originals)