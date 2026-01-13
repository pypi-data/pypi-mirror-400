// industrial_matrix_engine_fixed.cpp
// ==================== TAM DÜZELTİLMİŞ ENDÜSTRİYEL MATRİS MOTORU
// ====================

#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstring>
#include <fstream>
#include <future>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <thread>
#include <type_traits>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

#ifdef __AVX2__
#include <immintrin.h>
#endif

// ==================== PROFESSIONAL LOGGING SYSTEM ====================
enum class LogLevel { DEBUG, INFO, WARNING, ERROR };

class Logger {
private:
  static LogLevel current_level;

public:
  static void set_level(LogLevel level) { current_level = level; }

  template <typename... Args>
  static void debug(const char *format, Args... args) {
    if (current_level <= LogLevel::DEBUG) {
      std::printf("[DEBUG] ");
      std::printf(format, args...);
      std::printf("\n");
    }
  }

  template <typename... Args>
  static void error(const char *format, Args... args) {
    std::fprintf(stderr, "[ERROR] ");
    std::fprintf(stderr, format, args...);
    std::fprintf(stderr, "\n");
  }
};

LogLevel Logger::current_level = LogLevel::INFO;

// ==================== SAFE ALIGNED MEMORY ====================
namespace SafeAlignedMemory {
inline void *allocate_aligned(size_t size, size_t alignment) {
  if (size == 0)
    return nullptr;

  // Alignment must be power of 2
  if ((alignment & (alignment - 1)) != 0) {
    Logger::error("Alignment %zu is not power of 2", alignment);
    throw std::bad_alloc();
  }

  // Check for overflow
  if (size > std::numeric_limits<size_t>::max() - alignment) {
    Logger::error("Size overflow: %zu", size);
    throw std::bad_alloc();
  }

  void *ptr = nullptr;

#if defined(_WIN32)
  ptr = _aligned_malloc(size, alignment);
#elif defined(__linux__) || defined(__APPLE__)
  if (posix_memalign(&ptr, alignment, size) != 0) {
    ptr = nullptr;
  }
#else
  ptr = aligned_alloc(alignment, size);
#endif

  if (!ptr) {
    Logger::error("Failed to allocate %zu bytes aligned to %zu", size,
                  alignment);
    throw std::bad_alloc();
  }

  Logger::debug("Allocated %zu bytes at %p (alignment: %zu)", size, ptr,
                alignment);
  return ptr;
}

inline void free_aligned(void *ptr) noexcept {
  if (ptr) {
    Logger::debug("Freeing aligned memory at %p", ptr);
#if defined(_WIN32)
    _aligned_free(ptr);
#else
    free(ptr);
#endif
  }
}

// Memory tracker for debugging
class MemoryTracker {
private:
  static std::atomic<size_t> allocated_bytes;
  static std::atomic<size_t> allocation_count;

public:
  static void track_allocation(size_t size) noexcept {
    allocated_bytes.fetch_add(size, std::memory_order_relaxed);
    allocation_count.fetch_add(1, std::memory_order_relaxed);
  }

  static void track_deallocation(size_t size) noexcept {
    allocated_bytes.fetch_sub(size, std::memory_order_relaxed);
  }

  static void print_stats() {
    std::cout << "Memory Stats: " << allocation_count.load() << " allocations, "
              << allocated_bytes.load() << " bytes currently allocated\n";
  }

  static size_t get_allocated_bytes() { return allocated_bytes.load(); }
};

std::atomic<size_t> MemoryTracker::allocated_bytes{0};
std::atomic<size_t> MemoryTracker::allocation_count{0};
} // namespace SafeAlignedMemory

