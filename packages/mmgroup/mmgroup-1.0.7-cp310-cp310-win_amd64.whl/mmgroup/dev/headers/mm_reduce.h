// Warning: This file has been generated automatically. Do not change!



#ifndef MM_REDUCE_H
#define MM_REDUCE_H




/** @file mm_reduce.h

 Yet to be documented
*/

#include <stdint.h>
#include <stdlib.h>
#include "mat24_functions.h"
#include "mmgroup_generators.h"
#include "clifford12.h"   
#include "mm_basics.h"   
#include "mm_op_sub.h"   
#include "mm_op_p.h"   
#include "mm_reduce.h"   








/// @cond DO_NOT_DOCUMENT 
//  Definitions for using this header in a a DLL (or a shared library)

// Generic helper definitions for DLL (or shared library) support
#if defined(_WIN32) || defined(__CYGWIN__)
  #define MM_REDUCE_DLL_IMPORT __declspec(dllimport)
  #define MM_REDUCE_DLL_EXPORT __declspec(dllexport)
#elif (defined(__GNUC__) || defined(__clang__)) && defined(_WIN32)
  #define MM_REDUCE_DLL_IMPORT __attribute__((noinline,optimize("no-tree-vectorize"),visiblity("default")))
  #define MM_REDUCE_DLL_EXPORT __attribute__((noinline,optimize("no-tree-vectorize"),visiblity("default")))
#else
  #define MM_REDUCE_DLL_IMPORT
  #define MM_REDUCE_DLL_EXPORT
#endif

// Now we use the generic helper definitions above to define MM_REDUCE_API 
// MM_REDUCE_API is used for the public API symbols. It either DLL imports 
// or DLL exports 

#ifdef MM_REDUCE_DLL_EXPORTS // defined if we are building the MM_REDUCE DLL 
  #define MM_REDUCE_API MM_REDUCE_DLL_EXPORT
#else                  // not defined if we are using the MM_REDUCE DLL 
  #define MM_REDUCE_API  MM_REDUCE_DLL_IMPORT
#endif // MM_REDUCE_DLL_EXPORTS

/// @endcond
// %%FROM mm_order_vector.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT_TABLE  p
MM_REDUCE_API
extern const uint32_t MM_ORDER_VECTOR_TAG_DATA[];
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_load_tag_data(uint32_t *buf, uint32_t buf_size);
// %%EXPORT px
MM_REDUCE_API
void mm_order_load_vector(uint_mmv_t *p_dest);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_compare_vector(uint_mmv_t *p_v);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_compare_vector_part_A(uint_mmv_t *p_v);
// %%EXPORT px
MM_REDUCE_API
uint64_t mm_order_hash_vector(uint_mmv_t *p_dest);
/// @endcond 

// %%FROM mm_order.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_check_in_Gx0_fast(uint_mmv_t *v);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_check_in_Gx0(uint_mmv_t *v, uint32_t *g, uint32_t mode, uint_mmv_t *work);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_element_Gx0(uint32_t *g, uint32_t n, uint32_t *h, uint32_t o);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_element_M(uint32_t *g, uint32_t n, uint32_t o);
/// @endcond 

