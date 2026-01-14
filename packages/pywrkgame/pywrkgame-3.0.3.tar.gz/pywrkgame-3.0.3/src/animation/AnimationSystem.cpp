#include "pywrkgame/animation/AnimationSystem.h"
#include <algorithm>
#include <cmath>
#include <glm/gtx/quaternion.hpp>
#include <glm/gtc/matrix_transform.hpp>

namespace pywrkgame {

// ============================================================================
// Keyframe Interpolation
// ============================================================================

Keyframe AnimationChannel::Interpolate(float time) const {
    if (keyframes.empty()) {
        return Keyframe();
    }
    
    if (keyframes.size() == 1 || time <= keyframes[0].time) {
        return keyframes[0];
    }
    
    if (time >= keyframes.back().time) {
        return keyframes.back();
    }
    
    // Find the two keyframes to interpolate between
    size_t nextIndex = 0;
    for (size_t i = 0; i < keyframes.size(); ++i) {
        if (keyframes[i].time > time) {
            nextIndex = i;
            break;
        }
    }
    
    size_t prevIndex = nextIndex - 1;
    const Keyframe& prev = keyframes[prevIndex];
    const Keyframe& next = keyframes[nextIndex];
    
    // Calculate interpolation factor
    float timeDiff = next.time - prev.time;
    float factor = (time - prev.time) / timeDiff;
    
    // Interpolate
    Keyframe result;
    result.time = time;
    result.position = glm::mix(prev.position, next.position, factor);
    result.rotation = glm::slerp(prev.rotation, next.rotation, factor);
    result.scale = glm::mix(prev.scale, next.scale, factor);
    
    return result;
}

// ============================================================================
// AnimationClip
// ============================================================================

AnimationClip::AnimationClip(const std::string& name, float duration)
    : name(name), duration(duration) {
}

void AnimationClip::AddChannel(const AnimationChannel& channel) {
    channels.push_back(channel);
}

// ============================================================================
// Skeleton
// ============================================================================

Skeleton::Skeleton() {
}

int Skeleton::AddBone(const Bone& bone) {
    int index = static_cast<int>(bones.size());
    bones.push_back(bone);
    boneNameToIndex[bone.name] = index;
    return index;
}

Bone& Skeleton::GetBone(int index) {
    return bones[index];
}

const Bone& Skeleton::GetBone(int index) const {
    return bones[index];
}

int Skeleton::FindBoneIndex(const std::string& name) const {
    auto it = boneNameToIndex.find(name);
    if (it != boneNameToIndex.end()) {
        return it->second;
    }
    return -1;
}

void Skeleton::UpdateGlobalTransforms() {
    for (size_t i = 0; i < bones.size(); ++i) {
        Bone& bone = bones[i];
        
        if (bone.parentIndex == -1) {
            // Root bone
            bone.globalTransform = bone.localTransform;
        } else {
            // Child bone
            const Bone& parent = bones[bone.parentIndex];
            bone.globalTransform = parent.globalTransform * bone.localTransform;
        }
    }
}

void Skeleton::ApplyConstraints() {
    for (Bone& bone : bones) {
        if (bone.hasRotationConstraint) {
            // Extract rotation from local transform
            glm::quat rotation = glm::quat_cast(bone.localTransform);
            glm::vec3 euler = glm::eulerAngles(rotation);
            
            // Apply constraints
            euler.x = glm::clamp(euler.x, glm::radians(bone.minRotation.x), glm::radians(bone.maxRotation.x));
            euler.y = glm::clamp(euler.y, glm::radians(bone.minRotation.y), glm::radians(bone.maxRotation.y));
            euler.z = glm::clamp(euler.z, glm::radians(bone.minRotation.z), glm::radians(bone.maxRotation.z));
            
            // Reconstruct transform
            glm::quat constrainedRotation = glm::quat(euler);
            glm::vec3 position = glm::vec3(bone.localTransform[3]);
            glm::vec3 scale = glm::vec3(
                glm::length(glm::vec3(bone.localTransform[0])),
                glm::length(glm::vec3(bone.localTransform[1])),
                glm::length(glm::vec3(bone.localTransform[2]))
            );
            
            bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                                 glm::mat4_cast(constrainedRotation) *
                                 glm::scale(glm::mat4(1.0f), scale);
        }
        
        if (bone.hasPositionConstraint) {
            glm::vec3 position = glm::vec3(bone.localTransform[3]);
            position.x = glm::clamp(position.x, bone.minPosition.x, bone.maxPosition.x);
            position.y = glm::clamp(position.y, bone.minPosition.y, bone.maxPosition.y);
            position.z = glm::clamp(position.z, bone.minPosition.z, bone.maxPosition.z);
            bone.localTransform[3] = glm::vec4(position, 1.0f);
        }
    }
}

std::vector<glm::mat4> Skeleton::GetBoneMatrices() const {
    std::vector<glm::mat4> matrices;
    matrices.reserve(bones.size());
    
    for (const Bone& bone : bones) {
        matrices.push_back(bone.globalTransform * bone.offsetMatrix);
    }
    
    return matrices;
}

// ============================================================================
// SkeletalMesh
// ============================================================================

SkeletalMesh::SkeletalMesh() {
}

void SkeletalMesh::SetVertices(const std::vector<Vertex>& verts) {
    vertices = verts;
}

void SkeletalMesh::SetSkeleton(std::shared_ptr<Skeleton> skel) {
    skeleton = skel;
}

std::vector<glm::vec3> SkeletalMesh::GetDeformedPositions(const std::vector<glm::mat4>& boneMatrices) const {
    std::vector<glm::vec3> deformedPositions;
    deformedPositions.reserve(vertices.size());
    
    for (const Vertex& vertex : vertices) {
        glm::vec4 position(0.0f);
        
        for (const VertexWeight& weight : vertex.weights) {
            if (weight.boneIndex >= 0 && weight.boneIndex < static_cast<int>(boneMatrices.size())) {
                glm::vec4 transformedPos = boneMatrices[weight.boneIndex] * glm::vec4(vertex.position, 1.0f);
                position += transformedPos * weight.weight;
            }
        }
        
        deformedPositions.push_back(glm::vec3(position));
    }
    
    return deformedPositions;
}

std::vector<glm::vec3> SkeletalMesh::GetDeformedNormals(const std::vector<glm::mat4>& boneMatrices) const {
    std::vector<glm::vec3> deformedNormals;
    deformedNormals.reserve(vertices.size());
    
    for (const Vertex& vertex : vertices) {
        glm::vec3 normal(0.0f);
        
        for (const VertexWeight& weight : vertex.weights) {
            if (weight.boneIndex >= 0 && weight.boneIndex < static_cast<int>(boneMatrices.size())) {
                glm::mat3 normalMatrix = glm::mat3(glm::transpose(glm::inverse(boneMatrices[weight.boneIndex])));
                glm::vec3 transformedNormal = normalMatrix * vertex.normal;
                normal += transformedNormal * weight.weight;
            }
        }
        
        if (glm::length(normal) > 0.0f) {
            normal = glm::normalize(normal);
        }
        
        deformedNormals.push_back(normal);
    }
    
    return deformedNormals;
}

// ============================================================================
// AnimationSystem
// ============================================================================

AnimationSystem::AnimationSystem() : initialized(false) {
}

AnimationSystem::~AnimationSystem() {
    Shutdown();
}

bool AnimationSystem::Initialize() {
    if (initialized) {
        return true;
    }
    
    initialized = true;
    return true;
}

void AnimationSystem::Shutdown() {
    if (!initialized) {
        return;
    }
    
    animationClips.clear();
    entityAnimations.clear();
    initialized = false;
}

std::shared_ptr<AnimationClip> AnimationSystem::LoadAnimationClip(const std::string& name, float duration) {
    auto clip = std::make_shared<AnimationClip>(name, duration);
    animationClips[name] = clip;
    return clip;
}

std::shared_ptr<AnimationClip> AnimationSystem::GetAnimationClip(const std::string& name) {
    auto it = animationClips.find(name);
    if (it != animationClips.end()) {
        return it->second;
    }
    return nullptr;
}

std::shared_ptr<Skeleton> AnimationSystem::CreateSkeleton() {
    return std::make_shared<Skeleton>();
}

std::shared_ptr<SkeletalMesh> AnimationSystem::CreateSkeletalMesh() {
    return std::make_shared<SkeletalMesh>();
}

void AnimationSystem::PlayAnimation(int entityId, std::shared_ptr<AnimationClip> clip, bool loop) {
    AnimationState state;
    state.clip = clip;
    state.currentTime = 0.0f;
    state.isPlaying = true;
    state.isLooping = loop;
    state.playbackSpeed = 1.0f;
    
    entityAnimations[entityId] = state;
}

void AnimationSystem::StopAnimation(int entityId) {
    entityAnimations.erase(entityId);
}

void AnimationSystem::PauseAnimation(int entityId) {
    auto it = entityAnimations.find(entityId);
    if (it != entityAnimations.end()) {
        it->second.isPlaying = false;
    }
}

void AnimationSystem::ResumeAnimation(int entityId) {
    auto it = entityAnimations.find(entityId);
    if (it != entityAnimations.end()) {
        it->second.isPlaying = true;
    }
}

void AnimationSystem::SetPlaybackSpeed(int entityId, float speed) {
    auto it = entityAnimations.find(entityId);
    if (it != entityAnimations.end()) {
        it->second.playbackSpeed = speed;
    }
}

void AnimationSystem::Update(float deltaTime) {
    for (auto& pair : entityAnimations) {
        AnimationState& state = pair.second;
        
        if (!state.isPlaying || !state.clip) {
            continue;
        }
        
        state.currentTime += deltaTime * state.playbackSpeed;
        
        // Handle looping
        if (state.currentTime >= state.clip->GetDuration()) {
            if (state.isLooping) {
                state.currentTime = std::fmod(state.currentTime, state.clip->GetDuration());
            } else {
                state.currentTime = state.clip->GetDuration();
                state.isPlaying = false;
            }
        }
    }
}

AnimationState* AnimationSystem::GetAnimationState(int entityId) {
    auto it = entityAnimations.find(entityId);
    if (it != entityAnimations.end()) {
        return &it->second;
    }
    return nullptr;
}

void AnimationSystem::ApplyAnimation(Skeleton& skeleton, const AnimationClip& clip, float time) {
    for (const AnimationChannel& channel : clip.GetChannels()) {
        if (channel.boneIndex < 0 || channel.boneIndex >= skeleton.GetBoneCount()) {
            continue;
        }
        
        Keyframe frame = channel.Interpolate(time);
        Bone& bone = skeleton.GetBone(channel.boneIndex);
        
        // Build transform matrix from keyframe
        glm::mat4 translation = glm::translate(glm::mat4(1.0f), frame.position);
        glm::mat4 rotation = glm::mat4_cast(frame.rotation);
        glm::mat4 scale = glm::scale(glm::mat4(1.0f), frame.scale);
        
        bone.localTransform = translation * rotation * scale;
    }
    
    skeleton.ApplyConstraints();
    skeleton.UpdateGlobalTransforms();
}

} // namespace pywrkgame
