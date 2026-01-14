#include <gtest/gtest.h>
#include "pywrkgame/animation/AnimationSystem.h"
#include <random>
#include <vector>
#include <cmath>

using namespace pywrkgame;

// Property-based test helper class
class SkeletalAnimationPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        animSystem = std::make_unique<AnimationSystem>();
        ASSERT_TRUE(animSystem->Initialize());
        rng.seed(42); // Fixed seed for reproducibility
    }
    
    void TearDown() override {
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
    
    // Generate random quaternion
    glm::quat RandomQuat() {
        // Generate random axis
        glm::vec3 axis = glm::normalize(RandomVec3(-1.0f, 1.0f));
        float angle = RandomFloat(0.0f, glm::two_pi<float>());
        return glm::angleAxis(angle, axis);
    }
    
    // Create a simple skeleton with random bones
    std::shared_ptr<Skeleton> CreateRandomSkeleton(int numBones) {
        auto skeleton = animSystem->CreateSkeleton();
        
        for (int i = 0; i < numBones; ++i) {
            Bone bone;
            bone.name = "Bone_" + std::to_string(i);
            bone.parentIndex = (i == 0) ? -1 : RandomInt(0, i - 1);
            bone.offsetMatrix = glm::mat4(1.0f);
            bone.localTransform = glm::translate(glm::mat4(1.0f), RandomVec3(-5.0f, 5.0f));
            skeleton->AddBone(bone);
        }
        
        return skeleton;
    }
    
    // Create animation clip with random keyframes
    std::shared_ptr<AnimationClip> CreateRandomAnimationClip(const std::string& name, int numChannels, int numKeyframes) {
        float duration = RandomFloat(1.0f, 5.0f);
        auto clip = animSystem->LoadAnimationClip(name, duration);
        
        for (int i = 0; i < numChannels; ++i) {
            AnimationChannel channel;
            channel.boneIndex = i;
            
            for (int k = 0; k < numKeyframes; ++k) {
                Keyframe keyframe;
                keyframe.time = (duration / (numKeyframes - 1)) * k;
                keyframe.position = RandomVec3(-5.0f, 5.0f);
                keyframe.rotation = RandomQuat();
                keyframe.scale = glm::vec3(RandomFloat(0.5f, 2.0f));
                channel.keyframes.push_back(keyframe);
            }
            
            clip->AddChannel(channel);
        }
        
        return clip;
    }
    
    int RandomInt(int min, int max) {
        std::uniform_int_distribution<int> dist(min, max);
        return dist(rng);
    }
    
    std::unique_ptr<AnimationSystem> animSystem;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 30: Skeletal Animation Constraints
 * For any skeletal animation with bone constraints, movements should respect constraint limits
 * Validates: Requirements 6.4
 */
TEST_F(SkeletalAnimationPropertyTest, Property30_SkeletalAnimationConstraints) {
    const int NUM_ITERATIONS = 100;
    int constraintViolations = 0;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create skeleton with random constraints
        auto skeleton = animSystem->CreateSkeleton();
        
        int numBones = RandomInt(3, 10);
        for (int i = 0; i < numBones; ++i) {
            Bone bone;
            bone.name = "Bone_" + std::to_string(i);
            bone.parentIndex = (i == 0) ? -1 : RandomInt(0, i - 1);
            bone.offsetMatrix = glm::mat4(1.0f);
            
            // Set random rotation constraints
            bone.hasRotationConstraint = true;
            bone.minRotation = glm::vec3(RandomFloat(-90.0f, -10.0f));
            bone.maxRotation = glm::vec3(RandomFloat(10.0f, 90.0f));
            
            // Set random position constraints
            bone.hasPositionConstraint = true;
            bone.minPosition = glm::vec3(RandomFloat(-10.0f, -1.0f));
            bone.maxPosition = glm::vec3(RandomFloat(1.0f, 10.0f));
            
            // Set initial transform that might violate constraints
            glm::vec3 position = RandomVec3(-20.0f, 20.0f);
            glm::quat rotation = RandomQuat();
            glm::vec3 scale(1.0f);
            
            bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                                 glm::mat4_cast(rotation) *
                                 glm::scale(glm::mat4(1.0f), scale);
            
            skeleton->AddBone(bone);
        }
        
        // Apply constraints
        skeleton->ApplyConstraints();
        
        // Verify all bones respect constraints
        for (int i = 0; i < numBones; ++i) {
            const Bone& bone = skeleton->GetBone(i);
            
            if (bone.hasRotationConstraint) {
                glm::quat rotation = glm::quat_cast(bone.localTransform);
                glm::vec3 euler = glm::eulerAngles(rotation);
                
                // Check rotation constraints (with small tolerance for floating point)
                const float tolerance = 0.01f;
                if (euler.x < glm::radians(bone.minRotation.x) - tolerance ||
                    euler.x > glm::radians(bone.maxRotation.x) + tolerance ||
                    euler.y < glm::radians(bone.minRotation.y) - tolerance ||
                    euler.y > glm::radians(bone.maxRotation.y) + tolerance ||
                    euler.z < glm::radians(bone.minRotation.z) - tolerance ||
                    euler.z > glm::radians(bone.maxRotation.z) + tolerance) {
                    constraintViolations++;
                }
            }
            
            if (bone.hasPositionConstraint) {
                glm::vec3 position = glm::vec3(bone.localTransform[3]);
                
                // Check position constraints (with small tolerance)
                const float tolerance = 0.01f;
                if (position.x < bone.minPosition.x - tolerance ||
                    position.x > bone.maxPosition.x + tolerance ||
                    position.y < bone.minPosition.y - tolerance ||
                    position.y > bone.maxPosition.y + tolerance ||
                    position.z < bone.minPosition.z - tolerance ||
                    position.z > bone.maxPosition.z + tolerance) {
                    constraintViolations++;
                }
            }
        }
    }
    
    // Property: All bones should respect their constraints
    EXPECT_EQ(constraintViolations, 0) 
        << "Found " << constraintViolations << " constraint violations out of " 
        << NUM_ITERATIONS << " iterations";
}

