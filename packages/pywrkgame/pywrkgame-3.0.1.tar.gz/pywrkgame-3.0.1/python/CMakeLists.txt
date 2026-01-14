# Python bindings using pybind11
pybind11_add_module(pywrkgame 
    bindings.cpp
    core_bindings.cpp
    rendering_bindings.cpp
    physics_bindings.cpp
    audio_bindings.cpp
    ui_bindings.cpp
)

# Link with core library
target_link_libraries(pywrkgame PRIVATE pywrkgame_core)

# Compiler-specific options
target_compile_definitions(pywrkgame PRIVATE VERSION_INFO=${PROJECT_VERSION})

# Install Python module
install(TARGETS pywrkgame DESTINATION .)