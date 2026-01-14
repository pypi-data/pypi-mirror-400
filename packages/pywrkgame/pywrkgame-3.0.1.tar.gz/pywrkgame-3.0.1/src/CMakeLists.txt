# Core Engine Library
set(CORE_SOURCES
    core/EngineCore.cpp
    core/EntityManager.cpp
    core/ComponentManager.cpp
    core/SystemManager.cpp
    core/PerformanceOptimizer.cpp
    platform/PlatformManager.cpp
    platform/TouchInputManager.cpp
    rendering/RenderingEngine.cpp
    rendering/GraphicsDevice.cpp
    rendering/VulkanDevice.cpp
    rendering/MetalDevice.cpp
    rendering/D3D12Device.cpp
    rendering/PBRRenderer.cpp
    rendering/GlobalIllumination.cpp
    rendering/PostProcessing.cpp
    rendering/ParticleSystem.cpp
    rendering/LODSystem.cpp
    physics/PhysicsEngine.cpp
    physics/Bullet3Backend.cpp
    physics/Box2DBackend.cpp
    audio/AudioSystem.cpp
    network/NetworkManager.cpp
    ai/AIFramework.cpp
    assets/AssetManager.cpp
    ui/UISystem.cpp
    memory/MemoryManager.cpp
    animation/AnimationSystem.cpp
    animation/IKSolver.cpp
    animation/ProceduralAnimation.cpp
    tools/PerformanceProfiler.cpp
    tools/DebugTools.cpp
)

set(CORE_HEADERS
    ../include/pywrkgame/core/EngineCore.h
    ../include/pywrkgame/core/EntityManager.h
    ../include/pywrkgame/core/ComponentManager.h
    ../include/pywrkgame/core/SystemManager.h
    ../include/pywrkgame/core/PerformanceOptimizer.h
    ../include/pywrkgame/platform/PlatformManager.h
    ../include/pywrkgame/platform/TouchInputManager.h
    ../include/pywrkgame/rendering/RenderingEngine.h
    ../include/pywrkgame/rendering/GraphicsDevice.h
    ../include/pywrkgame/rendering/GraphicsTypes.h
    ../include/pywrkgame/rendering/VulkanDevice.h
    ../include/pywrkgame/rendering/MetalDevice.h
    ../include/pywrkgame/rendering/D3D12Device.h
    ../include/pywrkgame/rendering/PBRRenderer.h
    ../include/pywrkgame/rendering/GlobalIllumination.h
    ../include/pywrkgame/rendering/PostProcessing.h
    ../include/pywrkgame/rendering/ParticleSystem.h
    ../include/pywrkgame/rendering/LODSystem.h
    ../include/pywrkgame/physics/PhysicsEngine.h
    ../include/pywrkgame/physics/Bullet3Backend.h
    ../include/pywrkgame/physics/Box2DBackend.h
    ../include/pywrkgame/audio/AudioSystem.h
    ../include/pywrkgame/network/NetworkManager.h
    ../include/pywrkgame/ai/AIFramework.h
    ../include/pywrkgame/assets/AssetManager.h
    ../include/pywrkgame/ui/UISystem.h
    ../include/pywrkgame/memory/MemoryManager.h
    ../include/pywrkgame/animation/AnimationSystem.h
    ../include/pywrkgame/animation/IKSolver.h
    ../include/pywrkgame/animation/ProceduralAnimation.h
    ../include/pywrkgame/tools/PerformanceProfiler.h
    ../include/pywrkgame/tools/DebugTools.h
)

# Create core library
add_library(pywrkgame_core ${CORE_SOURCES} ${CORE_HEADERS})

# Link libraries
target_link_libraries(pywrkgame_core 
    PUBLIC
    glm::glm
    PRIVATE 
    Threads::Threads
)

# Platform-specific configurations
if(PLATFORM_WINDOWS)
    target_compile_definitions(pywrkgame_core PRIVATE PLATFORM_WINDOWS)
    target_link_libraries(pywrkgame_core PRIVATE d3d12 dxgi dbghelp psapi)
elseif(PLATFORM_MACOS)
    target_compile_definitions(pywrkgame_core PRIVATE PLATFORM_MACOS)
    find_library(METAL_FRAMEWORK Metal)
    find_library(METALKIT_FRAMEWORK MetalKit)
    target_link_libraries(pywrkgame_core PRIVATE ${METAL_FRAMEWORK} ${METALKIT_FRAMEWORK})
elseif(PLATFORM_LINUX)
    target_compile_definitions(pywrkgame_core PRIVATE PLATFORM_LINUX)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(VULKAN REQUIRED vulkan)
    target_link_libraries(pywrkgame_core PRIVATE ${VULKAN_LIBRARIES})
    target_include_directories(pywrkgame_core PRIVATE ${VULKAN_INCLUDE_DIRS})
endif()

# Set target properties
set_target_properties(pywrkgame_core PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
)

# Install targets
install(TARGETS pywrkgame_core
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)