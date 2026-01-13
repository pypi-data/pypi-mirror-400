"""This module is deprecated; do not use in new projects!"""

import warnings
from mmgroup import mm_op

warnings.warn("Module mmgroup.mm255 is deprecated! " 
    "Replace function 'op_<xxx>(*args)' in this module by function "
    "'mm_op_<xxx>(255, *args)' in module mmgroup.mm_op!",
    UserWarning)

def op_pi(*args, **kwds):
    return mm_op.mm_op_pi(255, *args, **kwds)

def op_copy(*args, **kwds):
    return mm_op.mm_op_copy(255, *args, **kwds)

def op_compare_len(*args, **kwds):
    return mm_op.mm_op_compare_len(255, *args, **kwds)

def op_compare(*args, **kwds):
    return mm_op.mm_op_compare(255, *args, **kwds)

def op_checkzero(*args, **kwds):
    return mm_op.mm_op_checkzero(255, *args, **kwds)

def op_vector_add(*args, **kwds):
    return mm_op.mm_op_vector_add(255, *args, **kwds)

def op_scalar_mul(*args, **kwds):
    return mm_op.mm_op_scalar_mul(255, *args, **kwds)

def op_compare_mod_q(*args, **kwds):
    return mm_op.mm_op_compare_mod_q(255, *args, **kwds)

def op_store_axis(*args, **kwds):
    return mm_op.mm_op_store_axis(255, *args, **kwds)

def op_xy(*args, **kwds):
    return mm_op.mm_op_xy(255, *args, **kwds)

def op_omega(*args, **kwds):
    return mm_op.mm_op_omega(255, *args, **kwds)

def op_t_A(*args, **kwds):
    return mm_op.mm_op_t_A(255, *args, **kwds)

def op_word(*args, **kwds):
    return mm_op.mm_op_word(255, *args, **kwds)

def op_word_tag_A(*args, **kwds):
    return mm_op.mm_op_word_tag_A(255, *args, **kwds)

def op_word_ABC(*args, **kwds):
    return mm_op.mm_op_word_ABC(255, *args, **kwds)

