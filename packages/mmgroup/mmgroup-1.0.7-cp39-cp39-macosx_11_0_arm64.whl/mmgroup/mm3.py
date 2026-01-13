"""This module is deprecated; do not use in new projects!"""

import warnings
from mmgroup import mm_op

warnings.warn("Module mmgroup.mm3 is deprecated! " 
    "Replace function 'op_<xxx>(*args)' in this module by function "
    "'mm_op_<xxx>(3, *args)' in module mmgroup.mm_op!",
    UserWarning)

def op_pi(*args, **kwds):
    return mm_op.mm_op_pi(3, *args, **kwds)

def op_copy(*args, **kwds):
    return mm_op.mm_op_copy(3, *args, **kwds)

def op_compare_len(*args, **kwds):
    return mm_op.mm_op_compare_len(3, *args, **kwds)

def op_compare(*args, **kwds):
    return mm_op.mm_op_compare(3, *args, **kwds)

def op_checkzero(*args, **kwds):
    return mm_op.mm_op_checkzero(3, *args, **kwds)

def op_vector_add(*args, **kwds):
    return mm_op.mm_op_vector_add(3, *args, **kwds)

def op_scalar_mul(*args, **kwds):
    return mm_op.mm_op_scalar_mul(3, *args, **kwds)

def op_compare_mod_q(*args, **kwds):
    return mm_op.mm_op_compare_mod_q(3, *args, **kwds)

def op_store_axis(*args, **kwds):
    return mm_op.mm_op_store_axis(3, *args, **kwds)

def op_xy(*args, **kwds):
    return mm_op.mm_op_xy(3, *args, **kwds)

def op_omega(*args, **kwds):
    return mm_op.mm_op_omega(3, *args, **kwds)

def op_t_A(*args, **kwds):
    return mm_op.mm_op_t_A(3, *args, **kwds)

def op_word(*args, **kwds):
    return mm_op.mm_op_word(3, *args, **kwds)

def op_word_tag_A(*args, **kwds):
    return mm_op.mm_op_word_tag_A(3, *args, **kwds)

def op_word_ABC(*args, **kwds):
    return mm_op.mm_op_word_ABC(3, *args, **kwds)

def op_eval_A_rank_mod3(*args, **kwds):
    return mm_op.mm_op_eval_A_rank_mod3(3, *args, **kwds)

def op_load_leech3matrix(*args, **kwds):
    return mm_op.mm_op_load_leech3matrix(3, *args, **kwds)

def op_eval_A_aux(*args, **kwds):
    return mm_op.mm_op_eval_A_aux(3, *args, **kwds)

def op_eval_A(*args, **kwds):
    return mm_op.mm_op_eval_A(3, *args, **kwds)

def op_norm_A(*args, **kwds):
    return mm_op.mm_op_norm_A(3, *args, **kwds)

def op_watermark_A(*args, **kwds):
    return mm_op.mm_op_watermark_A(3, *args, **kwds)

def op_watermark_A_perm_num(*args, **kwds):
    return mm_op.mm_op_watermark_A_perm_num(3, *args, **kwds)

