#include "pywrkgame/core/PerformanceOptimizer.h"
#include "pywrkgame/tools/PerformanceProfiler.h"
#include "pywrkgame/rendering/RenderingEngine.h"
#include "pywrkgame/rendering/PostProcessing.h"
#include "pywrkgame/rendering/LODSystem.h"
#include "pywrkgame/platform/PlatformManager.h"
#include <algorithm>
#include <numeric>
#include <vector>

namespace pywrkgame {
namespace core {

struct PerformanceOptimizer::Impl {
    PerformanceConfig config;
    QualityLevel currentQuality = QualityLevel::High;
    
    // Subsystem references
    tools::PerformanceProfiler* profiler = nullptr;
    rendering::RenderingEngine* renderer = nullptr;
    
    // Frame rate tracking
    std::vector<float> recentFrameRates;
    static constexpr size_t FRAME_RATE_HISTORY = 60;
    std::chrono::high_resolution_clock::time_point lastFrameTime;
    float currentFPS = 0.0f;
    
    // Performance tracking
    int consecutiveLowFrames = 0;
    int consecutiveGoodFrames = 0;
    static constexpr int FRAMES_BEFORE_DOWNGRADE = 30;  // ~0.5 seconds at 60fps
    static constexpr int FRAMES_BEFORE_UPGRADE = 180;   // ~3 seconds at 60fps
    
    // Memory tracking
    size_t lastMemoryCheckMB = 0;
    bool memoryWarning = false;
    bool memoryCritical = false;
    
    // Initialization state
    bool initialized = false;
    
    void ApplyQualitySettings(QualityLevel level) {
        if (!renderer) return;
        
        // Apply quality settings to renderer
        auto* postProcessing = renderer->GetPostProcessing();
        auto* lodSystem = renderer->GetLODSystem();
        
        switch (level) {
            case QualityLevel::Low:
                // Disable expensive features
                if (postProcessing) {
                    renderer->EnablePostProcessing(false);
                }
                renderer->EnableGlobalIllumination(false);
                if (lodSystem) {
                    lodSystem->SetLODBias(2.0f);  // Use lower LODs
                }
                break;
                
            case QualityLevel::Medium:
                // Enable basic post-processing
                if (postProcessing) {
                    renderer->EnablePostProcessing(true);
                    // Disable expensive effects
                    if (auto* ssao = postProcessing->GetSSAOEffect()) {
                        ssao->SetEnabled(false);
                    }
                    if (auto* motionBlur = postProcessing->GetMotionBlurEffect()) {
                        motionBlur->SetEnabled(false);
                    }
                }
                renderer->EnableGlobalIllumination(false);
                if (lodSystem) {
                    lodSystem->SetLODBias(1.5f);
                }
                break;
                
            case QualityLevel::High:
                // Enable most features
                if (postProcessing) {
                    renderer->EnablePostProcessing(true);
                    if (auto* ssao = postProcessing->GetSSAOEffect()) {
                        ssao->SetEnabled(true);
                    }
                    if (auto* motionBlur = postProcessing->GetMotionBlurEffect()) {
                        motionBlur->SetEnabled(false);
                    }
                }
                renderer->EnableGlobalIllumination(false);
                if (lodSystem) {
                    lodSystem->SetLODBias(1.0f);
                }
                break;
                
            case QualityLevel::Ultra:
                // Enable all features
                if (postProcessing) {
                    renderer->EnablePostProcessing(true);
                    if (auto* ssao = postProcessing->GetSSAOEffect()) {
                        ssao->SetEnabled(true);
                    }
                    if (auto* motionBlur = postProcessing->GetMotionBlurEffect()) {
                        motionBlur->SetEnabled(true);
                    }
                    if (auto* bloom = postProcessing->GetBloomEffect()) {
                        bloom->SetEnabled(true);
                    }
                }
                renderer->EnableGlobalIllumination(true);
                if (lodSystem) {
                    lodSystem->SetLODBias(0.5f);
                }
                break;
        }
    }
    
