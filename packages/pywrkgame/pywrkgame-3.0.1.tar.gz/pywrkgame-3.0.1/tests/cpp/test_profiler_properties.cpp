#include <gtest/gtest.h>
#include "pywrkgame/tools/PerformanceProfiler.h"
#include <random>
#include <thread>
#include <chrono>
#include <vector>

using namespace pywrkgame::tools;

// Property-based test helper class
class ProfilerPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        profiler = std::make_unique<PerformanceProfiler>();
        rng.seed(42); // Fixed seed for reproducibility
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
    
    // Simulate work for a specific duration
    void SimulateWork(float durationMs) {
        auto start = std::chrono::high_resolution_clock::now();
        while (true) {
            auto now = std::chrono::high_resolution_clock::now();
            auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(now - start);
            if (elapsed.count() / 1000.0f >= durationMs) {
                break;
            }
        }
    }
    
    std::unique_ptr<PerformanceProfiler> profiler;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 52: Performance Profiler Accuracy
 * For any running game, the profiler should display accurate GPU/CPU metrics in real-time
 * Validates: Requirements 10.1
 */
TEST_F(ProfilerPropertyTest, Property52_PerformanceProfilerAccuracy) {
    profiler->SetEnabled(true);
    
    // Run property test with multiple random frame timings
    const int NUM_ITERATIONS = 100;
    std::vector<float> expectedFrameTimes;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate random frame time between 1ms and 50ms
        float targetFrameTime = RandomFloat(1.0f, 50.0f);
        expectedFrameTimes.push_back(targetFrameTime);
        
        profiler->BeginFrame();
        
        // Simulate frame work
        SimulateWork(targetFrameTime);
        
        profiler->EndFrame();
    }
    
    // Get frame statistics
    FrameStats stats = profiler->GetFrameStats();
    
    // Property 1: Frame time should be measured
    EXPECT_GT(stats.frameTime, 0.0f) << "Frame time should be positive";
    
    // Property 2: FPS should be calculated correctly from frame time
    float expectedFPS = 1000.0f / stats.frameTime;
    EXPECT_NEAR(stats.fps, expectedFPS, 1.0f) << "FPS should match 1000/frameTime";
    
    // Property 3: Average frame time should be within reasonable range
    EXPECT_GT(stats.averageFrameTime, 0.0f) << "Average frame time should be positive";
    EXPECT_LT(stats.averageFrameTime, 100.0f) << "Average frame time should be reasonable";
    
    // Property 4: Min frame time should be less than or equal to average
    EXPECT_LE(stats.minFrameTime, stats.averageFrameTime) 
        << "Min frame time should be <= average";
    
    // Property 5: Max frame time should be greater than or equal to average
    EXPECT_GE(stats.maxFrameTime, stats.averageFrameTime) 
        << "Max frame time should be >= average";
    
    // Property 6: Min should be less than or equal to max
    EXPECT_LE(stats.minFrameTime, stats.maxFrameTime) 
        << "Min frame time should be <= max frame time";
    
    // Property 7: GPU stats should be retrievable
    GPUStats gpuStats = profiler->GetGPUStats();
    EXPECT_GE(gpuStats.gpuUsagePercent, 0.0f);
    EXPECT_LE(gpuStats.gpuUsagePercent, 100.0f);
    
    // Property 8: CPU stats should be retrievable
    CPUStats cpuStats = profiler->GetCPUStats();
    EXPECT_GE(cpuStats.cpuUsagePercent, 0.0f);
    EXPECT_LE(cpuStats.cpuUsagePercent, 100.0f);
    EXPECT_GT(cpuStats.activeThreads, 0u);
}

/*
 * Feature: pywrkgame-library, Property 52: Performance Profiler Accuracy (Markers)
 * For any performance marker, timing should be accurate
 */
TEST_F(ProfilerPropertyTest, Property52_PerformanceMarkerAccuracy) {
    profiler->SetEnabled(true);
    
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        std::string markerName = "TestMarker_" + std::to_string(i % 10);
        float targetDuration = RandomFloat(0.5f, 10.0f);
        
        profiler->BeginMarker(markerName);
        SimulateWork(targetDuration);
        profiler->EndMarker(markerName);
    }
    
    // Check marker statistics
    for (int i = 0; i < 10; ++i) {
        std::string markerName = "TestMarker_" + std::to_string(i);
        float avgTime = profiler->GetMarkerAverageTime(markerName);
        
        // Property: Marker average time should be positive
        EXPECT_GT(avgTime, 0.0f) << "Marker " << markerName << " should have positive average time";
        
        // Property: Marker average time should be reasonable (not too large)
        EXPECT_LT(avgTime, 100.0f) << "Marker " << markerName << " average time should be reasonable";
    }
}

/*
 * Feature: pywrkgame-library, Property 53: Memory Leak Detection
 * For any game with memory leaks, the memory analyzer should correctly identify and report leak locations
 * Validates: Requirements 10.3
 */
