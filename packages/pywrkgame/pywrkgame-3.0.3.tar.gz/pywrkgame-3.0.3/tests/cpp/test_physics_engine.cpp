#include <gtest/gtest.h>
#include "pywrkgame/physics/PhysicsEngine.h"

using namespace pywrkgame::physics;

class PhysicsEngineTest : public ::testing::Test {
protected:
    void SetUp() override {
        physics = std::make_unique<PhysicsEngine>();
    }
    
    std::unique_ptr<PhysicsEngine> physics;
};

TEST_F(PhysicsEngineTest, InitializeAndShutdown) {
    EXPECT_TRUE(physics->Initialize());
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, UpdateOperation) {
    EXPECT_TRUE(physics->Initialize());
    
    // Should not crash
    EXPECT_NO_THROW(physics->Update(0.016f));
}

TEST_F(PhysicsEngineTest, InitializeWithBullet3Backend) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    EXPECT_TRUE(physics->IsInitialized());
    EXPECT_EQ(physics->GetBackend(), PhysicsBackend::Bullet3);
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, InitializeWithBox2DBackend) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Box2D));
    EXPECT_TRUE(physics->IsInitialized());
    EXPECT_EQ(physics->GetBackend(), PhysicsBackend::Box2D);
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, CreateAndDestroyRigidBody) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    RigidBodyDesc desc;
    desc.position = Vec3(0.0f, 10.0f, 0.0f);
    desc.mass = 1.0f;
    
    RigidBodyHandle body = physics->CreateRigidBody(desc);
    EXPECT_NE(body, INVALID_HANDLE);
    
    physics->DestroyRigidBody(body);
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, RigidBodyTransform) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    RigidBodyDesc desc;
    desc.position = Vec3(1.0f, 2.0f, 3.0f);
    
    RigidBodyHandle body = physics->CreateRigidBody(desc);
    
    Vec3 position;
    Quat rotation;
    physics->GetRigidBodyTransform(body, position, rotation);
    
    EXPECT_FLOAT_EQ(position.x, 1.0f);
    EXPECT_FLOAT_EQ(position.y, 2.0f);
    EXPECT_FLOAT_EQ(position.z, 3.0f);
    
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, RigidBodyVelocity) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    RigidBodyDesc desc;
    RigidBodyHandle body = physics->CreateRigidBody(desc);
    
    Vec3 velocity(5.0f, 0.0f, 0.0f);
    physics->SetRigidBodyVelocity(body, velocity);
    
    Vec3 retrievedVelocity = physics->GetRigidBodyVelocity(body);
    EXPECT_FLOAT_EQ(retrievedVelocity.x, 5.0f);
    
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, CreateCollider) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    RigidBodyDesc bodyDesc;
    RigidBodyHandle body = physics->CreateRigidBody(bodyDesc);
    
    ColliderDesc colliderDesc;
    colliderDesc.shape = ColliderShape::Box;
    colliderDesc.size = Vec3(1.0f, 1.0f, 1.0f);
    
    ColliderHandle collider = physics->CreateCollider(body, colliderDesc);
    EXPECT_NE(collider, INVALID_HANDLE);
    
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, GravitySetting) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    Vec3 customGravity(0.0f, -20.0f, 0.0f);
    physics->SetGravity(customGravity);
    
    Vec3 retrievedGravity = physics->GetGravity();
    EXPECT_FLOAT_EQ(retrievedGravity.y, -20.0f);
    
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, CreateSoftBody) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    SoftBodyDesc desc;
    desc.vertices = {
        Vec3(0.0f, 0.0f, 0.0f),
        Vec3(1.0f, 0.0f, 0.0f),
        Vec3(0.0f, 1.0f, 0.0f)
    };
    desc.indices = {0, 1, 2};
    desc.mass = 1.0f;
    
    SoftBodyHandle softBody = physics->CreateSoftBody(desc);
    EXPECT_NE(softBody, INVALID_HANDLE);
    
    std::vector<Vec3> vertices;
    physics->GetSoftBodyVertices(softBody, vertices);
    EXPECT_EQ(vertices.size(), 3);
    
    physics->Shutdown();
}

TEST_F(PhysicsEngineTest, RaycastQuery) {
    EXPECT_TRUE(physics->Initialize(PhysicsBackend::Bullet3));
    
    // Create a body at origin
    RigidBodyDesc bodyDesc;
    bodyDesc.position = Vec3(0.0f, 0.0f, 0.0f);
    RigidBodyHandle body = physics->CreateRigidBody(bodyDesc);
    
    // Create a sphere collider
    ColliderDesc colliderDesc;
    colliderDesc.shape = ColliderShape::Sphere;
    colliderDesc.radius = 1.0f;
    physics->CreateCollider(body, colliderDesc);
    
    // Cast a ray that should hit
    Ray ray;
    ray.origin = Vec3(-5.0f, 0.0f, 0.0f);
    ray.direction = Vec3(1.0f, 0.0f, 0.0f);
    ray.maxDistance = 10.0f;
    
    RaycastResult result;
    bool hit = physics->RaycastQuery(ray, result);
    
    EXPECT_TRUE(hit);
    EXPECT_EQ(result.body, body);
    
    physics->Shutdown();
}