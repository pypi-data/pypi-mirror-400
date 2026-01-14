#include <gtest/gtest.h>
#include "pywrkgame/animation/AnimationSystem.h"
#include "pywrkgame/animation/IKSolver.h"
#include <random>
#include <vector>
#include <cmath>

using namespace pywrkgame;

// Property-based test helper class
class IKSolverPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        animSystem = std::make_unique<AnimationSystem>();
        ikSystem = std::make_unique<IKSystem>();
        ASSERT_TRUE(animSystem->Initialize());
        ASSERT_TRUE(ikSystem->Initialize());
        rng.seed(42); // Fixed seed for reproducibility
    }
    
    void TearDown() override {
        ikSystem->Shutdown();
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
        glm::vec3 axis = glm::normalize(RandomVec3(-1.0f, 1.0f));
        float angle = RandomFloat(0.0f, glm::two_pi<float>());
        return glm::angleAxis(angle, axis);
    }
    
    int RandomInt(int min, int max) {
        std::uniform_int_distribution<int> dist(min, max);
        return dist(rng);
    }
    
    // Create a simple chain skeleton
    std::shared_ptr<Skeleton> CreateChainSkeleton(int numBones, float boneLength) {
        auto skeleton = animSystem->CreateSkeleton();
        
        for (int i = 0; i < numBones; ++i) {
            Bone bone;
            bone.name = "Bone_" + std::to_string(i);
            bone.parentIndex = (i == 0) ? -1 : i - 1;
            bone.offsetMatrix = glm::mat4(1.0f);
            
            // Position bones along Y axis
            glm::vec3 position(0.0f, boneLength, 0.0f);
            bone.localTransform = glm::translate(glm::mat4(1.0f), position);
            
            skeleton->AddBone(bone);
        }
        
        skeleton->UpdateGlobalTransforms();
        return skeleton;
    }
    
    // Create IK chain from skeleton
    std::shared_ptr<IKChain> CreateIKChainFromSkeleton(const Skeleton& skeleton) {
        auto chain = ikSystem->CreateChain();
        
        for (int i = 0; i < skeleton.GetBoneCount(); ++i) {
            chain->AddBone(i);
        }
        
        chain->SetEndEffector(skeleton.GetBoneCount() - 1);
        return chain;
    }
    
    // Get end effector position
    glm::vec3 GetEndEffectorPosition(const Skeleton& skeleton, int endEffectorIndex) {
        const Bone& bone = skeleton.GetBone(endEffectorIndex);
        return glm::vec3(bone.globalTransform[3]);
    }
    
    std::unique_ptr<AnimationSystem> animSystem;
    std::unique_ptr<IKSystem> ikSystem;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 32: IK Solver Accuracy
 * For any IK chain setup, the solver should find valid solutions that satisfy end-effector constraints
 * Validates: Requirements 6.6
 */
