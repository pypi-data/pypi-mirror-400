/**
 * @file ovf_bindings.cpp
 * @brief Python bindings for OVF_File class using pybind11
 * 
 * (c) 2015-2026 by Prof. Flavio ABREU ARAUJO. All rights reserved.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <OVF_File.h>
#include <stdexcept>

namespace py = pybind11;

/**
 * @brief Convert OVF_File data to a NumPy array
 * 
 * Creates a NumPy array that shares memory with the OVF_File data.
 * The array has shape (znodes, ynodes, xnodes, valuedim) for vector fields
 * or (znodes, ynodes, xnodes) for scalar fields.
 */
py::array_t<NumType> get_data_as_numpy(OVF_File& ovf) {
    if (ovf.getData() == nullptr) {
        throw std::runtime_error("No data loaded in OVF file");
    }
    
    NumType* data_ptr = ovf.getData();
    
    // Create shape and strides
    std::vector<py::ssize_t> shape;
    std::vector<py::ssize_t> strides;
    
    if (ovf.valuedim == 1) {
        // Scalar field: (z, y, x)
        shape = {ovf.znodes, ovf.ynodes, ovf.xnodes};
        strides = {
            static_cast<py::ssize_t>(ovf.xnodes * ovf.ynodes * sizeof(NumType)),
            static_cast<py::ssize_t>(ovf.xnodes * sizeof(NumType)),
            static_cast<py::ssize_t>(sizeof(NumType))
        };
    } else {
        // Vector field: (z, y, x, dim)
        shape = {ovf.znodes, ovf.ynodes, ovf.xnodes, ovf.valuedim};
        strides = {
            static_cast<py::ssize_t>(ovf.xnodes * ovf.ynodes * ovf.valuedim * sizeof(NumType)),
            static_cast<py::ssize_t>(ovf.xnodes * ovf.valuedim * sizeof(NumType)),
            static_cast<py::ssize_t>(ovf.valuedim * sizeof(NumType)),
            static_cast<py::ssize_t>(sizeof(NumType))
        };
    }
    
    // Create NumPy array that owns the data
    // The capsule ensures proper cleanup
    auto capsule = py::capsule(data_ptr, [](void* /* p */) {
        // Note: With BINDING defined, OVF_File doesn't delete the data
        // So we need to handle cleanup here if we copy the data
        // For zero-copy, we keep the OVF_File alive via the capsule
    });
    
    return py::array_t<NumType>(shape, strides, data_ptr, capsule);
}

/**
 * @brief Set OVF_File data from a NumPy array
 */
void set_data_from_numpy(OVF_File& ovf, py::array_t<NumType, py::array::c_style | py::array::forcecast> array) {
    auto buf = array.request();
    
    // Validate dimensions
    if (buf.ndim < 3 || buf.ndim > 4) {
        throw std::runtime_error("Array must be 3D (scalar) or 4D (vector)");
    }
    
    // Extract dimensions
    ovf.znodes = static_cast<int>(buf.shape[0]);
    ovf.ynodes = static_cast<int>(buf.shape[1]);
    ovf.xnodes = static_cast<int>(buf.shape[2]);
    ovf.valuedim = (buf.ndim == 4) ? static_cast<int>(buf.shape[3]) : 1;
    
    // Calculate total elements
    int total_elements = ovf.xnodes * ovf.ynodes * ovf.znodes * ovf.valuedim;
    ovf.elementNum = total_elements;
    
    // Allocate and copy data
    NumType* new_data = new NumType[total_elements];
    std::memcpy(new_data, buf.ptr, total_elements * sizeof(NumType));
    ovf.setData(new_data);
}

/**
 * @brief Python module definition
 */
