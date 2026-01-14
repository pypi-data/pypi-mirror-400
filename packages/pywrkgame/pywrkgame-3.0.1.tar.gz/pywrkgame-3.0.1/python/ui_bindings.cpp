#include <pybind11/pybind11.h>
#include "pywrkgame/ui/UISystem.h"

namespace py = pybind11;
using namespace pywrkgame::ui;

void bind_ui(py::module& m) {
    // UISystem
    py::class_<UISystem>(m, "UISystem");
}