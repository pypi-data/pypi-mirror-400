#include "pywrkgame/animation/ProceduralAnimation.h"
#include "pywrkgame/animation/AnimationSystem.h"
#include <algorithm>
#include <cmath>
#include <random>
#include <glm/gtx/quaternion.hpp>
#include <glm/gtc/matrix_transform.hpp>

namespace pywrkgame {

// ============================================================================
// NoiseGenerator
// ============================================================================

NoiseGenerator::NoiseGenerator(NoiseType type)
    : noiseType(type)
    , seed(12345) {
}

void NoiseGenerator::SetSeed(unsigned int newSeed) {
    seed = newSeed;
}

float NoiseGenerator::Generate1D(float x, float frequency, float amplitude) const {
    return Generate3D(x * frequency, 0.0f, 0.0f) * amplitude;
}

float NoiseGenerator::Generate2D(float x, float y, float frequency, float amplitude) const {
    return Generate3D(x * frequency, y * frequency, 0.0f) * amplitude;
}

float NoiseGenerator::Generate3D(float x, float y, float z, float frequency, float amplitude) const {
    x *= frequency;
    y *= frequency;
    z *= frequency;
    
    float noise = 0.0f;
    
    switch (noiseType) {
        case NoiseType::Perlin:
            noise = PerlinNoise(x, y, z);
            break;
        case NoiseType::Simplex:
            noise = SimplexNoise(x, y, z);
            break;
        case NoiseType::Worley:
            noise = WorleyNoise(x, y, z);
            break;
        case NoiseType::White:
            noise = WhiteNoise(x, y, z);
            break;
    }
    
    return noise * amplitude;
}

float NoiseGenerator::GenerateFractal(float x, float y, float z, int octaves,
                                     float lacunarity, float persistence) const {
    float total = 0.0f;
    float frequency = 1.0f;
    float amplitude = 1.0f;
    float maxValue = 0.0f;
    
    for (int i = 0; i < octaves; ++i) {
        total += Generate3D(x, y, z, frequency, amplitude);
        maxValue += amplitude;
        
        frequency *= lacunarity;
        amplitude *= persistence;
    }
    
    return total / maxValue;
}

float NoiseGenerator::Fade(float t) const {
    return t * t * t * (t * (t * 6.0f - 15.0f) + 10.0f);
}

float NoiseGenerator::Lerp(float t, float a, float b) const {
    return a + t * (b - a);
}

float NoiseGenerator::Grad(int hash, float x, float y, float z) const {
    int h = hash & 15;
    float u = h < 8 ? x : y;
    float v = h < 4 ? y : (h == 12 || h == 14 ? x : z);
    return ((h & 1) == 0 ? u : -u) + ((h & 2) == 0 ? v : -v);
}

float NoiseGenerator::PerlinNoise(float x, float y, float z) const {
    // Simplified Perlin noise implementation
    int X = static_cast<int>(std::floor(x)) & 255;
    int Y = static_cast<int>(std::floor(y)) & 255;
    int Z = static_cast<int>(std::floor(z)) & 255;
    
    x -= std::floor(x);
    y -= std::floor(y);
    z -= std::floor(z);
    
    float u = Fade(x);
    float v = Fade(y);
    float w = Fade(z);
    
    // Hash coordinates
    int A = (X + seed) & 255;
    int B = (X + 1 + seed) & 255;
    
    // Interpolate
    float result = Lerp(w,
        Lerp(v, Lerp(u, Grad(A, x, y, z), Grad(B, x - 1, y, z)),
                Lerp(u, Grad(A, x, y - 1, z), Grad(B, x - 1, y - 1, z))),
        Lerp(v, Lerp(u, Grad(A, x, y, z - 1), Grad(B, x - 1, y, z - 1)),
                Lerp(u, Grad(A, x, y - 1, z - 1), Grad(B, x - 1, y - 1, z - 1)))
    );
    
    return (result + 1.0f) * 0.5f;  // Normalize to [0, 1]
}

float NoiseGenerator::SimplexNoise(float x, float y, float z) const {
    // Simplified simplex noise (similar to Perlin for this implementation)
    return PerlinNoise(x * 1.5f, y * 1.5f, z * 1.5f);
}

float NoiseGenerator::WorleyNoise(float x, float y, float z) const {
    // Simplified Worley noise (cellular noise)
    int xi = static_cast<int>(std::floor(x));
    int yi = static_cast<int>(std::floor(y));
    int zi = static_cast<int>(std::floor(z));
    
    float minDist = 10000.0f;
    
    // Check neighboring cells
    for (int dx = -1; dx <= 1; ++dx) {
        for (int dy = -1; dy <= 1; ++dy) {
            for (int dz = -1; dz <= 1; ++dz) {
                // Generate random point in cell
                int cellX = xi + dx;
                int cellY = yi + dy;
                int cellZ = zi + dz;
                
                unsigned int hash = (cellX * 73856093) ^ (cellY * 19349663) ^ (cellZ * 83492791) ^ seed;
                std::mt19937 rng(hash);
                std::uniform_real_distribution<float> dist(0.0f, 1.0f);
                
                float px = cellX + dist(rng);
                float py = cellY + dist(rng);
                float pz = cellZ + dist(rng);
                
                float dx2 = px - x;
                float dy2 = py - y;
                float dz2 = pz - z;
                float dist2 = dx2 * dx2 + dy2 * dy2 + dz2 * dz2;
                
                minDist = std::min(minDist, dist2);
            }
        }
    }
    
    return std::sqrt(minDist);
}

float NoiseGenerator::WhiteNoise(float x, float y, float z) const {
    unsigned int hash = static_cast<unsigned int>(x * 73856093) ^ 
                       static_cast<unsigned int>(y * 19349663) ^ 
                       static_cast<unsigned int>(z * 83492791) ^ seed;
    std::mt19937 rng(hash);
    std::uniform_real_distribution<float> dist(0.0f, 1.0f);
    return dist(rng);
}

// ============================================================================
// NoiseModifier
// ============================================================================

NoiseModifier::NoiseModifier(NoiseType type)
    : noiseGen(type)
    , frequency(1.0f)
    , amplitude(1.0f)
    , octaves(3)
    , affectPosition(true)
    , affectRotation(false)
    , affectScale(false) {
}

void NoiseModifier::SetNoiseType(NoiseType type) {
    noiseGen.SetType(type);
}

void NoiseModifier::Apply(Bone& bone, float time, float deltaTime) {
    if (!enabled || strength <= 0.0f) {
        return;
    }
    
    // Extract current transform components
    glm::vec3 position = glm::vec3(bone.localTransform[3]);
    glm::quat rotation = glm::quat_cast(bone.localTransform);
    glm::vec3 scale = glm::vec3(
        glm::length(glm::vec3(bone.localTransform[0])),
        glm::length(glm::vec3(bone.localTransform[1])),
        glm::length(glm::vec3(bone.localTransform[2]))
    );
    
    // Apply noise to position
    if (affectPosition) {
        float noiseX = noiseGen.GenerateFractal(time, 0.0f, 0.0f, octaves);
        float noiseY = noiseGen.GenerateFractal(0.0f, time, 0.0f, octaves);
        float noiseZ = noiseGen.GenerateFractal(0.0f, 0.0f, time, octaves);
        
        glm::vec3 noiseOffset(noiseX, noiseY, noiseZ);
        noiseOffset = (noiseOffset - 0.5f) * 2.0f * amplitude;  // Center around 0
        position += noiseOffset * strength;
    }
    
    // Apply noise to rotation
    if (affectRotation) {
        float noiseAngle = noiseGen.GenerateFractal(time, 1.0f, 1.0f, octaves);
        noiseAngle = (noiseAngle - 0.5f) * 2.0f * amplitude;
        
        glm::quat noiseRotation = glm::angleAxis(noiseAngle * strength, glm::vec3(0.0f, 1.0f, 0.0f));
        rotation = noiseRotation * rotation;
    }
    
    // Apply noise to scale
    if (affectScale) {
        float noiseScale = noiseGen.GenerateFractal(time, 2.0f, 2.0f, octaves);
        noiseScale = 1.0f + (noiseScale - 0.5f) * amplitude * strength;
        scale *= noiseScale;
    }
    
    // Rebuild transform
    bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                         glm::mat4_cast(rotation) *
                         glm::scale(glm::mat4(1.0f), scale);
}

// ============================================================================
// WaveModifier
// ============================================================================

WaveModifier::WaveModifier()
    : affectPosition(true)
    , affectRotation(false) {
}

void WaveModifier::Apply(Bone& bone, float time, float deltaTime) {
    if (!enabled || strength <= 0.0f) {
        return;
    }
    
    // Extract current transform components
    glm::vec3 position = glm::vec3(bone.localTransform[3]);
    glm::quat rotation = glm::quat_cast(bone.localTransform);
    glm::vec3 scale = glm::vec3(
        glm::length(glm::vec3(bone.localTransform[0])),
        glm::length(glm::vec3(bone.localTransform[1])),
        glm::length(glm::vec3(bone.localTransform[2]))
    );
    
    // Calculate wave value
    float waveValue = std::sin(time * waveParams.frequency + waveParams.phase) * waveParams.amplitude;
    
    // Apply wave to position
    if (affectPosition) {
        position += waveParams.direction * waveValue * strength;
    }
    
    // Apply wave to rotation
    if (affectRotation) {
        glm::quat waveRotation = glm::angleAxis(waveValue * strength, waveParams.direction);
        rotation = waveRotation * rotation;
    }
    
    // Rebuild transform
    bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                         glm::mat4_cast(rotation) *
                         glm::scale(glm::mat4(1.0f), scale);
}

// ============================================================================
// SpringModifier
// ============================================================================

SpringModifier::SpringModifier()
    : currentPosition(0.0f)
    , targetPosition(0.0f)
    , externalForce(0.0f) {
}

void SpringModifier::SetTarget(const glm::vec3& target) {
    targetPosition = target;
}

void SpringModifier::ApplyForce(const glm::vec3& force) {
    externalForce += force;
}

void SpringModifier::Reset() {
    currentPosition = springParams.restPosition;
    springParams.velocity = glm::vec3(0.0f);
    externalForce = glm::vec3(0.0f);
}

void SpringModifier::Apply(Bone& bone, float time, float deltaTime) {
    if (!enabled || strength <= 0.0f) {
        return;
    }
    
    // Extract current position
    glm::vec3 position = glm::vec3(bone.localTransform[3]);
    
    // Spring physics simulation
    glm::vec3 displacement = currentPosition - targetPosition;
    glm::vec3 springForce = -springParams.stiffness * displacement;
    glm::vec3 dampingForce = -springParams.damping * springParams.velocity;
    glm::vec3 totalForce = springForce + dampingForce + externalForce;
    
    // Update velocity and position
    glm::vec3 acceleration = totalForce / springParams.mass;
    springParams.velocity += acceleration * deltaTime;
    currentPosition += springParams.velocity * deltaTime;
    
    // Apply to bone position
    glm::vec3 offset = currentPosition - springParams.restPosition;
    position += offset * strength;
    
    // Reset external force
    externalForce = glm::vec3(0.0f);
    
    // Rebuild transform
    glm::quat rotation = glm::quat_cast(bone.localTransform);
    glm::vec3 scale = glm::vec3(
        glm::length(glm::vec3(bone.localTransform[0])),
        glm::length(glm::vec3(bone.localTransform[1])),
        glm::length(glm::vec3(bone.localTransform[2]))
    );
    
    bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                         glm::mat4_cast(rotation) *
                         glm::scale(glm::mat4(1.0f), scale);
}

// ============================================================================
// CustomModifier
// ============================================================================

CustomModifier::CustomModifier(ModifierFunction func)
    : modifierFunc(func) {
}

void CustomModifier::Apply(Bone& bone, float time, float deltaTime) {
    if (!enabled || !modifierFunc) {
        return;
    }
    
    modifierFunc(bone, time, deltaTime);
}

// ============================================================================
// ProceduralAnimationGenerator
// ============================================================================

ProceduralAnimationGenerator::ProceduralAnimationGenerator() {
}

void ProceduralAnimationGenerator::AddModifier(int boneIndex, std::shared_ptr<AnimationModifier> modifier) {
    boneModifiers[boneIndex].push_back(modifier);
}

void ProceduralAnimationGenerator::RemoveModifiers(int boneIndex) {
    boneModifiers.erase(boneIndex);
}

void ProceduralAnimationGenerator::RemoveModifier(int boneIndex, std::shared_ptr<AnimationModifier> modifier) {
    auto it = boneModifiers.find(boneIndex);
    if (it != boneModifiers.end()) {
        auto& modifiers = it->second;
        modifiers.erase(std::remove(modifiers.begin(), modifiers.end(), modifier), modifiers.end());
    }
}

void ProceduralAnimationGenerator::Apply(Skeleton& skeleton, float time, float deltaTime) {
    for (auto& pair : boneModifiers) {
        int boneIndex = pair.first;
        if (boneIndex < 0 || boneIndex >= skeleton.GetBoneCount()) {
            continue;
        }
        
        Bone& bone = skeleton.GetBone(boneIndex);
        
        for (auto& modifier : pair.second) {
            if (modifier && modifier->IsEnabled()) {
                modifier->Apply(bone, time, deltaTime);
            }
        }
    }
    
    skeleton.UpdateGlobalTransforms();
}

void ProceduralAnimationGenerator::Clear() {
    boneModifiers.clear();
}

std::vector<std::shared_ptr<AnimationModifier>> ProceduralAnimationGenerator::GetModifiers(int boneIndex) const {
    auto it = boneModifiers.find(boneIndex);
    if (it != boneModifiers.end()) {
        return it->second;
    }
    return {};
}

// ============================================================================
// AnimationBlender
// ============================================================================

AnimationBlender::AnimationBlender() {
}

void AnimationBlender::BlendBones(const Bone& bone1, const Bone& bone2, float weight, Bone& result) {
    // Extract transforms
    glm::vec3 pos1 = glm::vec3(bone1.localTransform[3]);
    glm::vec3 pos2 = glm::vec3(bone2.localTransform[3]);
    
    glm::quat rot1 = glm::quat_cast(bone1.localTransform);
    glm::quat rot2 = glm::quat_cast(bone2.localTransform);
    
    glm::vec3 scale1 = glm::vec3(
        glm::length(glm::vec3(bone1.localTransform[0])),
        glm::length(glm::vec3(bone1.localTransform[1])),
        glm::length(glm::vec3(bone1.localTransform[2]))
    );
    glm::vec3 scale2 = glm::vec3(
        glm::length(glm::vec3(bone2.localTransform[0])),
        glm::length(glm::vec3(bone2.localTransform[1])),
        glm::length(glm::vec3(bone2.localTransform[2]))
    );
    
    // Blend
    glm::vec3 blendedPos = glm::mix(pos1, pos2, weight);
    glm::quat blendedRot = glm::slerp(rot1, rot2, weight);
    glm::vec3 blendedScale = glm::mix(scale1, scale2, weight);
    
    // Build result transform
    result.localTransform = glm::translate(glm::mat4(1.0f), blendedPos) *
                           glm::mat4_cast(blendedRot) *
                           glm::scale(glm::mat4(1.0f), blendedScale);
}

void AnimationBlender::BlendMultipleBones(const std::vector<Bone>& bones,
                                         const std::vector<float>& weights,
                                         Bone& result) {
    if (bones.empty() || bones.size() != weights.size()) {
        return;
    }
    
    glm::vec3 blendedPos(0.0f);
    glm::quat blendedRot(1.0f, 0.0f, 0.0f, 0.0f);
    glm::vec3 blendedScale(0.0f);
    
    float totalWeight = 0.0f;
    for (float w : weights) {
        totalWeight += w;
    }
    
    if (totalWeight <= 0.0f) {
        return;
    }
    
    // Blend positions and scales linearly
    for (size_t i = 0; i < bones.size(); ++i) {
        float normalizedWeight = weights[i] / totalWeight;
        
        glm::vec3 pos = glm::vec3(bones[i].localTransform[3]);
        glm::vec3 scale = glm::vec3(
            glm::length(glm::vec3(bones[i].localTransform[0])),
            glm::length(glm::vec3(bones[i].localTransform[1])),
            glm::length(glm::vec3(bones[i].localTransform[2]))
        );
        
        blendedPos += pos * normalizedWeight;
        blendedScale += scale * normalizedWeight;
    }
    
    // Blend rotations using slerp
    blendedRot = glm::quat_cast(bones[0].localTransform);
    for (size_t i = 1; i < bones.size(); ++i) {
        glm::quat rot = glm::quat_cast(bones[i].localTransform);
        float normalizedWeight = weights[i] / totalWeight;
        blendedRot = glm::slerp(blendedRot, rot, normalizedWeight);
    }
    
    // Build result
    result.localTransform = glm::translate(glm::mat4(1.0f), blendedPos) *
                           glm::mat4_cast(blendedRot) *
                           glm::scale(glm::mat4(1.0f), blendedScale);
}

void AnimationBlender::BlendSkeletons(const Skeleton& skeleton1, const Skeleton& skeleton2,
                                     float weight, Skeleton& result) {
    int boneCount = std::min(skeleton1.GetBoneCount(), skeleton2.GetBoneCount());
    
    for (int i = 0; i < boneCount; ++i) {
        const Bone& bone1 = skeleton1.GetBone(i);
        const Bone& bone2 = skeleton2.GetBone(i);
        Bone& resultBone = result.GetBone(i);
        
        BlendBones(bone1, bone2, weight, resultBone);
    }
    
    result.UpdateGlobalTransforms();
}

void AnimationBlender::AdditiveBlend(const Bone& baseBone, const Bone& additiveBone,
                                    float weight, Bone& result) {
    // Extract transforms
    glm::vec3 basePos = glm::vec3(baseBone.localTransform[3]);
    glm::vec3 additivePos = glm::vec3(additiveBone.localTransform[3]);
    
    glm::quat baseRot = glm::quat_cast(baseBone.localTransform);
    glm::quat additiveRot = glm::quat_cast(additiveBone.localTransform);
    
    // Additive blend
    glm::vec3 blendedPos = basePos + (additivePos * weight);
    glm::quat blendedRot = baseRot * glm::slerp(glm::quat(1.0f, 0.0f, 0.0f, 0.0f), additiveRot, weight);
    
    glm::vec3 scale = glm::vec3(
        glm::length(glm::vec3(baseBone.localTransform[0])),
        glm::length(glm::vec3(baseBone.localTransform[1])),
        glm::length(glm::vec3(baseBone.localTransform[2]))
    );
    
    // Build result
    result.localTransform = glm::translate(glm::mat4(1.0f), blendedPos) *
                           glm::mat4_cast(blendedRot) *
                           glm::scale(glm::mat4(1.0f), scale);
}

// ============================================================================
// ProceduralAnimationSystem
// ============================================================================

ProceduralAnimationSystem::ProceduralAnimationSystem()
    : initialized(false)
    , currentTime(0.0f) {
}

ProceduralAnimationSystem::~ProceduralAnimationSystem() {
    Shutdown();
}

bool ProceduralAnimationSystem::Initialize() {
    if (initialized) {
        return true;
    }
    
    initialized = true;
    return true;
}

void ProceduralAnimationSystem::Shutdown() {
    if (!initialized) {
        return;
    }
    
    entityGenerators.clear();
    initialized = false;
}

std::shared_ptr<ProceduralAnimationGenerator> ProceduralAnimationSystem::CreateGenerator() {
    return std::make_shared<ProceduralAnimationGenerator>();
}

std::shared_ptr<NoiseModifier> ProceduralAnimationSystem::CreateNoiseModifier(NoiseType type) {
    return std::make_shared<NoiseModifier>(type);
}

std::shared_ptr<WaveModifier> ProceduralAnimationSystem::CreateWaveModifier() {
    return std::make_shared<WaveModifier>();
}

std::shared_ptr<SpringModifier> ProceduralAnimationSystem::CreateSpringModifier() {
    return std::make_shared<SpringModifier>();
}

std::shared_ptr<CustomModifier> ProceduralAnimationSystem::CreateCustomModifier(CustomModifier::ModifierFunction func) {
    return std::make_shared<CustomModifier>(func);
}

void ProceduralAnimationSystem::RegisterGenerator(int entityId, std::shared_ptr<ProceduralAnimationGenerator> generator) {
    entityGenerators[entityId] = generator;
}

void ProceduralAnimationSystem::UnregisterGenerator(int entityId) {
    entityGenerators.erase(entityId);
}

void ProceduralAnimationSystem::Update(float deltaTime) {
    currentTime += deltaTime;
    
    // Note: Actual application to skeletons would happen in the animation system
    // This is just tracking time for the procedural generators
}

std::shared_ptr<ProceduralAnimationGenerator> ProceduralAnimationSystem::GetGenerator(int entityId) {
    auto it = entityGenerators.find(entityId);
    if (it != entityGenerators.end()) {
        return it->second;
    }
    return nullptr;
}

} // namespace pywrkgame
