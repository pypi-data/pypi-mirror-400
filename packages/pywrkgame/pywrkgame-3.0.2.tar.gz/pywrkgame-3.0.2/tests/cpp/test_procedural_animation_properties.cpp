#include <gtest/gtest.h>
#include "pywrkgame/animation/AnimationSystem.h"
#include "pywrkgame/animation/ProceduralAnimation.h"
#include <random>
#include <vector>
#include <cmath>

using namespace pywrkgame;

// Property-based test helper class
class ProceduralAnimationPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        animSystem = std::make_unique<AnimationSystem>();
        procAnimSystem = std::make_unique<ProceduralAnimationSystem>();
        ASSERT_TRUE(animSystem->Initialize());
        ASSERT_TRUE(procAnimSystem->Initialize());
        rng.seed(42); // Fixed seed for reproducibility
    }
    
    void TearDown() override {
        procAnimSystem->Shutdown();
        animSystem->Shutdown();
    }
    
    // Generate random float within range
    float RandomFloat(float min = -10.0f, float max = 10.0f) {
        std::uniform_real_distribution<float> dist(min, max);
        return dist(rng);
    }
    
    // Generate random vec3 within range
    glm::vec3 RandomVec3(float min = -10.0f, float max = 10.0f) {
        return glm::vec3(RandomFloat(min, max), RandomFloat(min, max), RandomFloat(min, max));
    }
    
    int RandomInt(int min, int max) {
        std::uniform_int_distribution<int> dist(min, max);
        return dist(rng);
    }
    
    // Create a simple skeleton
    std::shared_ptr<Skeleton> CreateSimpleSkeleton(int numBones) {
        auto skeleton = animSystem->CreateSkeleton();
        
        for (int i = 0; i < numBones; ++i) {
            Bone bone;
            bone.name = "Bone_" + std::to_string(i);
            bone.parentIndex = (i == 0) ? -1 : i - 1;
            bone.offsetMatrix = glm::mat4(1.0f);
            bone.localTransform = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 1.0f, 0.0f));
            skeleton->AddBone(bone);
        }
        
        skeleton->UpdateGlobalTransforms();
        return skeleton;
    }
    
    std::unique_ptr<AnimationSystem> animSystem;
    std::unique_ptr<ProceduralAnimationSystem> procAnimSystem;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 31: Procedural Animation Generation
 * For any procedural animation parameters, generated animations should be smooth and realistic
 * Validates: Requirements 6.5
 */
TEST_F(ProceduralAnimationPropertyTest, Property31_ProceduralAnimationGeneration) {
    const int NUM_ITERATIONS = 100;
    int smoothAnimations = 0;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create skeleton and generator
        int numBones = RandomInt(2, 6);
        auto skeleton = CreateSimpleSkeleton(numBones);
        auto generator = procAnimSystem->CreateGenerator();
        
        // Add random modifiers to bones
        int targetBone = RandomInt(0, numBones - 1);
        
        // Create noise modifier
        auto noiseModifier = procAnimSystem->CreateNoiseModifier(NoiseType::Perlin);
        noiseModifier->SetFrequency(RandomFloat(0.5f, 2.0f));
        noiseModifier->SetAmplitude(RandomFloat(0.1f, 1.0f));
        noiseModifier->SetAffectPosition(true);
        
        generator->AddModifier(targetBone, noiseModifier);
        
        // Sample animation over time
        std::vector<glm::vec3> positions;
        const int numSamples = 20;
        const float timeStep = 0.05f;
        
        for (int sample = 0; sample < numSamples; ++sample) {
            float time = sample * timeStep;
            generator->Apply(*skeleton, time, timeStep);
            
            const Bone& bone = skeleton->GetBone(targetBone);
            glm::vec3 position = glm::vec3(bone.globalTransform[3]);
            positions.push_back(position);
        }
        
        // Check smoothness: consecutive positions should not have huge jumps
        bool isSmooth = true;
        for (size_t i = 1; i < positions.size(); ++i) {
            float distance = glm::length(positions[i] - positions[i-1]);
            
            // Maximum expected change per sample (based on amplitude and time step)
            float maxExpectedChange = 5.0f;
            
            if (distance > maxExpectedChange) {
                isSmooth = false;
                break;
            }
        }
        
        if (isSmooth) {
            smoothAnimations++;
        }
    }
    
    // Property: Procedural animations should be smooth
    float smoothnessRate = static_cast<float>(smoothAnimations) / NUM_ITERATIONS;
    EXPECT_GT(smoothnessRate, 0.9f)
        << "Procedural animation smoothness rate too low: " << smoothnessRate
        << " (" << smoothAnimations << "/" << NUM_ITERATIONS << ")";
}

