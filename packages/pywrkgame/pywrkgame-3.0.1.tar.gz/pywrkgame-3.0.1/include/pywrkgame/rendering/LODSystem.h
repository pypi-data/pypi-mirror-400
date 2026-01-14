#pragma once

#include "GraphicsTypes.h"
#include <memory>
#include <vector>
#include <functional>

namespace pywrkgame {
namespace rendering {

// Forward declarations
class GraphicsDevice;
class RenderingEngine;

// LOD level definition
struct LODLevel {
    MeshHandle mesh;
    float distance = 0.0f;        // Distance threshold for this LOD
    float screenCoverage = 1.0f;  // Screen coverage percentage (0-1)
    uint32_t triangleCount = 0;
};

// LOD group - manages multiple LOD levels for a single object
class LODGroup {
public:
    LODGroup();
    ~LODGroup();
    
    // Add LOD level
    void AddLODLevel(const LODLevel& level);
    void RemoveLODLevel(size_t index);
    void ClearLODLevels();
    
    // Get appropriate LOD based on distance
    MeshHandle GetLODForDistance(float distance) const;
    MeshHandle GetLODForScreenCoverage(float coverage) const;
    
    // LOD level access
    size_t GetLODLevelCount() const { return lodLevels.size(); }
    const LODLevel* GetLODLevel(size_t index) const;
    
    // Configuration
    void SetFadeTransitionWidth(float width) { fadeTransitionWidth = width; }
    float GetFadeTransitionWidth() const { return fadeTransitionWidth; }
    
    void SetAnimateCrossFading(bool enable) { animateCrossFading = enable; }
    bool IsAnimateCrossFading() const { return animateCrossFading; }
    
    // Statistics
    uint32_t GetCurrentLODIndex(float distance) const;
    uint32_t GetTriangleCountForDistance(float distance) const;
    
private:
    std::vector<LODLevel> lodLevels;
    float fadeTransitionWidth = 0.1f;  // Percentage of distance for fade transition
    bool animateCrossFading = false;
    
    void SortLODLevels();
};

// LOD generation settings
struct LODGenerationSettings {
    uint32_t numLevels = 4;
    float reductionFactor = 0.5f;  // Triangle reduction per level
    bool preserveBoundaries = true;
    bool preserveUVs = true;
    bool preserveNormals = true;
    float qualityThreshold = 0.8f;
};

// LOD system manager
class LODSystem {
public:
    LODSystem();
    ~LODSystem();
    
    bool Initialize(RenderingEngine* renderer);
    void Shutdown();
    
    // Update LOD selections based on camera
    void Update(const float cameraPosition[3], const float cameraForward[3]);
    
    // LOD group management
    uint32_t CreateLODGroup();
    void DestroyLODGroup(uint32_t groupId);
    LODGroup* GetLODGroup(uint32_t groupId);
    
    // Automatic LOD generation
    bool GenerateLODLevels(MeshHandle sourceMesh, LODGroup* group, 
                          const LODGenerationSettings& settings);
    
    // Manual LOD setup
    bool SetupLODGroup(uint32_t groupId, const std::vector<LODLevel>& levels);
    
    // Camera settings
    void SetCameraPosition(float x, float y, float z);
    void GetCameraPosition(float& x, float& y, float& z) const;
    
    void SetCameraFOV(float fov) { cameraFOV = fov; }
    float GetCameraFOV() const { return cameraFOV; }
    
    void SetScreenHeight(uint32_t height) { screenHeight = height; }
    uint32_t GetScreenHeight() const { return screenHeight; }
    
    // LOD bias (global quality adjustment)
    void SetLODBias(float bias) { lodBias = bias; }
    float GetLODBias() const { return lodBias; }
    
    // Performance monitoring
    struct LODStatistics {
        uint32_t totalGroups = 0;
        uint32_t activeGroups = 0;
        uint32_t totalTriangles = 0;
        uint32_t renderedTriangles = 0;
        float averageLODLevel = 0.0f;
        float triangleReduction = 0.0f;  // Percentage
    };
    
    LODStatistics GetStatistics() const;
    void ResetStatistics();
    
    // Enable/disable LOD system
    void SetEnabled(bool enabled) { this->enabled = enabled; }
    bool IsEnabled() const { return enabled; }
    
    bool IsInitialized() const { return initialized; }
    
private:
    bool initialized = false;
    bool enabled = true;
    RenderingEngine* renderer = nullptr;
    
    // LOD groups
    uint32_t nextGroupId = 1;
    std::vector<std::unique_ptr<LODGroup>> lodGroups;
    std::vector<uint32_t> groupIds;
    
    // Camera state
    float cameraPosition[3] = {0.0f, 0.0f, 0.0f};
    float cameraForward[3] = {0.0f, 0.0f, -1.0f};
    float cameraFOV = 60.0f;
    uint32_t screenHeight = 1080;
    
    // LOD settings
    float lodBias = 1.0f;  // 1.0 = normal, >1.0 = higher quality, <1.0 = lower quality
    
    // Statistics
    mutable LODStatistics statistics;
    
    // Helper functions
    float CalculateScreenCoverage(const float objectPosition[3], float objectRadius) const;
    float CalculateDistance(const float objectPosition[3]) const;
    void UpdateStatistics();
};

// LOD mesh simplification utilities
class LODMeshSimplifier {
public:
    // Simplify mesh to target triangle count
    static bool SimplifyMesh(const MeshData& input, MeshData& output, 
                           uint32_t targetTriangleCount);
    
    // Simplify mesh to target quality (0-1)
    static bool SimplifyMeshByQuality(const MeshData& input, MeshData& output, 
                                     float quality);
    
    // Calculate mesh complexity metrics
    static uint32_t GetTriangleCount(const MeshData& mesh);
    static float CalculateMeshComplexity(const MeshData& mesh);
    
    // Preserve specific features during simplification
    struct SimplificationOptions {
        bool preserveBoundaries = true;
        bool preserveUVSeams = true;
        bool preserveNormals = true;
        bool preserveColors = false;
        float boundaryWeight = 2.0f;
        float uvSeamWeight = 2.0f;
    };
    
    static bool SimplifyMeshWithOptions(const MeshData& input, MeshData& output,
                                       uint32_t targetTriangleCount,
                                       const SimplificationOptions& options);
};

} // namespace rendering
} // namespace pywrkgame
