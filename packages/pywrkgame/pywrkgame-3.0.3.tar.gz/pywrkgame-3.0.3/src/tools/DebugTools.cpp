#include "pywrkgame/tools/DebugTools.h"
#include <algorithm>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <csignal>

#ifdef _WIN32
#include <windows.h>
#include <dbghelp.h>
#pragma comment(lib, "dbghelp.lib")
#elif __APPLE__
#include <execinfo.h>
#include <sys/utsname.h>
#elif __linux__
#include <execinfo.h>
#include <sys/utsname.h>
#endif

namespace pywrkgame {
namespace tools {

// AssetDependencyTracker Implementation
struct AssetDependencyTracker::Impl {
    struct AssetNode {
        std::string path;
        size_t size = 0;
        bool isLoaded = false;
        std::unordered_set<std::string> dependencies;
        std::unordered_set<std::string> dependents;
    };
    
    std::unordered_map<std::string, AssetNode> assets;
    
    bool HasCircularDependencyRecursive(
        const std::string& assetPath,
        std::unordered_set<std::string>& visited,
        std::unordered_set<std::string>& recursionStack,
        std::vector<std::string>& chain
    ) const {
        auto it = assets.find(assetPath);
        if (it == assets.end()) return false;
        
        visited.insert(assetPath);
        recursionStack.insert(assetPath);
        chain.push_back(assetPath);
        
        for (const auto& dep : it->second.dependencies) {
            if (recursionStack.find(dep) != recursionStack.end()) {
                chain.push_back(dep);
                return true;
            }
            
            if (visited.find(dep) == visited.end()) {
                if (HasCircularDependencyRecursive(dep, visited, recursionStack, chain)) {
                    return true;
                }
            }
        }
        
        recursionStack.erase(assetPath);
        chain.pop_back();
        return false;
    }
    
    size_t CalculateTotalSizeRecursive(
        const std::string& assetPath,
        std::unordered_set<std::string>& visited
    ) const {
        auto it = assets.find(assetPath);
        if (it == assets.end() || visited.find(assetPath) != visited.end()) {
            return 0;
        }
        
        visited.insert(assetPath);
        size_t totalSize = it->second.size;
        
        for (const auto& dep : it->second.dependencies) {
            totalSize += CalculateTotalSizeRecursive(dep, visited);
        }
        
        return totalSize;
    }
};

AssetDependencyTracker::AssetDependencyTracker() : pImpl(std::make_unique<Impl>()) {}
AssetDependencyTracker::~AssetDependencyTracker() = default;

void AssetDependencyTracker::RegisterAsset(const std::string& assetPath, size_t size) {
    auto& node = pImpl->assets[assetPath];
    node.path = assetPath;
    node.size = size;
    node.isLoaded = true;
}

void AssetDependencyTracker::RegisterDependency(const std::string& assetPath, const std::string& dependencyPath) {
    pImpl->assets[assetPath].dependencies.insert(dependencyPath);
    pImpl->assets[dependencyPath].dependents.insert(assetPath);
}

void AssetDependencyTracker::UnregisterAsset(const std::string& assetPath) {
    auto it = pImpl->assets.find(assetPath);
    if (it != pImpl->assets.end()) {
        // Remove from dependents
        for (const auto& dep : it->second.dependencies) {
            auto depIt = pImpl->assets.find(dep);
            if (depIt != pImpl->assets.end()) {
                depIt->second.dependents.erase(assetPath);
            }
        }
        
        pImpl->assets.erase(it);
    }
}

std::vector<std::string> AssetDependencyTracker::GetDependencies(const std::string& assetPath) const {
    auto it = pImpl->assets.find(assetPath);
    if (it == pImpl->assets.end()) {
        return {};
    }
    
    return std::vector<std::string>(it->second.dependencies.begin(), it->second.dependencies.end());
}

std::vector<std::string> AssetDependencyTracker::GetDependents(const std::string& assetPath) const {
    auto it = pImpl->assets.find(assetPath);
    if (it == pImpl->assets.end()) {
        return {};
    }
    
    return std::vector<std::string>(it->second.dependents.begin(), it->second.dependents.end());
}

AssetDependency AssetDependencyTracker::GetAssetInfo(const std::string& assetPath) const {
    AssetDependency info;
    auto it = pImpl->assets.find(assetPath);
    if (it == pImpl->assets.end()) {
        return info;
    }
    
    info.assetPath = assetPath;
    info.totalSize = it->second.size;
    info.isLoaded = it->second.isLoaded;
    info.dependencies = std::vector<std::string>(
        it->second.dependencies.begin(),
        it->second.dependencies.end()
    );
    
    return info;
}

std::vector<AssetDependency> AssetDependencyTracker::GetAllAssets() const {
    std::vector<AssetDependency> assets;
    for (const auto& [path, node] : pImpl->assets) {
        assets.push_back(GetAssetInfo(path));
    }
    return assets;
}

bool AssetDependencyTracker::HasCircularDependencies(const std::string& assetPath) const {
    std::unordered_set<std::string> visited;
    std::unordered_set<std::string> recursionStack;
    std::vector<std::string> chain;
    return pImpl->HasCircularDependencyRecursive(assetPath, visited, recursionStack, chain);
}

std::vector<std::string> AssetDependencyTracker::GetCircularDependencyChain(const std::string& assetPath) const {
    std::unordered_set<std::string> visited;
    std::unordered_set<std::string> recursionStack;
    std::vector<std::string> chain;
    pImpl->HasCircularDependencyRecursive(assetPath, visited, recursionStack, chain);
    return chain;
}

size_t AssetDependencyTracker::CalculateTotalSize(const std::string& assetPath) const {
    std::unordered_set<std::string> visited;
    return pImpl->CalculateTotalSizeRecursive(assetPath, visited);
}

void AssetDependencyTracker::Clear() {
    pImpl->assets.clear();
}

// PhysicsVisualDebugger Implementation
struct PhysicsVisualDebugger::Impl {
    bool enabled = false;
    bool drawCollisionShapes = true;
    bool drawVelocities = true;
    bool drawContactPoints = true;
    bool drawConstraints = true;
    
