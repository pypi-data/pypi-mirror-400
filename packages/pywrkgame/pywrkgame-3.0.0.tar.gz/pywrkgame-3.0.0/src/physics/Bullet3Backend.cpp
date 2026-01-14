#include "pywrkgame/physics/Bullet3Backend.h"
#include <cmath>
#include <algorithm>

namespace pywrkgame {
namespace physics {

Bullet3Backend::Bullet3Backend() = default;

Bullet3Backend::~Bullet3Backend() {
    Shutdown();
}

bool Bullet3Backend::Initialize() {
    // Initialize Bullet3 physics world (simplified implementation)
    return true;
}

void Bullet3Backend::Update(float deltaTime) {
    // Update all rigid bodies with gravity and velocity
    for (auto& [handle, body] : rigidBodies) {
        if (!body.isKinematic) {
            // Apply gravity
            body.velocity = body.velocity + gravity * deltaTime;
            
            // Update position
            body.position = body.position + body.velocity * deltaTime;
        }
    }
    
    // Update soft bodies (simplified simulation)
    for (auto& [handle, softBody] : softBodies) {
        // Apply gravity to vertices
        for (auto& vertex : softBody.vertices) {
            vertex = vertex + gravity * (deltaTime * deltaTime);
        }
    }
    
    // Update fluid particles (simplified SPH simulation)
    for (auto& [handle, fluid] : fluids) {
        for (size_t i = 0; i < fluid.particles.size(); ++i) {
            // Apply gravity
            fluid.velocities[i] = fluid.velocities[i] + gravity * deltaTime;
            
            // Update position
            fluid.particles[i] = fluid.particles[i] + fluid.velocities[i] * deltaTime;
            
            // Simple boundary check (keep particles in bounds)
            if (fluid.particles[i].y < -10.0f) {
                fluid.particles[i].y = -10.0f;
                fluid.velocities[i].y = -fluid.velocities[i].y * 0.5f; // Bounce with damping
            }
        }
    }
    
    // Update cloth simulation
    for (auto& [handle, cloth] : cloths) {
        // Simple Verlet integration for cloth
        for (int i = 0; i < cloth.resolutionX * cloth.resolutionY; ++i) {
            if (!cloth.fixedVertices[i]) {
                // Apply gravity
                cloth.vertices[i] = cloth.vertices[i] + gravity * (deltaTime * deltaTime);
            }
        }
        
        // If attached to a body, update attachment point
        if (cloth.attachedBody != INVALID_HANDLE) {
            auto bodyIt = rigidBodies.find(cloth.attachedBody);
            if (bodyIt != rigidBodies.end()) {
                // Update first vertex to follow the body
                cloth.vertices[0] = bodyIt->second.position + cloth.attachmentOffset;
            }
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
                if (CheckCollision(handles[i], handles[j])) {
                    CollisionInfo info;
                    info.bodyA = handles[i];
                    info.bodyB = handles[j];
                    info.contactPoint = (rigidBodies[handles[i]].position + rigidBodies[handles[j]].position) * 0.5f;
                    info.contactNormal = (rigidBodies[handles[j]].position - rigidBodies[handles[i]].position).normalized();
                    info.penetrationDepth = 0.1f;
                    collisionCallback(info);
                }
            }
        }
    }
}

void Bullet3Backend::Shutdown() {
    rigidBodies.clear();
    softBodies.clear();
    fluids.clear();
    cloths.clear();
    colliders.clear();
    colliderToBody.clear();
}

RigidBodyHandle Bullet3Backend::CreateRigidBody(const RigidBodyDesc& desc) {
    RigidBodyHandle handle = AllocateHandle();
    
    RigidBodyData data;
    data.position = desc.position;
    data.rotation = desc.rotation;
    data.velocity = Vec3(0.0f, 0.0f, 0.0f);
    data.mass = desc.mass;
    data.isKinematic = desc.isKinematic;
    
    rigidBodies[handle] = data;
    return handle;
}

void Bullet3Backend::DestroyRigidBody(RigidBodyHandle handle) {
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

void Bullet3Backend::SetRigidBodyTransform(RigidBodyHandle handle, const Vec3& position, const Quat& rotation) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end()) {
        it->second.position = position;
        it->second.rotation = rotation;
    }
}

void Bullet3Backend::GetRigidBodyTransform(RigidBodyHandle handle, Vec3& position, Quat& rotation) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end()) {
        position = it->second.position;
        rotation = it->second.rotation;
    }
}

void Bullet3Backend::SetRigidBodyVelocity(RigidBodyHandle handle, const Vec3& velocity) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end()) {
        it->second.velocity = velocity;
    }
}