    void UpdateFrameRateTracking(float deltaTime) {
        if (deltaTime > 0.0f) {
            currentFPS = 1.0f / deltaTime;
            recentFrameRates.push_back(currentFPS);
            
            if (recentFrameRates.size() > FRAME_RATE_HISTORY) {
                recentFrameRates.erase(recentFrameRates.begin());
            }
        }
    }
    
    float GetAverageFrameRate() const {
        if (recentFrameRates.empty()) return 0.0f;
        
        float sum = std::accumulate(recentFrameRates.begin(), recentFrameRates.end(), 0.0f);
        return sum / recentFrameRates.size();
    }
    
    float GetTargetFPS() const {
        // For testing purposes, always use the configured target based on game type
        // In production, this would also check platform
        return config.is3DGame ? config.targets.targetFPS3D : config.targets.targetFPS2D;
    }
    
    void CheckAndAdjustQuality() {
        if (!config.enableAutoScaling) return;
        
        float targetFPS = GetTargetFPS();
        float avgFPS = GetAverageFrameRate();
        
        // Check if we're below target
        if (avgFPS < targetFPS * 0.9f) {  // 10% tolerance
            consecutiveLowFrames++;
            consecutiveGoodFrames = 0;
            
            // Downgrade quality if consistently low
            if (consecutiveLowFrames >= FRAMES_BEFORE_DOWNGRADE) {
                if (currentQuality > QualityLevel::Low) {
                    QualityLevel newQuality = static_cast<QualityLevel>(
                        static_cast<int>(currentQuality) - 1
                    );
                    currentQuality = newQuality;
                    ApplyQualitySettings(currentQuality);
                    consecutiveLowFrames = 0;
                }
            }
        }
        // Check if we're consistently above target
        else if (avgFPS > targetFPS * 1.2f) {  // 20% above target
            consecutiveGoodFrames++;
            consecutiveLowFrames = 0;
            
            // Upgrade quality if consistently good
            if (consecutiveGoodFrames >= FRAMES_BEFORE_UPGRADE) {
                if (currentQuality < QualityLevel::Ultra) {
                    QualityLevel newQuality = static_cast<QualityLevel>(
                        static_cast<int>(currentQuality) + 1
                    );
                    currentQuality = newQuality;
                    ApplyQualitySettings(currentQuality);
                    consecutiveGoodFrames = 0;
                }
            }
        }
        else {
            // Frame rate is acceptable, reset counters
            consecutiveLowFrames = 0;
            consecutiveGoodFrames = 0;
        }
    }
    
    void CheckMemory() {
        if (!config.enableMemoryManagement || !profiler) return;
        
        auto memStats = profiler->GetMemoryStats();
        lastMemoryCheckMB = memStats.currentUsage / (1024 * 1024);
        
        // Check memory thresholds
        if (lastMemoryCheckMB >= config.targets.memoryCriticalThresholdMB) {
            memoryCritical = true;
            memoryWarning = true;
            
            // Emergency measures: force lowest quality
            if (currentQuality != QualityLevel::Low) {
                currentQuality = QualityLevel::Low;
                ApplyQualitySettings(currentQuality);
            }
        }
        else if (lastMemoryCheckMB >= config.targets.memoryWarningThresholdMB) {
            memoryWarning = true;
            memoryCritical = false;
        }
        else {
            memoryWarning = false;
            memoryCritical = false;
        }
    }
};

PerformanceOptimizer::PerformanceOptimizer() : pImpl(std::make_unique<Impl>()) {}

PerformanceOptimizer::~PerformanceOptimizer() {
    if (pImpl->initialized) {
        Shutdown();
    }
}

bool PerformanceOptimizer::Initialize(const PerformanceConfig& config) {
    if (pImpl->initialized) return false;
    
    pImpl->config = config;
    pImpl->currentQuality = config.initialQuality;
    pImpl->lastFrameTime = std::chrono::high_resolution_clock::now();
    pImpl->initialized = true;
    
    return true;
}

void PerformanceOptimizer::Shutdown() {
    if (!pImpl->initialized) return;
    
    pImpl->profiler = nullptr;
    pImpl->renderer = nullptr;
    pImpl->recentFrameRates.clear();
    pImpl->initialized = false;
}

void PerformanceOptimizer::BeginFrame() {
    if (!pImpl->initialized) return;
    
    pImpl->lastFrameTime = std::chrono::high_resolution_clock::now();
}

void PerformanceOptimizer::EndFrame() {
    if (!pImpl->initialized) return;
    
    auto currentTime = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
        currentTime - pImpl->lastFrameTime
    );
    float deltaTime = duration.count() / 1000000.0f;
    