TEST_F(IKSolverPropertyTest, Property32_IKSolverAccuracy) {
    const int NUM_ITERATIONS = 100;
    int successfulSolves = 0;
    int totalTests = 0;
    
    // Test different IK algorithms
    std::vector<IKAlgorithm> algorithms = {
        IKAlgorithm::CCD,
        IKAlgorithm::FABRIK,
        IKAlgorithm::Jacobian
    };
    
    for (IKAlgorithm algorithm : algorithms) {
        for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
            // Create random chain
            int numBones = RandomInt(2, 6);
            float boneLength = RandomFloat(1.0f, 3.0f);
            auto skeleton = CreateChainSkeleton(numBones, boneLength);
            auto chain = CreateIKChainFromSkeleton(*skeleton);
            
            // Set reasonable iteration count and tolerance
            chain->SetMaxIterations(20);
            chain->SetTolerance(0.1f);
            
            // Calculate reachable target (within chain length)
            float totalLength = numBones * boneLength;
            float targetDistance = RandomFloat(0.5f, totalLength * 0.9f);
            
            glm::vec3 direction = glm::normalize(RandomVec3(-1.0f, 1.0f));
            glm::vec3 targetPosition = direction * targetDistance;
            
            // Solve IK
            bool solved = ikSystem->SolveIK(*skeleton, *chain, targetPosition, algorithm);
            
            totalTests++;
            
            if (solved) {
                // Verify end effector is close to target
                int endEffectorIndex = chain->GetEndEffector();
                glm::vec3 endEffectorPos = GetEndEffectorPosition(*skeleton, endEffectorIndex);
                float distance = glm::length(endEffectorPos - targetPosition);
                
                // Should be within tolerance (with some margin)
                if (distance < chain->GetTolerance() * 10.0f) {
                    successfulSolves++;
                }
            }
        }
    }
    
    // Property: IK solver should successfully reach reachable targets most of the time
    float successRate = static_cast<float>(successfulSolves) / totalTests;
    EXPECT_GT(successRate, 0.7f) 
        << "IK solver success rate too low: " << successRate 
        << " (" << successfulSolves << "/" << totalTests << ")";
}

/*
 * Additional property test: IK constraint enforcement
 * For any IK chain with constraints, solved poses should respect all constraints
 */
TEST_F(IKSolverPropertyTest, IKConstraintEnforcement) {
    const int NUM_ITERATIONS = 100;
    int constraintViolations = 0;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create chain with constraints
        int numBones = RandomInt(2, 5);
        float boneLength = RandomFloat(1.0f, 2.0f);
        auto skeleton = CreateChainSkeleton(numBones, boneLength);
        auto chain = CreateIKChainFromSkeleton(*skeleton);
        
        // Add random constraints to bones
        for (int i = 0; i < numBones; ++i) {
            IKConstraint constraint;
            constraint.type = IKConstraintType::HingeJoint;
            constraint.axis = glm::vec3(0.0f, 0.0f, 1.0f);
            constraint.minAngle = RandomFloat(-glm::pi<float>() / 2.0f, -0.1f);
            constraint.maxAngle = RandomFloat(0.1f, glm::pi<float>() / 2.0f);
            
            chain->SetConstraint(i, constraint);
        }
        
        // Solve for random reachable target
        float totalLength = numBones * boneLength;
        glm::vec3 targetPosition = RandomVec3(-totalLength * 0.8f, totalLength * 0.8f);
        
        ikSystem->SolveIK(*skeleton, *chain, targetPosition, IKAlgorithm::FABRIK);
        
        // Verify constraints are respected
        for (int i = 0; i < numBones; ++i) {
            const Bone& bone = skeleton->GetBone(i);
            const IKConstraint& constraint = chain->GetConstraint(i);
            
            if (constraint.type == IKConstraintType::HingeJoint) {
                glm::quat rotation = glm::quat_cast(bone.localTransform);
                glm::vec3 euler = glm::eulerAngles(rotation);
                
                float angle = glm::dot(euler, constraint.axis);
                
                // Check if angle is within constraints (with tolerance)
                const float tolerance = 0.2f;
                if (angle < constraint.minAngle - tolerance || 
                    angle > constraint.maxAngle + tolerance) {
                    constraintViolations++;
                }
            }
        }
    }
    
    // Property: Constraints should be respected in solved poses
    EXPECT_EQ(constraintViolations, 0)
        << "Found " << constraintViolations << " constraint violations";
}

/*
 * Additional property test: IK solution stability
 * For any target position, multiple solves should produce similar results
 */
