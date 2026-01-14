#include "pywrkgame/animation/IKSolver.h"
#include "pywrkgame/animation/AnimationSystem.h"
#include <algorithm>
#include <cmath>
#include <glm/gtx/quaternion.hpp>
#include <glm/gtc/matrix_transform.hpp>

namespace pywrkgame {

// ============================================================================
// IKChain
// ============================================================================

IKChain::IKChain()
    : endEffectorIndex(-1)
    , maxIterations(10)
    , tolerance(0.01f) {
}

void IKChain::AddBone(int boneIndex) {
    boneIndices.push_back(boneIndex);
}

void IKChain::SetEndEffector(int boneIndex) {
    endEffectorIndex = boneIndex;
}

void IKChain::SetConstraint(int boneIndex, const IKConstraint& constraint) {
    constraints[boneIndex] = constraint;
}

const IKConstraint& IKChain::GetConstraint(int boneIndex) const {
    static IKConstraint defaultConstraint;
    auto it = constraints.find(boneIndex);
    if (it != constraints.end()) {
        return it->second;
    }
    return defaultConstraint;
}

// ============================================================================
// IKSolver Base
// ============================================================================

IKSolver::IKSolver() {
}

IKSolver::~IKSolver() {
}

bool IKSolver::SolveWithOrientation(Skeleton& skeleton, const IKChain& chain,
                                   const glm::vec3& targetPosition,
                                   const glm::quat& targetOrientation) {
    // Default implementation: just solve for position
    // Derived classes can override for orientation support
    return Solve(skeleton, chain, targetPosition);
}

glm::vec3 IKSolver::GetBoneWorldPosition(const Skeleton& skeleton, int boneIndex) const {
    const Bone& bone = skeleton.GetBone(boneIndex);
    return glm::vec3(bone.globalTransform[3]);
}

glm::quat IKSolver::ApplyConstraint(const glm::quat& rotation, const IKConstraint& constraint) const {
    if (constraint.type == IKConstraintType::None) {
        return rotation;
    }
    
    if (constraint.type == IKConstraintType::FixedJoint) {
        return glm::quat(1.0f, 0.0f, 0.0f, 0.0f);  // Identity rotation
    }
    
    if (constraint.type == IKConstraintType::HingeJoint) {
        // Project rotation onto constraint axis
        glm::vec3 euler = glm::eulerAngles(rotation);
        float angle = glm::dot(euler, constraint.axis);
        angle = glm::clamp(angle, constraint.minAngle, constraint.maxAngle);
        return glm::angleAxis(angle, constraint.axis);
    }
    
    if (constraint.type == IKConstraintType::BallJoint) {
        // Clamp rotation angles
        glm::vec3 euler = glm::eulerAngles(rotation);
        euler.x = glm::clamp(euler.x, constraint.minAngle, constraint.maxAngle);
        euler.y = glm::clamp(euler.y, constraint.minAngle, constraint.maxAngle);
        euler.z = glm::clamp(euler.z, constraint.minAngle, constraint.maxAngle);
        return glm::quat(euler);
    }
    
    return rotation;
}

float IKSolver::GetBoneLength(const Skeleton& skeleton, int boneIndex) const {
    const Bone& bone = skeleton.GetBone(boneIndex);
    glm::vec3 localPos = glm::vec3(bone.localTransform[3]);
    return glm::length(localPos);
}

// ============================================================================
// CCD Solver
// ============================================================================

CCDSolver::CCDSolver() : IKSolver() {
}

bool CCDSolver::Solve(Skeleton& skeleton, const IKChain& chain, const glm::vec3& targetPosition) {
    const std::vector<int>& bones = chain.GetBones();
    if (bones.empty()) {
        return false;
    }
    
    int endEffectorIndex = chain.GetEndEffector();
    if (endEffectorIndex < 0) {
        endEffectorIndex = bones.back();
    }
    
    // Iteratively solve
    for (int iter = 0; iter < chain.GetMaxIterations(); ++iter) {
        skeleton.UpdateGlobalTransforms();
        
        glm::vec3 endEffectorPos = GetBoneWorldPosition(skeleton, endEffectorIndex);
        float distance = glm::length(endEffectorPos - targetPosition);
        
        // Check if we've reached the target
        if (distance < chain.GetTolerance()) {
            return true;
        }
        
        // Iterate through bones from end to root
        for (int i = static_cast<int>(bones.size()) - 1; i >= 0; --i) {
            int boneIndex = bones[i];
            
            skeleton.UpdateGlobalTransforms();
            endEffectorPos = GetBoneWorldPosition(skeleton, endEffectorIndex);
            
            // Rotate this bone to point towards target
            RotateBoneToTarget(skeleton, boneIndex, endEffectorPos, targetPosition);
            
            // Apply constraints
            Bone& bone = skeleton.GetBone(boneIndex);
            glm::quat rotation = glm::quat_cast(bone.localTransform);
            rotation = ApplyConstraint(rotation, chain.GetConstraint(boneIndex));
            
            // Rebuild transform
            glm::vec3 position = glm::vec3(bone.localTransform[3]);
            glm::vec3 scale = glm::vec3(
                glm::length(glm::vec3(bone.localTransform[0])),
                glm::length(glm::vec3(bone.localTransform[1])),
                glm::length(glm::vec3(bone.localTransform[2]))
            );
            
            bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                                 glm::mat4_cast(rotation) *
                                 glm::scale(glm::mat4(1.0f), scale);
        }
    }
    
    // Check final distance
    skeleton.UpdateGlobalTransforms();
    glm::vec3 endEffectorPos = GetBoneWorldPosition(skeleton, endEffectorIndex);
    float finalDistance = glm::length(endEffectorPos - targetPosition);
    
    return finalDistance < chain.GetTolerance() * 10.0f;  // Allow some tolerance
}

void CCDSolver::RotateBoneToTarget(Skeleton& skeleton, int boneIndex,
                                  const glm::vec3& endEffectorPos,
                                  const glm::vec3& targetPos) {
    Bone& bone = skeleton.GetBone(boneIndex);
    glm::vec3 bonePos = GetBoneWorldPosition(skeleton, boneIndex);
    
    // Calculate vectors
    glm::vec3 toEndEffector = glm::normalize(endEffectorPos - bonePos);
    glm::vec3 toTarget = glm::normalize(targetPos - bonePos);
    
    // Calculate rotation needed
    float dot = glm::dot(toEndEffector, toTarget);
    if (dot > 0.9999f) {
        return;  // Already aligned
    }
    
    glm::vec3 axis = glm::cross(toEndEffector, toTarget);
    if (glm::length(axis) < 0.0001f) {
        return;  // Vectors are parallel
    }
    
    axis = glm::normalize(axis);
    float angle = std::acos(glm::clamp(dot, -1.0f, 1.0f));
    
    glm::quat rotation = glm::angleAxis(angle, axis);
    
    // Apply rotation to bone's local transform
    glm::quat currentRotation = glm::quat_cast(bone.localTransform);
    glm::quat newRotation = rotation * currentRotation;
    
    // Rebuild transform
    glm::vec3 position = glm::vec3(bone.localTransform[3]);
    glm::vec3 scale = glm::vec3(
        glm::length(glm::vec3(bone.localTransform[0])),
        glm::length(glm::vec3(bone.localTransform[1])),
        glm::length(glm::vec3(bone.localTransform[2]))
    );
    
    bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                         glm::mat4_cast(newRotation) *
                         glm::scale(glm::mat4(1.0f), scale);
}

// ============================================================================
// FABRIK Solver
// ============================================================================

FABRIKSolver::FABRIKSolver() : IKSolver() {
}

bool FABRIKSolver::Solve(Skeleton& skeleton, const IKChain& chain, const glm::vec3& targetPosition) {
    const std::vector<int>& bones = chain.GetBones();
    if (bones.empty()) {
        return false;
    }
    
    // Get initial positions and bone lengths
    skeleton.UpdateGlobalTransforms();
    
    std::vector<glm::vec3> positions;
    std::vector<float> boneLengths;
    
    for (int boneIndex : bones) {
        positions.push_back(GetBoneWorldPosition(skeleton, boneIndex));
    }
    
    // Add end effector position
    int endEffectorIndex = chain.GetEndEffector();
    if (endEffectorIndex < 0) {
        endEffectorIndex = bones.back();
    }
    positions.push_back(GetBoneWorldPosition(skeleton, endEffectorIndex));
    
    // Calculate bone lengths
    for (size_t i = 0; i < positions.size() - 1; ++i) {
        float length = glm::length(positions[i + 1] - positions[i]);
        boneLengths.push_back(length);
    }
    
    glm::vec3 rootPosition = positions[0];
    
    // Check if target is reachable
    float totalLength = 0.0f;
    for (float length : boneLengths) {
        totalLength += length;
    }
    
    float distanceToTarget = glm::length(targetPosition - rootPosition);
    if (distanceToTarget > totalLength) {
        // Target is unreachable, stretch towards it
        glm::vec3 direction = glm::normalize(targetPosition - rootPosition);
        float currentLength = 0.0f;
        positions[0] = rootPosition;
        for (size_t i = 0; i < boneLengths.size(); ++i) {
            currentLength += boneLengths[i];
            positions[i + 1] = rootPosition + direction * currentLength;
        }
        
        ApplyPositionsToSkeleton(skeleton, chain, positions);
        return false;
    }
    
    // Iteratively solve
    for (int iter = 0; iter < chain.GetMaxIterations(); ++iter) {
        float distance = glm::length(positions.back() - targetPosition);
        
        if (distance < chain.GetTolerance()) {
            ApplyPositionsToSkeleton(skeleton, chain, positions);
            return true;
        }
        
        // Forward reaching
        ForwardReach(positions, targetPosition, boneLengths);
        
        // Backward reaching
        BackwardReach(positions, rootPosition, boneLengths);
    }
    
    ApplyPositionsToSkeleton(skeleton, chain, positions);
    
    float finalDistance = glm::length(positions.back() - targetPosition);
    return finalDistance < chain.GetTolerance() * 10.0f;
}

void FABRIKSolver::ForwardReach(std::vector<glm::vec3>& positions, const glm::vec3& target,
                               const std::vector<float>& boneLengths) {
    // Set end effector to target
    positions.back() = target;
    
    // Work backwards from end to root
    for (int i = static_cast<int>(positions.size()) - 2; i >= 0; --i) {
        glm::vec3 direction = glm::normalize(positions[i] - positions[i + 1]);
        positions[i] = positions[i + 1] + direction * boneLengths[i];
    }
}

void FABRIKSolver::BackwardReach(std::vector<glm::vec3>& positions, const glm::vec3& root,
                                const std::vector<float>& boneLengths) {
    // Set root to original position
    positions[0] = root;
    
    // Work forwards from root to end
    for (size_t i = 0; i < positions.size() - 1; ++i) {
        glm::vec3 direction = glm::normalize(positions[i + 1] - positions[i]);
        positions[i + 1] = positions[i] + direction * boneLengths[i];
    }
}

void FABRIKSolver::ApplyPositionsToSkeleton(Skeleton& skeleton, const IKChain& chain,
                                           const std::vector<glm::vec3>& positions) {
    const std::vector<int>& bones = chain.GetBones();
    
    for (size_t i = 0; i < bones.size(); ++i) {
        int boneIndex = bones[i];
        Bone& bone = skeleton.GetBone(boneIndex);
        
        // Calculate rotation from old direction to new direction
        glm::vec3 oldDir = glm::vec3(0.0f, 1.0f, 0.0f);  // Default bone direction
        if (i + 1 < positions.size()) {
            glm::vec3 newDir = glm::normalize(positions[i + 1] - positions[i]);
            
            glm::quat rotation = glm::rotation(oldDir, newDir);
            
            // Apply constraint
            rotation = ApplyConstraint(rotation, chain.GetConstraint(boneIndex));
            
            // Update bone transform
            glm::vec3 position = glm::vec3(bone.localTransform[3]);
            glm::vec3 scale = glm::vec3(
                glm::length(glm::vec3(bone.localTransform[0])),
                glm::length(glm::vec3(bone.localTransform[1])),
                glm::length(glm::vec3(bone.localTransform[2]))
            );
            
            bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                                 glm::mat4_cast(rotation) *
                                 glm::scale(glm::mat4(1.0f), scale);
        }
    }
    
    skeleton.UpdateGlobalTransforms();
}

// ============================================================================
// Jacobian Solver
// ============================================================================

JacobianSolver::JacobianSolver() 
    : IKSolver()
    , dampingFactor(0.1f) {
}

bool JacobianSolver::Solve(Skeleton& skeleton, const IKChain& chain, const glm::vec3& targetPosition) {
    const std::vector<int>& bones = chain.GetBones();
    if (bones.empty()) {
        return false;
    }
    
    int endEffectorIndex = chain.GetEndEffector();
    if (endEffectorIndex < 0) {
        endEffectorIndex = bones.back();
    }
    
    // Iteratively solve
    for (int iter = 0; iter < chain.GetMaxIterations(); ++iter) {
        skeleton.UpdateGlobalTransforms();
        
        glm::vec3 endEffectorPos = GetBoneWorldPosition(skeleton, endEffectorIndex);
        glm::vec3 error = targetPosition - endEffectorPos;
        
        float distance = glm::length(error);
        if (distance < chain.GetTolerance()) {
            return true;
        }
        
        // Compute Jacobian
        std::vector<std::vector<float>> jacobian;
        ComputeJacobian(skeleton, chain, endEffectorPos, jacobian);
        
        // Solve for joint angle changes
        std::vector<float> errorVec = {error.x, error.y, error.z};
        std::vector<float> deltaAngles = SolveDampedLeastSquares(jacobian, errorVec);
        
        // Apply angle changes to bones
        for (size_t i = 0; i < bones.size() && i < deltaAngles.size(); ++i) {
            int boneIndex = bones[i];
            Bone& bone = skeleton.GetBone(boneIndex);
            
            // Apply rotation change
            glm::quat currentRotation = glm::quat_cast(bone.localTransform);
            glm::quat deltaRotation = glm::angleAxis(deltaAngles[i], glm::vec3(0.0f, 1.0f, 0.0f));
            glm::quat newRotation = deltaRotation * currentRotation;
            
            // Apply constraint
            newRotation = ApplyConstraint(newRotation, chain.GetConstraint(boneIndex));
            
            // Update transform
            glm::vec3 position = glm::vec3(bone.localTransform[3]);
            glm::vec3 scale = glm::vec3(
                glm::length(glm::vec3(bone.localTransform[0])),
                glm::length(glm::vec3(bone.localTransform[1])),
                glm::length(glm::vec3(bone.localTransform[2]))
            );
            
            bone.localTransform = glm::translate(glm::mat4(1.0f), position) *
                                 glm::mat4_cast(newRotation) *
                                 glm::scale(glm::mat4(1.0f), scale);
        }
    }
    
    skeleton.UpdateGlobalTransforms();
    glm::vec3 endEffectorPos = GetBoneWorldPosition(skeleton, endEffectorIndex);
    float finalDistance = glm::length(endEffectorPos - targetPosition);
    
    return finalDistance < chain.GetTolerance() * 10.0f;
}

void JacobianSolver::ComputeJacobian(const Skeleton& skeleton, const IKChain& chain,
                                    const glm::vec3& endEffectorPos,
                                    std::vector<std::vector<float>>& jacobian) {
    const std::vector<int>& bones = chain.GetBones();
    
    // Jacobian is 3 x N matrix (3 for x,y,z; N for number of bones)
    jacobian.resize(3);
    for (auto& row : jacobian) {
        row.resize(bones.size(), 0.0f);
    }
    
    // Compute partial derivatives
    const float epsilon = 0.01f;
    
    for (size_t i = 0; i < bones.size(); ++i) {
        int boneIndex = bones[i];
        glm::vec3 bonePos = GetBoneWorldPosition(skeleton, boneIndex);
        
        // Approximate derivative: change in end effector position per unit rotation
        glm::vec3 axis = glm::vec3(0.0f, 1.0f, 0.0f);  // Rotation axis
        glm::vec3 r = endEffectorPos - bonePos;
        glm::vec3 derivative = glm::cross(axis, r);
        
        jacobian[0][i] = derivative.x;
        jacobian[1][i] = derivative.y;
        jacobian[2][i] = derivative.z;
    }
}

std::vector<float> JacobianSolver::SolveDampedLeastSquares(
    const std::vector<std::vector<float>>& jacobian,
    const std::vector<float>& error) {
    
    // Simplified damped least squares solution
    // In a full implementation, this would use proper matrix operations
    
    size_t numBones = jacobian[0].size();
    std::vector<float> deltaAngles(numBones, 0.0f);
    
    // Simple approximation: scale error by Jacobian transpose
    for (size_t i = 0; i < numBones; ++i) {
        float sum = 0.0f;
        for (size_t j = 0; j < 3; ++j) {
            sum += jacobian[j][i] * error[j];
        }
        
        // Apply damping
        float magnitude = 0.0f;
        for (size_t j = 0; j < 3; ++j) {
            magnitude += jacobian[j][i] * jacobian[j][i];
        }
        
        if (magnitude > 0.0f) {
            deltaAngles[i] = sum / (magnitude + dampingFactor * dampingFactor);
        }
    }
    
    return deltaAngles;
}

// ============================================================================
// IKSystem
// ============================================================================

IKSystem::IKSystem() : initialized(false) {
}

IKSystem::~IKSystem() {
    Shutdown();
}

bool IKSystem::Initialize() {
    if (initialized) {
        return true;
    }
    
    // Create default solvers
    solvers[IKAlgorithm::CCD] = std::make_shared<CCDSolver>();
    solvers[IKAlgorithm::FABRIK] = std::make_shared<FABRIKSolver>();
    solvers[IKAlgorithm::Jacobian] = std::make_shared<JacobianSolver>();
    
    initialized = true;
    return true;
}

void IKSystem::Shutdown() {
    if (!initialized) {
        return;
    }
    
    solvers.clear();
    initialized = false;
}

std::shared_ptr<IKChain> IKSystem::CreateChain() {
    return std::make_shared<IKChain>();
}

std::shared_ptr<IKSolver> IKSystem::CreateSolver(IKAlgorithm algorithm) {
    auto it = solvers.find(algorithm);
    if (it != solvers.end()) {
        return it->second;
    }
    return nullptr;
}

bool IKSystem::SolveIK(Skeleton& skeleton, const IKChain& chain,
                      const glm::vec3& targetPosition,
                      IKAlgorithm algorithm) {
    auto solver = CreateSolver(algorithm);
    if (!solver) {
        return false;
    }
    
    return solver->Solve(skeleton, chain, targetPosition);
}

bool IKSystem::SolveIKWithOrientation(Skeleton& skeleton, const IKChain& chain,
                                     const glm::vec3& targetPosition,
                                     const glm::quat& targetOrientation,
                                     IKAlgorithm algorithm) {
    auto solver = CreateSolver(algorithm);
    if (!solver) {
        return false;
    }
    
    return solver->SolveWithOrientation(skeleton, chain, targetPosition, targetOrientation);
}

} // namespace pywrkgame