/*
 * Additional property test: Noise modifier determinism
 * For any noise parameters with fixed seed, output should be deterministic
 */
TEST_F(ProceduralAnimationPropertyTest, NoiseModifierDeterminism) {
    const int NUM_ITERATIONS = 50;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create two identical setups
        auto skeleton1 = CreateSimpleSkeleton(3);
        auto skeleton2 = CreateSimpleSkeleton(3);
        
        auto generator1 = procAnimSystem->CreateGenerator();
        auto generator2 = procAnimSystem->CreateGenerator();
        
        // Create identical noise modifiers
        auto noiseModifier1 = procAnimSystem->CreateNoiseModifier(NoiseType::Perlin);
        auto noiseModifier2 = procAnimSystem->CreateNoiseModifier(NoiseType::Perlin);
        
        float frequency = RandomFloat(0.5f, 2.0f);
        float amplitude = RandomFloat(0.1f, 1.0f);
        
        noiseModifier1->SetFrequency(frequency);
        noiseModifier1->SetAmplitude(amplitude);
        noiseModifier2->SetFrequency(frequency);
        noiseModifier2->SetAmplitude(amplitude);
        
        generator1->AddModifier(0, noiseModifier1);
        generator2->AddModifier(0, noiseModifier2);
        
        // Apply at same time
        float time = RandomFloat(0.0f, 10.0f);
        generator1->Apply(*skeleton1, time, 0.016f);
        generator2->Apply(*skeleton2, time, 0.016f);
        
        // Verify results are identical
        const Bone& bone1 = skeleton1->GetBone(0);
        const Bone& bone2 = skeleton2->GetBone(0);
        
        glm::vec3 pos1 = glm::vec3(bone1.globalTransform[3]);
        glm::vec3 pos2 = glm::vec3(bone2.globalTransform[3]);
        
        float distance = glm::length(pos1 - pos2);
        
        EXPECT_LT(distance, 0.001f)
            << "Noise modifier not deterministic at iteration " << iter;
    }
}

/*
 * Additional property test: Wave modifier periodicity
 * For any wave parameters, output should be periodic
 */
TEST_F(ProceduralAnimationPropertyTest, WaveModifierPeriodicity) {
    const int NUM_ITERATIONS = 50;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        auto skeleton = CreateSimpleSkeleton(2);
        auto generator = procAnimSystem->CreateGenerator();
        
        // Create wave modifier
        auto waveModifier = procAnimSystem->CreateWaveModifier();
        WaveParameters params;
        params.frequency = RandomFloat(0.5f, 2.0f);
        params.amplitude = RandomFloat(0.5f, 2.0f);
        params.phase = 0.0f;
        params.direction = glm::vec3(0.0f, 1.0f, 0.0f);
        
        waveModifier->SetWaveParameters(params);
        waveModifier->SetAffectPosition(true);
        
        generator->AddModifier(0, waveModifier);
        
        // Sample at time t and t + period
        float period = (2.0f * glm::pi<float>()) / params.frequency;
        float time1 = RandomFloat(0.0f, 5.0f);
        float time2 = time1 + period;
        
        // Apply at time1
        auto skeleton1 = CreateSimpleSkeleton(2);
        auto generator1 = procAnimSystem->CreateGenerator();
        auto waveModifier1 = procAnimSystem->CreateWaveModifier();
        waveModifier1->SetWaveParameters(params);
        waveModifier1->SetAffectPosition(true);
        generator1->AddModifier(0, waveModifier1);
        generator1->Apply(*skeleton1, time1, 0.016f);
        
        // Apply at time2
        auto skeleton2 = CreateSimpleSkeleton(2);
        auto generator2 = procAnimSystem->CreateGenerator();
        auto waveModifier2 = procAnimSystem->CreateWaveModifier();
        waveModifier2->SetWaveParameters(params);
        waveModifier2->SetAffectPosition(true);
        generator2->AddModifier(0, waveModifier2);
        generator2->Apply(*skeleton2, time2, 0.016f);
        
        // Verify positions are similar (periodic)
        const Bone& bone1 = skeleton1->GetBone(0);
        const Bone& bone2 = skeleton2->GetBone(0);
        
        glm::vec3 pos1 = glm::vec3(bone1.globalTransform[3]);
        glm::vec3 pos2 = glm::vec3(bone2.globalTransform[3]);
        
        float distance = glm::length(pos1 - pos2);
        
        EXPECT_LT(distance, 0.1f)
            << "Wave modifier not periodic at iteration " << iter
            << ", distance: " << distance;
    }
}

/*
 * Additional property test: Spring modifier stability
 * For any spring parameters, system should eventually stabilize
 */
