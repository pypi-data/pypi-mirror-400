#include <gtest/gtest.h>
#include "pywrkgame/platform/PlatformManager.h"

using namespace pywrkgame::platform;

class PlatformManagerTest : public ::testing::Test {
protected:
    void SetUp() override {
        PlatformManager::Initialize();
    }
    
    void TearDown() override {
        PlatformManager::Shutdown();
    }
};

TEST_F(PlatformManagerTest, PlatformDetection) {
    PlatformType platform = PlatformManager::GetCurrentPlatform();
    EXPECT_NE(platform, PlatformType::Unknown);
    
    // Should detect one of the supported platforms
    bool isSupportedPlatform = (platform == PlatformType::Windows ||
                               platform == PlatformType::macOS ||
                               platform == PlatformType::Linux ||
                               platform == PlatformType::Android ||
                               platform == PlatformType::iOS ||
                               platform == PlatformType::PlayStation ||
                               platform == PlatformType::Xbox ||
                               platform == PlatformType::NintendoSwitch ||
                               platform == PlatformType::OculusVR ||
                               platform == PlatformType::HTCVive ||
                               platform == PlatformType::ARCore ||
                               platform == PlatformType::ARKit);
    EXPECT_TRUE(isSupportedPlatform);
}

TEST_F(PlatformManagerTest, PlatformNameAndVersion) {
    std::string platformName = PlatformManager::GetPlatformName();
    EXPECT_FALSE(platformName.empty());
    EXPECT_NE(platformName, "Unknown");
    
    std::string platformVersion = PlatformManager::GetPlatformVersion();
    EXPECT_FALSE(platformVersion.empty());
}

TEST_F(PlatformManagerTest, GraphicsAPISupport) {
    PlatformType platform = PlatformManager::GetCurrentPlatform();
    
    switch (platform) {
        case PlatformType::Windows:
            EXPECT_TRUE(PlatformManager::SupportsVulkan());
            EXPECT_TRUE(PlatformManager::SupportsDirectX12());
            EXPECT_TRUE(PlatformManager::SupportsOpenGL());
            EXPECT_FALSE(PlatformManager::SupportsMetal());
            break;
            
        case PlatformType::macOS:
        case PlatformType::iOS:
            EXPECT_TRUE(PlatformManager::SupportsMetal());
            EXPECT_TRUE(PlatformManager::SupportsOpenGL());
            EXPECT_FALSE(PlatformManager::SupportsVulkan());
            EXPECT_FALSE(PlatformManager::SupportsDirectX12());
            break;
            
        case PlatformType::Linux:
        case PlatformType::Android:
            EXPECT_TRUE(PlatformManager::SupportsVulkan());
            EXPECT_TRUE(PlatformManager::SupportsOpenGL());
            EXPECT_FALSE(PlatformManager::SupportsMetal());
            EXPECT_FALSE(PlatformManager::SupportsDirectX12());
            break;
            
        case PlatformType::PlayStation:
        case PlatformType::Xbox:
            EXPECT_TRUE(PlatformManager::SupportsVulkan());
            EXPECT_TRUE(PlatformManager::SupportsRayTracing());
            break;
            
        default:
            // Other platforms - basic OpenGL support expected
            EXPECT_TRUE(PlatformManager::SupportsOpenGL());
            break;
    }
}

TEST_F(PlatformManagerTest, PlatformCategoryDetection) {
    PlatformType platform = PlatformManager::GetCurrentPlatform();
    
    // Test mobile platform detection
    bool isMobile = PlatformManager::IsMobilePlatform();
    if (platform == PlatformType::Android || platform == PlatformType::iOS) {
        EXPECT_TRUE(isMobile);
    } else {
        EXPECT_FALSE(isMobile);
    }
    
    // Test console platform detection
    bool isConsole = PlatformManager::IsConsolePlatform();
    if (platform == PlatformType::PlayStation || 
        platform == PlatformType::Xbox || 
        platform == PlatformType::NintendoSwitch) {
        EXPECT_TRUE(isConsole);
    } else {
        EXPECT_FALSE(isConsole);
    }
    
    // Test VR platform detection
    bool isVR = PlatformManager::IsVRPlatform();
    if (platform == PlatformType::OculusVR || platform == PlatformType::HTCVive) {
        EXPECT_TRUE(isVR);
    } else {
        EXPECT_FALSE(isVR);
    }
    
    // Test AR platform detection
    bool isAR = PlatformManager::IsARPlatform();
    if (platform == PlatformType::ARCore || platform == PlatformType::ARKit) {
        EXPECT_TRUE(isAR);
    } else {
        EXPECT_FALSE(isAR);
    }
}

