#pragma once

#include "pywrkgame/physics/PhysicsMath.h"
#include <memory>
#include <vector>

namespace pywrkgame {
namespace physics {

// Physics backend types
enum class PhysicsBackend {
    Bullet3,    // 3D physics
    Box2D,      // 2D physics
    Custom
};

// Handle types for physics objects
using RigidBodyHandle = uint32_t;
using ColliderHandle = uint32_t;
using SoftBodyHandle = uint32_t;
using FluidHandle = uint32_t;
using ClothHandle = uint32_t;

// Invalid handle constant
constexpr uint32_t INVALID_HANDLE = 0xFFFFFFFF;

// Rigid body descriptor
struct RigidBodyDesc {
    Vec3 position{0.0f, 0.0f, 0.0f};
    Quat rotation = Quat::identity();
    float mass = 1.0f;
    bool isKinematic = false;
    bool is2D = false;  // For 2D physics
};

// Collider shapes
enum class ColliderShape {
    Box,
    Sphere,
    Capsule,
    Mesh,
    Plane
};

// Collider descriptor
struct ColliderDesc {
    ColliderShape shape = ColliderShape::Box;
    Vec3 size{1.0f, 1.0f, 1.0f};  // For box, sphere radius in x
    float radius = 0.5f;   // For sphere/capsule
    float height = 1.0f;   // For capsule
};

// Soft body descriptor
struct SoftBodyDesc {
    std::vector<Vec3> vertices;
    std::vector<uint32_t> indices;
    float mass = 1.0f;
    float stiffness = 0.5f;
    float damping = 0.1f;
};

// Fluid descriptor
struct FluidDesc {
    Vec3 position{0.0f, 0.0f, 0.0f};
    Vec3 size{10.0f, 10.0f, 10.0f};
    int particleCount = 1000;
    float viscosity = 0.1f;
    float density = 1.0f;
    float surfaceTension = 0.5f;
};

// Cloth descriptor
struct ClothDesc {
    Vec3 position{0.0f, 0.0f, 0.0f};
    Vec2 size{10.0f, 10.0f};
    int resolutionX = 20;
    int resolutionY = 20;
    float mass = 1.0f;
    float stiffness = 0.8f;
    float damping = 0.2f;
    bool fixedCorners = true;
};

// Collision callback
struct CollisionInfo {
    RigidBodyHandle bodyA;
    RigidBodyHandle bodyB;
    Vec3 contactPoint;
    Vec3 contactNormal;
    float penetrationDepth;
};

using CollisionCallback = void(*)(const CollisionInfo& info);

// Ray for raycasting
struct Ray {
    Vec3 origin;
    Vec3 direction;
    float maxDistance = 1000.0f;
};

// Raycast result
struct RaycastResult {
    bool hit = false;
    RigidBodyHandle body = INVALID_HANDLE;
    Vec3 hitPoint;
    Vec3 hitNormal;
    float distance = 0.0f;
};

// Abstract physics backend interface
class IPhysicsBackend {
public:
    virtual ~IPhysicsBackend() = default;
    
    virtual bool Initialize() = 0;
    virtual void Update(float deltaTime) = 0;
    virtual void Shutdown() = 0;
    
    virtual RigidBodyHandle CreateRigidBody(const RigidBodyDesc& desc) = 0;
    virtual void DestroyRigidBody(RigidBodyHandle handle) = 0;
    virtual void SetRigidBodyTransform(RigidBodyHandle handle, const Vec3& position, const Quat& rotation) = 0;
    virtual void GetRigidBodyTransform(RigidBodyHandle handle, Vec3& position, Quat& rotation) = 0;
    virtual void SetRigidBodyVelocity(RigidBodyHandle handle, const Vec3& velocity) = 0;
    virtual Vec3 GetRigidBodyVelocity(RigidBodyHandle handle) = 0;
    virtual void ApplyForce(RigidBodyHandle handle, const Vec3& force) = 0;
    virtual void ApplyImpulse(RigidBodyHandle handle, const Vec3& impulse) = 0;
    
    virtual ColliderHandle CreateCollider(RigidBodyHandle body, const ColliderDesc& desc) = 0;
    virtual void DestroyCollider(ColliderHandle handle) = 0;
    