// %%FROM mm_compress.c
#ifdef __cplusplus
extern "C" {
#endif


/// @cond DO_NOT_DOCUMENT
#define MM_COMPRESS_TYPE_NENTRIES 19
/// @endcond


/**
  @brief Structure for storing an element of the Monster compactly

  A properly *reduced* element of the Monster stored in a structure
  of type `gt_word_type` may also be encoded in this structure in a
  more compact form. This facilitates the conversion of that element
  to an integer, which is out of the scope of this module.

  This structure may store an element of the Monster as a word of
  generators of shape

  \f[
      y_f \, x_d \, x_{\delta} \, \pi \, c_1 \, \tau_1 \, c_2 \,
     \tau_1 \, c_3 \,  \tau_3 \, \ldots \, ,
  \f]

  where \f$d, f \in \mathcal{P}, \delta \in  \mathcal{C}^*\f$,
  and \f$\pi \in \mbox{Aut}_{\mbox{St}} \mathcal{P}\f$.
  Here \f$\pi\f$ must correspond to a generator with tag `p`. See
  section *Implementation of the generators of the monster group*
  in the *API reference* for details. \f$\tau_i\f$ is wqaul to
  generator \f$\tau\f$ or to its inverse.

  A generator \f$c_i\f$ is an element of the group \f$G_{x0}\f$
  referred by a 24-bit integer `c_i` representing a type-4 vector
  in *Leech lattice encoding*. This encodes the inverse of the
  element of \f$G_{x0}\f$ computed by applying the C function
  `gen_leech2_reduce_type4` to `c_i`.

  The product \f$y_f \, x_d \, x_{\delta} \, \pi\f$ is encdoded in 
  component `nx`, and the other generators are  encdoded in the 
  entries of component `w`, as desribed in the procedures below.

  For background see
  section *Computations in the Leech lattice modulo 2*
  in *The mmgroup guide for developers*.
   
*/
typedef struct{
   uint64_t nx;   ///< encoding of \f$ y_f \, x_d \, x_{\delta} \, \pi\f$ 
   uint32_t w[MM_COMPRESS_TYPE_NENTRIES];  ///< encoding of \f$c_i, \tau_i\f$
   uint32_t cur;  ///< index of last entry entered into component `w`
} mm_compress_type;





/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_REDUCE_API
int32_t mm_compress_type4(uint32_t i);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_compress_expand_type4(uint32_t i);
// %%EXPORT p
MM_REDUCE_API
void mm_compress_pc_init(mm_compress_type *pc);
// %%EXPORT p
MM_REDUCE_API
int32_t mm_compress_pc_add_nx(mm_compress_type *pc, uint32_t *m, uint32_t len);
// %%EXPORT p
MM_REDUCE_API
int32_t mm_compress_pc_add_type2(mm_compress_type *pc, uint32_t c);
// %%EXPORT 
MM_REDUCE_API
int32_t  mm_compress_pc_add_type4(mm_compress_type *pc, uint32_t c);
// %%EXPORT 
MM_REDUCE_API
int32_t mm_compress_pc_add_t(mm_compress_type *pc, uint32_t t);
// %%EXPORT 
MM_REDUCE_API
int32_t mm_compress_pc(mm_compress_type *pc, uint64_t *p_n);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_compress_pc_expand_int(uint64_t *p_n, uint32_t *m, uint32_t l_m);
/// @endcond  
#ifdef __cplusplus
}
#endif


// %%FROM mm_reduce.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_REDUCE_API
uint32_t mm_reduce_2A_axis_type(uint_mmv_t *v);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_analyze_2A_axis(uint_mmv_t *v, uint32_t * r);
// %%EXPORT px
MM_REDUCE_API
uint32_t mm_reduce_find_type4(uint32_t *v, uint32_t n, uint32_t v2);
// %%EXPORT px
MM_REDUCE_API
uint32_t mm_reduce_find_type4_axis(uint_mmv_t *v, uint32_t v2);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_transform_v4(uint_mmv_t *v, uint32_t v4, uint32_t *target_axes, uint32_t *r, uint_mmv_t *work);
// %%EXPORT px
MM_REDUCE_API
int32_t  mm_reduce_load_axis(uint_mmv_t *v, uint32_t s);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_map_axis(uint32_t *vt, uint_mmv_t *v, uint32_t *a, uint32_t n, uint_mmv_t *work);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_vector_vp(uint32_t *vt, uint_mmv_t *v, uint32_t mode, uint32_t *r, uint_mmv_t *work);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_vector_shortcut(uint32_t stage, uint32_t mode, uint32_t axis, uint32_t *r);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_vector_vm(uint32_t *vt, uint_mmv_t *v, uint32_t *r, uint_mmv_t *work);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_vector_v1(uint_mmv_t *v, uint32_t *r, uint_mmv_t *work);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_vector_incomplete(uint32_t *r);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_reduce_M(uint32_t *a, uint32_t n, uint32_t mode, uint32_t *r);
// %%EXPORT px
MM_REDUCE_API
uint32_t mm_reduce_set_order_vector_mod15(uint32_t mode);
/// @endcond 

