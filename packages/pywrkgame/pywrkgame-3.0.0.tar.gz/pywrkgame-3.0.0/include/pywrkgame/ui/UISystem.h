#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <unordered_map>

namespace pywrkgame {
namespace ui {

// Forward declarations
class UIElement;
class UISystem;

// Basic types
struct Vec2 {
    float x, y;
    Vec2(float x = 0.0f, float y = 0.0f) : x(x), y(y) {}
};

struct Rect {
    float x, y, width, height;
    Rect(float x = 0.0f, float y = 0.0f, float w = 0.0f, float h = 0.0f) 
        : x(x), y(y), width(w), height(h) {}
};

struct Color {
    float r, g, b, a;
    Color(float r = 1.0f, float g = 1.0f, float b = 1.0f, float a = 1.0f)
        : r(r), g(g), b(b), a(a) {}
};

// UI Event types
enum class UIEventType {
    None,
    MouseDown,
    MouseUp,
    MouseMove,
    TouchDown,
    TouchUp,
    TouchMove,
    KeyDown,
    KeyUp,
    Focus,
    Blur
};

struct UIEvent {
    UIEventType type;
    Vec2 position;
    int button;
    int keyCode;
    UIElement* target;
    
    UIEvent() : type(UIEventType::None), button(0), keyCode(0), target(nullptr) {}
};

// Layout types
enum class LayoutType {
    Absolute,
    Horizontal,
    Vertical,
    Grid
};

enum class Anchor {
    TopLeft,
    TopCenter,
    TopRight,
    MiddleLeft,
    MiddleCenter,
    MiddleRight,
    BottomLeft,
    BottomCenter,
    BottomRight
};

// Theme system
struct UITheme {
    Color primaryColor;
    Color secondaryColor;
    Color backgroundColor;
    Color textColor;
    Color borderColor;
    float borderWidth;
    float cornerRadius;
    std::string fontFamily;
    float fontSize;
    
    UITheme() 
        : primaryColor(0.2f, 0.6f, 1.0f, 1.0f)
        , secondaryColor(0.8f, 0.8f, 0.8f, 1.0f)
        , backgroundColor(0.95f, 0.95f, 0.95f, 1.0f)
        , textColor(0.1f, 0.1f, 0.1f, 1.0f)
        , borderColor(0.7f, 0.7f, 0.7f, 1.0f)
        , borderWidth(1.0f)
        , cornerRadius(4.0f)
        , fontFamily("Arial")
        , fontSize(14.0f) {}
};

// Base UI Element class
class UIElement {
public:
    UIElement();
    virtual ~UIElement() = default;
    
    // Hierarchy management
    void AddChild(std::shared_ptr<UIElement> child);
    void RemoveChild(std::shared_ptr<UIElement> child);
    UIElement* GetParent() const { return parent_; }
    const std::vector<std::shared_ptr<UIElement>>& GetChildren() const { return children_; }
    
    // Transform and layout
    void SetPosition(const Vec2& pos) { position_ = pos; isDirty_ = true; }
    void SetSize(const Vec2& size) { size_ = size; isDirty_ = true; }
    Vec2 GetPosition() const { return position_; }
    Vec2 GetSize() const { return size_; }
    Rect GetBounds() const { return Rect(position_.x, position_.y, size_.x, size_.y); }
    
    void SetAnchor(Anchor anchor) { anchor_ = anchor; isDirty_ = true; }
    Anchor GetAnchor() const { return anchor_; }
    
    // Visibility and interaction
    void SetVisible(bool visible) { visible_ = visible; }
    bool IsVisible() const { return visible_; }
    void SetEnabled(bool enabled) { enabled_ = enabled; }
    bool IsEnabled() const { return enabled_; }
    
    // Event handling
    using EventCallback = std::function<void(const UIEvent&)>;
    void SetEventCallback(UIEventType type, EventCallback callback);
    virtual bool HandleEvent(const UIEvent& event);
    
    // Layout
    void SetLayoutType(LayoutType type) { layoutType_ = type; isDirty_ = true; }
    LayoutType GetLayoutType() const { return layoutType_; }
    
