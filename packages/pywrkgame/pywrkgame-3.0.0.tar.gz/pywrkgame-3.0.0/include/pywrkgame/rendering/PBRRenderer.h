#pragma once

#include "GraphicsTypes.h"
#include "GraphicsDevice.h"
#include "GlobalIllumination.h"
#include <memory>
#include <unordered_map>

namespace pywrkgame {
namespace rendering {

// Forward declarations
struct MeshData;
struct MeshHandle;

// PBR Rendering Pipeline
class PBRRenderer {
public:
    PBRRenderer();
    ~PBRRenderer();

    // Initialize PBR renderer with graphics device
    bool Initialize(GraphicsDevice* device);
    void Shutdown();

    // PBR Material Management
    uint32_t CreatePBRMaterial(const PBRMaterialProperties& properties);
    void DestroyPBRMaterial(uint32_t materialId);
    void UpdatePBRMaterial(uint32_t materialId, const PBRMaterialProperties& properties);
    const PBRMaterialProperties* GetPBRMaterial(uint32_t materialId) const;

    // Environment Lighting
    bool SetupEnvironmentLighting(const HDRIEnvironment& hdri);
    void EnableEnvironmentLighting(bool enable);
    bool IsEnvironmentLightingEnabled() const { return environmentLightingEnabled; }
    const HDRIEnvironment* GetEnvironment() const { return environment.get(); }

    // Global Illumination
    GlobalIllumination* GetGlobalIllumination() { return globalIllumination.get(); }
    const GlobalIllumination* GetGlobalIllumination() const { return globalIllumination.get(); }
    void EnableGlobalIllumination(GITechnique technique);
    void DisableGlobalIllumination();

    // Rendering
    void RenderPBRMesh(MeshHandle mesh, uint32_t materialId, const float* transform);
    void BeginPBRPass();
    void EndPBRPass();

    // Shader management
    bool CompilePBRShaders(GraphicsAPI api);
    ShaderHandle GetPBRVertexShader() const { return pbrVertexShader; }
    ShaderHandle GetPBRFragmentShader() const { return pbrFragmentShader; }

    bool IsInitialized() const { return initialized; }

private:
    bool initialized = false;
    GraphicsDevice* device = nullptr;

    // PBR Materials storage
    uint32_t nextMaterialId = 1;
    std::unordered_map<uint32_t, PBRMaterialProperties> pbrMaterials;

    // Environment lighting
    bool environmentLightingEnabled = false;
    std::unique_ptr<HDRIEnvironment> environment;

    // Global Illumination
    std::unique_ptr<GlobalIllumination> globalIllumination;

    // PBR Shaders
    ShaderHandle pbrVertexShader;
    ShaderHandle pbrFragmentShader;

    // Helper methods
    bool CreateDefaultPBRShaders(GraphicsAPI api);
    std::string GeneratePBRVertexShader(GraphicsAPI api);
    std::string GeneratePBRFragmentShader(GraphicsAPI api);
};

} // namespace rendering
} // namespace pywrkgame
