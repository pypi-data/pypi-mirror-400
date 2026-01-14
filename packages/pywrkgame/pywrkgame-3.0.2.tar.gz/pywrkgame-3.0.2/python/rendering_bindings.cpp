#include <pybind11/pybind11.h>
#include "pywrkgame/rendering/RenderingEngine.h"

namespace py = pybind11;
using namespace pywrkgame::rendering;

void bind_rendering(py::module& m) {
    // RenderingEngine
    py::class_<RenderingEngine>(m, "RenderingEngine")
        .def("begin_frame", &RenderingEngine::BeginFrame)
        .def("render", &RenderingEngine::Render)
        .def("end_frame", &RenderingEngine::EndFrame);
}