TEST_F(IKSolverPropertyTest, IKSolutionStability) {
    const int NUM_ITERATIONS = 50;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create chain
        int numBones = RandomInt(3, 5);
        float boneLength = 2.0f;
        
        // Solve same target multiple times
        glm::vec3 targetPosition = RandomVec3(-5.0f, 5.0f);
        
        std::vector<glm::vec3> endEffectorPositions;
        
        for (int solve = 0; solve < 3; ++solve) {
            auto skeleton = CreateChainSkeleton(numBones, boneLength);
            auto chain = CreateIKChainFromSkeleton(*skeleton);
            
            chain->SetMaxIterations(20);
            chain->SetTolerance(0.1f);
            
            ikSystem->SolveIK(*skeleton, *chain, targetPosition, IKAlgorithm::FABRIK);
            
            int endEffectorIndex = chain->GetEndEffector();
            glm::vec3 endEffectorPos = GetEndEffectorPosition(*skeleton, endEffectorIndex);
            endEffectorPositions.push_back(endEffectorPos);
        }
        
        // Verify all solutions are similar
        for (size_t i = 1; i < endEffectorPositions.size(); ++i) {
            float distance = glm::length(endEffectorPositions[i] - endEffectorPositions[0]);
            
            // Solutions should be very similar (within 1 unit)
            EXPECT_LT(distance, 1.0f)
                << "IK solution unstable at iteration " << iter 
                << ", distance between solutions: " << distance;
        }
    }
}

/*
 * Additional property test: CCD vs FABRIK consistency
 * For any reachable target, both algorithms should reach similar end positions
 */
TEST_F(IKSolverPropertyTest, AlgorithmConsistency) {
    const int NUM_ITERATIONS = 50;
    int inconsistentResults = 0;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create chain
        int numBones = RandomInt(3, 5);
        float boneLength = 2.0f;
        float totalLength = numBones * boneLength;
        
        // Create reachable target
        float targetDistance = RandomFloat(0.5f, totalLength * 0.8f);
        glm::vec3 direction = glm::normalize(RandomVec3(-1.0f, 1.0f));
        glm::vec3 targetPosition = direction * targetDistance;
        
        // Solve with CCD
        auto skeletonCCD = CreateChainSkeleton(numBones, boneLength);
        auto chainCCD = CreateIKChainFromSkeleton(*skeletonCCD);
        chainCCD->SetMaxIterations(20);
        chainCCD->SetTolerance(0.1f);
        
        bool solvedCCD = ikSystem->SolveIK(*skeletonCCD, *chainCCD, targetPosition, IKAlgorithm::CCD);
        glm::vec3 endPosCCD = GetEndEffectorPosition(*skeletonCCD, chainCCD->GetEndEffector());
        
        // Solve with FABRIK
        auto skeletonFABRIK = CreateChainSkeleton(numBones, boneLength);
        auto chainFABRIK = CreateIKChainFromSkeleton(*skeletonFABRIK);
        chainFABRIK->SetMaxIterations(20);
        chainFABRIK->SetTolerance(0.1f);
        
        bool solvedFABRIK = ikSystem->SolveIK(*skeletonFABRIK, *chainFABRIK, targetPosition, IKAlgorithm::FABRIK);
        glm::vec3 endPosFABRIK = GetEndEffectorPosition(*skeletonFABRIK, chainFABRIK->GetEndEffector());
        
        // If both solved, end positions should be close to target
        if (solvedCCD && solvedFABRIK) {
            float distanceCCD = glm::length(endPosCCD - targetPosition);
            float distanceFABRIK = glm::length(endPosFABRIK - targetPosition);
            
            // Both should be reasonably close to target
            if (distanceCCD > 1.0f || distanceFABRIK > 1.0f) {
                inconsistentResults++;
            }
        }
    }
    
    // Property: Both algorithms should produce consistent results
    EXPECT_LT(inconsistentResults, NUM_ITERATIONS * 0.2f)
        << "Too many inconsistent results between algorithms: " << inconsistentResults;
}

/*
 * Additional property test: IK chain length preservation
 * For any IK solution, total chain length should remain constant
 */
