#pragma once

#include <memory>
#include <string>

namespace pywrkgame {
namespace core {

struct EngineConfig {
    std::string appName = "PyWRKGame Application";
    int windowWidth = 1280;
    int windowHeight = 720;
    bool fullscreen = false;
    bool vsync = true;
    int targetFPS = 60;
    bool enablePerformanceOptimization = true;
    bool is3DGame = true;
};

class EntityManager;
class SystemManager;
class ComponentManager;
class PerformanceOptimizer;

} // namespace core

// Forward declarations for subsystems
namespace rendering { class RenderingEngine; }
namespace physics { class PhysicsEngine; }
namespace audio { class AudioSystem; }
namespace network { class NetworkManager; }
namespace tools { class PerformanceProfiler; }

namespace core {

class EngineCore {
public:
    EngineCore();
    ~EngineCore();

    bool Initialize(const EngineConfig& config);
    void Update(float deltaTime);
    void Render();
    void Shutdown();

    // ECS Management
    EntityManager& GetEntityManager();
    SystemManager& GetSystemManager();
    ComponentManager& GetComponentManager();

    // Subsystem Access
    rendering::RenderingEngine& GetRenderer();
    physics::PhysicsEngine& GetPhysics();
    audio::AudioSystem& GetAudio();
    network::NetworkManager& GetNetwork();
    
    // Performance Management
    PerformanceOptimizer& GetPerformanceOptimizer();
    tools::PerformanceProfiler& GetProfiler();

    bool IsInitialized() const { return initialized; }

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
    bool initialized = false;
};

} // namespace core
} // namespace pywrkgame