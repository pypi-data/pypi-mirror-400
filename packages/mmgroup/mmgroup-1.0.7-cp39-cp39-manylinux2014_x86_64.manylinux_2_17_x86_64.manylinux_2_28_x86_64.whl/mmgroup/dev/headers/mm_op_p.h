// Warning: This file has been generated automatically. Do not change!
// This header has been created automatically, do not edit!

#ifndef MM_OP_P_H
#define MM_OP_P_H

#ifdef __cplusplus
extern "C" {
#endif



#include "mm_basics.h"






/// @cond DO_NOT_DOCUMENT 
//  Definitions for using this header in a a DLL (or a shared library)

// Generic helper definitions for DLL (or shared library) support
#if defined(_WIN32) || defined(__CYGWIN__)
  #define MM_OP_DLL_IMPORT __declspec(dllimport)
  #define MM_OP_DLL_EXPORT __declspec(dllexport)
#elif (defined(__GNUC__) || defined(__clang__)) && defined(_WIN32)
  #define MM_OP_DLL_IMPORT __attribute__((noinline,optimize("no-tree-vectorize"),visiblity("default")))
  #define MM_OP_DLL_EXPORT __attribute__((noinline,optimize("no-tree-vectorize"),visiblity("default")))
#else
  #define MM_OP_DLL_IMPORT
  #define MM_OP_DLL_EXPORT
#endif

// Now we use the generic helper definitions above to define MM_OP_API 
// MM_OP_API is used for the public API symbols. It either DLL imports 
// or DLL exports 

#ifdef MM_OP_DLL_EXPORTS // defined if we are building the MM_OP DLL 
  #define MM_OP_API MM_OP_DLL_EXPORT
#else                  // not defined if we are using the MM_OP DLL 
  #define MM_OP_API  MM_OP_DLL_IMPORT
#endif // MM_OP_DLL_EXPORTS

/// @endcond
// %%FROM mm_op_p_vector.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT_TABLE  p
MM_OP_API
extern const uint8_t MM_OP_P_TABLE[];
// %%EXPORT px
MM_OP_API
int32_t mm_op_copy(uint32_t p, uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op_compare_len(uint32_t p, uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t len);
// %%EXPORT px
MM_OP_API
int32_t mm_op_compare(uint32_t p, uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op_compare_abs(uint32_t p, uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op_checkzero(uint32_t p, uint_mmv_t *mv);
// %%EXPORT px
MM_OP_API
int32_t mm_op_vector_add(uint32_t p, uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op_scalar_mul(uint32_t p, int32_t factor, uint_mmv_t *mv1);
// %%EXPORT px
MM_OP_API
int32_t mm_op_compare_mod_q(uint32_t p, uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t q);
// %%EXPORT px
MM_OP_API
int32_t mm_op_store_axis(uint32_t p, uint32_t x, uint_mmv_t *mv);
// %%EXPORT px
MM_OP_API
int32_t mm_op_pi(uint32_t p, uint_mmv_t *v_in, uint32_t delta, uint32_t pi, uint_mmv_t * v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op_xy(uint32_t p, uint_mmv_t *v_in, uint32_t f, uint32_t e, uint32_t eps, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op_omega(uint32_t p, uint_mmv_t *v, uint32_t d);
// %%EXPORT px
MM_OP_API
int32_t mm_op_t_A(uint32_t p, uint_mmv_t *v_in,  uint32_t e, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op_word(uint32_t p, uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e, uint_mmv_t *work);
// %%EXPORT px
MM_OP_API
int32_t mm_op_word_tag_A(uint32_t p, uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e);
// %%EXPORT px
MM_OP_API
int32_t mm_op_word_ABC(uint32_t p, uint_mmv_t *v, uint32_t *g, int32_t len_g, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op_scalprod(uint32_t p, uint_mmv_t *v1, uint_mmv_t *v2);
// %%EXPORT px
MM_OP_API
int32_t mm_op_scalprod_ind(uint32_t p, uint_mmv_t *v1, uint_mmv_t *v2, uint16_t *ind);
// %%EXPORT px
MM_OP_API
int32_t mm_op_mul_std_axis(uint32_t p, uint_mmv_t *v);
/// @endcond 

// %%FROM mm_op_p_axis.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op_load_leech3matrix(uint32_t p, uint_mmv_t *v, uint64_t *a);
// %%EXPORT px
MM_OP_API
int64_t  mm_op_eval_A_rank_mod3(uint32_t p, uint_mmv_t *v, uint32_t d);
// %%EXPORT px
MM_OP_API
int32_t mm_op_eval_A_aux(uint32_t p, uint_mmv_t *v, uint32_t m_and, uint32_t m_xor, uint32_t row);
// %%EXPORT px
MM_OP_API
int32_t mm_op_eval_A(uint32_t p, uint_mmv_t *v, uint32_t v2);
// %%EXPORT px
MM_OP_API
int32_t mm_op_norm_A(uint32_t p, uint_mmv_t *v);
// %%EXPORT px
MM_OP_API
int32_t  mm_op_watermark_A(uint32_t p, uint_mmv_t *v, uint32_t *w);
// %%EXPORT px
MM_OP_API
int32_t mm_op_watermark_A_perm_num(uint32_t p, uint32_t *w, uint_mmv_t *v);
// %%EXPORT px
MM_OP_API
int32_t mm_op_eval_X_find_abs(uint32_t p, uint_mmv_t *v, uint32_t *p_out, uint32_t n,  uint32_t y0, uint32_t y1);
// %%EXPORT px
MM_OP_API
int32_t mm_op_eval_X_count_abs(uint32_t p, uint_mmv_t *v, uint32_t *p_out);
/// @endcond 

// %%INCLUDE_HEADERS


#ifdef __cplusplus
}
#endif
#endif  // #ifndef MM_OP_P_H



