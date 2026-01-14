#pragma once

#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace industrial_matrix {

// Forward declarations
template<typename T> class Matrix;

// Matrix types
using MatrixF32 = Matrix<float>;
using MatrixF64 = Matrix<double>;
using MatrixI32 = Matrix<int32_t>;
using MatrixI64 = Matrix<int64_t>;

template<typename T>
class Matrix {
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
    
public:
    // Factory methods
    static Matrix zeros(size_t rows, size_t cols);
    static Matrix ones(size_t rows, size_t cols);
    static Matrix identity(size_t n);
    static Matrix random(size_t rows, size_t cols, 
                        T min = T(0), T max = T(1));
    
    // Constructors
    Matrix();
    Matrix(size_t rows, size_t cols);
    Matrix(size_t rows, size_t cols, T value);
    Matrix(const Matrix& other);
    Matrix(Matrix&& other) noexcept;
    ~Matrix();
    
    // Assignment
    Matrix& operator=(const Matrix& other);
    Matrix& operator=(Matrix&& other) noexcept;
    
    // Properties
    size_t rows() const;
    size_t cols() const;
    size_t size() const;
    bool empty() const;
    std::pair<size_t, size_t> shape() const;
    
    // Element access
    T& operator()(size_t i, size_t j);
    const T& operator()(size_t i, size_t j) const;
    
    // Operations
    Matrix elementwise_add(const Matrix& other) const;
    Matrix elementwise_subtract(const Matrix& other) const;
    Matrix elementwise_multiply(const Matrix& other) const;
    Matrix elementwise_divide(const Matrix& other) const;
    
    Matrix matrix_multiply(const Matrix& other) const;
    Matrix transpose() const;
    
    Matrix scalar_add(T scalar) const;
    Matrix scalar_multiply(T scalar) const;
    
    // Norms and metrics
    T frobenius_norm() const;
    T infinity_norm() const;
    T trace() const;
    T sum() const;
    
    // Utility
    void fill(T value);
    Matrix copy() const;
    std::vector<T> to_vector() const;
    
    // I/O
    void print(const std::string& name = "") const;
    bool save_to_file(const std::string& filename) const;
    static Matrix load_from_file(const std::string& filename);
    
    // NumPy compatibility
    static Matrix from_numpy(const T* data, size_t rows, size_t cols);
    void to_numpy(T* data) const;
};

// Utility functions
template<typename T>
bool matrices_equal(const Matrix<T>& a, const Matrix<T>& b, double epsilon = 1e-9);

} // namespace industrial_matrix