    PhysicsDebugData debugData;
};

PhysicsVisualDebugger::PhysicsVisualDebugger() : pImpl(std::make_unique<Impl>()) {}
PhysicsVisualDebugger::~PhysicsVisualDebugger() = default;

void PhysicsVisualDebugger::SetEnabled(bool enabled) {
    pImpl->enabled = enabled;
}

bool PhysicsVisualDebugger::IsEnabled() const {
    return pImpl->enabled;
}

void PhysicsVisualDebugger::SetDrawCollisionShapes(bool draw) {
    pImpl->drawCollisionShapes = draw;
}

void PhysicsVisualDebugger::SetDrawVelocities(bool draw) {
    pImpl->drawVelocities = draw;
}

void PhysicsVisualDebugger::SetDrawContactPoints(bool draw) {
    pImpl->drawContactPoints = draw;
}

void PhysicsVisualDebugger::SetDrawConstraints(bool draw) {
    pImpl->drawConstraints = draw;
}

PhysicsDebugData PhysicsVisualDebugger::GetDebugData() const {
    return pImpl->debugData;
}

void PhysicsVisualDebugger::UpdateFromPhysicsEngine(const void* physicsEngine) {
    if (!pImpl->enabled) return;
    
    // This would be implemented to extract debug data from the physics engine
    // For now, it's a placeholder
    pImpl->debugData.rigidBodies.clear();
    pImpl->debugData.activeCollisions.clear();
}

void PhysicsVisualDebugger::Clear() {
    pImpl->debugData.rigidBodies.clear();
    pImpl->debugData.activeCollisions.clear();
}

// CrashReporter Implementation
struct CrashReporter::Impl {
    bool initialized = false;
    CrashCallback callback;
    std::vector<CrashInfo> crashHistory;
    static CrashReporter* instance;
};

CrashReporter* CrashReporter::Impl::instance = nullptr;

CrashReporter::CrashReporter() : pImpl(std::make_unique<Impl>()) {
    Impl::instance = this;
}

CrashReporter::~CrashReporter() {
    Shutdown();
    Impl::instance = nullptr;
}

void CrashReporter::Initialize() {
    if (pImpl->initialized) return;
    
#ifdef _WIN32
    SetUnhandledExceptionFilter([](EXCEPTION_POINTERS* exceptionInfo) -> LONG {
        if (Impl::instance) {
            CrashInfo info;
            info.exceptionMessage = "Unhandled exception";
            info.stackTrace = CaptureStackTrace();
            info.timestamp = []() {
                auto now = std::chrono::system_clock::now();
                auto time = std::chrono::system_clock::to_time_t(now);
                std::stringstream ss;
                ss << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S");
                return ss.str();
            }();
            info.systemInfo = GetSystemInfo();
            
            Impl::instance->pImpl->crashHistory.push_back(info);
            if (Impl::instance->pImpl->callback) {
                Impl::instance->pImpl->callback(info);
            }
        }
        return EXCEPTION_EXECUTE_HANDLER;
    });
#else
    std::signal(SIGSEGV, SignalHandler);
    std::signal(SIGABRT, SignalHandler);
    std::signal(SIGFPE, SignalHandler);
    std::signal(SIGILL, SignalHandler);
#endif
    
    pImpl->initialized = true;
}

void CrashReporter::Shutdown() {
    if (!pImpl->initialized) return;
    
#ifndef _WIN32
    std::signal(SIGSEGV, SIG_DFL);
    std::signal(SIGABRT, SIG_DFL);
    std::signal(SIGFPE, SIG_DFL);
    std::signal(SIGILL, SIG_DFL);
#endif
    
    pImpl->initialized = false;
}

void CrashReporter::SetCrashCallback(CrashCallback callback) {
    pImpl->callback = callback;
}

void CrashReporter::ReportCrash(const std::string& message) {
    CrashInfo info;
    info.exceptionMessage = message;
    info.stackTrace = CaptureStackTrace();
    
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S");
    info.timestamp = ss.str();
    
    info.systemInfo = GetSystemInfo();
    
    pImpl->crashHistory.push_back(info);
    if (pImpl->callback) {
        pImpl->callback(info);
    }
}

void CrashReporter::ReportException(const std::exception& e) {
    ReportCrash(std::string("Exception: ") + e.what());
}

std::vector<CrashInfo> CrashReporter::GetCrashHistory() const {
    return pImpl->crashHistory;
}

CrashInfo CrashReporter::GetLastCrash() const {
    if (pImpl->crashHistory.empty()) {
        return CrashInfo();
    }
    return pImpl->crashHistory.back();
}

bool CrashReporter::SaveCrashReport(const CrashInfo& info, const std::string& filepath) const {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        return false;
    }
    
