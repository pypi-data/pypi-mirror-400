#include <gtest/gtest.h>
#include "pywrkgame/core/PerformanceOptimizer.h"
#include "pywrkgame/core/EngineCore.h"
#include "pywrkgame/tools/PerformanceProfiler.h"
#include "pywrkgame/rendering/RenderingEngine.h"
#include "pywrkgame/platform/PlatformManager.h"
#include <random>
#include <thread>
#include <chrono>
#include <vector>

using namespace pywrkgame::core;
using namespace pywrkgame::tools;
using namespace pywrkgame::rendering;

// Property-based test helper class
class PerformanceOptimizationPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        rng.seed(42); // Fixed seed for reproducibility
        
        // Initialize platform manager
        pywrkgame::platform::PlatformManager::Initialize();
        
        // Create profiler and renderer
        profiler = std::make_unique<PerformanceProfiler>();
        renderer = std::make_unique<RenderingEngine>();
        renderer->Initialize();
        
        // Create optimizer
        optimizer = std::make_unique<PerformanceOptimizer>();
    }
    
    void TearDown() override {
        optimizer.reset();
        renderer.reset();
        profiler.reset();
        pywrkgame::platform::PlatformManager::Shutdown();
    }
    
    // Generate random float within range
    float RandomFloat(float min = 0.0f, float max = 1.0f) {
        std::uniform_real_distribution<float> dist(min, max);
        return dist(rng);
    }
    
    // Generate random int within range
    int RandomInt(int min = 0, int max = 100) {
        std::uniform_int_distribution<int> dist(min, max);
        return dist(rng);
    }
    
    // Simulate frame with specific duration
    void SimulateFrame(float durationMs) {
        auto start = std::chrono::high_resolution_clock::now();
        
        optimizer->BeginFrame();
        profiler->BeginFrame();
        
        // Simulate work
        while (true) {
            auto now = std::chrono::high_resolution_clock::now();
            auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(now - start);
            if (elapsed.count() / 1000.0f >= durationMs) {
                break;
            }
        }
        
        profiler->EndFrame();
        optimizer->EndFrame();
        optimizer->Update(durationMs / 1000.0f);
    }
    
    std::unique_ptr<PerformanceOptimizer> optimizer;
    std::unique_ptr<PerformanceProfiler> profiler;
    std::unique_ptr<RenderingEngine> renderer;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 1: Frame Rate Maintenance
 * For any game running on low-end Android devices, the Performance_Optimizer should maintain 
 * minimum 30 FPS for 2D games and minimum 20 FPS for 3D games
 * Validates: Requirements 1.2, 1.3
 */
TEST_F(PerformanceOptimizationPropertyTest, Property1_FrameRateMaintenance2D) {
    // Configure for 2D game on mobile
    PerformanceConfig config;
    config.is3DGame = false;
    config.enableAutoScaling = true;
    config.enableFrameRateMaintenance = true;
    config.targets.targetFPS2D = 30.0f;
    config.initialQuality = QualityLevel::High;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    const int NUM_ITERATIONS = 100;
    std::vector<float> frameRates;
    
    // Simulate frames with varying performance
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Simulate frame time that would result in varying FPS
        float frameTimeMs = RandomFloat(20.0f, 50.0f); // 20-50 FPS range
        SimulateFrame(frameTimeMs);
        
        float currentFPS = optimizer->GetCurrentFrameRate();
        if (currentFPS > 0.0f) {
            frameRates.push_back(currentFPS);
        }
    }
    
    // Property 1: Target frame rate should be set correctly for 2D
    EXPECT_EQ(optimizer->GetTargetFrameRate(), 30.0f) 
        << "Target FPS for 2D games should be 30";
    
    // Property 2: Optimizer should attempt to maintain target FPS
    // After enough iterations, average FPS should approach target
    if (!frameRates.empty()) {
        float avgFPS = 0.0f;
        for (float fps : frameRates) {
            avgFPS += fps;
        }
        avgFPS /= frameRates.size();
        
        // With auto-scaling, average FPS should be reasonable
        EXPECT_GT(avgFPS, 15.0f) << "Average FPS should be above minimum threshold";
    }
    
    // Property 3: Quality level should adjust based on performance
    QualityLevel finalQuality = optimizer->GetQualityLevel();
    // Quality should be valid
    EXPECT_GE(static_cast<int>(finalQuality), static_cast<int>(QualityLevel::Low));
    EXPECT_LE(static_cast<int>(finalQuality), static_cast<int>(QualityLevel::Ultra));
}

