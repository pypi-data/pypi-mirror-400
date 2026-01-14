#include "pywrkgame/physics/PhysicsEngine.h"
#include "pywrkgame/physics/Bullet3Backend.h"
#include "pywrkgame/physics/Box2DBackend.h"

namespace pywrkgame {
namespace physics {

PhysicsEngine::PhysicsEngine() = default;

PhysicsEngine::~PhysicsEngine() {
    if (initialized) {
        Shutdown();
    }
}

bool PhysicsEngine::Initialize(PhysicsBackend backendType) {
    if (initialized) {
        return false;
    }
    
    currentBackend = backendType;
    
    // Create appropriate backend
    switch (backendType) {
        case PhysicsBackend::Bullet3:
            backend = std::make_unique<Bullet3Backend>();
            break;
        case PhysicsBackend::Box2D:
            backend = std::make_unique<Box2DBackend>();
            break;
        case PhysicsBackend::Custom:
            // Custom backend would be set externally
            return false;
        default:
            return false;
    }
    
    if (!backend->Initialize()) {
        backend.reset();
        return false;
    }
    
    initialized = true;
    return true;
}

void PhysicsEngine::Update(float deltaTime) {
    if (!initialized || !backend) return;
    backend->Update(deltaTime);
}

void PhysicsEngine::Shutdown() {
    if (!initialized) return;
    
    if (backend) {
        backend->Shutdown();
        backend.reset();
    }
    
    initialized = false;
}

// Rigid body management
RigidBodyHandle PhysicsEngine::CreateRigidBody(const RigidBodyDesc& desc) {
    if (!initialized || !backend) return INVALID_HANDLE;
    return backend->CreateRigidBody(desc);
}

void PhysicsEngine::DestroyRigidBody(RigidBodyHandle handle) {
    if (!initialized || !backend) return;
    backend->DestroyRigidBody(handle);
}

void PhysicsEngine::SetRigidBodyTransform(RigidBodyHandle handle, const Vec3& position, const Quat& rotation) {
    if (!initialized || !backend) return;
    backend->SetRigidBodyTransform(handle, position, rotation);
}

void PhysicsEngine::GetRigidBodyTransform(RigidBodyHandle handle, Vec3& position, Quat& rotation) {
    if (!initialized || !backend) return;
    backend->GetRigidBodyTransform(handle, position, rotation);
}

void PhysicsEngine::SetRigidBodyVelocity(RigidBodyHandle handle, const Vec3& velocity) {
    if (!initialized || !backend) return;
    backend->SetRigidBodyVelocity(handle, velocity);
}

Vec3 PhysicsEngine::GetRigidBodyVelocity(RigidBodyHandle handle) {
    if (!initialized || !backend) return Vec3(0.0f, 0.0f, 0.0f);
    return backend->GetRigidBodyVelocity(handle);
}

void PhysicsEngine::ApplyForce(RigidBodyHandle handle, const Vec3& force) {
    if (!initialized || !backend) return;
    backend->ApplyForce(handle, force);
}

void PhysicsEngine::ApplyImpulse(RigidBodyHandle handle, const Vec3& impulse) {
    if (!initialized || !backend) return;
    backend->ApplyImpulse(handle, impulse);
}

// Collider management
ColliderHandle PhysicsEngine::CreateCollider(RigidBodyHandle body, const ColliderDesc& desc) {
    if (!initialized || !backend) return INVALID_HANDLE;
    return backend->CreateCollider(body, desc);
}

void PhysicsEngine::DestroyCollider(ColliderHandle handle) {
    if (!initialized || !backend) return;
    backend->DestroyCollider(handle);
}

// Soft body management
SoftBodyHandle PhysicsEngine::CreateSoftBody(const SoftBodyDesc& desc) {
    if (!initialized || !backend) return INVALID_HANDLE;
    return backend->CreateSoftBody(desc);
}

void PhysicsEngine::DestroySoftBody(SoftBodyHandle handle) {
    if (!initialized || !backend) return;
    backend->DestroySoftBody(handle);
}

void PhysicsEngine::GetSoftBodyVertices(SoftBodyHandle handle, std::vector<Vec3>& vertices) {
    if (!initialized || !backend) return;
    backend->GetSoftBodyVertices(handle, vertices);
}

// Fluid simulation
FluidHandle PhysicsEngine::CreateFluid(const FluidDesc& desc) {
    if (!initialized || !backend) return INVALID_HANDLE;
    return backend->CreateFluid(desc);
}

void PhysicsEngine::DestroyFluid(FluidHandle handle) {
    if (!initialized || !backend) return;
    backend->DestroyFluid(handle);
}

void PhysicsEngine::GetFluidParticles(FluidHandle handle, std::vector<Vec3>& particles) {
    if (!initialized || !backend) return;
    backend->GetFluidParticles(handle, particles);
}

// Cloth simulation
ClothHandle PhysicsEngine::CreateCloth(const ClothDesc& desc) {
    if (!initialized || !backend) return INVALID_HANDLE;
    return backend->CreateCloth(desc);
}

void PhysicsEngine::DestroyCloth(ClothHandle handle) {
    if (!initialized || !backend) return;
    backend->DestroyCloth(handle);
}

void PhysicsEngine::GetClothVertices(ClothHandle handle, std::vector<Vec3>& vertices) {
    if (!initialized || !backend) return;
    backend->GetClothVertices(handle, vertices);
}

void PhysicsEngine::AttachClothToBody(ClothHandle cloth, RigidBodyHandle body, const Vec3& offset) {
    if (!initialized || !backend) return;
    backend->AttachClothToBody(cloth, body, offset);
}

// Collision detection
void PhysicsEngine::SetCollisionCallback(CollisionCallback callback) {
    if (!initialized || !backend) return;
    backend->SetCollisionCallback(callback);
}

bool PhysicsEngine::RaycastQuery(const Ray& ray, RaycastResult& result) {
    if (!initialized || !backend) return false;
    return backend->RaycastQuery(ray, result);
}

bool PhysicsEngine::AreColliding(RigidBodyHandle bodyA, RigidBodyHandle bodyB) {
    if (!initialized || !backend) return false;
    return backend->AreColliding(bodyA, bodyB);
}

// Physics settings
void PhysicsEngine::SetGravity(const Vec3& gravity) {
    if (!initialized || !backend) return;
    backend->SetGravity(gravity);
}

Vec3 PhysicsEngine::GetGravity() {
    if (!initialized || !backend) return Vec3(0.0f, 0.0f, 0.0f);
    return backend->GetGravity();
}

} // namespace physics
} // namespace pywrkgame