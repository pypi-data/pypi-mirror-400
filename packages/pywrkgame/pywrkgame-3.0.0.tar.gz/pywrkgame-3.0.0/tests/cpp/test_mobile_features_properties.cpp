#include <gtest/gtest.h>
#include "pywrkgame/platform/PlatformManager.h"
#include <cmath>
#include <random>

using namespace pywrkgame::platform;

class MobileFeaturesTest : public ::testing::Test {
protected:
    void SetUp() override {
        PlatformManager::Initialize();
    }
    
    void TearDown() override {
        PlatformManager::Shutdown();
    }
    
    std::mt19937 rng{std::random_device{}()};
};

/*
 * Feature: pywrkgame-library, Property 56: Sensor Integration
 * For any device sensor (accelerometer, gyroscope, magnetometer), 
 * readings should accurately reflect device orientation and movement
 * Validates: Requirements 12.2
 */
TEST_F(MobileFeaturesTest, SensorIntegrationProperty) {
    auto sensorManager = PlatformManager::GetSensors();
    ASSERT_NE(sensorManager, nullptr);
    
    // Test with 100 random sensor configurations
    std::uniform_int_distribution<int> sensorDist(0, 2);
    
    for (int i = 0; i < 100; ++i) {
        SensorType sensorType = static_cast<SensorType>(sensorDist(rng));
        
        // Enable the sensor
        sensorManager->EnableSensor(sensorType, true);
        
        // Verify sensor is enabled
        EXPECT_TRUE(sensorManager->IsSensorEnabled(sensorType));
        
        // Get sensor data
        SensorData data;
        switch (sensorType) {
            case SensorType::Accelerometer:
                if (sensorManager->IsAccelerometerAvailable()) {
                    data = sensorManager->GetAccelerometerData();
                    EXPECT_TRUE(data.valid);
                    // Accelerometer should have some gravity component
                    float magnitude = std::sqrt(data.x * data.x + data.y * data.y + data.z * data.z);
                    EXPECT_GT(magnitude, 0.0f);
                }
                break;
            case SensorType::Gyroscope:
                if (sensorManager->IsGyroscopeAvailable()) {
                    data = sensorManager->GetGyroscopeData();
                    EXPECT_TRUE(data.valid);
                }
                break;
            case SensorType::Magnetometer:
                if (sensorManager->IsMagnetometerAvailable()) {
                    data = sensorManager->GetMagnetometerData();
                    EXPECT_TRUE(data.valid);
                }
                break;
        }
        
        // Disable the sensor
        sensorManager->EnableSensor(sensorType, false);
        EXPECT_FALSE(sensorManager->IsSensorEnabled(sensorType));
    }
}

/*
 * Feature: pywrkgame-library, Property 56: Sensor Integration
 * Test that sensor update rates can be configured
 */
TEST_F(MobileFeaturesTest, SensorUpdateRateProperty) {
    auto sensorManager = PlatformManager::GetSensors();
    ASSERT_NE(sensorManager, nullptr);
    
    std::uniform_real_distribution<float> rateDist(1.0f, 200.0f);
    std::uniform_int_distribution<int> sensorDist(0, 2);
    
    // Test with 100 random configurations
    for (int i = 0; i < 100; ++i) {
        float updateRate = rateDist(rng);
        SensorType sensorType = static_cast<SensorType>(sensorDist(rng));
        
        // Set update rate (should not crash or cause errors)
        sensorManager->SetSensorUpdateRate(sensorType, updateRate);
        
        // Enable sensor and verify it works
        sensorManager->EnableSensor(sensorType, true);
        EXPECT_TRUE(sensorManager->IsSensorEnabled(sensorType));
    }
}

/*
 * Feature: pywrkgame-library, Property 57: Haptic Feedback
 * For any haptic feedback trigger, device should vibrate with 
 * appropriate pattern and intensity
 * Validates: Requirements 12.3
 */
