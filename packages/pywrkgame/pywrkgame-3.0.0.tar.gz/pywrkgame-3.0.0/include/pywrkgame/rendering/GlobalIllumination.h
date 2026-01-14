#pragma once

#include "GraphicsTypes.h"
#include "GraphicsDevice.h"
#include <memory>
#include <vector>

namespace pywrkgame {
namespace rendering {

// Global Illumination Techniques
enum class GITechnique {
    None,
    ScreenSpace,      // Screen-space global illumination (SSGI)
    LightProbes,      // Light probe-based indirect lighting
    VoxelBased        // Voxel cone tracing for high-end platforms
};

// Light Probe
struct LightProbe {
    float position[3];
    TextureHandle irradianceMap;  // Cubemap for diffuse lighting
    TextureHandle reflectionMap;  // Cubemap for specular reflections
    float radius = 10.0f;
    float intensity = 1.0f;
};

// Voxel Grid Configuration
struct VoxelGridConfig {
    uint32_t resolution = 128;  // Voxel grid resolution (128^3)
    float worldSize = 100.0f;   // World space size covered by voxel grid
    uint32_t mipLevels = 6;     // Number of mip levels for cone tracing
    bool enableAnisotropic = true;  // Use anisotropic voxels
};

// Screen-Space GI Configuration
struct SSGIConfig {
    uint32_t rayCount = 4;      // Number of rays per pixel
    float rayLength = 5.0f;     // Maximum ray length in world space
    float thickness = 0.5f;     // Surface thickness for ray hits
    float intensity = 1.0f;     // GI intensity multiplier
    bool enableTemporalFilter = true;  // Temporal accumulation
};

// Global Illumination System
class GlobalIllumination {
public:
    GlobalIllumination();
    ~GlobalIllumination();

    // Initialize GI system
    bool Initialize(GraphicsDevice* device);
    void Shutdown();

    // Technique selection
    void SetTechnique(GITechnique technique);
    GITechnique GetTechnique() const { return currentTechnique; }

    // Screen-Space GI
    bool SetupScreenSpaceGI(const SSGIConfig& config);
    void RenderScreenSpaceGI();
    const SSGIConfig& GetSSGIConfig() const { return ssgiConfig; }

    // Light Probes
    uint32_t CreateLightProbe(const LightProbe& probe);
    void DestroyLightProbe(uint32_t probeId);
    void UpdateLightProbe(uint32_t probeId, const LightProbe& probe);
    const LightProbe* GetLightProbe(uint32_t probeId) const;
    void RenderLightProbes();

    // Voxel-Based GI
    bool SetupVoxelGI(const VoxelGridConfig& config);
    void VoxelizeScene();
    void RenderVoxelGI();
    const VoxelGridConfig& GetVoxelConfig() const { return voxelConfig; }

    // Enable/Disable GI
    void Enable(bool enable);
    bool IsEnabled() const { return enabled; }

    bool IsInitialized() const { return initialized; }

private:
    bool initialized = false;
    bool enabled = false;
    GraphicsDevice* device = nullptr;

    GITechnique currentTechnique = GITechnique::None;

    // Screen-Space GI
    SSGIConfig ssgiConfig;
    TextureHandle ssgiTexture;
    ShaderHandle ssgiShader;

    // Light Probes
    uint32_t nextProbeId = 1;
    std::vector<LightProbe> lightProbes;
    std::vector<uint32_t> probeIds;

    // Voxel-Based GI
    VoxelGridConfig voxelConfig;
    TextureHandle voxelTexture;  // 3D texture for voxel grid
    ShaderHandle voxelizeShader;
    ShaderHandle voxelConeTracingShader;

    // Helper methods
    bool InitializeScreenSpaceGI();
    bool InitializeLightProbes();
    bool InitializeVoxelGI();
    void CleanupScreenSpaceGI();
    void CleanupLightProbes();
    void CleanupVoxelGI();
};

} // namespace rendering
} // namespace pywrkgame
