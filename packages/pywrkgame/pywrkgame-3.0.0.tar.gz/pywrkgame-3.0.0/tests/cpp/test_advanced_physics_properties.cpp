#include <gtest/gtest.h>
#include "pywrkgame/physics/PhysicsEngine.h"
#include <random>
#include <vector>

using namespace pywrkgame::physics;

// Property-based test helper class for advanced physics
class AdvancedPhysicsPropertyTest : public ::testing::Test {
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
    
    // Generate random int within range
    int RandomInt(int min, int max) {
        std::uniform_int_distribution<int> dist(min, max);
        return dist(rng);
    }
    
    std::unique_ptr<PhysicsEngine> physics;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 29: Fluid Simulation Realism
 * For any fluid simulation, behavior should follow realistic fluid dynamics principles
 * Validates: Requirements 6.3
 */
TEST_F(AdvancedPhysicsPropertyTest, Property29_FluidSimulationRealism) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    // Run property test with multiple random fluid configurations
    const int NUM_ITERATIONS = 50;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Create a random fluid
        FluidDesc desc;
        desc.position = RandomVec3(-10.0f, 10.0f);
        desc.size = Vec3(RandomFloat(5.0f, 20.0f), RandomFloat(5.0f, 20.0f), RandomFloat(5.0f, 20.0f));
        desc.particleCount = RandomInt(100, 1000);
        desc.viscosity = RandomFloat(0.01f, 1.0f);
        desc.density = RandomFloat(0.5f, 2.0f);
        desc.surfaceTension = RandomFloat(0.1f, 1.0f);
        
        FluidHandle fluid = physics->CreateFluid(desc);
        ASSERT_NE(fluid, INVALID_HANDLE);
        
        // Get initial particle positions
        std::vector<Vec3> initialParticles;
        physics->GetFluidParticles(fluid, initialParticles);
        EXPECT_GT(initialParticles.size(), 0) << "Fluid should have particles";
        
        // Simulate for several frames
        for (int frame = 0; frame < 20; ++frame) {
            physics->Update(0.016f);
        }
        
        // Get updated particle positions
        std::vector<Vec3> updatedParticles;
        physics->GetFluidParticles(fluid, updatedParticles);
        
        // Property: Fluid particles should move under gravity
        // At least some particles should have moved downward
        int particlesMoved = 0;
        for (size_t p = 0; p < initialParticles.size() && p < updatedParticles.size(); ++p) {
            float verticalDisplacement = updatedParticles[p].y - initialParticles[p].y;
            if (verticalDisplacement < -0.1f) { // Moved down
                particlesMoved++;
            }
        }
        
        // Most particles should move downward due to gravity
        float movementRatio = static_cast<float>(particlesMoved) / initialParticles.size();
        EXPECT_GT(movementRatio, 0.5f) << "Most fluid particles should move downward under gravity";
        
        // Property: Particle count should remain constant
        EXPECT_EQ(initialParticles.size(), updatedParticles.size()) 
            << "Fluid particle count should remain constant";
        
        physics->DestroyFluid(fluid);
    }
    
    physics->Shutdown();
}

/*
 * Feature: pywrkgame-library, Property 33: Cloth and Hair Simulation
 * For any cloth or hair simulation, behavior should be realistic and respond correctly to forces
 * Validates: Requirements 6.7
 */
TEST_F(AdvancedPhysicsPropertyTest, Property33_ClothSimulation) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    // Run property test with multiple random cloth configurations
    const int NUM_ITERATIONS = 50;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Create a random cloth
        ClothDesc desc;
        desc.position = RandomVec3(-10.0f, 10.0f);
        desc.size = Vec2(RandomFloat(5.0f, 15.0f), RandomFloat(5.0f, 15.0f));
        desc.resolutionX = RandomInt(5, 20);
        desc.resolutionY = RandomInt(5, 20);
        desc.mass = RandomFloat(0.5f, 5.0f);
        desc.stiffness = RandomFloat(0.3f, 1.0f);
        desc.damping = RandomFloat(0.05f, 0.5f);
        desc.fixedCorners = (i % 2 == 0); // Alternate between fixed and free
        
        ClothHandle cloth = physics->CreateCloth(desc);
        ASSERT_NE(cloth, INVALID_HANDLE);
        
        // Get initial vertex positions
        std::vector<Vec3> initialVertices;
        physics->GetClothVertices(cloth, initialVertices);
        int expectedVertexCount = desc.resolutionX * desc.resolutionY;
        EXPECT_EQ(initialVertices.size(), expectedVertexCount) 
            << "Cloth should have correct number of vertices";
        
        // Simulate for several frames
        for (int frame = 0; frame < 20; ++frame) {
            physics->Update(0.016f);
        }
        
        // Get updated vertex positions
        std::vector<Vec3> updatedVertices;
        physics->GetClothVertices(cloth, updatedVertices);
        
        // Property: Cloth vertices should move under gravity (except fixed ones)
        int verticesMoved = 0;
        for (size_t v = 0; v < initialVertices.size() && v < updatedVertices.size(); ++v) {
            float displacement = initialVertices[v].distance(updatedVertices[v]);
            if (displacement > 0.01f) {
                verticesMoved++;
            }
        }
        
        // At least some vertices should move (unless all are fixed)
        if (!desc.fixedCorners || desc.resolutionX * desc.resolutionY > 4) {
            EXPECT_GT(verticesMoved, 0) << "Some cloth vertices should move under physics simulation";
        }
        
        // Property: Vertex count should remain constant
        EXPECT_EQ(initialVertices.size(), updatedVertices.size()) 
            << "Cloth vertex count should remain constant";
        
        physics->DestroyCloth(cloth);
    }
    
    physics->Shutdown();
}

