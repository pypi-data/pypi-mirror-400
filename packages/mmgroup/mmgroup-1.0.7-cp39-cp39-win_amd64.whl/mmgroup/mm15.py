"""This module is deprecated; do not use in new projects!"""

import warnings
from mmgroup import mm_op

warnings.warn("Module mmgroup.mm15 is deprecated! " 
    "Replace function 'op_<xxx>(*args)' in this module by function "
    "'mm_op_<xxx>(15, *args)' in module mmgroup.mm_op!",
    UserWarning)

def op_pi(*args, **kwds):
    return mm_op.mm_op_pi(15, *args, **kwds)

def op_copy(*args, **kwds):
    return mm_op.mm_op_copy(15, *args, **kwds)

def op_compare_len(*args, **kwds):
    return mm_op.mm_op_compare_len(15, *args, **kwds)

def op_compare(*args, **kwds):
    return mm_op.mm_op_compare(15, *args, **kwds)

def op_checkzero(*args, **kwds):
    return mm_op.mm_op_checkzero(15, *args, **kwds)

def op_vector_add(*args, **kwds):
    return mm_op.mm_op_vector_add(15, *args, **kwds)

def op_scalar_mul(*args, **kwds):
    return mm_op.mm_op_scalar_mul(15, *args, **kwds)

def op_compare_mod_q(*args, **kwds):
    return mm_op.mm_op_compare_mod_q(15, *args, **kwds)

def op_store_axis(*args, **kwds):
    return mm_op.mm_op_store_axis(15, *args, **kwds)

def op_xy(*args, **kwds):
    return mm_op.mm_op_xy(15, *args, **kwds)

def op_omega(*args, **kwds):
    return mm_op.mm_op_omega(15, *args, **kwds)

def op_t_A(*args, **kwds):
    return mm_op.mm_op_t_A(15, *args, **kwds)

def op_word(*args, **kwds):
    return mm_op.mm_op_word(15, *args, **kwds)

def op_word_tag_A(*args, **kwds):
    return mm_op.mm_op_word_tag_A(15, *args, **kwds)

def op_word_ABC(*args, **kwds):
    return mm_op.mm_op_word_ABC(15, *args, **kwds)

def op_eval_A_rank_mod3(*args, **kwds):
    return mm_op.mm_op_eval_A_rank_mod3(15, *args, **kwds)

def op_load_leech3matrix(*args, **kwds):
    return mm_op.mm_op_load_leech3matrix(15, *args, **kwds)

def op_eval_A_aux(*args, **kwds):
    return mm_op.mm_op_eval_A_aux(15, *args, **kwds)

def op_eval_A(*args, **kwds):
    return mm_op.mm_op_eval_A(15, *args, **kwds)

def op_norm_A(*args, **kwds):
    return mm_op.mm_op_norm_A(15, *args, **kwds)

def op_watermark_A(*args, **kwds):
    return mm_op.mm_op_watermark_A(15, *args, **kwds)

def op_watermark_A_perm_num(*args, **kwds):
    return mm_op.mm_op_watermark_A_perm_num(15, *args, **kwds)

def op_eval_X_find_abs(*args, **kwds):
    return mm_op.mm_op_eval_X_find_abs(15, *args, **kwds)

def op_eval_X_count_abs(*args, **kwds):
    return mm_op.mm_op_eval_X_count_abs(15, *args, **kwds)