Vec3 Bullet3Backend::GetRigidBodyVelocity(RigidBodyHandle handle) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end()) {
        return it->second.velocity;
    }
    return Vec3(0.0f, 0.0f, 0.0f);
}

void Bullet3Backend::ApplyForce(RigidBodyHandle handle, const Vec3& force) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end() && !it->second.isKinematic) {
        // F = ma, so a = F/m
        Vec3 acceleration = force / it->second.mass;
        it->second.velocity = it->second.velocity + acceleration * 0.016f; // Assume 60 FPS
    }
}

void Bullet3Backend::ApplyImpulse(RigidBodyHandle handle, const Vec3& impulse) {
    auto it = rigidBodies.find(handle);
    if (it != rigidBodies.end() && !it->second.isKinematic) {
        // Impulse directly changes velocity: J = m*v, so v = J/m
        it->second.velocity = it->second.velocity + impulse / it->second.mass;
    }
}

ColliderHandle Bullet3Backend::CreateCollider(RigidBodyHandle body, const ColliderDesc& desc) {
    ColliderHandle handle = AllocateHandle();
    colliders[handle] = desc;
    colliderToBody[handle] = body;
    return handle;
}

void Bullet3Backend::DestroyCollider(ColliderHandle handle) {
    colliders.erase(handle);
    colliderToBody.erase(handle);
}

SoftBodyHandle Bullet3Backend::CreateSoftBody(const SoftBodyDesc& desc) {
    SoftBodyHandle handle = AllocateHandle();
    
    SoftBodyData data;
    data.vertices = desc.vertices;
    data.indices = desc.indices;
    data.mass = desc.mass;
    data.stiffness = desc.stiffness;
    data.damping = desc.damping;
    
    softBodies[handle] = data;
    return handle;
}

void Bullet3Backend::DestroySoftBody(SoftBodyHandle handle) {
    softBodies.erase(handle);
}

void Bullet3Backend::GetSoftBodyVertices(SoftBodyHandle handle, std::vector<Vec3>& vertices) {
    auto it = softBodies.find(handle);
    if (it != softBodies.end()) {
        vertices = it->second.vertices;
    }
}

void Bullet3Backend::SetCollisionCallback(CollisionCallback callback) {
    collisionCallback = callback;
}

bool Bullet3Backend::RaycastQuery(const Ray& ray, RaycastResult& result) {
    result.hit = false;
    result.distance = ray.maxDistance;
    
    // Simple raycast against all rigid bodies (sphere approximation)
    for (const auto& [handle, body] : rigidBodies) {
        // Get collider for this body
        float radius = 0.5f; // Default radius
        for (const auto& [colliderHandle, bodyHandle] : colliderToBody) {
            if (bodyHandle == handle) {
                auto colliderIt = colliders.find(colliderHandle);
                if (colliderIt != colliders.end()) {
                    if (colliderIt->second.shape == ColliderShape::Sphere) {
                        radius = colliderIt->second.radius;
                    } else if (colliderIt->second.shape == ColliderShape::Box) {
                        radius = colliderIt->second.size.length() * 0.5f;
                    }
                }
                break;
            }
        }
        
        // Ray-sphere intersection
        Vec3 oc = ray.origin - body.position;
        float a = ray.direction.dot(ray.direction);
        float b = 2.0f * oc.dot(ray.direction);
        float c = oc.dot(oc) - radius * radius;
        float discriminant = b * b - 4 * a * c;
        
        if (discriminant >= 0) {
            float t = (-b - std::sqrt(discriminant)) / (2.0f * a);
            if (t > 0 && t < result.distance) {
                result.hit = true;
                result.body = handle;
                result.distance = t;
                result.hitPoint = ray.origin + ray.direction * t;
                result.hitNormal = (result.hitPoint - body.position).normalized();
            }
        }
    }
    
    return result.hit;
}

bool Bullet3Backend::AreColliding(RigidBodyHandle bodyA, RigidBodyHandle bodyB) {
    return CheckCollision(bodyA, bodyB);
}

void Bullet3Backend::SetGravity(const Vec3& g) {
    gravity = g;
}

Vec3 Bullet3Backend::GetGravity() {
    return gravity;
}

RigidBodyHandle Bullet3Backend::AllocateHandle() {
    return nextHandle++;
}

