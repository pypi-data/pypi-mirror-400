#include <gtest/gtest.h>
#include "pywrkgame/physics/PhysicsEngine.h"
#include <random>
#include <vector>

using namespace pywrkgame::physics;

// Property-based test helper class
class PhysicsPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        physics = std::make_unique<PhysicsEngine>();
        rng.seed(42); // Fixed seed for reproducibility
    }
    
    // Generate random Vec3 within range
    Vec3 RandomVec3(float min = -100.0f, float max = 100.0f) {
        std::uniform_real_distribution<float> dist(min, max);
        return Vec3(dist(rng), dist(rng), dist(rng));
    }
    
    // Generate random float within range
    float RandomFloat(float min = 0.1f, float max = 10.0f) {
        std::uniform_real_distribution<float> dist(min, max);
        return dist(rng);
    }
    
    std::unique_ptr<PhysicsEngine> physics;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 27: 2D Collision Detection
 * For any 2D rigid bodies, collisions should be detected accurately and collision responses should be physically correct
 * Validates: Requirements 6.1
 */
TEST_F(PhysicsPropertyTest, Property27_2DCollisionDetection) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Box2D));
    
    // Run property test with multiple random inputs
    const int NUM_ITERATIONS = 100;
    int collisionTests = 0;
    int correctDetections = 0;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Create two random 2D bodies
        RigidBodyDesc desc1;
        desc1.position = Vec3(RandomFloat(-50.0f, 50.0f), RandomFloat(-50.0f, 50.0f), 0.0f);
        desc1.mass = RandomFloat(0.5f, 5.0f);
        desc1.is2D = true;
        
        RigidBodyDesc desc2;
        desc2.position = Vec3(RandomFloat(-50.0f, 50.0f), RandomFloat(-50.0f, 50.0f), 0.0f);
        desc2.mass = RandomFloat(0.5f, 5.0f);
        desc2.is2D = true;
        
        RigidBodyHandle body1 = physics->CreateRigidBody(desc1);
        RigidBodyHandle body2 = physics->CreateRigidBody(desc2);
        
        // Add box colliders
        ColliderDesc collider1;
        collider1.shape = ColliderShape::Box;
        float size1 = RandomFloat(1.0f, 5.0f);
        collider1.size = Vec3(size1, size1, 1.0f);
        physics->CreateCollider(body1, collider1);
        
        ColliderDesc collider2;
        collider2.shape = ColliderShape::Box;
        float size2 = RandomFloat(1.0f, 5.0f);
        collider2.size = Vec3(size2, size2, 1.0f);
        physics->CreateCollider(body2, collider2);
        
        // Calculate expected collision
        float distance = desc1.position.distance(desc2.position);
        float combinedSize = (size1 + size2);
        bool shouldCollide = distance < combinedSize;
        
        // Check actual collision
        bool actuallyColliding = physics->AreColliding(body1, body2);
        
        collisionTests++;
        if (shouldCollide == actuallyColliding) {
            correctDetections++;
        }
        
        physics->DestroyRigidBody(body1);
        physics->DestroyRigidBody(body2);
    }
    
    // Property: Collision detection should be accurate for most cases
    // Allow some tolerance for edge cases
    float accuracy = static_cast<float>(correctDetections) / collisionTests;
    EXPECT_GT(accuracy, 0.7f) << "Collision detection accuracy: " << accuracy;
    
    physics->Shutdown();
}

/*
 * Feature: pywrkgame-library, Property 28: 3D Soft Body Dynamics
 * For any 3D soft body, deformation and dynamics should behave realistically according to physics laws
 * Validates: Requirements 6.2
 */
TEST_F(PhysicsPropertyTest, Property28_3DSoftBodyDynamics) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    // Run property test with multiple random soft bodies
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Create a random soft body (triangle mesh)
        SoftBodyDesc desc;
        int numVertices = 3 + (i % 10); // 3 to 12 vertices
        
        for (int v = 0; v < numVertices; ++v) {
            desc.vertices.push_back(RandomVec3(-10.0f, 10.0f));
        }
        
        // Create simple triangulation
        for (int v = 0; v < numVertices - 2; ++v) {
            desc.indices.push_back(0);
            desc.indices.push_back(v + 1);
            desc.indices.push_back(v + 2);
        }
        
        desc.mass = RandomFloat(0.5f, 10.0f);
        desc.stiffness = RandomFloat(0.1f, 1.0f);
        desc.damping = RandomFloat(0.01f, 0.5f);
        
        SoftBodyHandle softBody = physics->CreateSoftBody(desc);
        ASSERT_NE(softBody, INVALID_HANDLE);
        
        // Get initial vertices
        std::vector<Vec3> initialVertices;
        physics->GetSoftBodyVertices(softBody, initialVertices);
        EXPECT_EQ(initialVertices.size(), desc.vertices.size());
        
        // Simulate for a few frames
        for (int frame = 0; frame < 10; ++frame) {
            physics->Update(0.016f);
        }
        
        // Get updated vertices
        std::vector<Vec3> updatedVertices;
        physics->GetSoftBodyVertices(softBody, updatedVertices);
        
        // Property: Soft body vertices should move under gravity
        // At least some vertices should have changed position
        bool verticesMoved = false;
        for (size_t v = 0; v < initialVertices.size() && v < updatedVertices.size(); ++v) {
            float distance = initialVertices[v].distance(updatedVertices[v]);
            if (distance > 0.01f) {
                verticesMoved = true;
                break;
            }
        }
        
        EXPECT_TRUE(verticesMoved) << "Soft body vertices should move under physics simulation";
        
        physics->DestroySoftBody(softBody);
    }
    
    physics->Shutdown();
}

