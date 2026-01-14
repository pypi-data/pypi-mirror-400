/**
 * Property-Based Tests for PBR Rendering System
 * Feature: pywrkgame-library, Property 4: PBR Material Rendering
 * Validates: Requirements 3.1
 * 
 * Property 4: PBR Material Rendering
 * For any 3D object with PBR materials, the Rendering_Engine should produce 
 * physically accurate lighting and shading
 */

#include <gtest/gtest.h>
#include <rapidcheck/gtest.h>
#include "pywrkgame/rendering/RenderingEngine.h"
#include "pywrkgame/rendering/PBRRenderer.h"
#include <cmath>
#include <algorithm>

using namespace pywrkgame::rendering;

// Helper function to validate PBR material properties are within valid ranges
bool IsValidPBRMaterial(const PBRMaterialProperties& props) {
    // Albedo should be in [0, 1] range for each component
    for (int i = 0; i < 3; ++i) {
        if (props.albedo[i] < 0.0f || props.albedo[i] > 1.0f) {
            return false;
        }
    }
    
    // Metallic should be in [0, 1] range
    if (props.metallic < 0.0f || props.metallic > 1.0f) {
        return false;
    }
    
    // Roughness should be in [0, 1] range
    if (props.roughness < 0.0f || props.roughness > 1.0f) {
        return false;
    }
    
    // AO should be in [0, 1] range
    if (props.ao < 0.0f || props.ao > 1.0f) {
        return false;
    }
    
    // Emissive should be non-negative
    for (int i = 0; i < 3; ++i) {
        if (props.emissive[i] < 0.0f) {
            return false;
        }
    }
    
    // Emissive strength should be non-negative
    if (props.emissiveStrength < 0.0f) {
        return false;
    }
    
    return true;
}

// Generator for valid PBR material properties
namespace rc {
    template<>
    struct Arbitrary<PBRMaterialProperties> {
        static Gen<PBRMaterialProperties> arbitrary() {
            return gen::build<PBRMaterialProperties>(
                gen::set(&PBRMaterialProperties::albedo,
                    gen::construct<std::array<float, 3>>(
                        gen::inRange(0.0f, 1.0f),
                        gen::inRange(0.0f, 1.0f),
                        gen::inRange(0.0f, 1.0f)
                    ).as([](const std::array<float, 3>& arr) {
                        float result[3];
                        std::copy(arr.begin(), arr.end(), result);
                        return result;
                    })
                ),
                gen::set(&PBRMaterialProperties::metallic, gen::inRange(0.0f, 1.0f)),
                gen::set(&PBRMaterialProperties::roughness, gen::inRange(0.0f, 1.0f)),
                gen::set(&PBRMaterialProperties::ao, gen::inRange(0.0f, 1.0f)),
                gen::set(&PBRMaterialProperties::emissive,
                    gen::construct<std::array<float, 3>>(
                        gen::inRange(0.0f, 10.0f),
                        gen::inRange(0.0f, 10.0f),
                        gen::inRange(0.0f, 10.0f)
                    ).as([](const std::array<float, 3>& arr) {
                        float result[3];
                        std::copy(arr.begin(), arr.end(), result);
                        return result;
                    })
                ),
                gen::set(&PBRMaterialProperties::emissiveStrength, gen::inRange(0.0f, 10.0f))
            );
        }
    };
}

class PBRRenderingTest : public ::testing::Test {
protected:
    void SetUp() override {
        renderer = std::make_unique<RenderingEngine>();
        ASSERT_TRUE(renderer->Initialize());
        pbrRenderer = renderer->GetPBRRenderer();
        ASSERT_NE(pbrRenderer, nullptr);
    }
    
    void TearDown() override {
        renderer->Shutdown();
    }
    
    std::unique_ptr<RenderingEngine> renderer;
    PBRRenderer* pbrRenderer = nullptr;
};

// Unit test: Basic PBR renderer initialization
TEST_F(PBRRenderingTest, PBRRendererInitialized) {
    EXPECT_TRUE(pbrRenderer->IsInitialized());
}

