#include "pywrkgame/rendering/RenderingEngine.h"
#include "pywrkgame/rendering/PBRRenderer.h"
#include "pywrkgame/rendering/PostProcessing.h"
#include "pywrkgame/rendering/ParticleSystem.h"
#include "pywrkgame/rendering/LODSystem.h"
#include <cstring>

namespace pywrkgame {
namespace rendering {

RenderingEngine::RenderingEngine() = default;

RenderingEngine::~RenderingEngine() {
    if (initialized) {
        Shutdown();
    }
}

bool RenderingEngine::Initialize(GraphicsAPI api) {
    if (initialized) {
        return false;
    }
    
    // Create graphics device
    device = CreateGraphicsDevice(api);
    if (!device) {
        return false;
    }

    // Initialize graphics device
    if (!device->Initialize()) {
        device.reset();
        return false;
    }

    // Initialize PBR renderer
    pbrRenderer = std::make_unique<PBRRenderer>();
    if (!pbrRenderer->Initialize(device.get())) {
        pbrRenderer.reset();
        device->Shutdown();
        device.reset();
        return false;
    }
    
    initialized = true;
    frameCount = 0;
    drawCallCount = 0;
    return true;
}

void RenderingEngine::BeginFrame() {
    if (!initialized || !device) return;
    
    device->BeginFrame();
    drawCallCount = 0;
}

void RenderingEngine::Render() {
    if (!initialized || !device) return;
    
    // Execute forward rendering pipeline
    ExecuteForwardRenderingPipeline();
}

void RenderingEngine::EndFrame() {
    if (!initialized || !device) return;
    
    device->EndFrame();
    device->Present();
    
    frameCount++;
    ClearRenderQueue();
}

void RenderingEngine::Shutdown() {
    if (!initialized) return;
    
    // Clean up all resources
    for (auto& [id, mesh] : meshes) {
        if (mesh.vertexBuffer.IsValid()) {
            device->DestroyBuffer(mesh.vertexBuffer);
        }
        if (mesh.indexBuffer.IsValid()) {
            device->DestroyBuffer(mesh.indexBuffer);
        }
    }
    meshes.clear();

    for (auto& [id, material] : materials) {
        if (material.shader.IsValid()) {
            device->DestroyShader(material.shader);
        }
        for (auto& [slot, texture] : material.textures) {
            if (texture.IsValid()) {
                device->DestroyTexture(texture);
            }
        }
    }
    materials.clear();

    renderQueue.clear();

    // Shutdown PBR renderer
    if (pbrRenderer) {
        pbrRenderer->Shutdown();
        pbrRenderer.reset();
    }
    
    if (device) {
        device->Shutdown();
        device.reset();
    }
    
    initialized = false;
}

// Texture management
TextureHandle RenderingEngine::CreateTexture(const TextureDesc& desc) {
    if (!initialized || !device) {
        return TextureHandle{};
    }
    return device->CreateTexture(desc);
}

void RenderingEngine::DestroyTexture(TextureHandle handle) {
    if (!initialized || !device) return;
    device->DestroyTexture(handle);
}

void RenderingEngine::UpdateTexture(TextureHandle handle, const void* data, size_t size, uint32_t mipLevel) {
    if (!initialized || !device) return;
    device->UpdateTexture(handle, data, size, mipLevel);
}

// Buffer management
BufferHandle RenderingEngine::CreateBuffer(const BufferDesc& desc) {
    if (!initialized || !device) {
        return BufferHandle{};
    }
    return device->CreateBuffer(desc);
}

void RenderingEngine::DestroyBuffer(BufferHandle handle) {
    if (!initialized || !device) return;
    device->DestroyBuffer(handle);
}

void RenderingEngine::UpdateBuffer(BufferHandle handle, const void* data, size_t size, size_t offset) {
    if (!initialized || !device) return;
    device->UpdateBuffer(handle, data, size, offset);
}

// Shader management
ShaderHandle RenderingEngine::CreateShader(const ShaderDesc& desc) {
    if (!initialized || !device) {
        return ShaderHandle{};
    }
    return device->CreateShader(desc);
}

void RenderingEngine::DestroyShader(ShaderHandle handle) {
    if (!initialized || !device) return;
    device->DestroyShader(handle);
}

ShaderHandle RenderingEngine::CompileShader(const std::string& source, ShaderStage stage) {
    if (!initialized || !device) {
        return ShaderHandle{};
    }

    ShaderDesc desc{};
    desc.stage = stage;
    desc.source = source;
    desc.isSpirV = false;

    return device->CreateShader(desc);
}

// Mesh management
MeshHandle RenderingEngine::CreateMesh(const MeshData& data) {
    if (!initialized || !device) {
        return MeshHandle{};
    }

    MeshResource resource{};

    // Create vertex buffer
    if (!data.vertices.empty()) {
        BufferDesc vbDesc{};
        vbDesc.size = data.vertices.size() * sizeof(float);
        vbDesc.type = BufferType::Vertex;
        vbDesc.initialData = data.vertices.data();
        vbDesc.dynamic = false;

        resource.vertexBuffer = device->CreateBuffer(vbDesc);
        if (!resource.vertexBuffer.IsValid()) {
            return MeshHandle{};
        }
        resource.vertexCount = data.vertexCount;
    }

    // Create index buffer
    if (!data.indices.empty()) {
        BufferDesc ibDesc{};
        ibDesc.size = data.indices.size() * sizeof(uint32_t);
        ibDesc.type = BufferType::Index;
        ibDesc.initialData = data.indices.data();
        ibDesc.dynamic = false;

        resource.indexBuffer = device->CreateBuffer(ibDesc);
        if (!resource.indexBuffer.IsValid()) {
            if (resource.vertexBuffer.IsValid()) {
                device->DestroyBuffer(resource.vertexBuffer);
            }
            return MeshHandle{};
        }
        resource.indexCount = data.indexCount;
    }

    // Store mesh resource
    MeshHandle handle;
    handle.id = nextMeshId++;
    handle.generation = 1;

    meshes[handle.id] = resource;

    return handle;
}

void RenderingEngine::DestroyMesh(MeshHandle handle) {
    if (!initialized || !device || !handle.IsValid()) return;

    auto it = meshes.find(handle.id);
    if (it != meshes.end()) {
        if (it->second.vertexBuffer.IsValid()) {
            device->DestroyBuffer(it->second.vertexBuffer);
        }
        if (it->second.indexBuffer.IsValid()) {
            device->DestroyBuffer(it->second.indexBuffer);
        }
        meshes.erase(it);
    }
}

void RenderingEngine::UpdateMesh(MeshHandle handle, const MeshData& data) {
    if (!initialized || !device || !handle.IsValid()) return;

    auto it = meshes.find(handle.id);
    if (it == meshes.end()) return;

    // Update vertex buffer
    if (!data.vertices.empty() && it->second.vertexBuffer.IsValid()) {
        device->UpdateBuffer(it->second.vertexBuffer, data.vertices.data(), 
                           data.vertices.size() * sizeof(float));
        it->second.vertexCount = data.vertexCount;
    }

    // Update index buffer
    if (!data.indices.empty() && it->second.indexBuffer.IsValid()) {
        device->UpdateBuffer(it->second.indexBuffer, data.indices.data(), 
                           data.indices.size() * sizeof(uint32_t));
        it->second.indexCount = data.indexCount;
    }
}

// Material management
MaterialHandle RenderingEngine::CreateMaterial() {
    if (!initialized) {
        return MaterialHandle{};
    }

    MaterialHandle handle;
    handle.id = nextMaterialId++;
    handle.generation = 1;

    materials[handle.id] = MaterialResource{};

    return handle;
}

void RenderingEngine::DestroyMaterial(MaterialHandle handle) {
    if (!initialized || !handle.IsValid()) return;

    auto it = materials.find(handle.id);
    if (it != materials.end()) {
        // Note: We don't destroy shader and textures here as they might be shared
        // The user is responsible for managing shader and texture lifetimes
        materials.erase(it);
    }
}

void RenderingEngine::SetMaterialTexture(MaterialHandle material, TextureHandle texture, uint32_t slot) {
    if (!initialized || !material.IsValid()) return;

    auto it = materials.find(material.id);
    if (it != materials.end()) {
        it->second.textures[slot] = texture;
    }
}

void RenderingEngine::SetMaterialShader(MaterialHandle material, ShaderHandle shader) {
    if (!initialized || !material.IsValid()) return;

    auto it = materials.find(material.id);
    if (it != materials.end()) {
        it->second.shader = shader;
    }
}

// Rendering
void RenderingEngine::SubmitRenderObject(const RenderObject& object) {
    if (!initialized) return;
    renderQueue.push_back(object);
}

void RenderingEngine::ClearRenderQueue() {
    renderQueue.clear();
}

void RenderingEngine::ExecuteForwardRenderingPipeline() {
    if (!device || renderQueue.empty()) return;

    device->BeginRenderPass();

    // Set default viewport (will be configurable later)
    device->SetViewport(0.0f, 0.0f, 1920.0f, 1080.0f);
    device->SetScissor(0, 0, 1920, 1080);

    // Render all objects in the queue
    for (const auto& object : renderQueue) {
        if (!object.visible) continue;
        if (!object.mesh.IsValid()) continue;

        // Get mesh resource
        auto meshIt = meshes.find(object.mesh.id);
        if (meshIt == meshes.end()) continue;

        const auto& meshResource = meshIt->second;

        // Draw the mesh
        if (meshResource.indexCount > 0) {
            device->DrawIndexed(meshResource.indexCount, 1, 0, 0, 0);
            drawCallCount++;
        } else if (meshResource.vertexCount > 0) {
            device->Draw(meshResource.vertexCount, 1, 0, 0);
            drawCallCount++;
        }
    }

    device->EndRenderPass();
}

// PBR Pipeline Setup
bool RenderingEngine::SetupPBRPipeline() {
    if (!initialized || !pbrRenderer) {
        return false;
    }

    // PBR renderer is already initialized during engine initialization
    // This method can be used to reconfigure or reset the PBR pipeline
    return pbrRenderer->IsInitialized();
}

void RenderingEngine::EnableGlobalIllumination(bool enable) {
    if (!initialized || !pbrRenderer) {
        return;
    }

    pbrRenderer->EnableEnvironmentLighting(enable);
}

// Post-Processing Setup
bool RenderingEngine::SetupPostProcessing(const PostProcessConfig& config) {
    if (!initialized || !device) {
        return false;
    }

    // Create post-processing pipeline if it doesn't exist
    if (!postProcessing) {
        postProcessing = std::make_unique<PostProcessingPipeline>();
        if (!postProcessing->Initialize(device.get(), config)) {
            postProcessing.reset();
            return false;
        }
    } else {
        // Update configuration
        postProcessing->SetConfig(config);
    }

    postProcessingEnabled = true;
    return true;
}

void RenderingEngine::EnablePostProcessing(bool enable) {
    postProcessingEnabled = enable && postProcessing && postProcessing->IsInitialized();
}

// Particle System Setup
bool RenderingEngine::SetupParticleSystem() {
    if (!initialized || !device) {
        return false;
    }

    // Create particle system if it doesn't exist
    if (!particleSystem) {
        particleSystem = std::make_unique<ParticleSystem>();
        if (!particleSystem->Initialize(device.get())) {
            particleSystem.reset();
            return false;
        }
    }

    return true;
}

// LOD System Setup
bool RenderingEngine::SetupLODSystem() {
    if (!initialized) {
        return false;
    }

    // Create LOD system if it doesn't exist
    if (!lodSystem) {
        lodSystem = std::make_unique<LODSystem>();
        if (!lodSystem->Initialize(this)) {
            lodSystem.reset();
            return false;
        }
    }

    return true;
}

} // namespace rendering
} // namespace pywrkgame