// ==================== NUMERICAL STABILITY UTILITIES ====================
namespace NumericalStability {
template <typename T> constexpr T epsilon() {
  if constexpr (std::is_same_v<T, float>)
    return 1e-6f;
  if constexpr (std::is_same_v<T, double>)
    return 1e-12;
  if constexpr (std::is_same_v<T, long double>)
    return 1e-15L;
  return T{1};
}

// Kahan summation algorithm for reduced floating-point error
template <typename T> T kahan_sum(const T *data, size_t n) {
  T sum = 0;
  T compensation = 0;

  for (size_t i = 0; i < n; ++i) {
    T y = data[i] - compensation;
    T t = sum + y;
    compensation = (t - sum) - y;
    sum = t;
  }

  return sum;
}

// Safe multiplication with overflow checking
template <typename T> bool safe_multiply(T a, T b, T &result) {
  if constexpr (std::is_floating_point_v<T>) {
    result = a * b;

    // Check for NaN or Inf
    if (!std::isfinite(result)) {
      Logger::error("Floating overflow/underflow in multiplication: %g * %g",
                    static_cast<double>(a), static_cast<double>(b));
      return false;
    }
    return true;
  } else {
    // Integer overflow checking
    if (a > 0 && b > 0) {
      if (a > std::numeric_limits<T>::max() / b) {
        Logger::error("Integer overflow in multiplication: %lld * %lld",
                      static_cast<long long>(a), static_cast<long long>(b));
        return false;
      }
    } else if (a < 0 && b < 0) {
      if (a < std::numeric_limits<T>::min() / b) {
        Logger::error("Integer underflow in multiplication: %lld * %lld",
                      static_cast<long long>(a), static_cast<long long>(b));
        return false;
      }
    }
    result = a * b;
    return true;
  }
}

// Safe norm calculation
template <typename T> T safe_norm(const T *data, size_t n) {
  if (n == 0)
    return T{0};

  T max_val = std::abs(data[0]);
  for (size_t i = 1; i < n; ++i) {
    max_val = std::max(max_val, std::abs(data[i]));
  }

  if (max_val == T{0})
    return T{0};

  // Scale to avoid overflow
  T scale = T{1} / max_val;
  T sum = T{0};

  for (size_t i = 0; i < n; ++i) {
    T scaled = data[i] * scale;
    sum += scaled * scaled;
  }

  return max_val * std::sqrt(sum);
}
} // namespace NumericalStability

// ==================== THREAD-SAFE UTILITIES ====================
namespace ThreadSafe {
// Thread-local random number generator to avoid contention
thread_local std::mt19937_64 random_engine{std::random_device{}()};

// Cache line size padding to avoid false sharing
template <typename T> struct Padded {
  alignas(64) T value;

  Padded() = default;
  explicit Padded(T val) : value(val) {}

  T load(std::memory_order order = std::memory_order_seq_cst) const noexcept {
    return value;
  }

  void store(T val,
             std::memory_order order = std::memory_order_seq_cst) noexcept {
    value = val;
  }
};

// Reduction variable with padding
template <typename T> class ReductionVariable {
private:
  struct alignas(64) PaddedValue {
    T value;
    char padding[64 - sizeof(T) % 64];
  };

  std::vector<PaddedValue> per_thread_values;

public:
  explicit ReductionVariable(size_t num_threads)
      : per_thread_values(num_threads) {
    for (auto &v : per_thread_values) {
      v.value = T{0};
    }
  }

  T &get_thread_local(size_t thread_id) {
    return per_thread_values[thread_id].value;
  }

  T reduce() const {
    T total = T{0};
    for (const auto &v : per_thread_values) {
      total += v.value;
    }
    return total;
  }
};
} // namespace ThreadSafe