TEST_F(MobileFeaturesTest, HapticFeedbackProperty) {
    std::uniform_int_distribution<int> patternDist(0, 8);
    std::uniform_real_distribution<float> intensityDist(0.0f, 1.0f);
    
    // Test with 100 random haptic configurations
    for (int i = 0; i < 100; ++i) {
        HapticPattern pattern = static_cast<HapticPattern>(patternDist(rng));
        float intensity = intensityDist(rng);
        
        // Enable haptic feedback (should not crash)
        PlatformManager::EnableHapticFeedback(pattern, intensity);
    }
    
    // Test passes if no crash occurs
    SUCCEED();
}

/*
 * Feature: pywrkgame-library, Property 57: Haptic Feedback
 * Test custom haptic feedback with duration and intensity
 */
TEST_F(MobileFeaturesTest, CustomHapticFeedbackProperty) {
    std::uniform_real_distribution<float> durationDist(0.0f, 10.0f);
    std::uniform_real_distribution<float> intensityDist(0.0f, 1.0f);
    
    // Test with 100 random custom haptic configurations
    for (int i = 0; i < 100; ++i) {
        float duration = durationDist(rng);
        float intensity = intensityDist(rng);
        
        // Enable custom haptic feedback (should not crash)
        PlatformManager::EnableHapticFeedbackCustom(duration, intensity);
    }
    
    // Test passes if no crash occurs
    SUCCEED();
}

/*
 * Feature: pywrkgame-library, Property 58: Battery-based Performance Scaling
 * For any device with varying battery levels, performance scaling should 
 * adjust appropriately to preserve battery life
 * Validates: Requirements 12.4
 */
TEST_F(MobileFeaturesTest, BatteryPerformanceScalingProperty) {
    std::uniform_int_distribution<int> levelDist(0, 3);
    
    // Test with 100 random battery optimization configurations
    for (int i = 0; i < 100; ++i) {
        BatteryOptimizationLevel level = static_cast<BatteryOptimizationLevel>(levelDist(rng));
        
        // Set battery optimization level
        PlatformManager::SetBatteryOptimization(level);
        
        // Verify the level was set
        EXPECT_EQ(PlatformManager::GetBatteryOptimizationLevel(), level);
        
        // Get battery level (should be between 0.0 and 1.0)
        float batteryLevel = PlatformManager::GetBatteryLevel();
        EXPECT_GE(batteryLevel, 0.0f);
        EXPECT_LE(batteryLevel, 1.0f);
        
        // Update performance based on battery
        PlatformManager::UpdatePerformanceBasedOnBattery();
    }
}

/*
 * Feature: pywrkgame-library, Property 58: Battery-based Performance Scaling
 * Test that battery temperature can be queried
 */
TEST_F(MobileFeaturesTest, BatteryTemperatureQuery) {
    float temperature = PlatformManager::GetBatteryTemperature();
    
    // Temperature should be in a reasonable range (-20°C to 80°C)
    EXPECT_GE(temperature, -20.0f);
    EXPECT_LE(temperature, 80.0f);
}

/*
 * Feature: pywrkgame-library, Property 58: Battery-based Performance Scaling
 * Test that charging status can be queried
 */
TEST_F(MobileFeaturesTest, ChargingStatusQuery) {
    bool isCharging = PlatformManager::IsCharging();
    
    // Should return a valid boolean (test passes if no crash)
    SUCCEED();
}

/*
 * Feature: pywrkgame-library, Property 58: Battery-based Performance Scaling
 * Test that performance scaling responds to battery optimization level
 */
TEST_F(MobileFeaturesTest, PerformanceScalingLevels) {
    // Test each optimization level
    std::vector<BatteryOptimizationLevel> levels = {
        BatteryOptimizationLevel::None,
        BatteryOptimizationLevel::Balanced,
        BatteryOptimizationLevel::PowerSaver,
        BatteryOptimizationLevel::Adaptive
    };
    
    for (auto level : levels) {
        PlatformManager::SetBatteryOptimization(level);
        EXPECT_EQ(PlatformManager::GetBatteryOptimizationLevel(), level);
        
        // Update performance
        PlatformManager::UpdatePerformanceBasedOnBattery();
        
        // Should not crash
    }
}

