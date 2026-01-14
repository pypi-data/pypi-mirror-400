#include <gtest/gtest.h>
#include "pywrkgame/tools/DebugTools.h"
#include <random>
#include <vector>
#include <algorithm>
#include <fstream>

using namespace pywrkgame::tools;

// Property-based test helper class
class DebugToolsPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        assetTracker = std::make_unique<AssetDependencyTracker>();
        physicsDebugger = std::make_unique<PhysicsVisualDebugger>();
        crashReporter = std::make_unique<CrashReporter>();
        rng.seed(42); // Fixed seed for reproducibility
    }
    
    void TearDown() override {
        assetTracker->Clear();
        physicsDebugger->Clear();
    }
    
    // Generate random string
    std::string RandomString(int length = 10) {
        const char* chars = "abcdefghijklmnopqrstuvwxyz0123456789";
        std::string result;
        std::uniform_int_distribution<int> dist(0, 35);
        for (int i = 0; i < length; ++i) {
            result += chars[dist(rng)];
        }
        return result;
    }
    
    // Generate random size
    size_t RandomSize(size_t min = 1024, size_t max = 1024 * 1024) {
        std::uniform_int_distribution<size_t> dist(min, max);
        return dist(rng);
    }
    
    // Generate random int
    int RandomInt(int min = 0, int max = 100) {
        std::uniform_int_distribution<int> dist(min, max);
        return dist(rng);
    }
    
    std::unique_ptr<AssetDependencyTracker> assetTracker;
    std::unique_ptr<PhysicsVisualDebugger> physicsDebugger;
    std::unique_ptr<CrashReporter> crashReporter;
    std::mt19937 rng;
};

/*
 * Feature: pywrkgame-library, Property 54: Asset Dependency Tracking
 * For any loaded asset, dependency tracking should correctly identify all required dependencies
 * Validates: Requirements 10.4
 */
TEST_F(DebugToolsPropertyTest, Property54_AssetDependencyTracking) {
    const int NUM_ITERATIONS = 100;
    std::vector<std::string> assetPaths;
    
    // Create random assets
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        std::string assetPath = "asset_" + std::to_string(i) + ".dat";
        size_t size = RandomSize(1024, 100 * 1024);
        
        assetTracker->RegisterAsset(assetPath, size);
        assetPaths.push_back(assetPath);
    }
    
    // Property 1: All registered assets should be retrievable
    std::vector<AssetDependency> allAssets = assetTracker->GetAllAssets();
    EXPECT_EQ(allAssets.size(), NUM_ITERATIONS) 
        << "All registered assets should be retrievable";
    
    // Create random dependency relationships
    std::vector<std::pair<std::string, std::string>> dependencies;
    for (int i = 0; i < NUM_ITERATIONS / 2; ++i) {
        int assetIdx = RandomInt(0, assetPaths.size() - 1);
        int depIdx = RandomInt(0, assetPaths.size() - 1);
        
        if (assetIdx != depIdx) {
            std::string asset = assetPaths[assetIdx];
            std::string dependency = assetPaths[depIdx];
            
            assetTracker->RegisterDependency(asset, dependency);
            dependencies.push_back({asset, dependency});
        }
    }
    
    // Property 2: All registered dependencies should be retrievable
    for (const auto& [asset, dependency] : dependencies) {
        std::vector<std::string> deps = assetTracker->GetDependencies(asset);
        EXPECT_TRUE(std::find(deps.begin(), deps.end(), dependency) != deps.end())
            << "Registered dependency should be retrievable";
        
        // Property 3: Dependent relationship should be bidirectional
        std::vector<std::string> dependents = assetTracker->GetDependents(dependency);
        EXPECT_TRUE(std::find(dependents.begin(), dependents.end(), asset) != dependents.end())
            << "Dependent relationship should be bidirectional";
    }
    
    // Property 4: Asset info should contain correct data
    for (const std::string& assetPath : assetPaths) {
        AssetDependency info = assetTracker->GetAssetInfo(assetPath);
        EXPECT_EQ(info.assetPath, assetPath) << "Asset path should match";
        EXPECT_GT(info.totalSize, 0u) << "Asset size should be positive";
        EXPECT_TRUE(info.isLoaded) << "Asset should be marked as loaded";
    }
    
    // Property 5: Total size calculation should include dependencies
    for (const std::string& assetPath : assetPaths) {
        size_t totalSize = assetTracker->CalculateTotalSize(assetPath);
        AssetDependency info = assetTracker->GetAssetInfo(assetPath);
        
        // Total size should be at least the asset's own size
        EXPECT_GE(totalSize, info.totalSize) 
            << "Total size should include at least the asset's own size";
    }
    
    // Property 6: Unregistering an asset should remove it
    if (!assetPaths.empty()) {
        std::string assetToRemove = assetPaths[0];
        assetTracker->UnregisterAsset(assetToRemove);
        
        AssetDependency info = assetTracker->GetAssetInfo(assetToRemove);
        EXPECT_EQ(info.assetPath, "") << "Unregistered asset should not be found";
    }
}

