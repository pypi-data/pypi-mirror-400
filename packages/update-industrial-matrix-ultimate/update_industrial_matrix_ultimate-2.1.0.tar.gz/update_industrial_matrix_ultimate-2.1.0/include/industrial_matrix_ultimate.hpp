// industrial_matrix_ultimate.hpp
// Ultimate Matrix Library - Header Only Core
#pragma once

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
#include <memory>
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

namespace industrial_matrix {

// Forward declarations
template <typename T> class UltimateMatrix;

// Type aliases
using MatrixF32 = UltimateMatrix<float>;
using MatrixF64 = UltimateMatrix<double>;
using MatrixI32 = UltimateMatrix<int32_t>;
using MatrixI64 = UltimateMatrix<int64_t>;

// ==================== SAFE ALIGNED MEMORY ====================
namespace memory {
inline void *allocate_aligned(size_t size, size_t alignment) {
  if (size == 0)
    return nullptr;

  if ((alignment & (alignment - 1)) != 0) {
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

  if (!ptr)
    throw std::bad_alloc();
  return ptr;
}

inline void free_aligned(void *ptr) noexcept {
  if (ptr) {
#if defined(_WIN32)
    _aligned_free(ptr);
#else
    free(ptr);
#endif
  }
}
} // namespace memory

// ==================== NUMERICAL STABILITY ====================
namespace numerical {
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

template <typename T> T safe_norm(const T *data, size_t n) {
  if (n == 0)
    return T{0};

  T max_val = std::abs(data[0]);
  for (size_t i = 1; i < n; ++i) {
    max_val = std::max(max_val, std::abs(data[i]));
  }

  if (max_val == T{0})
    return T{0};

  T scale = T{1} / max_val;
  T sum = T{0};

  for (size_t i = 0; i < n; ++i) {
    T scaled = data[i] * scale;
    sum += scaled * scaled;
  }

  return max_val * std::sqrt(sum);
}
} // namespace numerical

// ==================== ULTIMATE MATRIX CLASS ====================
template <typename T> class UltimateMatrix {
private:
  std::unique_ptr<T, decltype(&memory::free_aligned)> data_;
  size_t rows_;
  size_t cols_;
  size_t stride_;

  static void validate_dimensions(size_t rows, size_t cols) {
    if (rows == 0 || cols == 0) {
      throw std::invalid_argument("Matrix dimensions cannot be zero");
    }
    if (rows > std::numeric_limits<size_t>::max() / cols) {
      throw std::overflow_error("Matrix size overflow");
    }
  }

  // Private constructor
  UltimateMatrix(size_t rows, size_t cols, T init_val = T{})
      : data_(nullptr, &memory::free_aligned), rows_(rows), cols_(cols),
        stride_(cols) {

    T *ptr =
        static_cast<T *>(memory::allocate_aligned(rows * cols * sizeof(T), 64));
    data_.reset(ptr);
    std::fill(ptr, ptr + rows * cols, init_val);
  }

public:
  // ========== FACTORY METHODS ==========
  static UltimateMatrix zeros(size_t rows, size_t cols) {
    validate_dimensions(rows, cols);
    return UltimateMatrix(rows, cols, T{0});
  }

  static UltimateMatrix ones(size_t rows, size_t cols) {
    validate_dimensions(rows, cols);
    return UltimateMatrix(rows, cols, T{1});
  }

  static UltimateMatrix identity(size_t n) {
    validate_dimensions(n, n);
    UltimateMatrix mat(n, n, T{0});
    for (size_t i = 0; i < n; ++i) {
      mat(i, i) = T{1};
    }
    return mat;
  }

  static UltimateMatrix random(size_t rows, size_t cols, T min_val = T{0},
                               T max_val = T{1}) {
    validate_dimensions(rows, cols);
    UltimateMatrix mat(rows, cols);

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
          mat.data_.get()[i] = dist(local_engine);
        }
      } else {
        std::uniform_int_distribution<T> dist(min_val, max_val);
        for (size_t i = start; i < end; ++i) {
          mat.data_.get()[i] = dist(local_engine);
        }
      }
    }

