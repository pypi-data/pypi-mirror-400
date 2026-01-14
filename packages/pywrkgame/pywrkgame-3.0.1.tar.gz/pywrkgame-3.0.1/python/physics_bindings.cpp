#include <pybind11/pybind11.h>
#include "pywrkgame/physics/PhysicsEngine.h"

namespace py = pybind11;
using namespace pywrkgame::physics;

void bind_physics(py::module& m) {
    // PhysicsEngine
    py::class_<PhysicsEngine>(m, "PhysicsEngine")
        .def("update", &PhysicsEngine::Update);
}