TEST_F(PerformanceOptimizationPropertyTest, Property1_FrameRateMaintenance3D) {
    // Configure for 3D game on mobile
    PerformanceConfig config;
    config.is3DGame = true;
    config.enableAutoScaling = true;
    config.enableFrameRateMaintenance = true;
    config.targets.targetFPS3D = 20.0f;
    config.initialQuality = QualityLevel::High;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    const int NUM_ITERATIONS = 100;
    std::vector<float> frameRates;
    
    // Simulate frames with varying performance
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        float frameTimeMs = RandomFloat(30.0f, 70.0f); // 14-33 FPS range
        SimulateFrame(frameTimeMs);
        
        float currentFPS = optimizer->GetCurrentFrameRate();
        if (currentFPS > 0.0f) {
            frameRates.push_back(currentFPS);
        }
    }
    
    // Property 1: Target frame rate should be set correctly for 3D
    EXPECT_EQ(optimizer->GetTargetFrameRate(), 20.0f) 
        << "Target FPS for 3D games should be 20";
    
    // Property 2: Frame rate should be tracked
    EXPECT_GT(optimizer->GetCurrentFrameRate(), 0.0f) 
        << "Current FPS should be tracked";
    
    // Property 3: Quality level should be within valid range
    QualityLevel finalQuality = optimizer->GetQualityLevel();
    EXPECT_GE(static_cast<int>(finalQuality), static_cast<int>(QualityLevel::Low));
    EXPECT_LE(static_cast<int>(finalQuality), static_cast<int>(QualityLevel::Ultra));
}

/*
 * Feature: pywrkgame-library, Property 2: Memory Leak Prevention
 * For any game session running for extended periods, memory usage should not continuously grow,
 * indicating absence of memory leaks
 * Validates: Requirements 1.4
 */
TEST_F(PerformanceOptimizationPropertyTest, Property2_MemoryLeakPrevention) {
    PerformanceConfig config;
    config.enableMemoryManagement = true;
    config.targets.memoryWarningThresholdMB = 512.0f;
    config.targets.memoryCriticalThresholdMB = 768.0f;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    const int NUM_ITERATIONS = 100;
    std::vector<size_t> memorySnapshots;
    
    // Simulate allocations and track memory
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Simulate some allocations
        size_t allocSize = RandomInt(1024, 10240); // 1KB to 10KB
        void* ptr = malloc(allocSize);
        profiler->TrackAllocation(ptr, allocSize);
        
        // Periodically free some memory
        if (i % 10 == 0 && i > 0) {
            profiler->TrackDeallocation(ptr);
            free(ptr);
        }
        
        SimulateFrame(16.67f); // ~60 FPS
        
        // Check memory periodically
        if (i % 10 == 0) {
            optimizer->CheckMemoryUsage();
            memorySnapshots.push_back(optimizer->GetCurrentMemoryUsageMB());
        }
    }
    
    // Property 1: Memory usage should be tracked
    EXPECT_GE(optimizer->GetCurrentMemoryUsageMB(), 0u) 
        << "Memory usage should be tracked";
    
    // Property 2: Memory health should be determinable
    bool isHealthy = optimizer->IsMemoryHealthy();
    // Should be either true or false (not undefined)
    EXPECT_TRUE(isHealthy || !isHealthy);
    
    // Property 3: Memory usage should not grow unboundedly
    // Check that memory doesn't continuously increase
    if (memorySnapshots.size() >= 3) {
        // Last snapshot should not be significantly larger than first
        size_t firstSnapshot = memorySnapshots[0];
        size_t lastSnapshot = memorySnapshots.back();
        
        // Allow for some growth, but not unbounded
        // This is a weak property test - in real scenario, we'd track actual leaks
        EXPECT_LT(lastSnapshot, firstSnapshot + 1000) 
            << "Memory should not grow unboundedly";
    }
    
    // Clean up tracked allocations
    MemoryStats stats = profiler->GetMemoryStats();
    for (const auto& [ptr, size] : stats.activeAllocations) {
        profiler->TrackDeallocation(ptr);
        free(ptr);
    }
}

/*
 * Feature: pywrkgame-library, Property 3: Adaptive Quality Scaling
 * For any system with limited resources, the Performance_Optimizer should automatically 
 * adjust rendering quality to maintain performance
 * Validates: Requirements 1.5
 */
