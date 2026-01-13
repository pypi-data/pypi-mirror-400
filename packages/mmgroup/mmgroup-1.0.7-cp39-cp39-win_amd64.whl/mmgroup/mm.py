"""This module is deprecated; do not use in new projects!"""

import warnings
from mmgroup import mm_op

warnings.warn("Module mmgroup.mm is deprecated! " 
    "Replace a function in this module by the "
    "corresponding function in module mmgroup.mm_op!",
    UserWarning)


def mm_aux_read_direct_mmv1(*args, **kwds):
    return mm_op.mm_aux_read_mmv1(*args, **kwds) 

PROTECT_OVERFLOW = mm_op.PROTECT_OVERFLOW
INT_BITS = mm_op.INT_BITS
mm_aux_mmv_size = mm_op.mm_aux_mmv_size
mm_aux_zero_mmv = mm_op.mm_aux_zero_mmv
mm_aux_random_mmv = mm_op.mm_aux_random_mmv
mm_aux_reduce_mmv = mm_op.mm_aux_reduce_mmv
mm_aux_reduce_mmv_fields = mm_op.mm_aux_reduce_mmv_fields
mm_aux_check_mmv = mm_op.mm_aux_check_mmv
mm_aux_small24_expand = mm_op.mm_aux_small24_expand
mm_aux_small24_compress = mm_op.mm_aux_small24_compress
mm_aux_mmv_to_bytes = mm_op.mm_aux_mmv_to_bytes
mm_aux_bytes_to_mmv = mm_op.mm_aux_bytes_to_mmv
mm_aux_mmv_to_sparse = mm_op.mm_aux_mmv_to_sparse
mm_aux_mmv_extract_sparse = mm_op.mm_aux_mmv_extract_sparse
mm_aux_mmv_get_sparse = mm_op.mm_aux_mmv_get_sparse
mm_aux_mmv_add_sparse = mm_op.mm_aux_mmv_add_sparse
mm_aux_mmv_set_sparse = mm_op.mm_aux_mmv_set_sparse
mm_aux_mmv_extract_sparse_signs = mm_op.mm_aux_mmv_extract_sparse_signs
mm_aux_mmv_extract_x_signs = mm_op.mm_aux_mmv_extract_x_signs
mm_aux_mul_sparse = mm_op.mm_aux_mul_sparse
mm_aux_index_extern_to_sparse = mm_op.mm_aux_index_extern_to_sparse
mm_aux_array_extern_to_sparse = mm_op.mm_aux_array_extern_to_sparse
mm_aux_index_sparse_to_extern = mm_op.mm_aux_index_sparse_to_extern
mm_aux_index_sparse_to_leech = mm_op.mm_aux_index_sparse_to_leech
mm_aux_index_sparse_to_leech2 = mm_op.mm_aux_index_sparse_to_leech2
mm_aux_index_leech2_to_sparse = mm_op.mm_aux_index_leech2_to_sparse
mm_aux_index_intern_to_sparse = mm_op.mm_aux_index_intern_to_sparse
mm_aux_hash = mm_op.mm_aux_hash
mm_sub_test_prep_pi_64 = mm_op.mm_sub_test_prep_pi_64
mm_sub_test_prep_xy = mm_op.mm_sub_test_prep_xy
mm_group_prepare_op_ABC = mm_op.mm_group_prepare_op_ABC
mm_sub_get_table_xi = mm_op.mm_sub_get_table_xi
mm_crt_combine = mm_op.mm_crt_combine
mm_crt_combine_bytes = mm_op.mm_crt_combine_bytes
mm_crt_check_v2 = mm_op.mm_crt_check_v2
mm_crt_check_g = mm_op.mm_crt_check_g
mm_crt_norm_int32_32 = mm_op.mm_crt_norm_int32_32
mm_crt_norm_int32 = mm_op.mm_crt_norm_int32
mm_crt_v2_int32_32 = mm_op.mm_crt_v2_int32_32
mm_crt_v2_int32 = mm_op.mm_crt_v2_int32
mmv_array = mm_op.mmv_array
mm_vector = mm_op.mm_vector