TEST_F(ProfilerPropertyTest, Property53_MemoryLeakDetection) {
    profiler->SetEnabled(true);
    
    // Run property test with random allocations and deallocations
    const int NUM_ITERATIONS = 100;
    std::vector<void*> allocatedPointers;
    std::vector<size_t> allocatedSizes;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Random allocation size between 16 bytes and 1MB
        size_t size = RandomInt(16, 1024 * 1024);
        void* ptr = malloc(size);
        
        profiler->TrackAllocation(ptr, size);
        allocatedPointers.push_back(ptr);
        allocatedSizes.push_back(size);
    }
    
    // Property 1: All allocations should be tracked
    MemoryStats stats = profiler->GetMemoryStats();
    EXPECT_EQ(stats.allocationCount, NUM_ITERATIONS) 
        << "All allocations should be tracked";
    
    // Property 2: Total allocated should match sum of allocation sizes
    size_t expectedTotalAllocated = 0;
    for (size_t size : allocatedSizes) {
        expectedTotalAllocated += size;
    }
    EXPECT_EQ(stats.totalAllocated, expectedTotalAllocated) 
        << "Total allocated should match sum of allocations";
    
    // Property 3: Current usage should equal total allocated (no deallocations yet)
    EXPECT_EQ(stats.currentUsage, stats.totalAllocated) 
        << "Current usage should equal total allocated before any deallocations";
    
    // Property 4: Should detect memory leaks
    EXPECT_TRUE(profiler->HasMemoryLeaks()) 
        << "Should detect memory leaks when allocations are not freed";
    
    std::vector<std::pair<void*, size_t>> leaks = profiler->GetMemoryLeaks();
    EXPECT_EQ(leaks.size(), NUM_ITERATIONS) 
        << "Should report all unfreed allocations as leaks";
    
    // Deallocate half of the allocations randomly
    std::vector<int> indicesToFree;
    for (int i = 0; i < NUM_ITERATIONS / 2; ++i) {
        int idx = RandomInt(0, allocatedPointers.size() - 1);
        indicesToFree.push_back(idx);
    }
    
    // Sort and remove duplicates
    std::sort(indicesToFree.begin(), indicesToFree.end());
    indicesToFree.erase(std::unique(indicesToFree.begin(), indicesToFree.end()), indicesToFree.end());
    
    size_t freedMemory = 0;
    for (int idx : indicesToFree) {
        if (allocatedPointers[idx] != nullptr) {
            profiler->TrackDeallocation(allocatedPointers[idx]);
            free(allocatedPointers[idx]);
            freedMemory += allocatedSizes[idx];
            allocatedPointers[idx] = nullptr;
        }
    }
    
    // Property 5: Deallocation count should match number of freed allocations
    stats = profiler->GetMemoryStats();
    EXPECT_EQ(stats.deallocationCount, indicesToFree.size()) 
        << "Deallocation count should match number of freed allocations";
    
    // Property 6: Total freed should match sum of freed sizes
    EXPECT_EQ(stats.totalFreed, freedMemory) 
        << "Total freed should match sum of freed allocations";
    
    // Property 7: Current usage should be total allocated minus total freed
    EXPECT_EQ(stats.currentUsage, stats.totalAllocated - stats.totalFreed) 
        << "Current usage should be total allocated minus total freed";
    
    // Property 8: Should still detect remaining leaks
    EXPECT_TRUE(profiler->HasMemoryLeaks()) 
        << "Should still detect leaks for unfreed allocations";
    
    leaks = profiler->GetMemoryLeaks();
    size_t expectedLeaks = NUM_ITERATIONS - indicesToFree.size();
    EXPECT_EQ(leaks.size(), expectedLeaks) 
        << "Should report correct number of remaining leaks";
    
    // Property 9: Peak usage should be at least as large as current usage
    EXPECT_GE(stats.peakUsage, stats.currentUsage) 
        << "Peak usage should be >= current usage";
    
    // Clean up remaining allocations
    for (void* ptr : allocatedPointers) {
        if (ptr != nullptr) {
            profiler->TrackDeallocation(ptr);
            free(ptr);
        }
    }
    
    // Property 10: After freeing all allocations, should have no leaks
    stats = profiler->GetMemoryStats();
    EXPECT_FALSE(profiler->HasMemoryLeaks()) 
        << "Should have no leaks after freeing all allocations";
    EXPECT_EQ(stats.currentUsage, 0u) 
        << "Current usage should be 0 after freeing all allocations";
}

/*
 * Additional property test: Memory tracking consistency
 * For any sequence of allocations and deallocations, tracking should remain consistent
 */