    return mat;
  }

  // ========== CORE OPERATIONS ==========
  UltimateMatrix elementwise_add(const UltimateMatrix &other) const {
    if (rows_ != other.rows_ || cols_ != other.cols_) {
      throw std::invalid_argument("Matrices must have same shape");
    }

    UltimateMatrix result(rows_, cols_);
    const size_t n = rows_ * cols_;

#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) {
      result.data_.get()[i] = data_.get()[i] + other.data_.get()[i];
    }

    return result;
  }

  UltimateMatrix elementwise_multiply(const UltimateMatrix &other) const {
    if (rows_ != other.rows_ || cols_ != other.cols_) {
      throw std::invalid_argument("Matrices must have same shape");
    }

    UltimateMatrix result(rows_, cols_);
    const size_t n = rows_ * cols_;

#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) {
      result.data_.get()[i] = data_.get()[i] * other.data_.get()[i];
    }

    return result;
  }

  UltimateMatrix matrix_multiply(const UltimateMatrix &other) const {
    if (cols_ != other.rows_) {
      throw std::invalid_argument("Matrix dimension mismatch");
    }

    const size_t block_size = 64;
    UltimateMatrix result(rows_, other.cols_, T{0});

#pragma omp parallel for collapse(2) schedule(dynamic)
    for (size_t bi = 0; bi < rows_; bi += block_size) {
      for (size_t bj = 0; bj < other.cols_; bj += block_size) {
        for (size_t bk = 0; bk < cols_; bk += block_size) {
          size_t i_end = std::min(bi + block_size, rows_);
          size_t j_end = std::min(bj + block_size, other.cols_);
          size_t k_end = std::min(bk + block_size, cols_);

          for (size_t i = bi; i < i_end; ++i) {
            T *row_a = data_.get() + i * stride_;
            T *row_c = result.data_.get() + i * result.stride_;

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

  UltimateMatrix transpose() const {
    UltimateMatrix result(cols_, rows_);

#pragma omp parallel for collapse(2)
    for (size_t i = 0; i < rows_; ++i) {
      for (size_t j = 0; j < cols_; ++j) {
        result(j, i) = (*this)(i, j);
      }
    }

    return result;
  }

  UltimateMatrix scalar_multiply(T scalar) const {
    UltimateMatrix result(rows_, cols_);
    const size_t n = rows_ * cols_;

#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) {
      result.data_.get()[i] = data_.get()[i] * scalar;
    }

    return result;
  }

  UltimateMatrix scalar_add(T scalar) const {
    UltimateMatrix result(rows_, cols_);
    const size_t n = rows_ * cols_;

#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) {
      result.data_.get()[i] = data_.get()[i] + scalar;
    }

    return result;
  }

  // ========== PROPERTIES ==========
  size_t rows() const noexcept { return rows_; }
  size_t cols() const noexcept { return cols_; }
  size_t size() const noexcept { return rows_ * cols_; }
  bool empty() const noexcept { return rows_ == 0 || cols_ == 0; }
  std::pair<size_t, size_t> shape() const noexcept { return {rows_, cols_}; }

  // ========== ACCESSORS ==========
  T &operator()(size_t i, size_t j) {
    if (i >= rows_ || j >= cols_) {
      throw std::out_of_range("Matrix index out of range");
    }
    return data_.get()[i * stride_ + j];
  }

  const T &operator()(size_t i, size_t j) const {
    if (i >= rows_ || j >= cols_) {
      throw std::out_of_range("Matrix index out of range");
    }
    return data_.get()[i * stride_ + j];
  }

  T *data() noexcept { return data_.get(); }
  const T *data() const noexcept { return data_.get(); }

  // ========== ADVANCED OPERATIONS ==========
  T frobenius_norm() const { return numerical::safe_norm(data_.get(), size()); }

  T sum() const { return numerical::kahan_sum(data_.get(), size()); }

  T trace() const {
    T sum = T{0};
    size_t n = std::min(rows_, cols_);
    for (size_t i = 0; i < n; ++i) {
      sum += (*this)(i, i);
    }
    return sum;
  }

  // ========== UTILITIES ==========
  void fill(T value) { std::fill(data_.get(), data_.get() + size(), value); }

  UltimateMatrix copy() const {
    UltimateMatrix result(rows_, cols_);
    std::copy(data_.get(), data_.get() + size(), result.data_.get());
    return result;
  }

  std::vector<T> to_vector() const {
    return std::vector<T>(data_.get(), data_.get() + size());
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

  // ========== NUMPY COMPATIBILITY ==========
  static UltimateMatrix from_numpy(const T *numpy_data, size_t rows,
                                   size_t cols) {
    UltimateMatrix mat(rows, cols);
    std::copy(numpy_data, numpy_data + rows * cols, mat.data_.get());
    return mat;
  }

  void to_numpy(T *numpy_data) const {
    std::copy(data_.get(), data_.get() + size(), numpy_data);
  }
};

} // namespace industrial_matrix
