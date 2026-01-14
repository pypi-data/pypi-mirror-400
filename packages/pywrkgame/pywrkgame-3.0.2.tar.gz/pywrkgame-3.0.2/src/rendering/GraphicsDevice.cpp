#include "pywrkgame/rendering/GraphicsDevice.h"
#include "pywrkgame/rendering/VulkanDevice.h"
#include "pywrkgame/rendering/MetalDevice.h"
#include "pywrkgame/rendering/D3D12Device.h"

namespace pywrkgame {
namespace rendering {

std::unique_ptr<GraphicsDevice> CreateGraphicsDevice(GraphicsAPI api) {
    // Automatic API selection based on platform
    if (api == GraphicsAPI::Auto) {
#if defined(__APPLE__)
        api = GraphicsAPI::Metal;
#elif defined(_WIN32)
        api = GraphicsAPI::D3D12;
#else
        api = GraphicsAPI::Vulkan;
#endif
    }

    // Create appropriate device
    switch (api) {
        case GraphicsAPI::Vulkan:
            return std::make_unique<VulkanDevice>();
        case GraphicsAPI::Metal:
            return std::make_unique<MetalDevice>();
        case GraphicsAPI::D3D12:
            return std::make_unique<D3D12Device>();
        default:
            return nullptr;
    }
}

} // namespace rendering
} // namespace pywrkgame
