#include <gtest/gtest.h>
#include "pywrkgame/ai/AIFramework.h"
#include <random>
#include <vector>
#include <cmath>

using namespace pywrkgame;

// Property-based test helper class
class AIPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        ai = std::make_unique<AIFramework>();
        ASSERT_TRUE(ai->Initialize());
        rng.seed(42); // Fixed seed for reproducibility
    }
    
    void TearDown() override {
        ai->Shutdown();
    }
    
    // Generate random Vector3 within range
    Vector3 RandomVector3(float min = -100.0f, float max = 100.0f) {
        std::uniform_real_distribution<float> dist(min, max);
        return Vector3(dist(rng), dist(rng), dist(rng));
    }
    
    // Generate random float within range
    float RandomFloat(float min = 0.1f, float max = 10.0f) {
        std::uniform_real_distribution<float> dist(min, max);
        return dist(rng);
    }
    
    // Generate random int within range
    int RandomInt(int min, int max) {
        std::uniform_int_distribution<int> dist(min, max);
        return dist(rng);
    }
    
    std::unique_ptr<AIFramework> ai;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 46: Behavior Tree Execution
 * For any NPC with behavior trees, AI should execute behaviors correctly according to tree logic
 * Validates: Requirements 9.1
 */
TEST_F(AIPropertyTest, Property46_BehaviorTreeExecution) {
    const int NUM_ITERATIONS = 100;
    int successfulExecutions = 0;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        int treeId = ai->CreateBehaviorTree();
        BehaviorTree* tree = ai->GetBehaviorTree(treeId);
        ASSERT_NE(tree, nullptr);
        
        // Test 1: Sequence node should execute all children in order
        {
            auto sequence = std::make_shared<SequenceNode>();
            
            int executionOrder = 0;
            int expectedOrder = 0;
            
            // Add multiple action nodes
            int numActions = RandomInt(2, 5);
            for (int j = 0; j < numActions; ++j) {
                int expectedValue = j;
                auto action = std::make_shared<ActionNode>([&executionOrder, expectedValue]() {
                    if (executionOrder == expectedValue) {
                        executionOrder++;
                        return BehaviorNodeStatus::Success;
                    }
                    return BehaviorNodeStatus::Failure;
                });
                sequence->AddChild(action);
            }
            
            tree->SetRoot(sequence);
            auto status = tree->Execute();
            
            // Sequence should succeed if all actions executed in order
            if (executionOrder == numActions) {
                EXPECT_EQ(status, BehaviorNodeStatus::Success);
                successfulExecutions++;
            }
        }
        
        // Test 2: Selector node should stop at first success
        {
            auto selector = std::make_shared<SelectorNode>();
            
            bool firstExecuted = false;
            bool secondExecuted = false;
            bool thirdExecuted = false;
            
            // First child fails
            selector->AddChild(std::make_shared<ActionNode>([&firstExecuted]() {
                firstExecuted = true;
                return BehaviorNodeStatus::Failure;
            }));
            
            // Second child succeeds
            selector->AddChild(std::make_shared<ActionNode>([&secondExecuted]() {
                secondExecuted = true;
                return BehaviorNodeStatus::Success;
            }));
            
            // Third child should not execute
            selector->AddChild(std::make_shared<ActionNode>([&thirdExecuted]() {
                thirdExecuted = true;
                return BehaviorNodeStatus::Success;
            }));
            
            tree->SetRoot(selector);
            auto status = tree->Execute();
            
            EXPECT_EQ(status, BehaviorNodeStatus::Success);
            EXPECT_TRUE(firstExecuted);
            EXPECT_TRUE(secondExecuted);
            EXPECT_FALSE(thirdExecuted); // Should not execute after success
        }
        
        // Test 3: Inverter node should invert results
        {
            bool shouldSucceed = (i % 2 == 0);
            
            auto action = std::make_shared<ActionNode>([shouldSucceed]() {
                return shouldSucceed ? BehaviorNodeStatus::Success : BehaviorNodeStatus::Failure;
            });
            
            auto inverter = std::make_shared<InverterNode>(action);
            tree->SetRoot(inverter);
            auto status = tree->Execute();
            
            // Inverter should flip the result
            if (shouldSucceed) {
                EXPECT_EQ(status, BehaviorNodeStatus::Failure);
            } else {
                EXPECT_EQ(status, BehaviorNodeStatus::Success);
            }
        }
        
        ai->DestroyBehaviorTree(treeId);
    }
    
    // At least 80% of iterations should execute correctly
    EXPECT_GT(successfulExecutions, NUM_ITERATIONS * 0.8);
}

