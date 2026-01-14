#include "pywrkgame/physics/Box2DBackend.h"
#include <cmath>

namespace pywrkgame {
namespace physics {

Box2DBackend::Box2DBackend() = default;

Box2DBackend::~Box2DBackend() {
    Shutdown();
}

bool Box2DBackend::Initialize() {
    // Initialize Box2D physics world (simplified implementation)
    return true;
}

void Box2DBackend::Update(float deltaTime) {
    // Update all 2D rigid bodies
    for (auto& [handle, body] : rigidBodies) {
        if (!body.isKinematic) {
            // Apply gravity (only Y component for 2D)
            body.velocity.y += gravity.y * deltaTime;
            
            // Update position
            body.position = body.position + body.velocity * deltaTime;
        }
    }
    
    // Check for collisions and invoke callback if set
    if (collisionCallback) {
        std::vector<RigidBodyHandle> handles;
        for (const auto& [handle, _] : rigidBodies) {
            handles.push_back(handle);
        }
        
        for (size_t i = 0; i < handles.size(); ++i) {
            for (size_t j = i + 1; j < handles.size(); ++j) {
                if (CheckCollision2D(handles[i], handles[j])) {
                    CollisionInfo info;
                    info.bodyA = handles[i];
                    info.bodyB = handles[j];
                    Vec2 posA = rigidBodies[handles[i]].position;
                    Vec2 posB = rigidBodies[handles[j]].position;
                    Vec2 contact2D = (posA + posB) * 0.5f;
                    info.contactPoint = Vec3(contact2D.x, contact2D.y, 0.0f);
                    Vec2 normal2D = (posB - posA).normalized();
                    info.contactNormal = Vec3(normal2D.x, normal2D.y, 0.0f);
                    info.penetrationDepth = 0.1f;
                    collisionCallback(info);
                }
            }
        }
    }
}

void Box2DBackend::Shutdown() {
    rigidBodies.clear();
    colliders.clear();
    colliderToBody.clear();
}

RigidBodyHandle Box2DBackend::CreateRigidBody(const RigidBodyDesc& desc) {
    RigidBodyHandle handle = AllocateHandle();
    
    RigidBody2D data;
    data.position = Vec2(desc.position.x, desc.position.y);
    data.rotation = 0.0f; // Extract rotation from quaternion if needed
    data.velocity = Vec2(0.0f, 0.0f);
    data.mass = desc.mass;
    data.isKinematic = desc.isKinematic;
    data.size = Vec2(1.0f, 1.0f); // Default size
    
    rigidBodies[handle] = data;
    return handle;
}

void Box2DBackend::DestroyRigidBody(RigidBodyHandle handle) {
    rigidBodies.erase(handle);
    
    // Remove associated colliders
    std::vector<ColliderHandle> toRemove;
    for (const auto& [colliderHandle, bodyHandle] : colliderToBody) {
        if (bodyHandle == handle) {
            toRemove.push_back(colliderHandle);
        }
    }
    for (auto colliderHandle : toRemove) {
        DestroyCollider(colliderHandle);
    }
}

void Box2DBackend::SetRigidBodyTransform(RigidBodyHandle handle, const Vec3& position, const Quat& rotation) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end()) {
        it->second.position = Vec2(position.x, position.y);
        // Convert quaternion to 2D rotation if needed
    }
}

void Box2DBackend::GetRigidBodyTransform(RigidBodyHandle handle, Vec3& position, Quat& rotation) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end()) {
        position = Vec3(it->second.position.x, it->second.position.y, 0.0f);
        rotation = Quat::identity(); // Identity for 2D
    }
}

void Box2DBackend::SetRigidBodyVelocity(RigidBodyHandle handle, const Vec3& velocity) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end()) {
        it->second.velocity = Vec2(velocity.x, velocity.y);
    }
}

Vec3 Box2DBackend::GetRigidBodyVelocity(RigidBodyHandle handle) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end()) {
        return Vec3(it->second.velocity.x, it->second.velocity.y, 0.0f);
    }
    return Vec3(0.0f, 0.0f, 0.0f);
}

void Box2DBackend::ApplyForce(RigidBodyHandle handle, const Vec3& force) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end() && !it->second.isKinematic) {
        Vec2 force2D(force.x, force.y);
        Vec2 acceleration = force2D / it->second.mass;
        it->second.velocity = it->second.velocity + acceleration * 0.016f; // Assume 60 FPS
    }
}

void Box2DBackend::ApplyImpulse(RigidBodyHandle handle, const Vec3& impulse) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end() && !it->second.isKinematic) {
        Vec2 impulse2D(impulse.x, impulse.y);
        it->second.velocity = it->second.velocity + impulse2D / it->second.mass;
    }
}

