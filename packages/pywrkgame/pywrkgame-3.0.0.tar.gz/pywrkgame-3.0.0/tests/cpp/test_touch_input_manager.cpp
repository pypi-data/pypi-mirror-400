#include <gtest/gtest.h>
#include "pywrkgame/platform/TouchInputManager.h"
#include "pywrkgame/platform/PlatformManager.h"

using namespace pywrkgame::platform;

class TouchInputManagerTest : public ::testing::Test {
protected:
    void SetUp() override {
        PlatformManager::Initialize();
        touchManager = PlatformManager::GetTouchInput();
    }
    
    void TearDown() override {
        PlatformManager::Shutdown();
    }
    
    TouchInputManager* touchManager = nullptr;
};

TEST_F(TouchInputManagerTest, BasicFunctionality) {
    ASSERT_NE(touchManager, nullptr);
    
    // Test multi-touch support
    bool multiTouchSupported = touchManager->IsMultiTouchSupported();
    if (PlatformManager::IsMobilePlatform()) {
        EXPECT_TRUE(multiTouchSupported);
        EXPECT_GT(touchManager->GetMaxTouchPoints(), 1);
    } else {
        // Desktop platforms may or may not support multi-touch
        EXPECT_GE(touchManager->GetMaxTouchPoints(), 1);
    }
}

TEST_F(TouchInputManagerTest, GestureConfiguration) {
    // Test gesture enabling/disabling
    touchManager->EnableGesture(GestureType::Tap, true);
    EXPECT_TRUE(touchManager->IsGestureEnabled(GestureType::Tap));
    
    touchManager->EnableGesture(GestureType::Tap, false);
    EXPECT_FALSE(touchManager->IsGestureEnabled(GestureType::Tap));
    
    // Test gesture thresholds
    float originalThreshold = touchManager->GetGestureThreshold(GestureType::Swipe);
    touchManager->SetGestureThreshold(GestureType::Swipe, 100.0f);
    EXPECT_EQ(touchManager->GetGestureThreshold(GestureType::Swipe), 100.0f);
    
    // Restore original threshold
    touchManager->SetGestureThreshold(GestureType::Swipe, originalThreshold);
}

TEST_F(TouchInputManagerTest, TouchSensitivity) {
    // Test touch sensitivity
    float originalSensitivity = touchManager->GetTouchSensitivity();
    
    touchManager->SetTouchSensitivity(0.5f);
    EXPECT_EQ(touchManager->GetTouchSensitivity(), 0.5f);
    
    touchManager->SetTouchSensitivity(2.0f);
    EXPECT_EQ(touchManager->GetTouchSensitivity(), 2.0f);
    
    // Test bounds - should clamp to valid range
    touchManager->SetTouchSensitivity(0.05f);
    EXPECT_GE(touchManager->GetTouchSensitivity(), 0.1f);
    
    touchManager->SetTouchSensitivity(5.0f);
    EXPECT_LE(touchManager->GetTouchSensitivity(), 2.0f);
    
    // Restore original sensitivity
    touchManager->SetTouchSensitivity(originalSensitivity);
}

TEST_F(TouchInputManagerTest, GestureCallbacks) {
    bool callbackTriggered = false;
    GestureEvent receivedEvent;
    
    // Register a callback
    touchManager->RegisterGestureCallback(GestureType::Tap, 
        [&callbackTriggered, &receivedEvent](const GestureEvent& event) {
            callbackTriggered = true;
            receivedEvent = event;
        });
    
    // Enable the gesture
    touchManager->EnableGesture(GestureType::Tap, true);
    
    // Test that callback is registered (we can't easily trigger actual touch events in unit tests)
    EXPECT_TRUE(touchManager->IsGestureEnabled(GestureType::Tap));
    
    // Unregister callback
    touchManager->UnregisterGestureCallback(GestureType::Tap);
}

TEST_F(TouchInputManagerTest, TouchTracking) {
    // Test initial state
    std::vector<TouchPoint> touches = touchManager->GetActiveTouches();
    EXPECT_TRUE(touches.empty());
    
    // Test update and reset
    touchManager->Update(0.016f); // 60 FPS
    touchManager->Reset();
    
    touches = touchManager->GetActiveTouches();
    EXPECT_TRUE(touches.empty());
}

TEST_F(TouchInputManagerTest, AllGestureTypes) {
    // Test that all gesture types can be configured
    std::vector<GestureType> gestureTypes = {
        GestureType::Tap,
        GestureType::DoubleTap,
        GestureType::LongPress,
        GestureType::Swipe,
        GestureType::Pinch,
        GestureType::Rotate,
        GestureType::Pan
    };
    
    for (GestureType type : gestureTypes) {
        // Test enabling/disabling
        touchManager->EnableGesture(type, true);
        EXPECT_TRUE(touchManager->IsGestureEnabled(type));
        
        touchManager->EnableGesture(type, false);
        EXPECT_FALSE(touchManager->IsGestureEnabled(type));
        
        // Test threshold setting
        float threshold = touchManager->GetGestureThreshold(type);
        EXPECT_GE(threshold, 0.0f);
        
        touchManager->SetGestureThreshold(type, 50.0f);
        EXPECT_EQ(touchManager->GetGestureThreshold(type), 50.0f);
        
        // Restore original threshold
        touchManager->SetGestureThreshold(type, threshold);
    }
}