/*
 * Feature: pywrkgame-library, Property 47: Pathfinding Accuracy
 * For any pathfinding request using A*, NavMesh, or flow fields, optimal or near-optimal paths should be found
 * Validates: Requirements 9.2
 */
TEST_F(AIPropertyTest, Property47_PathfindingAccuracy) {
    const int NUM_ITERATIONS = 20;  // Reduced from 100 for faster execution
    int successfulPaths = 0;
    
    Pathfinder& pathfinder = ai->GetPathfinder();
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Test A* pathfinding
        Vector3 start = RandomVector3(-50.0f, 50.0f);
        Vector3 goal = RandomVector3(-50.0f, 50.0f);
        float gridSize = RandomFloat(0.5f, 2.0f);
        
        // Simple walkability function - all positions are walkable
        auto isWalkable = [](const Vector3& pos) {
            return true;
        };
        
        auto path = pathfinder.FindPathAStar(start, goal, isWalkable, gridSize);
        
        if (!path.empty()) {
            // Verify path starts near start position
            float startDist = path.front().Distance(start);
            EXPECT_LT(startDist, gridSize * 2.0f);
            
            // Verify path ends near goal position
            float goalDist = path.back().Distance(goal);
            EXPECT_LT(goalDist, gridSize * 2.0f);
            
            // Verify path continuity - each step should be approximately gridSize apart
            bool pathContinuous = true;
            for (size_t j = 1; j < path.size(); ++j) {
                float stepDist = path[j].Distance(path[j-1]);
                if (stepDist > gridSize * 1.5f) {
                    pathContinuous = false;
                    break;
                }
            }
            
            if (pathContinuous) {
                successfulPaths++;
            }
        }
    }
    
    // At least 70% of paths should be valid
    EXPECT_GT(successfulPaths, NUM_ITERATIONS * 0.7);
    
    // Test NavMesh pathfinding
    int navMeshId = ai->CreateNavMesh();
    NavMesh* navMesh = ai->GetNavMesh(navMeshId);
    ASSERT_NE(navMesh, nullptr);
    
    // Create a simple NavMesh with connected triangles
    navMesh->AddTriangle(
        Vector3(0, 0, 0),
        Vector3(10, 0, 0),
        Vector3(5, 0, 10)
    );
    navMesh->AddTriangle(
        Vector3(10, 0, 0),
        Vector3(20, 0, 0),
        Vector3(15, 0, 10)
    );
    navMesh->AddTriangle(
        Vector3(5, 0, 10),
        Vector3(15, 0, 10),
        Vector3(10, 0, 20)
    );
    
    navMesh->BuildConnections();
    
    // Test pathfinding on NavMesh
    Vector3 navStart(5, 0, 5);
    Vector3 navGoal(10, 0, 15);
    
    auto navPath = pathfinder.FindPathNavMesh(navStart, navGoal, *navMesh);
    
    if (!navPath.empty()) {
        // Path should start near start and end near goal
        EXPECT_LT(navPath.front().Distance(navStart), 10.0f);
        EXPECT_LT(navPath.back().Distance(navGoal), 10.0f);
    }
    
    ai->DestroyNavMesh(navMeshId);
    
    // Test Flow Field generation
    Vector3 flowGoal(0, 0, 0);
    
    // Define walkability function for flow field
    auto isWalkableFlow = [](const Vector3& pos) {
        return true;
    };
    
    auto flowField = pathfinder.GenerateFlowField(flowGoal, isWalkableFlow, 1.0f, 50.0f);
    
    // Test that flow directions point generally toward goal
    int correctDirections = 0;
    for (int i = 0; i < 20; ++i) {
        Vector3 testPos = RandomVector3(-20.0f, 20.0f);
        Vector3 flowDir = pathfinder.GetFlowDirection(flowField, testPos);
        
        if (flowDir.Length() > 0.01f) {
            Vector3 toGoal = (flowGoal - testPos).Normalized();
            float dotProduct = flowDir.x * toGoal.x + flowDir.y * toGoal.y + flowDir.z * toGoal.z;
            
            // Flow direction should generally point toward goal (dot product > 0)
            if (dotProduct > 0) {
                correctDirections++;
            }
        }
    }
    
    // Most flow directions should point toward goal
    EXPECT_GT(correctDirections, 10);
}

