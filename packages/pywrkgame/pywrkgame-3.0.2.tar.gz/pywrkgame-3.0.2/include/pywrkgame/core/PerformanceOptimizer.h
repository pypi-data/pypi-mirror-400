#pragma once

#include <memory>
#include <chrono>

namespace pywrkgame {

// Forward declarations
namespace tools { class PerformanceProfiler; }
namespace rendering { class RenderingEngine; }

namespace core {

// Quality levels for adaptive scaling
enum class QualityLevel {
    Low = 0,
    Medium = 1,
    High = 2,
    Ultra = 3
};

// Performance targets
struct PerformanceTargets {
    float targetFPS2D = 30.0f;  // Minimum FPS for 2D games on low-end devices
    float targetFPS3D = 20.0f;  // Minimum FPS for 3D games on low-end devices
    float targetFPSDesktop = 60.0f;  // Target FPS for desktop
    float memoryWarningThresholdMB = 512.0f;  // Memory warning threshold
    float memoryCriticalThresholdMB = 768.0f;  // Memory critical threshold
};

// Performance optimization configuration
struct PerformanceConfig {
    bool enableAutoScaling = true;
    bool enableMemoryManagement = true;
    bool enableFrameRateMaintenance = true;
    PerformanceTargets targets;
    QualityLevel initialQuality = QualityLevel::High;
    bool is3DGame = true;  // false for 2D games
};

class PerformanceOptimizer {
public:
    PerformanceOptimizer();
    ~PerformanceOptimizer();

    // Initialization
    bool Initialize(const PerformanceConfig& config);
    void Shutdown();

    // Frame management
    void BeginFrame();
    void EndFrame();
    void Update(float deltaTime);

    // Quality management
    void SetQualityLevel(QualityLevel level);
    QualityLevel GetQualityLevel() const;
    void EnableAutoScaling(bool enable);
    bool IsAutoScalingEnabled() const;

    // Frame rate maintenance
    float GetTargetFrameRate() const;
    float GetCurrentFrameRate() const;
    bool IsFrameRateStable() const;

    // Memory management
    void CheckMemoryUsage();
    bool IsMemoryHealthy() const;
    size_t GetCurrentMemoryUsageMB() const;
    void TriggerGarbageCollection();

    // Performance metrics
    bool IsPerformanceHealthy() const;
    float GetPerformanceScore() const;  // 0.0 to 1.0

    // Integration with subsystems
    void SetProfiler(tools::PerformanceProfiler* profiler);
    void SetRenderer(rendering::RenderingEngine* renderer);

private:
    struct Impl;
    std::unique_ptr<Impl> pImpl;
};

} // namespace core
} // namespace pywrkgame