    file << "Crash Report\n";
    file << "============\n\n";
    file << "Timestamp: " << info.timestamp << "\n";
    file << "Message: " << info.exceptionMessage << "\n\n";
    
    file << "Stack Trace:\n";
    for (size_t i = 0; i < info.stackTrace.size(); ++i) {
        file << "  " << i << ": " << info.stackTrace[i] << "\n";
    }
    
    file << "\nSystem Information:\n";
    for (const auto& [key, value] : info.systemInfo) {
        file << "  " << key << ": " << value << "\n";
    }
    
    return true;
}

std::vector<std::string> CrashReporter::CaptureStackTrace(int maxDepth) {
    std::vector<std::string> trace;
    
#if defined(_WIN32)
    void* stack[64];
    HANDLE process = GetCurrentProcess();
    SymInitialize(process, nullptr, TRUE);
    
    WORD frames = CaptureStackBackTrace(0, maxDepth, stack, nullptr);
    
    SYMBOL_INFO* symbol = (SYMBOL_INFO*)calloc(sizeof(SYMBOL_INFO) + 256 * sizeof(char), 1);
    symbol->MaxNameLen = 255;
    symbol->SizeOfStruct = sizeof(SYMBOL_INFO);
    
    for (WORD i = 0; i < frames; ++i) {
        if (SymFromAddr(process, (DWORD64)stack[i], 0, symbol)) {
            trace.push_back(std::string(symbol->Name));
        } else {
            std::stringstream ss;
            ss << "0x" << std::hex << (uint64_t)stack[i];
            trace.push_back(ss.str());
        }
    }
    
    free(symbol);
#elif defined(__APPLE__) || defined(__linux__)
    void* callstack[64];
    int frames = backtrace(callstack, maxDepth);
    char** symbols = backtrace_symbols(callstack, frames);
    
    for (int i = 0; i < frames; ++i) {
        trace.push_back(symbols[i]);
    }
    
    free(symbols);
#endif
    
    return trace;
}

std::unordered_map<std::string, std::string> CrashReporter::GetSystemInfo() {
    std::unordered_map<std::string, std::string> info;
    
#ifdef _WIN32
    info["Platform"] = "Windows";
    
    SYSTEM_INFO sysInfo;
    ::GetSystemInfo(&sysInfo);
    info["Processors"] = std::to_string(sysInfo.dwNumberOfProcessors);
    
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memInfo);
    info["TotalMemory"] = std::to_string(memInfo.ullTotalPhys / (1024 * 1024)) + " MB";
    info["AvailableMemory"] = std::to_string(memInfo.ullAvailPhys / (1024 * 1024)) + " MB";
#elif defined(__APPLE__) || defined(__linux__)
    struct utsname unameData;
    if (uname(&unameData) == 0) {
        info["Platform"] = unameData.sysname;
        info["Version"] = unameData.release;
        info["Machine"] = unameData.machine;
    }
    
#ifdef __APPLE__
    info["OS"] = "macOS";
#else
    info["OS"] = "Linux";
#endif
#endif
    
    return info;
}

void CrashReporter::SignalHandler(int signal) {
    if (Impl::instance) {
        std::string message = "Signal " + std::to_string(signal);
        switch (signal) {
            case SIGSEGV: message = "Segmentation fault"; break;
            case SIGABRT: message = "Abort signal"; break;
            case SIGFPE: message = "Floating point exception"; break;
            case SIGILL: message = "Illegal instruction"; break;
        }
        
        Impl::instance->ReportCrash(message);
    }
    
    std::exit(signal);
}

} // namespace tools
} // namespace pywrkgame
