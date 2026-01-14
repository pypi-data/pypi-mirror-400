#pragma once

#include <vector>
#include <memory>

namespace pywrkgame {
namespace core {

class System {
public:
    virtual ~System() = default;
    virtual void Update(float deltaTime) = 0;
    virtual void Initialize() = 0;
    virtual void Shutdown() = 0;
};

class SystemManager {
public:
    SystemManager();
    ~SystemManager();
    
    // Delete copy constructor and copy assignment
    SystemManager(const SystemManager&) = delete;
    SystemManager& operator=(const SystemManager&) = delete;
    
    // Allow move constructor and move assignment
    SystemManager(SystemManager&&) = default;
    SystemManager& operator=(SystemManager&&) = default;

    template<typename T>
    void RegisterSystem() {
        systems.push_back(std::make_unique<T>());
        systems.back()->Initialize();
    }

    void Update(float deltaTime);
    void Shutdown();

private:
    std::vector<std::unique_ptr<System>> systems;
};

} // namespace core
} // namespace pywrkgame