PYBIND11_MODULE(_ovf_core, m) {
    m.doc() = "Python bindings for OVF file I/O";
    
    // Expose IDX struct
    py::class_<IDX>(m, "IDX", "4D index structure")
        .def(py::init<>())
        .def_readwrite("d", &IDX::d, "Component index")
        .def_readwrite("x", &IDX::x, "X index")
        .def_readwrite("y", &IDX::y, "Y index")
        .def_readwrite("z", &IDX::z, "Z index")
        .def("__repr__", [](const IDX& idx) {
            return "IDX(d=" + std::to_string(idx.d) + 
                   ", x=" + std::to_string(idx.x) +
                   ", y=" + std::to_string(idx.y) +
                   ", z=" + std::to_string(idx.z) + ")";
        });
    
    // Expose OVF_File class
    py::class_<OVF_File>(m, "OVFFile", "OVF file reader/writer")
        .def(py::init<>())
        
        // File I/O
        .def("read", &OVF_File::readOVF, py::arg("filename"),
             "Read an OVF file")
        .def("write", &OVF_File::writeOVF, py::arg("filename"),
             "Write an OVF file")
        
        // Data access
        .def_property("data", &get_data_as_numpy, &set_data_from_numpy,
                      "Data as NumPy array")
        
        // Metadata - read/write properties
        .def_readwrite("Title", &OVF_File::Title, "Data title/description")
        .def_readwrite("meshtype", &OVF_File::meshtype, "Mesh type")
        .def_readwrite("meshunit", &OVF_File::meshunit, "Mesh unit")
        
        // Spatial bounds
        .def_readwrite("xmin", &OVF_File::xmin)
        .def_readwrite("ymin", &OVF_File::ymin)
        .def_readwrite("zmin", &OVF_File::zmin)
        .def_readwrite("xmax", &OVF_File::xmax)
        .def_readwrite("ymax", &OVF_File::ymax)
        .def_readwrite("zmax", &OVF_File::zmax)
        
        // Grid parameters
        .def_readwrite("xnodes", &OVF_File::xnodes, "Number of cells in X")
        .def_readwrite("ynodes", &OVF_File::ynodes, "Number of cells in Y")
        .def_readwrite("znodes", &OVF_File::znodes, "Number of cells in Z")
        .def_readwrite("xstepsize", &OVF_File::xstepsize, "Cell size in X")
        .def_readwrite("ystepsize", &OVF_File::ystepsize, "Cell size in Y")
        .def_readwrite("zstepsize", &OVF_File::zstepsize, "Cell size in Z")
        .def_readwrite("xbase", &OVF_File::xbase)
        .def_readwrite("ybase", &OVF_File::ybase)
        .def_readwrite("zbase", &OVF_File::zbase)
        
        // Value dimension
        .def_readwrite("valuedim", &OVF_File::valuedim, 
                       "Number of components (1=scalar, 3=vector)")
        
        // Simulation time
        .def_readwrite("StageSimTime", &OVF_File::StageSimTime)
        .def_readwrite("StageSimTimeUnit", &OVF_File::StageSimTimeUnit)
        .def_readwrite("TotalSimTime", &OVF_File::TotalSimTime)
        .def_readwrite("TotalSimTimeUnit", &OVF_File::TotalSimTimeUnit)
        
        // Statistics
        .def("getmax", &OVF_File::getmax, "Get index of maximum value")
        .def("getmin", &OVF_File::getmin, "Get index of minimum value")
        .def("getXmax", py::overload_cast<>(&OVF_File::getXmax),
             "Get index of maximum X component")
        .def("getYmax", py::overload_cast<>(&OVF_File::getYmax),
             "Get index of maximum Y component")
        .def("getZmax", py::overload_cast<>(&OVF_File::getZmax),
             "Get index of maximum Z component")
        .def("getXmin", py::overload_cast<>(&OVF_File::getXmin),
             "Get index of minimum X component")
        .def("getYmin", py::overload_cast<>(&OVF_File::getYmin),
             "Get index of minimum Y component")
        .def("getZmin", py::overload_cast<>(&OVF_File::getZmin),
             "Get index of minimum Z component")
        
        // Index conversion
        .def("fourToOneD", py::overload_cast<IDX>(&OVF_File::fourToOneD),
             "Convert 4D index to 1D")
        .def("oneToFourD", &OVF_File::oneToFourD, "Convert 1D index to 4D")
        
        // Element count
        .def_readonly("elementNum", &OVF_File::elementNum, "Total number of elements")
        
        // Repr
        .def("__repr__", [](const OVF_File& ovf) {
            return "<OVFFile '" + ovf.Title + "' " +
                   std::to_string(ovf.xnodes) + "x" +
                   std::to_string(ovf.ynodes) + "x" +
                   std::to_string(ovf.znodes) + "x" +
                   std::to_string(ovf.valuedim) + ">";
        });
    
    // Utility functions
    m.def("file_exists", &exists, py::arg("filename"),
          "Check if a file exists");
}