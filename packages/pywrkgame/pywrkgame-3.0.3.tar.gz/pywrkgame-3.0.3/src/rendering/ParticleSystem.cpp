#include "pywrkgame/rendering/ParticleSystem.h"
#include <cmath>
#include <cstdlib>
#include <algorithm>

namespace pywrkgame {
namespace rendering {

// ============================================================================
// Particle Emitter
// ============================================================================

ParticleEmitter::ParticleEmitter() = default;

ParticleEmitter::~ParticleEmitter() {
    Shutdown();
}

bool ParticleEmitter::Initialize(GraphicsDevice* dev, const ParticleEmitterConfig& cfg) {
    if (!dev) return false;
    if (initialized) return false;
    
    device = dev;
    config = cfg;
    
    // Allocate particle array
    particles.resize(config.maxParticles);
    activeParticleCount = 0;
    
    // Initialize GPU resources if GPU simulation is enabled
    if (config.useGPUSimulation) {
        InitializeGPUResources();
    }
    
    initialized = true;
    return true;
}

void ParticleEmitter::Shutdown() {
    if (!initialized) return;
    
    CleanupGPUResources();
    
    particles.clear();
    activeParticleCount = 0;
    device = nullptr;
    initialized = false;
}

void ParticleEmitter::Update(float deltaTime) {
    if (!initialized || !playing || paused) return;
    
    elapsedTime += deltaTime;
    
    // Check if emitter should stop (non-looping)
    if (!config.looping && elapsedTime >= config.duration) {
        Stop();
        return;
    }
    
    // Emit new particles
    if (playing) {
        emissionAccumulator += config.emissionRate * deltaTime;
        uint32_t particlesToEmit = static_cast<uint32_t>(emissionAccumulator);
        emissionAccumulator -= particlesToEmit;
        
        Emit(particlesToEmit);
    }
    
    // Update particles
    if (config.useGPUSimulation) {
        UpdateGPU(deltaTime);
    } else {
        for (auto& particle : particles) {
            if (particle.active) {
                UpdateParticleCPU(particle, deltaTime);
            }
        }
    }
}

void ParticleEmitter::UpdateGPU(float deltaTime) {
    if (!device || !computeShader.IsValid()) return;
    
    // Update particle buffer with compute shader
    // This is a placeholder for actual GPU compute implementation
    // In a real implementation, this would dispatch a compute shader
    // that updates all particles in parallel on the GPU
}

void ParticleEmitter::Emit(uint32_t count) {
    if (!initialized) return;
    
    for (uint32_t i = 0; i < count; ++i) {
        if (activeParticleCount >= config.maxParticles) {
            break;
        }
        EmitParticle();
    }
}

void ParticleEmitter::EmitParticle() {
    // Find inactive particle
    Particle* particle = nullptr;
    for (auto& p : particles) {
        if (!p.active) {
            particle = &p;
            break;
        }
    }
    
    if (!particle) return;
    
    // Initialize particle
    particle->active = true;
    particle->age = 0.0f;
    
    // Lifetime
    float lifetimeVar = RandomRange(-config.lifetimeVariation, config.lifetimeVariation);
    particle->lifetime = config.startLifetime + lifetimeVar;
    
    // Position based on emitter shape
    switch (config.shape) {
        case EmitterShape::Point:
            particle->position[0] = position[0];
            particle->position[1] = position[1];
            particle->position[2] = position[2];
            break;
            
        case EmitterShape::Sphere: {
            float theta = RandomRange(0.0f, 2.0f * 3.14159f);
            float phi = RandomRange(0.0f, 3.14159f);
            float r = RandomRange(0.0f, config.shapeRadius);
            
            particle->position[0] = position[0] + r * std::sin(phi) * std::cos(theta);
            particle->position[1] = position[1] + r * std::sin(phi) * std::sin(theta);
            particle->position[2] = position[2] + r * std::cos(phi);
            break;
        }
        
        case EmitterShape::Box:
            particle->position[0] = position[0] + RandomRange(-config.shapeSize[0] / 2, config.shapeSize[0] / 2);
            particle->position[1] = position[1] + RandomRange(-config.shapeSize[1] / 2, config.shapeSize[1] / 2);
            particle->position[2] = position[2] + RandomRange(-config.shapeSize[2] / 2, config.shapeSize[2] / 2);
            break;
            
        case EmitterShape::Cone: {
            float angle = RandomRange(0.0f, config.shapeAngle * 3.14159f / 180.0f);
            float theta = RandomRange(0.0f, 2.0f * 3.14159f);
            float r = RandomRange(0.0f, config.shapeRadius);
            
            particle->position[0] = position[0] + r * std::sin(angle) * std::cos(theta);
            particle->position[1] = position[1] + r * std::cos(angle);
            particle->position[2] = position[2] + r * std::sin(angle) * std::sin(theta);
            break;
        }
        
        case EmitterShape::Circle: {
            float theta = RandomRange(0.0f, 2.0f * 3.14159f);
            float r = RandomRange(0.0f, config.shapeRadius);
            
            particle->position[0] = position[0] + r * std::cos(theta);
            particle->position[1] = position[1];
            particle->position[2] = position[2] + r * std::sin(theta);
            break;
        }
    }
    
    // Velocity
    float speedVar = RandomRange(-config.speedVariation, config.speedVariation);
    float speed = config.startSpeed + speedVar;
    
    // Direction based on emitter shape
    float direction[3] = {0.0f, 1.0f, 0.0f}; // Default up
    
    if (config.shape == EmitterShape::Sphere) {
        // Radial direction from center
        direction[0] = particle->position[0] - position[0];
        direction[1] = particle->position[1] - position[1];
        direction[2] = particle->position[2] - position[2];
        
        float length = std::sqrt(direction[0] * direction[0] + 
                                direction[1] * direction[1] + 
                                direction[2] * direction[2]);
        if (length > 0.0001f) {
            direction[0] /= length;
            direction[1] /= length;
            direction[2] /= length;
        }
    }
    
    particle->velocity[0] = direction[0] * speed;
    particle->velocity[1] = direction[1] * speed;
    particle->velocity[2] = direction[2] * speed;
    
    // Acceleration (gravity)
    particle->acceleration[0] = config.gravity[0];
    particle->acceleration[1] = config.gravity[1];
    particle->acceleration[2] = config.gravity[2];
    
    // Size
    float sizeVar = RandomRange(-config.sizeVariation, config.sizeVariation);
    particle->size = config.startSize + sizeVar;
    
    // Rotation
    float rotationVar = RandomRange(-config.rotationVariation, config.rotationVariation);
    particle->rotation = config.startRotation + rotationVar;
    
    // Color
    particle->color[0] = config.startColor[0];
    particle->color[1] = config.startColor[1];
    particle->color[2] = config.startColor[2];
    particle->color[3] = config.startColor[3];
    
    activeParticleCount++;
}

void ParticleEmitter::UpdateParticleCPU(Particle& particle, float deltaTime) {
    // Update age
    particle.age += deltaTime;
    
    // Check if particle should die
    if (particle.age >= particle.lifetime) {
        particle.active = false;
        activeParticleCount--;
        return;
    }
    
    // Apply drag
    if (config.drag > 0.0f) {
        float dragFactor = 1.0f - config.drag * deltaTime;
        dragFactor = std::max(0.0f, dragFactor);
        particle.velocity[0] *= dragFactor;
        particle.velocity[1] *= dragFactor;
        particle.velocity[2] *= dragFactor;
    }
    
    // Update velocity with acceleration
    particle.velocity[0] += particle.acceleration[0] * deltaTime;
    particle.velocity[1] += particle.acceleration[1] * deltaTime;
    particle.velocity[2] += particle.acceleration[2] * deltaTime;
    
    // Update position with velocity
    particle.position[0] += particle.velocity[0] * deltaTime;
    particle.position[1] += particle.velocity[1] * deltaTime;
    particle.position[2] += particle.velocity[2] * deltaTime;
    
    // Fade out alpha over lifetime
    float lifetimeRatio = particle.age / particle.lifetime;
    particle.color[3] = config.startColor[3] * (1.0f - lifetimeRatio);
}

void ParticleEmitter::Play() {
    playing = true;
    paused = false;
}

void ParticleEmitter::Pause() {
    paused = true;
}

void ParticleEmitter::Stop() {
    playing = false;
    paused = false;
}

void ParticleEmitter::Reset() {
    // Deactivate all particles
    for (auto& particle : particles) {
        particle.active = false;
    }
    activeParticleCount = 0;
    emissionAccumulator = 0.0f;
    elapsedTime = 0.0f;
}

void ParticleEmitter::SetConfig(const ParticleEmitterConfig& cfg) {
    config = cfg;
    
    // Resize particle array if max particles changed
    if (particles.size() != config.maxParticles) {
        particles.resize(config.maxParticles);
        activeParticleCount = std::min(activeParticleCount, config.maxParticles);
    }
}

void ParticleEmitter::SetPosition(float x, float y, float z) {
    position[0] = x;
    position[1] = y;
    position[2] = z;
}

void ParticleEmitter::GetPosition(float& x, float& y, float& z) const {
    x = position[0];
    y = position[1];
    z = position[2];
}

void ParticleEmitter::SetRotation(float x, float y, float z) {
    rotation[0] = x;
    rotation[1] = y;
    rotation[2] = z;
}

void ParticleEmitter::GetRotation(float& x, float& y, float& z) const {
    x = rotation[0];
    y = rotation[1];
    z = rotation[2];
}

void ParticleEmitter::InitializeGPUResources() {
    if (!device) return;
    
    // Create particle buffer for GPU simulation
    BufferDesc bufferDesc{};
    bufferDesc.size = particles.size() * sizeof(Particle);
    bufferDesc.type = BufferType::Storage;
    bufferDesc.dynamic = true;
    particleBuffer = device->CreateBuffer(bufferDesc);
    
    // Create compute shader for particle update
    ShaderDesc computeDesc{};
    computeDesc.stage = ShaderStage::Compute;
    computeDesc.source = "// Particle Update Compute Shader";
    computeShader = device->CreateShader(computeDesc);
    
    // Create render shader for particle rendering
    ShaderDesc renderDesc{};
    renderDesc.stage = ShaderStage::Fragment;
    renderDesc.source = "// Particle Render Shader";
    renderShader = device->CreateShader(renderDesc);
}

void ParticleEmitter::CleanupGPUResources() {
    if (!device) return;
    
    if (particleBuffer.IsValid()) {
        device->DestroyBuffer(particleBuffer);
        particleBuffer = BufferHandle{};
    }
    
    if (computeShader.IsValid()) {
        device->DestroyShader(computeShader);
        computeShader = ShaderHandle{};
    }
    
    if (renderShader.IsValid()) {
        device->DestroyShader(renderShader);
        renderShader = ShaderHandle{};
    }
}

float ParticleEmitter::RandomRange(float min, float max) {
    float random = static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
    return min + random * (max - min);
}

// ============================================================================
// Particle System
// ============================================================================

ParticleSystem::ParticleSystem() = default;

ParticleSystem::~ParticleSystem() {
    Shutdown();
}

bool ParticleSystem::Initialize(GraphicsDevice* dev) {
    if (!dev) return false;
    if (initialized) return false;
    
    device = dev;
    
    // Create quad vertex buffer for billboard rendering
    float quadVertices[] = {
        -0.5f, -0.5f, 0.0f, 0.0f, 0.0f,
         0.5f, -0.5f, 0.0f, 1.0f, 0.0f,
         0.5f,  0.5f, 0.0f, 1.0f, 1.0f,
        -0.5f,  0.5f, 0.0f, 0.0f, 1.0f
    };
    
    BufferDesc quadDesc{};
    quadDesc.size = sizeof(quadVertices);
    quadDesc.type = BufferType::Vertex;
    quadDesc.initialData = quadVertices;
    quadDesc.dynamic = false;
    quadVertexBuffer = device->CreateBuffer(quadDesc);
    
    if (!quadVertexBuffer.IsValid()) {
        return false;
    }
    
    // Create billboard shader
    ShaderDesc shaderDesc{};
    shaderDesc.stage = ShaderStage::Fragment;
    shaderDesc.source = "// Billboard Shader";
    billboardShader = device->CreateShader(shaderDesc);
    
    if (!billboardShader.IsValid()) {
        device->DestroyBuffer(quadVertexBuffer);
        return false;
    }
    
    initialized = true;
    return true;
}

void ParticleSystem::Shutdown() {
    if (!initialized) return;
    
    // Destroy all emitters
    emitters.clear();
    emitterIds.clear();
    
    // Cleanup GPU resources
    if (device) {
        if (quadVertexBuffer.IsValid()) {
            device->DestroyBuffer(quadVertexBuffer);
            quadVertexBuffer = BufferHandle{};
        }
        
        if (billboardShader.IsValid()) {
            device->DestroyShader(billboardShader);
            billboardShader = ShaderHandle{};
        }
    }
    
    device = nullptr;
    initialized = false;
}

void ParticleSystem::Update(float deltaTime) {
    if (!initialized) return;
    
    // Update all emitters
    for (auto& emitter : emitters) {
        if (emitter) {
            emitter->Update(deltaTime);
        }
    }
}

void ParticleSystem::Render() {
    if (!initialized || !device) return;
    
    // Render all emitters
    // This is a placeholder for actual rendering implementation
    // In a real implementation, this would:
    // 1. Sort particles by distance to camera (for alpha blending)
    // 2. Batch particles by texture
    // 3. Render using instanced drawing or compute shader
}

uint32_t ParticleSystem::CreateEmitter(const ParticleEmitterConfig& config) {
    if (!initialized) return 0;
    
    auto emitter = std::make_unique<ParticleEmitter>();
    if (!emitter->Initialize(device, config)) {
        return 0;
    }
    
    uint32_t id = nextEmitterId++;
    emitterIds.push_back(id);
    emitters.push_back(std::move(emitter));
    
    return id;
}

void ParticleSystem::DestroyEmitter(uint32_t emitterId) {
    if (!initialized) return;
    
    for (size_t i = 0; i < emitterIds.size(); ++i) {
        if (emitterIds[i] == emitterId) {
            emitters[i]->Shutdown();
            emitters.erase(emitters.begin() + i);
            emitterIds.erase(emitterIds.begin() + i);
            break;
        }
    }
}

ParticleEmitter* ParticleSystem::GetEmitter(uint32_t emitterId) {
    if (!initialized) return nullptr;
    
    for (size_t i = 0; i < emitterIds.size(); ++i) {
        if (emitterIds[i] == emitterId) {
            return emitters[i].get();
        }
    }
    
    return nullptr;
}

void ParticleSystem::SetGlobalGravity(float x, float y, float z) {
    globalGravity[0] = x;
    globalGravity[1] = y;
    globalGravity[2] = z;
}

void ParticleSystem::GetGlobalGravity(float& x, float& y, float& z) const {
    x = globalGravity[0];
    y = globalGravity[1];
    z = globalGravity[2];
}

void ParticleSystem::EnableGPUSimulation(bool enable) {
    gpuSimulationEnabled = enable;
}

uint32_t ParticleSystem::GetTotalParticleCount() const {
    uint32_t total = 0;
    for (const auto& emitter : emitters) {
        if (emitter) {
            total += emitter->GetActiveParticleCount();
        }
    }
    return total;
}

} // namespace rendering
} // namespace pywrkgame