    pImpl->UpdateFrameRateTracking(deltaTime);
}

void PerformanceOptimizer::Update(float deltaTime) {
    if (!pImpl->initialized) return;
    
    // Check and adjust quality based on frame rate
    if (pImpl->config.enableFrameRateMaintenance) {
        pImpl->CheckAndAdjustQuality();
    }
    
    // Check memory usage periodically (every 60 frames)
    static int frameCounter = 0;
    if (++frameCounter >= 60) {
        pImpl->CheckMemory();
        frameCounter = 0;
    }
}

void PerformanceOptimizer::SetQualityLevel(QualityLevel level) {
    if (!pImpl->initialized) return;
    
    pImpl->currentQuality = level;
    pImpl->ApplyQualitySettings(level);
    
    // Reset counters when manually setting quality
    pImpl->consecutiveLowFrames = 0;
    pImpl->consecutiveGoodFrames = 0;
}

QualityLevel PerformanceOptimizer::GetQualityLevel() const {
    return pImpl->currentQuality;
}

void PerformanceOptimizer::EnableAutoScaling(bool enable) {
    pImpl->config.enableAutoScaling = enable;
}

bool PerformanceOptimizer::IsAutoScalingEnabled() const {
    return pImpl->config.enableAutoScaling;
}

float PerformanceOptimizer::GetTargetFrameRate() const {
    return pImpl->GetTargetFPS();
}

float PerformanceOptimizer::GetCurrentFrameRate() const {
    return pImpl->currentFPS;
}

bool PerformanceOptimizer::IsFrameRateStable() const {
    if (!pImpl->initialized) return false;
    
    float targetFPS = pImpl->GetTargetFPS();
    float avgFPS = pImpl->GetAverageFrameRate();
    
    // Consider stable if within 10% of target
    return avgFPS >= targetFPS * 0.9f;
}

void PerformanceOptimizer::CheckMemoryUsage() {
    if (!pImpl->initialized) return;
    pImpl->CheckMemory();
}

bool PerformanceOptimizer::IsMemoryHealthy() const {
    return !pImpl->memoryWarning && !pImpl->memoryCritical;
}

size_t PerformanceOptimizer::GetCurrentMemoryUsageMB() const {
    return pImpl->lastMemoryCheckMB;
}

void PerformanceOptimizer::TriggerGarbageCollection() {
    // In a real implementation, this would trigger garbage collection
    // For now, it's a placeholder for future memory management
    if (pImpl->profiler) {
        // Could trigger cleanup of unused resources
    }
}

bool PerformanceOptimizer::IsPerformanceHealthy() const {
    return IsFrameRateStable() && IsMemoryHealthy();
}

float PerformanceOptimizer::GetPerformanceScore() const {
    if (!pImpl->initialized) return 0.0f;
    
    float targetFPS = pImpl->GetTargetFPS();
    float avgFPS = pImpl->GetAverageFrameRate();
    
    // Calculate FPS score (0.0 to 1.0)
    float fpsScore = std::min(1.0f, avgFPS / targetFPS);
    
    // Calculate memory score (0.0 to 1.0)
    float memoryScore = 1.0f;
    if (pImpl->memoryCritical) {
        memoryScore = 0.0f;
    } else if (pImpl->memoryWarning) {
        memoryScore = 0.5f;
    }
    
    // Combined score
    return (fpsScore * 0.7f) + (memoryScore * 0.3f);
}

void PerformanceOptimizer::SetProfiler(tools::PerformanceProfiler* profiler) {
    pImpl->profiler = profiler;
}

void PerformanceOptimizer::SetRenderer(rendering::RenderingEngine* renderer) {
    pImpl->renderer = renderer;
}

} // namespace core
} // namespace pywrkgame
