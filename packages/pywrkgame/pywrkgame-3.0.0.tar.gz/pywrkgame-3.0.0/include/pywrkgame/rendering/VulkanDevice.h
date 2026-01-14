#pragma once

#include "GraphicsDevice.h"
#include <unordered_map>

namespace pywrkgame {
namespace rendering {

class VulkanDevice : public GraphicsDevice {
public:
    VulkanDevice();
    ~VulkanDevice() override;

    bool Initialize() override;
    void Shutdown() override;

    void BeginFrame() override;
    void EndFrame() override;
    void Present() override;

    TextureHandle CreateTexture(const TextureDesc& desc) override;
    BufferHandle CreateBuffer(const BufferDesc& desc) override;
    ShaderHandle CreateShader(const ShaderDesc& desc) override;

    void DestroyTexture(TextureHandle handle) override;
    void DestroyBuffer(BufferHandle handle) override;
    void DestroyShader(ShaderHandle handle) override;

    void UpdateBuffer(BufferHandle handle, const void* data, size_t size, size_t offset = 0) override;
    void UpdateTexture(TextureHandle handle, const void* data, size_t size, uint32_t mipLevel = 0) override;

    void BeginRenderPass() override;
    void EndRenderPass() override;

    void Draw(uint32_t vertexCount, uint32_t instanceCount = 1, uint32_t firstVertex = 0, uint32_t firstInstance = 0) override;
    void DrawIndexed(uint32_t indexCount, uint32_t instanceCount = 1, uint32_t firstIndex = 0, int32_t vertexOffset = 0, uint32_t firstInstance = 0) override;

    void SetViewport(float x, float y, float width, float height) override;
    void SetScissor(int32_t x, int32_t y, uint32_t width, uint32_t height) override;

    GraphicsAPI GetAPI() const override { return GraphicsAPI::Vulkan; }
    bool IsInitialized() const override { return initialized; }

private:
    uint32_t nextTextureId = 1;
    uint32_t nextBufferId = 1;
    uint32_t nextShaderId = 1;

    // Resource tracking (simplified for now)
    std::unordered_map<uint32_t, TextureDesc> textures;
    std::unordered_map<uint32_t, BufferDesc> buffers;
    std::unordered_map<uint32_t, ShaderDesc> shaders;

    bool inRenderPass = false;
    bool inFrame = false;
};

} // namespace rendering
} // namespace pywrkgame
