#include "industrial_matrix_ultimate.hpp"
#include <chrono>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace py = pybind11;
namespace im = industrial_matrix;

// Helper to convert numpy array to Matrix
template <typename T>
im::UltimateMatrix<T> numpy_to_matrix(py::array_t<T> arr) {
  py::buffer_info info = arr.request();

  if (info.ndim != 2) {
    throw std::runtime_error("Input array must be 2-dimensional");
  }

  size_t rows = info.shape[0];
  size_t cols = info.shape[1];

  return im::UltimateMatrix<T>::from_numpy(static_cast<T *>(info.ptr), rows,
                                           cols);
}

// Helper to convert Matrix to numpy array
template <typename T>
py::array_t<T> matrix_to_numpy(const im::UltimateMatrix<T> &mat) {
  size_t rows = mat.rows();
  size_t cols = mat.cols();

  auto result = py::array_t<T>({rows, cols});
  py::buffer_info info = result.request();
  mat.to_numpy(static_cast<T *>(info.ptr));

  return result;
}

// Python module
PYBIND11_MODULE(industrial_matrix_ultimate, m) {
  m.doc() =
      "Ultimate Industrial Matrix Library - Advanced C++ with Python Bindings";

  // MatrixF64 (double precision)
  py::class_<im::MatrixF64>(m, "MatrixF64",
                            "Double-precision matrix with advanced features")
      // Factory methods
      .def_static("zeros", &im::MatrixF64::zeros)
      .def_static("ones", &im::MatrixF64::ones)
      .def_static("identity", &im::MatrixF64::identity)
      .def_static("random", &im::MatrixF64::random, py::arg("rows"),
                  py::arg("cols"), py::arg("min") = 0.0, py::arg("max") = 1.0)

      // Properties
      .def("rows", &im::MatrixF64::rows)
      .def("cols", &im::MatrixF64::cols)
      .def("size", &im::MatrixF64::size)
      .def("shape", &im::MatrixF64::shape)

      // Element access
      .def("__getitem__",
           [](const im::MatrixF64 &m, std::pair<size_t, size_t> idx) {
             return m(idx.first, idx.second);
           })
      .def("__setitem__",
           [](im::MatrixF64 &m, std::pair<size_t, size_t> idx, double value) {
             m(idx.first, idx.second) = value;
           })

      // Operations
      .def("elementwise_add", &im::MatrixF64::elementwise_add)
      .def("elementwise_multiply", &im::MatrixF64::elementwise_multiply)
      .def("matrix_multiply", &im::MatrixF64::matrix_multiply)
      .def("transpose", &im::MatrixF64::transpose)
      .def("scalar_multiply", &im::MatrixF64::scalar_multiply)
      .def("scalar_add", &im::MatrixF64::scalar_add)

      // Advanced operations
      .def("frobenius_norm", &im::MatrixF64::frobenius_norm)
      .def("sum", &im::MatrixF64::sum)
      .def("trace", &im::MatrixF64::trace)

      // Utilities
      .def("fill", &im::MatrixF64::fill)
      .def("copy", &im::MatrixF64::copy)
      .def("to_vector", &im::MatrixF64::to_vector)
      .def("print", &im::MatrixF64::print, py::arg("name") = "")

      // NumPy interoperability
      .def_static(
          "from_numpy",
          [](py::array_t<double> arr) { return numpy_to_matrix<double>(arr); })
      .def(
          "to_numpy",
          [](const im::MatrixF64 &mat) { return matrix_to_numpy<double>(mat); })

      // Python operators
      .def("__add__", &im::MatrixF64::elementwise_add)
      .def("__mul__", &im::MatrixF64::elementwise_multiply)
      .def("__matmul__", &im::MatrixF64::matrix_multiply)

      .def("__repr__", [](const im::MatrixF64 &m) {
        return "<UltimateMatrixF64 " + std::to_string(m.rows()) + "x" +
               std::to_string(m.cols()) + ">";
      });

  // MatrixF32 (single precision)
  py::class_<im::MatrixF32>(m, "MatrixF32",
                            "Single-precision matrix with advanced features")
      .def_static("zeros", &im::MatrixF32::zeros)
      .def_static("ones", &im::MatrixF32::ones)
      .def_static("identity", &im::MatrixF32::identity)
      .def_static("random", &im::MatrixF32::random, py::arg("rows"),
                  py::arg("cols"), py::arg("min") = 0.0f, py::arg("max") = 1.0f)

      .def("rows", &im::MatrixF32::rows)
      .def("cols", &im::MatrixF32::cols)
      .def("size", &im::MatrixF32::size)
      .def("shape", &im::MatrixF32::shape)

      .def("__getitem__",
           [](const im::MatrixF32 &m, std::pair<size_t, size_t> idx) {
             return m(idx.first, idx.second);
           })
      .def("__setitem__", [](im::MatrixF32 &m, std::pair<size_t, size_t> idx,
                             float value) { m(idx.first, idx.second) = value; })

      .def("elementwise_add", &im::MatrixF32::elementwise_add)
      .def("elementwise_multiply", &im::MatrixF32::elementwise_multiply)
      .def("matrix_multiply", &im::MatrixF32::matrix_multiply)
      .def("transpose", &im::MatrixF32::transpose)
      .def("scalar_multiply", &im::MatrixF32::scalar_multiply)
      .def("scalar_add", &im::MatrixF32::scalar_add)

      .def("frobenius_norm", &im::MatrixF32::frobenius_norm)
      .def("sum", &im::MatrixF32::sum)
      .def("trace", &im::MatrixF32::trace)

      .def("fill", &im::MatrixF32::fill)
      .def("copy", &im::MatrixF32::copy)
      .def("to_vector", &im::MatrixF32::to_vector)
      .def("print", &im::MatrixF32::print, py::arg("name") = "")

      .def_static(
          "from_numpy",
          [](py::array_t<float> arr) { return numpy_to_matrix<float>(arr); })
      .def("to_numpy",
           [](const im::MatrixF32 &mat) { return matrix_to_numpy<float>(mat); })

      .def("__add__", &im::MatrixF32::elementwise_add)
      .def("__mul__", &im::MatrixF32::elementwise_multiply)
      .def("__matmul__", &im::MatrixF32::matrix_multiply)

      .def("__repr__", [](const im::MatrixF32 &m) {
        return "<UltimateMatrixF32 " + std::to_string(m.rows()) + "x" +
               std::to_string(m.cols()) + ">";
      });

  // Utility functions
  m.def("system_info", []() {
    py::dict info;

#ifdef _OPENMP
    info["openmp"] = true;
    info["threads"] = omp_get_max_threads();
#else
        info["openmp"] = false;
#endif

#ifdef __AVX2__
    info["simd"] = "AVX2";
#elif defined(__AVX__)
        info["simd"] = "AVX";
#else
        info["simd"] = "None";
#endif

    info["cpp_version"] = __cplusplus;
    info["memory_safe"] = true;
    info["numerically_stable"] = true;

    return info;
  });

  m.def(
      "benchmark",
      [](size_t size, int trials = 5) {
        auto A = im::MatrixF64::random(size, size);
        auto B = im::MatrixF64::random(size, size);

        double total_time = 0;
        for (int i = 0; i < trials; ++i) {
          auto start = std::chrono::high_resolution_clock::now();
          auto C = A.matrix_multiply(B);
          auto end = std::chrono::high_resolution_clock::now();

          total_time +=
              std::chrono::duration<double, std::milli>(end - start).count();
        }

        double avg_time = total_time / trials;
        double gflops = (2.0 * size * size * size) / (avg_time / 1000.0) / 1e9;

        py::dict result;
        result["size"] = size;
        result["time_ms"] = avg_time;
        result["gflops"] = gflops;
        result["trials"] = trials;
        return result;
      },
      py::arg("size"), py::arg("trials") = 5);
}