TEST_F(IKSolverPropertyTest, ChainLengthPreservation) {
    const int NUM_ITERATIONS = 100;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create chain
        int numBones = RandomInt(3, 6);
        float boneLength = 2.0f;
        auto skeleton = CreateChainSkeleton(numBones, boneLength);
        auto chain = CreateIKChainFromSkeleton(*skeleton);
        
        // Calculate initial total length
        float initialLength = 0.0f;
        for (int i = 0; i < numBones - 1; ++i) {
            glm::vec3 pos1 = GetEndEffectorPosition(*skeleton, i);
            glm::vec3 pos2 = GetEndEffectorPosition(*skeleton, i + 1);
            initialLength += glm::length(pos2 - pos1);
        }
        
        // Solve for random target
        glm::vec3 targetPosition = RandomVec3(-5.0f, 5.0f);
        ikSystem->SolveIK(*skeleton, *chain, targetPosition, IKAlgorithm::FABRIK);
        
        // Calculate final total length
        float finalLength = 0.0f;
        for (int i = 0; i < numBones - 1; ++i) {
            glm::vec3 pos1 = GetEndEffectorPosition(*skeleton, i);
            glm::vec3 pos2 = GetEndEffectorPosition(*skeleton, i + 1);
            finalLength += glm::length(pos2 - pos1);
        }
        
        // Property: Chain length should be preserved (within tolerance)
        float lengthDifference = std::abs(finalLength - initialLength);
        EXPECT_LT(lengthDifference, 0.5f)
            << "Chain length not preserved at iteration " << iter
            << ", initial: " << initialLength << ", final: " << finalLength;
    }
}

/*
 * Additional property test: Unreachable target handling
 * For any unreachable target, solver should stretch towards it without breaking
 */
TEST_F(IKSolverPropertyTest, UnreachableTargetHandling) {
    const int NUM_ITERATIONS = 50;
    
    for (int iter = 0; iter < NUM_ITERATIONS; ++iter) {
        // Create chain
        int numBones = RandomInt(2, 4);
        float boneLength = 2.0f;
        float totalLength = numBones * boneLength;
        auto skeleton = CreateChainSkeleton(numBones, boneLength);
        auto chain = CreateIKChainFromSkeleton(*skeleton);
        
        // Create unreachable target (beyond chain length)
        float targetDistance = RandomFloat(totalLength * 1.5f, totalLength * 3.0f);
        glm::vec3 direction = glm::normalize(RandomVec3(-1.0f, 1.0f));
        glm::vec3 targetPosition = direction * targetDistance;
        
        // Solve IK
        ikSystem->SolveIK(*skeleton, *chain, targetPosition, IKAlgorithm::FABRIK);
        
        // Verify skeleton is still valid (no NaN or infinite values)
        bool skeletonValid = true;
        for (int i = 0; i < numBones; ++i) {
            const Bone& bone = skeleton->GetBone(i);
            glm::vec3 pos = glm::vec3(bone.globalTransform[3]);
            
            if (std::isnan(pos.x) || std::isnan(pos.y) || std::isnan(pos.z) ||
                std::isinf(pos.x) || std::isinf(pos.y) || std::isinf(pos.z)) {
                skeletonValid = false;
                break;
            }
        }
        
        EXPECT_TRUE(skeletonValid)
            << "Skeleton became invalid when solving for unreachable target at iteration " << iter;
        
        // Verify chain is stretched towards target
        int endEffectorIndex = chain->GetEndEffector();
        glm::vec3 endEffectorPos = GetEndEffectorPosition(*skeleton, endEffectorIndex);
        glm::vec3 toTarget = glm::normalize(targetPosition);
        glm::vec3 toEndEffector = glm::normalize(endEffectorPos);
        
        float alignment = glm::dot(toTarget, toEndEffector);
        
        // End effector should be pointing towards target (alignment > 0.5)
        EXPECT_GT(alignment, 0.5f)
            << "Chain not stretched towards unreachable target at iteration " << iter;
    }
}
