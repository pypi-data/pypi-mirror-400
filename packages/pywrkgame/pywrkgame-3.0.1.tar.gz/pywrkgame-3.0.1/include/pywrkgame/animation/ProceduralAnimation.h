#pragma once

#include <vector>
#include <memory>
#include <functional>
#define GLM_ENABLE_EXPERIMENTAL
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

namespace pywrkgame {

// Forward declarations
class Skeleton;
struct Bone;

// Noise types for procedural animation
enum class NoiseType {
    Perlin,
    Simplex,
    Worley,
    White
};

// Procedural animation modifier types
enum class ModifierType {
    Noise,
    Wave,
    Spring,
    Damping,
    Custom
};

// Noise generator for procedural effects
class NoiseGenerator {
public:
    NoiseGenerator(NoiseType type = NoiseType::Perlin);
    
    // Generate 1D noise
    float Generate1D(float x, float frequency = 1.0f, float amplitude = 1.0f) const;
    
    // Generate 2D noise
    float Generate2D(float x, float y, float frequency = 1.0f, float amplitude = 1.0f) const;
    
    // Generate 3D noise
    float Generate3D(float x, float y, float z, float frequency = 1.0f, float amplitude = 1.0f) const;
    
    // Generate fractal noise (multiple octaves)
    float GenerateFractal(float x, float y, float z, int octaves = 4, 
                         float lacunarity = 2.0f, float persistence = 0.5f) const;
    
    void SetSeed(unsigned int seed);
    void SetType(NoiseType type) { noiseType = type; }
    
private:
    NoiseType noiseType;
    unsigned int seed;
    
    // Perlin noise implementation
    float PerlinNoise(float x, float y, float z) const;
    
    // Simplex noise implementation
    float SimplexNoise(float x, float y, float z) const;
    
    // Worley noise implementation
    float WorleyNoise(float x, float y, float z) const;
    
    // White noise implementation
    float WhiteNoise(float x, float y, float z) const;
    
    // Helper functions
    float Fade(float t) const;
    float Lerp(float t, float a, float b) const;
    float Grad(int hash, float x, float y, float z) const;
};

// Wave parameters for oscillating animations
struct WaveParameters {
    float frequency;
    float amplitude;
    float phase;
    glm::vec3 direction;
    
    WaveParameters()
        : frequency(1.0f)
        , amplitude(1.0f)
        , phase(0.0f)
        , direction(0.0f, 1.0f, 0.0f)
    {}
};

// Spring parameters for physics-based animation
struct SpringParameters {
    float stiffness;
    float damping;
    float mass;
    glm::vec3 restPosition;
    glm::vec3 velocity;
    
    SpringParameters()
        : stiffness(100.0f)
        , damping(10.0f)
        , mass(1.0f)
        , restPosition(0.0f)
        , velocity(0.0f)
    {}
};

// Base class for animation modifiers
class AnimationModifier {
public:
    virtual ~AnimationModifier() = default;
    
    // Apply modifier to bone transform
    virtual void Apply(Bone& bone, float time, float deltaTime) = 0;
    
    // Set modifier strength (0-1)
    void SetStrength(float strength) { this->strength = glm::clamp(strength, 0.0f, 1.0f); }
    float GetStrength() const { return strength; }
    
    // Enable/disable modifier
    void SetEnabled(bool enabled) { this->enabled = enabled; }
    bool IsEnabled() const { return enabled; }
    
protected:
    float strength = 1.0f;
    bool enabled = true;
};

// Noise-based animation modifier
class NoiseModifier : public AnimationModifier {
public:
    NoiseModifier(NoiseType type = NoiseType::Perlin);
    
    void Apply(Bone& bone, float time, float deltaTime) override;
    
    void SetNoiseType(NoiseType type);
    void SetFrequency(float freq) { frequency = freq; }
    void SetAmplitude(float amp) { amplitude = amp; }
    void SetOctaves(int oct) { octaves = oct; }
    
    void SetAffectPosition(bool affect) { affectPosition = affect; }
    void SetAffectRotation(bool affect) { affectRotation = affect; }
    void SetAffectScale(bool affect) { affectScale = affect; }
    
private:
    NoiseGenerator noiseGen;
    float frequency;
    float amplitude;
    int octaves;
    bool affectPosition;
    bool affectRotation;
    bool affectScale;
};

// Wave-based animation modifier
class WaveModifier : public AnimationModifier {
public:
    WaveModifier();
    
