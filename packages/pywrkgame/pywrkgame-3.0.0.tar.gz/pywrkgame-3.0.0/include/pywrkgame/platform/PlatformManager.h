#pragma once

#include "TouchInputManager.h"
#include <memory>
#include <vector>
#include <string>
#include <functional>

namespace pywrkgame {
namespace platform {

enum class PlatformType {
    Windows,
    macOS,
    Linux,
    Android,
    iOS,
    PlayStation,
    Xbox,
    NintendoSwitch,
    OculusVR,
    HTCVive,
    ARCore,
    ARKit,
    Unknown
};

enum class HapticPattern {
    Light,
    Medium,
    Heavy,
    Success,
    Warning,
    Error,
    Selection,
    Impact,
    Custom
};

enum class BatteryOptimizationLevel {
    None,           // No optimization, full performance
    Balanced,       // Balanced performance and battery life
    PowerSaver,     // Aggressive power saving
    Adaptive        // Automatically adjust based on battery level
};

enum class AppLifecycleState {
    Active,         // App is in foreground and active
    Paused,         // App is paused (background or interrupted)
    Resumed,        // App is resuming from pause
    Terminated      // App is being terminated
};

// Callback types for lifecycle events
using LifecycleCallback = std::function<void(AppLifecycleState)>;
using PurchaseCallback = std::function<void(bool, const std::string&)>;
using AchievementCallback = std::function<void(bool, const std::string&)>;
using LeaderboardCallback = std::function<void(bool, const std::vector<std::pair<std::string, int>>&)>;

enum class SensorType {
    Accelerometer = 0,
    Gyroscope = 1,
    Magnetometer = 2
};

struct SensorData {
    float x, y, z;
    double timestamp;
    bool valid;
    
    SensorData() : x(0.0f), y(0.0f), z(0.0f), timestamp(0.0), valid(false) {}
    SensorData(float x_, float y_, float z_, double ts) 
        : x(x_), y(y_), z(z_), timestamp(ts), valid(true) {}
};

// Abstract interface for sensor management
class SensorManager {
public:
    virtual ~SensorManager() = default;
    virtual bool IsAccelerometerAvailable() const = 0;
    virtual bool IsGyroscopeAvailable() const = 0;
    virtual bool IsMagnetometerAvailable() const = 0;
    virtual SensorData GetAccelerometerData() const = 0;
    virtual SensorData GetGyroscopeData() const = 0;
    virtual SensorData GetMagnetometerData() const = 0;
    virtual void EnableSensor(SensorType sensorType, bool enable) = 0;
    virtual bool IsSensorEnabled(SensorType sensorType) const = 0;
    virtual void SetSensorUpdateRate(SensorType sensorType, float hz) = 0;
};

class PlatformManager {
public:
    static bool Initialize();
    static void Shutdown();
    
    // Platform Detection
    static PlatformType GetCurrentPlatform();
    static bool IsMobilePlatform();
    static bool IsConsolePlatform();
    static bool IsVRPlatform();
    static bool IsARPlatform();
    static std::string GetPlatformName();
    static std::string GetPlatformVersion();
    
    // Graphics API Support
    static bool SupportsVulkan();
    static bool SupportsMetal();
    static bool SupportsDirectX12();
    static bool SupportsOpenGL();
    static bool SupportsRayTracing();
    
    // Platform Capabilities
    static bool HasTouchScreen();
    static bool HasKeyboard();
    static bool HasMouse();
    static bool HasGamepad();
    static bool HasHapticFeedback();
    static bool HasSensors();
    static bool HasCamera();
    static bool HasMicrophone();
    static bool HasGPS();
    
    // Mobile-Specific Features
    static void EnableHapticFeedback(HapticPattern pattern, float intensity = 1.0f);
    static void EnableHapticFeedbackCustom(float duration, float intensity);
    static void SetBatteryOptimization(BatteryOptimizationLevel level);
    static BatteryOptimizationLevel GetBatteryOptimizationLevel();
    static float GetBatteryLevel();
    static bool IsCharging();
    static float GetBatteryTemperature();
    static void UpdatePerformanceBasedOnBattery();
    static TouchInputManager* GetTouchInput();
    static SensorManager* GetSensors();
    
    // Console-Specific Features
    static void SetControllerVibration(int controller, float intensity);
    static bool IsControllerConnected(int controller);
    static int GetConnectedControllerCount();
    
    // VR/AR Features
    static bool IsVRHeadsetConnected();
    static bool IsARSupported();
    static void EnableVRMode(bool enable);
    static void EnableARMode(bool enable);
    
    // Mobile Lifecycle Management
    static void RegisterLifecycleCallback(LifecycleCallback callback);
    static void UnregisterLifecycleCallback();
    static AppLifecycleState GetCurrentLifecycleState();
    static void PauseApp();
    static void ResumeApp();
    static bool IsAppPaused();
    
    // In-App Purchases
    static bool IsInAppPurchaseSupported();
    static void InitializeInAppPurchases();
    static void PurchaseProduct(const std::string& productId, PurchaseCallback callback);
    static void RestorePurchases(PurchaseCallback callback);
    static std::vector<std::string> GetPurchasedProducts();
    
    // Social Features
    static bool IsSocialFeaturesSupported();
    static void InitializeSocialFeatures();
    static void UnlockAchievement(const std::string& achievementId, AchievementCallback callback);
    static void SubmitScore(const std::string& leaderboardId, int score, AchievementCallback callback);
    static void ShowLeaderboard(const std::string& leaderboardId);
    static void GetLeaderboardScores(const std::string& leaderboardId, LeaderboardCallback callback);
    
    // Performance and Memory
    static size_t GetTotalMemory();
    static size_t GetAvailableMemory();
    static int GetCPUCoreCount();
    static float GetCPUFrequency();
    static std::string GetGPUName();
    static size_t GetGPUMemory();

private:
    static PlatformType currentPlatform;
    static bool initialized;
    static std::unique_ptr<TouchInputManager> touchManager;
    static std::unique_ptr<SensorManager> sensorManager;
    static BatteryOptimizationLevel batteryOptLevel;
    static float lastBatteryLevel;
    static float performanceScale;
    static AppLifecycleState lifecycleState;
    static LifecycleCallback lifecycleCallback;
    static std::vector<std::string> purchasedProducts;
    static bool inAppPurchasesInitialized;
    static bool socialFeaturesInitialized;
    
    static void DetectPlatform();
    static void InitializePlatformSpecific();
    static void ShutdownPlatformSpecific();
    static float CalculatePerformanceScale(float batteryLevel, bool isCharging);
    static void NotifyLifecycleChange(AppLifecycleState newState);
};

} // namespace platform
} // namespace pywrkgame