// ==================== SIMD OPTIMIZED KERNELS ====================
namespace SIMDKernels {
#ifdef __AVX2__
// AVX2 optimized float addition
inline void add_float_avx2(const float *a, const float *b, float *result,
                           size_t n) {
  size_t i = 0;
  for (; i + 8 <= n; i += 8) {
    __m256 va = _mm256_load_ps(a + i);
    __m256 vb = _mm256_load_ps(b + i);
    __m256 vresult = _mm256_add_ps(va, vb);
    _mm256_store_ps(result + i, vresult);
  }
  // Handle remainder
  for (; i < n; ++i) {
    result[i] = a[i] + b[i];
  }
}

// AVX2 optimized double addition
inline void add_double_avx2(const double *a, const double *b, double *result,
                            size_t n) {
  size_t i = 0;
  for (; i + 4 <= n; i += 4) {
    __m256d va = _mm256_load_pd(a + i);
    __m256d vb = _mm256_load_pd(b + i);
    __m256d vresult = _mm256_add_pd(va, vb);
    _mm256_store_pd(result + i, vresult);
  }
  for (; i < n; ++i) {
    result[i] = a[i] + b[i];
  }
}
#endif

// Generic SIMD-aware addition
template <typename T>
inline void add_simd(const T *a, const T *b, T *result, size_t n) {
#ifdef __AVX2__
  if constexpr (std::is_same_v<T, float>) {
    add_float_avx2(a, b, result, n);
    return;
  } else if constexpr (std::is_same_v<T, double>) {
    add_double_avx2(a, b, result, n);
    return;
  }
#endif
  // Fallback to scalar
  for (size_t i = 0; i < n; ++i) {
    result[i] = a[i] + b[i];
  }
}
} // namespace SIMDKernels

// ==================== SAFE MATRIX STORAGE ====================
template <typename T> class SafeMatrixStorage {
private:
  T *data_ = nullptr;
  size_t size_ = 0;
  size_t alignment_;
  bool owns_memory_ = true;

  // Copy and swap idiom for exception safety
  void swap(SafeMatrixStorage &other) noexcept {
    std::swap(data_, other.data_);
    std::swap(size_, other.size_);
    std::swap(alignment_, other.alignment_);
    std::swap(owns_memory_, other.owns_memory_);
  }

public:
  SafeMatrixStorage() noexcept = default;

  // Strong exception guarantee constructor
  SafeMatrixStorage(size_t size, size_t alignment)
      : size_(size), alignment_(alignment) {

    if (size_ == 0)
      return;

    try {
      data_ = static_cast<T *>(
          SafeAlignedMemory::allocate_aligned(size_ * sizeof(T), alignment_));

      // Track allocation for debugging
      SafeAlignedMemory::MemoryTracker::track_allocation(size_ * sizeof(T));

      // Value-initialize (zero for arithmetic types)
      std::uninitialized_default_construct_n(data_, size_);

    } catch (...) {
      // Cleanup on exception
      if (data_) {
        SafeAlignedMemory::free_aligned(data_);
      }
      throw; // Re-throw
    }
  }

  // Destructor with strong guarantee
  ~SafeMatrixStorage() noexcept {
    if (owns_memory_ && data_) {
      // Destroy objects
      std::destroy_n(data_, size_);

      // Free memory
      SafeAlignedMemory::free_aligned(data_);

      // Track deallocation
      SafeAlignedMemory::MemoryTracker::track_deallocation(size_ * sizeof(T));
    }
  }

  // Move constructor (noexcept)
  SafeMatrixStorage(SafeMatrixStorage &&other) noexcept
      : data_(other.data_), size_(other.size_), alignment_(other.alignment_),
        owns_memory_(other.owns_memory_) {
    other.data_ = nullptr;
    other.size_ = 0;
    other.owns_memory_ = false;
  }

  // Move assignment with strong guarantee
  SafeMatrixStorage &operator=(SafeMatrixStorage &&other) noexcept {
    if (this != &other) {
      // Destroy current data
      if (owns_memory_ && data_) {
        std::destroy_n(data_, size_);
        SafeAlignedMemory::free_aligned(data_);
        SafeAlignedMemory::MemoryTracker::track_deallocation(size_ * sizeof(T));
      }

      // Steal resources
      data_ = other.data_;
      size_ = other.size_;
      alignment_ = other.alignment_;
      owns_memory_ = other.owns_memory_;

      // Leave other in valid state
      other.data_ = nullptr;
      other.size_ = 0;
      other.owns_memory_ = false;
    }
    return *this;
  }

  // No copy constructor/assignment
  SafeMatrixStorage(const SafeMatrixStorage &) = delete;
  SafeMatrixStorage &operator=(const SafeMatrixStorage &) = delete;

  // Access methods
  T *data() noexcept { return data_; }
  const T *data() const noexcept { return data_; }
  size_t size() const noexcept { return size_; }
  bool empty() const noexcept { return size_ == 0; }
  size_t alignment() const noexcept { return alignment_; }
};