    // Theme
    void SetTheme(const UITheme& theme) { theme_ = theme; isDirty_ = true; }
    const UITheme& GetTheme() const { return theme_; }
    
    // Update and render
    virtual void Update(float deltaTime);
    virtual void Render();
    void UpdateLayout();
    
    // Utility
    bool ContainsPoint(const Vec2& point) const;
    UIElement* FindElementAt(const Vec2& point);
    
protected:
    Vec2 position_;
    Vec2 size_;
    Anchor anchor_;
    bool visible_;
    bool enabled_;
    bool isDirty_;
    
    LayoutType layoutType_;
    UITheme theme_;
    
    UIElement* parent_;
    std::vector<std::shared_ptr<UIElement>> children_;
    std::unordered_map<UIEventType, EventCallback> eventCallbacks_;
    
    virtual void OnLayout() {}
    virtual void OnRender() {}
};

// Responsive layout system
class ResponsiveLayout {
public:
    struct ScreenSize {
        float width;
        float height;
        
        ScreenSize(float w = 0.0f, float h = 0.0f) : width(w), height(h) {}
    };
    
    enum class Breakpoint {
        Mobile,      // < 768px
        Tablet,      // 768px - 1024px
        Desktop,     // > 1024px
        Custom
    };
    
    ResponsiveLayout();
    
    void SetScreenSize(const ScreenSize& size);
    ScreenSize GetScreenSize() const { return screenSize_; }
    Breakpoint GetCurrentBreakpoint() const;
    
    // Layout rules for different breakpoints
    void AddLayoutRule(Breakpoint breakpoint, std::function<void(UIElement*)> rule);
    void ApplyLayout(UIElement* element);
    
private:
    ScreenSize screenSize_;
    std::unordered_map<Breakpoint, std::vector<std::function<void(UIElement*)>>> layoutRules_;
};

// Mobile UI Components

// Joystick Control
class Joystick : public UIElement {
public:
    Joystick();
    
    void SetDeadZone(float deadZone) { deadZone_ = deadZone; }
    float GetDeadZone() const { return deadZone_; }
    
    void SetMaxDistance(float maxDistance) { maxDistance_ = maxDistance; }
    float GetMaxDistance() const { return maxDistance_; }
    
    Vec2 GetDirection() const { return direction_; }
    float GetMagnitude() const { return magnitude_; }
    
    bool HandleEvent(const UIEvent& event) override;
    void Update(float deltaTime) override;
    
protected:
    void OnRender() override;
    
private:
    Vec2 basePosition_;
    Vec2 stickPosition_;
    Vec2 direction_;
    float magnitude_;
    float deadZone_;
    float maxDistance_;
    bool isActive_;
};

// Drag and Drop Support
class DraggableElement : public UIElement {
public:
    DraggableElement();
    
    void SetDraggable(bool draggable) { draggable_ = draggable; }
    bool IsDraggable() const { return draggable_; }
    
    void SetDragConstraint(const Rect& constraint) { dragConstraint_ = constraint; hasConstraint_ = true; }
    void ClearDragConstraint() { hasConstraint_ = false; }
    
    bool IsDragging() const { return isDragging_; }
    
    using DragStartCallback = std::function<void(DraggableElement*)>;
    using DragCallback = std::function<void(DraggableElement*, const Vec2&)>;
    using DragEndCallback = std::function<void(DraggableElement*)>;
    
    void SetDragStartCallback(DragStartCallback callback) { onDragStart_ = callback; }
    void SetDragCallback(DragCallback callback) { onDrag_ = callback; }
    void SetDragEndCallback(DragEndCallback callback) { onDragEnd_ = callback; }
    
    bool HandleEvent(const UIEvent& event) override;
    
private:
    bool draggable_;
    bool isDragging_;
    Vec2 dragOffset_;
    Rect dragConstraint_;
    bool hasConstraint_;
    
    DragStartCallback onDragStart_;
    DragCallback onDrag_;
    DragEndCallback onDragEnd_;
};

// Drop Zone
class DropZone : public UIElement {
public:
    DropZone();
    