/*
 * Additional property test: Cloth attachment to rigid body
 * For any cloth attached to a rigid body, the attachment point should follow the body
 */
TEST_F(AdvancedPhysicsPropertyTest, ClothAttachmentProperty) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    const int NUM_ITERATIONS = 30;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Create a rigid body
        RigidBodyDesc bodyDesc;
        bodyDesc.position = RandomVec3(-10.0f, 10.0f);
        bodyDesc.mass = RandomFloat(1.0f, 10.0f);
        bodyDesc.isKinematic = true; // Make it kinematic so we can control it
        
        RigidBodyHandle body = physics->CreateRigidBody(bodyDesc);
        
        // Create a cloth
        ClothDesc clothDesc;
        clothDesc.position = bodyDesc.position + Vec3(0.0f, -2.0f, 0.0f);
        clothDesc.size = Vec2(5.0f, 5.0f);
        clothDesc.resolutionX = 10;
        clothDesc.resolutionY = 10;
        clothDesc.fixedCorners = false;
        
        ClothHandle cloth = physics->CreateCloth(clothDesc);
        
        // Attach cloth to body
        Vec3 attachmentOffset(0.0f, 0.0f, 0.0f);
        physics->AttachClothToBody(cloth, body, attachmentOffset);
        
        // Move the body
        Vec3 newPosition = bodyDesc.position + RandomVec3(-5.0f, 5.0f);
        physics->SetRigidBodyTransform(body, newPosition, Quat::identity());
        
        // Simulate for a few frames
        for (int frame = 0; frame < 5; ++frame) {
            physics->Update(0.016f);
        }
        
        // Get cloth vertices
        std::vector<Vec3> vertices;
        physics->GetClothVertices(cloth, vertices);
        
        // Property: First vertex (attachment point) should be near the body position
        if (!vertices.empty()) {
            float distance = vertices[0].distance(newPosition + attachmentOffset);
            EXPECT_LT(distance, 1.0f) << "Attached cloth vertex should follow the rigid body";
        }
        
        physics->DestroyCloth(cloth);
        physics->DestroyRigidBody(body);
    }
    
    physics->Shutdown();
}

/*
 * Additional property test: Fluid particle conservation
 * For any fluid, the number of particles should remain constant throughout simulation
 */
TEST_F(AdvancedPhysicsPropertyTest, FluidParticleConservationProperty) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    const int NUM_ITERATIONS = 30;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        FluidDesc desc;
        desc.position = RandomVec3(-10.0f, 10.0f);
        desc.size = Vec3(10.0f, 10.0f, 10.0f);
        desc.particleCount = RandomInt(100, 500);
        desc.viscosity = RandomFloat(0.1f, 0.5f);
        
        FluidHandle fluid = physics->CreateFluid(desc);
        
        // Get initial particle count
        std::vector<Vec3> particles;
        physics->GetFluidParticles(fluid, particles);
        size_t initialCount = particles.size();
        
        // Simulate for many frames
        for (int frame = 0; frame < 100; ++frame) {
            physics->Update(0.016f);
        }
        
        // Get final particle count
        particles.clear();
        physics->GetFluidParticles(fluid, particles);
        size_t finalCount = particles.size();
        
        // Property: Particle count must be conserved
        EXPECT_EQ(initialCount, finalCount) 
            << "Fluid simulation must conserve particle count";
        
        physics->DestroyFluid(fluid);
    }
    
    physics->Shutdown();
}

/*
 * Additional property test: Cloth structural integrity
 * For any cloth, the mesh structure should remain valid throughout simulation
 */
TEST_F(AdvancedPhysicsPropertyTest, ClothStructuralIntegrityProperty) {
    ASSERT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    const int NUM_ITERATIONS = 30;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        ClothDesc desc;
        desc.position = RandomVec3(-10.0f, 10.0f);
        desc.size = Vec2(10.0f, 10.0f);
        desc.resolutionX = RandomInt(5, 15);
        desc.resolutionY = RandomInt(5, 15);
        desc.mass = RandomFloat(1.0f, 5.0f);
        
        ClothHandle cloth = physics->CreateCloth(desc);
        
        int expectedVertexCount = desc.resolutionX * desc.resolutionY;
        
        // Simulate for many frames
        for (int frame = 0; frame < 100; ++frame) {
            physics->Update(0.016f);
            
            // Check vertex count periodically
            if (frame % 20 == 0) {
                std::vector<Vec3> vertices;
                physics->GetClothVertices(cloth, vertices);
                
                // Property: Vertex count must remain constant
                EXPECT_EQ(vertices.size(), expectedVertexCount) 
                    << "Cloth must maintain structural integrity (constant vertex count)";
            }
        }
        
        physics->DestroyCloth(cloth);
    }
    
    physics->Shutdown();
}
