#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <unordered_map>
#include <unordered_set>

namespace pywrkgame {
namespace tools {

// Forward declarations
namespace physics { class PhysicsEngine; }

// Asset dependency information
struct AssetDependency {
    std::string assetPath;
    std::vector<std::string> dependencies;
    size_t totalSize = 0;
    bool isLoaded = false;
};

// Crash information
struct CrashInfo {
    std::string exceptionMessage;
    std::vector<std::string> stackTrace;
    std::string timestamp;
    std::unordered_map<std::string, std::string> systemInfo;
};

// Physics debug visualization data
struct PhysicsDebugData {
    struct CollisionShape {
        enum class Type { Box, Sphere, Capsule, Mesh };
        Type type;
        std::vector<float> vertices;
        std::vector<uint32_t> indices;
        bool isActive = true;
    };
    
    struct RigidBody {
        uint32_t id;
        std::vector<float> position;
        std::vector<float> rotation;
        std::vector<float> velocity;
        float mass;
        bool isKinematic;
        std::vector<CollisionShape> shapes;
    };
    
    std::vector<RigidBody> rigidBodies;
    std::vector<std::pair<uint32_t, uint32_t>> activeCollisions;
};

// Asset Dependency Tracker
class AssetDependencyTracker {
public:
    AssetDependencyTracker();
    ~AssetDependencyTracker();
    
    // Track asset loading
    void RegisterAsset(const std::string& assetPath, size_t size);
    void RegisterDependency(const std::string& assetPath, const std::string& dependencyPath);
    void UnregisterAsset(const std::string& assetPath);
    
    // Query dependencies
    std::vector<std::string> GetDependencies(const std::string& assetPath) const;
    std::vector<std::string> GetDependents(const std::string& assetPath) const;
    AssetDependency GetAssetInfo(const std::string& assetPath) const;
    
    // Get all tracked assets
    std::vector<AssetDependency> GetAllAssets() const;
    
    // Detect circular dependencies
    bool HasCircularDependencies(const std::string& assetPath) const;
    std::vector<std::string> GetCircularDependencyChain(const std::string& assetPath) const;
    
    // Calculate total size including dependencies
    size_t CalculateTotalSize(const std::string& assetPath) const;
    
    // Clear all tracking data
    void Clear();

private:
    struct Impl;
    std::unique_ptr<Impl> pImpl;
};

// Physics Visual Debugger
class PhysicsVisualDebugger {
public:
    PhysicsVisualDebugger();
    ~PhysicsVisualDebugger();
    
    // Enable/disable debugging
    void SetEnabled(bool enabled);
    bool IsEnabled() const;
    
    // Visualization options
    void SetDrawCollisionShapes(bool draw);
    void SetDrawVelocities(bool draw);
    void SetDrawContactPoints(bool draw);
    void SetDrawConstraints(bool draw);
    
    // Get debug visualization data
    PhysicsDebugData GetDebugData() const;
    
    // Update from physics engine
    void UpdateFromPhysicsEngine(const void* physicsEngine);
    
    // Clear debug data
    void Clear();

private:
    struct Impl;
    std::unique_ptr<Impl> pImpl;
};

// Crash Reporter
class CrashReporter {
public:
    CrashReporter();
    ~CrashReporter();
    
    // Initialize crash handling
    void Initialize();
    void Shutdown();
    
    // Set crash callback
    using CrashCallback = std::function<void(const CrashInfo&)>;
    void SetCrashCallback(CrashCallback callback);
    
    // Manual crash reporting
    void ReportCrash(const std::string& message);
    void ReportException(const std::exception& e);
    
    // Get crash history
    std::vector<CrashInfo> GetCrashHistory() const;
    CrashInfo GetLastCrash() const;
    
    // Save crash report to file
    bool SaveCrashReport(const CrashInfo& info, const std::string& filepath) const;
    
    // Generate stack trace
    static std::vector<std::string> CaptureStackTrace(int maxDepth = 64);
    
    // System information
    static std::unordered_map<std::string, std::string> GetSystemInfo();

private:
    struct Impl;
    std::unique_ptr<Impl> pImpl;
    
    static void SignalHandler(int signal);
};

} // namespace tools
} // namespace pywrkgame