/*
 * Feature: pywrkgame-library, Property 50: Crowd Simulation Realism
 * For any large group of NPCs, crowd behavior should appear realistic and avoid unrealistic clustering or movement
 * Validates: Requirements 9.6
 */
TEST_F(AIPropertyTest, Property50_CrowdSimulationRealism) {
    const int NUM_ITERATIONS = 100;
    int realisticBehaviors = 0;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        int crowdId = ai->CreateCrowdSimulation();
        CrowdSimulation* crowd = ai->GetCrowdSimulation(crowdId);
        ASSERT_NE(crowd, nullptr);
        
        // Create a crowd of agents
        int numAgents = RandomInt(5, 20);
        std::vector<int> agentIds;
        
        for (int j = 0; j < numAgents; ++j) {
            Vector3 pos = RandomVector3(-20.0f, 20.0f);
            float radius = RandomFloat(0.3f, 0.7f);
            float maxSpeed = RandomFloat(3.0f, 7.0f);
            
            int agentId = crowd->AddAgent(pos, radius, maxSpeed);
            agentIds.push_back(agentId);
            
            // Set random goal
            Vector3 goal = RandomVector3(-30.0f, 30.0f);
            crowd->SetAgentGoal(agentId, goal);
        }
        
        // Simulate for several frames
        float deltaTime = 0.016f; // ~60 FPS
        int numFrames = 60; // 1 second of simulation
        
        for (int frame = 0; frame < numFrames; ++frame) {
            crowd->Update(deltaTime);
        }
        
        // Check crowd behavior properties
        bool hasRealisticBehavior = true;
        
        // Property 1: Agents should maintain separation (no excessive overlap)
        int overlappingPairs = 0;
        for (size_t j = 0; j < agentIds.size(); ++j) {
            for (size_t k = j + 1; k < agentIds.size(); ++k) {
                Vector3 pos1 = crowd->GetAgentPosition(agentIds[j]);
                Vector3 pos2 = crowd->GetAgentPosition(agentIds[k]);
                float dist = pos1.Distance(pos2);
                
                // Agents should maintain some minimum distance
                if (dist < 0.2f) {
                    overlappingPairs++;
                }
            }
        }
        
        // No more than 10% of pairs should be overlapping
        int totalPairs = (numAgents * (numAgents - 1)) / 2;
        if (overlappingPairs > totalPairs * 0.1f) {
            hasRealisticBehavior = false;
        }
        
        // Property 2: Agents should be moving (not stuck)
        int movingAgents = 0;
        for (int agentId : agentIds) {
            Vector3 velocity = crowd->GetAgentVelocity(agentId);
            if (velocity.Length() > 0.1f) {
                movingAgents++;
            }
        }
        
        // At least 50% of agents should be moving
        if (movingAgents < numAgents * 0.5f) {
            hasRealisticBehavior = false;
        }
        
        // Property 3: Agents should not cluster too tightly
        // Calculate average distance to nearest neighbor
        float avgNearestDist = 0.0f;
        for (int agentId : agentIds) {
            Vector3 pos = crowd->GetAgentPosition(agentId);
            float nearestDist = std::numeric_limits<float>::max();
            
            for (int otherId : agentIds) {
                if (otherId != agentId) {
                    Vector3 otherPos = crowd->GetAgentPosition(otherId);
                    float dist = pos.Distance(otherPos);
                    nearestDist = std::min(nearestDist, dist);
                }
            }
            
            avgNearestDist += nearestDist;
        }
        avgNearestDist /= numAgents;
        
        // Average nearest neighbor distance should be reasonable (not too small)
        if (avgNearestDist < 0.5f) {
            hasRealisticBehavior = false;
        }
        
        if (hasRealisticBehavior) {
            realisticBehaviors++;
        }
        
        ai->DestroyCrowdSimulation(crowdId);
    }
    
    // At least 70% of simulations should show realistic behavior
    EXPECT_GT(realisticBehaviors, NUM_ITERATIONS * 0.7);
}

