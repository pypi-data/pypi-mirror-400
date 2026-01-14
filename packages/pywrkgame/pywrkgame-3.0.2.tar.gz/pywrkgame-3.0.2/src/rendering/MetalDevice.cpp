#include "pywrkgame/rendering/MetalDevice.h"

namespace pywrkgame {
namespace rendering {

MetalDevice::MetalDevice() = default;

MetalDevice::~MetalDevice() {
    if (initialized) {
        Shutdown();
    }
}

bool MetalDevice::Initialize() {
    if (initialized) {
        return false;
    }

    // Simplified Metal initialization
    // In a real implementation, this would:
    // - Create MTLDevice
    // - Create command queue
    // - Setup drawable and render pass descriptors

    initialized = true;
    return true;
}

void MetalDevice::Shutdown() {
    if (!initialized) {
        return;
    }

    textures.clear();
    buffers.clear();
    shaders.clear();

    initialized = false;
}

void MetalDevice::BeginFrame() {
    if (!initialized) {
        return;
    }
    inFrame = true;
}

void MetalDevice::EndFrame() {
    if (!initialized || !inFrame) {
        return;
    }
    inFrame = false;
}

void MetalDevice::Present() {
    if (!initialized) {
        return;
    }
    // Present drawable
}

TextureHandle MetalDevice::CreateTexture(const TextureDesc& desc) {
    if (!initialized) {
        return TextureHandle{};
    }

    TextureHandle handle;
    handle.id = nextTextureId++;
    handle.generation = 1;

    textures[handle.id] = desc;

    return handle;
}

BufferHandle MetalDevice::CreateBuffer(const BufferDesc& desc) {
    if (!initialized) {
        return BufferHandle{};
    }

    BufferHandle handle;
    handle.id = nextBufferId++;
    handle.generation = 1;

    buffers[handle.id] = desc;

    return handle;
}

ShaderHandle MetalDevice::CreateShader(const ShaderDesc& desc) {
    if (!initialized) {
        return ShaderHandle{};
    }

    ShaderHandle handle;
    handle.id = nextShaderId++;
    handle.generation = 1;

    shaders[handle.id] = desc;

    return handle;
}

void MetalDevice::DestroyTexture(TextureHandle handle) {
    if (!initialized || !handle.IsValid()) {
        return;
    }

    textures.erase(handle.id);
}

void MetalDevice::DestroyBuffer(BufferHandle handle) {
    if (!initialized || !handle.IsValid()) {
        return;
    }

    buffers.erase(handle.id);
}

void MetalDevice::DestroyShader(ShaderHandle handle) {
    if (!initialized || !handle.IsValid()) {
        return;
    }

    shaders.erase(handle.id);
}

void MetalDevice::UpdateBuffer(BufferHandle handle, const void* data, size_t size, size_t offset) {
    if (!initialized || !handle.IsValid() || !data) {
        return;
    }
    // Update MTLBuffer
}

void MetalDevice::UpdateTexture(TextureHandle handle, const void* data, size_t size, uint32_t mipLevel) {
    if (!initialized || !handle.IsValid() || !data) {
        return;
    }
    // Update MTLTexture
}

void MetalDevice::BeginRenderPass() {
    if (!initialized || !inFrame) {
        return;
    }
    inRenderPass = true;
}

void MetalDevice::EndRenderPass() {
    if (!initialized || !inRenderPass) {
        return;
    }
    inRenderPass = false;
}

void MetalDevice::Draw(uint32_t vertexCount, uint32_t instanceCount, uint32_t firstVertex, uint32_t firstInstance) {
    if (!initialized || !inRenderPass) {
        return;
    }
    // Metal draw call
}

void MetalDevice::DrawIndexed(uint32_t indexCount, uint32_t instanceCount, uint32_t firstIndex, int32_t vertexOffset, uint32_t firstInstance) {
    if (!initialized || !inRenderPass) {
        return;
    }
    // Metal indexed draw call
}

void MetalDevice::SetViewport(float x, float y, float width, float height) {
    if (!initialized) {
        return;
    }
    // Set Metal viewport
}

void MetalDevice::SetScissor(int32_t x, int32_t y, uint32_t width, uint32_t height) {
    if (!initialized) {
        return;
    }
    // Set Metal scissor rect
}

} // namespace rendering
} // namespace pywrkgame