/*
 * Additional property test: Bone hierarchy consistency
 * For any skeleton, global transforms should be consistent with parent-child relationships
 */
TEST_F(SkeletalAnimationPropertyTest, BoneHierarchyConsistency) {
    const int NUM_ITERATIONS = 100;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        int numBones = RandomInt(3, 15);
        auto skeleton = CreateRandomSkeleton(numBones);
        
        // Update global transforms
        skeleton->UpdateGlobalTransforms();
        
        // Verify hierarchy consistency
        for (int i = 0; i < numBones; ++i) {
            const Bone& bone = skeleton->GetBone(i);
            
            if (bone.parentIndex == -1) {
                // Root bone: global should equal local
                for (int row = 0; row < 4; ++row) {
                    for (int col = 0; col < 4; ++col) {
                        EXPECT_NEAR(bone.globalTransform[row][col], 
                                   bone.localTransform[row][col], 
                                   0.001f)
                            << "Root bone global transform mismatch at iteration " << iter;
                    }
                }
            } else {
                // Child bone: global should equal parent.global * local
                const Bone& parent = skeleton->GetBone(bone.parentIndex);
                glm::mat4 expectedGlobal = parent.globalTransform * bone.localTransform;
                
                for (int row = 0; row < 4; ++row) {
                    for (int col = 0; col < 4; ++col) {
                        EXPECT_NEAR(bone.globalTransform[row][col], 
                                   expectedGlobal[row][col], 
                                   0.001f)
                            << "Child bone global transform mismatch at iteration " << iter;
                    }
                }
            }
        }
    }
}

/*
 * Additional property test: Animation interpolation smoothness
 * For any animation, interpolated keyframes should produce smooth transitions
 */
TEST_F(SkeletalAnimationPropertyTest, AnimationInterpolationSmoothness) {
    const int NUM_ITERATIONS = 100;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        int numChannels = RandomInt(1, 5);
        int numKeyframes = RandomInt(3, 10);
        
        std::string clipName = "TestClip_" + std::to_string(iter);
        auto clip = CreateRandomAnimationClip(clipName, numChannels, numKeyframes);
        
        // Test interpolation at various time points
        float duration = clip->GetDuration();
        const int numSamples = 20;
        
        for (const AnimationChannel& channel : clip->GetChannels()) {
            std::vector<Keyframe> samples;
            
            for (int s = 0; s < numSamples; ++s) {
                float time = (duration / (numSamples - 1)) * s;
                Keyframe interpolated = channel.Interpolate(time);
                samples.push_back(interpolated);
            }
            
            // Verify smoothness: consecutive samples should not have huge jumps
            for (size_t s = 1; s < samples.size(); ++s) {
                float positionDiff = glm::length(samples[s].position - samples[s-1].position);
                float scaleDiff = glm::length(samples[s].scale - samples[s-1].scale);
                
                // Maximum expected change per sample (based on duration and sampling)
                float maxExpectedChange = 50.0f * (duration / numSamples);
                
                EXPECT_LT(positionDiff, maxExpectedChange)
                    << "Position jump too large between samples at iteration " << iter;
                EXPECT_LT(scaleDiff, maxExpectedChange)
                    << "Scale jump too large between samples at iteration " << iter;
            }
        }
    }
}

/*
 * Additional property test: Skeletal mesh deformation
 * For any skeletal mesh, deformed vertices should be influenced by bone weights correctly
 */