    void Apply(Bone& bone, float time, float deltaTime) override;
    
    void SetWaveParameters(const WaveParameters& params) { waveParams = params; }
    const WaveParameters& GetWaveParameters() const { return waveParams; }
    
    void SetAffectPosition(bool affect) { affectPosition = affect; }
    void SetAffectRotation(bool affect) { affectRotation = affect; }
    
private:
    WaveParameters waveParams;
    bool affectPosition;
    bool affectRotation;
};

// Spring-based physics animation modifier
class SpringModifier : public AnimationModifier {
public:
    SpringModifier();
    
    void Apply(Bone& bone, float time, float deltaTime) override;
    
    void SetSpringParameters(const SpringParameters& params) { springParams = params; }
    const SpringParameters& GetSpringParameters() const { return springParams; }
    
    void SetTarget(const glm::vec3& target);
    void ApplyForce(const glm::vec3& force);
    
    void Reset();
    
private:
    SpringParameters springParams;
    glm::vec3 currentPosition;
    glm::vec3 targetPosition;
    glm::vec3 externalForce;
};

// Custom modifier using user-defined function
class CustomModifier : public AnimationModifier {
public:
    using ModifierFunction = std::function<void(Bone&, float, float)>;
    
    CustomModifier(ModifierFunction func);
    
    void Apply(Bone& bone, float time, float deltaTime) override;
    
    void SetFunction(ModifierFunction func) { modifierFunc = func; }
    
private:
    ModifierFunction modifierFunc;
};

// Procedural animation generator
class ProceduralAnimationGenerator {
public:
    ProceduralAnimationGenerator();
    
    // Add modifier to specific bone
    void AddModifier(int boneIndex, std::shared_ptr<AnimationModifier> modifier);
    
    // Remove all modifiers from bone
    void RemoveModifiers(int boneIndex);
    
    // Remove specific modifier
    void RemoveModifier(int boneIndex, std::shared_ptr<AnimationModifier> modifier);
    
    // Apply all modifiers to skeleton
    void Apply(Skeleton& skeleton, float time, float deltaTime);
    
    // Clear all modifiers
    void Clear();
    
    // Get modifiers for bone
    std::vector<std::shared_ptr<AnimationModifier>> GetModifiers(int boneIndex) const;
    
private:
    std::unordered_map<int, std::vector<std::shared_ptr<AnimationModifier>>> boneModifiers;
};

// Animation blending system
class AnimationBlender {
public:
    AnimationBlender();
    
    // Blend between two bone transforms
    static void BlendBones(const Bone& bone1, const Bone& bone2, float weight, Bone& result);
    
    // Blend multiple bone transforms with weights
    static void BlendMultipleBones(const std::vector<Bone>& bones, 
                                   const std::vector<float>& weights, 
                                   Bone& result);
    
    // Blend two skeletons
    static void BlendSkeletons(const Skeleton& skeleton1, const Skeleton& skeleton2, 
                              float weight, Skeleton& result);
    
    // Additive blending
    static void AdditiveBlend(const Bone& baseBone, const Bone& additiveBone, 
                             float weight, Bone& result);
};

// Procedural animation system
class ProceduralAnimationSystem {
public:
    ProceduralAnimationSystem();
    ~ProceduralAnimationSystem();
    
    bool Initialize();
    void Shutdown();
    
    // Create procedural animation generator
    std::shared_ptr<ProceduralAnimationGenerator> CreateGenerator();
    
    // Create modifiers
    std::shared_ptr<NoiseModifier> CreateNoiseModifier(NoiseType type = NoiseType::Perlin);
    std::shared_ptr<WaveModifier> CreateWaveModifier();
    std::shared_ptr<SpringModifier> CreateSpringModifier();
    std::shared_ptr<CustomModifier> CreateCustomModifier(CustomModifier::ModifierFunction func);
    
    // Register generator for entity
    void RegisterGenerator(int entityId, std::shared_ptr<ProceduralAnimationGenerator> generator);
    void UnregisterGenerator(int entityId);
    
    // Update all registered generators
    void Update(float deltaTime);
    
    // Get generator for entity
    std::shared_ptr<ProceduralAnimationGenerator> GetGenerator(int entityId);
    
private:
    bool initialized;
    float currentTime;
    std::unordered_map<int, std::shared_ptr<ProceduralAnimationGenerator>> entityGenerators;
};

} // namespace pywrkgame
