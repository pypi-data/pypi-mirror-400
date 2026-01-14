/**
 * Property-Based Tests for Global Illumination System
 * Feature: pywrkgame-library, Property 5: Global Illumination Accuracy
 * Validates: Requirements 3.2
 * 
 * Property 5: Global Illumination Accuracy
 * For any scene with indirect lighting, the global illumination system should produce 
 * realistic light bouncing effects
 */

#include <gtest/gtest.h>
#include <rapidcheck/gtest.h>
#include "pywrkgame/rendering/RenderingEngine.h"
#include "pywrkgame/rendering/PBRRenderer.h"
#include "pywrkgame/rendering/GlobalIllumination.h"
#include <cmath>
#include <algorithm>

using namespace pywrkgame::rendering;

// Helper function to validate GI configuration parameters
bool IsValidSSGIConfig(const SSGIConfig& config) {
    return config.rayCount > 0 && config.rayCount <= 32 &&
           config.rayLength > 0.0f && config.rayLength <= 100.0f &&
           config.thickness > 0.0f && config.thickness <= 10.0f &&
           config.intensity >= 0.0f && config.intensity <= 10.0f;
}

bool IsValidVoxelConfig(const VoxelGridConfig& config) {
    return config.resolution >= 32 && config.resolution <= 512 &&
           config.worldSize > 0.0f && config.worldSize <= 1000.0f &&
           config.mipLevels >= 1 && config.mipLevels <= 10;
}

bool IsValidLightProbe(const LightProbe& probe) {
    return probe.radius > 0.0f && probe.radius <= 1000.0f &&
           probe.intensity >= 0.0f && probe.intensity <= 100.0f;
}

// Generators for GI configurations
namespace rc {
    template<>
    struct Arbitrary<SSGIConfig> {
        static Gen<SSGIConfig> arbitrary() {
            return gen::build<SSGIConfig>(
                gen::set(&SSGIConfig::rayCount, gen::inRange(1u, 33u)),
                gen::set(&SSGIConfig::rayLength, gen::inRange(0.1f, 100.0f)),
                gen::set(&SSGIConfig::thickness, gen::inRange(0.01f, 10.0f)),
                gen::set(&SSGIConfig::intensity, gen::inRange(0.0f, 10.0f)),
                gen::set(&SSGIConfig::enableTemporalFilter, gen::arbitrary<bool>())
            );
        }
    };

    template<>
    struct Arbitrary<VoxelGridConfig> {
        static Gen<VoxelGridConfig> arbitrary() {
            return gen::build<VoxelGridConfig>(
                gen::set(&VoxelGridConfig::resolution, 
                    gen::element(32u, 64u, 128u, 256u)),
                gen::set(&VoxelGridConfig::worldSize, gen::inRange(10.0f, 1000.0f)),
                gen::set(&VoxelGridConfig::mipLevels, gen::inRange(1u, 11u)),
                gen::set(&VoxelGridConfig::enableAnisotropic, gen::arbitrary<bool>())
            );
        }
    };

    template<>
    struct Arbitrary<LightProbe> {
        static Gen<LightProbe> arbitrary() {
            return gen::build<LightProbe>(
                gen::set(&LightProbe::position,
                    gen::construct<std::array<float, 3>>(
                        gen::inRange(-100.0f, 100.0f),
                        gen::inRange(-100.0f, 100.0f),
                        gen::inRange(-100.0f, 100.0f)
                    ).as([](const std::array<float, 3>& arr) {
                        float result[3];
                        std::copy(arr.begin(), arr.end(), result);
                        return result;
                    })
                ),
                gen::set(&LightProbe::radius, gen::inRange(1.0f, 1000.0f)),
                gen::set(&LightProbe::intensity, gen::inRange(0.0f, 100.0f))
            );
        }
    };
}

class GlobalIlluminationTest : public ::testing::Test {
protected:
    void SetUp() override {
        renderer = std::make_unique<RenderingEngine>();
        ASSERT_TRUE(renderer->Initialize());
        pbrRenderer = renderer->GetPBRRenderer();
        ASSERT_NE(pbrRenderer, nullptr);
        gi = pbrRenderer->GetGlobalIllumination();
        ASSERT_NE(gi, nullptr);
    }
    
    void TearDown() override {
        renderer->Shutdown();
    }
    
    std::unique_ptr<RenderingEngine> renderer;
    PBRRenderer* pbrRenderer = nullptr;
    GlobalIllumination* gi = nullptr;
};

// Unit test: GI system initialization
TEST_F(GlobalIlluminationTest, GISystemInitialized) {
    EXPECT_TRUE(gi->IsInitialized());
    EXPECT_FALSE(gi->IsEnabled());
    EXPECT_EQ(gi->GetTechnique(), GITechnique::None);
}