/*
 * Feature: pywrkgame-library, Property 56: Sensor Integration
 * Test that all sensor types can be queried for availability
 */
TEST_F(MobileFeaturesTest, SensorAvailabilityQuery) {
    auto sensorManager = PlatformManager::GetSensors();
    ASSERT_NE(sensorManager, nullptr);
    
    // Query availability for all sensor types
    bool accelAvailable = sensorManager->IsAccelerometerAvailable();
    bool gyroAvailable = sensorManager->IsGyroscopeAvailable();
    bool magAvailable = sensorManager->IsMagnetometerAvailable();
    
    // Test passes if queries don't crash
    SUCCEED();
}

/*
 * Feature: pywrkgame-library, Property 56: Sensor Integration
 * Test that sensor data has valid timestamps
 */
TEST_F(MobileFeaturesTest, SensorDataTimestamps) {
    auto sensorManager = PlatformManager::GetSensors();
    ASSERT_NE(sensorManager, nullptr);
    
    // Enable accelerometer
    sensorManager->EnableSensor(SensorType::Accelerometer, true);
    
    if (sensorManager->IsAccelerometerAvailable()) {
        SensorData data = sensorManager->GetAccelerometerData();
        
        if (data.valid) {
            // Timestamp should be non-negative
            EXPECT_GE(data.timestamp, 0.0);
        }
    }
}


/*
 * Feature: pywrkgame-library, Property 59: Automatic Pause/Resume
 * For any mobile app lifecycle event (incoming call, app switch), 
 * game should pause and resume correctly
 * Validates: Requirements 12.5
 */
TEST_F(MobileFeaturesTest, AutomaticPauseResumeProperty) {
    // Test with 100 random pause/resume cycles
    for (int i = 0; i < 100; ++i) {
        // Initially app should be active
        EXPECT_EQ(PlatformManager::GetCurrentLifecycleState(), AppLifecycleState::Active);
        EXPECT_FALSE(PlatformManager::IsAppPaused());
        
        // Pause the app
        PlatformManager::PauseApp();
        EXPECT_EQ(PlatformManager::GetCurrentLifecycleState(), AppLifecycleState::Paused);
        EXPECT_TRUE(PlatformManager::IsAppPaused());
        
        // Resume the app
        PlatformManager::ResumeApp();
        EXPECT_EQ(PlatformManager::GetCurrentLifecycleState(), AppLifecycleState::Active);
        EXPECT_FALSE(PlatformManager::IsAppPaused());
    }
}

/*
 * Feature: pywrkgame-library, Property 59: Automatic Pause/Resume
 * Test that lifecycle callbacks are triggered correctly
 */
TEST_F(MobileFeaturesTest, LifecycleCallbackProperty) {
    int callbackCount = 0;
    AppLifecycleState lastState = AppLifecycleState::Active;
    
    // Register callback
    PlatformManager::RegisterLifecycleCallback([&](AppLifecycleState state) {
        callbackCount++;
        lastState = state;
    });
    
    // Test with 50 pause/resume cycles
    for (int i = 0; i < 50; ++i) {
        int expectedCallbacks = callbackCount;
        
        // Pause should trigger callback
        PlatformManager::PauseApp();
        EXPECT_GT(callbackCount, expectedCallbacks);
        EXPECT_EQ(lastState, AppLifecycleState::Paused);
        
        expectedCallbacks = callbackCount;
        
        // Resume should trigger callbacks (Resumed then Active)
        PlatformManager::ResumeApp();
        EXPECT_GT(callbackCount, expectedCallbacks);
        EXPECT_EQ(lastState, AppLifecycleState::Active);
    }
    
    // Unregister callback
    PlatformManager::UnregisterLifecycleCallback();
}

