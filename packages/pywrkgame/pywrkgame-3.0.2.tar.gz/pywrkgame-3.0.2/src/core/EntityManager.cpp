#include "pywrkgame/core/EntityManager.h"

namespace pywrkgame {
namespace core {

EntityManager::EntityManager() {
    entityGenerations.reserve(1000); // Reserve space for initial entities
}

EntityManager::~EntityManager() = default;

EntityID EntityManager::CreateEntity() {
    uint32_t index;
    uint8_t generation;
    
    if (!availableIndices.empty()) {
        index = availableIndices.front();
        availableIndices.pop();
        generation = entityGenerations[index];
    } else {
        index = nextEntityIndex++;
        if (index >= entityGenerations.size()) {
            entityGenerations.resize(index + 1, 0);
        }
        generation = entityGenerations[index];
    }
    
    entityCount++;
    
    return CreateEntityID(index, generation);
}

void EntityManager::DestroyEntity(EntityID entity) {
    if (entity == INVALID_ENTITY) {
        return;
    }
    
    uint32_t index = GetEntityIndex(entity);
    uint8_t generation = GetEntityGeneration(entity);
    
    if (index >= entityGenerations.size() || entityGenerations[index] != generation) {
        return; // Entity doesn't exist or generation mismatch
    }
    
    // Increment generation to invalidate this entity ID
    entityGenerations[index]++;
    availableIndices.push(index);
    entityCount--;
}

bool EntityManager::IsEntityValid(EntityID entity) const {
    if (entity == INVALID_ENTITY) {
        return false;
    }
    
    uint32_t index = GetEntityIndex(entity);
    uint8_t generation = GetEntityGeneration(entity);
    
    return index < entityGenerations.size() && 
           entityGenerations[index] == generation;
}

size_t EntityManager::GetEntityCount() const {
    return entityCount;
}

} // namespace core
} // namespace pywrkgame