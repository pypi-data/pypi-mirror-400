#include "pywrkgame/core/SystemManager.h"

namespace pywrkgame {
namespace core {

SystemManager::SystemManager() = default;

SystemManager::~SystemManager() {
    Shutdown();
}

void SystemManager::Update(float deltaTime) {
    for (auto& system : systems) {
        system->Update(deltaTime);
    }
}

void SystemManager::Shutdown() {
    for (auto& system : systems) {
        system->Shutdown();
    }
    systems.clear();
}

} // namespace core
} // namespace pywrkgame