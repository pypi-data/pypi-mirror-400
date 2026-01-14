#include "pywrkgame/platform/TouchInputManager.h"
#include "pywrkgame/platform/PlatformManager.h"
#include <algorithm>
#include <cmath>
#include <unordered_map>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace pywrkgame {
namespace platform {

class DefaultTouchInputManager : public TouchInputManager {
private:
    std::unordered_map<GestureType, GestureCallback> gestureCallbacks;
    std::unordered_map<GestureType, bool> enabledGestures;
    std::unordered_map<GestureType, float> gestureThresholds;
    std::vector<TouchPoint> currentTouches;
    std::vector<TouchPoint> previousTouches;
    float touchSensitivity = 1.0f;
    
    // Gesture detection state
    struct GestureState {
        bool inProgress = false;
        double startTime = 0.0;
        float startX = 0.0f, startY = 0.0f;
        float lastScale = 1.0f;
        float lastRotation = 0.0f;
        int tapCount = 0;
        double lastTapTime = 0.0;
    } gestureState;

public:
    DefaultTouchInputManager() {
        // Initialize default gesture thresholds
        gestureThresholds[GestureType::Tap] = 10.0f;
        gestureThresholds[GestureType::DoubleTap] = 15.0f;
        gestureThresholds[GestureType::LongPress] = 20.0f;
        gestureThresholds[GestureType::Swipe] = 50.0f;
        gestureThresholds[GestureType::Pinch] = 0.1f;
        gestureThresholds[GestureType::Rotate] = 5.0f;
        gestureThresholds[GestureType::Pan] = 5.0f;
        
        // Enable all gestures by default
        for (auto& pair : gestureThresholds) {
            enabledGestures[pair.first] = true;
        }
    }
    
    bool IsMultiTouchSupported() const override {
        return PlatformManager::IsMobilePlatform();
    }
    
    int GetMaxTouchPoints() const override {
        if (PlatformManager::IsMobilePlatform()) {
            return 10; // Most mobile devices support up to 10 touch points
        }
        return 1; // Desktop platforms typically support single touch
    }
    
    std::vector<TouchPoint> GetActiveTouches() const override {
        return currentTouches;
    }
    
    void RegisterGestureCallback(GestureType type, GestureCallback callback) override {
        gestureCallbacks[type] = callback;
    }
    
    void UnregisterGestureCallback(GestureType type) override {
        gestureCallbacks.erase(type);
    }
    
    void EnableGesture(GestureType type, bool enable) override {
        enabledGestures[type] = enable;
    }
    
    bool IsGestureEnabled(GestureType type) const override {
        auto it = enabledGestures.find(type);
        return it != enabledGestures.end() ? it->second : false;
    }
    
    void SetTouchSensitivity(float sensitivity) override {
        touchSensitivity = std::max(0.1f, std::min(2.0f, sensitivity));
    }
    
    float GetTouchSensitivity() const override {
        return touchSensitivity;
    }
    
    void SetGestureThreshold(GestureType type, float threshold) override {
        gestureThresholds[type] = threshold;
    }
    
    float GetGestureThreshold(GestureType type) const override {
        auto it = gestureThresholds.find(type);
        return it != gestureThresholds.end() ? it->second : 0.0f;
    }
    
    void Update(float deltaTime) override {
        // In a real implementation, this would poll the platform's touch input system
        // For now, we'll simulate basic touch input processing
        ProcessTouchInput(currentTouches);
        DetectGestures(currentTouches);
        
        // Store current touches as previous for next frame
        previousTouches = currentTouches;
    }
    
    void Reset() override {
        currentTouches.clear();
        previousTouches.clear();
        gestureState = GestureState{};
    }
    
protected:
    void ProcessTouchInput(const std::vector<TouchPoint>& touches) override {
        // Apply touch sensitivity
        for (auto& touch : currentTouches) {
            // Sensitivity affects how responsive touch input is
            // This is a simplified implementation
        }
    }
    
    void DetectGestures(const std::vector<TouchPoint>& touches) override {
        if (touches.empty()) {
            gestureState.inProgress = false;
            return;
        }
        
        // Single touch gestures
        if (touches.size() == 1) {
            DetectSingleTouchGestures(touches[0]);
        }
        // Multi-touch gestures
        else if (touches.size() >= 2) {
            DetectMultiTouchGestures(touches);
        }
    }
    
