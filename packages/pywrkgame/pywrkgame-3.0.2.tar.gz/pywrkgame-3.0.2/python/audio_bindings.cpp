#include <pybind11/pybind11.h>
#include "pywrkgame/audio/AudioSystem.h"

namespace py = pybind11;
using namespace pywrkgame::audio;

void bind_audio(py::module& m) {
    // AudioSystem
    py::class_<AudioSystem>(m, "AudioSystem");
}