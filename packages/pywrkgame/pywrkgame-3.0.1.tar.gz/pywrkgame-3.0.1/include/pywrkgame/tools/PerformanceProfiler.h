#pragma once

#include <chrono>
#include <vector>
#include <string>
#include <unordered_map>
#include <memory>

namespace pywrkgame {
namespace tools {

// GPU Statistics
struct GPUStats {
    float gpuUsagePercent = 0.0f;
    size_t vramUsedBytes = 0;
    size_t vramTotalBytes = 0;
    float gpuTemperature = 0.0f;
    uint32_t drawCalls = 0;
    uint32_t triangles = 0;
};

// CPU Statistics
struct CPUStats {
    float cpuUsagePercent = 0.0f;
    uint32_t activeThreads = 0;
    float cpuTemperature = 0.0f;
};

// Memory Statistics
struct MemoryStats {
    size_t totalAllocated = 0;
    size_t totalFreed = 0;
    size_t currentUsage = 0;
    size_t peakUsage = 0;
    uint32_t allocationCount = 0;
    uint32_t deallocationCount = 0;
    std::vector<std::pair<void*, size_t>> activeAllocations;
};

// Frame Statistics
struct FrameStats {
    float frameTime = 0.0f;
    float fps = 0.0f;
    float averageFrameTime = 0.0f;
    float minFrameTime = 0.0f;
    float maxFrameTime = 0.0f;
};

// Performance Marker for profiling specific sections
struct PerformanceMarker {
    std::string name;
    std::chrono::high_resolution_clock::time_point startTime;
    std::chrono::high_resolution_clock::time_point endTime;
    float durationMs = 0.0f;
};

class PerformanceProfiler {
public:
    PerformanceProfiler();
    ~PerformanceProfiler();

    // Frame timing
    void BeginFrame();
    void EndFrame();
    
    // Performance markers
    void BeginMarker(const std::string& name);
    void EndMarker(const std::string& name);
    
    // Statistics retrieval
    FrameStats GetFrameStats() const;
    GPUStats GetGPUStats() const;
    CPUStats GetCPUStats() const;
    MemoryStats GetMemoryStats() const;
    
    // Get marker statistics
    float GetMarkerAverageTime(const std::string& name) const;
    std::vector<PerformanceMarker> GetActiveMarkers() const;
    
    // Memory tracking
    void TrackAllocation(void* ptr, size_t size);
    void TrackDeallocation(void* ptr);
    
    // Memory leak detection
    bool HasMemoryLeaks() const;
    std::vector<std::pair<void*, size_t>> GetMemoryLeaks() const;
    
    // Reset statistics
    void Reset();
    
    // Enable/disable profiling
    void SetEnabled(bool enabled);
    bool IsEnabled() const;

private:
    struct Impl;
    std::unique_ptr<Impl> pImpl;
};

// RAII helper for automatic marker timing
class ScopedPerformanceMarker {
public:
    ScopedPerformanceMarker(PerformanceProfiler& profiler, const std::string& name);
    ~ScopedPerformanceMarker();

private:
    PerformanceProfiler& profiler;
    std::string name;
};

} // namespace tools
} // namespace pywrkgame