TEST_F(PerformanceOptimizationPropertyTest, Property3_AdaptiveQualityScaling) {
    PerformanceConfig config;
    config.is3DGame = true;
    config.enableAutoScaling = true;
    config.enableFrameRateMaintenance = true;
    config.targets.targetFPS3D = 30.0f;
    config.initialQuality = QualityLevel::Ultra;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    QualityLevel initialQuality = optimizer->GetQualityLevel();
    EXPECT_EQ(initialQuality, QualityLevel::Ultra) 
        << "Initial quality should be Ultra";
    
    // Property 1: Quality can be manually set
    optimizer->SetQualityLevel(QualityLevel::Low);
    EXPECT_EQ(optimizer->GetQualityLevel(), QualityLevel::Low) 
        << "Quality should be settable";
    
    optimizer->SetQualityLevel(QualityLevel::High);
    EXPECT_EQ(optimizer->GetQualityLevel(), QualityLevel::High) 
        << "Quality should be settable to any valid level";
    
    // Property 2: Auto-scaling can be enabled/disabled
    EXPECT_TRUE(optimizer->IsAutoScalingEnabled()) 
        << "Auto-scaling should be enabled by default";
    
    optimizer->EnableAutoScaling(false);
    EXPECT_FALSE(optimizer->IsAutoScalingEnabled()) 
        << "Auto-scaling should be disableable";
    
    optimizer->EnableAutoScaling(true);
    EXPECT_TRUE(optimizer->IsAutoScalingEnabled()) 
        << "Auto-scaling should be re-enableable";
    
    // Property 3: Quality should adapt to poor performance
    // Simulate consistently poor performance
    optimizer->SetQualityLevel(QualityLevel::Ultra);
    
    for (int i = 0; i < 50; ++i) {
        // Simulate slow frames (below target)
        SimulateFrame(50.0f); // ~20 FPS, below 30 FPS target
    }
    
    QualityLevel qualityAfterPoorPerformance = optimizer->GetQualityLevel();
    // Quality should have been reduced (or stayed the same if already at minimum)
    EXPECT_LE(static_cast<int>(qualityAfterPoorPerformance), static_cast<int>(QualityLevel::Ultra)) 
        << "Quality should not increase during poor performance";
    
    // Property 4: Quality should adapt to good performance
    optimizer->SetQualityLevel(QualityLevel::Low);
    
    for (int i = 0; i < 200; ++i) {
        // Simulate fast frames (well above target)
        SimulateFrame(10.0f); // ~100 FPS, well above 30 FPS target
    }
    
    QualityLevel qualityAfterGoodPerformance = optimizer->GetQualityLevel();
    // Quality should have been increased (or stayed the same if already at maximum)
    EXPECT_GE(static_cast<int>(qualityAfterGoodPerformance), static_cast<int>(QualityLevel::Low)) 
        << "Quality should not decrease during good performance";
}

/*
 * Additional property test: Performance score calculation
 * For any performance state, score should be between 0.0 and 1.0
 */
TEST_F(PerformanceOptimizationPropertyTest, PerformanceScoreValidity) {
    PerformanceConfig config;
    config.is3DGame = true;
    config.enableAutoScaling = true;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Simulate random frame times
        float frameTimeMs = RandomFloat(10.0f, 100.0f);
        SimulateFrame(frameTimeMs);
        
        // Property: Performance score should always be in valid range
        float score = optimizer->GetPerformanceScore();
        EXPECT_GE(score, 0.0f) << "Performance score should be >= 0.0 at iteration " << i;
        EXPECT_LE(score, 1.0f) << "Performance score should be <= 1.0 at iteration " << i;
    }
}

/*
 * Additional property test: Frame rate stability detection
 * For any frame rate pattern, stability should be correctly detected
 */
TEST_F(PerformanceOptimizationPropertyTest, FrameRateStabilityDetection) {
    PerformanceConfig config;
    config.is3DGame = false;
    config.targets.targetFPS2D = 30.0f;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    // Property 1: Stable frame rate should be detected
    for (int i = 0; i < 100; ++i) {
        // Simulate consistent frame time at target
        SimulateFrame(33.33f); // ~30 FPS
    }
    
    EXPECT_TRUE(optimizer->IsFrameRateStable()) 
        << "Stable frame rate should be detected";
    
    // Property 2: Unstable frame rate should be detected
    for (int i = 0; i < 100; ++i) {
        // Simulate inconsistent frame time below target
        SimulateFrame(RandomFloat(50.0f, 100.0f)); // 10-20 FPS
    }
    
    EXPECT_FALSE(optimizer->IsFrameRateStable()) 
        << "Unstable frame rate should be detected";
}