TEST_F(SkeletalAnimationPropertyTest, SkeletalMeshDeformation) {
    const int NUM_ITERATIONS = 100;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        int numBones = RandomInt(2, 8);
        auto skeleton = CreateRandomSkeleton(numBones);
        skeleton->UpdateGlobalTransforms();
        
        auto mesh = animSystem->CreateSkeletalMesh();
        mesh->SetSkeleton(skeleton);
        
        // Create random vertices with weights
        std::vector<SkeletalMesh::Vertex> vertices;
        int numVertices = RandomInt(10, 50);
        
        for (int v = 0; v < numVertices; ++v) {
            SkeletalMesh::Vertex vertex;
            vertex.position = RandomVec3(-10.0f, 10.0f);
            vertex.normal = glm::normalize(RandomVec3(-1.0f, 1.0f));
            vertex.texCoord = glm::vec2(RandomFloat(0.0f, 1.0f), RandomFloat(0.0f, 1.0f));
            
            // Add 1-4 bone weights
            int numWeights = RandomInt(1, std::min(4, numBones));
            float totalWeight = 0.0f;
            
            for (int w = 0; w < numWeights; ++w) {
                SkeletalMesh::VertexWeight weight;
                weight.boneIndex = RandomInt(0, numBones - 1);
                weight.weight = RandomFloat(0.1f, 1.0f);
                totalWeight += weight.weight;
                vertex.weights.push_back(weight);
            }
            
            // Normalize weights
            for (auto& weight : vertex.weights) {
                weight.weight /= totalWeight;
            }
            
            vertices.push_back(vertex);
        }
        
        mesh->SetVertices(vertices);
        
        // Get bone matrices and deform mesh
        auto boneMatrices = skeleton->GetBoneMatrices();
        auto deformedPositions = mesh->GetDeformedPositions(boneMatrices);
        auto deformedNormals = mesh->GetDeformedNormals(boneMatrices);
        
        // Verify deformation
        EXPECT_EQ(deformedPositions.size(), vertices.size())
            << "Deformed positions count mismatch at iteration " << iter;
        EXPECT_EQ(deformedNormals.size(), vertices.size())
            << "Deformed normals count mismatch at iteration " << iter;
        
        // Verify normals are normalized
        for (const glm::vec3& normal : deformedNormals) {
            float length = glm::length(normal);
            if (length > 0.0f) {
                EXPECT_NEAR(length, 1.0f, 0.01f)
                    << "Deformed normal not normalized at iteration " << iter;
            }
        }
    }
}

/*
 * Additional property test: Animation playback state management
 * For any animation playback, state should be managed correctly
 */
TEST_F(SkeletalAnimationPropertyTest, AnimationPlaybackStateManagement) {
    const int NUM_ITERATIONS = 100;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        int entityId = RandomInt(1, 1000);
        
        // Create random animation
        std::string clipName = "PlaybackTest_" + std::to_string(iter);
        auto clip = CreateRandomAnimationClip(clipName, RandomInt(1, 5), RandomInt(3, 8));
        
        // Play animation
        bool shouldLoop = (RandomInt(0, 1) == 1);
        animSystem->PlayAnimation(entityId, clip, shouldLoop);
        
        // Verify state is created
        AnimationState* state = animSystem->GetAnimationState(entityId);
        ASSERT_NE(state, nullptr) << "Animation state not created at iteration " << iter;
        EXPECT_TRUE(state->isPlaying) << "Animation should be playing at iteration " << iter;
        EXPECT_EQ(state->isLooping, shouldLoop) << "Loop state mismatch at iteration " << iter;
        EXPECT_FLOAT_EQ(state->currentTime, 0.0f) << "Initial time should be 0 at iteration " << iter;
        
        // Pause animation
        animSystem->PauseAnimation(entityId);
        state = animSystem->GetAnimationState(entityId);
        EXPECT_FALSE(state->isPlaying) << "Animation should be paused at iteration " << iter;
        
        // Resume animation
        animSystem->ResumeAnimation(entityId);
        state = animSystem->GetAnimationState(entityId);
        EXPECT_TRUE(state->isPlaying) << "Animation should be playing after resume at iteration " << iter;
        
        // Set playback speed
        float speed = RandomFloat(0.5f, 2.0f);
        animSystem->SetPlaybackSpeed(entityId, speed);
        state = animSystem->GetAnimationState(entityId);
        EXPECT_FLOAT_EQ(state->playbackSpeed, speed) << "Playback speed mismatch at iteration " << iter;
        
        // Stop animation
        animSystem->StopAnimation(entityId);
        state = animSystem->GetAnimationState(entityId);
        EXPECT_EQ(state, nullptr) << "Animation state should be removed after stop at iteration " << iter;
    }
}
