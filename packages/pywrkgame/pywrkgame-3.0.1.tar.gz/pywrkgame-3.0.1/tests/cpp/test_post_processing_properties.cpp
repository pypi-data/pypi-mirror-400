/**
 * Property-Based Tests for Post-Processing System
 * Feature: pywrkgame-library, Property 7: Post-Processing Effects
 * Validates: Requirements 3.4
 * 
 * Property 7: Post-Processing Effects
 * For any scene with enabled post-processing effects (bloom, HDR, SSAO, motion blur), 
 * each effect should render correctly without artifacts
 */

#include <gtest/gtest.h>
#include <rapidcheck/gtest.h>
#include "pywrkgame/rendering/RenderingEngine.h"
#include "pywrkgame/rendering/PostProcessing.h"
#include <cmath>
#include <algorithm>

using namespace pywrkgame::rendering;

// Helper function to validate post-processing configuration
bool IsValidPostProcessConfig(const PostProcessConfig& config) {
    // Exposure should be positive
    if (config.exposure <= 0.0f) {
        return false;
    }
    
    // Bloom threshold should be non-negative
    if (config.bloomThreshold < 0.0f) {
        return false;
    }
    
    // Bloom intensity should be in [0, 1] range
    if (config.bloomIntensity < 0.0f || config.bloomIntensity > 1.0f) {
        return false;
    }
    
    // Bloom iterations should be reasonable (1-10)
    if (config.bloomIterations < 1 || config.bloomIterations > 10) {
        return false;
    }
    
    // SSAO radius should be positive
    if (config.ssaoRadius <= 0.0f) {
        return false;
    }
    
    // SSAO bias should be non-negative and small
    if (config.ssaoBias < 0.0f || config.ssaoBias > 1.0f) {
        return false;
    }
    
    // SSAO samples should be reasonable (4-64)
    if (config.ssaoSamples < 4 || config.ssaoSamples > 64) {
        return false;
    }
    
    // Motion blur strength should be non-negative
    if (config.motionBlurStrength < 0.0f) {
        return false;
    }
    
    // Motion blur samples should be reasonable (2-32)
    if (config.motionBlurSamples < 2 || config.motionBlurSamples > 32) {
        return false;
    }
    
    return true;
}

// Generator for valid post-processing configuration
namespace rc {
    template<>
    struct Arbitrary<PostProcessConfig> {
        static Gen<PostProcessConfig> arbitrary() {
            return gen::build<PostProcessConfig>(
                gen::set(&PostProcessConfig::enableHDR, gen::arbitrary<bool>()),
                gen::set(&PostProcessConfig::exposure, gen::inRange(0.1f, 10.0f)),
                gen::set(&PostProcessConfig::enableToneMapping, gen::arbitrary<bool>()),
                gen::set(&PostProcessConfig::toneMappingOp, 
                    gen::element(
                        ToneMappingOperator::Reinhard,
                        ToneMappingOperator::Filmic,
                        ToneMappingOperator::ACES,
                        ToneMappingOperator::Uncharted2
                    )
                ),
                gen::set(&PostProcessConfig::enableBloom, gen::arbitrary<bool>()),
                gen::set(&PostProcessConfig::bloomThreshold, gen::inRange(0.0f, 5.0f)),
                gen::set(&PostProcessConfig::bloomIntensity, gen::inRange(0.0f, 1.0f)),
                gen::set(&PostProcessConfig::bloomIterations, gen::inRange(1u, 11u)),
                gen::set(&PostProcessConfig::enableSSAO, gen::arbitrary<bool>()),
                gen::set(&PostProcessConfig::ssaoRadius, gen::inRange(0.1f, 2.0f)),
                gen::set(&PostProcessConfig::ssaoBias, gen::inRange(0.0f, 0.1f)),
                gen::set(&PostProcessConfig::ssaoSamples, gen::inRange(4u, 65u)),
                gen::set(&PostProcessConfig::enableMotionBlur, gen::arbitrary<bool>()),
                gen::set(&PostProcessConfig::motionBlurStrength, gen::inRange(0.0f, 5.0f)),
                gen::set(&PostProcessConfig::motionBlurSamples, gen::inRange(2u, 33u))
            );
        }
    };
}