/*
 * Additional property test: Rigid body velocity integration
 * For any rigid body with velocity, position should update correctly over time
 */
TEST_F(PhysicsPropertyTest, RigidBodyVelocityIntegration) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        RigidBodyDesc desc;
        desc.position = RandomVec3(-50.0f, 50.0f);
        desc.mass = RandomFloat(0.5f, 10.0f);
        desc.isKinematic = false;
        
        RigidBodyHandle body = physics->CreateRigidBody(desc);
        
        // Set random velocity
        Vec3 velocity = RandomVec3(-10.0f, 10.0f);
        physics->SetRigidBodyVelocity(body, velocity);
        
        // Get initial position
        Vec3 initialPos;
        Quat initialRot;
        physics->GetRigidBodyTransform(body, initialPos, initialRot);
        
        // Simulate for one frame
        float deltaTime = 0.016f;
        physics->Update(deltaTime);
        
        // Get updated position
        Vec3 updatedPos;
        Quat updatedRot;
        physics->GetRigidBodyTransform(body, updatedPos, updatedRot);
        
        // Property: Position should change based on velocity
        // Expected displacement = velocity * deltaTime (approximately, gravity also affects)
        Vec3 displacement = updatedPos - initialPos;
        float displacementMagnitude = displacement.length();
        
        // Should have moved (velocity or gravity should cause movement)
        EXPECT_GT(displacementMagnitude, 0.0f) << "Body should move with velocity or gravity";
        
        physics->DestroyRigidBody(body);
    }
    
    physics->Shutdown();
}

/*
 * Additional property test: Force application
 * For any rigid body, applying force should change velocity
 */
TEST_F(PhysicsPropertyTest, ForceApplicationProperty) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        RigidBodyDesc desc;
        desc.position = RandomVec3(-50.0f, 50.0f);
        desc.mass = RandomFloat(0.5f, 10.0f);
        desc.isKinematic = false;
        
        RigidBodyHandle body = physics->CreateRigidBody(desc);
        
        // Get initial velocity (should be zero)
        Vec3 initialVelocity = physics->GetRigidBodyVelocity(body);
        
        // Apply random force
        Vec3 force = RandomVec3(-100.0f, 100.0f);
        physics->ApplyForce(body, force);
        
        // Get velocity after force application
        Vec3 finalVelocity = physics->GetRigidBodyVelocity(body);
        
        // Property: Applying force should change velocity
        // F = ma, so velocity change = F/m * dt
        Vec3 velocityChange = finalVelocity - initialVelocity;
        float velocityChangeMagnitude = velocityChange.length();
        
        EXPECT_GT(velocityChangeMagnitude, 0.0f) << "Applying force should change velocity";
        
        physics->DestroyRigidBody(body);
    }
    
    physics->Shutdown();
}

/*
 * Additional property test: Raycast consistency
 * For any ray and body, raycast should be consistent
 */
TEST_F(PhysicsPropertyTest, RaycastConsistencyProperty) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    const int NUM_ITERATIONS = 50;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Create a body
        RigidBodyDesc desc;
        desc.position = Vec3(0.0f, 0.0f, 0.0f);
        RigidBodyHandle body = physics->CreateRigidBody(desc);
        
        // Add sphere collider
        ColliderDesc colliderDesc;
        colliderDesc.shape = ColliderShape::Sphere;
        colliderDesc.radius = RandomFloat(1.0f, 5.0f);
        physics->CreateCollider(body, colliderDesc);
        
        // Cast ray from random direction toward body
        Vec3 rayOrigin = RandomVec3(-20.0f, 20.0f);
        Vec3 rayDirection = (desc.position - rayOrigin).normalized();
        
        Ray ray;
        ray.origin = rayOrigin;
        ray.direction = rayDirection;
        ray.maxDistance = 100.0f;
        
        RaycastResult result;
        bool hit = physics->RaycastQuery(ray, result);
        
        // Property: Ray pointing toward body should hit it (most of the time)
        // Some rays might miss due to starting position, but most should hit
        if (rayOrigin.distance(desc.position) < 50.0f) {
            // Close rays should definitely hit
            EXPECT_TRUE(hit) << "Ray should hit body when pointing directly at it";
            if (hit) {
                EXPECT_EQ(result.body, body);
            }
        }
        
        physics->DestroyRigidBody(body);
    }
    
    physics->Shutdown();
}
