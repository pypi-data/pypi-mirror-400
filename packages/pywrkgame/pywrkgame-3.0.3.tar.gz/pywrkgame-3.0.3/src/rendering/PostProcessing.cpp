#include "pywrkgame/rendering/PostProcessing.h"
#include <cmath>
#include <algorithm>

namespace pywrkgame {
namespace rendering {

// ============================================================================
// HDR and Tone Mapping Effect
// ============================================================================

HDRToneMappingEffect::HDRToneMappingEffect() = default;

HDRToneMappingEffect::~HDRToneMappingEffect() {
    Shutdown();
}

bool HDRToneMappingEffect::Initialize(GraphicsDevice* dev) {
    if (!dev) return false;
    
    device = dev;
    
    // Create shader for HDR tone mapping
    // In a real implementation, this would load actual shader code
    ShaderDesc shaderDesc{};
    shaderDesc.stage = ShaderStage::Fragment;
    shaderDesc.source = "// HDR Tone Mapping Shader";
    shader = device->CreateShader(shaderDesc);
    
    if (!shader.IsValid()) {
        return false;
    }
    
    // Create uniform buffer for parameters
    BufferDesc bufferDesc{};
    bufferDesc.size = 64; // Enough for exposure and tone mapping params
    bufferDesc.type = BufferType::Uniform;
    bufferDesc.dynamic = true;
    uniformBuffer = device->CreateBuffer(bufferDesc);
    
    return uniformBuffer.IsValid();
}

void HDRToneMappingEffect::Apply(TextureHandle input, TextureHandle output) {
    if (!enabled || !device || !shader.IsValid()) return;
    
    // Update uniform buffer with current parameters
    struct Uniforms {
        float exposure;
        int toneMappingOp;
        float padding[2];
    } uniforms;
    
    uniforms.exposure = exposure;
    uniforms.toneMappingOp = static_cast<int>(toneMappingOp);
    
    device->UpdateBuffer(uniformBuffer, &uniforms, sizeof(uniforms));
    
    // Apply tone mapping (simplified - actual implementation would use compute shader or render pass)
    // This is a placeholder for the actual GPU implementation
}

void HDRToneMappingEffect::Shutdown() {
    if (device) {
        if (shader.IsValid()) {
            device->DestroyShader(shader);
            shader = ShaderHandle{};
        }
        if (uniformBuffer.IsValid()) {
            device->DestroyBuffer(uniformBuffer);
            uniformBuffer = BufferHandle{};
        }
    }
    device = nullptr;
}

// ============================================================================
// Bloom Effect
// ============================================================================

BloomEffect::BloomEffect() = default;

BloomEffect::~BloomEffect() {
    Shutdown();
}

bool BloomEffect::Initialize(GraphicsDevice* dev) {
    if (!dev) return false;
    
    device = dev;
    
    // Create shaders for bloom passes
    ShaderDesc brightPassDesc{};
    brightPassDesc.stage = ShaderStage::Fragment;
    brightPassDesc.source = "// Bright Pass Shader";
    brightPassShader = device->CreateShader(brightPassDesc);
    
    ShaderDesc blurDesc{};
    blurDesc.stage = ShaderStage::Fragment;
    blurDesc.source = "// Gaussian Blur Shader";
    blurShader = device->CreateShader(blurDesc);
    
    ShaderDesc combineDesc{};
    combineDesc.stage = ShaderStage::Fragment;
    combineDesc.source = "// Combine Shader";
    combineShader = device->CreateShader(combineDesc);
    
    if (!brightPassShader.IsValid() || !blurShader.IsValid() || !combineShader.IsValid()) {
        Shutdown();
        return false;
    }
    
    // Create temporary textures for bloom passes
    // These would be created at the appropriate resolution
    tempTextures.resize(iterations * 2); // Horizontal and vertical blur for each iteration
    
    for (size_t i = 0; i < tempTextures.size(); ++i) {
        TextureDesc texDesc{};
        texDesc.width = 1920 >> (i / 2 + 1); // Downsample for each iteration
        texDesc.height = 1080 >> (i / 2 + 1);
        texDesc.format = TextureFormat::RGBA16F;
        texDesc.isRenderTarget = true;
        
        tempTextures[i] = device->CreateTexture(texDesc);
        if (!tempTextures[i].IsValid()) {
            Shutdown();
            return false;
        }
    }
    
    return true;
}

void BloomEffect::Apply(TextureHandle input, TextureHandle output) {
    if (!enabled || !device) return;
    if (!brightPassShader.IsValid() || !blurShader.IsValid() || !combineShader.IsValid()) return;
    
    // 1. Bright pass - extract bright pixels above threshold
    // 2. Downsample and blur multiple times
    // 3. Upsample and combine with original image
    
    // This is a placeholder for the actual GPU implementation
    // Real implementation would use compute shaders or render passes
}

void BloomEffect::Shutdown() {
    if (device) {
        if (brightPassShader.IsValid()) {
            device->DestroyShader(brightPassShader);
            brightPassShader = ShaderHandle{};
        }
        if (blurShader.IsValid()) {
            device->DestroyShader(blurShader);
            blurShader = ShaderHandle{};
        }
        if (combineShader.IsValid()) {
            device->DestroyShader(combineShader);
            combineShader = ShaderHandle{};
        }
        
        for (auto& texture : tempTextures) {
            if (texture.IsValid()) {
                device->DestroyTexture(texture);
            }
        }
        tempTextures.clear();
    }
    device = nullptr;
}

// ============================================================================
// SSAO Effect
// ============================================================================

SSAOEffect::SSAOEffect() = default;

SSAOEffect::~SSAOEffect() {
    Shutdown();
}

bool SSAOEffect::Initialize(GraphicsDevice* dev) {
    if (!dev) return false;
    
    device = dev;
    
    // Create SSAO shader
    ShaderDesc ssaoDesc{};
    ssaoDesc.stage = ShaderStage::Fragment;
    ssaoDesc.source = "// SSAO Shader";
    ssaoShader = device->CreateShader(ssaoDesc);
    
    // Create blur shader for SSAO
    ShaderDesc blurDesc{};
    blurDesc.stage = ShaderStage::Fragment;
    blurDesc.source = "// SSAO Blur Shader";
    blurShader = device->CreateShader(blurDesc);
    
    if (!ssaoShader.IsValid() || !blurShader.IsValid()) {
        Shutdown();
        return false;
    }
    
    // Create noise texture for SSAO
    TextureDesc noiseDesc{};
    noiseDesc.width = 4;
    noiseDesc.height = 4;
    noiseDesc.format = TextureFormat::RGB8;
    
    // Generate random noise
    float noiseData[4 * 4 * 3];
    for (int i = 0; i < 4 * 4 * 3; i += 3) {
        noiseData[i] = (float)rand() / RAND_MAX * 2.0f - 1.0f;
        noiseData[i + 1] = (float)rand() / RAND_MAX * 2.0f - 1.0f;
        noiseData[i + 2] = 0.0f;
    }
    
    noiseDesc.initialData = noiseData;
    noiseDesc.dataSize = sizeof(noiseData);
    noiseTexture = device->CreateTexture(noiseDesc);
    
    // Create sample kernel buffer
    BufferDesc kernelDesc{};
    kernelDesc.size = samples * 4 * sizeof(float); // vec4 per sample
    kernelDesc.type = BufferType::Uniform;
    kernelDesc.dynamic = false;
    
    // Generate sample kernel
    std::vector<float> kernelData(samples * 4);
    for (uint32_t i = 0; i < samples; ++i) {
        float scale = (float)i / (float)samples;
        scale = 0.1f + scale * scale * 0.9f; // Lerp between 0.1 and 1.0
        
        kernelData[i * 4 + 0] = ((float)rand() / RAND_MAX * 2.0f - 1.0f) * scale;
        kernelData[i * 4 + 1] = ((float)rand() / RAND_MAX * 2.0f - 1.0f) * scale;
        kernelData[i * 4 + 2] = ((float)rand() / RAND_MAX) * scale;
        kernelData[i * 4 + 3] = 0.0f;
    }
    
    kernelDesc.initialData = kernelData.data();
    sampleKernel = device->CreateBuffer(kernelDesc);
    
    return noiseTexture.IsValid() && sampleKernel.IsValid();
}

void SSAOEffect::Apply(TextureHandle input, TextureHandle output) {
    if (!enabled || !device) return;
    if (!ssaoShader.IsValid() || !blurShader.IsValid()) return;
    
    // 1. Generate SSAO texture using depth and normal buffers
    // 2. Blur SSAO texture to reduce noise
    // 3. Apply to final image
    
    // This is a placeholder for the actual GPU implementation
}

void SSAOEffect::Shutdown() {
    if (device) {
        if (ssaoShader.IsValid()) {
            device->DestroyShader(ssaoShader);
            ssaoShader = ShaderHandle{};
        }
        if (blurShader.IsValid()) {
            device->DestroyShader(blurShader);
            blurShader = ShaderHandle{};
        }
        if (noiseTexture.IsValid()) {
            device->DestroyTexture(noiseTexture);
            noiseTexture = TextureHandle{};
        }
        if (sampleKernel.IsValid()) {
            device->DestroyBuffer(sampleKernel);
            sampleKernel = BufferHandle{};
        }
    }
    device = nullptr;
}

// ============================================================================
// Motion Blur Effect
// ============================================================================

MotionBlurEffect::MotionBlurEffect() = default;

MotionBlurEffect::~MotionBlurEffect() {
    Shutdown();
}

bool MotionBlurEffect::Initialize(GraphicsDevice* dev) {
    if (!dev) return false;
    
    device = dev;
    
    // Create motion blur shader
    ShaderDesc shaderDesc{};
    shaderDesc.stage = ShaderStage::Fragment;
    shaderDesc.source = "// Motion Blur Shader";
    shader = device->CreateShader(shaderDesc);
    
    if (!shader.IsValid()) {
        return false;
    }
    
    // Create velocity buffer
    TextureDesc velocityDesc{};
    velocityDesc.width = 1920;
    velocityDesc.height = 1080;
    velocityDesc.format = TextureFormat::RG8;
    velocityDesc.isRenderTarget = true;
    velocityBuffer = device->CreateTexture(velocityDesc);
    
    return velocityBuffer.IsValid();
}

void MotionBlurEffect::Apply(TextureHandle input, TextureHandle output) {
    if (!enabled || !device || !shader.IsValid()) return;
    
    // Apply motion blur using velocity buffer
    // This is a placeholder for the actual GPU implementation
}

void MotionBlurEffect::Shutdown() {
    if (device) {
        if (shader.IsValid()) {
            device->DestroyShader(shader);
            shader = ShaderHandle{};
        }
        if (velocityBuffer.IsValid()) {
            device->DestroyTexture(velocityBuffer);
            velocityBuffer = TextureHandle{};
        }
    }
    device = nullptr;
}

// ============================================================================
// Post-Processing Pipeline
// ============================================================================

PostProcessingPipeline::PostProcessingPipeline() = default;

PostProcessingPipeline::~PostProcessingPipeline() {
    Shutdown();
}

bool PostProcessingPipeline::Initialize(GraphicsDevice* dev, const PostProcessConfig& cfg) {
    if (!dev) return false;
    if (initialized) return false;
    
    device = dev;
    config = cfg;
    
    // Create and initialize HDR/Tone Mapping effect
    auto hdr = std::make_unique<HDRToneMappingEffect>();
    if (!hdr->Initialize(device)) {
        return false;
    }
    hdr->SetEnabled(config.enableHDR && config.enableToneMapping);
    hdr->SetExposure(config.exposure);
    hdr->SetToneMappingOperator(config.toneMappingOp);
    hdrEffect = hdr.get();
    effects.push_back(std::move(hdr));
    
    // Create and initialize Bloom effect
    auto bloom = std::make_unique<BloomEffect>();
    if (!bloom->Initialize(device)) {
        Shutdown();
        return false;
    }
    bloom->SetEnabled(config.enableBloom);
    bloom->SetThreshold(config.bloomThreshold);
    bloom->SetIntensity(config.bloomIntensity);
    bloom->SetIterations(config.bloomIterations);
    bloomEffect = bloom.get();
    effects.push_back(std::move(bloom));
    
    // Create and initialize SSAO effect
    auto ssao = std::make_unique<SSAOEffect>();
    if (!ssao->Initialize(device)) {
        Shutdown();
        return false;
    }
    ssao->SetEnabled(config.enableSSAO);
    ssao->SetRadius(config.ssaoRadius);
    ssao->SetBias(config.ssaoBias);
    ssao->SetSamples(config.ssaoSamples);
    ssaoEffect = ssao.get();
    effects.push_back(std::move(ssao));
    
    // Create and initialize Motion Blur effect
    auto motionBlur = std::make_unique<MotionBlurEffect>();
    if (!motionBlur->Initialize(device)) {
        Shutdown();
        return false;
    }
    motionBlur->SetEnabled(config.enableMotionBlur);
    motionBlur->SetStrength(config.motionBlurStrength);
    motionBlur->SetSamples(config.motionBlurSamples);
    motionBlurEffect = motionBlur.get();
    effects.push_back(std::move(motionBlur));
    
    // Create intermediate render targets
    CreateIntermediateTargets();
    
    initialized = true;
    return true;
}

void PostProcessingPipeline::Shutdown() {
    if (!initialized) return;
    
    DestroyIntermediateTargets();
    
    // Clear effect pointers (they're owned by the effects vector)
    hdrEffect = nullptr;
    bloomEffect = nullptr;
    ssaoEffect = nullptr;
    motionBlurEffect = nullptr;
    
    // Shutdown and destroy all effects
    for (auto& effect : effects) {
        if (effect) {
            effect->Shutdown();
        }
    }
    effects.clear();
    
    device = nullptr;
    initialized = false;
}

void PostProcessingPipeline::Apply(TextureHandle input, TextureHandle output) {
    if (!initialized || !device) return;
    if (!input.IsValid() || !output.IsValid()) return;
    
    // If no effects are enabled, just copy input to output
    bool anyEnabled = false;
    for (const auto& effect : effects) {
        if (effect && effect->IsEnabled()) {
            anyEnabled = true;
            break;
        }
    }
    
    if (!anyEnabled) {
        // Direct copy (would use blit in real implementation)
        return;
    }
    
    // Apply effects in chain using intermediate targets
    TextureHandle currentInput = input;
    TextureHandle currentOutput;
    
    size_t intermediateIndex = 0;
    for (size_t i = 0; i < effects.size(); ++i) {
        if (!effects[i] || !effects[i]->IsEnabled()) {
            continue;
        }
        
        // Determine output target
        if (i == effects.size() - 1) {
            // Last effect outputs to final target
            currentOutput = output;
        } else {
            // Use intermediate target
            if (intermediateIndex < intermediateTargets.size()) {
                currentOutput = intermediateTargets[intermediateIndex];
                intermediateIndex++;
            } else {
                // Fallback to output if we run out of intermediate targets
                currentOutput = output;
            }
        }
        
        // Apply effect
        effects[i]->Apply(currentInput, currentOutput);
        
        // Output becomes input for next effect
        currentInput = currentOutput;
    }
}

void PostProcessingPipeline::SetConfig(const PostProcessConfig& cfg) {
    config = cfg;
    
    // Update individual effects
    if (hdrEffect) {
        hdrEffect->SetEnabled(config.enableHDR && config.enableToneMapping);
        hdrEffect->SetExposure(config.exposure);
        hdrEffect->SetToneMappingOperator(config.toneMappingOp);
    }
    
    if (bloomEffect) {
        bloomEffect->SetEnabled(config.enableBloom);
        bloomEffect->SetThreshold(config.bloomThreshold);
        bloomEffect->SetIntensity(config.bloomIntensity);
        bloomEffect->SetIterations(config.bloomIterations);
    }
    
    if (ssaoEffect) {
        ssaoEffect->SetEnabled(config.enableSSAO);
        ssaoEffect->SetRadius(config.ssaoRadius);
        ssaoEffect->SetBias(config.ssaoBias);
        ssaoEffect->SetSamples(config.ssaoSamples);
    }
    
    if (motionBlurEffect) {
        motionBlurEffect->SetEnabled(config.enableMotionBlur);
        motionBlurEffect->SetStrength(config.motionBlurStrength);
        motionBlurEffect->SetSamples(config.motionBlurSamples);
    }
}

void PostProcessingPipeline::AddEffect(std::unique_ptr<PostProcessEffect_Base> effect) {
    if (effect) {
        effects.push_back(std::move(effect));
    }
}

void PostProcessingPipeline::RemoveEffect(size_t index) {
    if (index < effects.size()) {
        effects.erase(effects.begin() + index);
    }
}

void PostProcessingPipeline::ClearEffects() {
    for (auto& effect : effects) {
        if (effect) {
            effect->Shutdown();
        }
    }
    effects.clear();
    
    hdrEffect = nullptr;
    bloomEffect = nullptr;
    ssaoEffect = nullptr;
    motionBlurEffect = nullptr;
}

PostProcessEffect_Base* PostProcessingPipeline::GetEffect(size_t index) {
    if (index < effects.size()) {
        return effects[index].get();
    }
    return nullptr;
}

void PostProcessingPipeline::CreateIntermediateTargets() {
    if (!device) return;
    
    // Create intermediate render targets for effect chaining
    // We need at least as many as there are enabled effects minus one
    const size_t numTargets = 3; // Enough for most effect chains
    
    intermediateTargets.resize(numTargets);
    
    for (size_t i = 0; i < numTargets; ++i) {
        TextureDesc desc{};
        desc.width = 1920;
        desc.height = 1080;
        desc.format = TextureFormat::RGBA16F; // HDR format
        desc.isRenderTarget = true;
        
        intermediateTargets[i] = device->CreateTexture(desc);
    }
}

void PostProcessingPipeline::DestroyIntermediateTargets() {
    if (!device) return;
    
    for (auto& target : intermediateTargets) {
        if (target.IsValid()) {
            device->DestroyTexture(target);
        }
    }
    intermediateTargets.clear();
}

} // namespace rendering
} // namespace pywrkgame
