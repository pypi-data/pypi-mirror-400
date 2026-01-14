#include "pywrkgame/rendering/PBRRenderer.h"
#include "pywrkgame/rendering/RenderingEngine.h"
#include "pywrkgame/rendering/GlobalIllumination.h"
#include <cstring>
#include <sstream>

namespace pywrkgame {
namespace rendering {

PBRRenderer::PBRRenderer() = default;

PBRRenderer::~PBRRenderer() {
    if (initialized) {
        Shutdown();
    }
}

bool PBRRenderer::Initialize(GraphicsDevice* dev) {
    if (initialized || !dev) {
        return false;
    }

    device = dev;

    // Compile PBR shaders based on the graphics API
    GraphicsAPI api = GraphicsAPI::Vulkan; // Default, should be queried from device
    if (!CompilePBRShaders(api)) {
        device = nullptr;
        return false;
    }

    // Initialize Global Illumination system
    globalIllumination = std::make_unique<GlobalIllumination>();
    if (!globalIllumination->Initialize(device)) {
        globalIllumination.reset();
        device->DestroyShader(pbrVertexShader);
        device->DestroyShader(pbrFragmentShader);
        pbrVertexShader = ShaderHandle{};
        pbrFragmentShader = ShaderHandle{};
        device = nullptr;
        return false;
    }

    initialized = true;
    return true;
}

void PBRRenderer::Shutdown() {
    if (!initialized) return;

    // Clean up Global Illumination
    if (globalIllumination) {
        globalIllumination->Shutdown();
        globalIllumination.reset();
    }

    // Clean up shaders
    if (device) {
        if (pbrVertexShader.IsValid()) {
            device->DestroyShader(pbrVertexShader);
        }
        if (pbrFragmentShader.IsValid()) {
            device->DestroyShader(pbrFragmentShader);
        }
    }

    // Clean up materials
    pbrMaterials.clear();

    // Clean up environment
    environment.reset();

    device = nullptr;
    initialized = false;
}

// PBR Material Management
uint32_t PBRRenderer::CreatePBRMaterial(const PBRMaterialProperties& properties) {
    if (!initialized) {
        return 0;
    }

    uint32_t materialId = nextMaterialId++;
    pbrMaterials[materialId] = properties;
    return materialId;
}

void PBRRenderer::DestroyPBRMaterial(uint32_t materialId) {
    if (!initialized || materialId == 0) return;

    auto it = pbrMaterials.find(materialId);
    if (it != pbrMaterials.end()) {
        pbrMaterials.erase(it);
    }
}

void PBRRenderer::UpdatePBRMaterial(uint32_t materialId, const PBRMaterialProperties& properties) {
    if (!initialized || materialId == 0) return;

    auto it = pbrMaterials.find(materialId);
    if (it != pbrMaterials.end()) {
        it->second = properties;
    }
}

const PBRMaterialProperties* PBRRenderer::GetPBRMaterial(uint32_t materialId) const {
    if (!initialized || materialId == 0) {
        return nullptr;
    }

    auto it = pbrMaterials.find(materialId);
    if (it != pbrMaterials.end()) {
        return &it->second;
    }
    return nullptr;
}

// Environment Lighting
bool PBRRenderer::SetupEnvironmentLighting(const HDRIEnvironment& hdri) {
    if (!initialized) {
        return false;
    }

    // Validate HDRI environment
    if (!hdri.environmentMap.IsValid()) {
        return false;
    }

    environment = std::make_unique<HDRIEnvironment>(hdri);
    return true;
}

void PBRRenderer::EnableEnvironmentLighting(bool enable) {
    if (!initialized) return;
    environmentLightingEnabled = enable && environment != nullptr;
}

// Rendering
void PBRRenderer::RenderPBRMesh(MeshHandle mesh, uint32_t materialId, const float* transform) {
    if (!initialized || !device || !mesh.IsValid() || materialId == 0) {
        return;
    }

    // Get material
    auto it = pbrMaterials.find(materialId);
    if (it == pbrMaterials.end()) {
        return;
    }

    const auto& material = it->second;

    // Bind PBR shaders
    // (In a real implementation, we would bind shaders and set uniforms here)
    
    // Set material properties as shader uniforms
    // (This would involve actual GPU buffer updates in a real implementation)
    
    // Bind textures
    if (material.useAlbedoMap && material.albedoMap.IsValid()) {
        // Bind albedo texture to slot 0
    }
    if (material.useNormalMap && material.normalMap.IsValid()) {
        // Bind normal texture to slot 1
    }
    if (material.useMetallicRoughnessMap && material.metallicRoughnessMap.IsValid()) {
        // Bind metallic-roughness texture to slot 2
    }
    if (material.useAOMap && material.aoMap.IsValid()) {
        // Bind AO texture to slot 3
    }
    if (material.useEmissiveMap && material.emissiveMap.IsValid()) {
        // Bind emissive texture to slot 4
    }

    // Bind environment maps if enabled
    if (environmentLightingEnabled && environment) {
        // Bind environment maps
    }

    // Draw mesh
    // (Actual draw call would be made here)
}

void PBRRenderer::BeginPBRPass() {
    if (!initialized || !device) return;
    
    // Begin render pass with PBR pipeline state
    device->BeginRenderPass();
}

void PBRRenderer::EndPBRPass() {
    if (!initialized || !device) return;
    
    device->EndRenderPass();
}

// Shader Compilation
bool PBRRenderer::CompilePBRShaders(GraphicsAPI api) {
    if (!device) {
        return false;
    }

    return CreateDefaultPBRShaders(api);
}

bool PBRRenderer::CreateDefaultPBRShaders(GraphicsAPI api) {
    // Generate vertex shader
    std::string vertexSource = GeneratePBRVertexShader(api);
    ShaderDesc vertexDesc{};
    vertexDesc.stage = ShaderStage::Vertex;
    vertexDesc.source = vertexSource;
    vertexDesc.isSpirV = false;

    pbrVertexShader = device->CreateShader(vertexDesc);
    if (!pbrVertexShader.IsValid()) {
        return false;
    }

    // Generate fragment shader
    std::string fragmentSource = GeneratePBRFragmentShader(api);
    ShaderDesc fragmentDesc{};
    fragmentDesc.stage = ShaderStage::Fragment;
    fragmentDesc.source = fragmentSource;
    fragmentDesc.isSpirV = false;

    pbrFragmentShader = device->CreateShader(fragmentDesc);
    if (!pbrFragmentShader.IsValid()) {
        device->DestroyShader(pbrVertexShader);
        pbrVertexShader = ShaderHandle{};
        return false;
    }

    return true;
}

std::string PBRRenderer::GeneratePBRVertexShader(GraphicsAPI api) {
    // Generate a basic PBR vertex shader
    // This is a simplified version - real implementation would be more complex
    
    std::stringstream ss;
    
    if (api == GraphicsAPI::Vulkan) {
        ss << "#version 450\n";
        ss << "layout(location = 0) in vec3 inPosition;\n";
        ss << "layout(location = 1) in vec3 inNormal;\n";
        ss << "layout(location = 2) in vec2 inTexCoord;\n";
        ss << "layout(location = 3) in vec3 inTangent;\n";
        ss << "\n";
        ss << "layout(location = 0) out vec3 fragPosition;\n";
        ss << "layout(location = 1) out vec3 fragNormal;\n";
        ss << "layout(location = 2) out vec2 fragTexCoord;\n";
        ss << "layout(location = 3) out vec3 fragTangent;\n";
        ss << "\n";
        ss << "layout(binding = 0) uniform UniformBufferObject {\n";
        ss << "    mat4 model;\n";
        ss << "    mat4 view;\n";
        ss << "    mat4 projection;\n";
        ss << "} ubo;\n";
        ss << "\n";
        ss << "void main() {\n";
        ss << "    vec4 worldPos = ubo.model * vec4(inPosition, 1.0);\n";
        ss << "    fragPosition = worldPos.xyz;\n";
        ss << "    fragNormal = mat3(transpose(inverse(ubo.model))) * inNormal;\n";
        ss << "    fragTexCoord = inTexCoord;\n";
        ss << "    fragTangent = mat3(ubo.model) * inTangent;\n";
        ss << "    gl_Position = ubo.projection * ubo.view * worldPos;\n";
        ss << "}\n";
    } else {
        // Fallback GLSL shader
        ss << "#version 330 core\n";
        ss << "layout(location = 0) in vec3 inPosition;\n";
        ss << "layout(location = 1) in vec3 inNormal;\n";
        ss << "layout(location = 2) in vec2 inTexCoord;\n";
        ss << "\n";
        ss << "out vec3 fragPosition;\n";
        ss << "out vec3 fragNormal;\n";
        ss << "out vec2 fragTexCoord;\n";
        ss << "\n";
        ss << "uniform mat4 model;\n";
        ss << "uniform mat4 view;\n";
        ss << "uniform mat4 projection;\n";
        ss << "\n";
        ss << "void main() {\n";
        ss << "    vec4 worldPos = model * vec4(inPosition, 1.0);\n";
        ss << "    fragPosition = worldPos.xyz;\n";
        ss << "    fragNormal = mat3(transpose(inverse(model))) * inNormal;\n";
        ss << "    fragTexCoord = inTexCoord;\n";
        ss << "    gl_Position = projection * view * worldPos;\n";
        ss << "}\n";
    }
    
    return ss.str();
}

std::string PBRRenderer::GeneratePBRFragmentShader(GraphicsAPI api) {
    // Generate a basic PBR fragment shader with Cook-Torrance BRDF
    // This is a simplified version - real implementation would be more complex
    
    std::stringstream ss;
    
    if (api == GraphicsAPI::Vulkan) {
        ss << "#version 450\n";
        ss << "layout(location = 0) in vec3 fragPosition;\n";
        ss << "layout(location = 1) in vec3 fragNormal;\n";
        ss << "layout(location = 2) in vec2 fragTexCoord;\n";
        ss << "layout(location = 3) in vec3 fragTangent;\n";
        ss << "\n";
        ss << "layout(location = 0) out vec4 outColor;\n";
        ss << "\n";
        ss << "layout(binding = 1) uniform MaterialProperties {\n";
        ss << "    vec3 albedo;\n";
        ss << "    float metallic;\n";
        ss << "    float roughness;\n";
        ss << "    float ao;\n";
        ss << "    vec3 emissive;\n";
        ss << "    float emissiveStrength;\n";
        ss << "} material;\n";
        ss << "\n";
        ss << "layout(binding = 2) uniform sampler2D albedoMap;\n";
        ss << "layout(binding = 3) uniform sampler2D normalMap;\n";
        ss << "layout(binding = 4) uniform sampler2D metallicRoughnessMap;\n";
        ss << "layout(binding = 5) uniform sampler2D aoMap;\n";
        ss << "layout(binding = 6) uniform sampler2D emissiveMap;\n";
        ss << "layout(binding = 7) uniform samplerCube irradianceMap;\n";
        ss << "layout(binding = 8) uniform samplerCube prefilteredMap;\n";
        ss << "layout(binding = 9) uniform sampler2D brdfLUT;\n";
        ss << "\n";
        ss << "const float PI = 3.14159265359;\n";
        ss << "\n";
        ss << "// PBR Functions\n";
        ss << "vec3 fresnelSchlick(float cosTheta, vec3 F0) {\n";
        ss << "    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);\n";
        ss << "}\n";
        ss << "\n";
        ss << "float DistributionGGX(vec3 N, vec3 H, float roughness) {\n";
        ss << "    float a = roughness * roughness;\n";
        ss << "    float a2 = a * a;\n";
        ss << "    float NdotH = max(dot(N, H), 0.0);\n";
        ss << "    float NdotH2 = NdotH * NdotH;\n";
        ss << "    float nom = a2;\n";
        ss << "    float denom = (NdotH2 * (a2 - 1.0) + 1.0);\n";
        ss << "    denom = PI * denom * denom;\n";
        ss << "    return nom / denom;\n";
        ss << "}\n";
        ss << "\n";
        ss << "float GeometrySchlickGGX(float NdotV, float roughness) {\n";
        ss << "    float r = (roughness + 1.0);\n";
        ss << "    float k = (r * r) / 8.0;\n";
        ss << "    float nom = NdotV;\n";
        ss << "    float denom = NdotV * (1.0 - k) + k;\n";
        ss << "    return nom / denom;\n";
        ss << "}\n";
        ss << "\n";
        ss << "float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {\n";
        ss << "    float NdotV = max(dot(N, V), 0.0);\n";
        ss << "    float NdotL = max(dot(N, L), 0.0);\n";
        ss << "    float ggx2 = GeometrySchlickGGX(NdotV, roughness);\n";
        ss << "    float ggx1 = GeometrySchlickGGX(NdotL, roughness);\n";
        ss << "    return ggx1 * ggx2;\n";
        ss << "}\n";
        ss << "\n";
        ss << "void main() {\n";
        ss << "    // Sample material properties\n";
        ss << "    vec3 albedo = material.albedo;\n";
        ss << "    float metallic = material.metallic;\n";
        ss << "    float roughness = material.roughness;\n";
        ss << "    float ao = material.ao;\n";
        ss << "    \n";
        ss << "    // Simple lighting calculation\n";
        ss << "    vec3 N = normalize(fragNormal);\n";
        ss << "    vec3 V = normalize(vec3(0.0, 0.0, 1.0) - fragPosition);\n";
        ss << "    \n";
        ss << "    // Calculate reflectance at normal incidence\n";
        ss << "    vec3 F0 = vec3(0.04);\n";
        ss << "    F0 = mix(F0, albedo, metallic);\n";
        ss << "    \n";
        ss << "    // Simple directional light\n";
        ss << "    vec3 L = normalize(vec3(1.0, 1.0, 1.0));\n";
        ss << "    vec3 H = normalize(V + L);\n";
        ss << "    vec3 radiance = vec3(1.0);\n";
        ss << "    \n";
        ss << "    // Cook-Torrance BRDF\n";
        ss << "    float NDF = DistributionGGX(N, H, roughness);\n";
        ss << "    float G = GeometrySmith(N, V, L, roughness);\n";
        ss << "    vec3 F = fresnelSchlick(max(dot(H, V), 0.0), F0);\n";
        ss << "    \n";
        ss << "    vec3 numerator = NDF * G * F;\n";
        ss << "    float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;\n";
        ss << "    vec3 specular = numerator / denominator;\n";
        ss << "    \n";
        ss << "    vec3 kS = F;\n";
        ss << "    vec3 kD = vec3(1.0) - kS;\n";
        ss << "    kD *= 1.0 - metallic;\n";
        ss << "    \n";
        ss << "    float NdotL = max(dot(N, L), 0.0);\n";
        ss << "    vec3 Lo = (kD * albedo / PI + specular) * radiance * NdotL;\n";
        ss << "    \n";
        ss << "    // Ambient lighting\n";
        ss << "    vec3 ambient = vec3(0.03) * albedo * ao;\n";
        ss << "    vec3 color = ambient + Lo;\n";
        ss << "    \n";
        ss << "    // Add emissive\n";
        ss << "    color += material.emissive * material.emissiveStrength;\n";
        ss << "    \n";
        ss << "    // HDR tonemapping\n";
        ss << "    color = color / (color + vec3(1.0));\n";
        ss << "    // Gamma correction\n";
        ss << "    color = pow(color, vec3(1.0/2.2));\n";
        ss << "    \n";
        ss << "    outColor = vec4(color, 1.0);\n";
        ss << "}\n";
    } else {
        // Fallback GLSL shader
        ss << "#version 330 core\n";
        ss << "in vec3 fragPosition;\n";
        ss << "in vec3 fragNormal;\n";
        ss << "in vec2 fragTexCoord;\n";
        ss << "\n";
        ss << "out vec4 outColor;\n";
        ss << "\n";
        ss << "uniform vec3 albedo;\n";
        ss << "uniform float metallic;\n";
        ss << "uniform float roughness;\n";
        ss << "uniform float ao;\n";
        ss << "\n";
        ss << "void main() {\n";
        ss << "    vec3 N = normalize(fragNormal);\n";
        ss << "    vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));\n";
        ss << "    float diff = max(dot(N, lightDir), 0.0);\n";
        ss << "    vec3 color = albedo * diff * ao;\n";
        ss << "    outColor = vec4(color, 1.0);\n";
        ss << "}\n";
    }
    
    return ss.str();
}

// Global Illumination
void PBRRenderer::EnableGlobalIllumination(GITechnique technique) {
    if (!initialized || !globalIllumination) {
        return;
    }

    globalIllumination->SetTechnique(technique);
    globalIllumination->Enable(true);
}

void PBRRenderer::DisableGlobalIllumination() {
    if (!initialized || !globalIllumination) {
        return;
    }

    globalIllumination->Enable(false);
}

} // namespace rendering
} // namespace pywrkgame
