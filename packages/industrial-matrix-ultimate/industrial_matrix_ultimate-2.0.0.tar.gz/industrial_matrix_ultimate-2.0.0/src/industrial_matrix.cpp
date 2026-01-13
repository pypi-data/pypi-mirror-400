#include "industrial_matrix.hpp"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <random>
#include <stdexcept>

#ifdef _OPENMP
#include <omp.h>
#endif

#ifdef __AVX2__
#include <immintrin.h>
#endif

namespace industrial_matrix {

// SIMD kernels
namespace simd {
#ifdef __AVX2__
inline void add_float_avx2(const float *a, const float *b, float *r, size_t n) {
  size_t i = 0;
  for (; i + 8 <= n; i += 8) {
    __m256 va = _mm256_load_ps(a + i);
    __m256 vb = _mm256_load_ps(b + i);
    __m256 vr = _mm256_add_ps(va, vb);
    _mm256_store_ps(r + i, vr);
  }
  for (; i < n; ++i)
    r[i] = a[i] + b[i];
}

inline void add_double_avx2(const double *a, const double *b, double *r,
                            size_t n) {
  size_t i = 0;
  for (; i + 4 <= n; i += 4) {
    __m256d va = _mm256_load_pd(a + i);
    __m256d vb = _mm256_load_pd(b + i);
    __m256d vr = _mm256_add_pd(va, vb);
    _mm256_store_pd(r + i, vr);
  }
  for (; i < n; ++i)
    r[i] = a[i] + b[i];
}
#endif
} // namespace simd

// Matrix implementation
template <typename T> class Matrix<T>::Impl {
private:
  std::unique_ptr<T[]> data_;
  size_t rows_;
  size_t cols_;
  size_t stride_;

  void check_index(size_t i, size_t j) const {
    if (i >= rows_ || j >= cols_) {
      throw std::out_of_range("Matrix index out of range");
    }
  }

public:
  Impl(size_t rows, size_t cols, T init = T(0))
      : rows_(rows), cols_(cols), stride_(cols) {

    if (rows == 0 || cols == 0) {
      throw std::invalid_argument("Matrix dimensions cannot be zero");
    }

    data_ = std::make_unique<T[]>(rows * cols);
    std::fill(data_.get(), data_.get() + rows * cols, init);
  }

  Impl(const Impl &other)
      : rows_(other.rows_), cols_(other.cols_), stride_(other.cols_) {

    data_ = std::make_unique<T[]>(rows_ * cols_);
    std::copy(other.data_.get(), other.data_.get() + rows_ * cols_,
              data_.get());
  }

  // Getters
  size_t rows() const { return rows_; }
  size_t cols() const { return cols_; }
  size_t size() const { return rows_ * cols_; }
  T *data() { return data_.get(); }
  const T *data() const { return data_.get(); }

  // Element access
  T &at(size_t i, size_t j) {
    check_index(i, j);
    return data_[i * stride_ + j];
  }

  const T &at(size_t i, size_t j) const {
    check_index(i, j);
    return data_[i * stride_ + j];
  }

  // Matrix multiplication (optimized)
  std::unique_ptr<Impl> matmul(const Impl &other) const {
    if (cols_ != other.rows_) {
      throw std::invalid_argument(
          "Matrix dimensions mismatch for multiplication");
    }

    auto result = std::make_unique<Impl>(rows_, other.cols_, T(0));
    const size_t block_size = 64;

#pragma omp parallel for collapse(2) schedule(dynamic)
    for (size_t bi = 0; bi < rows_; bi += block_size) {
      for (size_t bj = 0; bj < other.cols_; bj += block_size) {
        for (size_t bk = 0; bk < cols_; bk += block_size) {

          size_t i_end = std::min(bi + block_size, rows_);
          size_t j_end = std::min(bj + block_size, other.cols_);
          size_t k_end = std::min(bk + block_size, cols_);

          for (size_t i = bi; i < i_end; ++i) {
            T *row_c = result->data_.get() + i * result->stride_;
            const T *row_a = data_.get() + i * stride_;

            for (size_t k = bk; k < k_end; ++k) {
              T aik = row_a[k];
              const T *row_b = other.data_.get() + k * other.stride_;

#pragma omp simd
              for (size_t j = bj; j < j_end; ++j) {
                row_c[j] += aik * row_b[j];
              }
            }
          }
        }
      }
    }

    return result;
  }

  // Transpose
  std::unique_ptr<Impl> transpose() const {
    auto result = std::make_unique<Impl>(cols_, rows_);

#pragma omp parallel for collapse(2)
    for (size_t i = 0; i < rows_; ++i) {
      for (size_t j = 0; j < cols_; ++j) {
        result->at(j, i) = at(i, j);
      }
    }

    return result;
  }

  // Element-wise operations
  std::unique_ptr<Impl> elementwise_add(const Impl &other) const {
    if (rows_ != other.rows_ || cols_ != other.cols_) {
      throw std::invalid_argument("Matrix dimensions mismatch");
    }

    auto result = std::make_unique<Impl>(rows_, cols_);
    const size_t n = size();
    const T *a = data_.get();
    const T *b = other.data_.get();
    T *r = result->data_.get();

#ifdef __AVX2__
    if constexpr (std::is_same_v<T, float>) {
      simd::add_float_avx2(a, b, r, n);
      return result;
    } else if constexpr (std::is_same_v<T, double>) {
      simd::add_double_avx2(a, b, r, n);
      return result;
    }
#endif

#pragma omp parallel for
    for (size_t i = 0; i < n; ++i) {
      r[i] = a[i] + b[i];
    }

    return result;
  }

  // Print matrix
  void print(const std::string &name) const {
    if (!name.empty()) {
      std::cout << name << " (" << rows_ << "x" << cols_ << "):\n";
    }

    size_t max_rows = std::min(rows_, size_t(10));
    size_t max_cols = std::min(cols_, size_t(10));

    for (size_t i = 0; i < max_rows; ++i) {
      for (size_t j = 0; j < max_cols; ++j) {
        if constexpr (std::is_integral_v<T>) {
          std::cout << std::setw(6) << at(i, j);
        } else {
          std::cout << std::fixed << std::setprecision(3) << std::setw(8)
                    << at(i, j);
        }
      }
      if (max_cols < cols_)
        std::cout << " ...";
      std::cout << "\n";
    }
    if (max_rows < rows_) {
      std::cout << "... (" << rows_ - max_rows << " more rows)\n";
    }
    std::cout << std::endl;
  }
};

// ========== Matrix class method implementations ==========

template <typename T> Matrix<T> Matrix<T>::zeros(size_t rows, size_t cols) {
  return Matrix(rows, cols, T(0));
}

template <typename T> Matrix<T> Matrix<T>::ones(size_t rows, size_t cols) {
  return Matrix(rows, cols, T(1));
}

template <typename T> Matrix<T> Matrix<T>::identity(size_t n) {
  Matrix mat(n, n, T(0));
  for (size_t i = 0; i < n; ++i) {
    mat(i, i) = T(1);
  }
  return mat;
}

template <typename T>
Matrix<T> Matrix<T>::random(size_t rows, size_t cols, T min, T max) {
  Matrix mat(rows, cols);
  std::random_device rd;
  std::mt19937 gen(rd());

  if constexpr (std::is_floating_point_v<T>) {
    std::uniform_real_distribution<T> dist(min, max);
    for (size_t i = 0; i < rows * cols; ++i) {
      mat.impl_->data()[i] = dist(gen);
    }
  } else {
    std::uniform_int_distribution<T> dist(min, max);
    for (size_t i = 0; i < rows * cols; ++i) {
      mat.impl_->data()[i] = dist(gen);
    }
  }

  return mat;
}

template <typename T>
Matrix<T>::Matrix() : impl_(std::make_unique<Impl>(1, 1)) {}

template <typename T>
Matrix<T>::Matrix(size_t rows, size_t cols)
    : impl_(std::make_unique<Impl>(rows, cols)) {}

template <typename T>
Matrix<T>::Matrix(size_t rows, size_t cols, T value)
    : impl_(std::make_unique<Impl>(rows, cols, value)) {}

template <typename T>
Matrix<T>::Matrix(const Matrix &other)
    : impl_(std::make_unique<Impl>(*other.impl_)) {}

template <typename T>
Matrix<T>::Matrix(Matrix &&other) noexcept : impl_(std::move(other.impl_)) {}

template <typename T> Matrix<T>::~Matrix() = default;

template <typename T> Matrix<T> &Matrix<T>::operator=(const Matrix &other) {
  if (this != &other) {
    impl_ = std::make_unique<Impl>(*other.impl_);
  }
  return *this;
}

template <typename T> Matrix<T> &Matrix<T>::operator=(Matrix &&other) noexcept {
  if (this != &other) {
    impl_ = std::move(other.impl_);
  }
  return *this;
}

template <typename T> size_t Matrix<T>::rows() const { return impl_->rows(); }

template <typename T> size_t Matrix<T>::cols() const { return impl_->cols(); }

template <typename T> size_t Matrix<T>::size() const { return impl_->size(); }

template <typename T> bool Matrix<T>::empty() const {
  return impl_->size() == 0;
}

template <typename T> std::pair<size_t, size_t> Matrix<T>::shape() const {
  return {impl_->rows(), impl_->cols()};
}

template <typename T> T &Matrix<T>::operator()(size_t i, size_t j) {
  return impl_->at(i, j);
}

template <typename T> const T &Matrix<T>::operator()(size_t i, size_t j) const {
  return impl_->at(i, j);
}

template <typename T>
Matrix<T> Matrix<T>::elementwise_add(const Matrix &other) const {
  Matrix result;
  result.impl_ = impl_->elementwise_add(*other.impl_);
  return result;
}

template <typename T>
Matrix<T> Matrix<T>::elementwise_subtract(const Matrix &other) const {
  Matrix result(rows(), cols());
  for (size_t i = 0; i < rows(); ++i) {
    for (size_t j = 0; j < cols(); ++j) {
      result(i, j) = (*this)(i, j) - other(i, j);
    }
  }
  return result;
}

template <typename T>
Matrix<T> Matrix<T>::elementwise_multiply(const Matrix &other) const {
  Matrix result(rows(), cols());
  for (size_t i = 0; i < rows(); ++i) {
    for (size_t j = 0; j < cols(); ++j) {
      result(i, j) = (*this)(i, j) * other(i, j);
    }
  }
  return result;
}

template <typename T>
Matrix<T> Matrix<T>::elementwise_divide(const Matrix &other) const {
  Matrix result(rows(), cols());
  for (size_t i = 0; i < rows(); ++i) {
    for (size_t j = 0; j < cols(); ++j) {
      result(i, j) = (*this)(i, j) / other(i, j);
    }
  }
  return result;
}

template <typename T>
Matrix<T> Matrix<T>::matrix_multiply(const Matrix &other) const {
  Matrix result;
  result.impl_ = impl_->matmul(*other.impl_);
  return result;
}

template <typename T> Matrix<T> Matrix<T>::transpose() const {
  Matrix result;
  result.impl_ = impl_->transpose();
  return result;
}

template <typename T> Matrix<T> Matrix<T>::scalar_add(T scalar) const {
  Matrix result(rows(), cols());
  for (size_t i = 0; i < rows(); ++i) {
    for (size_t j = 0; j < cols(); ++j) {
      result(i, j) = (*this)(i, j) + scalar;
    }
  }
  return result;
}

template <typename T> Matrix<T> Matrix<T>::scalar_multiply(T scalar) const {
  Matrix result(rows(), cols());
  for (size_t i = 0; i < rows(); ++i) {
    for (size_t j = 0; j < cols(); ++j) {
      result(i, j) = (*this)(i, j) * scalar;
    }
  }
  return result;
}

template <typename T> T Matrix<T>::frobenius_norm() const {
  T sum = T(0);
  const size_t n = size();
  const T *data = impl_->data();

#pragma omp parallel for reduction(+ : sum)
  for (size_t i = 0; i < n; ++i) {
    sum += data[i] * data[i];
  }

  return std::sqrt(sum);
}

template <typename T> T Matrix<T>::infinity_norm() const {
  T max_sum = T(0);
  for (size_t i = 0; i < rows(); ++i) {
    T row_sum = T(0);
    for (size_t j = 0; j < cols(); ++j) {
      row_sum += std::abs((*this)(i, j));
    }
    max_sum = std::max(max_sum, row_sum);
  }
  return max_sum;
}

template <typename T> T Matrix<T>::trace() const {
  T sum = T(0);
  size_t n = std::min(rows(), cols());
  for (size_t i = 0; i < n; ++i) {
    sum += (*this)(i, i);
  }
  return sum;
}

template <typename T> T Matrix<T>::sum() const {
  T total = T(0);
  const size_t n = size();
  const T *data = impl_->data();

#pragma omp parallel for reduction(+ : total)
  for (size_t i = 0; i < n; ++i) {
    total += data[i];
  }
  return total;
}

template <typename T> void Matrix<T>::fill(T value) {
  T *data = impl_->data();
  const size_t n = size();
  std::fill(data, data + n, value);
}

template <typename T> Matrix<T> Matrix<T>::copy() const {
  return Matrix(*this);
}

template <typename T> std::vector<T> Matrix<T>::to_vector() const {
  const T *data = impl_->data();
  const size_t n = size();
  return std::vector<T>(data, data + n);
}

template <typename T> void Matrix<T>::print(const std::string &name) const {
  impl_->print(name);
}

template <typename T>
bool Matrix<T>::save_to_file(const std::string &filename) const {
  std::ofstream file(filename, std::ios::binary);
  if (!file)
    return false;

  size_t r = rows(), c = cols();
  file.write(reinterpret_cast<const char *>(&r), sizeof(size_t));
  file.write(reinterpret_cast<const char *>(&c), sizeof(size_t));
  file.write(reinterpret_cast<const char *>(impl_->data()), size() * sizeof(T));

  return file.good();
}

template <typename T>
Matrix<T> Matrix<T>::load_from_file(const std::string &filename) {
  std::ifstream file(filename, std::ios::binary);
  if (!file)
    throw std::runtime_error("Cannot open file");

  size_t r, c;
  file.read(reinterpret_cast<char *>(&r), sizeof(size_t));
  file.read(reinterpret_cast<char *>(&c), sizeof(size_t));

  Matrix mat(r, c);
  file.read(reinterpret_cast<char *>(mat.impl_->data()), r * c * sizeof(T));

  return mat;
}

template <typename T>
Matrix<T> Matrix<T>::from_numpy(const T *data, size_t rows, size_t cols) {
  Matrix mat(rows, cols);
  std::copy(data, data + rows * cols, mat.impl_->data());
  return mat;
}

template <typename T> void Matrix<T>::to_numpy(T *data) const {
  std::copy(impl_->data(), impl_->data() + size(), data);
}

// Explicit template instantiations
template class Matrix<float>;
template class Matrix<double>;
template class Matrix<int32_t>;
template class Matrix<int64_t>;

} // namespace industrial_matrix