// Unit test: Create PBR material with default properties
TEST_F(PBRRenderingTest, CreateDefaultPBRMaterial) {
    PBRMaterialProperties props{};
    props.albedo[0] = 1.0f;
    props.albedo[1] = 1.0f;
    props.albedo[2] = 1.0f;
    props.metallic = 0.0f;
    props.roughness = 0.5f;
    props.ao = 1.0f;
    
    uint32_t materialId = pbrRenderer->CreatePBRMaterial(props);
    EXPECT_NE(materialId, 0u);
    
    const auto* retrievedProps = pbrRenderer->GetPBRMaterial(materialId);
    ASSERT_NE(retrievedProps, nullptr);
    
    EXPECT_FLOAT_EQ(retrievedProps->albedo[0], 1.0f);
    EXPECT_FLOAT_EQ(retrievedProps->albedo[1], 1.0f);
    EXPECT_FLOAT_EQ(retrievedProps->albedo[2], 1.0f);
    EXPECT_FLOAT_EQ(retrievedProps->metallic, 0.0f);
    EXPECT_FLOAT_EQ(retrievedProps->roughness, 0.5f);
    EXPECT_FLOAT_EQ(retrievedProps->ao, 1.0f);
    
    pbrRenderer->DestroyPBRMaterial(materialId);
}

// Unit test: Update PBR material properties
TEST_F(PBRRenderingTest, UpdatePBRMaterial) {
    PBRMaterialProperties props{};
    props.albedo[0] = 1.0f;
    props.albedo[1] = 0.0f;
    props.albedo[2] = 0.0f;
    props.metallic = 0.0f;
    props.roughness = 0.5f;
    
    uint32_t materialId = pbrRenderer->CreatePBRMaterial(props);
    ASSERT_NE(materialId, 0u);
    
    // Update properties
    props.albedo[0] = 0.0f;
    props.albedo[1] = 1.0f;
    props.albedo[2] = 0.0f;
    props.metallic = 1.0f;
    props.roughness = 0.1f;
    
    pbrRenderer->UpdatePBRMaterial(materialId, props);
    
    const auto* retrievedProps = pbrRenderer->GetPBRMaterial(materialId);
    ASSERT_NE(retrievedProps, nullptr);
    
    EXPECT_FLOAT_EQ(retrievedProps->albedo[0], 0.0f);
    EXPECT_FLOAT_EQ(retrievedProps->albedo[1], 1.0f);
    EXPECT_FLOAT_EQ(retrievedProps->albedo[2], 0.0f);
    EXPECT_FLOAT_EQ(retrievedProps->metallic, 1.0f);
    EXPECT_FLOAT_EQ(retrievedProps->roughness, 0.1f);
    
    pbrRenderer->DestroyPBRMaterial(materialId);
}

// Unit test: Destroy PBR material
TEST_F(PBRRenderingTest, DestroyPBRMaterial) {
    PBRMaterialProperties props{};
    uint32_t materialId = pbrRenderer->CreatePBRMaterial(props);
    ASSERT_NE(materialId, 0u);
    
    pbrRenderer->DestroyPBRMaterial(materialId);
    
    // After destruction, material should not be retrievable
    const auto* retrievedProps = pbrRenderer->GetPBRMaterial(materialId);
    EXPECT_EQ(retrievedProps, nullptr);
}

// Unit test: PBR shaders are compiled
TEST_F(PBRRenderingTest, PBRShadersCompiled) {
    auto vertexShader = pbrRenderer->GetPBRVertexShader();
    auto fragmentShader = pbrRenderer->GetPBRFragmentShader();
    
    EXPECT_TRUE(vertexShader.IsValid());
    EXPECT_TRUE(fragmentShader.IsValid());
}

// Unit test: Setup environment lighting
TEST_F(PBRRenderingTest, SetupEnvironmentLighting) {
    // Create a dummy environment map texture
    TextureDesc envDesc{};
    envDesc.width = 512;
    envDesc.height = 512;
    envDesc.format = TextureFormat::RGBA16F;
    
    auto envMap = renderer->CreateTexture(envDesc);
    ASSERT_TRUE(envMap.IsValid());
    
    HDRIEnvironment hdri{};
    hdri.environmentMap = envMap;
    hdri.intensity = 1.0f;
    hdri.rotation = 0.0f;
    
    EXPECT_TRUE(pbrRenderer->SetupEnvironmentLighting(hdri));
    
    pbrRenderer->EnableEnvironmentLighting(true);
    EXPECT_TRUE(pbrRenderer->IsEnvironmentLightingEnabled());
    
    pbrRenderer->EnableEnvironmentLighting(false);
    EXPECT_FALSE(pbrRenderer->IsEnvironmentLightingEnabled());
    
    renderer->DestroyTexture(envMap);
}

