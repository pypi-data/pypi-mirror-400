#include "pywrkgame/core/EngineCore.h"
#include "pywrkgame/core/EntityManager.h"
#include "pywrkgame/core/SystemManager.h"
#include "pywrkgame/core/ComponentManager.h"
#include "pywrkgame/core/PerformanceOptimizer.h"
#include "pywrkgame/rendering/RenderingEngine.h"
#include "pywrkgame/physics/PhysicsEngine.h"
#include "pywrkgame/audio/AudioSystem.h"
#include "pywrkgame/network/NetworkManager.h"
#include "pywrkgame/platform/PlatformManager.h"
#include "pywrkgame/tools/PerformanceProfiler.h"

namespace pywrkgame {
namespace core {

class EngineCore::Impl {
public:
    std::unique_ptr<EntityManager> entityManager;
    std::unique_ptr<SystemManager> systemManager;
    std::unique_ptr<ComponentManager> componentManager;
    std::unique_ptr<rendering::RenderingEngine> renderer;
    std::unique_ptr<physics::PhysicsEngine> physics;
    std::unique_ptr<audio::AudioSystem> audio;
    std::unique_ptr<network::NetworkManager> network;
    std::unique_ptr<PerformanceOptimizer> performanceOptimizer;
    std::unique_ptr<tools::PerformanceProfiler> profiler;
    
    EngineConfig config;
};

EngineCore::EngineCore() : pImpl(std::make_unique<Impl>()) {}

EngineCore::~EngineCore() {
    if (initialized) {
        Shutdown();
    }
}

bool EngineCore::Initialize(const EngineConfig& config) {
    if (initialized) {
        return false;
    }

    pImpl->config = config;

    // Initialize platform manager first
    if (!platform::PlatformManager::Initialize()) {
        return false;
    }

    // Initialize performance profiler
    pImpl->profiler = std::make_unique<tools::PerformanceProfiler>();

    // Initialize ECS framework
    pImpl->entityManager = std::make_unique<EntityManager>();
    pImpl->componentManager = std::make_unique<ComponentManager>();
    pImpl->systemManager = std::make_unique<SystemManager>();

    // Initialize subsystems
    pImpl->renderer = std::make_unique<rendering::RenderingEngine>();
    pImpl->physics = std::make_unique<physics::PhysicsEngine>();
    pImpl->audio = std::make_unique<audio::AudioSystem>();
    pImpl->network = std::make_unique<network::NetworkManager>();

    // Initialize all subsystems
    if (!pImpl->renderer->Initialize()) return false;
    if (!pImpl->physics->Initialize()) return false;
    if (!pImpl->audio->Initialize()) return false;
    if (!pImpl->network->Initialize()) return false;

    // Initialize performance optimizer
    if (config.enablePerformanceOptimization) {
        pImpl->performanceOptimizer = std::make_unique<PerformanceOptimizer>();
        PerformanceConfig perfConfig;
        perfConfig.is3DGame = config.is3DGame;
        perfConfig.enableAutoScaling = true;
        perfConfig.enableMemoryManagement = true;
        perfConfig.enableFrameRateMaintenance = true;
        
        if (!pImpl->performanceOptimizer->Initialize(perfConfig)) {
            return false;
        }
        
        // Connect optimizer to subsystems
        pImpl->performanceOptimizer->SetProfiler(pImpl->profiler.get());
        pImpl->performanceOptimizer->SetRenderer(pImpl->renderer.get());
    }

    initialized = true;
    return true;
}

void EngineCore::Update(float deltaTime) {
    if (!initialized) return;

    // Begin performance tracking
    if (pImpl->profiler) {
        pImpl->profiler->BeginFrame();
    }
    if (pImpl->performanceOptimizer) {
        pImpl->performanceOptimizer->BeginFrame();
    }

    pImpl->systemManager->Update(deltaTime);
    pImpl->physics->Update(deltaTime);
    
    // Update performance optimizer
    if (pImpl->performanceOptimizer) {
        pImpl->performanceOptimizer->Update(deltaTime);
    }
}

void EngineCore::Render() {
    if (!initialized) return;

    pImpl->renderer->BeginFrame();
    pImpl->renderer->Render();
    pImpl->renderer->EndFrame();
    
    // End performance tracking
    if (pImpl->performanceOptimizer) {
        pImpl->performanceOptimizer->EndFrame();
    }
    if (pImpl->profiler) {
        pImpl->profiler->EndFrame();
    }
}

void EngineCore::Shutdown() {
    if (!initialized) return;

    if (pImpl->performanceOptimizer) {
        pImpl->performanceOptimizer->Shutdown();
    }

    pImpl->network->Shutdown();
    pImpl->audio->Shutdown();
    pImpl->physics->Shutdown();
    pImpl->renderer->Shutdown();

    pImpl->systemManager.reset();
    pImpl->componentManager.reset();
    pImpl->entityManager.reset();
    pImpl->profiler.reset();
    pImpl->performanceOptimizer.reset();

    platform::PlatformManager::Shutdown();
    
    initialized = false;
}

EntityManager& EngineCore::GetEntityManager() {
    return *pImpl->entityManager;
}

SystemManager& EngineCore::GetSystemManager() {
    return *pImpl->systemManager;
}

ComponentManager& EngineCore::GetComponentManager() {
    return *pImpl->componentManager;
}

rendering::RenderingEngine& EngineCore::GetRenderer() {
    return *pImpl->renderer;
}

physics::PhysicsEngine& EngineCore::GetPhysics() {
    return *pImpl->physics;
}

audio::AudioSystem& EngineCore::GetAudio() {
    return *pImpl->audio;
}

network::NetworkManager& EngineCore::GetNetwork() {
    return *pImpl->network;
}

PerformanceOptimizer& EngineCore::GetPerformanceOptimizer() {
    return *pImpl->performanceOptimizer;
}

tools::PerformanceProfiler& EngineCore::GetProfiler() {
    return *pImpl->profiler;
}

} // namespace core
} // namespace pywrkgame