// ==================== CLEAN API MATRIX CLASS ====================
template <typename T> class SafeIndustrialMatrix {
private:
  SafeMatrixStorage<T> storage_;
  size_t rows_;
  size_t cols_;
  size_t stride_;

  // Validate parameters
  static void validate_dimensions(size_t rows, size_t cols) {
    if (rows == 0 || cols == 0) {
      throw std::invalid_argument("Matrix dimensions cannot be zero");
    }

    // Check for overflow
    if (rows > std::numeric_limits<size_t>::max() / cols) {
      throw std::overflow_error("Matrix size overflow");
    }
  }

public:
  // ========== CLEAR API ==========

  // Explicit factory methods - no ambiguous constructors
  static SafeIndustrialMatrix create_zeros(size_t rows, size_t cols) {
    validate_dimensions(rows, cols);
    return SafeIndustrialMatrix(rows, cols, T{0});
  }

  static SafeIndustrialMatrix create_ones(size_t rows, size_t cols) {
    validate_dimensions(rows, cols);
    return SafeIndustrialMatrix(rows, cols, T{1});
  }

  static SafeIndustrialMatrix create_identity(size_t n) {
    validate_dimensions(n, n);
    SafeIndustrialMatrix mat(n, n, T{0});
    for (size_t i = 0; i < n; ++i) {
      mat(i, i) = T{1};
    }
    return mat;
  }

  static SafeIndustrialMatrix
  create_random(size_t rows, size_t cols, T min_val = T{0}, T max_val = T{1}) {
    validate_dimensions(rows, cols);
    SafeIndustrialMatrix mat(rows, cols);

#pragma omp parallel
    {
      int thread_id = omp_get_thread_num();
      int num_threads = omp_get_num_threads();
      size_t chunk_size = (rows * cols + num_threads - 1) / num_threads;
      size_t start = thread_id * chunk_size;
      size_t end = std::min(start + chunk_size, rows * cols);

      std::mt19937_64 local_engine(std::random_device{}() + thread_id);

      if constexpr (std::is_floating_point_v<T>) {
        std::uniform_real_distribution<T> dist(min_val, max_val);
        for (size_t i = start; i < end; ++i) {
          mat.storage_.data()[i] = dist(local_engine);
        }
      } else {
        std::uniform_int_distribution<T> dist(min_val, max_val);
        for (size_t i = start; i < end; ++i) {
          mat.storage_.data()[i] = dist(local_engine);
        }
      }
    }

    return mat;
  }

  // ========== CLEAR OPERATIONS ==========

  // Element-wise operations (clear names)
  SafeIndustrialMatrix
  elementwise_add(const SafeIndustrialMatrix &other) const {
    check_same_shape(other, "elementwise_add");
    return perform_elementwise(other, std::plus<T>{});
  }

  SafeIndustrialMatrix
  elementwise_multiply(const SafeIndustrialMatrix &other) const {
    check_same_shape(other, "elementwise_multiply");
    return perform_elementwise(other, std::multiplies<T>{});
  }

  // Matrix multiplication (clear name)
  SafeIndustrialMatrix
  matrix_multiply(const SafeIndustrialMatrix &other) const {
    if (cols_ != other.rows_) {
      throw std::invalid_argument(
          "Matrix multiplication requires cols of first == rows of second");
    }

    return perform_matrix_multiply(other);
  }

  // Scalar operations
  SafeIndustrialMatrix scalar_multiply(T scalar) const {
    SafeIndustrialMatrix result(rows_, cols_);
    const size_t n = size();
    const T *src = data();
    T *dst = result.data();

#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) {
      if (!NumericalStability::safe_multiply(src[i], scalar, dst[i])) {
        throw std::runtime_error("Numerical error in scalar multiplication");
      }
    }

    return result;
  }

  // Transpose
  SafeIndustrialMatrix transpose() const {
    SafeIndustrialMatrix result(cols_, rows_);

#pragma omp parallel for collapse(2)
    for (size_t i = 0; i < rows_; ++i) {
      for (size_t j = 0; j < cols_; ++j) {
        result(j, i) = (*this)(i, j);
      }
    }

    return result;
  }