bool Bullet3Backend::CheckCollision(RigidBodyHandle bodyA, RigidBodyHandle bodyB) {
    auto itA = rigidBodies.find(bodyA);
    auto itB = rigidBodies.find(bodyB);
    
    if (itA == rigidBodies.end() || itB == rigidBodies.end()) {
        return false;
    }
    
    // Get collider sizes (simplified - assume sphere colliders)
    float radiusA = 0.5f;
    float radiusB = 0.5f;
    
    for (const auto& [colliderHandle, bodyHandle] : colliderToBody) {
        if (bodyHandle == bodyA) {
            auto colliderIt = colliders.find(colliderHandle);
            if (colliderIt != colliders.end()) {
                if (colliderIt->second.shape == ColliderShape::Sphere) {
                    radiusA = colliderIt->second.radius;
                } else if (colliderIt->second.shape == ColliderShape::Box) {
                    radiusA = colliderIt->second.size.length() * 0.5f;
                }
            }
        }
        if (bodyHandle == bodyB) {
            auto colliderIt = colliders.find(colliderHandle);
            if (colliderIt != colliders.end()) {
                if (colliderIt->second.shape == ColliderShape::Sphere) {
                    radiusB = colliderIt->second.radius;
                } else if (colliderIt->second.shape == ColliderShape::Box) {
                    radiusB = colliderIt->second.size.length() * 0.5f;
                }
            }
        }
    }
    
    // Simple sphere-sphere collision
    float distance = itA->second.position.distance(itB->second.position);
    return distance < (radiusA + radiusB);
}

// Fluid simulation methods
FluidHandle Bullet3Backend::CreateFluid(const FluidDesc& desc) {
    FluidHandle handle = AllocateHandle();
    
    FluidData data;
    data.viscosity = desc.viscosity;
    data.density = desc.density;
    data.surfaceTension = desc.surfaceTension;
    
    // Initialize particles in a grid
    int particlesPerSide = static_cast<int>(std::cbrt(desc.particleCount));
    float spacing = desc.size.x / particlesPerSide;
    
    for (int x = 0; x < particlesPerSide; ++x) {
        for (int y = 0; y < particlesPerSide; ++y) {
            for (int z = 0; z < particlesPerSide; ++z) {
                Vec3 pos = desc.position + Vec3(x * spacing, y * spacing, z * spacing);
                data.particles.push_back(pos);
                data.velocities.push_back(Vec3(0.0f, 0.0f, 0.0f));
            }
        }
    }
    
    fluids[handle] = data;
    return handle;
}

void Bullet3Backend::DestroyFluid(FluidHandle handle) {
    fluids.erase(handle);
}

void Bullet3Backend::GetFluidParticles(FluidHandle handle, std::vector<Vec3>& particles) {
    auto it = fluids.find(handle);
    if (it != fluids.end()) {
        particles = it->second.particles;
    }
}

// Cloth simulation methods
ClothHandle Bullet3Backend::CreateCloth(const ClothDesc& desc) {
    ClothHandle handle = AllocateHandle();
    
    ClothData data;
    data.resolutionX = desc.resolutionX;
    data.resolutionY = desc.resolutionY;
    data.mass = desc.mass;
    data.stiffness = desc.stiffness;
    data.damping = desc.damping;
    
    // Create cloth grid
    float stepX = desc.size.x / (desc.resolutionX - 1);
    float stepY = desc.size.y / (desc.resolutionY - 1);
    
    for (int y = 0; y < desc.resolutionY; ++y) {
        for (int x = 0; x < desc.resolutionX; ++x) {
            Vec3 pos = desc.position + Vec3(x * stepX, -y * stepY, 0.0f);
            data.vertices.push_back(pos);
            
            // Fix corners if requested
            bool isCorner = (x == 0 || x == desc.resolutionX - 1) && y == 0;
            data.fixedVertices.push_back(desc.fixedCorners && isCorner);
        }
    }
    
    // Create triangles
    for (int y = 0; y < desc.resolutionY - 1; ++y) {
        for (int x = 0; x < desc.resolutionX - 1; ++x) {
            int i0 = y * desc.resolutionX + x;
            int i1 = i0 + 1;
            int i2 = i0 + desc.resolutionX;
            int i3 = i2 + 1;
            
            // Two triangles per quad
            data.indices.push_back(i0);
            data.indices.push_back(i2);
            data.indices.push_back(i1);
            
            data.indices.push_back(i1);
            data.indices.push_back(i2);
            data.indices.push_back(i3);
        }
    }
    
    cloths[handle] = data;
    return handle;
}

void Bullet3Backend::DestroyCloth(ClothHandle handle) {
    cloths.erase(handle);
}

void Bullet3Backend::GetClothVertices(ClothHandle handle, std::vector<Vec3>& vertices) {
    auto it = cloths.find(handle);
    if (it != cloths.end()) {
        vertices = it->second.vertices;
    }
}

void Bullet3Backend::AttachClothToBody(ClothHandle cloth, RigidBodyHandle body, const Vec3& offset) {
    auto clothIt = cloths.find(cloth);
    if (clothIt != cloths.end()) {
        clothIt->second.attachedBody = body;
        clothIt->second.attachmentOffset = offset;
    }
}

} // namespace physics
} // namespace pywrkgame