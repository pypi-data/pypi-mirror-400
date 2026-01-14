#pragma once

#include "pywrkgame/physics/PhysicsEngine.h"
#include <unordered_map>

namespace pywrkgame {
namespace physics {

// Bullet3 backend implementation for 3D physics
class Bullet3Backend : public IPhysicsBackend {
public:
    Bullet3Backend();
    ~Bullet3Backend() override;
    
    bool Initialize() override;
    void Update(float deltaTime) override;
    void Shutdown() override;
    
    RigidBodyHandle CreateRigidBody(const RigidBodyDesc& desc) override;
    void DestroyRigidBody(RigidBodyHandle handle) override;
    void SetRigidBodyTransform(RigidBodyHandle handle, const Vec3& position, const Quat& rotation) override;
    void GetRigidBodyTransform(RigidBodyHandle handle, Vec3& position, Quat& rotation) override;
    void SetRigidBodyVelocity(RigidBodyHandle handle, const Vec3& velocity) override;
    Vec3 GetRigidBodyVelocity(RigidBodyHandle handle) override;
    void ApplyForce(RigidBodyHandle handle, const Vec3& force) override;
    void ApplyImpulse(RigidBodyHandle handle, const Vec3& impulse) override;
    
    ColliderHandle CreateCollider(RigidBodyHandle body, const ColliderDesc& desc) override;
    void DestroyCollider(ColliderHandle handle) override;
    
    SoftBodyHandle CreateSoftBody(const SoftBodyDesc& desc) override;
    void DestroySoftBody(SoftBodyHandle handle) override;
    void GetSoftBodyVertices(SoftBodyHandle handle, std::vector<Vec3>& vertices) override;
    
    FluidHandle CreateFluid(const FluidDesc& desc) override;
    void DestroyFluid(FluidHandle handle) override;
    void GetFluidParticles(FluidHandle handle, std::vector<Vec3>& particles) override;
    
    ClothHandle CreateCloth(const ClothDesc& desc) override;
    void DestroyCloth(ClothHandle handle) override;
    void GetClothVertices(ClothHandle handle, std::vector<Vec3>& vertices) override;
    void AttachClothToBody(ClothHandle cloth, RigidBodyHandle body, const Vec3& offset) override;
    
    void SetCollisionCallback(CollisionCallback callback) override;
    bool RaycastQuery(const Ray& ray, RaycastResult& result) override;
    bool AreColliding(RigidBodyHandle bodyA, RigidBodyHandle bodyB) override;
    
    void SetGravity(const Vec3& gravity) override;
    Vec3 GetGravity() override;

private:
    struct RigidBodyData {
        Vec3 position;
        Quat rotation;
        Vec3 velocity;
        float mass;
        bool isKinematic;
    };
    
    struct SoftBodyData {
        std::vector<Vec3> vertices;
        std::vector<uint32_t> indices;
        float mass;
        float stiffness;
        float damping;
    };
    
    struct FluidData {
        std::vector<Vec3> particles;
        std::vector<Vec3> velocities;
        float viscosity;
        float density;
        float surfaceTension;
    };
    
    struct ClothData {
        std::vector<Vec3> vertices;
        std::vector<uint32_t> indices;
        int resolutionX;
        int resolutionY;
        float mass;
        float stiffness;
        float damping;
        std::vector<bool> fixedVertices;
        RigidBodyHandle attachedBody = INVALID_HANDLE;
        Vec3 attachmentOffset;
    };
    
    uint32_t nextHandle = 1;
    std::unordered_map<RigidBodyHandle, RigidBodyData> rigidBodies;
    std::unordered_map<SoftBodyHandle, SoftBodyData> softBodies;
    std::unordered_map<FluidHandle, FluidData> fluids;
    std::unordered_map<ClothHandle, ClothData> cloths;
    std::unordered_map<ColliderHandle, ColliderDesc> colliders;
    std::unordered_map<ColliderHandle, RigidBodyHandle> colliderToBody;
    
    Vec3 gravity{0.0f, -9.81f, 0.0f};
    CollisionCallback collisionCallback = nullptr;
    
    RigidBodyHandle AllocateHandle();
    bool CheckCollision(RigidBodyHandle bodyA, RigidBodyHandle bodyB);
};

} // namespace physics
} // namespace pywrkgame
