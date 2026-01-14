#include "pywrkgame/ui/UISystem.h"
#include <algorithm>
#include <cmath>

namespace pywrkgame {
namespace ui {

// UIElement implementation
UIElement::UIElement()
    : position_(0.0f, 0.0f)
    , size_(100.0f, 100.0f)
    , anchor_(Anchor::TopLeft)
    , visible_(true)
    , enabled_(true)
    , isDirty_(true)
    , layoutType_(LayoutType::Absolute)
    , parent_(nullptr) {
}

void UIElement::AddChild(std::shared_ptr<UIElement> child) {
    if (child) {
        child->parent_ = this;
        children_.push_back(child);
        isDirty_ = true;
    }
}

void UIElement::RemoveChild(std::shared_ptr<UIElement> child) {
    auto it = std::find(children_.begin(), children_.end(), child);
    if (it != children_.end()) {
        (*it)->parent_ = nullptr;
        children_.erase(it);
        isDirty_ = true;
    }
}

void UIElement::SetEventCallback(UIEventType type, EventCallback callback) {
    eventCallbacks_[type] = callback;
}

bool UIElement::HandleEvent(const UIEvent& event) {
    if (!visible_ || !enabled_) {
        return false;
    }
    
    // Check if event is within bounds
    if (event.type == UIEventType::MouseDown || 
        event.type == UIEventType::MouseUp || 
        event.type == UIEventType::MouseMove ||
        event.type == UIEventType::TouchDown ||
        event.type == UIEventType::TouchUp ||
        event.type == UIEventType::TouchMove) {
        if (!ContainsPoint(event.position)) {
            return false;
        }
    }
    
    // Call registered callback
    auto it = eventCallbacks_.find(event.type);
    if (it != eventCallbacks_.end()) {
        it->second(event);
        return true;
    }
    
    return false;
}

void UIElement::Update(float deltaTime) {
    if (!visible_) {
        return;
    }
    
    // Update layout if dirty
    if (isDirty_) {
        UpdateLayout();
        isDirty_ = false;
    }
    
    // Update children
    for (auto& child : children_) {
        child->Update(deltaTime);
    }
}

void UIElement::Render() {
    if (!visible_) {
        return;
    }
    
    // Render this element
    OnRender();
    
    // Render children
    for (auto& child : children_) {
        child->Render();
    }
}

void UIElement::UpdateLayout() {
    // Apply anchor positioning
    if (parent_) {
        Vec2 parentSize = parent_->GetSize();
        Vec2 anchoredPos = position_;
        
        switch (anchor_) {
            case Anchor::TopLeft:
                // No adjustment needed
                break;
            case Anchor::TopCenter:
                anchoredPos.x = (parentSize.x - size_.x) * 0.5f + position_.x;
                break;
            case Anchor::TopRight:
                anchoredPos.x = parentSize.x - size_.x + position_.x;
                break;
            case Anchor::MiddleLeft:
                anchoredPos.y = (parentSize.y - size_.y) * 0.5f + position_.y;
                break;
            case Anchor::MiddleCenter:
                anchoredPos.x = (parentSize.x - size_.x) * 0.5f + position_.x;
                anchoredPos.y = (parentSize.y - size_.y) * 0.5f + position_.y;
                break;
            case Anchor::MiddleRight:
                anchoredPos.x = parentSize.x - size_.x + position_.x;
                anchoredPos.y = (parentSize.y - size_.y) * 0.5f + position_.y;
                break;
            case Anchor::BottomLeft:
                anchoredPos.y = parentSize.y - size_.y + position_.y;
                break;
            case Anchor::BottomCenter:
                anchoredPos.x = (parentSize.x - size_.x) * 0.5f + position_.x;
                anchoredPos.y = parentSize.y - size_.y + position_.y;
                break;
            case Anchor::BottomRight:
                anchoredPos.x = parentSize.x - size_.x + position_.x;
                anchoredPos.y = parentSize.y - size_.y + position_.y;
                break;
        }
        
        position_ = anchoredPos;
    }
    
    // Apply layout to children
    if (layoutType_ != LayoutType::Absolute && !children_.empty()) {
        float currentX = 0.0f;
        float currentY = 0.0f;
        
        switch (layoutType_) {
            case LayoutType::Horizontal:
                for (auto& child : children_) {
                    child->SetPosition(Vec2(currentX, currentY));
                    currentX += child->GetSize().x;
                }
                break;
                
            case LayoutType::Vertical:
                for (auto& child : children_) {
                    child->SetPosition(Vec2(currentX, currentY));
                    currentY += child->GetSize().y;
                }
                break;
                
            case LayoutType::Grid:
                // Simple grid layout - can be enhanced
                {
                    int columns = static_cast<int>(std::sqrt(children_.size()));
                    if (columns == 0) columns = 1;
                    float cellWidth = size_.x / columns;
                    float cellHeight = size_.y / ((children_.size() + columns - 1) / columns);
                    
                    int col = 0;
                    int row = 0;
                    for (auto& child : children_) {
                        child->SetPosition(Vec2(col * cellWidth, row * cellHeight));
                        col++;
                        if (col >= columns) {
                            col = 0;
                            row++;
                        }
                    }
                }
                break;
                
            case LayoutType::Absolute:
            default:
                // Children use their own positions
                break;
        }
    }
    
    OnLayout();
}

bool UIElement::ContainsPoint(const Vec2& point) const {
    return point.x >= position_.x && point.x <= position_.x + size_.x &&
           point.y >= position_.y && point.y <= position_.y + size_.y;
}

UIElement* UIElement::FindElementAt(const Vec2& point) {
    if (!visible_ || !ContainsPoint(point)) {
        return nullptr;
    }
    
    // Check children first (reverse order for proper z-ordering)
    for (auto it = children_.rbegin(); it != children_.rend(); ++it) {
        UIElement* found = (*it)->FindElementAt(point);
        if (found) {
            return found;
        }
    }
    
    // Return this element if no child was found
    return this;
}

// ResponsiveLayout implementation
ResponsiveLayout::ResponsiveLayout()
    : screenSize_(1920.0f, 1080.0f) {
}

void ResponsiveLayout::SetScreenSize(const ScreenSize& size) {
    screenSize_ = size;
}

ResponsiveLayout::Breakpoint ResponsiveLayout::GetCurrentBreakpoint() const {
    if (screenSize_.width < 768.0f) {
        return Breakpoint::Mobile;
    } else if (screenSize_.width < 1024.0f) {
        return Breakpoint::Tablet;
    } else {
        return Breakpoint::Desktop;
    }
}

void ResponsiveLayout::AddLayoutRule(Breakpoint breakpoint, std::function<void(UIElement*)> rule) {
    layoutRules_[breakpoint].push_back(rule);
}

void ResponsiveLayout::ApplyLayout(UIElement* element) {
    if (!element) {
        return;
    }
    
    Breakpoint currentBreakpoint = GetCurrentBreakpoint();
    auto it = layoutRules_.find(currentBreakpoint);
    if (it != layoutRules_.end()) {
        for (auto& rule : it->second) {
            rule(element);
        }
    }
}

// UISystem implementation
UISystem::UISystem()
    : initialized_(false)
    , focusedElement_(nullptr)
    , hoveredElement_(nullptr)
    , currentDraggable_(nullptr) {
}

UISystem::~UISystem() {
    Shutdown();
}

bool UISystem::Initialize() {
    if (initialized_) {
        return true;
    }
    
    // Create root element
    rootElement_ = std::make_shared<UIElement>();
    rootElement_->SetSize(Vec2(1920.0f, 1080.0f)); // Default screen size
    
    initialized_ = true;
    return true;
}

void UISystem::Shutdown() {
    if (!initialized_) {
        return;
    }
    
    rootElement_.reset();
    focusedElement_ = nullptr;
    hoveredElement_ = nullptr;
    
    initialized_ = false;
}

void UISystem::SetRootElement(std::shared_ptr<UIElement> root) {
    rootElement_ = root;
    if (rootElement_) {
        rootElement_->SetTheme(globalTheme_);
    }
}

void UISystem::SetGlobalTheme(const UITheme& theme) {
    globalTheme_ = theme;
    
    // Apply theme to all elements recursively
    if (rootElement_) {
        std::function<void(UIElement*)> applyTheme = [&](UIElement* element) {
            element->SetTheme(theme);
            for (auto& child : element->GetChildren()) {
                applyTheme(child.get());
            }
        };
        applyTheme(rootElement_.get());
    }
}

void UISystem::SetScreenSize(float width, float height) {
    responsiveLayout_.SetScreenSize(ResponsiveLayout::ScreenSize(width, height));
    
    if (rootElement_) {
        rootElement_->SetSize(Vec2(width, height));
        responsiveLayout_.ApplyLayout(rootElement_.get());
    }
}

void UISystem::RouteEvent(const UIEvent& event) {
    if (!rootElement_) {
        return;
    }
    
    // Find target element
    UIElement* target = nullptr;
    if (event.type == UIEventType::MouseDown || 
        event.type == UIEventType::MouseUp || 
        event.type == UIEventType::MouseMove ||
        event.type == UIEventType::TouchDown ||
        event.type == UIEventType::TouchUp ||
        event.type == UIEventType::TouchMove) {
        target = rootElement_->FindElementAt(event.position);
    } else {
        target = focusedElement_;
    }
    
    // Handle drag and drop
    if (event.type == UIEventType::MouseDown || event.type == UIEventType::TouchDown) {
        // Check if we're starting to drag something
        for (auto* draggable : draggables_) {
            if (draggable->ContainsPoint(event.position) && draggable->IsDraggable()) {
                currentDraggable_ = draggable;
                break;
            }
        }
    } else if (event.type == UIEventType::MouseUp || event.type == UIEventType::TouchUp) {
        // Check if we're dropping on a drop zone
        if (currentDraggable_ && currentDraggable_->IsDragging()) {
            for (auto* dropZone : dropZones_) {
                if (dropZone->ContainsPoint(event.position) && dropZone->AcceptsDrop()) {
                    // Trigger drop callback
                    auto callback = dropZone->GetChildren(); // This is a placeholder
                    // In a real implementation, we'd call the drop callback here
                    break;
                }
            }
        }
        currentDraggable_ = nullptr;
    } else if (event.type == UIEventType::MouseMove || event.type == UIEventType::TouchMove) {
        // Update drop zone hover states
        for (auto* dropZone : dropZones_) {
            bool wasHovered = dropZone->IsHovered();
            bool isNowHovered = dropZone->ContainsPoint(event.position) && currentDraggable_ != nullptr;
            
            if (isNowHovered != wasHovered) {
                // Update hover state (would need to add setter)
                // dropZone->SetHovered(isNowHovered);
            }
        }
    }
    
    // Handle hover state
    if (event.type == UIEventType::MouseMove || event.type == UIEventType::TouchMove) {
        if (hoveredElement_ != target) {
            // Send blur event to previous hovered element
            if (hoveredElement_) {
                UIEvent blurEvent;
                blurEvent.type = UIEventType::Blur;
                blurEvent.target = hoveredElement_;
                hoveredElement_->HandleEvent(blurEvent);
            }
            
            hoveredElement_ = target;
            
            // Send focus event to new hovered element
            if (hoveredElement_) {
                UIEvent focusEvent;
                focusEvent.type = UIEventType::Focus;
                focusEvent.target = hoveredElement_;
                hoveredElement_->HandleEvent(focusEvent);
            }
        }
    }
    
    // Route event to target
    if (target) {
        UIEvent routedEvent = event;
        routedEvent.target = target;
        target->HandleEvent(routedEvent);
        
        // Update focused element on mouse/touch down
        if (event.type == UIEventType::MouseDown || event.type == UIEventType::TouchDown) {
            if (focusedElement_ != target) {
                // Send blur to previous focused element
                if (focusedElement_) {
                    UIEvent blurEvent;
                    blurEvent.type = UIEventType::Blur;
                    blurEvent.target = focusedElement_;
                    focusedElement_->HandleEvent(blurEvent);
                }
                
                focusedElement_ = target;
                
                // Send focus to new focused element
                UIEvent focusEvent;
                focusEvent.type = UIEventType::Focus;
                focusEvent.target = focusedElement_;
                focusedElement_->HandleEvent(focusEvent);
            }
        }
    }
}

void UISystem::Update(float deltaTime) {
    if (!initialized_ || !rootElement_) {
        return;
    }
    
    rootElement_->Update(deltaTime);
}

void UISystem::Render() {
    if (!initialized_ || !rootElement_) {
        return;
    }
    
    rootElement_->Render();
}

// Joystick implementation
Joystick::Joystick()
    : magnitude_(0.0f)
    , deadZone_(0.1f)
    , maxDistance_(100.0f)
    , isActive_(false) {
    SetSize(Vec2(200.0f, 200.0f));
}

bool Joystick::HandleEvent(const UIEvent& event) {
    if (!visible_ || !enabled_) {
        return false;
    }
    
    if (event.type == UIEventType::TouchDown || event.type == UIEventType::MouseDown) {
        if (ContainsPoint(event.position)) {
            isActive_ = true;
            basePosition_ = Vec2(position_.x + size_.x * 0.5f, position_.y + size_.y * 0.5f);
            stickPosition_ = event.position;
            return true;
        }
    } else if (event.type == UIEventType::TouchMove || event.type == UIEventType::MouseMove) {
        if (isActive_) {
            stickPosition_ = event.position;
            
            // Calculate direction and magnitude
            Vec2 delta(stickPosition_.x - basePosition_.x, stickPosition_.y - basePosition_.y);
            float distance = std::sqrt(delta.x * delta.x + delta.y * delta.y);
            
            if (distance > maxDistance_) {
                delta.x = (delta.x / distance) * maxDistance_;
                delta.y = (delta.y / distance) * maxDistance_;
                stickPosition_.x = basePosition_.x + delta.x;
                stickPosition_.y = basePosition_.y + delta.y;
                distance = maxDistance_;
            }
            
            magnitude_ = distance / maxDistance_;
            
            if (magnitude_ < deadZone_) {
                direction_ = Vec2(0.0f, 0.0f);
                magnitude_ = 0.0f;
            } else {
                direction_.x = delta.x / distance;
                direction_.y = delta.y / distance;
            }
            
            return true;
        }
    } else if (event.type == UIEventType::TouchUp || event.type == UIEventType::MouseUp) {
        if (isActive_) {
            isActive_ = false;
            direction_ = Vec2(0.0f, 0.0f);
            magnitude_ = 0.0f;
            stickPosition_ = basePosition_;
            return true;
        }
    }
    
    return UIElement::HandleEvent(event);
}

void Joystick::Update(float deltaTime) {
    UIElement::Update(deltaTime);
}

void Joystick::OnRender() {
    // Rendering would be implemented with actual graphics API
    // This is a placeholder for the rendering logic
}

// DraggableElement implementation
DraggableElement::DraggableElement()
    : draggable_(true)
    , isDragging_(false)
    , hasConstraint_(false) {
}

bool DraggableElement::HandleEvent(const UIEvent& event) {
    if (!visible_ || !enabled_ || !draggable_) {
        return UIElement::HandleEvent(event);
    }
    
    if (event.type == UIEventType::TouchDown || event.type == UIEventType::MouseDown) {
        if (ContainsPoint(event.position)) {
            isDragging_ = true;
            dragOffset_.x = event.position.x - position_.x;
            dragOffset_.y = event.position.y - position_.y;
            
            if (onDragStart_) {
                onDragStart_(this);
            }
            
            return true;
        }
    } else if (event.type == UIEventType::TouchMove || event.type == UIEventType::MouseMove) {
        if (isDragging_) {
            Vec2 newPos(event.position.x - dragOffset_.x, event.position.y - dragOffset_.y);
            
            // Apply constraints if set
            if (hasConstraint_) {
                newPos.x = std::max(dragConstraint_.x, std::min(newPos.x, dragConstraint_.x + dragConstraint_.width - size_.x));
                newPos.y = std::max(dragConstraint_.y, std::min(newPos.y, dragConstraint_.y + dragConstraint_.height - size_.y));
            }
            
            SetPosition(newPos);
            
            if (onDrag_) {
                onDrag_(this, newPos);
            }
            
            return true;
        }
    } else if (event.type == UIEventType::TouchUp || event.type == UIEventType::MouseUp) {
        if (isDragging_) {
            isDragging_ = false;
            
            if (onDragEnd_) {
                onDragEnd_(this);
            }
            
            return true;
        }
    }
    
    return UIElement::HandleEvent(event);
}

// DropZone implementation
DropZone::DropZone()
    : acceptDrop_(true)
    , isHovered_(false) {
}

bool DropZone::HandleEvent(const UIEvent& event) {
    if (!visible_ || !enabled_ || !acceptDrop_) {
        return UIElement::HandleEvent(event);
    }
    
    // Drop zones don't handle events directly, they're checked by the UI system
    return UIElement::HandleEvent(event);
}

void DropZone::Update(float deltaTime) {
    UIElement::Update(deltaTime);
}

void DropZone::OnRender() {
    // Rendering would be implemented with actual graphics API
    // Highlight the drop zone when hovered
}

// ProgressBar implementation
ProgressBar::ProgressBar()
    : progress_(0.0f)
    , displayProgress_(0.0f)
    , style_(Style::Horizontal)
    , animated_(true)
    , animationSpeed_(2.0f)
    , fillColor_(0.2f, 0.6f, 1.0f, 1.0f)
    , backgroundColor_(0.8f, 0.8f, 0.8f, 1.0f) {
    SetSize(Vec2(200.0f, 20.0f));
}

void ProgressBar::SetProgress(float progress) {
    progress_ = std::max(0.0f, std::min(1.0f, progress));
}

void ProgressBar::Update(float deltaTime) {
    UIElement::Update(deltaTime);
    
    if (animated_) {
        // Smoothly animate progress
        float diff = progress_ - displayProgress_;
        if (std::abs(diff) > 0.001f) {
            displayProgress_ += diff * animationSpeed_ * deltaTime;
            displayProgress_ = std::max(0.0f, std::min(1.0f, displayProgress_));
        } else {
            displayProgress_ = progress_;
        }
    } else {
        displayProgress_ = progress_;
    }
}

void ProgressBar::OnRender() {
    // Rendering would be implemented with actual graphics API
    // Draw background and fill based on displayProgress_
}

// UISystem drag and drop management
void UISystem::RegisterDraggable(DraggableElement* element) {
    if (element && std::find(draggables_.begin(), draggables_.end(), element) == draggables_.end()) {
        draggables_.push_back(element);
    }
}

void UISystem::UnregisterDraggable(DraggableElement* element) {
    auto it = std::find(draggables_.begin(), draggables_.end(), element);
    if (it != draggables_.end()) {
        draggables_.erase(it);
        if (currentDraggable_ == element) {
            currentDraggable_ = nullptr;
        }
    }
}

void UISystem::RegisterDropZone(DropZone* zone) {
    if (zone && std::find(dropZones_.begin(), dropZones_.end(), zone) == dropZones_.end()) {
        dropZones_.push_back(zone);
    }
}

void UISystem::UnregisterDropZone(DropZone* zone) {
    auto it = std::find(dropZones_.begin(), dropZones_.end(), zone);
    if (it != dropZones_.end()) {
        dropZones_.erase(it);
    }
}

// DialogSystem implementation
DialogSystem::DialogSystem()
    : currentNodeId_(-1)
    , isActive_(false) {
    SetSize(Vec2(400.0f, 300.0f));
}

void DialogSystem::AddNode(const DialogNode& node) {
    nodes_[node.id] = node;
}

void DialogSystem::SetCurrentNode(int nodeId) {
    if (nodes_.find(nodeId) != nodes_.end()) {
        currentNodeId_ = nodeId;
    }
}

const DialogNode* DialogSystem::GetNode(int nodeId) const {
    auto it = nodes_.find(nodeId);
    if (it != nodes_.end()) {
        return &it->second;
    }
    return nullptr;
}

const DialogNode* DialogSystem::GetCurrentNodeData() const {
    return GetNode(currentNodeId_);
}

void DialogSystem::SelectOption(int optionIndex) {
    const DialogNode* currentNode = GetCurrentNodeData();
    if (!currentNode || optionIndex < 0 || optionIndex >= static_cast<int>(currentNode->options.size())) {
        return;
    }
    
    const DialogOption& option = currentNode->options[optionIndex];
    
    // Check condition if present
    if (option.condition && !option.condition()) {
        return;
    }
    
    // Move to next node
    if (option.nextNodeId == -1) {
        EndDialog();
    } else {
        SetCurrentNode(option.nextNodeId);
    }
}

void DialogSystem::StartDialog(int startNodeId) {
    SetCurrentNode(startNodeId);
    isActive_ = true;
    SetVisible(true);
}

void DialogSystem::EndDialog() {
    isActive_ = false;
    SetVisible(false);
    
    if (onDialogEnd_) {
        onDialogEnd_();
    }
}

void DialogSystem::Update(float deltaTime) {
    UIElement::Update(deltaTime);
}

void DialogSystem::OnRender() {
    // Rendering would be implemented with actual graphics API
    // Display current dialog node text and options
}

// Minimap implementation
Minimap::Minimap()
    : worldBounds_(0.0f, 0.0f, 1000.0f, 1000.0f)
    , cameraPosition_(0.0f, 0.0f)
    , zoom_(1.0f)
    , nextObjectId_(0) {
    SetSize(Vec2(200.0f, 200.0f));
}

int Minimap::AddMapObject(const MapObject& obj) {
    int id = nextObjectId_++;
    mapObjects_[id] = obj;
    return id;
}

void Minimap::RemoveMapObject(int id) {
    mapObjects_.erase(id);
}

void Minimap::UpdateMapObject(int id, const Vec2& worldPosition) {
    auto it = mapObjects_.find(id);
    if (it != mapObjects_.end()) {
        it->second.worldPosition = worldPosition;
    }
}

void Minimap::SetMapObjectVisible(int id, bool visible) {
    auto it = mapObjects_.find(id);
    if (it != mapObjects_.end()) {
        it->second.visible = visible;
    }
}

void Minimap::ClearMapObjects() {
    mapObjects_.clear();
}

void Minimap::Update(float deltaTime) {
    UIElement::Update(deltaTime);
}

Vec2 Minimap::WorldToMinimapPosition(const Vec2& worldPos) const {
    // Convert world position to minimap position
    float normalizedX = (worldPos.x - worldBounds_.x) / worldBounds_.width;
    float normalizedY = (worldPos.y - worldBounds_.y) / worldBounds_.height;
    
    return Vec2(
        position_.x + normalizedX * size_.x,
        position_.y + normalizedY * size_.y
    );
}

void Minimap::OnRender() {
    // Rendering would be implemented with actual graphics API
    // Draw minimap background and objects
}

// AccessibilityManager implementation
AccessibilityManager& AccessibilityManager::GetInstance() {
    static AccessibilityManager instance;
    return instance;
}

void AccessibilityManager::SetColorBlindMode(AccessibilitySettings::ColorBlindType type) {
    settings_.colorBlindType = type;
    settings_.colorBlindMode = (type != AccessibilitySettings::ColorBlindType::None);
}

Color AccessibilityManager::AdjustColor(const Color& original) const {
    if (!settings_.colorBlindMode) {
        return original;
    }
    
    Color adjusted = original;
    
    // Apply color blind adjustments
    switch (settings_.colorBlindType) {
        case AccessibilitySettings::ColorBlindType::Protanopia:
            // Red-blind: reduce red channel
            adjusted.r = adjusted.r * 0.567f + adjusted.g * 0.433f;
            adjusted.g = adjusted.g * 0.558f + adjusted.r * 0.442f;
            break;
            
        case AccessibilitySettings::ColorBlindType::Deuteranopia:
            // Green-blind: reduce green channel
            adjusted.r = adjusted.r * 0.625f + adjusted.g * 0.375f;
            adjusted.g = adjusted.g * 0.7f + adjusted.r * 0.3f;
            break;
            
        case AccessibilitySettings::ColorBlindType::Tritanopia:
            // Blue-blind: reduce blue channel
            adjusted.g = adjusted.g * 0.95f + adjusted.b * 0.05f;
            adjusted.b = adjusted.b * 0.433f + adjusted.g * 0.567f;
            break;
            
        case AccessibilitySettings::ColorBlindType::None:
        default:
            break;
    }
    
    // Apply high contrast if enabled
    if (settings_.highContrastMode) {
        // Increase contrast by pushing values toward extremes
        adjusted.r = (adjusted.r < 0.5f) ? adjusted.r * 0.5f : 0.5f + (adjusted.r - 0.5f) * 1.5f;
        adjusted.g = (adjusted.g < 0.5f) ? adjusted.g * 0.5f : 0.5f + (adjusted.g - 0.5f) * 1.5f;
        adjusted.b = (adjusted.b < 0.5f) ? adjusted.b * 0.5f : 0.5f + (adjusted.b - 0.5f) * 1.5f;
        
        // Clamp values
        adjusted.r = std::max(0.0f, std::min(1.0f, adjusted.r));
        adjusted.g = std::max(0.0f, std::min(1.0f, adjusted.g));
        adjusted.b = std::max(0.0f, std::min(1.0f, adjusted.b));
    }
    
    return adjusted;
}

} // namespace ui
} // namespace pywrkgame
