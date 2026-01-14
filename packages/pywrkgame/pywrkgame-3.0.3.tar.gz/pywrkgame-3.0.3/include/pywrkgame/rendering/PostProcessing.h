#pragma once

#include "GraphicsDevice.h"
#include "GraphicsTypes.h"
#include <memory>
#include <vector>
#include <functional>

namespace pywrkgame {
namespace rendering {

// Post-processing effect types
enum class PostProcessEffect {
    HDR,
    ToneMapping,
    Bloom,
    SSAO,
    MotionBlur,
    ColorGrading,
    Vignette,
    ChromaticAberration
};

// Tone mapping operators
enum class ToneMappingOperator {
    Reinhard,
    Filmic,
    ACES,
    Uncharted2
};

// Post-processing configuration
struct PostProcessConfig {
    // HDR settings
    bool enableHDR = true;
    float exposure = 1.0f;
    
    // Tone mapping settings
    bool enableToneMapping = true;
    ToneMappingOperator toneMappingOp = ToneMappingOperator::ACES;
    
    // Bloom settings
    bool enableBloom = false;
    float bloomThreshold = 1.0f;
    float bloomIntensity = 0.5f;
    uint32_t bloomIterations = 5;
    
    // SSAO settings
    bool enableSSAO = false;
    float ssaoRadius = 0.5f;
    float ssaoBias = 0.025f;
    uint32_t ssaoSamples = 16;
    
    // Motion blur settings
    bool enableMotionBlur = false;
    float motionBlurStrength = 1.0f;
    uint32_t motionBlurSamples = 8;
};

// Post-processing effect interface
class PostProcessEffect_Base {
public:
    virtual ~PostProcessEffect_Base() = default;
    virtual bool Initialize(GraphicsDevice* device) = 0;
    virtual void Apply(TextureHandle input, TextureHandle output) = 0;
    virtual void Shutdown() = 0;
    virtual bool IsEnabled() const = 0;
    virtual void SetEnabled(bool enabled) = 0;
};

// HDR and Tone Mapping effect
class HDRToneMappingEffect : public PostProcessEffect_Base {
public:
    HDRToneMappingEffect();
    ~HDRToneMappingEffect() override;
    
    bool Initialize(GraphicsDevice* device) override;
    void Apply(TextureHandle input, TextureHandle output) override;
    void Shutdown() override;
    
    bool IsEnabled() const override { return enabled; }
    void SetEnabled(bool value) override { enabled = value; }
    
    void SetExposure(float exposure) { this->exposure = exposure; }
    float GetExposure() const { return exposure; }
    
    void SetToneMappingOperator(ToneMappingOperator op) { toneMappingOp = op; }
    ToneMappingOperator GetToneMappingOperator() const { return toneMappingOp; }
    
private:
    GraphicsDevice* device = nullptr;
    bool enabled = true;
    float exposure = 1.0f;
    ToneMappingOperator toneMappingOp = ToneMappingOperator::ACES;
    
    ShaderHandle shader;
    BufferHandle uniformBuffer;
};

// Bloom effect
class BloomEffect : public PostProcessEffect_Base {
public:
    BloomEffect();
    ~BloomEffect() override;
    
    bool Initialize(GraphicsDevice* device) override;
    void Apply(TextureHandle input, TextureHandle output) override;
    void Shutdown() override;
    
    bool IsEnabled() const override { return enabled; }
    void SetEnabled(bool value) override { enabled = value; }
    
    void SetThreshold(float threshold) { this->threshold = threshold; }
    float GetThreshold() const { return threshold; }
    
    void SetIntensity(float intensity) { this->intensity = intensity; }
    float GetIntensity() const { return intensity; }
    
    void SetIterations(uint32_t iterations) { this->iterations = iterations; }
    uint32_t GetIterations() const { return iterations; }
    
private:
    GraphicsDevice* device = nullptr;
    bool enabled = false;
    float threshold = 1.0f;
    float intensity = 0.5f;
    uint32_t iterations = 5;
    