// Property Test: PBR Material Properties Validation
RC_GTEST_PROP(PBRRenderingPropertyTest, MaterialPropertiesAreValid, ()) {
    /*
     * Feature: pywrkgame-library, Property 4: PBR Material Rendering
     * For any 3D object with PBR materials, the Rendering_Engine should produce 
     * physically accurate lighting and shading
     * 
     * This test verifies that:
     * 1. Any valid PBR material can be created
     * 2. Material properties are stored correctly
     * 3. Material properties remain within physically valid ranges
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    auto pbrRenderer = renderer->GetPBRRenderer();
    RC_ASSERT(pbrRenderer != nullptr);
    RC_ASSERT(pbrRenderer->IsInitialized());
    
    // Generate random PBR material properties
    auto props = *rc::gen::arbitrary<PBRMaterialProperties>();
    
    // Verify generated properties are valid
    RC_ASSERT(IsValidPBRMaterial(props));
    
    // Create material with generated properties
    uint32_t materialId = pbrRenderer->CreatePBRMaterial(props);
    RC_ASSERT(materialId != 0);
    
    // Retrieve and verify properties
    const auto* retrievedProps = pbrRenderer->GetPBRMaterial(materialId);
    RC_ASSERT(retrievedProps != nullptr);
    
    // Verify all properties match
    RC_ASSERT(std::abs(retrievedProps->albedo[0] - props.albedo[0]) < 0.0001f);
    RC_ASSERT(std::abs(retrievedProps->albedo[1] - props.albedo[1]) < 0.0001f);
    RC_ASSERT(std::abs(retrievedProps->albedo[2] - props.albedo[2]) < 0.0001f);
    RC_ASSERT(std::abs(retrievedProps->metallic - props.metallic) < 0.0001f);
    RC_ASSERT(std::abs(retrievedProps->roughness - props.roughness) < 0.0001f);
    RC_ASSERT(std::abs(retrievedProps->ao - props.ao) < 0.0001f);
    
    // Verify retrieved properties are still valid
    RC_ASSERT(IsValidPBRMaterial(*retrievedProps));
    
    // Clean up
    pbrRenderer->DestroyPBRMaterial(materialId);
    renderer->Shutdown();
}

// Property Test: Multiple PBR Materials
RC_GTEST_PROP(PBRRenderingPropertyTest, MultipleMaterialsAreIndependent, ()) {
    /*
     * Feature: pywrkgame-library, Property 4: PBR Material Rendering
     * 
     * This test verifies that:
     * 1. Multiple PBR materials can be created simultaneously
     * 2. Each material maintains its own independent properties
     * 3. Modifying one material doesn't affect others
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    auto pbrRenderer = renderer->GetPBRRenderer();
    RC_ASSERT(pbrRenderer != nullptr);
    
    // Generate two different materials
    auto props1 = *rc::gen::arbitrary<PBRMaterialProperties>();
    auto props2 = *rc::gen::arbitrary<PBRMaterialProperties>();
    
    // Create both materials
    uint32_t materialId1 = pbrRenderer->CreatePBRMaterial(props1);
    uint32_t materialId2 = pbrRenderer->CreatePBRMaterial(props2);
    
    RC_ASSERT(materialId1 != 0);
    RC_ASSERT(materialId2 != 0);
    RC_ASSERT(materialId1 != materialId2);
    
    // Verify both materials have correct properties
    const auto* retrieved1 = pbrRenderer->GetPBRMaterial(materialId1);
    const auto* retrieved2 = pbrRenderer->GetPBRMaterial(materialId2);
    
    RC_ASSERT(retrieved1 != nullptr);
    RC_ASSERT(retrieved2 != nullptr);
    
    // Verify material 1 properties
    RC_ASSERT(std::abs(retrieved1->metallic - props1.metallic) < 0.0001f);
    RC_ASSERT(std::abs(retrieved1->roughness - props1.roughness) < 0.0001f);
    
    // Verify material 2 properties
    RC_ASSERT(std::abs(retrieved2->metallic - props2.metallic) < 0.0001f);
    RC_ASSERT(std::abs(retrieved2->roughness - props2.roughness) < 0.0001f);
    
    // Update material 1
    props1.metallic = 0.9f;
    props1.roughness = 0.1f;
    pbrRenderer->UpdatePBRMaterial(materialId1, props1);
    
    // Verify material 1 changed
    retrieved1 = pbrRenderer->GetPBRMaterial(materialId1);
    RC_ASSERT(std::abs(retrieved1->metallic - 0.9f) < 0.0001f);
    RC_ASSERT(std::abs(retrieved1->roughness - 0.1f) < 0.0001f);
    
    // Verify material 2 unchanged
    retrieved2 = pbrRenderer->GetPBRMaterial(materialId2);
    RC_ASSERT(std::abs(retrieved2->metallic - props2.metallic) < 0.0001f);
    RC_ASSERT(std::abs(retrieved2->roughness - props2.roughness) < 0.0001f);
    
    // Clean up
    pbrRenderer->DestroyPBRMaterial(materialId1);
    pbrRenderer->DestroyPBRMaterial(materialId2);
    renderer->Shutdown();
}

// Property Test: PBR Material Lifecycle
RC_GTEST_PROP(PBRRenderingPropertyTest, MaterialLifecycleIsCorrect, ()) {
    /*
     * Feature: pywrkgame-library, Property 4: PBR Material Rendering
     * 
     * This test verifies that:
     * 1. Materials can be created and destroyed in any order
     * 2. Destroyed materials cannot be retrieved
     * 3. Material IDs are unique
     */
    
    auto renderer = std::make_unique<RenderingEngine>();
    RC_ASSERT(renderer->Initialize());
    
    auto pbrRenderer = renderer->GetPBRRenderer();
    RC_ASSERT(pbrRenderer != nullptr);
    
    // Generate a random number of materials (1-10)
    auto numMaterials = *rc::gen::inRange(1, 11);
    
    std::vector<uint32_t> materialIds;
    std::vector<PBRMaterialProperties> properties;
    
    // Create materials
    for (int i = 0; i < numMaterials; ++i) {
        auto props = *rc::gen::arbitrary<PBRMaterialProperties>();
        uint32_t id = pbrRenderer->CreatePBRMaterial(props);
        
        RC_ASSERT(id != 0);
        
        // Verify ID is unique
        for (auto existingId : materialIds) {
            RC_ASSERT(id != existingId);
        }
        
        materialIds.push_back(id);
        properties.push_back(props);
    }
    
    // Verify all materials exist and have correct properties
    for (size_t i = 0; i < materialIds.size(); ++i) {
        const auto* retrieved = pbrRenderer->GetPBRMaterial(materialIds[i]);
        RC_ASSERT(retrieved != nullptr);
        RC_ASSERT(std::abs(retrieved->metallic - properties[i].metallic) < 0.0001f);
    }
    
    // Destroy half of the materials
    for (size_t i = 0; i < materialIds.size() / 2; ++i) {
        pbrRenderer->DestroyPBRMaterial(materialIds[i]);
        
        // Verify destroyed material cannot be retrieved
        const auto* retrieved = pbrRenderer->GetPBRMaterial(materialIds[i]);
        RC_ASSERT(retrieved == nullptr);
    }
    
    // Verify remaining materials still exist
    for (size_t i = materialIds.size() / 2; i < materialIds.size(); ++i) {
        const auto* retrieved = pbrRenderer->GetPBRMaterial(materialIds[i]);
        RC_ASSERT(retrieved != nullptr);
    }
    
    // Clean up remaining materials
    for (size_t i = materialIds.size() / 2; i < materialIds.size(); ++i) {
        pbrRenderer->DestroyPBRMaterial(materialIds[i]);
    }
    
    renderer->Shutdown();
}
