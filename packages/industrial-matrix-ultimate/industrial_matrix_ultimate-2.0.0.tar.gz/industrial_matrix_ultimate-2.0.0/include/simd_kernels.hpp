#pragma once

#include <cstddef>

namespace industrial_matrix {
namespace simd {

#ifdef __AVX2__
void add_float_avx2(const float *a, const float *b, float *r, size_t n);
void add_double_avx2(const double *a, const double *b, double *r, size_t n);
void mul_float_avx2(const float *a, const float *b, float *r, size_t n);
void mul_double_avx2(const double *a, const double *b, double *r, size_t n);
#endif

} // namespace simd
} // namespace industrial_matrix