TEST_F(ProceduralAnimationPropertyTest, SpringModifierStability) {
    const int NUM_ITERATIONS = 50;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        auto skeleton = CreateSimpleSkeleton(2);
        auto generator = procAnimSystem->CreateGenerator();
        
        // Create spring modifier
        auto springModifier = procAnimSystem->CreateSpringModifier();
        SpringParameters params;
        params.stiffness = RandomFloat(50.0f, 200.0f);
        params.damping = RandomFloat(5.0f, 20.0f);
        params.mass = 1.0f;
        params.restPosition = glm::vec3(0.0f);
        params.velocity = glm::vec3(0.0f);
        
        springModifier->SetSpringParameters(params);
        springModifier->SetTarget(RandomVec3(-2.0f, 2.0f));
        
        generator->AddModifier(0, springModifier);
        
        // Simulate for a while
        float time = 0.0f;
        float deltaTime = 0.016f;
        std::vector<glm::vec3> positions;
        
        for (int step = 0; step < 200; ++step) {
            generator->Apply(*skeleton, time, deltaTime);
            time += deltaTime;
            
            const Bone& bone = skeleton->GetBone(0);
            glm::vec3 position = glm::vec3(bone.globalTransform[3]);
            positions.push_back(position);
        }
        
        // Check if system stabilized (last few positions should be similar)
        if (positions.size() >= 10) {
            float maxVariation = 0.0f;
            for (size_t i = positions.size() - 10; i < positions.size() - 1; ++i) {
                float distance = glm::length(positions[i + 1] - positions[i]);
                maxVariation = std::max(maxVariation, distance);
            }
            
            // System should have stabilized (very small movement)
            EXPECT_LT(maxVariation, 0.5f)
                << "Spring system did not stabilize at iteration " << iter
                << ", max variation: " << maxVariation;
        }
    }
}

/*
 * Additional property test: Animation blending linearity
 * For any two bone transforms, blending should be linear
 */
TEST_F(ProceduralAnimationPropertyTest, AnimationBlendingLinearity) {
    const int NUM_ITERATIONS = 100;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create two random bones
        Bone bone1, bone2, result;
        
        bone1.localTransform = glm::translate(glm::mat4(1.0f), RandomVec3(-5.0f, 5.0f));
        bone2.localTransform = glm::translate(glm::mat4(1.0f), RandomVec3(-5.0f, 5.0f));
        
        // Test blending at different weights
        std::vector<float> weights = {0.0f, 0.25f, 0.5f, 0.75f, 1.0f};
        std::vector<glm::vec3> blendedPositions;
        
        for (float weight : weights) {
            AnimationBlender::BlendBones(bone1, bone2, weight, result);
            glm::vec3 position = glm::vec3(result.localTransform[3]);
            blendedPositions.push_back(position);
        }
        
        // Verify linearity: position at weight 0.5 should be midpoint
        glm::vec3 pos1 = glm::vec3(bone1.localTransform[3]);
        glm::vec3 pos2 = glm::vec3(bone2.localTransform[3]);
        glm::vec3 expectedMidpoint = (pos1 + pos2) * 0.5f;
        glm::vec3 actualMidpoint = blendedPositions[2];  // weight 0.5
        
        float distance = glm::length(expectedMidpoint - actualMidpoint);
        
        EXPECT_LT(distance, 0.01f)
            << "Blending not linear at iteration " << iter;
        
        // Verify endpoints
        EXPECT_LT(glm::length(blendedPositions[0] - pos1), 0.01f)
            << "Blend at weight 0 should equal bone1";
        EXPECT_LT(glm::length(blendedPositions[4] - pos2), 0.01f)
            << "Blend at weight 1 should equal bone2";
    }
}

/*
 * Additional property test: Modifier strength scaling
 * For any modifier, effect should scale linearly with strength
 */