// %%FROM mm_suborbit.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_REDUCE_API
uint32_t mm_reduce_op_2A_axis_type(uint_mmv_t *v, uint32_t *g, uint32_t len_g, uint32_t mode);
/// @endcond 

// %%FROM mm_shorten.c

/// @cond DO_NOT_DOCUMENT 
#define MAX_GT_WORD_DATA 24

/// @endcond 



/** 
   @brief Stucture to store a subword of generators of the Monster

   This structure is required in file ``mm_shorten.c``.

   It stores a subword of a word in the Monster in a node
   of a circular doubly-linked list. There is a dedicated EOF (end of
   file) mark in that list, in which member ``eof``is set to 1; and
   elsewhere member ``eof`` is set to zero. Note that standard
   operations like insertions and deletions are easier in a circular
   doubly-linked list than in a standard doubly-linked list.

   Member ``data`` contains a word \f$g\f$ of generators of the
   subgroup \f$G_{x0}\f$; and member ``t_exp`` contains an
   exponent \f$0 \leq e < 3\f$. Then the structure represents the
   element  \f$g \tau^e\f$ of the Monster, where  \f$\tau\f$  is
   the triality element in the subgroup  \f$N_0\f$ of the Monster.

   The length of a word in member ``data`` is limited to the
   size ``MAX_GT_WORD_DATA - 1``; and we will reduce that word
   using function ``xsp2co1_reduce_word`` in module ``xsp2co1.c``
   if necessary. Note that member ``data`` may contain atoms with
   tags ``'x', 'y', 'd', 'p', 'l'`` only, and the inversion bit
   in such an atom is always cleared.

   Member ``img_Omega`` contains the image \f$g \cdot \Omega\f$,
   where \f$\Omega\f$ is the standard frame of the Leech lattice
   mod 2. Here ``img_Omega`` is given in Leech lattice encoding.
   Member ``reduced`` is 1 if the word in member ``data`` is
   reduced (by function ``xsp2co1_reduce_word``) and 0 otherwise.
   
*/
struct gt_subword_s {
    uint32_t eof;        ///< 0 means standard subword, 1 means EOF mark 
    uint32_t length;     ///< Number of entries in component ``data``
    uint32_t img_Omega;  ///< Image of \f$\Omega\f$ under element
    uint32_t t_exp;      ///< Exponent of final tag 't' 
    uint32_t reduced;    ///< True if part 'data' is reduced 
    struct gt_subword_s *p_prev;     ///< Pointer to previous subword 
    struct gt_subword_s *p_next;     ///< Pointer to previous subword 
    uint32_t data[MAX_GT_WORD_DATA]; ///< Element of monster group 
} ;




/** 
   @brief typedef for structure ``struct gt_subword_s``
*/
typedef struct gt_subword_s gt_subword_type;

/** 
   @brief Structure to store an array of entries of type ``gt_subword_type``

   We allocate several entries of of type ``gt_subword_type`` with a
   single call to function ``malloc``. This saves a considerable amount
   of interaction with the operating system.

   This structure contains an array of type ``gt_subword_type[]`` plus
   the necessary bookkeeping information.
*/
struct gt_subword_buf_s {
    uint32_t capacity;   ///< max No of type ``gt_subword_s `` entries
    uint32_t n_used;     ///< used No of type ``gt_subword_s `` entries
    struct gt_subword_buf_s *p_next; ///< Pointer to next buffer
    gt_subword_type subwords[1];     ///< array of subwords in this buffer
} ;




/** 
   @brief typedef for structure ``struct gt_subword_buf_s``
*/
typedef struct gt_subword_buf_s gt_subword_buf_type;