    ShaderHandle brightPassShader;
    ShaderHandle blurShader;
    ShaderHandle combineShader;
    std::vector<TextureHandle> tempTextures;
};

// SSAO (Screen Space Ambient Occlusion) effect
class SSAOEffect : public PostProcessEffect_Base {
public:
    SSAOEffect();
    ~SSAOEffect() override;
    
    bool Initialize(GraphicsDevice* device) override;
    void Apply(TextureHandle input, TextureHandle output) override;
    void Shutdown() override;
    
    bool IsEnabled() const override { return enabled; }
    void SetEnabled(bool value) override { enabled = value; }
    
    void SetRadius(float radius) { this->radius = radius; }
    float GetRadius() const { return radius; }
    
    void SetBias(float bias) { this->bias = bias; }
    float GetBias() const { return bias; }
    
    void SetSamples(uint32_t samples) { this->samples = samples; }
    uint32_t GetSamples() const { return samples; }
    
private:
    GraphicsDevice* device = nullptr;
    bool enabled = false;
    float radius = 0.5f;
    float bias = 0.025f;
    uint32_t samples = 16;
    
    ShaderHandle ssaoShader;
    ShaderHandle blurShader;
    TextureHandle noiseTexture;
    BufferHandle sampleKernel;
};

// Motion Blur effect
class MotionBlurEffect : public PostProcessEffect_Base {
public:
    MotionBlurEffect();
    ~MotionBlurEffect() override;
    
    bool Initialize(GraphicsDevice* device) override;
    void Apply(TextureHandle input, TextureHandle output) override;
    void Shutdown() override;
    
    bool IsEnabled() const override { return enabled; }
    void SetEnabled(bool value) override { enabled = value; }
    
    void SetStrength(float strength) { this->strength = strength; }
    float GetStrength() const { return strength; }
    
    void SetSamples(uint32_t samples) { this->samples = samples; }
    uint32_t GetSamples() const { return samples; }
    
private:
    GraphicsDevice* device = nullptr;
    bool enabled = false;
    float strength = 1.0f;
    uint32_t samples = 8;
    
    ShaderHandle shader;
    TextureHandle velocityBuffer;
};

// Post-processing pipeline manager
class PostProcessingPipeline {
public:
    PostProcessingPipeline();
    ~PostProcessingPipeline();
    
    bool Initialize(GraphicsDevice* device, const PostProcessConfig& config);
    void Shutdown();
    
    // Apply all enabled effects in the chain
    void Apply(TextureHandle input, TextureHandle output);
    
    // Configuration
    void SetConfig(const PostProcessConfig& config);
    PostProcessConfig GetConfig() const { return config; }
    
    // Effect management
    void AddEffect(std::unique_ptr<PostProcessEffect_Base> effect);
    void RemoveEffect(size_t index);
    void ClearEffects();
    size_t GetEffectCount() const { return effects.size(); }
    PostProcessEffect_Base* GetEffect(size_t index);
    
    // Individual effect access
    HDRToneMappingEffect* GetHDREffect() { return hdrEffect; }
    BloomEffect* GetBloomEffect() { return bloomEffect; }
    SSAOEffect* GetSSAOEffect() { return ssaoEffect; }
    MotionBlurEffect* GetMotionBlurEffect() { return motionBlurEffect; }
    
    bool IsInitialized() const { return initialized; }
    
private:
    bool initialized = false;
    GraphicsDevice* device = nullptr;
    PostProcessConfig config;
    
    // Built-in effects
    HDRToneMappingEffect* hdrEffect = nullptr;
    BloomEffect* bloomEffect = nullptr;
    SSAOEffect* ssaoEffect = nullptr;
    MotionBlurEffect* motionBlurEffect = nullptr;
    
    // Effect chain
    std::vector<std::unique_ptr<PostProcessEffect_Base>> effects;
    
    // Intermediate render targets
    std::vector<TextureHandle> intermediateTargets;
    
    void CreateIntermediateTargets();
    void DestroyIntermediateTargets();
};

} // namespace rendering
} // namespace pywrkgame
