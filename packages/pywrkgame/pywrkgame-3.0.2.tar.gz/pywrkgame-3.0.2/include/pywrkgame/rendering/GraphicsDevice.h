#pragma once

#include "GraphicsTypes.h"
#include <memory>
#include <vector>

namespace pywrkgame {
namespace rendering {

// Abstract base class for graphics device
class GraphicsDevice {
public:
    virtual ~GraphicsDevice() = default;

    // Initialization and shutdown
    virtual bool Initialize() = 0;
    virtual void Shutdown() = 0;

    // Frame management
    virtual void BeginFrame() = 0;
    virtual void EndFrame() = 0;
    virtual void Present() = 0;

    // Resource creation
    virtual TextureHandle CreateTexture(const TextureDesc& desc) = 0;
    virtual BufferHandle CreateBuffer(const BufferDesc& desc) = 0;
    virtual ShaderHandle CreateShader(const ShaderDesc& desc) = 0;

    // Resource destruction
    virtual void DestroyTexture(TextureHandle handle) = 0;
    virtual void DestroyBuffer(BufferHandle handle) = 0;
    virtual void DestroyShader(ShaderHandle handle) = 0;

    // Resource updates
    virtual void UpdateBuffer(BufferHandle handle, const void* data, size_t size, size_t offset = 0) = 0;
    virtual void UpdateTexture(TextureHandle handle, const void* data, size_t size, uint32_t mipLevel = 0) = 0;

    // Render pass management
    virtual void BeginRenderPass() = 0;
    virtual void EndRenderPass() = 0;

    // Drawing commands
    virtual void Draw(uint32_t vertexCount, uint32_t instanceCount = 1, uint32_t firstVertex = 0, uint32_t firstInstance = 0) = 0;
    virtual void DrawIndexed(uint32_t indexCount, uint32_t instanceCount = 1, uint32_t firstIndex = 0, int32_t vertexOffset = 0, uint32_t firstInstance = 0) = 0;

    // State management
    virtual void SetViewport(float x, float y, float width, float height) = 0;
    virtual void SetScissor(int32_t x, int32_t y, uint32_t width, uint32_t height) = 0;

    // Query capabilities
    virtual GraphicsAPI GetAPI() const = 0;
    virtual bool IsInitialized() const = 0;

protected:
    bool initialized = false;
};

// Factory function to create appropriate graphics device based on platform
std::unique_ptr<GraphicsDevice> CreateGraphicsDevice(GraphicsAPI api = GraphicsAPI::Auto);

} // namespace rendering
} // namespace pywrkgame