    virtual SoftBodyHandle CreateSoftBody(const SoftBodyDesc& desc) = 0;
    virtual void DestroySoftBody(SoftBodyHandle handle) = 0;
    virtual void GetSoftBodyVertices(SoftBodyHandle handle, std::vector<Vec3>& vertices) = 0;
    
    virtual FluidHandle CreateFluid(const FluidDesc& desc) = 0;
    virtual void DestroyFluid(FluidHandle handle) = 0;
    virtual void GetFluidParticles(FluidHandle handle, std::vector<Vec3>& particles) = 0;
    
    virtual ClothHandle CreateCloth(const ClothDesc& desc) = 0;
    virtual void DestroyCloth(ClothHandle handle) = 0;
    virtual void GetClothVertices(ClothHandle handle, std::vector<Vec3>& vertices) = 0;
    virtual void AttachClothToBody(ClothHandle cloth, RigidBodyHandle body, const Vec3& offset) = 0;
    
    virtual void SetCollisionCallback(CollisionCallback callback) = 0;
    virtual bool RaycastQuery(const Ray& ray, RaycastResult& result) = 0;
    virtual bool AreColliding(RigidBodyHandle bodyA, RigidBodyHandle bodyB) = 0;
    
    virtual void SetGravity(const Vec3& gravity) = 0;
    virtual Vec3 GetGravity() = 0;
};

// Main physics engine class
class PhysicsEngine {
public:
    PhysicsEngine();
    ~PhysicsEngine();

    // Initialization with backend selection
    bool Initialize(PhysicsBackend backend = PhysicsBackend::Bullet3);
    void Update(float deltaTime);
    void Shutdown();
    
    // Rigid body management
    RigidBodyHandle CreateRigidBody(const RigidBodyDesc& desc);
    void DestroyRigidBody(RigidBodyHandle handle);
    void SetRigidBodyTransform(RigidBodyHandle handle, const Vec3& position, const Quat& rotation);
    void GetRigidBodyTransform(RigidBodyHandle handle, Vec3& position, Quat& rotation);
    void SetRigidBodyVelocity(RigidBodyHandle handle, const Vec3& velocity);
    Vec3 GetRigidBodyVelocity(RigidBodyHandle handle);
    void ApplyForce(RigidBodyHandle handle, const Vec3& force);
    void ApplyImpulse(RigidBodyHandle handle, const Vec3& impulse);
    
    // Collider management
    ColliderHandle CreateCollider(RigidBodyHandle body, const ColliderDesc& desc);
    void DestroyCollider(ColliderHandle handle);
    
    // Soft body management
    SoftBodyHandle CreateSoftBody(const SoftBodyDesc& desc);
    void DestroySoftBody(SoftBodyHandle handle);
    void GetSoftBodyVertices(SoftBodyHandle handle, std::vector<Vec3>& vertices);
    
    // Fluid simulation
    FluidHandle CreateFluid(const FluidDesc& desc);
    void DestroyFluid(FluidHandle handle);
    void GetFluidParticles(FluidHandle handle, std::vector<Vec3>& particles);
    
    // Cloth simulation
    ClothHandle CreateCloth(const ClothDesc& desc);
    void DestroyCloth(ClothHandle handle);
    void GetClothVertices(ClothHandle handle, std::vector<Vec3>& vertices);
    void AttachClothToBody(ClothHandle cloth, RigidBodyHandle body, const Vec3& offset);
    
    // Collision detection
    void SetCollisionCallback(CollisionCallback callback);
    bool RaycastQuery(const Ray& ray, RaycastResult& result);
    bool AreColliding(RigidBodyHandle bodyA, RigidBodyHandle bodyB);
    
    // Physics settings
    void SetGravity(const Vec3& gravity);
    Vec3 GetGravity();
    
    // Query methods
    bool IsInitialized() const { return initialized; }
    PhysicsBackend GetBackend() const { return currentBackend; }

private:
    bool initialized = false;
    PhysicsBackend currentBackend = PhysicsBackend::Bullet3;
    std::unique_ptr<IPhysicsBackend> backend;
};

} // namespace physics
} // namespace pywrkgame