#include "pywrkgame/tools/PerformanceProfiler.h"
#include <algorithm>
#include <numeric>
#include <thread>

#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
#elif __APPLE__
#include <mach/mach.h>
#include <sys/sysctl.h>
#elif __linux__
#include <sys/sysinfo.h>
#include <fstream>
#endif

namespace pywrkgame {
namespace tools {

struct PerformanceProfiler::Impl {
    bool enabled = true;
    
    // Frame timing
    std::chrono::high_resolution_clock::time_point frameStartTime;
    std::chrono::high_resolution_clock::time_point frameEndTime;
    std::vector<float> frameTimes;
    static constexpr size_t MAX_FRAME_HISTORY = 120;
    
    // Performance markers
    std::unordered_map<std::string, PerformanceMarker> activeMarkers;
    std::unordered_map<std::string, std::vector<float>> markerHistory;
    
    // Memory tracking
    std::unordered_map<void*, size_t> allocations;
    size_t totalAllocated = 0;
    size_t totalFreed = 0;
    size_t peakUsage = 0;
    uint32_t allocationCount = 0;
    uint32_t deallocationCount = 0;
    
    // GPU/CPU stats
    GPUStats gpuStats;
    CPUStats cpuStats;
    
    void UpdateGPUStats() {
        // Platform-specific GPU stats collection
        // This is a simplified implementation
        gpuStats.drawCalls = 0; // Would be updated by rendering engine
        gpuStats.triangles = 0; // Would be updated by rendering engine
        
#ifdef _WIN32
        // Windows-specific GPU monitoring could use DXGI or similar
        gpuStats.gpuUsagePercent = 0.0f;
        gpuStats.vramUsedBytes = 0;
        gpuStats.vramTotalBytes = 0;
#elif __APPLE__
        // macOS-specific GPU monitoring
        gpuStats.gpuUsagePercent = 0.0f;
        gpuStats.vramUsedBytes = 0;
        gpuStats.vramTotalBytes = 0;
#elif __linux__
        // Linux-specific GPU monitoring (could use nvidia-smi parsing)
        gpuStats.gpuUsagePercent = 0.0f;
        gpuStats.vramUsedBytes = 0;
        gpuStats.vramTotalBytes = 0;
#endif
    }
    
    void UpdateCPUStats() {
#ifdef _WIN32
        SYSTEM_INFO sysInfo;
        GetSystemInfo(&sysInfo);
        cpuStats.activeThreads = sysInfo.dwNumberOfProcessors;
        
        // Get CPU usage
        FILETIME idleTime, kernelTime, userTime;
        if (GetSystemTimes(&idleTime, &kernelTime, &userTime)) {
            // Simplified CPU usage calculation
            cpuStats.cpuUsagePercent = 0.0f; // Would need proper calculation
        }
#elif __APPLE__
        int mib[2] = {CTL_HW, HW_NCPU};
        int numCPU = 0;
        size_t len = sizeof(numCPU);
        sysctl(mib, 2, &numCPU, &len, nullptr, 0);
        cpuStats.activeThreads = numCPU;
        cpuStats.cpuUsagePercent = 0.0f; // Would need proper calculation
#elif __linux__
        cpuStats.activeThreads = std::thread::hardware_concurrency();
        
        // Read CPU usage from /proc/stat
        std::ifstream statFile("/proc/stat");
        if (statFile.is_open()) {
            std::string line;
            std::getline(statFile, line);
            // Parse and calculate CPU usage
            cpuStats.cpuUsagePercent = 0.0f; // Simplified
        }
#endif
    }
};

PerformanceProfiler::PerformanceProfiler() : pImpl(std::make_unique<Impl>()) {}

PerformanceProfiler::~PerformanceProfiler() = default;

void PerformanceProfiler::BeginFrame() {
    if (!pImpl->enabled) return;
    
    pImpl->frameStartTime = std::chrono::high_resolution_clock::now();
}

void PerformanceProfiler::EndFrame() {
    if (!pImpl->enabled) return;
    
    pImpl->frameEndTime = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
        pImpl->frameEndTime - pImpl->frameStartTime
    );
    float frameTimeMs = duration.count() / 1000.0f;
    
    pImpl->frameTimes.push_back(frameTimeMs);
    if (pImpl->frameTimes.size() > Impl::MAX_FRAME_HISTORY) {
        pImpl->frameTimes.erase(pImpl->frameTimes.begin());
    }
    