    void DetectSingleTouchGestures(const TouchPoint& touch) {
        if (!gestureState.inProgress) {
            gestureState.inProgress = true;
            gestureState.startTime = touch.timestamp;
            gestureState.startX = touch.x;
            gestureState.startY = touch.y;
            return;
        }
        
        float deltaX = touch.x - gestureState.startX;
        float deltaY = touch.y - gestureState.startY;
        float distance = std::sqrt(deltaX * deltaX + deltaY * deltaY);
        double duration = touch.timestamp - gestureState.startTime;
        
        // Detect tap
        if (!touch.active && distance < GetGestureThreshold(GestureType::Tap) && 
            duration < 0.3 && IsGestureEnabled(GestureType::Tap)) {
            
            // Check for double tap
            if (duration - gestureState.lastTapTime < 0.5 && IsGestureEnabled(GestureType::DoubleTap)) {
                TriggerGestureCallback({GestureType::DoubleTap, touch.x, touch.y, 0, 0, 1.0f, 0.0f, 1, touch.timestamp});
                gestureState.tapCount = 0;
            } else {
                TriggerGestureCallback({GestureType::Tap, touch.x, touch.y, 0, 0, 1.0f, 0.0f, 1, touch.timestamp});
                gestureState.tapCount++;
            }
            gestureState.lastTapTime = touch.timestamp;
        }
        
        // Detect long press
        if (touch.active && distance < GetGestureThreshold(GestureType::LongPress) && 
            duration > 1.0 && IsGestureEnabled(GestureType::LongPress)) {
            TriggerGestureCallback({GestureType::LongPress, touch.x, touch.y, 0, 0, 1.0f, 0.0f, 1, touch.timestamp});
        }
        
        // Detect swipe
        if (!touch.active && distance > GetGestureThreshold(GestureType::Swipe) && 
            duration < 0.5 && IsGestureEnabled(GestureType::Swipe)) {
            TriggerGestureCallback({GestureType::Swipe, touch.x, touch.y, deltaX, deltaY, 1.0f, 0.0f, 1, touch.timestamp});
        }
        
        // Detect pan
        if (touch.active && distance > GetGestureThreshold(GestureType::Pan) && 
            IsGestureEnabled(GestureType::Pan)) {
            TriggerGestureCallback({GestureType::Pan, touch.x, touch.y, deltaX, deltaY, 1.0f, 0.0f, 1, touch.timestamp});
        }
    }
    
    void DetectMultiTouchGestures(const std::vector<TouchPoint>& touches) {
        if (touches.size() < 2) return;
        
        const TouchPoint& touch1 = touches[0];
        const TouchPoint& touch2 = touches[1];
        
        // Calculate current distance and angle
        float dx = touch2.x - touch1.x;
        float dy = touch2.y - touch1.y;
        float currentDistance = std::sqrt(dx * dx + dy * dy);
        float currentAngle = std::atan2(dy, dx) * 180.0f / M_PI;
        
        if (!gestureState.inProgress) {
            gestureState.inProgress = true;
            gestureState.lastScale = currentDistance;
            gestureState.lastRotation = currentAngle;
            return;
        }
        
        // Detect pinch
        if (IsGestureEnabled(GestureType::Pinch)) {
            float scale = currentDistance / gestureState.lastScale;
            if (std::abs(scale - 1.0f) > GetGestureThreshold(GestureType::Pinch)) {
                float centerX = (touch1.x + touch2.x) * 0.5f;
                float centerY = (touch1.y + touch2.y) * 0.5f;
                TriggerGestureCallback({GestureType::Pinch, centerX, centerY, 0, 0, scale, 0.0f, 2, touch1.timestamp});
            }
        }
        
        // Detect rotation
        if (IsGestureEnabled(GestureType::Rotate)) {
            float rotation = currentAngle - gestureState.lastRotation;
            if (std::abs(rotation) > GetGestureThreshold(GestureType::Rotate)) {
                float centerX = (touch1.x + touch2.x) * 0.5f;
                float centerY = (touch1.y + touch2.y) * 0.5f;
                TriggerGestureCallback({GestureType::Rotate, centerX, centerY, 0, 0, 1.0f, rotation, 2, touch1.timestamp});
            }
        }
    }
    
    void TriggerGestureCallback(const GestureEvent& event) override {
        auto it = gestureCallbacks.find(event.type);
        if (it != gestureCallbacks.end() && it->second) {
            it->second(event);
        }
    }
};

// Factory function to create platform-specific TouchInputManager
std::unique_ptr<TouchInputManager> CreateTouchInputManager() {
    return std::make_unique<DefaultTouchInputManager>();
}

} // namespace platform
} // namespace pywrkgame