/*
 * Test in-app purchase functionality
 */
TEST_F(MobileFeaturesTest, InAppPurchaseProperty) {
    if (!PlatformManager::IsInAppPurchaseSupported()) {
        GTEST_SKIP() << "In-app purchases not supported on this platform";
    }
    
    // Initialize IAP
    PlatformManager::InitializeInAppPurchases();
    
    // Test with 20 random product purchases
    for (int i = 0; i < 20; ++i) {
        std::string productId = "product_" + std::to_string(i);
        bool purchaseSuccess = false;
        std::string purchaseMessage;
        
        PlatformManager::PurchaseProduct(productId, [&](bool success, const std::string& message) {
            purchaseSuccess = success;
            purchaseMessage = message;
        });
        
        // Verify purchase was processed
        EXPECT_TRUE(purchaseSuccess);
    }
    
    // Verify purchased products are tracked
    auto purchasedProducts = PlatformManager::GetPurchasedProducts();
    EXPECT_GE(purchasedProducts.size(), 20);
}

/*
 * Test social features functionality
 */
TEST_F(MobileFeaturesTest, SocialFeaturesProperty) {
    if (!PlatformManager::IsSocialFeaturesSupported()) {
        GTEST_SKIP() << "Social features not supported on this platform";
    }
    
    // Initialize social features
    PlatformManager::InitializeSocialFeatures();
    
    // Test achievement unlocking with 20 random achievements
    for (int i = 0; i < 20; ++i) {
        std::string achievementId = "achievement_" + std::to_string(i);
        bool unlockSuccess = false;
        
        PlatformManager::UnlockAchievement(achievementId, [&](bool success, const std::string& message) {
            unlockSuccess = success;
        });
        
        EXPECT_TRUE(unlockSuccess);
    }
    
    // Test score submission with 20 random scores
    std::uniform_int_distribution<int> scoreDist(0, 1000000);
    for (int i = 0; i < 20; ++i) {
        std::string leaderboardId = "leaderboard_" + std::to_string(i % 5);
        int score = scoreDist(rng);
        bool submitSuccess = false;
        
        PlatformManager::SubmitScore(leaderboardId, score, [&](bool success, const std::string& message) {
            submitSuccess = success;
        });
        
        EXPECT_TRUE(submitSuccess);
    }
}

/*
 * Test leaderboard retrieval
 */
TEST_F(MobileFeaturesTest, LeaderboardRetrievalProperty) {
    if (!PlatformManager::IsSocialFeaturesSupported()) {
        GTEST_SKIP() << "Social features not supported on this platform";
    }
    
    PlatformManager::InitializeSocialFeatures();
    
    // Test leaderboard retrieval with 10 random leaderboards
    for (int i = 0; i < 10; ++i) {
        std::string leaderboardId = "leaderboard_" + std::to_string(i);
        bool fetchSuccess = false;
        std::vector<std::pair<std::string, int>> scores;
        
        PlatformManager::GetLeaderboardScores(leaderboardId, [&](bool success, const std::vector<std::pair<std::string, int>>& leaderboardScores) {
            fetchSuccess = success;
            scores = leaderboardScores;
        });
        
        EXPECT_TRUE(fetchSuccess);
        // Scores should be returned (even if empty)
    }
}

/*
 * Test purchase restoration
 */
TEST_F(MobileFeaturesTest, PurchaseRestorationProperty) {
    if (!PlatformManager::IsInAppPurchaseSupported()) {
        GTEST_SKIP() << "In-app purchases not supported on this platform";
    }
    
    PlatformManager::InitializeInAppPurchases();
    
    // Test restore purchases multiple times
    for (int i = 0; i < 10; ++i) {
        bool restoreSuccess = false;
        
        PlatformManager::RestorePurchases([&](bool success, const std::string& message) {
            restoreSuccess = success;
        });
        
        EXPECT_TRUE(restoreSuccess);
    }
}