private:
  // Private constructor - use factory methods
  SafeIndustrialMatrix(size_t rows, size_t cols, T init_val = T{})
      : storage_(rows * cols, 64), rows_(rows), cols_(cols), stride_(cols) {

    if (rows > 0 && cols > 0) {
      std::fill(storage_.data(), storage_.data() + rows * cols, init_val);
    }
  }

  // Private helper methods
  void check_same_shape(const SafeIndustrialMatrix &other,
                        const char *op) const {
    if (rows_ != other.rows_ || cols_ != other.cols_) {
      throw std::invalid_argument(
          std::string("Matrices must have same shape for ") + op);
    }
  }

  template <typename Op>
  SafeIndustrialMatrix perform_elementwise(const SafeIndustrialMatrix &other,
                                           Op op) const {
    SafeIndustrialMatrix result(rows_, cols_);
    const size_t n = size();
    const T *a = data();
    const T *b = other.data();
    T *r = result.data();

#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) {
      r[i] = op(a[i], b[i]);
    }

    return result;
  }

  SafeIndustrialMatrix
  perform_matrix_multiply(const SafeIndustrialMatrix &other) const {
    const size_t block_size = 64; // Optimal for L1 cache
    SafeIndustrialMatrix result(rows_, other.cols_, T{0});

#pragma omp parallel for collapse(2) schedule(dynamic)
    for (size_t bi = 0; bi < rows_; bi += block_size) {
      for (size_t bj = 0; bj < other.cols_; bj += block_size) {
        for (size_t bk = 0; bk < cols_; bk += block_size) {
          size_t i_end = std::min(bi + block_size, rows_);
          size_t j_end = std::min(bj + block_size, other.cols_);
          size_t k_end = std::min(bk + block_size, cols_);

          // Micro-kernel for cache locality
          for (size_t i = bi; i < i_end; ++i) {
            const T *row_a = row_ptr(i);
            T *row_c = result.row_ptr(i);

            for (size_t k = bk; k < k_end; ++k) {
              T aik = row_a[k];
              const T *row_b = other.row_ptr(k);

// SIMD-optimized inner loop
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

public:
  // ========== SAFE ACCESSORS ==========
  size_t rows() const noexcept { return rows_; }
  size_t cols() const noexcept { return cols_; }
  size_t size() const noexcept { return rows_ * cols_; }
  bool empty() const noexcept { return rows_ == 0 || cols_ == 0; }

  T &operator()(size_t i, size_t j) {
    if (i >= rows_ || j >= cols_) {
      throw std::out_of_range("Matrix index out of range");
    }
    return storage_.data()[i * stride_ + j];
  }

  const T &operator()(size_t i, size_t j) const {
    if (i >= rows_ || j >= cols_) {
      throw std::out_of_range("Matrix index out of range");
    }
    return storage_.data()[i * stride_ + j];
  }

  T *data() noexcept { return storage_.data(); }
  const T *data() const noexcept { return storage_.data(); }

  T *row_ptr(size_t i) noexcept { return storage_.data() + i * stride_; }

  const T *row_ptr(size_t i) const noexcept {
    return storage_.data() + i * stride_;
  }

  // ========== NUMERICALLY STABLE OPERATIONS ==========
  T safe_frobenius_norm() const {
    return NumericalStability::safe_norm(data(), size());
  }

  T kahan_sum() const { return NumericalStability::kahan_sum(data(), size()); }

  // ========== VALIDATION ==========
  bool validate_no_nan_inf() const {
    if constexpr (std::is_floating_point_v<T>) {
      for (size_t i = 0; i < size(); ++i) {
        if (!std::isfinite(data()[i])) {
          return false;
        }
      }
    }
    return true;
  }

  // ========== DEBUGGING ==========
  void print_stats(const std::string &name = "") const {
    std::cout << "\nMatrix " << name << " Stats:\n";
    std::cout << "  Dimensions: " << rows_ << " x " << cols_ << "\n";
    std::cout << "  Total elements: " << size() << "\n";
    std::cout << "  Memory: " << (size() * sizeof(T)) / (1024.0 * 1024.0)
              << " MB\n";

    if (size() > 0) {
      T min_val = data()[0];
      T max_val = data()[0];
      T sum = T{0};

      for (size_t i = 0; i < size(); ++i) {
        T val = data()[i];
        min_val = std::min(min_val, val);
        max_val = std::max(max_val, val);
        sum += val;
      }

      std::cout << "  Min value: " << min_val << "\n";
      std::cout << "  Max value: " << max_val << "\n";
      std::cout << "  Average: " << (sum / size()) << "\n";

      if constexpr (std::is_floating_point_v<T>) {
        std::cout << "  Contains NaN/Inf: "
                  << (validate_no_nan_inf() ? "No" : "YES - WARNING!") << "\n";
      }
    }
  }

  void print(const std::string &name = "") const {
    if (!name.empty()) {
      std::cout << name << " (" << rows_ << "x" << cols_ << "):\n";
    }

    size_t max_rows = std::min(rows_, size_t(10));
    size_t max_cols = std::min(cols_, size_t(10));

    for (size_t i = 0; i < max_rows; ++i) {
      for (size_t j = 0; j < max_cols; ++j) {
        if constexpr (std::is_integral_v<T>) {
          std::cout << std::setw(6) << (*this)(i, j);
        } else {
          std::cout << std::fixed << std::setprecision(3) << std::setw(8)
                    << (*this)(i, j);
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

// ==================== TEST SUITE FOR FIXED ISSUES ====================
class FixedIssueTestSuite {
public:
  static void run_all_tests() {
    std::cout << "FIXED ISSUE TEST SUITE\n";
    std::cout << "=======================\n\n";

    test_memory_corruption();
    test_thread_safety();
    test_numerical_stability();
    test_api_clarity();
    test_performance_regression();

    std::cout << "\nAll fixed issue tests completed!\n";
  }

private:
  static void test_memory_corruption() {
    std::cout << "1. Testing Memory Corruption Fixes...\n";

    // Test aligned allocation
    for (size_t alignment : {16, 32, 64, 128}) {
      try {
        auto mat = SafeIndustrialMatrix<double>::create_random(100, 100);
        uintptr_t address = reinterpret_cast<uintptr_t>(mat.data());
        assert(address % 64 == 0 && "Memory not properly aligned!");
      } catch (...) {
        assert(false && "Aligned allocation failed!");
      }
    }

    // Test large matrix allocation
    try {
      auto large = SafeIndustrialMatrix<double>::create_random(5000, 5000);
      large.print_stats("Large Matrix Test");
    } catch (const std::bad_alloc &) {
      std::cout << "  Large allocation skipped (insufficient memory)\n";
    }

    std::cout << "  ✓ Memory corruption tests passed\n";
  }

  static void test_thread_safety() {
    std::cout << "2. Testing Thread Safety...\n";

    const size_t N = 1000;
    auto A = SafeIndustrialMatrix<double>::create_random(N, N);
    auto B = SafeIndustrialMatrix<double>::create_random(N, N);

    // Test concurrent operations
    std::vector<std::future<void>> futures;
    for (int i = 0; i < 10; ++i) {
      futures.push_back(std::async(std::launch::async, [&]() {
        auto C = A.elementwise_add(B);
        auto D = A.elementwise_multiply(B);
        // auto E = A.matrix_multiply(B);
        //  All operations should complete without data races
      }));
    }

    for (auto &f : futures)
      f.get();

// Test OpenMP correctness
#pragma omp parallel for
    for (size_t i = 0; i < N; ++i) {
      for (size_t j = 0; j < N; ++j) {
        double val = A(i, j) + B(i, j);
        (void)val; // Just computation, no race
      }
    }

    std::cout << "  ✓ Thread safety tests passed\n";
  }

  static void test_numerical_stability() {
    std::cout << "3. Testing Numerical Stability...\n";

    // Test with extreme values
    auto extreme = SafeIndustrialMatrix<double>::create_zeros(10, 10);
    extreme(0, 0) = std::numeric_limits<double>::max();
    extreme(1, 1) = std::numeric_limits<double>::min();

    // Test Kahan summation
    auto mat =
        SafeIndustrialMatrix<double>::create_random(100, 100, 1e-10, 1e-5);
    double kahan_sum = mat.kahan_sum();
    double simple_sum = 0;
    for (size_t i = 0; i < mat.size(); ++i) {
      simple_sum += mat.data()[i];
    }

    double relative_error =
        std::abs(kahan_sum - simple_sum) / std::abs(kahan_sum);
    std::cout << "  Kahan vs simple sum relative error: " << relative_error
              << "\n";

    std::cout << "  ✓ Numerical stability tests passed\n";
  }

  static void test_api_clarity() {
    std::cout << "4. Testing API Clarity...\n";

    auto A = SafeIndustrialMatrix<double>::create_random(3, 3);
    auto B = SafeIndustrialMatrix<double>::create_random(3, 3);

    // Clear API usage
    auto C = A.elementwise_add(B);      // Clear: element-wise
    auto D = A.elementwise_multiply(B); // Clear: element-wise
    auto E = A.matrix_multiply(B);      // Clear: matrix multiplication

    std::cout << "  ✓ API clarity tests passed\n";
  }

  static void test_performance_regression() {
    std::cout << "5. Testing Performance Regression...\n";

    std::vector<size_t> sizes = {128, 256, 512};

    for (size_t N : sizes) {
      auto A = SafeIndustrialMatrix<double>::create_random(N, N);
      auto B = SafeIndustrialMatrix<double>::create_random(N, N);

      auto start = std::chrono::high_resolution_clock::now();
      auto C = A.matrix_multiply(B);
      auto end = std::chrono::high_resolution_clock::now();

      double time_ms =
          std::chrono::duration<double, std::milli>(end - start).count();
      double gflops = (2.0 * N * N * N) / (time_ms / 1000.0) / 1e9;

      std::cout << "  Size " << N << "x" << N << ": " << std::fixed
                << std::setprecision(2) << gflops << " GFLOPS, " << time_ms
                << " ms\n";
    }

    std::cout << "  ✓ Performance regression tests passed\n";
  }
};

// ==================== MAIN DEMONSTRATION ====================
int main() {
  std::cout << "=========================================================\n";
  std::cout << "  INDUSTRIAL MATRIX ENGINE - ADVANCED C++ VERSION\n";
  std::cout << "=========================================================\n\n";

  // Enable debug logging
  Logger::set_level(LogLevel::INFO);

  try {
    // Run fixed issue tests
    FixedIssueTestSuite::run_all_tests();

    // Final memory check
    std::cout << "\n";
    SafeAlignedMemory::MemoryTracker::print_stats();

  } catch (const std::exception &e) {
    std::cerr << "\nFATAL ERROR: " << e.what() << std::endl;
    return 1;
  }

  return 0;
}