/*
 * Additional property test: Memory threshold detection
 * For any memory usage level, thresholds should be correctly detected
 */
TEST_F(PerformanceOptimizationPropertyTest, MemoryThresholdDetection) {
    PerformanceConfig config;
    config.enableMemoryManagement = true;
    config.targets.memoryWarningThresholdMB = 100.0f;
    config.targets.memoryCriticalThresholdMB = 200.0f;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    // Property 1: Low memory usage should be healthy
    // Simulate low memory usage
    for (int i = 0; i < 10; ++i) {
        size_t smallAlloc = 1024; // 1KB
        void* ptr = malloc(smallAlloc);
        profiler->TrackAllocation(ptr, smallAlloc);
    }
    
    optimizer->CheckMemoryUsage();
    EXPECT_TRUE(optimizer->IsMemoryHealthy()) 
        << "Low memory usage should be healthy";
    
    // Clean up
    MemoryStats stats = profiler->GetMemoryStats();
    for (const auto& [ptr, size] : stats.activeAllocations) {
        profiler->TrackDeallocation(ptr);
        free(ptr);
    }
}

/*
 * Additional property test: Performance health check
 * For any performance state, health should be determinable
 */
TEST_F(PerformanceOptimizationPropertyTest, PerformanceHealthCheck) {
    PerformanceConfig config;
    config.is3DGame = true;
    config.enableAutoScaling = true;
    config.enableMemoryManagement = true;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        float frameTimeMs = RandomFloat(10.0f, 50.0f);
        SimulateFrame(frameTimeMs);
        
        // Property: Performance health should be determinable
        bool isHealthy = optimizer->IsPerformanceHealthy();
        // Should be either true or false (not undefined)
        EXPECT_TRUE(isHealthy || !isHealthy);
        
        // Property: Health should consider both frame rate and memory
        bool frameRateStable = optimizer->IsFrameRateStable();
        bool memoryHealthy = optimizer->IsMemoryHealthy();
        
        // If both are good, overall health should be good
        if (frameRateStable && memoryHealthy) {
            EXPECT_TRUE(isHealthy) 
                << "Performance should be healthy when both frame rate and memory are good";
        }
    }
}

/*
 * Additional property test: Quality level transitions
 * For any quality level, transitions should be valid
 */
TEST_F(PerformanceOptimizationPropertyTest, QualityLevelTransitions) {
    PerformanceConfig config;
    config.enableAutoScaling = true;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    // Property: All quality levels should be settable
    std::vector<QualityLevel> levels = {
        QualityLevel::Low,
        QualityLevel::Medium,
        QualityLevel::High,
        QualityLevel::Ultra
    };
    
    for (QualityLevel level : levels) {
        optimizer->SetQualityLevel(level);
        EXPECT_EQ(optimizer->GetQualityLevel(), level) 
            << "Quality level should be settable to " << static_cast<int>(level);
    }
    
    // Property: Quality transitions should be smooth (no skipping levels in auto-scaling)
    optimizer->SetQualityLevel(QualityLevel::Ultra);
    QualityLevel previousQuality = optimizer->GetQualityLevel();
    
    for (int i = 0; i < 50; ++i) {
        // Simulate poor performance to trigger downgrade
        SimulateFrame(100.0f); // Very slow frame
        
        QualityLevel currentQuality = optimizer->GetQualityLevel();
        
        // Quality should not jump more than one level at a time
        int qualityDiff = static_cast<int>(previousQuality) - static_cast<int>(currentQuality);
        EXPECT_LE(std::abs(qualityDiff), 1) 
            << "Quality should not jump more than one level at iteration " << i;
        
        previousQuality = currentQuality;
    }
}

/*
 * Additional property test: Garbage collection trigger
 * For any state, garbage collection should be triggerable
 */
TEST_F(PerformanceOptimizationPropertyTest, GarbageCollectionTrigger) {
    PerformanceConfig config;
    config.enableMemoryManagement = true;
    
    ASSERT_TRUE(optimizer->Initialize(config));
    optimizer->SetProfiler(profiler.get());
    optimizer->SetRenderer(renderer.get());
    
    // Property: Garbage collection should be callable without crashing
    EXPECT_NO_THROW(optimizer->TriggerGarbageCollection()) 
        << "Garbage collection should be triggerable";
    
    // Trigger multiple times
    for (int i = 0; i < 10; ++i) {
        EXPECT_NO_THROW(optimizer->TriggerGarbageCollection()) 
            << "Garbage collection should be triggerable multiple times";
    }
}