/** 
   @brief Stucture to store a word of generators of the Monster

   This structure is required in file ``mm_shorten.c``.

   It stores a word in the Monster in a circular
   doubly-linked list of nodes of type ``gt_subword_type``. Each of
   these node represents subword of that word, and there is a
   dedicated EOF (end of file) mark in that list that marks both,
   the beginning and the end of the list. Member ``p_end`` always
   points to the EOF mark.

   The structure contains a pointer ``p_node`` pointing to one of
   the nodes of the list, which we will call the **current** node.
   Some functions in these module take a pointer to this structure,
   and the perform operations on the current node. The pointer may
   be manipulated with function ``gt_word_seek``.

*/
typedef struct {
    gt_subword_type *p_end;   ///< Pointer to the **end mark** subword 
    gt_subword_type *p_node;  ///< Pointer to current subword 
    gt_subword_type *p_free;  ///< Pointer to list of free subwords
    int32_t reduce_mode;      ///< Mode for the reduction of a word 

    /* memory management */
    uint32_t is_allocated;    ///< 1 if this structure has been allcocated
    gt_subword_buf_type *pb0; ///< pointer to first buffer
    gt_subword_buf_type *pbe; ///< pointer to last buffer
    gt_subword_buf_type buf;  ///< 1st buffer containing Array of subwords 
} gt_word_type;





#ifdef __cplusplus
extern "C" {
#endif
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT p
MM_REDUCE_API
void gt_subword_clear(gt_subword_type *p_gtsub);
// %%EXPORT p
MM_REDUCE_API
gt_word_type *gt_word_alloc(uint32_t mode, void *p_buffer, size_t nbytes);
// %%EXPORT p
MM_REDUCE_API
void gt_word_free(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
void gt_word_clear(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_insert(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_delete(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_seek(gt_word_type *p_gt, int32_t pos, uint32_t set);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_append_sub_part(gt_word_type *p_gt, uint32_t *a,  uint32_t n);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_reduce_sub(gt_word_type *p_gt, uint32_t sub_mode);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_rule_join(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_rule_t_xi_t(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_reduce_input(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_append(gt_word_type *p_gt, uint32_t *a, uint32_t n);
// %%EXPORT px
MM_REDUCE_API
uint32_t gt_word_n_subwords(uint32_t *a, uint32_t n);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_length(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_reduce(gt_word_type *p_gt);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_store(gt_word_type *p_gt, uint32_t *pa, uint32_t maxlen);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_to_mm_compress(gt_word_type *p_gt, mm_compress_type *p_c);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_compress(gt_word_type *p_gt, uint64_t *p_n);
// %%EXPORT px
MM_REDUCE_API
int32_t gt_word_shorten(uint32_t *g, uint32_t n, uint32_t *g1, uint32_t n1max, uint32_t mode);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_pickle(gt_word_type* p_gt, uint32_t *buf, uint32_t maxlen);
// %%EXPORT p
MM_REDUCE_API
int32_t gt_word_len_pickle(gt_word_type* p_gt);
/// @endcond  
#ifdef __cplusplus
}
#endif


// %%FROM mm_vector_v1_mod3.c
/// @cond DO_NOT_DOCUMENT 
// %%EXPORT px
MM_REDUCE_API
void mm_order_load_vector_v1_mod3(uint_mmv_t *p_dest);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_compare_v1_mod3(uint_mmv_t *v);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_order_find_Gx0_via_v1_mod3(uint_mmv_t *v,  uint32_t *g);
/// @endcond 

// %%FROM mm_profile_abc_mod3.c
/// @cond DO_NOT_DOCUMENT
// %%EXPORT px
MM_REDUCE_API
int32_t mm_profile_mod3_load(uint32_t p, uint_mmv_t *v, uint64_t *a, uint32_t t);
// %%EXPORT px
MM_REDUCE_API
int64_t mm_profile_mod3_hash(uint64_t *a, uint16_t *b, uint32_t mode);
// %%EXPORT px
MM_REDUCE_API
int32_t mm_profile_mod3_permute24(uint16_t *b, uint8_t *p, uint16_t *b1);
/// @endcond 

// %%FROM mm_profile_graph24.c
/// @cond DO_NOT_DOCUMENT
// %%EXPORT px
MM_REDUCE_API
void mm_profile_graph24(uint16_t *b);
/// @endcond 

// %%INCLUDE_HEADERS



#endif  // #ifndef MM_REDUCE_H