/*
 * Feature: pywrkgame-library, Property 54: Circular Dependency Detection
 * For any asset dependency graph, circular dependencies should be detected
 */
TEST_F(DebugToolsPropertyTest, Property54_CircularDependencyDetection) {
    // Create a simple circular dependency: A -> B -> C -> A
    assetTracker->RegisterAsset("asset_a.dat", 1024);
    assetTracker->RegisterAsset("asset_b.dat", 2048);
    assetTracker->RegisterAsset("asset_c.dat", 3072);
    
    assetTracker->RegisterDependency("asset_a.dat", "asset_b.dat");
    assetTracker->RegisterDependency("asset_b.dat", "asset_c.dat");
    assetTracker->RegisterDependency("asset_c.dat", "asset_a.dat");
    
    // Property 1: Circular dependency should be detected
    EXPECT_TRUE(assetTracker->HasCircularDependencies("asset_a.dat"))
        << "Should detect circular dependency starting from asset_a";
    EXPECT_TRUE(assetTracker->HasCircularDependencies("asset_b.dat"))
        << "Should detect circular dependency starting from asset_b";
    EXPECT_TRUE(assetTracker->HasCircularDependencies("asset_c.dat"))
        << "Should detect circular dependency starting from asset_c";
    
    // Property 2: Circular dependency chain should be retrievable
    std::vector<std::string> chain = assetTracker->GetCircularDependencyChain("asset_a.dat");
    EXPECT_GT(chain.size(), 0u) << "Circular dependency chain should not be empty";
    
    // Property 3: Chain should contain the starting asset
    EXPECT_TRUE(std::find(chain.begin(), chain.end(), "asset_a.dat") != chain.end())
        << "Chain should contain the starting asset";
    
    // Test non-circular dependencies
    assetTracker->Clear();
    assetTracker->RegisterAsset("asset_x.dat", 1024);
    assetTracker->RegisterAsset("asset_y.dat", 2048);
    assetTracker->RegisterAsset("asset_z.dat", 3072);
    
    assetTracker->RegisterDependency("asset_x.dat", "asset_y.dat");
    assetTracker->RegisterDependency("asset_y.dat", "asset_z.dat");
    
    // Property 4: Non-circular dependencies should not be detected as circular
    EXPECT_FALSE(assetTracker->HasCircularDependencies("asset_x.dat"))
        << "Should not detect circular dependency in linear chain";
}

/*
 * Feature: pywrkgame-library, Property 54: Complex Dependency Graphs
 * For any complex dependency graph, tracking should remain accurate
 */
TEST_F(DebugToolsPropertyTest, Property54_ComplexDependencyGraphs) {
    const int NUM_ASSETS = 50;
    std::vector<std::string> assets;
    
    // Create assets
    for (int i = 0; i < NUM_ASSETS; ++i) {
        std::string assetPath = "complex_asset_" + std::to_string(i) + ".dat";
        assetTracker->RegisterAsset(assetPath, RandomSize());
        assets.push_back(assetPath);
    }
    
    // Create complex dependency graph (tree-like structure)
    for (int i = 1; i < NUM_ASSETS; ++i) {
        int parentIdx = (i - 1) / 2; // Binary tree structure
        assetTracker->RegisterDependency(assets[i], assets[parentIdx]);
    }
    
    // Property 1: Root asset should have many dependents (not dependencies)
    std::vector<std::string> rootDependents = assetTracker->GetDependents(assets[0]);
    EXPECT_GT(rootDependents.size(), 0u) 
        << "Root asset should have dependents in tree structure";
    
    // Property 2: Leaf assets should have dependencies but no dependents
    int leafIdx = NUM_ASSETS - 1;
    std::vector<std::string> leafDeps = assetTracker->GetDependencies(assets[leafIdx]);
    EXPECT_EQ(leafDeps.size(), 1u) 
        << "Leaf asset should have exactly one dependency";
    
    std::vector<std::string> leafDependents = assetTracker->GetDependents(assets[leafIdx]);
    EXPECT_EQ(leafDependents.size(), 0u) 
        << "Leaf asset should have no dependents";
    
    // Property 3: Leaf total size should include parent chain
    size_t leafTotalSize = assetTracker->CalculateTotalSize(assets[leafIdx]);
    AssetDependency leafInfo = assetTracker->GetAssetInfo(assets[leafIdx]);
    EXPECT_GT(leafTotalSize, leafInfo.totalSize) 
        << "Leaf asset total size should include parent chain";
    
    // Property 4: Each asset (except root) should have exactly one dependency
    for (int i = 1; i < NUM_ASSETS; ++i) {
        std::vector<std::string> deps = assetTracker->GetDependencies(assets[i]);
        EXPECT_EQ(deps.size(), 1u) 
            << "Each non-root asset should have exactly one dependency in tree structure";
    }
    
    // Property 5: Root should have no dependencies
    std::vector<std::string> rootDeps = assetTracker->GetDependencies(assets[0]);
    EXPECT_EQ(rootDeps.size(), 0u) << "Root asset should have no dependencies";
}

