#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "pywrkgame/core/EngineCore.h"
#include "pywrkgame/core/EntityManager.h"
#include "pywrkgame/core/ComponentManager.h"
#include "pywrkgame/core/SystemManager.h"

namespace py = pybind11;
using namespace pywrkgame::core;

// Custom Python exceptions
namespace pywrkgame {
namespace python {

class PyWRKGameError : public std::runtime_error {
public:
    explicit PyWRKGameError(const std::string& msg) : std::runtime_error(msg) {}
};

class InitializationError : public PyWRKGameError {
public:
    explicit InitializationError(const std::string& msg) : PyWRKGameError(msg) {}
};

class ResourceError : public PyWRKGameError {
public:
    explicit ResourceError(const std::string& msg) : PyWRKGameError(msg) {}
};

class RenderingError : public PyWRKGameError {
public:
    explicit RenderingError(const std::string& msg) : PyWRKGameError(msg) {}
};

class PhysicsError : public PyWRKGameError {
public:
    explicit PhysicsError(const std::string& msg) : PyWRKGameError(msg) {}
};

} // namespace python
} // namespace pywrkgame

// High-level GameObject wrapper class
class GameObject {
public:
    GameObject(EngineCore* engine, EntityID entity) 
        : engine_(engine), entity_(entity) {}

    EntityID GetEntityID() const { return entity_; }
    
    bool IsValid() const {
        return engine_ && engine_->GetEntityManager().IsEntityValid(entity_);
    }

    void Destroy() {
        if (IsValid()) {
            engine_->GetEntityManager().DestroyEntity(entity_);
        }
    }

    // Python-friendly component access
    py::object GetComponent(const std::string& componentType) {
        // This will be extended with actual component types
        throw pywrkgame::python::ResourceError("Component type not registered: " + componentType);
    }

    void AddComponent(const std::string& componentType, py::dict data) {
        // This will be extended with actual component types
        throw pywrkgame::python::ResourceError("Component type not registered: " + componentType);
    }

    void RemoveComponent(const std::string& componentType) {
        // This will be extended with actual component types
        throw pywrkgame::python::ResourceError("Component type not registered: " + componentType);
    }

    bool HasComponent(const std::string& componentType) const {
        // This will be extended with actual component types
        return false;
    }

private:
    EngineCore* engine_;
    EntityID entity_;
};

// Enhanced Engine wrapper with error handling
class EngineWrapper {
public:
    EngineWrapper() : core_(std::make_unique<EngineCore>()) {}

    bool Initialize(const EngineConfig& config) {
        try {
            bool result = core_->Initialize(config);
            if (!result) {
                throw pywrkgame::python::InitializationError("Failed to initialize engine");
            }
            return result;
        } catch (const std::exception& e) {
            throw pywrkgame::python::InitializationError(std::string("Engine initialization failed: ") + e.what());
        }
    }

    void Update(float deltaTime) {
        if (!core_->IsInitialized()) {
            throw pywrkgame::python::PyWRKGameError("Engine not initialized");
        }
        try {
            core_->Update(deltaTime);
        } catch (const std::exception& e) {
            throw pywrkgame::python::PyWRKGameError(std::string("Update failed: ") + e.what());
        }
    }

    void Render() {
        if (!core_->IsInitialized()) {
            throw pywrkgame::python::PyWRKGameError("Engine not initialized");
        }
        try {
            core_->Render();
        } catch (const std::exception& e) {
            throw pywrkgame::python::RenderingError(std::string("Render failed: ") + e.what());
        }
    }

    void Shutdown() {
        core_->Shutdown();
    }

    bool IsInitialized() const {
        return core_->IsInitialized();
    }

    // High-level GameObject creation
    GameObject CreateGameObject() {
        if (!core_->IsInitialized()) {
            throw pywrkgame::python::PyWRKGameError("Engine not initialized");
        }
        EntityID entity = core_->GetEntityManager().CreateEntity();
        return GameObject(core_.get(), entity);
    }

    // Direct access to subsystems
    EntityManager& GetEntityManager() { return core_->GetEntityManager(); }
    ComponentManager& GetComponentManager() { return core_->GetComponentManager(); }
    SystemManager& GetSystemManager() { return core_->GetSystemManager(); }

private:
    std::unique_ptr<EngineCore> core_;
};

