#pragma once

#include "EntityManager.h"
#include <unordered_map>
#include <memory>
#include <typeindex>
#include <array>
#include <vector>

namespace pywrkgame {
namespace core {

class IComponentArray {
public:
    virtual ~IComponentArray() = default;
    virtual void EntityDestroyed(EntityID entity) = 0;
};

template<typename T>
class ComponentArray : public IComponentArray {
public:
    void InsertData(EntityID entity, T component) {
        if (entityToIndexMap.find(entity) != entityToIndexMap.end()) {
            // Component already exists, update it
            size_t index = entityToIndexMap[entity];
            componentArray[index] = component;
            return;
        }

        size_t newIndex = size;
        entityToIndexMap[entity] = newIndex;
        indexToEntityMap[newIndex] = entity;
        componentArray[newIndex] = component;
        ++size;
    }

    void RemoveData(EntityID entity) {
        if (entityToIndexMap.find(entity) == entityToIndexMap.end()) {
            return; // Component doesn't exist
        }

        size_t indexOfRemovedEntity = entityToIndexMap[entity];
        size_t indexOfLastElement = size - 1;
        componentArray[indexOfRemovedEntity] = componentArray[indexOfLastElement];

        EntityID entityOfLastElement = indexToEntityMap[indexOfLastElement];
        entityToIndexMap[entityOfLastElement] = indexOfRemovedEntity;
        indexToEntityMap[indexOfRemovedEntity] = entityOfLastElement;

        entityToIndexMap.erase(entity);
        indexToEntityMap.erase(indexOfLastElement);

        --size;
    }

    T& GetData(EntityID entity) {
        return componentArray[entityToIndexMap[entity]];
    }

    bool HasComponent(EntityID entity) const {
        return entityToIndexMap.find(entity) != entityToIndexMap.end();
    }

    void EntityDestroyed(EntityID entity) override {
        if (entityToIndexMap.find(entity) != entityToIndexMap.end()) {
            RemoveData(entity);
        }
    }

private:
    std::array<T, 1000> componentArray{};
    std::unordered_map<EntityID, size_t> entityToIndexMap{};
    std::unordered_map<size_t, EntityID> indexToEntityMap{};
    size_t size{};
};

class ComponentManager {
public:
    template<typename T>
    void RegisterComponent() {
        std::type_index typeIndex(typeid(T));
        componentTypes.insert({typeIndex, nextComponentType});
        componentArrays.insert({typeIndex, std::make_shared<ComponentArray<T>>()});
        ++nextComponentType;
    }

    template<typename T>
    void AddComponent(EntityID entity, T component) {
        GetComponentArray<T>()->InsertData(entity, component);
    }

    template<typename T>
    void RemoveComponent(EntityID entity) {
        GetComponentArray<T>()->RemoveData(entity);
    }

    template<typename T>
    T& GetComponent(EntityID entity) {
        return GetComponentArray<T>()->GetData(entity);
    }

    template<typename T>
    bool HasComponent(EntityID entity) {
        return GetComponentArray<T>()->HasComponent(entity);
    }

    void EntityDestroyed(EntityID entity) {
        for (auto const& pair : componentArrays) {
            auto const& component = pair.second;
            component->EntityDestroyed(entity);
        }
    }

private:
    std::unordered_map<std::type_index, uint8_t> componentTypes{};
    std::unordered_map<std::type_index, std::shared_ptr<IComponentArray>> componentArrays{};
    uint8_t nextComponentType{};

    template<typename T>
    std::shared_ptr<ComponentArray<T>> GetComponentArray() {
        std::type_index typeIndex(typeid(T));
        return std::static_pointer_cast<ComponentArray<T>>(componentArrays[typeIndex]);
    }
};

} // namespace core
} // namespace pywrkgame