/*
 * Feature: pywrkgame-library, Property 55: Crash Reporting
 * For any application crash, crash reports with accurate stack traces should be generated automatically
 * Validates: Requirements 10.7
 */
TEST_F(DebugToolsPropertyTest, Property55_CrashReporting) {
    crashReporter->Initialize();
    
    // Property 1: Manual crash reporting should work
    std::string testMessage = "Test crash message";
    crashReporter->ReportCrash(testMessage);
    
    std::vector<CrashInfo> history = crashReporter->GetCrashHistory();
    EXPECT_EQ(history.size(), 1u) << "Crash should be recorded in history";
    
    CrashInfo lastCrash = crashReporter->GetLastCrash();
    EXPECT_EQ(lastCrash.exceptionMessage, testMessage) 
        << "Crash message should match";
    
    // Property 2: Stack trace should be captured
    EXPECT_GT(lastCrash.stackTrace.size(), 0u) 
        << "Stack trace should be captured";
    
    // Property 3: Timestamp should be set
    EXPECT_FALSE(lastCrash.timestamp.empty()) 
        << "Timestamp should be set";
    
    // Property 4: System info should be captured
    EXPECT_GT(lastCrash.systemInfo.size(), 0u) 
        << "System info should be captured";
    
    // Property 5: Multiple crashes should be tracked
    for (int i = 0; i < 10; ++i) {
        crashReporter->ReportCrash("Crash " + std::to_string(i));
    }
    
    history = crashReporter->GetCrashHistory();
    EXPECT_EQ(history.size(), 11u) << "All crashes should be tracked";
    
    // Property 6: Exception reporting should work
    try {
        throw std::runtime_error("Test exception");
    } catch (const std::exception& e) {
        crashReporter->ReportException(e);
    }
    
    history = crashReporter->GetCrashHistory();
    EXPECT_EQ(history.size(), 12u) << "Exception should be tracked";
    
    lastCrash = crashReporter->GetLastCrash();
    EXPECT_TRUE(lastCrash.exceptionMessage.find("Test exception") != std::string::npos)
        << "Exception message should be captured";
    
    crashReporter->Shutdown();
}

/*
 * Feature: pywrkgame-library, Property 55: Crash Report Saving
 * For any crash report, it should be saveable to a file
 */
TEST_F(DebugToolsPropertyTest, Property55_CrashReportSaving) {
    crashReporter->Initialize();
    
    // Generate a crash report
    crashReporter->ReportCrash("Test crash for file saving");
    CrashInfo crashInfo = crashReporter->GetLastCrash();
    
    // Property 1: Crash report should be saveable to file
    std::string filepath = "test_crash_report.txt";
    bool saved = crashReporter->SaveCrashReport(crashInfo, filepath);
    EXPECT_TRUE(saved) << "Crash report should be saved successfully";
    
    // Property 2: Saved file should exist and contain crash information
    std::ifstream file(filepath);
    EXPECT_TRUE(file.is_open()) << "Crash report file should exist";
    
    if (file.is_open()) {
        std::string content((std::istreambuf_iterator<char>(file)),
                           std::istreambuf_iterator<char>());
        
        // Property 3: File should contain crash message
        EXPECT_TRUE(content.find("Test crash for file saving") != std::string::npos)
            << "File should contain crash message";
        
        // Property 4: File should contain timestamp
        EXPECT_TRUE(content.find("Timestamp:") != std::string::npos)
            << "File should contain timestamp";
        
        // Property 5: File should contain stack trace section
        EXPECT_TRUE(content.find("Stack Trace:") != std::string::npos)
            << "File should contain stack trace section";
        
        // Property 6: File should contain system info section
        EXPECT_TRUE(content.find("System Information:") != std::string::npos)
            << "File should contain system information section";
        
        file.close();
    }
    
    // Clean up
    std::remove(filepath.c_str());
    
    crashReporter->Shutdown();
}

