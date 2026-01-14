#include "pywrkgame/rendering/LODSystem.h"
#include "pywrkgame/rendering/RenderingEngine.h"
#include <cmath>
#include <algorithm>

namespace pywrkgame {
namespace rendering {

// ============================================================================
// LOD Group
// ============================================================================

LODGroup::LODGroup() = default;

LODGroup::~LODGroup() = default;

void LODGroup::AddLODLevel(const LODLevel& level) {
    lodLevels.push_back(level);
    SortLODLevels();
}

void LODGroup::RemoveLODLevel(size_t index) {
    if (index < lodLevels.size()) {
        lodLevels.erase(lodLevels.begin() + index);
    }
}

void LODGroup::ClearLODLevels() {
    lodLevels.clear();
}

MeshHandle LODGroup::GetLODForDistance(float distance) const {
    if (lodLevels.empty()) {
        return MeshHandle{};
    }
    
    // Find appropriate LOD level based on distance
    for (size_t i = 0; i < lodLevels.size(); ++i) {
        if (distance <= lodLevels[i].distance) {
            return lodLevels[i].mesh;
        }
    }
    
    // Return lowest quality LOD if distance exceeds all thresholds
    return lodLevels.back().mesh;
}

MeshHandle LODGroup::GetLODForScreenCoverage(float coverage) const {
    if (lodLevels.empty()) {
        return MeshHandle{};
    }
    
    // Find appropriate LOD level based on screen coverage
    for (size_t i = 0; i < lodLevels.size(); ++i) {
        if (coverage >= lodLevels[i].screenCoverage) {
            return lodLevels[i].mesh;
        }
    }
    
    // Return lowest quality LOD if coverage is below all thresholds
    return lodLevels.back().mesh;
}

const LODLevel* LODGroup::GetLODLevel(size_t index) const {
    if (index < lodLevels.size()) {
        return &lodLevels[index];
    }
    return nullptr;
}

uint32_t LODGroup::GetCurrentLODIndex(float distance) const {
    if (lodLevels.empty()) {
        return 0;
    }
    
    for (size_t i = 0; i < lodLevels.size(); ++i) {
        if (distance <= lodLevels[i].distance) {
            return static_cast<uint32_t>(i);
        }
    }
    
    return static_cast<uint32_t>(lodLevels.size() - 1);
}

uint32_t LODGroup::GetTriangleCountForDistance(float distance) const {
    uint32_t index = GetCurrentLODIndex(distance);
    if (index < lodLevels.size()) {
        return lodLevels[index].triangleCount;
    }
    return 0;
}

void LODGroup::SortLODLevels() {
    // Sort LOD levels by distance (ascending)
    std::sort(lodLevels.begin(), lodLevels.end(),
        [](const LODLevel& a, const LODLevel& b) {
            return a.distance < b.distance;
        });
}

// ============================================================================
// LOD System
// ============================================================================

LODSystem::LODSystem() = default;

LODSystem::~LODSystem() {
    Shutdown();
}

bool LODSystem::Initialize(RenderingEngine* rend) {
    if (!rend) return false;
    if (initialized) return false;
    
    renderer = rend;
    initialized = true;
    
    return true;
}

void LODSystem::Shutdown() {
    if (!initialized) return;
    
    // Destroy all LOD groups
    lodGroups.clear();
    groupIds.clear();
    
    renderer = nullptr;
    initialized = false;
}

void LODSystem::Update(const float camPosition[3], const float camForward[3]) {
    if (!initialized || !enabled) return;
    
    // Update camera state
    cameraPosition[0] = camPosition[0];
    cameraPosition[1] = camPosition[1];
    cameraPosition[2] = camPosition[2];
    
    cameraForward[0] = camForward[0];
    cameraForward[1] = camForward[1];
    cameraForward[2] = camForward[2];
    
    // Update statistics
    UpdateStatistics();
}

uint32_t LODSystem::CreateLODGroup() {
    if (!initialized) return 0;
    
    auto group = std::make_unique<LODGroup>();
    
    uint32_t id = nextGroupId++;
    groupIds.push_back(id);
    lodGroups.push_back(std::move(group));
    
    return id;
}

void LODSystem::DestroyLODGroup(uint32_t groupId) {
    if (!initialized) return;
    
    for (size_t i = 0; i < groupIds.size(); ++i) {
        if (groupIds[i] == groupId) {
            lodGroups.erase(lodGroups.begin() + i);
            groupIds.erase(groupIds.begin() + i);
            break;
        }
    }
}

LODGroup* LODSystem::GetLODGroup(uint32_t groupId) {
    if (!initialized) return nullptr;
    
    for (size_t i = 0; i < groupIds.size(); ++i) {
        if (groupIds[i] == groupId) {
            return lodGroups[i].get();
        }
    }
    
    return nullptr;
}

bool LODSystem::GenerateLODLevels(MeshHandle sourceMesh, LODGroup* group,
                                 const LODGenerationSettings& settings) {
    if (!initialized || !renderer || !group) return false;
    if (!sourceMesh.IsValid()) return false;
    
    // This is a placeholder for actual LOD generation
    // In a real implementation, this would:
    // 1. Get the source mesh data
    // 2. Generate simplified versions using mesh simplification algorithms
    // 3. Create LOD levels with appropriate distance thresholds
    // 4. Add the LOD levels to the group
    
    // For now, just add the source mesh as LOD 0
    LODLevel level0;
    level0.mesh = sourceMesh;
    level0.distance = 50.0f;
    level0.screenCoverage = 0.5f;
    level0.triangleCount = 1000; // Placeholder
    
    group->AddLODLevel(level0);
    
    // Generate additional LOD levels
    for (uint32_t i = 1; i < settings.numLevels; ++i) {
        LODLevel level;
        level.mesh = sourceMesh; // Placeholder - should be simplified mesh
        level.distance = 50.0f * (i + 1);
        level.screenCoverage = 0.5f / (i + 1);
        level.triangleCount = static_cast<uint32_t>(1000 * std::pow(settings.reductionFactor, i));
        
        group->AddLODLevel(level);
    }
    
    return true;
}

bool LODSystem::SetupLODGroup(uint32_t groupId, const std::vector<LODLevel>& levels) {
    if (!initialized) return false;
    
    auto* group = GetLODGroup(groupId);
    if (!group) return false;
    
    group->ClearLODLevels();
    
    for (const auto& level : levels) {
        group->AddLODLevel(level);
    }
    
    return true;
}

void LODSystem::SetCameraPosition(float x, float y, float z) {
    cameraPosition[0] = x;
    cameraPosition[1] = y;
    cameraPosition[2] = z;
}

void LODSystem::GetCameraPosition(float& x, float& y, float& z) const {
    x = cameraPosition[0];
    y = cameraPosition[1];
    z = cameraPosition[2];
}

LODSystem::LODStatistics LODSystem::GetStatistics() const {
    return statistics;
}

void LODSystem::ResetStatistics() {
    statistics = LODStatistics{};
}

float LODSystem::CalculateScreenCoverage(const float objectPosition[3], float objectRadius) const {
    // Calculate distance from camera to object
    float distance = CalculateDistance(objectPosition);
    
    if (distance <= 0.0001f) {
        return 1.0f;
    }
    
    // Calculate screen coverage based on distance and object size
    // This is a simplified calculation
    float fovRadians = cameraFOV * 3.14159f / 180.0f;
    float tanHalfFOV = std::tan(fovRadians * 0.5f);
    
    float projectedSize = (objectRadius / distance) / tanHalfFOV;
    float screenCoverage = projectedSize * screenHeight;
    
    // Normalize to 0-1 range
    return std::min(1.0f, screenCoverage / screenHeight);
}

float LODSystem::CalculateDistance(const float objectPosition[3]) const {
    float dx = objectPosition[0] - cameraPosition[0];
    float dy = objectPosition[1] - cameraPosition[1];
    float dz = objectPosition[2] - cameraPosition[2];
    
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

void LODSystem::UpdateStatistics() {
    statistics.totalGroups = static_cast<uint32_t>(lodGroups.size());
    statistics.activeGroups = 0;
    statistics.totalTriangles = 0;
    statistics.renderedTriangles = 0;
    statistics.averageLODLevel = 0.0f;
    
    if (lodGroups.empty()) {
        statistics.triangleReduction = 0.0f;
        return;
    }
    
    uint32_t totalLODLevel = 0;
    
    for (const auto& group : lodGroups) {
        if (!group) continue;
        
        size_t levelCount = group->GetLODLevelCount();
        if (levelCount == 0) continue;
        
        statistics.activeGroups++;
        
        // Get highest quality LOD (LOD 0)
        const auto* level0 = group->GetLODLevel(0);
        if (level0) {
            statistics.totalTriangles += level0->triangleCount;
        }
        
        // Assume object is at origin for statistics (placeholder)
        float objectPos[3] = {0.0f, 0.0f, 0.0f};
        float distance = CalculateDistance(objectPos);
        
        uint32_t currentLOD = group->GetCurrentLODIndex(distance * lodBias);
        totalLODLevel += currentLOD;
        
        uint32_t triangles = group->GetTriangleCountForDistance(distance * lodBias);
        statistics.renderedTriangles += triangles;
    }
    
    if (statistics.activeGroups > 0) {
        statistics.averageLODLevel = static_cast<float>(totalLODLevel) / statistics.activeGroups;
    }
    
    if (statistics.totalTriangles > 0) {
        statistics.triangleReduction = 
            (1.0f - static_cast<float>(statistics.renderedTriangles) / statistics.totalTriangles) * 100.0f;
    }
}

// ============================================================================
// LOD Mesh Simplifier
// ============================================================================

bool LODMeshSimplifier::SimplifyMesh(const MeshData& input, MeshData& output,
                                    uint32_t targetTriangleCount) {
    // This is a placeholder for actual mesh simplification
    // In a real implementation, this would use algorithms like:
    // - Quadric Error Metrics (QEM)
    // - Edge collapse
    // - Vertex clustering
    
    // For now, just copy the input mesh
    output = input;
    
    return true;
}

bool LODMeshSimplifier::SimplifyMeshByQuality(const MeshData& input, MeshData& output,
                                             float quality) {
    if (quality < 0.0f || quality > 1.0f) {
        return false;
    }
    
    uint32_t inputTriangleCount = GetTriangleCount(input);
    uint32_t targetTriangleCount = static_cast<uint32_t>(inputTriangleCount * quality);
    
    return SimplifyMesh(input, output, targetTriangleCount);
}

uint32_t LODMeshSimplifier::GetTriangleCount(const MeshData& mesh) {
    return mesh.indexCount / 3;
}

float LODMeshSimplifier::CalculateMeshComplexity(const MeshData& mesh) {
    // Simple complexity metric based on triangle count
    // In a real implementation, this would consider:
    // - Triangle count
    // - Vertex count
    // - Texture coordinates
    // - Normal variations
    // - Material complexity
    
    return static_cast<float>(GetTriangleCount(mesh));
}

bool LODMeshSimplifier::SimplifyMeshWithOptions(const MeshData& input, MeshData& output,
                                               uint32_t targetTriangleCount,
                                               const SimplificationOptions& options) {
    // This is a placeholder for mesh simplification with options
    // In a real implementation, this would respect the preservation options
    
    return SimplifyMesh(input, output, targetTriangleCount);
}

} // namespace rendering
} // namespace pywrkgame
