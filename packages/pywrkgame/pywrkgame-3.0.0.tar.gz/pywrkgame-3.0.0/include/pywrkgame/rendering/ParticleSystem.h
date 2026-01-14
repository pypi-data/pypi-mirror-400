#pragma once

#include "GraphicsDevice.h"
#include "GraphicsTypes.h"
#include <memory>
#include <vector>
#include <functional>

namespace pywrkgame {
namespace rendering {

// Particle structure
struct Particle {
    float position[3] = {0.0f, 0.0f, 0.0f};
    float velocity[3] = {0.0f, 0.0f, 0.0f};
    float acceleration[3] = {0.0f, 0.0f, 0.0f};
    float color[4] = {1.0f, 1.0f, 1.0f, 1.0f};
    float size = 1.0f;
    float rotation = 0.0f;
    float lifetime = 1.0f;
    float age = 0.0f;
    bool active = false;
};

// Particle emitter shape
enum class EmitterShape {
    Point,
    Sphere,
    Box,
    Cone,
    Circle
};

// Particle rendering mode
enum class ParticleRenderMode {
    Billboard,      // Always face camera
    Stretched,      // Stretch along velocity
    Mesh,          // Use 3D mesh
    Trail          // Leave trail behind
};

// Particle emitter configuration
struct ParticleEmitterConfig {
    // Emission properties
    EmitterShape shape = EmitterShape::Point;
    float emissionRate = 10.0f;        // Particles per second
    uint32_t maxParticles = 1000;
    bool looping = true;
    float duration = 5.0f;
    
    // Shape parameters
    float shapeRadius = 1.0f;
    float shapeAngle = 45.0f;          // For cone emitter
    float shapeSize[3] = {1.0f, 1.0f, 1.0f};  // For box emitter
    
    // Particle properties
    float startLifetime = 5.0f;
    float startSpeed = 5.0f;
    float startSize = 1.0f;
    float startRotation = 0.0f;
    float startColor[4] = {1.0f, 1.0f, 1.0f, 1.0f};
    
    // Particle variation (randomness)
    float lifetimeVariation = 0.0f;
    float speedVariation = 0.0f;
    float sizeVariation = 0.0f;
    float rotationVariation = 0.0f;
    
    // Physics
    float gravity[3] = {0.0f, -9.81f, 0.0f};
    float drag = 0.0f;
    
    // Rendering
    ParticleRenderMode renderMode = ParticleRenderMode::Billboard;
    TextureHandle texture;
    bool useGPUSimulation = true;
};

// Particle emitter
class ParticleEmitter {
public:
    ParticleEmitter();
    ~ParticleEmitter();
    
    bool Initialize(GraphicsDevice* device, const ParticleEmitterConfig& config);
    void Shutdown();
    
    // Update particles (CPU simulation)
    void Update(float deltaTime);
    
    // Update particles (GPU simulation)
    void UpdateGPU(float deltaTime);
    
    // Emit particles
    void Emit(uint32_t count);
    
    // Control
    void Play();
    void Pause();
    void Stop();
    void Reset();
    
    bool IsPlaying() const { return playing; }
    bool IsPaused() const { return paused; }
    
    // Configuration
    void SetConfig(const ParticleEmitterConfig& config);
    ParticleEmitterConfig GetConfig() const { return config; }
    
    // Particle access
    uint32_t GetActiveParticleCount() const { return activeParticleCount; }
    uint32_t GetMaxParticles() const { return config.maxParticles; }
    const std::vector<Particle>& GetParticles() const { return particles; }
    
    // Transform
    void SetPosition(float x, float y, float z);
    void GetPosition(float& x, float& y, float& z) const;
    
    void SetRotation(float x, float y, float z);
    void GetRotation(float& x, float& y, float& z) const;
    
    bool IsInitialized() const { return initialized; }
    
private:
    bool initialized = false;
    GraphicsDevice* device = nullptr;
    ParticleEmitterConfig config;
    
    // Particle data
    std::vector<Particle> particles;
    uint32_t activeParticleCount = 0;
    
    // GPU resources
    BufferHandle particleBuffer;
    BufferHandle indirectDrawBuffer;
    ShaderHandle computeShader;
    ShaderHandle renderShader;
    
    // State
    bool playing = false;
    bool paused = false;
    float emissionAccumulator = 0.0f;
    float elapsedTime = 0.0f;
    
    // Transform
    float position[3] = {0.0f, 0.0f, 0.0f};
    float rotation[3] = {0.0f, 0.0f, 0.0f};
    
    // Helper functions
    void EmitParticle();
    void UpdateParticleCPU(Particle& particle, float deltaTime);
    void InitializeGPUResources();
    void CleanupGPUResources();
    float RandomRange(float min, float max);
};

// Particle system manager
class ParticleSystem {
public:
    ParticleSystem();
    ~ParticleSystem();
    
    bool Initialize(GraphicsDevice* device);
    void Shutdown();
    
    // Update all emitters
    void Update(float deltaTime);
    
    // Render all emitters
    void Render();
    
    // Emitter management
    uint32_t CreateEmitter(const ParticleEmitterConfig& config);
    void DestroyEmitter(uint32_t emitterId);
    ParticleEmitter* GetEmitter(uint32_t emitterId);
    
    // Global settings
    void SetGlobalGravity(float x, float y, float z);
    void GetGlobalGravity(float& x, float& y, float& z) const;
    
    void EnableGPUSimulation(bool enable);
    bool IsGPUSimulationEnabled() const { return gpuSimulationEnabled; }
    
    // Statistics
    uint32_t GetTotalParticleCount() const;
    uint32_t GetEmitterCount() const { return static_cast<uint32_t>(emitters.size()); }
    
    bool IsInitialized() const { return initialized; }
    
private:
    bool initialized = false;
    GraphicsDevice* device = nullptr;
    
    // Emitters
    uint32_t nextEmitterId = 1;
    std::vector<std::unique_ptr<ParticleEmitter>> emitters;
    std::vector<uint32_t> emitterIds;
    
    // Global settings
    float globalGravity[3] = {0.0f, -9.81f, 0.0f};
    bool gpuSimulationEnabled = true;
    
    // Rendering resources
    BufferHandle quadVertexBuffer;
    ShaderHandle billboardShader;
};

} // namespace rendering
} // namespace pywrkgame