class PostProcessingTest : public ::testing::Test {
protected:
    void SetUp() override {
        renderer = std::make_unique<RenderingEngine>();
        ASSERT_TRUE(renderer->Initialize());
    }
    
    void TearDown() override {
        renderer->Shutdown();
    }
    
    std::unique_ptr<RenderingEngine> renderer;
};

// Unit test: Post-processing pipeline initialization
TEST_F(PostProcessingTest, PostProcessingInitialization) {
    PostProcessConfig config{};
    config.enableHDR = true;
    config.enableToneMapping = true;
    config.enableBloom = false;
    config.enableSSAO = false;
    config.enableMotionBlur = false;
    
    EXPECT_TRUE(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    ASSERT_NE(postProcessing, nullptr);
    EXPECT_TRUE(postProcessing->IsInitialized());
}

// Unit test: HDR and tone mapping effect
TEST_F(PostProcessingTest, HDRToneMappingEffect) {
    PostProcessConfig config{};
    config.enableHDR = true;
    config.enableToneMapping = true;
    config.exposure = 1.5f;
    config.toneMappingOp = ToneMappingOperator::ACES;
    
    ASSERT_TRUE(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    ASSERT_NE(postProcessing, nullptr);
    
    auto* hdrEffect = postProcessing->GetHDREffect();
    ASSERT_NE(hdrEffect, nullptr);
    EXPECT_TRUE(hdrEffect->IsEnabled());
    EXPECT_FLOAT_EQ(hdrEffect->GetExposure(), 1.5f);
    EXPECT_EQ(hdrEffect->GetToneMappingOperator(), ToneMappingOperator::ACES);
}

// Unit test: Bloom effect configuration
TEST_F(PostProcessingTest, BloomEffectConfiguration) {
    PostProcessConfig config{};
    config.enableBloom = true;
    config.bloomThreshold = 1.2f;
    config.bloomIntensity = 0.7f;
    config.bloomIterations = 6;
    
    ASSERT_TRUE(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    ASSERT_NE(postProcessing, nullptr);
    
    auto* bloomEffect = postProcessing->GetBloomEffect();
    ASSERT_NE(bloomEffect, nullptr);
    EXPECT_TRUE(bloomEffect->IsEnabled());
    EXPECT_FLOAT_EQ(bloomEffect->GetThreshold(), 1.2f);
    EXPECT_FLOAT_EQ(bloomEffect->GetIntensity(), 0.7f);
    EXPECT_EQ(bloomEffect->GetIterations(), 6u);
}

// Unit test: SSAO effect configuration
TEST_F(PostProcessingTest, SSAOEffectConfiguration) {
    PostProcessConfig config{};
    config.enableSSAO = true;
    config.ssaoRadius = 0.8f;
    config.ssaoBias = 0.03f;
    config.ssaoSamples = 32;
    
    ASSERT_TRUE(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    ASSERT_NE(postProcessing, nullptr);
    
    auto* ssaoEffect = postProcessing->GetSSAOEffect();
    ASSERT_NE(ssaoEffect, nullptr);
    EXPECT_TRUE(ssaoEffect->IsEnabled());
    EXPECT_FLOAT_EQ(ssaoEffect->GetRadius(), 0.8f);
    EXPECT_FLOAT_EQ(ssaoEffect->GetBias(), 0.03f);
    EXPECT_EQ(ssaoEffect->GetSamples(), 32u);
}

// Unit test: Motion blur effect configuration
TEST_F(PostProcessingTest, MotionBlurEffectConfiguration) {
    PostProcessConfig config{};
    config.enableMotionBlur = true;
    config.motionBlurStrength = 1.5f;
    config.motionBlurSamples = 12;
    
    ASSERT_TRUE(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    ASSERT_NE(postProcessing, nullptr);
    
    auto* motionBlurEffect = postProcessing->GetMotionBlurEffect();
    ASSERT_NE(motionBlurEffect, nullptr);
    EXPECT_TRUE(motionBlurEffect->IsEnabled());
    EXPECT_FLOAT_EQ(motionBlurEffect->GetStrength(), 1.5f);
    EXPECT_EQ(motionBlurEffect->GetSamples(), 12u);
}

// Unit test: Enable/disable post-processing
TEST_F(PostProcessingTest, EnableDisablePostProcessing) {
    PostProcessConfig config{};
    ASSERT_TRUE(renderer->SetupPostProcessing(config));
    
    renderer->EnablePostProcessing(true);
    // Note: We can't directly check if it's enabled without adding a getter
    // This is just testing that the call doesn't crash
    
    renderer->EnablePostProcessing(false);
}

// Unit test: Update post-processing configuration
TEST_F(PostProcessingTest, UpdateConfiguration) {
    PostProcessConfig config{};
    config.enableBloom = false;
    config.bloomIntensity = 0.5f;
    
    ASSERT_TRUE(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    ASSERT_NE(postProcessing, nullptr);
    
    auto* bloomEffect = postProcessing->GetBloomEffect();
    ASSERT_NE(bloomEffect, nullptr);
    EXPECT_FALSE(bloomEffect->IsEnabled());
    EXPECT_FLOAT_EQ(bloomEffect->GetIntensity(), 0.5f);
    
    // Update configuration
    config.enableBloom = true;
    config.bloomIntensity = 0.8f;
    postProcessing->SetConfig(config);
    
    EXPECT_TRUE(bloomEffect->IsEnabled());
    EXPECT_FLOAT_EQ(bloomEffect->GetIntensity(), 0.8f);
}

// Unit test: Multiple effects enabled simultaneously
TEST_F(PostProcessingTest, MultipleEffectsEnabled) {
    PostProcessConfig config{};
    config.enableHDR = true;
    config.enableToneMapping = true;
    config.enableBloom = true;
    config.enableSSAO = true;
    config.enableMotionBlur = true;
    
    ASSERT_TRUE(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    ASSERT_NE(postProcessing, nullptr);
    
    EXPECT_TRUE(postProcessing->GetHDREffect()->IsEnabled());
    EXPECT_TRUE(postProcessing->GetBloomEffect()->IsEnabled());
    EXPECT_TRUE(postProcessing->GetSSAOEffect()->IsEnabled());
    EXPECT_TRUE(postProcessing->GetMotionBlurEffect()->IsEnabled());
}

// Property Test: Post-Processing Configuration Validation
RC_GTEST_PROP(PostProcessingPropertyTest, ConfigurationIsValid, ()) {
    /*
     * Feature: pywrkgame-library, Property 7: Post-Processing Effects
     * For any scene with enabled post-processing effects, each effect should 
     * render correctly without artifacts
     * 
     * This test verifies that:
     * 1. Any valid post-processing configuration can be created
     * 2. Configuration parameters are stored correctly
     * 3. Configuration parameters remain within valid ranges
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    // Generate random post-processing configuration
    auto config = *rc::gen::arbitrary<PostProcessConfig>();
    
    // Verify generated configuration is valid
    RC_ASSERT(IsValidPostProcessConfig(config));
    
    // Setup post-processing with generated configuration
    RC_ASSERT(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    RC_ASSERT(postProcessing != nullptr);
    RC_ASSERT(postProcessing->IsInitialized());
    
    // Verify configuration was applied correctly
    auto retrievedConfig = postProcessing->GetConfig();
    
    RC_ASSERT(retrievedConfig.enableHDR == config.enableHDR);
    RC_ASSERT(std::abs(retrievedConfig.exposure - config.exposure) < 0.0001f);
    RC_ASSERT(retrievedConfig.enableToneMapping == config.enableToneMapping);
    RC_ASSERT(retrievedConfig.toneMappingOp == config.toneMappingOp);
    
    RC_ASSERT(retrievedConfig.enableBloom == config.enableBloom);
    RC_ASSERT(std::abs(retrievedConfig.bloomThreshold - config.bloomThreshold) < 0.0001f);
    RC_ASSERT(std::abs(retrievedConfig.bloomIntensity - config.bloomIntensity) < 0.0001f);
    RC_ASSERT(retrievedConfig.bloomIterations == config.bloomIterations);
    
    RC_ASSERT(retrievedConfig.enableSSAO == config.enableSSAO);
    RC_ASSERT(std::abs(retrievedConfig.ssaoRadius - config.ssaoRadius) < 0.0001f);
    RC_ASSERT(std::abs(retrievedConfig.ssaoBias - config.ssaoBias) < 0.0001f);
    RC_ASSERT(retrievedConfig.ssaoSamples == config.ssaoSamples);
    
    RC_ASSERT(retrievedConfig.enableMotionBlur == config.enableMotionBlur);
    RC_ASSERT(std::abs(retrievedConfig.motionBlurStrength - config.motionBlurStrength) < 0.0001f);
    RC_ASSERT(retrievedConfig.motionBlurSamples == config.motionBlurSamples);
    
    // Verify retrieved configuration is still valid
    RC_ASSERT(IsValidPostProcessConfig(retrievedConfig));
    
    renderer->Shutdown();
}

// Property Test: Effect Enable/Disable State
RC_GTEST_PROP(PostProcessingPropertyTest, EffectStateIsCorrect, ()) {
    /*
     * Feature: pywrkgame-library, Property 7: Post-Processing Effects
     * 
     * This test verifies that:
     * 1. Effects can be enabled or disabled independently
     * 2. Effect state matches configuration
     * 3. Changing one effect's state doesn't affect others
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    // Generate random configuration
    auto config = *rc::gen::arbitrary<PostProcessConfig>();
    RC_ASSERT(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    RC_ASSERT(postProcessing != nullptr);
    
    // Verify each effect's enabled state matches configuration
    auto* hdrEffect = postProcessing->GetHDREffect();
    auto* bloomEffect = postProcessing->GetBloomEffect();
    auto* ssaoEffect = postProcessing->GetSSAOEffect();
    auto* motionBlurEffect = postProcessing->GetMotionBlurEffect();
    
    RC_ASSERT(hdrEffect != nullptr);
    RC_ASSERT(bloomEffect != nullptr);
    RC_ASSERT(ssaoEffect != nullptr);
    RC_ASSERT(motionBlurEffect != nullptr);
    
    // HDR effect is enabled if both HDR and tone mapping are enabled
    RC_ASSERT(hdrEffect->IsEnabled() == (config.enableHDR && config.enableToneMapping));
    RC_ASSERT(bloomEffect->IsEnabled() == config.enableBloom);
    RC_ASSERT(ssaoEffect->IsEnabled() == config.enableSSAO);
    RC_ASSERT(motionBlurEffect->IsEnabled() == config.enableMotionBlur);
    
    // Toggle bloom effect
    bool newBloomState = !config.enableBloom;
    bloomEffect->SetEnabled(newBloomState);
    RC_ASSERT(bloomEffect->IsEnabled() == newBloomState);
    
    // Verify other effects unchanged
    RC_ASSERT(hdrEffect->IsEnabled() == (config.enableHDR && config.enableToneMapping));
    RC_ASSERT(ssaoEffect->IsEnabled() == config.enableSSAO);
    RC_ASSERT(motionBlurEffect->IsEnabled() == config.enableMotionBlur);
    
    renderer->Shutdown();
}

// Property Test: Configuration Update
RC_GTEST_PROP(PostProcessingPropertyTest, ConfigurationUpdateWorks, ()) {
    /*
     * Feature: pywrkgame-library, Property 7: Post-Processing Effects
     * 
     * This test verifies that:
     * 1. Post-processing configuration can be updated after initialization
     * 2. Updated configuration is applied correctly to all effects
     * 3. Effects reflect the new configuration parameters
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    // Generate initial configuration
    auto config1 = *rc::gen::arbitrary<PostProcessConfig>();
    RC_ASSERT(renderer->SetupPostProcessing(config1));
    
    auto* postProcessing = renderer->GetPostProcessing();
    RC_ASSERT(postProcessing != nullptr);
    
    // Generate new configuration
    auto config2 = *rc::gen::arbitrary<PostProcessConfig>();
    postProcessing->SetConfig(config2);
    
    // Verify new configuration was applied
    auto retrievedConfig = postProcessing->GetConfig();
    
    RC_ASSERT(std::abs(retrievedConfig.exposure - config2.exposure) < 0.0001f);
    RC_ASSERT(std::abs(retrievedConfig.bloomThreshold - config2.bloomThreshold) < 0.0001f);
    RC_ASSERT(std::abs(retrievedConfig.bloomIntensity - config2.bloomIntensity) < 0.0001f);
    RC_ASSERT(retrievedConfig.bloomIterations == config2.bloomIterations);
    RC_ASSERT(std::abs(retrievedConfig.ssaoRadius - config2.ssaoRadius) < 0.0001f);
    RC_ASSERT(std::abs(retrievedConfig.ssaoBias - config2.ssaoBias) < 0.0001f);
    RC_ASSERT(retrievedConfig.ssaoSamples == config2.ssaoSamples);
    RC_ASSERT(std::abs(retrievedConfig.motionBlurStrength - config2.motionBlurStrength) < 0.0001f);
    RC_ASSERT(retrievedConfig.motionBlurSamples == config2.motionBlurSamples);
    
    // Verify effects reflect new configuration
    auto* hdrEffect = postProcessing->GetHDREffect();
    auto* bloomEffect = postProcessing->GetBloomEffect();
    auto* ssaoEffect = postProcessing->GetSSAOEffect();
    auto* motionBlurEffect = postProcessing->GetMotionBlurEffect();
    
    RC_ASSERT(std::abs(hdrEffect->GetExposure() - config2.exposure) < 0.0001f);
    RC_ASSERT(std::abs(bloomEffect->GetThreshold() - config2.bloomThreshold) < 0.0001f);
    RC_ASSERT(std::abs(bloomEffect->GetIntensity() - config2.bloomIntensity) < 0.0001f);
    RC_ASSERT(bloomEffect->GetIterations() == config2.bloomIterations);
    RC_ASSERT(std::abs(ssaoEffect->GetRadius() - config2.ssaoRadius) < 0.0001f);
    RC_ASSERT(std::abs(ssaoEffect->GetBias() - config2.ssaoBias) < 0.0001f);
    RC_ASSERT(ssaoEffect->GetSamples() == config2.ssaoSamples);
    RC_ASSERT(std::abs(motionBlurEffect->GetStrength() - config2.motionBlurStrength) < 0.0001f);
    RC_ASSERT(motionBlurEffect->GetSamples() == config2.motionBlurSamples);
    
    renderer->Shutdown();
}

// Property Test: Effect Count
RC_GTEST_PROP(PostProcessingPropertyTest, EffectCountIsCorrect, ()) {
    /*
     * Feature: pywrkgame-library, Property 7: Post-Processing Effects
     * 
     * This test verifies that:
     * 1. Post-processing pipeline tracks all effects correctly
     * 2. Effect count matches the number of initialized effects
     * 3. Effects can be accessed by index
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    auto config = *rc::gen::arbitrary<PostProcessConfig>();
    RC_ASSERT(renderer->SetupPostProcessing(config));
    
    auto* postProcessing = renderer->GetPostProcessing();
    RC_ASSERT(postProcessing != nullptr);
    
    // Should have 4 built-in effects: HDR, Bloom, SSAO, Motion Blur
    size_t effectCount = postProcessing->GetEffectCount();
    RC_ASSERT(effectCount == 4);
    
    // Verify all effects can be accessed
    for (size_t i = 0; i < effectCount; ++i) {
        auto* effect = postProcessing->GetEffect(i);
        RC_ASSERT(effect != nullptr);
    }
    
    // Accessing out of bounds should return nullptr
    auto* invalidEffect = postProcessing->GetEffect(effectCount);
    RC_ASSERT(invalidEffect == nullptr);
    
    renderer->Shutdown();
}