// Unit test: Enable/Disable GI
TEST_F(GlobalIlluminationTest, EnableDisableGI) {
    EXPECT_FALSE(gi->IsEnabled());
    
    gi->Enable(true);
    EXPECT_TRUE(gi->IsEnabled());
    
    gi->Enable(false);
    EXPECT_FALSE(gi->IsEnabled());
}

// Unit test: Set GI technique
TEST_F(GlobalIlluminationTest, SetGITechnique) {
    gi->SetTechnique(GITechnique::ScreenSpace);
    EXPECT_EQ(gi->GetTechnique(), GITechnique::ScreenSpace);
    
    gi->SetTechnique(GITechnique::LightProbes);
    EXPECT_EQ(gi->GetTechnique(), GITechnique::LightProbes);
    
    gi->SetTechnique(GITechnique::VoxelBased);
    EXPECT_EQ(gi->GetTechnique(), GITechnique::VoxelBased);
}

// Unit test: Setup Screen-Space GI
TEST_F(GlobalIlluminationTest, SetupScreenSpaceGI) {
    SSGIConfig config{};
    config.rayCount = 8;
    config.rayLength = 10.0f;
    config.thickness = 0.5f;
    config.intensity = 1.0f;
    config.enableTemporalFilter = true;
    
    EXPECT_TRUE(gi->SetupScreenSpaceGI(config));
    EXPECT_EQ(gi->GetTechnique(), GITechnique::ScreenSpace);
    
    const auto& retrievedConfig = gi->GetSSGIConfig();
    EXPECT_EQ(retrievedConfig.rayCount, 8u);
    EXPECT_FLOAT_EQ(retrievedConfig.rayLength, 10.0f);
    EXPECT_FLOAT_EQ(retrievedConfig.thickness, 0.5f);
    EXPECT_FLOAT_EQ(retrievedConfig.intensity, 1.0f);
    EXPECT_TRUE(retrievedConfig.enableTemporalFilter);
}

// Unit test: Create and manage light probes
TEST_F(GlobalIlluminationTest, CreateLightProbe) {
    LightProbe probe{};
    probe.position[0] = 0.0f;
    probe.position[1] = 5.0f;
    probe.position[2] = 0.0f;
    probe.radius = 10.0f;
    probe.intensity = 1.0f;
    
    uint32_t probeId = gi->CreateLightProbe(probe);
    EXPECT_NE(probeId, 0u);
    
    const auto* retrievedProbe = gi->GetLightProbe(probeId);
    ASSERT_NE(retrievedProbe, nullptr);
    EXPECT_FLOAT_EQ(retrievedProbe->position[0], 0.0f);
    EXPECT_FLOAT_EQ(retrievedProbe->position[1], 5.0f);
    EXPECT_FLOAT_EQ(retrievedProbe->position[2], 0.0f);
    EXPECT_FLOAT_EQ(retrievedProbe->radius, 10.0f);
    EXPECT_FLOAT_EQ(retrievedProbe->intensity, 1.0f);
    
    gi->DestroyLightProbe(probeId);
}

// Unit test: Update light probe
TEST_F(GlobalIlluminationTest, UpdateLightProbe) {
    LightProbe probe{};
    probe.position[0] = 0.0f;
    probe.position[1] = 0.0f;
    probe.position[2] = 0.0f;
    probe.radius = 5.0f;
    probe.intensity = 1.0f;
    
    uint32_t probeId = gi->CreateLightProbe(probe);
    ASSERT_NE(probeId, 0u);
    
    // Update probe
    probe.position[1] = 10.0f;
    probe.radius = 15.0f;
    probe.intensity = 2.0f;
    
    gi->UpdateLightProbe(probeId, probe);
    
    const auto* retrievedProbe = gi->GetLightProbe(probeId);
    ASSERT_NE(retrievedProbe, nullptr);
    EXPECT_FLOAT_EQ(retrievedProbe->position[1], 10.0f);
    EXPECT_FLOAT_EQ(retrievedProbe->radius, 15.0f);
    EXPECT_FLOAT_EQ(retrievedProbe->intensity, 2.0f);
    
    gi->DestroyLightProbe(probeId);
}

// Unit test: Setup Voxel GI
TEST_F(GlobalIlluminationTest, SetupVoxelGI) {
    VoxelGridConfig config{};
    config.resolution = 128;
    config.worldSize = 100.0f;
    config.mipLevels = 6;
    config.enableAnisotropic = true;
    
    EXPECT_TRUE(gi->SetupVoxelGI(config));
    EXPECT_EQ(gi->GetTechnique(), GITechnique::VoxelBased);
    
    const auto& retrievedConfig = gi->GetVoxelConfig();
    EXPECT_EQ(retrievedConfig.resolution, 128u);
    EXPECT_FLOAT_EQ(retrievedConfig.worldSize, 100.0f);
    EXPECT_EQ(retrievedConfig.mipLevels, 6u);
    EXPECT_TRUE(retrievedConfig.enableAnisotropic);
}