TEST_F(ProceduralAnimationPropertyTest, ModifierStrengthScaling) {
    const int NUM_ITERATIONS = 50;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Test with noise modifier
        auto noiseModifier = procAnimSystem->CreateNoiseModifier(NoiseType::Perlin);
        noiseModifier->SetFrequency(1.0f);
        noiseModifier->SetAmplitude(1.0f);
        noiseModifier->SetAffectPosition(true);
        
        float time = RandomFloat(0.0f, 10.0f);
        
        // Apply with different strengths
        std::vector<float> strengths = {0.0f, 0.5f, 1.0f};
        std::vector<glm::vec3> positions;
        
        for (float strength : strengths) {
            auto skeleton = CreateSimpleSkeleton(2);
            auto generator = procAnimSystem->CreateGenerator();
            
            auto modifier = procAnimSystem->CreateNoiseModifier(NoiseType::Perlin);
            modifier->SetFrequency(1.0f);
            modifier->SetAmplitude(1.0f);
            modifier->SetAffectPosition(true);
            modifier->SetStrength(strength);
            
            generator->AddModifier(0, modifier);
            generator->Apply(*skeleton, time, 0.016f);
            
            const Bone& bone = skeleton->GetBone(0);
            glm::vec3 position = glm::vec3(bone.globalTransform[3]);
            positions.push_back(position);
        }
        
        // Verify strength 0 has no effect
        glm::vec3 originalPos(0.0f, 1.0f, 0.0f);  // Initial bone position
        float distanceAtZero = glm::length(positions[0] - originalPos);
        EXPECT_LT(distanceAtZero, 0.01f)
            << "Strength 0 should have no effect at iteration " << iter;
        
        // Verify effect scales with strength
        float effectAt50 = glm::length(positions[1] - originalPos);
        float effectAt100 = glm::length(positions[2] - originalPos);
        
        // Effect at 100% should be roughly twice effect at 50%
        if (effectAt50 > 0.01f && effectAt100 > 0.01f) {
            float ratio = effectAt100 / effectAt50;
            EXPECT_GT(ratio, 1.5f)
                << "Effect should scale with strength at iteration " << iter;
            EXPECT_LT(ratio, 2.5f)
                << "Effect scaling should be roughly linear at iteration " << iter;
        }
    }
}

/*
 * Additional property test: Multiple modifier composition
 * For any combination of modifiers, application order should not cause instability
 */
TEST_F(ProceduralAnimationPropertyTest, MultipleModifierComposition) {
    const int NUM_ITERATIONS = 50;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        auto skeleton = CreateSimpleSkeleton(3);
        auto generator = procAnimSystem->CreateGenerator();
        
        // Add multiple modifiers to same bone
        int targetBone = 1;
        
        auto noiseModifier = procAnimSystem->CreateNoiseModifier(NoiseType::Perlin);
        noiseModifier->SetFrequency(1.0f);
        noiseModifier->SetAmplitude(0.5f);
        noiseModifier->SetAffectPosition(true);
        
        auto waveModifier = procAnimSystem->CreateWaveModifier();
        WaveParameters waveParams;
        waveParams.frequency = 2.0f;
        waveParams.amplitude = 0.3f;
        waveModifier->SetWaveParameters(waveParams);
        waveModifier->SetAffectPosition(true);
        
        generator->AddModifier(targetBone, noiseModifier);
        generator->AddModifier(targetBone, waveModifier);
        
        // Apply over time
        float time = 0.0f;
        bool stable = true;
        
        for (int step = 0; step < 50; ++step) {
            generator->Apply(*skeleton, time, 0.016f);
            time += 0.016f;
            
            const Bone& bone = skeleton->GetBone(targetBone);
            glm::vec3 position = glm::vec3(bone.globalTransform[3]);
            
            // Check for NaN or infinite values
            if (std::isnan(position.x) || std::isnan(position.y) || std::isnan(position.z) ||
                std::isinf(position.x) || std::isinf(position.y) || std::isinf(position.z)) {
                stable = false;
                break;
            }
            
            // Check for unreasonable values
            if (glm::length(position) > 1000.0f) {
                stable = false;
                break;
            }
        }
        
        EXPECT_TRUE(stable)
            << "Multiple modifiers caused instability at iteration " << iter;
    }
}

/*
 * Additional property test: Noise type consistency
 * For any noise type, output should be within expected range
 */
TEST_F(ProceduralAnimationPropertyTest, NoiseTypeConsistency) {
    const int NUM_ITERATIONS = 100;
    
    std::vector<NoiseType> noiseTypes = {
        NoiseType::Perlin,
        NoiseType::Simplex,
        NoiseType::Worley,
        NoiseType::White
    };
    
    for (NoiseType noiseType : noiseTypes) {
        for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
            NoiseGenerator noiseGen(noiseType);
            
            float x = RandomFloat(-100.0f, 100.0f);
            float y = RandomFloat(-100.0f, 100.0f);
            float z = RandomFloat(-100.0f, 100.0f);
            
            float noise = noiseGen.Generate3D(x, y, z, 1.0f, 1.0f);
            
            // Noise should be in reasonable range (typically [0, 1] or [-1, 1])
            EXPECT_FALSE(std::isnan(noise))
                << "Noise generated NaN for type " << static_cast<int>(noiseType);
            EXPECT_FALSE(std::isinf(noise))
                << "Noise generated infinity for type " << static_cast<int>(noiseType);
            EXPECT_GE(noise, -2.0f)
                << "Noise value too low for type " << static_cast<int>(noiseType);
            EXPECT_LE(noise, 2.0f)
                << "Noise value too high for type " << static_cast<int>(noiseType);
        }
    }
}