/*
 * Feature: pywrkgame-library, Property 55: Stack Trace Capture
 * For any point in execution, stack trace should be capturable
 */
TEST_F(DebugToolsPropertyTest, Property55_StackTraceCapture) {
    // Property 1: Stack trace should be capturable
    std::vector<std::string> stackTrace = CrashReporter::CaptureStackTrace();
    EXPECT_GT(stackTrace.size(), 0u) << "Stack trace should contain frames";
    
    // Property 2: Stack trace depth should be controllable
    std::vector<std::string> shortTrace = CrashReporter::CaptureStackTrace(5);
    EXPECT_LE(shortTrace.size(), 5u) << "Stack trace should respect max depth";
    
    // Property 3: Stack trace should contain function information
    bool hasValidFrames = false;
    for (const std::string& frame : stackTrace) {
        if (!frame.empty()) {
            hasValidFrames = true;
            break;
        }
    }
    EXPECT_TRUE(hasValidFrames) << "Stack trace should contain valid frames";
}

/*
 * Feature: pywrkgame-library, Property 55: System Information Collection
 * For any system, system information should be collectible
 */
TEST_F(DebugToolsPropertyTest, Property55_SystemInformationCollection) {
    // Property 1: System info should be collectible
    auto systemInfo = CrashReporter::GetSystemInfo();
    EXPECT_GT(systemInfo.size(), 0u) << "System info should contain data";
    
    // Property 2: System info should contain platform information
    EXPECT_TRUE(systemInfo.find("Platform") != systemInfo.end() ||
                systemInfo.find("OS") != systemInfo.end())
        << "System info should contain platform/OS information";
    
    // Property 3: All system info values should be non-empty
    for (const auto& [key, value] : systemInfo) {
        EXPECT_FALSE(key.empty()) << "System info key should not be empty";
        EXPECT_FALSE(value.empty()) << "System info value should not be empty";
    }
}

/*
 * Additional property test: Physics debugger enable/disable
 * For any physics debugger state, enabling/disabling should work correctly
 */
TEST_F(DebugToolsPropertyTest, PhysicsDebuggerEnableDisable) {
    // Property 1: Physics debugger should start disabled
    EXPECT_FALSE(physicsDebugger->IsEnabled());
    
    // Property 2: Enabling should work
    physicsDebugger->SetEnabled(true);
    EXPECT_TRUE(physicsDebugger->IsEnabled());
    
    // Property 3: Disabling should work
    physicsDebugger->SetEnabled(false);
    EXPECT_FALSE(physicsDebugger->IsEnabled());
}

/*
 * Additional property test: Physics debugger visualization options
 * For any visualization option, it should be settable
 */
TEST_F(DebugToolsPropertyTest, PhysicsDebuggerVisualizationOptions) {
    physicsDebugger->SetEnabled(true);
    
    // Property: All visualization options should be settable without errors
    physicsDebugger->SetDrawCollisionShapes(true);
    physicsDebugger->SetDrawVelocities(true);
    physicsDebugger->SetDrawContactPoints(true);
    physicsDebugger->SetDrawConstraints(true);
    
    physicsDebugger->SetDrawCollisionShapes(false);
    physicsDebugger->SetDrawVelocities(false);
    physicsDebugger->SetDrawContactPoints(false);
    physicsDebugger->SetDrawConstraints(false);
    
    // If we get here without crashes, the property holds
    SUCCEED();
}

/*
 * Additional property test: Crash callback functionality
 * For any crash callback, it should be invoked on crash
 */
TEST_F(DebugToolsPropertyTest, CrashCallbackFunctionality) {
    crashReporter->Initialize();
    
    bool callbackInvoked = false;
    CrashInfo receivedInfo;
    
    crashReporter->SetCrashCallback([&](const CrashInfo& info) {
        callbackInvoked = true;
        receivedInfo = info;
    });
    
    // Property: Callback should be invoked when crash is reported
    std::string testMessage = "Callback test crash";
    crashReporter->ReportCrash(testMessage);
    
    EXPECT_TRUE(callbackInvoked) << "Crash callback should be invoked";
    EXPECT_EQ(receivedInfo.exceptionMessage, testMessage) 
        << "Callback should receive correct crash info";
    
    crashReporter->Shutdown();
}
