// Warning: This file has been generated automatically. Do not change!
// This header has been created automatically, do not edit!

#ifndef MM_OP_H
#define MM_OP_H

#ifdef __cplusplus
extern "C" {
#endif

#include "mm_basics.h"




/** @file mm_op_sub.h

 The header file ``mm_op_sub.h`` contains basic definitions for the
 C files dealing with  vectors of the 198884-dimensional representation
 of the monster group modulo ``p``,
 as described in  *The C interface of the mmgroup project*,
 section *Description of the mmgroup.mm extension*.
*/






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
// %%FROM mm3_op_misc.c
/** 
  This enumeration contains the  offsets for the tags ``A,B,C,T,X,Z,Y``
  in a vector in the 196884-dimensional representation of the monster,
  stored in the internal representation.

  This is similar to enum MM_AUX_OFS in file ``mm_basics.h``. But 
  here the offsets are given in units of 64-bit integers
  for a vector of the  representation \f$\rho_{3}\f$ of the
  monster group in characteristic  3.

  Thes definition are used in all C files dealing with the 
  representation of the Monster modulo 3.
*/
enum MM_OP3_OFS  {
 MM_OP3_OFS_A = (MM_AUX_OFS_A >> 5), /**< Offset for tag A */
 MM_OP3_OFS_B = (MM_AUX_OFS_B >> 5), /**< Offset for tag B */   
 MM_OP3_OFS_C = (MM_AUX_OFS_C >> 5), /**< Offset for tag C */    
 MM_OP3_OFS_T = (MM_AUX_OFS_T >> 5), /**< Offset for tag T */  
 MM_OP3_OFS_X = (MM_AUX_OFS_X >> 5), /**< Offset for tag X */   
 MM_OP3_OFS_Z = (MM_AUX_OFS_Z >> 5), /**< Offset for tag Z */   
 MM_OP3_OFS_Y = (MM_AUX_OFS_Y >> 5), /**< Offset for tag Y */    
 MM_OP3_LEN_V = (MM_AUX_LEN_V >> 5), /**< Total length of the internal representation */    
};
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op3_copy(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_compare_len(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t len);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_compare(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_compare_abs(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_checkzero(uint_mmv_t *mv);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_vector_add(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_scalar_mul(int32_t factor, uint_mmv_t *mv1);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_compare_mod_q(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t q);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_store_axis(uint32_t x, uint_mmv_t *mv);
/// @endcond

// %%FROM mm3_op_pi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op3_neg_scalprod_d_i(uint_mmv_t* v);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_pi(uint_mmv_t *v_in, uint32_t delta, uint32_t pi, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op3_delta(uint_mmv_t *v_in, uint32_t delta, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op3_pi_tag_ABC(uint_mmv_t *v, uint32_t delta, uint32_t pi, uint32_t mode);
// %%EXPORT 
MM_OP_API
int32_t mm_op3_delta_tag_ABC(uint_mmv_t *v, uint32_t d, uint32_t mode);
/// @endcond 

// %%FROM mm3_op_xy.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op3_xy(uint_mmv_t *v_in, uint32_t f, uint32_t e, uint32_t eps, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_omega(uint_mmv_t *v, uint32_t d);
// %%EXPORT 
MM_OP_API
int32_t mm_op3_xy_tag_ABC(uint_mmv_t *v, uint32_t f, uint32_t e, uint32_t eps, uint32_t mode);
/// @endcond 

// %%FROM mm3_op_t.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op3_t(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_t_A(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op3_t_ABC(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm3_op_xi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op3_xi(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op3_xi_tag_A(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm3_op_word.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op3_word(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e, uint_mmv_t *work);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_word_tag_A(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_word_ABC(uint_mmv_t *v, uint32_t *g, int32_t len_g, uint_mmv_t *v_out);
/// @endcond

// %%FROM mm3_op_scalprod.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op3_scalprod(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_scalprod_ind(uint_mmv_t *mv1, uint_mmv_t *mv2, uint16_t *ind);
/// @endcond 

// %%FROM mm3_op_std_axis.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op3_mul_std_axis(uint_mmv_t *v);
/// @endcond 

// %%FROM mm7_op_misc.c
/** 
  This enumeration contains the  offsets for the tags ``A,B,C,T,X,Z,Y``
  in a vector in the 196884-dimensional representation of the monster,
  stored in the internal representation.

  This is similar to enum MM_AUX_OFS in file ``mm_basics.h``. But 
  here the offsets are given in units of 64-bit integers
  for a vector of the  representation \f$\rho_{7}\f$ of the
  monster group in characteristic  7.

  Thes definition are used in all C files dealing with the 
  representation of the Monster modulo 7.
*/
enum MM_OP7_OFS  {
 MM_OP7_OFS_A = (MM_AUX_OFS_A >> 4), /**< Offset for tag A */
 MM_OP7_OFS_B = (MM_AUX_OFS_B >> 4), /**< Offset for tag B */   
 MM_OP7_OFS_C = (MM_AUX_OFS_C >> 4), /**< Offset for tag C */    
 MM_OP7_OFS_T = (MM_AUX_OFS_T >> 4), /**< Offset for tag T */  
 MM_OP7_OFS_X = (MM_AUX_OFS_X >> 4), /**< Offset for tag X */   
 MM_OP7_OFS_Z = (MM_AUX_OFS_Z >> 4), /**< Offset for tag Z */   
 MM_OP7_OFS_Y = (MM_AUX_OFS_Y >> 4), /**< Offset for tag Y */    
 MM_OP7_LEN_V = (MM_AUX_LEN_V >> 4), /**< Total length of the internal representation */    
};
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op7_copy(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_compare_len(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t len);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_compare(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_compare_abs(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_checkzero(uint_mmv_t *mv);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_vector_add(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_scalar_mul(int32_t factor, uint_mmv_t *mv1);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_compare_mod_q(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t q);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_store_axis(uint32_t x, uint_mmv_t *mv);
/// @endcond

// %%FROM mm7_op_pi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op7_neg_scalprod_d_i(uint_mmv_t* v);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_pi(uint_mmv_t *v_in, uint32_t delta, uint32_t pi, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op7_delta(uint_mmv_t *v_in, uint32_t delta, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op7_pi_tag_ABC(uint_mmv_t *v, uint32_t delta, uint32_t pi, uint32_t mode);
// %%EXPORT 
MM_OP_API
int32_t mm_op7_delta_tag_ABC(uint_mmv_t *v, uint32_t d, uint32_t mode);
/// @endcond 

// %%FROM mm7_op_xy.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op7_xy(uint_mmv_t *v_in, uint32_t f, uint32_t e, uint32_t eps, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_omega(uint_mmv_t *v, uint32_t d);
// %%EXPORT 
MM_OP_API
int32_t mm_op7_xy_tag_ABC(uint_mmv_t *v, uint32_t f, uint32_t e, uint32_t eps, uint32_t mode);
/// @endcond 

// %%FROM mm7_op_t.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op7_t(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_t_A(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op7_t_ABC(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm7_op_xi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op7_xi(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op7_xi_tag_A(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm7_op_word.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op7_word(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e, uint_mmv_t *work);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_word_tag_A(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e);
// %%EXPORT px
MM_OP_API
int32_t mm_op7_word_ABC(uint_mmv_t *v, uint32_t *g, int32_t len_g, uint_mmv_t *v_out);
/// @endcond

// %%FROM mm7_op_scalprod.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op7_scalprod(uint_mmv_t *mv1, uint_mmv_t *mv2);
/// @endcond 

// %%FROM mm7_op_std_axis.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op7_mul_std_axis(uint_mmv_t *v);
/// @endcond 

// %%FROM mm15_op_misc.c
/** 
  This enumeration contains the  offsets for the tags ``A,B,C,T,X,Z,Y``
  in a vector in the 196884-dimensional representation of the monster,
  stored in the internal representation.

  This is similar to enum MM_AUX_OFS in file ``mm_basics.h``. But 
  here the offsets are given in units of 64-bit integers
  for a vector of the  representation \f$\rho_{15}\f$ of the
  monster group in characteristic  15.

  Thes definition are used in all C files dealing with the 
  representation of the Monster modulo 15.
*/
enum MM_OP15_OFS  {
 MM_OP15_OFS_A = (MM_AUX_OFS_A >> 4), /**< Offset for tag A */
 MM_OP15_OFS_B = (MM_AUX_OFS_B >> 4), /**< Offset for tag B */   
 MM_OP15_OFS_C = (MM_AUX_OFS_C >> 4), /**< Offset for tag C */    
 MM_OP15_OFS_T = (MM_AUX_OFS_T >> 4), /**< Offset for tag T */  
 MM_OP15_OFS_X = (MM_AUX_OFS_X >> 4), /**< Offset for tag X */   
 MM_OP15_OFS_Z = (MM_AUX_OFS_Z >> 4), /**< Offset for tag Z */   
 MM_OP15_OFS_Y = (MM_AUX_OFS_Y >> 4), /**< Offset for tag Y */    
 MM_OP15_LEN_V = (MM_AUX_LEN_V >> 4), /**< Total length of the internal representation */    
};
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op15_copy(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_compare_len(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t len);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_compare(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_compare_abs(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_checkzero(uint_mmv_t *mv);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_vector_add(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_scalar_mul(int32_t factor, uint_mmv_t *mv1);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_compare_mod_q(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t q);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_store_axis(uint32_t x, uint_mmv_t *mv);
/// @endcond

// %%FROM mm15_op_pi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op15_neg_scalprod_d_i(uint_mmv_t* v);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_pi(uint_mmv_t *v_in, uint32_t delta, uint32_t pi, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op15_delta(uint_mmv_t *v_in, uint32_t delta, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op15_pi_tag_ABC(uint_mmv_t *v, uint32_t delta, uint32_t pi, uint32_t mode);
// %%EXPORT 
MM_OP_API
int32_t mm_op15_delta_tag_ABC(uint_mmv_t *v, uint32_t d, uint32_t mode);
/// @endcond 

// %%FROM mm15_op_xy.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op15_xy(uint_mmv_t *v_in, uint32_t f, uint32_t e, uint32_t eps, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_omega(uint_mmv_t *v, uint32_t d);
// %%EXPORT 
MM_OP_API
int32_t mm_op15_xy_tag_ABC(uint_mmv_t *v, uint32_t f, uint32_t e, uint32_t eps, uint32_t mode);
/// @endcond 

// %%FROM mm15_op_t.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op15_t(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_t_A(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op15_t_ABC(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm15_op_xi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op15_xi(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op15_xi_tag_A(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm15_op_word.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op15_word(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e, uint_mmv_t *work);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_word_tag_A(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_word_ABC(uint_mmv_t *v, uint32_t *g, int32_t len_g, uint_mmv_t *v_out);
/// @endcond

// %%FROM mm15_op_scalprod.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op15_scalprod(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_scalprod_ind(uint_mmv_t *mv1, uint_mmv_t *mv2, uint16_t *ind);
/// @endcond 

// %%FROM mm15_op_std_axis.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op15_mul_std_axis(uint_mmv_t *v);
/// @endcond 

// %%FROM mm31_op_misc.c
/** 
  This enumeration contains the  offsets for the tags ``A,B,C,T,X,Z,Y``
  in a vector in the 196884-dimensional representation of the monster,
  stored in the internal representation.

  This is similar to enum MM_AUX_OFS in file ``mm_basics.h``. But 
  here the offsets are given in units of 64-bit integers
  for a vector of the  representation \f$\rho_{31}\f$ of the
  monster group in characteristic  31.

  Thes definition are used in all C files dealing with the 
  representation of the Monster modulo 31.
*/
enum MM_OP31_OFS  {
 MM_OP31_OFS_A = (MM_AUX_OFS_A >> 3), /**< Offset for tag A */
 MM_OP31_OFS_B = (MM_AUX_OFS_B >> 3), /**< Offset for tag B */   
 MM_OP31_OFS_C = (MM_AUX_OFS_C >> 3), /**< Offset for tag C */    
 MM_OP31_OFS_T = (MM_AUX_OFS_T >> 3), /**< Offset for tag T */  
 MM_OP31_OFS_X = (MM_AUX_OFS_X >> 3), /**< Offset for tag X */   
 MM_OP31_OFS_Z = (MM_AUX_OFS_Z >> 3), /**< Offset for tag Z */   
 MM_OP31_OFS_Y = (MM_AUX_OFS_Y >> 3), /**< Offset for tag Y */    
 MM_OP31_LEN_V = (MM_AUX_LEN_V >> 3), /**< Total length of the internal representation */    
};
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op31_copy(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_compare_len(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t len);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_compare(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_compare_abs(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_checkzero(uint_mmv_t *mv);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_vector_add(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_scalar_mul(int32_t factor, uint_mmv_t *mv1);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_compare_mod_q(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t q);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_store_axis(uint32_t x, uint_mmv_t *mv);
/// @endcond

// %%FROM mm31_op_pi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op31_neg_scalprod_d_i(uint_mmv_t* v);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_pi(uint_mmv_t *v_in, uint32_t delta, uint32_t pi, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op31_delta(uint_mmv_t *v_in, uint32_t delta, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op31_pi_tag_ABC(uint_mmv_t *v, uint32_t delta, uint32_t pi, uint32_t mode);
// %%EXPORT 
MM_OP_API
int32_t mm_op31_delta_tag_ABC(uint_mmv_t *v, uint32_t d, uint32_t mode);
/// @endcond 

// %%FROM mm31_op_xy.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op31_xy(uint_mmv_t *v_in, uint32_t f, uint32_t e, uint32_t eps, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_omega(uint_mmv_t *v, uint32_t d);
// %%EXPORT 
MM_OP_API
int32_t mm_op31_xy_tag_ABC(uint_mmv_t *v, uint32_t f, uint32_t e, uint32_t eps, uint32_t mode);
/// @endcond 

// %%FROM mm31_op_t.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op31_t(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_t_A(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op31_t_ABC(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm31_op_xi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op31_xi(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op31_xi_tag_A(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm31_op_word.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op31_word(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e, uint_mmv_t *work);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_word_tag_A(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e);
// %%EXPORT px
MM_OP_API
int32_t mm_op31_word_ABC(uint_mmv_t *v, uint32_t *g, int32_t len_g, uint_mmv_t *v_out);
/// @endcond

// %%FROM mm31_op_scalprod.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op31_scalprod(uint_mmv_t *mv1, uint_mmv_t *mv2);
/// @endcond 

// %%FROM mm31_op_std_axis.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op31_mul_std_axis(uint_mmv_t *v);
/// @endcond 

// %%FROM mm127_op_misc.c
/** 
  This enumeration contains the  offsets for the tags ``A,B,C,T,X,Z,Y``
  in a vector in the 196884-dimensional representation of the monster,
  stored in the internal representation.

  This is similar to enum MM_AUX_OFS in file ``mm_basics.h``. But 
  here the offsets are given in units of 64-bit integers
  for a vector of the  representation \f$\rho_{127}\f$ of the
  monster group in characteristic  127.

  Thes definition are used in all C files dealing with the 
  representation of the Monster modulo 127.
*/
enum MM_OP127_OFS  {
 MM_OP127_OFS_A = (MM_AUX_OFS_A >> 3), /**< Offset for tag A */
 MM_OP127_OFS_B = (MM_AUX_OFS_B >> 3), /**< Offset for tag B */   
 MM_OP127_OFS_C = (MM_AUX_OFS_C >> 3), /**< Offset for tag C */    
 MM_OP127_OFS_T = (MM_AUX_OFS_T >> 3), /**< Offset for tag T */  
 MM_OP127_OFS_X = (MM_AUX_OFS_X >> 3), /**< Offset for tag X */   
 MM_OP127_OFS_Z = (MM_AUX_OFS_Z >> 3), /**< Offset for tag Z */   
 MM_OP127_OFS_Y = (MM_AUX_OFS_Y >> 3), /**< Offset for tag Y */    
 MM_OP127_LEN_V = (MM_AUX_LEN_V >> 3), /**< Total length of the internal representation */    
};
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op127_copy(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_compare_len(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t len);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_compare(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_compare_abs(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_checkzero(uint_mmv_t *mv);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_vector_add(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_scalar_mul(int32_t factor, uint_mmv_t *mv1);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_compare_mod_q(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t q);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_store_axis(uint32_t x, uint_mmv_t *mv);
/// @endcond

// %%FROM mm127_op_pi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op127_neg_scalprod_d_i(uint_mmv_t* v);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_pi(uint_mmv_t *v_in, uint32_t delta, uint32_t pi, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op127_delta(uint_mmv_t *v_in, uint32_t delta, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op127_pi_tag_ABC(uint_mmv_t *v, uint32_t delta, uint32_t pi, uint32_t mode);
// %%EXPORT 
MM_OP_API
int32_t mm_op127_delta_tag_ABC(uint_mmv_t *v, uint32_t d, uint32_t mode);
/// @endcond 

// %%FROM mm127_op_xy.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op127_xy(uint_mmv_t *v_in, uint32_t f, uint32_t e, uint32_t eps, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_omega(uint_mmv_t *v, uint32_t d);
// %%EXPORT 
MM_OP_API
int32_t mm_op127_xy_tag_ABC(uint_mmv_t *v, uint32_t f, uint32_t e, uint32_t eps, uint32_t mode);
/// @endcond 

// %%FROM mm127_op_t.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op127_t(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_t_A(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op127_t_ABC(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm127_op_xi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op127_xi(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op127_xi_tag_A(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm127_op_word.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op127_word(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e, uint_mmv_t *work);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_word_tag_A(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e);
// %%EXPORT px
MM_OP_API
int32_t mm_op127_word_ABC(uint_mmv_t *v, uint32_t *g, int32_t len_g, uint_mmv_t *v_out);
/// @endcond

// %%FROM mm127_op_scalprod.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op127_scalprod(uint_mmv_t *mv1, uint_mmv_t *mv2);
/// @endcond 

// %%FROM mm127_op_std_axis.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op127_mul_std_axis(uint_mmv_t *v);
/// @endcond 

// %%FROM mm255_op_misc.c
/** 
  This enumeration contains the  offsets for the tags ``A,B,C,T,X,Z,Y``
  in a vector in the 196884-dimensional representation of the monster,
  stored in the internal representation.

  This is similar to enum MM_AUX_OFS in file ``mm_basics.h``. But 
  here the offsets are given in units of 64-bit integers
  for a vector of the  representation \f$\rho_{255}\f$ of the
  monster group in characteristic  255.

  Thes definition are used in all C files dealing with the 
  representation of the Monster modulo 255.
*/
enum MM_OP255_OFS  {
 MM_OP255_OFS_A = (MM_AUX_OFS_A >> 3), /**< Offset for tag A */
 MM_OP255_OFS_B = (MM_AUX_OFS_B >> 3), /**< Offset for tag B */   
 MM_OP255_OFS_C = (MM_AUX_OFS_C >> 3), /**< Offset for tag C */    
 MM_OP255_OFS_T = (MM_AUX_OFS_T >> 3), /**< Offset for tag T */  
 MM_OP255_OFS_X = (MM_AUX_OFS_X >> 3), /**< Offset for tag X */   
 MM_OP255_OFS_Z = (MM_AUX_OFS_Z >> 3), /**< Offset for tag Z */   
 MM_OP255_OFS_Y = (MM_AUX_OFS_Y >> 3), /**< Offset for tag Y */    
 MM_OP255_LEN_V = (MM_AUX_LEN_V >> 3), /**< Total length of the internal representation */    
};
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op255_copy(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_compare_len(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t len);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_compare(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_compare_abs(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_checkzero(uint_mmv_t *mv);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_vector_add(uint_mmv_t *mv1, uint_mmv_t *mv2);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_scalar_mul(int32_t factor, uint_mmv_t *mv1);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_compare_mod_q(uint_mmv_t *mv1, uint_mmv_t *mv2, uint32_t q);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_store_axis(uint32_t x, uint_mmv_t *mv);
/// @endcond

// %%FROM mm255_op_pi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op255_neg_scalprod_d_i(uint_mmv_t* v);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_pi(uint_mmv_t *v_in, uint32_t delta, uint32_t pi, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op255_delta(uint_mmv_t *v_in, uint32_t delta, uint_mmv_t * v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op255_pi_tag_ABC(uint_mmv_t *v, uint32_t delta, uint32_t pi, uint32_t mode);
// %%EXPORT 
MM_OP_API
int32_t mm_op255_delta_tag_ABC(uint_mmv_t *v, uint32_t d, uint32_t mode);
/// @endcond 

// %%FROM mm255_op_xy.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op255_xy(uint_mmv_t *v_in, uint32_t f, uint32_t e, uint32_t eps, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_omega(uint_mmv_t *v, uint32_t d);
// %%EXPORT 
MM_OP_API
int32_t mm_op255_xy_tag_ABC(uint_mmv_t *v, uint32_t f, uint32_t e, uint32_t eps, uint32_t mode);
/// @endcond 

// %%FROM mm255_op_t.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op255_t(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_t_A(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op255_t_ABC(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm255_op_xi.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT 
MM_OP_API
int32_t mm_op255_xi(uint_mmv_t *v_in,  uint32_t exp, uint_mmv_t *v_out);
// %%EXPORT 
MM_OP_API
int32_t mm_op255_xi_tag_A(uint_mmv_t *v,  uint32_t exp);
/// @endcond 

// %%FROM mm255_op_word.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op255_word(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e, uint_mmv_t *work);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_word_tag_A(uint_mmv_t *v, uint32_t *g, int32_t len_g, int32_t e);
// %%EXPORT px
MM_OP_API
int32_t mm_op255_word_ABC(uint_mmv_t *v, uint32_t *g, int32_t len_g, uint_mmv_t *v_out);
/// @endcond

// %%FROM mm255_op_scalprod.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op255_scalprod(uint_mmv_t *mv1, uint_mmv_t *mv2);
/// @endcond 

// %%FROM mm255_op_std_axis.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op255_mul_std_axis(uint_mmv_t *v);
/// @endcond 

// %%FROM mm3_op_rank_A.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op3_load_leech3matrix(uint_mmv_t *v, uint64_t *a);
// %%EXPORT px
MM_OP_API
int64_t  mm_op3_eval_A_rank_mod3(uint_mmv_t *v, uint32_t d);
/// @endcond

// %%FROM mm3_op_eval_A.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op3_eval_A_aux(uint_mmv_t *v, uint32_t m_and, uint32_t m_xor, uint32_t row);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_eval_A(uint64_t *v, uint32_t v2);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_norm_A(uint_mmv_t *v);
// %%EXPORT px
MM_OP_API
int32_t  mm_op3_watermark_A(uint_mmv_t *v, uint32_t *w);
// %%EXPORT px
MM_OP_API
int32_t mm_op3_watermark_A_perm_num(uint32_t *w, uint_mmv_t *v);
/// @endcond

// %%FROM mm15_op_rank_A.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op15_load_leech3matrix(uint_mmv_t *v, uint64_t *a);
// %%EXPORT px
MM_OP_API
int64_t  mm_op15_eval_A_rank_mod3(uint_mmv_t *v, uint32_t d);
/// @endcond

// %%FROM mm15_op_eval_A.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op15_eval_A_aux(uint_mmv_t *v, uint32_t m_and, uint32_t m_xor, uint32_t row);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_eval_A(uint64_t *v, uint32_t v2);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_norm_A(uint_mmv_t *v);
// %%EXPORT px
MM_OP_API
int32_t  mm_op15_watermark_A(uint_mmv_t *v, uint32_t *w);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_watermark_A_perm_num(uint32_t *w, uint_mmv_t *v);
/// @endcond

// %%FROM mm15_op_eval_X.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_OP_API
int32_t mm_op15_eval_X_find_abs(uint_mmv_t *v, uint32_t *p_out, uint32_t n,  uint32_t y0, uint32_t y1);
// %%EXPORT px
MM_OP_API
int32_t mm_op15_eval_X_count_abs(uint_mmv_t *v, uint32_t *p_out);
/// @endcond 

// %%INCLUDE_HEADERS


#ifdef __cplusplus
}
#endif
#endif  // #ifndef MM_OP_H


                                  