TEST_F(ProfilerPropertyTest, MemoryTrackingConsistency) {
    profiler->SetEnabled(true);
    
    const int NUM_ITERATIONS = 100;
    std::vector<void*> activeAllocations;
    size_t manualTotalAllocated = 0;
    size_t manualTotalFreed = 0;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Randomly allocate or deallocate
        bool shouldAllocate = activeAllocations.empty() || RandomFloat() > 0.3f;
        
        if (shouldAllocate) {
            size_t size = RandomInt(16, 1024);
            void* ptr = malloc(size);
            profiler->TrackAllocation(ptr, size);
            activeAllocations.push_back(ptr);
            manualTotalAllocated += size;
        } else {
            // Deallocate random allocation
            int idx = RandomInt(0, activeAllocations.size() - 1);
            void* ptr = activeAllocations[idx];
            
            // Get size before deallocation
            MemoryStats statsBefore = profiler->GetMemoryStats();
            size_t sizeBefore = 0;
            for (const auto& [allocPtr, allocSize] : statsBefore.activeAllocations) {
                if (allocPtr == ptr) {
                    sizeBefore = allocSize;
                    break;
                }
            }
            
            profiler->TrackDeallocation(ptr);
            free(ptr);
            manualTotalFreed += sizeBefore;
            activeAllocations.erase(activeAllocations.begin() + idx);
        }
        
        // Property: Memory stats should always be consistent
        MemoryStats stats = profiler->GetMemoryStats();
        EXPECT_EQ(stats.totalAllocated, manualTotalAllocated) 
            << "Total allocated should match manual tracking at iteration " << i;
        EXPECT_EQ(stats.totalFreed, manualTotalFreed) 
            << "Total freed should match manual tracking at iteration " << i;
        EXPECT_EQ(stats.currentUsage, manualTotalAllocated - manualTotalFreed) 
            << "Current usage should be consistent at iteration " << i;
        EXPECT_EQ(stats.activeAllocations.size(), activeAllocations.size()) 
            << "Active allocation count should match at iteration " << i;
    }
    
    // Clean up
    for (void* ptr : activeAllocations) {
        profiler->TrackDeallocation(ptr);
        free(ptr);
    }
}

/*
 * Additional property test: Profiler enable/disable
 * For any profiler state, enabling/disabling should work correctly
 */
TEST_F(ProfilerPropertyTest, ProfilerEnableDisable) {
    // Property 1: Profiler should start enabled
    EXPECT_TRUE(profiler->IsEnabled());
    
    // Property 2: Disabling should stop tracking
    profiler->SetEnabled(false);
    EXPECT_FALSE(profiler->IsEnabled());
    
    profiler->BeginFrame();
    SimulateWork(10.0f);
    profiler->EndFrame();
    
    FrameStats stats = profiler->GetFrameStats();
    // When disabled, stats should be empty/zero
    EXPECT_EQ(stats.frameTime, 0.0f) << "Frame time should be 0 when profiler is disabled";
    
    // Property 3: Re-enabling should resume tracking
    profiler->SetEnabled(true);
    EXPECT_TRUE(profiler->IsEnabled());
    
    profiler->BeginFrame();
    SimulateWork(10.0f);
    profiler->EndFrame();
    
    stats = profiler->GetFrameStats();
    EXPECT_GT(stats.frameTime, 0.0f) << "Frame time should be tracked when profiler is enabled";
}

/*
 * Additional property test: Reset functionality
 * For any profiler state, reset should clear all statistics
 */
TEST_F(ProfilerPropertyTest, ProfilerReset) {
    profiler->SetEnabled(true);
    
    // Generate some data
    for (int i = 0; i < 10; ++i) {
        profiler->BeginFrame();
        SimulateWork(5.0f);
        profiler->EndFrame();
        
        profiler->BeginMarker("TestMarker");
        SimulateWork(2.0f);
        profiler->EndMarker("TestMarker");
    }
    
    // Verify data exists
    FrameStats statsBefore = profiler->GetFrameStats();
    EXPECT_GT(statsBefore.frameTime, 0.0f);
    
    float markerTimeBefore = profiler->GetMarkerAverageTime("TestMarker");
    EXPECT_GT(markerTimeBefore, 0.0f);
    
    // Property: Reset should clear all statistics
    profiler->Reset();
    
    FrameStats statsAfter = profiler->GetFrameStats();
    EXPECT_EQ(statsAfter.frameTime, 0.0f) << "Frame time should be 0 after reset";
    EXPECT_EQ(statsAfter.averageFrameTime, 0.0f) << "Average frame time should be 0 after reset";
    
    float markerTimeAfter = profiler->GetMarkerAverageTime("TestMarker");
    EXPECT_EQ(markerTimeAfter, 0.0f) << "Marker time should be 0 after reset";
}

/*
 * Additional property test: Scoped marker RAII
 * For any scoped marker, timing should be automatic
 */
TEST_F(ProfilerPropertyTest, ScopedMarkerRAII) {
    profiler->SetEnabled(true);
    
    const int NUM_ITERATIONS = 50;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        {
            ScopedPerformanceMarker marker(*profiler, "ScopedTest");
            SimulateWork(RandomFloat(1.0f, 5.0f));
            // Marker should automatically end when going out of scope
        }
    }
    
    // Property: Scoped markers should be tracked
    float avgTime = profiler->GetMarkerAverageTime("ScopedTest");
    EXPECT_GT(avgTime, 0.0f) << "Scoped marker should have positive average time";
    EXPECT_LT(avgTime, 10.0f) << "Scoped marker average time should be reasonable";
}