TEST_F(PlatformManagerTest, PlatformCapabilities) {
    PlatformType platform = PlatformManager::GetCurrentPlatform();
    
    // Test input capabilities
    if (PlatformManager::IsMobilePlatform()) {
        EXPECT_TRUE(PlatformManager::HasTouchScreen());
        EXPECT_FALSE(PlatformManager::HasKeyboard());
        EXPECT_FALSE(PlatformManager::HasMouse());
        EXPECT_TRUE(PlatformManager::HasSensors());
        EXPECT_TRUE(PlatformManager::HasCamera());
        EXPECT_TRUE(PlatformManager::HasGPS());
        EXPECT_TRUE(PlatformManager::HasHapticFeedback());
    } else if (PlatformManager::IsConsolePlatform()) {
        EXPECT_FALSE(PlatformManager::HasTouchScreen());
        EXPECT_FALSE(PlatformManager::HasKeyboard());
        EXPECT_FALSE(PlatformManager::HasMouse());
        EXPECT_TRUE(PlatformManager::HasGamepad());
        EXPECT_TRUE(PlatformManager::HasHapticFeedback());
    } else if (PlatformManager::IsVRPlatform()) {
        EXPECT_FALSE(PlatformManager::HasKeyboard());
        EXPECT_FALSE(PlatformManager::HasMouse());
        EXPECT_TRUE(PlatformManager::HasSensors());
        EXPECT_TRUE(PlatformManager::HasHapticFeedback());
    } else {
        // Desktop platforms
        EXPECT_TRUE(PlatformManager::HasKeyboard());
        EXPECT_TRUE(PlatformManager::HasMouse());
        EXPECT_FALSE(PlatformManager::HasTouchScreen());
        EXPECT_FALSE(PlatformManager::HasSensors());
    }
    
    // All platforms should have microphone support
    EXPECT_TRUE(PlatformManager::HasMicrophone());
}

TEST_F(PlatformManagerTest, MemoryAndPerformanceInfo) {
    size_t totalMemory = PlatformManager::GetTotalMemory();
    size_t availableMemory = PlatformManager::GetAvailableMemory();
    int cpuCores = PlatformManager::GetCPUCoreCount();
    std::string gpuName = PlatformManager::GetGPUName();
    
    // Memory should be non-zero on real systems
    if (totalMemory > 0) {
        EXPECT_GT(totalMemory, 0);
        EXPECT_LE(availableMemory, totalMemory);
    }
    
    // CPU cores should be at least 1
    EXPECT_GE(cpuCores, 1);
    
    // GPU name should not be empty
    EXPECT_FALSE(gpuName.empty());
}

TEST_F(PlatformManagerTest, MobileSpecificFeatures) {
    if (PlatformManager::IsMobilePlatform()) {
        // Test battery information
        float batteryLevel = PlatformManager::GetBatteryLevel();
        EXPECT_GE(batteryLevel, 0.0f);
        EXPECT_LE(batteryLevel, 1.0f);
        
        // Test sensor manager
        SensorManager* sensorManager = PlatformManager::GetSensors();
        ASSERT_NE(sensorManager, nullptr);
        
        // Mobile platforms should have accelerometer
        EXPECT_TRUE(sensorManager->IsAccelerometerAvailable());
        
        // Test sensor data
        SensorData accelData = sensorManager->GetAccelerometerData();
        // Should have some gravity component (default is -9.81 on Z)
        EXPECT_NE(accelData.z, 0.0f);
        
        // Test touch input manager
        TouchInputManager* touchManager = PlatformManager::GetTouchInput();
        ASSERT_NE(touchManager, nullptr);
        EXPECT_TRUE(touchManager->IsMultiTouchSupported());
        EXPECT_GT(touchManager->GetMaxTouchPoints(), 1);
    }
}

TEST_F(PlatformManagerTest, ConsoleSpecificFeatures) {
    if (PlatformManager::IsConsolePlatform()) {
        // Test controller support
        int controllerCount = PlatformManager::GetConnectedControllerCount();
        EXPECT_GE(controllerCount, 0);
        
        // Test controller vibration (should not crash)
        PlatformManager::SetControllerVibration(0, 0.5f);
        PlatformManager::SetControllerVibration(0, 0.0f);
    }
}

TEST_F(PlatformManagerTest, VRARFeatures) {
    if (PlatformManager::IsVRPlatform()) {
        EXPECT_TRUE(PlatformManager::IsVRHeadsetConnected());
        
        // Test VR mode (should not crash)
        PlatformManager::EnableVRMode(true);
        PlatformManager::EnableVRMode(false);
    }
    
    if (PlatformManager::IsARSupported()) {
        // Test AR mode (should not crash)
        PlatformManager::EnableARMode(true);
        PlatformManager::EnableARMode(false);
    }
}

TEST_F(PlatformManagerTest, HapticFeedback) {
    if (PlatformManager::HasHapticFeedback()) {
        // Test different haptic patterns (should not crash)
        PlatformManager::EnableHapticFeedback(HapticPattern::Light);
        PlatformManager::EnableHapticFeedback(HapticPattern::Medium);
        PlatformManager::EnableHapticFeedback(HapticPattern::Heavy);
    }
}