    // Update GPU and CPU stats
    pImpl->UpdateGPUStats();
    pImpl->UpdateCPUStats();
}

void PerformanceProfiler::BeginMarker(const std::string& name) {
    if (!pImpl->enabled) return;
    
    PerformanceMarker marker;
    marker.name = name;
    marker.startTime = std::chrono::high_resolution_clock::now();
    pImpl->activeMarkers[name] = marker;
}

void PerformanceProfiler::EndMarker(const std::string& name) {
    if (!pImpl->enabled) return;
    
    auto it = pImpl->activeMarkers.find(name);
    if (it != pImpl->activeMarkers.end()) {
        it->second.endTime = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            it->second.endTime - it->second.startTime
        );
        it->second.durationMs = duration.count() / 1000.0f;
        
        // Store in history
        pImpl->markerHistory[name].push_back(it->second.durationMs);
        if (pImpl->markerHistory[name].size() > Impl::MAX_FRAME_HISTORY) {
            pImpl->markerHistory[name].erase(pImpl->markerHistory[name].begin());
        }
        
        pImpl->activeMarkers.erase(it);
    }
}

FrameStats PerformanceProfiler::GetFrameStats() const {
    FrameStats stats;
    
    if (pImpl->frameTimes.empty()) {
        return stats;
    }
    
    stats.frameTime = pImpl->frameTimes.back();
    stats.fps = 1000.0f / stats.frameTime;
    
    float sum = std::accumulate(pImpl->frameTimes.begin(), pImpl->frameTimes.end(), 0.0f);
    stats.averageFrameTime = sum / pImpl->frameTimes.size();
    
    stats.minFrameTime = *std::min_element(pImpl->frameTimes.begin(), pImpl->frameTimes.end());
    stats.maxFrameTime = *std::max_element(pImpl->frameTimes.begin(), pImpl->frameTimes.end());
    
    return stats;
}

GPUStats PerformanceProfiler::GetGPUStats() const {
    return pImpl->gpuStats;
}

CPUStats PerformanceProfiler::GetCPUStats() const {
    return pImpl->cpuStats;
}

MemoryStats PerformanceProfiler::GetMemoryStats() const {
    MemoryStats stats;
    stats.totalAllocated = pImpl->totalAllocated;
    stats.totalFreed = pImpl->totalFreed;
    stats.currentUsage = pImpl->totalAllocated - pImpl->totalFreed;
    stats.peakUsage = pImpl->peakUsage;
    stats.allocationCount = pImpl->allocationCount;
    stats.deallocationCount = pImpl->deallocationCount;
    
    for (const auto& [ptr, size] : pImpl->allocations) {
        stats.activeAllocations.push_back({ptr, size});
    }
    
    return stats;
}

float PerformanceProfiler::GetMarkerAverageTime(const std::string& name) const {
    auto it = pImpl->markerHistory.find(name);
    if (it == pImpl->markerHistory.end() || it->second.empty()) {
        return 0.0f;
    }
    
    float sum = std::accumulate(it->second.begin(), it->second.end(), 0.0f);
    return sum / it->second.size();
}

std::vector<PerformanceMarker> PerformanceProfiler::GetActiveMarkers() const {
    std::vector<PerformanceMarker> markers;
    for (const auto& [name, marker] : pImpl->activeMarkers) {
        markers.push_back(marker);
    }
    return markers;
}

void PerformanceProfiler::TrackAllocation(void* ptr, size_t size) {
    if (!pImpl->enabled || ptr == nullptr) return;
    
    pImpl->allocations[ptr] = size;
    pImpl->totalAllocated += size;
    pImpl->allocationCount++;
    
    size_t currentUsage = pImpl->totalAllocated - pImpl->totalFreed;
    if (currentUsage > pImpl->peakUsage) {
        pImpl->peakUsage = currentUsage;
    }
}

void PerformanceProfiler::TrackDeallocation(void* ptr) {
    if (!pImpl->enabled || ptr == nullptr) return;
    
    auto it = pImpl->allocations.find(ptr);
    if (it != pImpl->allocations.end()) {
        pImpl->totalFreed += it->second;
        pImpl->deallocationCount++;
        pImpl->allocations.erase(it);
    }
}

bool PerformanceProfiler::HasMemoryLeaks() const {
    return !pImpl->allocations.empty();
}

std::vector<std::pair<void*, size_t>> PerformanceProfiler::GetMemoryLeaks() const {
    std::vector<std::pair<void*, size_t>> leaks;
    for (const auto& [ptr, size] : pImpl->allocations) {
        leaks.push_back({ptr, size});
    }
    return leaks;
}

void PerformanceProfiler::Reset() {
    pImpl->frameTimes.clear();
    pImpl->markerHistory.clear();
    pImpl->activeMarkers.clear();
}

void PerformanceProfiler::SetEnabled(bool enabled) {
    pImpl->enabled = enabled;
}

bool PerformanceProfiler::IsEnabled() const {
    return pImpl->enabled;
}

// ScopedPerformanceMarker implementation
ScopedPerformanceMarker::ScopedPerformanceMarker(PerformanceProfiler& profiler, const std::string& name)
    : profiler(profiler), name(name) {
    profiler.BeginMarker(name);
}

ScopedPerformanceMarker::~ScopedPerformanceMarker() {
    profiler.EndMarker(name);
}

} // namespace tools
} // namespace pywrkgame