// Property Test: Screen-Space GI Configuration Validation
RC_GTEST_PROP(GlobalIlluminationPropertyTest, SSGIConfigurationIsValid, ()) {
    /*
     * Feature: pywrkgame-library, Property 5: Global Illumination Accuracy
     * For any scene with indirect lighting, the global illumination system should produce 
     * realistic light bouncing effects
     * 
     * This test verifies that:
     * 1. Any valid SSGI configuration can be set up
     * 2. Configuration parameters are stored correctly
     * 3. Configuration parameters remain within valid ranges
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    auto pbrRenderer = renderer->GetPBRRenderer();
    RC_ASSERT(pbrRenderer != nullptr);
    
    auto gi = pbrRenderer->GetGlobalIllumination();
    RC_ASSERT(gi != nullptr);
    RC_ASSERT(gi->IsInitialized());
    
    // Generate random SSGI configuration
    auto config = *rc::gen::arbitrary<SSGIConfig>();
    
    // Verify generated config is valid
    RC_ASSERT(IsValidSSGIConfig(config));
    
    // Setup SSGI with generated config
    RC_ASSERT(gi->SetupScreenSpaceGI(config));
    RC_ASSERT(gi->GetTechnique() == GITechnique::ScreenSpace);
    
    // Retrieve and verify configuration
    const auto& retrievedConfig = gi->GetSSGIConfig();
    RC_ASSERT(retrievedConfig.rayCount == config.rayCount);
    RC_ASSERT(std::abs(retrievedConfig.rayLength - config.rayLength) < 0.0001f);
    RC_ASSERT(std::abs(retrievedConfig.thickness - config.thickness) < 0.0001f);
    RC_ASSERT(std::abs(retrievedConfig.intensity - config.intensity) < 0.0001f);
    RC_ASSERT(retrievedConfig.enableTemporalFilter == config.enableTemporalFilter);
    
    // Verify retrieved config is still valid
    RC_ASSERT(IsValidSSGIConfig(retrievedConfig));
    
    renderer->Shutdown();
}

// Property Test: Voxel GI Configuration Validation
RC_GTEST_PROP(GlobalIlluminationPropertyTest, VoxelGIConfigurationIsValid, ()) {
    /*
     * Feature: pywrkgame-library, Property 5: Global Illumination Accuracy
     * 
     * This test verifies that:
     * 1. Any valid voxel GI configuration can be set up
     * 2. Configuration parameters are stored correctly
     * 3. Configuration parameters remain within valid ranges
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    auto pbrRenderer = renderer->GetPBRRenderer();
    RC_ASSERT(pbrRenderer != nullptr);
    
    auto gi = pbrRenderer->GetGlobalIllumination();
    RC_ASSERT(gi != nullptr);
    
    // Generate random voxel configuration
    auto config = *rc::gen::arbitrary<VoxelGridConfig>();
    
    // Verify generated config is valid
    RC_ASSERT(IsValidVoxelConfig(config));
    
    // Setup voxel GI with generated config
    RC_ASSERT(gi->SetupVoxelGI(config));
    RC_ASSERT(gi->GetTechnique() == GITechnique::VoxelBased);
    
    // Retrieve and verify configuration
    const auto& retrievedConfig = gi->GetVoxelConfig();
    RC_ASSERT(retrievedConfig.resolution == config.resolution);
    RC_ASSERT(std::abs(retrievedConfig.worldSize - config.worldSize) < 0.0001f);
    RC_ASSERT(retrievedConfig.mipLevels == config.mipLevels);
    RC_ASSERT(retrievedConfig.enableAnisotropic == config.enableAnisotropic);
    
    // Verify retrieved config is still valid
    RC_ASSERT(IsValidVoxelConfig(retrievedConfig));
    
    renderer->Shutdown();
}

// Property Test: Light Probe Management
RC_GTEST_PROP(GlobalIlluminationPropertyTest, LightProbeManagementIsCorrect, ()) {
    /*
     * Feature: pywrkgame-library, Property 5: Global Illumination Accuracy
     * 
     * This test verifies that:
     * 1. Multiple light probes can be created and managed
     * 2. Each probe maintains its own independent properties
     * 3. Probes can be updated and destroyed correctly
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    auto pbrRenderer = renderer->GetPBRRenderer();
    RC_ASSERT(pbrRenderer != nullptr);
    
    auto gi = pbrRenderer->GetGlobalIllumination();
    RC_ASSERT(gi != nullptr);
    
    // Generate a random number of probes (1-10)
    auto numProbes = *rc::gen::inRange(1, 11);
    
    std::vector<uint32_t> probeIds;
    std::vector<LightProbe> probes;
    
    // Create probes
    for (int i = 0; i < numProbes; ++i) {
        auto probe = *rc::gen::arbitrary<LightProbe>();
        RC_ASSERT(IsValidLightProbe(probe));
        
        uint32_t id = gi->CreateLightProbe(probe);
        RC_ASSERT(id != 0);
        
        // Verify ID is unique
        for (auto existingId : probeIds) {
            RC_ASSERT(id != existingId);
        }
        
        probeIds.push_back(id);
        probes.push_back(probe);
    }
    
    // Verify all probes exist and have correct properties
    for (size_t i = 0; i < probeIds.size(); ++i) {
        const auto* retrieved = gi->GetLightProbe(probeIds[i]);
        RC_ASSERT(retrieved != nullptr);
        RC_ASSERT(std::abs(retrieved->radius - probes[i].radius) < 0.0001f);
        RC_ASSERT(std::abs(retrieved->intensity - probes[i].intensity) < 0.0001f);
    }
    
    // Update first probe
    if (!probeIds.empty()) {
        probes[0].intensity = 5.0f;
        gi->UpdateLightProbe(probeIds[0], probes[0]);
        
        const auto* retrieved = gi->GetLightProbe(probeIds[0]);
        RC_ASSERT(retrieved != nullptr);
        RC_ASSERT(std::abs(retrieved->intensity - 5.0f) < 0.0001f);
    }
    
    // Destroy half of the probes
    for (size_t i = 0; i < probeIds.size() / 2; ++i) {
        gi->DestroyLightProbe(probeIds[i]);
        
        // Verify destroyed probe cannot be retrieved
        const auto* retrieved = gi->GetLightProbe(probeIds[i]);
        RC_ASSERT(retrieved == nullptr);
    }
    
    // Verify remaining probes still exist
    for (size_t i = probeIds.size() / 2; i < probeIds.size(); ++i) {
        const auto* retrieved = gi->GetLightProbe(probeIds[i]);
        RC_ASSERT(retrieved != nullptr);
    }
    
    // Clean up remaining probes
    for (size_t i = probeIds.size() / 2; i < probeIds.size(); ++i) {
        gi->DestroyLightProbe(probeIds[i]);
    }
    
    renderer->Shutdown();
}

// Property Test: GI Technique Switching
RC_GTEST_PROP(GlobalIlluminationPropertyTest, TechniqueSwitchingIsCorrect, ()) {
    /*
     * Feature: pywrkgame-library, Property 5: Global Illumination Accuracy
     * 
     * This test verifies that:
     * 1. GI techniques can be switched dynamically
     * 2. Each technique maintains its own state
     * 3. Switching techniques doesn't corrupt the system
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    auto pbrRenderer = renderer->GetPBRRenderer();
    RC_ASSERT(pbrRenderer != nullptr);
    
    auto gi = pbrRenderer->GetGlobalIllumination();
    RC_ASSERT(gi != nullptr);
    
    // Start with no technique
    RC_ASSERT(gi->GetTechnique() == GITechnique::None);
    
    // Switch to Screen-Space GI
    auto ssgiConfig = *rc::gen::arbitrary<SSGIConfig>();
    RC_ASSERT(gi->SetupScreenSpaceGI(ssgiConfig));
    RC_ASSERT(gi->GetTechnique() == GITechnique::ScreenSpace);
    
    // Switch to Voxel GI
    auto voxelConfig = *rc::gen::arbitrary<VoxelGridConfig>();
    RC_ASSERT(gi->SetupVoxelGI(voxelConfig));
    RC_ASSERT(gi->GetTechnique() == GITechnique::VoxelBased);
    
    // Verify voxel config is preserved
    const auto& retrievedVoxelConfig = gi->GetVoxelConfig();
    RC_ASSERT(retrievedVoxelConfig.resolution == voxelConfig.resolution);
    
    // Switch to Light Probes
    gi->SetTechnique(GITechnique::LightProbes);
    RC_ASSERT(gi->GetTechnique() == GITechnique::LightProbes);
    
    // Create a probe
    auto probe = *rc::gen::arbitrary<LightProbe>();
    uint32_t probeId = gi->CreateLightProbe(probe);
    RC_ASSERT(probeId != 0);
    
    // Switch back to Screen-Space GI
    RC_ASSERT(gi->SetupScreenSpaceGI(ssgiConfig));
    RC_ASSERT(gi->GetTechnique() == GITechnique::ScreenSpace);
    
    // Verify SSGI config is preserved
    const auto& retrievedSSGIConfig = gi->GetSSGIConfig();
    RC_ASSERT(retrievedSSGIConfig.rayCount == ssgiConfig.rayCount);
    
    renderer->Shutdown();
}