ColliderHandle Box2DBackend::CreateCollider(RigidBodyHandle body, const ColliderDesc& desc) {
    ColliderHandle handle = AllocateHandle();
    colliders[handle] = desc;
    colliderToBody[handle] = body;
    
    // Update body size based on collider
    auto bodyIt = rigidBodies.find(body);
    if (bodyIt != rigidBodies.end()) {
        if (desc.shape == ColliderShape::Box) {
            bodyIt->second.size = Vec2(desc.size.x, desc.size.y);
        } else if (desc.shape == ColliderShape::Sphere) {
            bodyIt->second.size = Vec2(desc.radius * 2.0f, desc.radius * 2.0f);
        }
    }
    
    return handle;
}

void Box2DBackend::DestroyCollider(ColliderHandle handle) {
    colliders.erase(handle);
    colliderToBody.erase(handle);
}

SoftBodyHandle Box2DBackend::CreateSoftBody(const SoftBodyDesc& desc) {
    // Soft bodies not supported in 2D backend
    return INVALID_HANDLE;
}

void Box2DBackend::DestroySoftBody(SoftBodyHandle handle) {
    // Not supported
}

void Box2DBackend::GetSoftBodyVertices(SoftBodyHandle handle, std::vector<Vec3>& vertices) {
    // Not supported
}

void Box2DBackend::SetCollisionCallback(CollisionCallback callback) {
    collisionCallback = callback;
}

bool Box2DBackend::RaycastQuery(const Ray& ray, RaycastResult& result) {
    result.hit = false;
    result.distance = ray.maxDistance;
    
    // Simple 2D raycast
    Vec2 rayOrigin2D(ray.origin.x, ray.origin.y);
    Vec2 rayDir2D(ray.direction.x, ray.direction.y);
    
    for (const auto& [handle, body] : rigidBodies) {
        // Simple circle collision for raycast
        float radius = body.size.length() * 0.5f;
        
        Vec2 oc = rayOrigin2D - body.position;
        float a = rayDir2D.dot(rayDir2D);
        float b = 2.0f * oc.dot(rayDir2D);
        float c = oc.dot(oc) - radius * radius;
        float discriminant = b * b - 4 * a * c;
        
        if (discriminant >= 0) {
            float t = (-b - std::sqrt(discriminant)) / (2.0f * a);
            if (t > 0 && t < result.distance) {
                result.hit = true;
                result.body = handle;
                result.distance = t;
                Vec2 hitPoint2D = rayOrigin2D + rayDir2D * t;
                result.hitPoint = Vec3(hitPoint2D.x, hitPoint2D.y, 0.0f);
                Vec2 normal2D = (hitPoint2D - body.position).normalized();
                result.hitNormal = Vec3(normal2D.x, normal2D.y, 0.0f);
            }
        }
    }
    
    return result.hit;
}

bool Box2DBackend::AreColliding(RigidBodyHandle bodyA, RigidBodyHandle bodyB) {
    return CheckCollision2D(bodyA, bodyB);
}

void Box2DBackend::SetGravity(const Vec3& g) {
    gravity = g;
}

Vec3 Box2DBackend::GetGravity() {
    return gravity;
}

RigidBodyHandle Box2DBackend::AllocateHandle() {
    return nextHandle++;
}

bool Box2DBackend::CheckCollision2D(RigidBodyHandle bodyA, RigidBodyHandle bodyB) {
    auto itA = rigidBodies.find(bodyA);
    auto itB = rigidBodies.find(bodyB);
    
    if (itA == rigidBodies.end() || itB == rigidBodies.end()) {
        return false;
    }
    
    const auto& bodyAData = itA->second;
    const auto& bodyBData = itB->second;
    
    // AABB collision detection
    Vec2 halfSizeA = bodyAData.size * 0.5f;
    Vec2 halfSizeB = bodyBData.size * 0.5f;
    
    bool collisionX = (bodyAData.position.x + halfSizeA.x >= bodyBData.position.x - halfSizeB.x) &&
                      (bodyBData.position.x + halfSizeB.x >= bodyAData.position.x - halfSizeA.x);
    
    bool collisionY = (bodyAData.position.y + halfSizeA.y >= bodyBData.position.y - halfSizeB.y) &&
                      (bodyBData.position.y + halfSizeB.y >= bodyAData.position.y - halfSizeA.y);
    
    return collisionX && collisionY;
}

// Fluid simulation methods (not supported in 2D backend)
FluidHandle Box2DBackend::CreateFluid(const FluidDesc& desc) {
    return INVALID_HANDLE;
}

void Box2DBackend::DestroyFluid(FluidHandle handle) {
    // Not supported
}

void Box2DBackend::GetFluidParticles(FluidHandle handle, std::vector<Vec3>& particles) {
    // Not supported
}

// Cloth simulation methods (not supported in 2D backend)
ClothHandle Box2DBackend::CreateCloth(const ClothDesc& desc) {
    return INVALID_HANDLE;
}

void Box2DBackend::DestroyCloth(ClothHandle handle) {
    // Not supported
}

void Box2DBackend::GetClothVertices(ClothHandle handle, std::vector<Vec3>& vertices) {
    // Not supported
}

void Box2DBackend::AttachClothToBody(ClothHandle cloth, RigidBodyHandle body, const Vec3& offset) {
    // Not supported
}

} // namespace physics
} // namespace pywrkgame