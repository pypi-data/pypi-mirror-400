#pragma once

#include <cstdint>
#include <string>
#include <memory>
#include <vector>

namespace pywrkgame {
namespace rendering {

// Graphics API enumeration
enum class GraphicsAPI {
    Vulkan,
    Metal,
    D3D12,
    Auto  // Automatic selection based on platform
};

// Texture formats
enum class TextureFormat {
    RGBA8,
    RGBA16F,
    RGBA32F,
    RGB8,
    RG8,
    R8,
    Depth24Stencil8,
    Depth32F,
    DDS,
    KTX,
    ASTC
};

// Buffer types
enum class BufferType {
    Vertex,
    Index,
    Uniform,
    Storage
};

// Shader stages
enum class ShaderStage {
    Vertex,
    Fragment,
    Compute,
    Geometry,
    TessControl,
    TessEvaluation
};

// Resource handles (opaque types)
struct TextureHandle {
    uint32_t id = 0;
    uint32_t generation = 0;
    
    bool IsValid() const { return id != 0; }
    bool operator==(const TextureHandle& other) const {
        return id == other.id && generation == other.generation;
    }
};

struct BufferHandle {
    uint32_t id = 0;
    uint32_t generation = 0;
    
    bool IsValid() const { return id != 0; }
    bool operator==(const BufferHandle& other) const {
        return id == other.id && generation == other.generation;
    }
};

struct ShaderHandle {
    uint32_t id = 0;
    uint32_t generation = 0;
    
    bool IsValid() const { return id != 0; }
    bool operator==(const ShaderHandle& other) const {
        return id == other.id && generation == other.generation;
    }
};

// Resource descriptors
struct TextureDesc {
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t depth = 1;
    uint32_t mipLevels = 1;
    TextureFormat format = TextureFormat::RGBA8;
    bool isRenderTarget = false;
    bool isDepthStencil = false;
    const void* initialData = nullptr;
    size_t dataSize = 0;
};

// Mesh data structure
struct MeshData {
    std::vector<float> vertices;
    std::vector<uint32_t> indices;
    uint32_t vertexCount = 0;
    uint32_t indexCount = 0;
};

// Mesh handle
struct MeshHandle {
    uint32_t id = 0;
    uint32_t generation = 0;
    
    bool IsValid() const { return id != 0; }
    bool operator==(const MeshHandle& other) const {
        return id == other.id && generation == other.generation;
    }
};

// Material handle
struct MaterialHandle {
    uint32_t id = 0;
    uint32_t generation = 0;
    
    bool IsValid() const { return id != 0; }
    bool operator==(const MaterialHandle& other) const {
        return id == other.id && generation == other.generation;
    }
};

struct BufferDesc {
    size_t size = 0;
    BufferType type = BufferType::Vertex;
    const void* initialData = nullptr;
    bool dynamic = false;
};

struct ShaderDesc {
    ShaderStage stage = ShaderStage::Vertex;
    std::string source;
    std::string entryPoint = "main";
    bool isSpirV = false;  // For pre-compiled SPIR-V shaders
};

// PBR Material Properties
struct PBRMaterialProperties {
    float albedo[3] = {1.0f, 1.0f, 1.0f};  // Base color (RGB)
    float metallic = 0.0f;                  // Metallic factor [0, 1]
    float roughness = 0.5f;                 // Roughness factor [0, 1]
    float ao = 1.0f;                        // Ambient occlusion [0, 1]
    
    // Texture handles for PBR maps
    TextureHandle albedoMap;
    TextureHandle normalMap;
    TextureHandle metallicRoughnessMap;
    TextureHandle aoMap;
    TextureHandle emissiveMap;
    
    // Emissive properties
    float emissive[3] = {0.0f, 0.0f, 0.0f};
    float emissiveStrength = 1.0f;
    
    // Additional properties
    bool useAlbedoMap = false;
    bool useNormalMap = false;
    bool useMetallicRoughnessMap = false;
    bool useAOMap = false;
    bool useEmissiveMap = false;
};

// HDRI Environment Map
struct HDRIEnvironment {
    TextureHandle environmentMap;
    TextureHandle irradianceMap;
    TextureHandle prefilteredMap;
    TextureHandle brdfLUT;
    float intensity = 1.0f;
    float rotation = 0.0f;
};

} // namespace rendering
} // namespace pywrkgame
