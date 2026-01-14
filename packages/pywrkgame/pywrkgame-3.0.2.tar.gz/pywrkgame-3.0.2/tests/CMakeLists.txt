# Test configuration
include(FetchContent)

# Fetch GoogleTest
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.14.0
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# C++ unit tests (excluding property-based tests for now)
set(CPP_TEST_SOURCES
    cpp/test_engine_core.cpp
    cpp/test_ecs_framework.cpp
    cpp/test_rendering_engine.cpp
    cpp/test_physics_engine.cpp
    cpp/test_audio_system.cpp
    cpp/test_platform_manager.cpp
    cpp/test_touch_input_manager.cpp
    cpp/test_ui_system_properties.cpp
    cpp/test_network_properties.cpp
    cpp/test_advanced_network_properties.cpp
    cpp/test_ai_foundation_properties.cpp
    cpp/test_advanced_ai_properties.cpp
    cpp/test_profiler_properties.cpp
    cpp/test_debug_tools_properties.cpp
    cpp/test_mobile_features_properties.cpp
    cpp/test_performance_optimization_properties.cpp
)

add_executable(cpp_tests ${CPP_TEST_SOURCES})
target_link_libraries(cpp_tests 
    PRIVATE 
    pywrkgame_core
    gtest_main
    gmock_main
)

# Add test discovery
include(GoogleTest)
gtest_discover_tests(cpp_tests)

# Python property-based tests
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/python/conftest.py.in
    ${CMAKE_CURRENT_BINARY_DIR}/python/conftest.py
    @ONLY
)

# Copy Python test files
file(GLOB PYTHON_TESTS "python/test_*.py")
foreach(test_file ${PYTHON_TESTS})
    get_filename_component(test_name ${test_file} NAME)
    configure_file(${test_file} ${CMAKE_CURRENT_BINARY_DIR}/python/${test_name} COPYONLY)
endforeach()

# Add Python test target
add_test(
    NAME python_tests
    COMMAND ${Python3_EXECUTABLE} -m pytest ${CMAKE_CURRENT_BINARY_DIR}/python -v
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)