void bind_core(py::module& m) {
    // Register custom exceptions
    py::register_exception<pywrkgame::python::PyWRKGameError>(m, "PyWRKGameError");
    py::register_exception<pywrkgame::python::InitializationError>(m, "InitializationError");
    py::register_exception<pywrkgame::python::ResourceError>(m, "ResourceError");
    py::register_exception<pywrkgame::python::RenderingError>(m, "RenderingError");
    py::register_exception<pywrkgame::python::PhysicsError>(m, "PhysicsError");

    // EngineConfig
    py::class_<EngineConfig>(m, "EngineConfig")
        .def(py::init<>())
        .def_readwrite("app_name", &EngineConfig::appName)
        .def_readwrite("window_width", &EngineConfig::windowWidth)
        .def_readwrite("window_height", &EngineConfig::windowHeight)
        .def_readwrite("fullscreen", &EngineConfig::fullscreen)
        .def_readwrite("vsync", &EngineConfig::vsync)
        .def_readwrite("target_fps", &EngineConfig::targetFPS);

    // EntityID type
    m.attr("INVALID_ENTITY") = INVALID_ENTITY;

    // GameObject wrapper
    py::class_<GameObject>(m, "GameObject")
        .def("get_entity_id", &GameObject::GetEntityID)
        .def("is_valid", &GameObject::IsValid)
        .def("destroy", &GameObject::Destroy)
        .def("get_component", &GameObject::GetComponent)
        .def("add_component", &GameObject::AddComponent)
        .def("remove_component", &GameObject::RemoveComponent)
        .def("has_component", &GameObject::HasComponent)
        .def("__repr__", [](const GameObject& obj) {
            return "<GameObject entity_id=" + std::to_string(obj.GetEntityID()) + 
                   " valid=" + (obj.IsValid() ? "True" : "False") + ">";
        });

    // Enhanced Engine wrapper
    py::class_<EngineWrapper>(m, "Engine")
        .def(py::init<>())
        .def("initialize", &EngineWrapper::Initialize,
             "Initialize the engine with configuration",
             py::arg("config"))
        .def("update", &EngineWrapper::Update,
             "Update the engine for one frame",
             py::arg("delta_time"))
        .def("render", &EngineWrapper::Render,
             "Render the current frame")
        .def("shutdown", &EngineWrapper::Shutdown,
             "Shutdown the engine and cleanup resources")
        .def("is_initialized", &EngineWrapper::IsInitialized,
             "Check if engine is initialized")
        .def("create_game_object", &EngineWrapper::CreateGameObject,
             "Create a new game object")
        .def("get_entity_manager", &EngineWrapper::GetEntityManager,
             py::return_value_policy::reference_internal)
        .def("get_component_manager", &EngineWrapper::GetComponentManager,
             py::return_value_policy::reference_internal)
        .def("get_system_manager", &EngineWrapper::GetSystemManager,
             py::return_value_policy::reference_internal)
        .def("__repr__", [](const EngineWrapper& engine) {
            return "<Engine initialized=" + std::string(engine.IsInitialized() ? "True" : "False") + ">";
        });

    // EntityManager
    py::class_<EntityManager>(m, "EntityManager")
        .def("create_entity", &EntityManager::CreateEntity,
             "Create a new entity and return its ID")
        .def("destroy_entity", &EntityManager::DestroyEntity,
             "Destroy an entity by ID",
             py::arg("entity"))
        .def("is_entity_valid", &EntityManager::IsEntityValid,
             "Check if an entity ID is valid",
             py::arg("entity"))
        .def("get_entity_count", &EntityManager::GetEntityCount,
             "Get the total number of active entities");

    // ComponentManager
    py::class_<ComponentManager>(m, "ComponentManager")
        .def("entity_destroyed", &ComponentManager::EntityDestroyed,
             "Notify that an entity was destroyed",
             py::arg("entity"));

    // System base class
    py::class_<System, std::shared_ptr<System>>(m, "System")
        .def("update", &System::Update, py::arg("delta_time"))
        .def("initialize", &System::Initialize)
        .def("shutdown", &System::Shutdown);

    // SystemManager
    py::class_<SystemManager>(m, "SystemManager")
        .def("update", &SystemManager::Update,
             "Update all registered systems",
             py::arg("delta_time"))
        .def("shutdown", &SystemManager::Shutdown,
             "Shutdown all registered systems");
}