#pragma once

#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#define GLM_ENABLE_EXPERIMENTAL
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

namespace pywrkgame {

// Forward declarations
class AnimationClip;
class Skeleton;
class SkeletalMesh;

// Bone structure representing a single bone in the skeleton
struct Bone {
    std::string name;
    int parentIndex;  // -1 for root bone
    glm::mat4 offsetMatrix;  // Transform from mesh space to bone space
    glm::mat4 localTransform;  // Local transform relative to parent
    glm::mat4 globalTransform;  // Global transform in model space
    
    // Constraints
    bool hasRotationConstraint;
    glm::vec3 minRotation;
    glm::vec3 maxRotation;
    
    bool hasPositionConstraint;
    glm::vec3 minPosition;
    glm::vec3 maxPosition;
    
    Bone() 
        : parentIndex(-1)
        , offsetMatrix(1.0f)
        , localTransform(1.0f)
        , globalTransform(1.0f)
        , hasRotationConstraint(false)
        , minRotation(-180.0f)
        , maxRotation(180.0f)
        , hasPositionConstraint(false)
        , minPosition(-1000.0f)
        , maxPosition(1000.0f)
    {}
};

// Keyframe for animation
struct Keyframe {
    float time;
    glm::vec3 position;
    glm::quat rotation;
    glm::vec3 scale;
    
    Keyframe() 
        : time(0.0f)
        , position(0.0f)
        , rotation(1.0f, 0.0f, 0.0f, 0.0f)
        , scale(1.0f)
    {}
};

// Animation channel for a single bone
struct AnimationChannel {
    int boneIndex;
    std::vector<Keyframe> keyframes;
    
    AnimationChannel() : boneIndex(-1) {}
    
    // Interpolate between keyframes at given time
    Keyframe Interpolate(float time) const;
};

// Animation clip containing all animation data
class AnimationClip {
public:
    AnimationClip(const std::string& name, float duration);
    
    void AddChannel(const AnimationChannel& channel);
    const std::vector<AnimationChannel>& GetChannels() const { return channels; }
    
    float GetDuration() const { return duration; }
    const std::string& GetName() const { return name; }
    
private:
    std::string name;
    float duration;
    std::vector<AnimationChannel> channels;
};

// Skeleton representing bone hierarchy
class Skeleton {
public:
    Skeleton();
    
    int AddBone(const Bone& bone);
    Bone& GetBone(int index);
    const Bone& GetBone(int index) const;
    
    int GetBoneCount() const { return static_cast<int>(bones.size()); }
    int FindBoneIndex(const std::string& name) const;
    
    // Update global transforms based on local transforms
    void UpdateGlobalTransforms();
    
    // Apply constraints to bone transforms
    void ApplyConstraints();
    
    // Get final bone matrices for skinning
    std::vector<glm::mat4> GetBoneMatrices() const;
    
private:
    std::vector<Bone> bones;
    std::unordered_map<std::string, int> boneNameToIndex;
};

// Animation state for playback
struct AnimationState {
    std::shared_ptr<AnimationClip> clip;
    float currentTime;
    bool isPlaying;
    bool isLooping;
    float playbackSpeed;
    
    AnimationState()
        : currentTime(0.0f)
        , isPlaying(false)
        , isLooping(true)
        , playbackSpeed(1.0f)
    {}
};

// Skeletal mesh with bone weights
class SkeletalMesh {
public:
    struct VertexWeight {
        int boneIndex;
        float weight;
    };
    
    struct Vertex {
        glm::vec3 position;
        glm::vec3 normal;
        glm::vec2 texCoord;
        std::vector<VertexWeight> weights;  // Up to 4 weights per vertex
    };
    
    SkeletalMesh();
    
    void SetVertices(const std::vector<Vertex>& verts);
    void SetSkeleton(std::shared_ptr<Skeleton> skel);
    
    const std::vector<Vertex>& GetVertices() const { return vertices; }
    std::shared_ptr<Skeleton> GetSkeleton() const { return skeleton; }
    
    // Apply bone transforms to vertices
    std::vector<glm::vec3> GetDeformedPositions(const std::vector<glm::mat4>& boneMatrices) const;
    std::vector<glm::vec3> GetDeformedNormals(const std::vector<glm::mat4>& boneMatrices) const;
    
private:
    std::vector<Vertex> vertices;
    std::shared_ptr<Skeleton> skeleton;
};

// Main animation system
class AnimationSystem {
public:
    AnimationSystem();
    ~AnimationSystem();
    
    bool Initialize();
    void Shutdown();
    
    // Animation clip management
    std::shared_ptr<AnimationClip> LoadAnimationClip(const std::string& name, float duration);
    std::shared_ptr<AnimationClip> GetAnimationClip(const std::string& name);
    
    // Skeleton management
    std::shared_ptr<Skeleton> CreateSkeleton();
    
    // Skeletal mesh management
    std::shared_ptr<SkeletalMesh> CreateSkeletalMesh();
    
    // Animation playback
    void PlayAnimation(int entityId, std::shared_ptr<AnimationClip> clip, bool loop = true);
    void StopAnimation(int entityId);
    void PauseAnimation(int entityId);
    void ResumeAnimation(int entityId);
    void SetPlaybackSpeed(int entityId, float speed);
    
    // Update all active animations
    void Update(float deltaTime);
    
    // Get animation state for entity
    AnimationState* GetAnimationState(int entityId);
    
private:
    bool initialized;
    std::unordered_map<std::string, std::shared_ptr<AnimationClip>> animationClips;
    std::unordered_map<int, AnimationState> entityAnimations;
    
    // Apply animation clip to skeleton at given time
    void ApplyAnimation(Skeleton& skeleton, const AnimationClip& clip, float time);
};

} // namespace pywrkgame
