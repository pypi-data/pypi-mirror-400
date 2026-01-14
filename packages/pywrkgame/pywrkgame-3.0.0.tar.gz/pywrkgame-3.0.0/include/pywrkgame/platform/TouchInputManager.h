#pragma once

#include <vector>
#include <functional>

namespace pywrkgame {
namespace platform {

enum class GestureType {
    Tap,
    DoubleTap,
    LongPress,
    Swipe,
    Pinch,
    Rotate,
    Pan
};

struct TouchPoint {
    int id;
    float x, y;
    float pressure;
    bool active;
    double timestamp;
};

struct GestureEvent {
    GestureType type;
    float x, y;
    float deltaX, deltaY;
    float scale;
    float rotation;
    int touchCount;
    double timestamp;
};

using GestureCallback = std::function<void(const GestureEvent&)>;

class TouchInputManager {
public:
    virtual ~TouchInputManager() = default;
    
    // Multi-touch support
    virtual bool IsMultiTouchSupported() const = 0;
    virtual int GetMaxTouchPoints() const = 0;
    virtual std::vector<TouchPoint> GetActiveTouches() const = 0;
    
    // Gesture recognition
    virtual void RegisterGestureCallback(GestureType type, GestureCallback callback) = 0;
    virtual void UnregisterGestureCallback(GestureType type) = 0;
    virtual void EnableGesture(GestureType type, bool enable) = 0;
    virtual bool IsGestureEnabled(GestureType type) const = 0;
    
    // Touch sensitivity and configuration
    virtual void SetTouchSensitivity(float sensitivity) = 0;
    virtual float GetTouchSensitivity() const = 0;
    virtual void SetGestureThreshold(GestureType type, float threshold) = 0;
    virtual float GetGestureThreshold(GestureType type) const = 0;
    
    // Touch tracking
    virtual void Update(float deltaTime) = 0;
    virtual void Reset() = 0;
    
protected:
    // Helper methods for gesture recognition
    virtual void ProcessTouchInput(const std::vector<TouchPoint>& touches) = 0;
    virtual void DetectGestures(const std::vector<TouchPoint>& touches) = 0;
    virtual void TriggerGestureCallback(const GestureEvent& event) = 0;
};

} // namespace platform
} // namespace pywrkgame