#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "pywrkgame/core/EngineCore.h"

namespace py = pybind11;

// Forward declarations for binding functions
void bind_core(py::module& m);
void bind_rendering(py::module& m);
void bind_physics(py::module& m);
void bind_audio(py::module& m);
void bind_ui(py::module& m);

PYBIND11_MODULE(pywrkgame, m) {
    m.doc() = "PyWRKGame 3.0.0 - High-Performance Game Engine";
    
    // Bind all subsystems
    bind_core(m);
    bind_rendering(m);
    bind_physics(m);
    bind_audio(m);
    bind_ui(m);
}