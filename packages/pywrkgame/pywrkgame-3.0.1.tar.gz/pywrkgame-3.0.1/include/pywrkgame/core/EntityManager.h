#pragma once

#include <cstdint>
#include <vector>
#include <queue>

namespace pywrkgame {
namespace core {

// EntityID encodes both index (lower 24 bits) and generation (upper 8 bits)
using EntityID = uint32_t;
constexpr EntityID INVALID_ENTITY = 0;

// Helper functions to encode/decode entity ID
inline uint32_t GetEntityIndex(EntityID entity) {
    return entity & 0x00FFFFFF;
}

inline uint8_t GetEntityGeneration(EntityID entity) {
    return (entity >> 24) & 0xFF;
}

inline EntityID CreateEntityID(uint32_t index, uint8_t generation) {
    return (static_cast<uint32_t>(generation) << 24) | (index & 0x00FFFFFF);
}

class EntityManager {
public:
    EntityManager();
    ~EntityManager();

    EntityID CreateEntity();
    void DestroyEntity(EntityID entity);
    bool IsEntityValid(EntityID entity) const;
    
    size_t GetEntityCount() const;

private:
    std::vector<uint8_t> entityGenerations;  // Generation counter for each index
    std::queue<uint32_t> availableIndices;   // Available entity indices
    uint32_t nextEntityIndex = 1;
    size_t entityCount = 0;
};

} // namespace core
} // namespace pywrkgame