    void SetAcceptDrop(bool accept) { acceptDrop_ = accept; }
    bool AcceptsDrop() const { return acceptDrop_; }
    
    bool IsHovered() const { return isHovered_; }
    
    using DropCallback = std::function<void(DropZone*, DraggableElement*)>;
    void SetDropCallback(DropCallback callback) { onDrop_ = callback; }
    
    bool HandleEvent(const UIEvent& event) override;
    void Update(float deltaTime) override;
    
protected:
    void OnRender() override;
    
private:
    bool acceptDrop_;
    bool isHovered_;
    DropCallback onDrop_;
};

// Progress Bar
class ProgressBar : public UIElement {
public:
    enum class Style {
        Horizontal,
        Vertical,
        Circular
    };
    
    ProgressBar();
    
    void SetProgress(float progress);
    float GetProgress() const { return progress_; }
    
    void SetStyle(Style style) { style_ = style; }
    Style GetStyle() const { return style_; }
    
    void SetAnimated(bool animated) { animated_ = animated; }
    bool IsAnimated() const { return animated_; }
    
    void SetAnimationSpeed(float speed) { animationSpeed_ = speed; }
    float GetAnimationSpeed() const { return animationSpeed_; }
    
    void SetFillColor(const Color& color) { fillColor_ = color; }
    Color GetFillColor() const { return fillColor_; }
    
    void SetBackgroundColor(const Color& color) { backgroundColor_ = color; }
    Color GetBackgroundColor() const { return backgroundColor_; }
    
    void Update(float deltaTime) override;
    
protected:
    void OnRender() override;
    
private:
    float progress_;
    float displayProgress_;
    Style style_;
    bool animated_;
    float animationSpeed_;
    Color fillColor_;
    Color backgroundColor_;
};

// Advanced UI Features

// Dialog System
struct DialogOption {
    std::string text;
    int nextNodeId;
    std::function<bool()> condition; // Optional condition to show this option
    
    DialogOption() : nextNodeId(-1) {}
    DialogOption(const std::string& t, int next) : text(t), nextNodeId(next) {}
};

struct DialogNode {
    int id;
    std::string speaker;
    std::string text;
    std::vector<DialogOption> options;
    
    DialogNode() : id(-1) {}
    DialogNode(int nodeId, const std::string& spk, const std::string& txt) 
        : id(nodeId), speaker(spk), text(txt) {}
};

class DialogSystem : public UIElement {
public:
    DialogSystem();
    
    void AddNode(const DialogNode& node);
    void SetCurrentNode(int nodeId);
    int GetCurrentNode() const { return currentNodeId_; }
    
    const DialogNode* GetNode(int nodeId) const;
    const DialogNode* GetCurrentNodeData() const;
    
    void SelectOption(int optionIndex);
    
    using DialogEndCallback = std::function<void()>;
    void SetDialogEndCallback(DialogEndCallback callback) { onDialogEnd_ = callback; }
    
    bool IsActive() const { return isActive_; }
    void StartDialog(int startNodeId);
    void EndDialog();
    
    void Update(float deltaTime) override;
    
protected:
    void OnRender() override;
    
private:
    std::unordered_map<int, DialogNode> nodes_;
    int currentNodeId_;
    bool isActive_;
    DialogEndCallback onDialogEnd_;
};

// Minimap Component
class Minimap : public UIElement {
public:
    struct MapObject {
        Vec2 worldPosition;
        Color color;
        float size;
        bool visible;
        
        MapObject() : size(5.0f), visible(true) {}
        MapObject(const Vec2& pos, const Color& col) 
            : worldPosition(pos), color(col), size(5.0f), visible(true) {}
    };
    
    Minimap();
    
    void SetWorldBounds(const Rect& bounds) { worldBounds_ = bounds; }
    Rect GetWorldBounds() const { return worldBounds_; }
    
    void SetCameraPosition(const Vec2& pos) { cameraPosition_ = pos; }
    Vec2 GetCameraPosition() const { return cameraPosition_; }
    
    void SetZoom(float zoom) { zoom_ = zoom; }
    float GetZoom() const { return zoom_; }
    
