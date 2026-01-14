#pragma once

#include "GraphicsDevice.h"
#include "GraphicsTypes.h"
#include "PBRRenderer.h"
#include "PostProcessing.h"
#include "ParticleSystem.h"
#include <memory>
#include <vector>
#include <unordered_map>

namespace pywrkgame {
namespace rendering {

// Forward declarations
class LODSystem;

// Mesh data structure
// Render object (combines mesh, material, and transform)
struct RenderObject {
    MeshHandle mesh;
    MaterialHandle material;
    float transform[16]; // 4x4 matrix
    bool visible = true;
};

class RenderingEngine {
public:
    RenderingEngine();
    ~RenderingEngine();

    bool Initialize(GraphicsAPI api = GraphicsAPI::Auto);
    void BeginFrame();
    void Render();
    void EndFrame();
    void Shutdown();

    // Resource management - Textures
    TextureHandle CreateTexture(const TextureDesc& desc);
    void DestroyTexture(TextureHandle handle);
    void UpdateTexture(TextureHandle handle, const void* data, size_t size, uint32_t mipLevel = 0);

    // Resource management - Buffers
    BufferHandle CreateBuffer(const BufferDesc& desc);
    void DestroyBuffer(BufferHandle handle);
    void UpdateBuffer(BufferHandle handle, const void* data, size_t size, size_t offset = 0);

    // Resource management - Shaders
    ShaderHandle CreateShader(const ShaderDesc& desc);
    void DestroyShader(ShaderHandle handle);
    ShaderHandle CompileShader(const std::string& source, ShaderStage stage);

    // Resource management - Meshes
    MeshHandle CreateMesh(const MeshData& data);
    void DestroyMesh(MeshHandle handle);
    void UpdateMesh(MeshHandle handle, const MeshData& data);

    // Resource management - Materials
    MaterialHandle CreateMaterial();
    void DestroyMaterial(MaterialHandle handle);
    void SetMaterialTexture(MaterialHandle material, TextureHandle texture, uint32_t slot = 0);
    void SetMaterialShader(MaterialHandle material, ShaderHandle shader);

    // Rendering
    void SubmitRenderObject(const RenderObject& object);
    void ClearRenderQueue();

    // Get graphics device
    GraphicsDevice* GetDevice() { return device.get(); }
    const GraphicsDevice* GetDevice() const { return device.get(); }

    // PBR Rendering System
    PBRRenderer* GetPBRRenderer() { return pbrRenderer.get(); }
    const PBRRenderer* GetPBRRenderer() const { return pbrRenderer.get(); }
    bool SetupPBRPipeline();
    void EnableGlobalIllumination(bool enable);

    // Post-Processing System
    PostProcessingPipeline* GetPostProcessing() { return postProcessing.get(); }
    const PostProcessingPipeline* GetPostProcessing() const { return postProcessing.get(); }
    bool SetupPostProcessing(const PostProcessConfig& config);
    void EnablePostProcessing(bool enable);

    // Particle System
    ParticleSystem* GetParticleSystem() { return particleSystem.get(); }
    const ParticleSystem* GetParticleSystem() const { return particleSystem.get(); }
    bool SetupParticleSystem();

    // LOD System
    LODSystem* GetLODSystem() { return lodSystem.get(); }
    const LODSystem* GetLODSystem() const { return lodSystem.get(); }
    bool SetupLODSystem();

    bool IsInitialized() const { return initialized; }

    // Frame statistics
    uint32_t GetFrameCount() const { return frameCount; }
    uint32_t GetDrawCallCount() const { return drawCallCount; }

private:
    bool initialized = false;
    std::unique_ptr<GraphicsDevice> device;
    std::unique_ptr<PBRRenderer> pbrRenderer;
    std::unique_ptr<PostProcessingPipeline> postProcessing;
    std::unique_ptr<ParticleSystem> particleSystem;
    std::unique_ptr<LODSystem> lodSystem;
    bool postProcessingEnabled = false;

    // Resource tracking
    struct MeshResource {
        BufferHandle vertexBuffer;
        BufferHandle indexBuffer;
        uint32_t vertexCount = 0;
        uint32_t indexCount = 0;
    };

    struct MaterialResource {
        ShaderHandle shader;
        std::unordered_map<uint32_t, TextureHandle> textures;
    };

    uint32_t nextMeshId = 1;
    uint32_t nextMaterialId = 1;
    std::unordered_map<uint32_t, MeshResource> meshes;
    std::unordered_map<uint32_t, MaterialResource> materials;

    // Render queue
    std::vector<RenderObject> renderQueue;

    // Frame statistics
    uint32_t frameCount = 0;
    uint32_t drawCallCount = 0;

    // Forward rendering pipeline
    void ExecuteForwardRenderingPipeline();
};

} // namespace rendering
} // namespace pywrkgame
