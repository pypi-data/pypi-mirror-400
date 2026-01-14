#pragma once

#include <vector>
#include <memory>
#include <unordered_map>
#define GLM_ENABLE_EXPERIMENTAL
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

namespace pywrkgame {

// Forward declarations
class Skeleton;
struct Bone;

// IK constraint types
enum class IKConstraintType {
    None,
    HingeJoint,      // Rotation around single axis
    BallJoint,       // Free rotation with limits
    FixedJoint       // No rotation allowed
};

// IK constraint for a joint
struct IKConstraint {
    IKConstraintType type;
    glm::vec3 axis;           // For hinge joints
    float minAngle;           // Minimum rotation angle (radians)
    float maxAngle;           // Maximum rotation angle (radians)
    
    IKConstraint()
        : type(IKConstraintType::None)
        , axis(0.0f, 1.0f, 0.0f)
        , minAngle(-glm::pi<float>())
        , maxAngle(glm::pi<float>())
    {}
};

// IK chain representing a series of bones
class IKChain {
public:
    IKChain();
    
    // Add bone to chain
    void AddBone(int boneIndex);
    
    // Set end effector (last bone in chain)
    void SetEndEffector(int boneIndex);
    
    // Get bones in chain
    const std::vector<int>& GetBones() const { return boneIndices; }
    int GetEndEffector() const { return endEffectorIndex; }
    
    // Set constraint for a bone in the chain
    void SetConstraint(int boneIndex, const IKConstraint& constraint);
    const IKConstraint& GetConstraint(int boneIndex) const;
    
    // Chain properties
    void SetMaxIterations(int iterations) { maxIterations = iterations; }
    void SetTolerance(float tol) { tolerance = tol; }
    
    int GetMaxIterations() const { return maxIterations; }
    float GetTolerance() const { return tolerance; }
    
private:
    std::vector<int> boneIndices;
    int endEffectorIndex;
    std::unordered_map<int, IKConstraint> constraints;
    int maxIterations;
    float tolerance;
};

// IK solver algorithms
enum class IKAlgorithm {
    CCD,        // Cyclic Coordinate Descent
    FABRIK,     // Forward And Backward Reaching Inverse Kinematics
    Jacobian    // Jacobian-based solver
};

// IK solver base class
class IKSolver {
public:
    IKSolver();
    virtual ~IKSolver();
    
    // Solve IK for a chain to reach target position
    virtual bool Solve(Skeleton& skeleton, const IKChain& chain, const glm::vec3& targetPosition) = 0;
    
    // Solve IK with target position and orientation
    virtual bool SolveWithOrientation(Skeleton& skeleton, const IKChain& chain, 
                                     const glm::vec3& targetPosition, 
                                     const glm::quat& targetOrientation);
    
protected:
    // Helper: Get world position of bone
    glm::vec3 GetBoneWorldPosition(const Skeleton& skeleton, int boneIndex) const;
    
    // Helper: Apply constraint to rotation
    glm::quat ApplyConstraint(const glm::quat& rotation, const IKConstraint& constraint) const;
    
    // Helper: Calculate bone length
    float GetBoneLength(const Skeleton& skeleton, int boneIndex) const;
};

// CCD (Cyclic Coordinate Descent) IK Solver
class CCDSolver : public IKSolver {
public:
    CCDSolver();
    
    bool Solve(Skeleton& skeleton, const IKChain& chain, const glm::vec3& targetPosition) override;
    
private:
    // Rotate bone to point towards target
    void RotateBoneToTarget(Skeleton& skeleton, int boneIndex, 
                           const glm::vec3& endEffectorPos, 
                           const glm::vec3& targetPos);
};

// FABRIK (Forward And Backward Reaching Inverse Kinematics) Solver
class FABRIKSolver : public IKSolver {
public:
    FABRIKSolver();
    
    bool Solve(Skeleton& skeleton, const IKChain& chain, const glm::vec3& targetPosition) override;
    
private:
    // Forward reaching phase
    void ForwardReach(std::vector<glm::vec3>& positions, const glm::vec3& target, 
                     const std::vector<float>& boneLengths);
    
    // Backward reaching phase
    void BackwardReach(std::vector<glm::vec3>& positions, const glm::vec3& root, 
                      const std::vector<float>& boneLengths);
    
    // Apply positions back to skeleton
    void ApplyPositionsToSkeleton(Skeleton& skeleton, const IKChain& chain, 
                                 const std::vector<glm::vec3>& positions);
};

// Jacobian-based IK Solver (more advanced, handles multiple constraints)
class JacobianSolver : public IKSolver {
public:
    JacobianSolver();
    
    bool Solve(Skeleton& skeleton, const IKChain& chain, const glm::vec3& targetPosition) override;
    
    void SetDampingFactor(float damping) { dampingFactor = damping; }
    float GetDampingFactor() const { return dampingFactor; }
    
private:
    float dampingFactor;  // For damped least squares
    
    // Compute Jacobian matrix
    void ComputeJacobian(const Skeleton& skeleton, const IKChain& chain, 
                        const glm::vec3& endEffectorPos,
                        std::vector<std::vector<float>>& jacobian);
    
    // Solve using damped least squares
    std::vector<float> SolveDampedLeastSquares(const std::vector<std::vector<float>>& jacobian,
                                               const std::vector<float>& error);
};

// IK system manager
class IKSystem {
public:
    IKSystem();
    ~IKSystem();
    
    bool Initialize();
    void Shutdown();
    
    // Create IK chain
    std::shared_ptr<IKChain> CreateChain();
    
    // Create solver of specific type
    std::shared_ptr<IKSolver> CreateSolver(IKAlgorithm algorithm);
    
    // Solve IK for a chain
    bool SolveIK(Skeleton& skeleton, const IKChain& chain, 
                const glm::vec3& targetPosition, 
                IKAlgorithm algorithm = IKAlgorithm::FABRIK);
    
    // Solve IK with orientation
    bool SolveIKWithOrientation(Skeleton& skeleton, const IKChain& chain,
                               const glm::vec3& targetPosition,
                               const glm::quat& targetOrientation,
                               IKAlgorithm algorithm = IKAlgorithm::FABRIK);
    
private:
    bool initialized;
    std::unordered_map<IKAlgorithm, std::shared_ptr<IKSolver>> solvers;
};

} // namespace pywrkgame