    int AddMapObject(const MapObject& obj);
    void RemoveMapObject(int id);
    void UpdateMapObject(int id, const Vec2& worldPosition);
    void SetMapObjectVisible(int id, bool visible);
    
    void ClearMapObjects();
    int GetMapObjectCount() const { return static_cast<int>(mapObjects_.size()); }
    
    Vec2 WorldToMinimapPosition(const Vec2& worldPos) const;
    
    void Update(float deltaTime) override;
    
protected:
    void OnRender() override;
    
private:
    Rect worldBounds_;
    Vec2 cameraPosition_;
    float zoom_;
    std::unordered_map<int, MapObject> mapObjects_;
    int nextObjectId_;
};

// Accessibility Features
struct AccessibilitySettings {
    bool screenReaderEnabled;
    bool highContrastMode;
    bool colorBlindMode;
    enum class ColorBlindType {
        None,
        Protanopia,    // Red-blind
        Deuteranopia,  // Green-blind
        Tritanopia     // Blue-blind
    } colorBlindType;
    float textScale;
    bool reduceMotion;
    
    AccessibilitySettings() 
        : screenReaderEnabled(false)
        , highContrastMode(false)
        , colorBlindMode(false)
        , colorBlindType(ColorBlindType::None)
        , textScale(1.0f)
        , reduceMotion(false) {}
};

class AccessibilityManager {
public:
    static AccessibilityManager& GetInstance();
    
    void SetSettings(const AccessibilitySettings& settings) { settings_ = settings; }
    const AccessibilitySettings& GetSettings() const { return settings_; }
    
    void EnableScreenReader(bool enable) { settings_.screenReaderEnabled = enable; }
    bool IsScreenReaderEnabled() const { return settings_.screenReaderEnabled; }
    
    void EnableHighContrast(bool enable) { settings_.highContrastMode = enable; }
    bool IsHighContrastEnabled() const { return settings_.highContrastMode; }
    
    void SetColorBlindMode(AccessibilitySettings::ColorBlindType type);
    AccessibilitySettings::ColorBlindType GetColorBlindMode() const { return settings_.colorBlindType; }
    
    void SetTextScale(float scale) { settings_.textScale = scale; }
    float GetTextScale() const { return settings_.textScale; }
    
    void EnableReduceMotion(bool enable) { settings_.reduceMotion = enable; }
    bool IsReduceMotionEnabled() const { return settings_.reduceMotion; }
    
    // Apply accessibility adjustments to colors
    Color AdjustColor(const Color& original) const;
    
private:
    AccessibilityManager() = default;
    AccessibilitySettings settings_;
};

// Main UI System
class UISystem {
public:
    UISystem();
    ~UISystem();
    
    bool Initialize();
    void Shutdown();
    
    // Root element management
    void SetRootElement(std::shared_ptr<UIElement> root);
    std::shared_ptr<UIElement> GetRootElement() const { return rootElement_; }
    
    // Theme management
    void SetGlobalTheme(const UITheme& theme);
    const UITheme& GetGlobalTheme() const { return globalTheme_; }
    
    // Responsive layout
    void SetScreenSize(float width, float height);
    ResponsiveLayout& GetResponsiveLayout() { return responsiveLayout_; }
    
    // Event routing
    void RouteEvent(const UIEvent& event);
    
    // Drag and drop management
    void RegisterDraggable(DraggableElement* element);
    void UnregisterDraggable(DraggableElement* element);
    void RegisterDropZone(DropZone* zone);
    void UnregisterDropZone(DropZone* zone);
    DraggableElement* GetCurrentDraggable() const { return currentDraggable_; }
    
    // Update and render
    void Update(float deltaTime);
    void Render();
    
private:
    std::shared_ptr<UIElement> rootElement_;
    UITheme globalTheme_;
    ResponsiveLayout responsiveLayout_;
    bool initialized_;
    
    UIElement* focusedElement_;
    UIElement* hoveredElement_;
    
    // Drag and drop state
    std::vector<DraggableElement*> draggables_;
    std::vector<DropZone*> dropZones_;
    DraggableElement* currentDraggable_;
};

} // namespace ui
} // namespace pywrkgame