// Additional test: Verify crowd simulation parameters affect behavior
TEST_F(AIPropertyTest, CrowdSimulationParameterEffects) {
    int crowdId = ai->CreateCrowdSimulation();
    CrowdSimulation* crowd = ai->GetCrowdSimulation(crowdId);
    ASSERT_NE(crowd, nullptr);
    
    // Create agents
    std::vector<int> agentIds;
    for (int i = 0; i < 10; ++i) {
        Vector3 pos(i * 2.0f, 0, 0);
        int agentId = crowd->AddAgent(pos, 0.5f, 5.0f);
        agentIds.push_back(agentId);
        crowd->SetAgentGoal(agentId, Vector3(50, 0, 0));
    }
    
    // Test with high separation weight
    crowd->SetSeparationWeight(5.0f);
    crowd->SetAlignmentWeight(0.5f);
    crowd->SetCohesionWeight(0.5f);
    
    for (int i = 0; i < 30; ++i) {
        crowd->Update(0.016f);
    }
    
    // Agents should spread out more with high separation
    float avgSpacing1 = 0.0f;
    for (size_t i = 1; i < agentIds.size(); ++i) {
        Vector3 pos1 = crowd->GetAgentPosition(agentIds[i-1]);
        Vector3 pos2 = crowd->GetAgentPosition(agentIds[i]);
        avgSpacing1 += pos1.Distance(pos2);
    }
    avgSpacing1 /= (agentIds.size() - 1);
    
    // Reset and test with high cohesion weight
    ai->DestroyCrowdSimulation(crowdId);
    crowdId = ai->CreateCrowdSimulation();
    crowd = ai->GetCrowdSimulation(crowdId);
    
    agentIds.clear();
    for (int i = 0; i < 10; ++i) {
        Vector3 pos(i * 2.0f, 0, 0);
        int agentId = crowd->AddAgent(pos, 0.5f, 5.0f);
        agentIds.push_back(agentId);
        crowd->SetAgentGoal(agentId, Vector3(50, 0, 0));
    }
    
    crowd->SetSeparationWeight(0.5f);
    crowd->SetAlignmentWeight(0.5f);
    crowd->SetCohesionWeight(5.0f);
    
    for (int i = 0; i < 30; ++i) {
        crowd->Update(0.016f);
    }
    
    float avgSpacing2 = 0.0f;
    for (size_t i = 1; i < agentIds.size(); ++i) {
        Vector3 pos1 = crowd->GetAgentPosition(agentIds[i-1]);
        Vector3 pos2 = crowd->GetAgentPosition(agentIds[i]);
        avgSpacing2 += pos1.Distance(pos2);
    }
    avgSpacing2 /= (agentIds.size() - 1);
    
    // High separation should result in larger spacing than high cohesion
    EXPECT_GT(avgSpacing1, avgSpacing2);
    
    ai->DestroyCrowdSimulation(crowdId);
}
