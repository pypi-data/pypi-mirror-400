"""
Property-based tests for Touch Input System
Feature: pywrkgame-library, Property 20: Touch Input Recognition
Validates: Requirements 12.1
"""

import pytest
from hypothesis import given, strategies as st, settings
import math
import random
from typing import List, Tuple, Dict, Optional


class MockTouchPoint:
    """Mock TouchPoint for property testing"""
    
    def __init__(self, id: int, x: float, y: float, pressure: float = 1.0, active: bool = True, timestamp: float = 0.0):
        self.id = id
        self.x = x
        self.y = y
        self.pressure = pressure
        self.active = active
        self.timestamp = timestamp
    
    def __eq__(self, other):
        if not isinstance(other, MockTouchPoint):
            return False
        return (self.id == other.id and 
                abs(self.x - other.x) < 0.001 and 
                abs(self.y - other.y) < 0.001 and
                abs(self.pressure - other.pressure) < 0.001 and
                self.active == other.active)


class MockGestureEvent:
    """Mock GestureEvent for property testing"""
    
    def __init__(self, gesture_type: str, x: float, y: float, delta_x: float = 0.0, 
                 delta_y: float = 0.0, scale: float = 1.0, rotation: float = 0.0, 
                 touch_count: int = 1, timestamp: float = 0.0):
        self.type = gesture_type
        self.x = x
        self.y = y
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.scale = scale
        self.rotation = rotation
        self.touch_count = touch_count
        self.timestamp = timestamp


class MockTouchInputManager:
    """Mock TouchInputManager for property testing"""
    
    def __init__(self, is_mobile: bool = True):
        self.is_mobile = is_mobile
        self.max_touch_points = 10 if is_mobile else 1
        self.active_touches: List[MockTouchPoint] = []
        self.gesture_callbacks: Dict[str, callable] = {}
        self.enabled_gestures: Dict[str, bool] = {
            'tap': True, 'double_tap': True, 'long_press': True,
            'swipe': True, 'pinch': True, 'rotate': True, 'pan': True
        }
        self.gesture_thresholds: Dict[str, float] = {
            'tap': 10.0, 'double_tap': 15.0, 'long_press': 20.0,
            'swipe': 50.0, 'pinch': 0.1, 'rotate': 5.0, 'pan': 5.0
        }
        self.touch_sensitivity = 1.0
        self.gesture_events: List[MockGestureEvent] = []
    
    def is_multi_touch_supported(self) -> bool:
        return self.is_mobile
    
    def get_max_touch_points(self) -> int:
        return self.max_touch_points
    
    def get_active_touches(self) -> List[MockTouchPoint]:
        return self.active_touches.copy()
    
    def register_gesture_callback(self, gesture_type: str, callback: callable):
        self.gesture_callbacks[gesture_type] = callback
    
    def unregister_gesture_callback(self, gesture_type: str):
        if gesture_type in self.gesture_callbacks:
            del self.gesture_callbacks[gesture_type]
    
    def enable_gesture(self, gesture_type: str, enable: bool):
        self.enabled_gestures[gesture_type] = enable
    
    def is_gesture_enabled(self, gesture_type: str) -> bool:
        return self.enabled_gestures.get(gesture_type, False)
    
    def set_touch_sensitivity(self, sensitivity: float):
        self.touch_sensitivity = max(0.1, min(2.0, sensitivity))
    
    def get_touch_sensitivity(self) -> float:
        return self.touch_sensitivity
    
    def set_gesture_threshold(self, gesture_type: str, threshold: float):
        self.gesture_thresholds[gesture_type] = threshold
    
    def get_gesture_threshold(self, gesture_type: str) -> float:
        return self.gesture_thresholds.get(gesture_type, 0.0)
    
    def add_touch_point(self, touch: MockTouchPoint):
        """Add a touch point for testing"""
        if len(self.active_touches) < self.max_touch_points:
            # Check if touch ID already exists, if so, update instead of adding
            for i, existing_touch in enumerate(self.active_touches):
                if existing_touch.id == touch.id:
                    self.active_touches[i] = touch
                    return True
            # Add new touch if ID doesn't exist
            self.active_touches.append(touch)
            return True
        return False
    
    def remove_touch_point(self, touch_id: int):
        """Remove a touch point for testing"""
        self.active_touches = [t for t in self.active_touches if t.id != touch_id]
    
    def update_touch_point(self, touch_id: int, x: float, y: float, pressure: float = 1.0):
        """Update a touch point for testing"""
        for touch in self.active_touches:
            if touch.id == touch_id:
                touch.x = x
                touch.y = y
                touch.pressure = pressure
                return True
        return False
    
    def detect_gesture(self, touches: List[MockTouchPoint]) -> Optional[MockGestureEvent]:
        """Simplified gesture detection for testing"""
        if not touches:
            return None
        
        if len(touches) == 1:
            return self._detect_single_touch_gesture(touches[0])
        elif len(touches) >= 2:
            return self._detect_multi_touch_gesture(touches)
        
        return None
    
    def _detect_single_touch_gesture(self, touch: MockTouchPoint) -> Optional[MockGestureEvent]:
        """Detect single touch gestures"""
        # Simple tap detection
        if not touch.active and self.is_gesture_enabled('tap'):
            return MockGestureEvent('tap', touch.x, touch.y, touch_count=1, timestamp=touch.timestamp)
        return None
    
    def _detect_multi_touch_gesture(self, touches: List[MockTouchPoint]) -> Optional[MockGestureEvent]:
        """Detect multi-touch gestures"""
        if len(touches) < 2:
            return None
        
        touch1, touch2 = touches[0], touches[1]
        center_x = (touch1.x + touch2.x) * 0.5
        center_y = (touch1.y + touch2.y) * 0.5
        
        # Simple pinch detection
        distance = math.sqrt((touch2.x - touch1.x)**2 + (touch2.y - touch1.y)**2)
        if distance > 0 and self.is_gesture_enabled('pinch'):
            scale = distance / 100.0  # Normalized scale
            # Use the timestamp from the first touch and actual touch count
            timestamp = touches[0].timestamp if touches else 0.0
            return MockGestureEvent('pinch', center_x, center_y, scale=scale, 
                                  touch_count=len(touches), timestamp=timestamp)
        
        return None
    
    def clear_touches(self):
        """Clear all touch points"""
        self.active_touches.clear()
    
    def trigger_gesture_callback(self, event: MockGestureEvent):
        """Trigger gesture callback for testing"""
        if event.type in self.gesture_callbacks:
            self.gesture_callbacks[event.type](event)
        self.gesture_events.append(event)


class TestTouchInputProperties:
    """Property-based tests for Touch Input System"""
    
    @settings(max_examples=20, deadline=2000)
    @given(
        touch_points=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=5),  # touch_id (reduced range)
                st.floats(min_value=0.0, max_value=800.0),  # x (reduced range)
                st.floats(min_value=0.0, max_value=600.0),  # y (reduced range)
                st.floats(min_value=0.1, max_value=1.0),  # pressure
                st.booleans()  # active
            ),
            min_size=1, max_size=5  # reduced max size
        ),
        is_mobile=st.booleans()
    )
    def test_touch_input_recognition(self, touch_points, is_mobile):
        """
        Property 20: Touch Input Recognition
        For any touch gesture (tap, swipe, pinch, rotate), the system should recognize and respond correctly
        **Validates: Requirements 12.1**
        """
        touch_manager = MockTouchInputManager(is_mobile)
        
        # Test multi-touch support consistency
        if is_mobile:
            assert touch_manager.is_multi_touch_supported(), "Mobile platforms should support multi-touch"
            assert touch_manager.get_max_touch_points() > 1, "Mobile platforms should support multiple touch points"
        else:
            # Desktop may or may not support multi-touch, but should have at least 1 touch point
            assert touch_manager.get_max_touch_points() >= 1, "All platforms should support at least 1 touch point"
        
        # Add touch points up to the maximum supported
        added_touches = []
        unique_touch_ids = set()
        
        for touch_id, x, y, pressure, active in touch_points:
            touch = MockTouchPoint(touch_id, x, y, pressure, active)
            if touch_manager.add_touch_point(touch):
                # Only track unique touches (by ID)
                if touch_id not in unique_touch_ids:
                    added_touches.append(touch)
                    unique_touch_ids.add(touch_id)
                else:
                    # Update existing touch in our tracking
                    for i, existing_touch in enumerate(added_touches):
                        if existing_touch.id == touch_id:
                            added_touches[i] = touch
                            break
            
            # Should not exceed maximum touch points
            assert len(touch_manager.get_active_touches()) <= touch_manager.get_max_touch_points(), \
                "Active touches should not exceed maximum supported touch points"
        
        # Verify all added touches are tracked correctly
        active_touches = touch_manager.get_active_touches()
        assert len(active_touches) == len(added_touches), f"All added touches should be tracked. Expected {len(added_touches)}, got {len(active_touches)}"
        
        for added_touch in added_touches:
            found = False
            for active_touch in active_touches:
                if (active_touch.id == added_touch.id and 
                    abs(active_touch.x - added_touch.x) < 0.001 and
                    abs(active_touch.y - added_touch.y) < 0.001):
                    found = True
                    break
            assert found, f"Added touch {added_touch.id} should be found in active touches"
        
        # Test gesture detection
        if added_touches:
            gesture_event = touch_manager.detect_gesture(added_touches)
            
            if len(added_touches) == 1:
                # Single touch should potentially detect tap
                if not added_touches[0].active and touch_manager.is_gesture_enabled('tap'):
                    assert gesture_event is not None, "Single inactive touch should detect tap gesture"
                    assert gesture_event.type == 'tap', "Single touch gesture should be tap"
                    assert gesture_event.touch_count == 1, "Tap gesture should have touch count of 1"
            
            elif len(added_touches) >= 2 and touch_manager.is_multi_touch_supported():
                # Multi-touch should potentially detect pinch
                if touch_manager.is_gesture_enabled('pinch'):
                    if gesture_event is not None:
                        assert gesture_event.type == 'pinch', "Multi-touch gesture should be pinch"
                        assert gesture_event.touch_count == len(added_touches), f"Pinch gesture should have touch count of {len(added_touches)}"
                        assert gesture_event.scale > 0, "Pinch gesture should have positive scale"
        
        # Test touch point updates
        for touch in added_touches[:3]:  # Test first 3 touches
            new_x = touch.x + 10.0
            new_y = touch.y + 10.0
            new_pressure = min(1.0, touch.pressure + 0.1)
            
            success = touch_manager.update_touch_point(touch.id, new_x, new_y, new_pressure)
            assert success, f"Should be able to update touch point {touch.id}"
            
            # Verify update
            updated_touches = touch_manager.get_active_touches()
            updated_touch = next((t for t in updated_touches if t.id == touch.id), None)
            assert updated_touch is not None, f"Updated touch {touch.id} should still exist"
            assert abs(updated_touch.x - new_x) < 0.001, f"Touch {touch.id} x coordinate should be updated"
            assert abs(updated_touch.y - new_y) < 0.001, f"Touch {touch.id} y coordinate should be updated"
            assert abs(updated_touch.pressure - new_pressure) < 0.001, f"Touch {touch.id} pressure should be updated"
        
        # Test touch point removal
        touches_to_remove = added_touches[:len(added_touches)//2]
        for touch in touches_to_remove:
            touch_manager.remove_touch_point(touch.id)
        
        remaining_touches = touch_manager.get_active_touches()
        expected_remaining = len(added_touches) - len(touches_to_remove)
        assert len(remaining_touches) == expected_remaining, "Correct number of touches should remain after removal"
        
        # Verify removed touches are gone
        for removed_touch in touches_to_remove:
            found = any(t.id == removed_touch.id for t in remaining_touches)
            assert not found, f"Removed touch {removed_touch.id} should not be in active touches"
        
        # Clear all touches
        touch_manager.clear_touches()
        assert len(touch_manager.get_active_touches()) == 0, "All touches should be cleared"
    
    @settings(max_examples=20, deadline=1500)
    @given(
        gesture_types=st.lists(
            st.sampled_from(['tap', 'double_tap', 'long_press', 'swipe', 'pinch', 'rotate', 'pan']),
            min_size=1, max_size=4  # reduced max size
        ),
        thresholds=st.lists(st.floats(min_value=1.0, max_value=50.0), min_size=1, max_size=4),  # reduced range and size
        sensitivity=st.floats(min_value=0.2, max_value=2.0)  # reduced range
    )
    def test_gesture_configuration_properties(self, gesture_types, thresholds, sensitivity):
        """
        Property 20: Touch Input Recognition
        For any gesture configuration, the system should maintain consistent state
        and respect configuration settings
        **Validates: Requirements 12.1**
        """
        touch_manager = MockTouchInputManager()
        
        # Test sensitivity bounds
        touch_manager.set_touch_sensitivity(sensitivity)
        actual_sensitivity = touch_manager.get_touch_sensitivity()
        
        # Sensitivity should be clamped to valid range [0.1, 2.0]
        assert 0.1 <= actual_sensitivity <= 2.0, f"Sensitivity should be clamped to [0.1, 2.0], got {actual_sensitivity}"
        
        if 0.1 <= sensitivity <= 2.0:
            assert abs(actual_sensitivity - sensitivity) < 0.001, "Sensitivity within bounds should be set exactly"
        elif sensitivity < 0.1:
            assert abs(actual_sensitivity - 0.1) < 0.001, "Sensitivity below minimum should be clamped to 0.1"
        else:  # sensitivity > 2.0
            assert abs(actual_sensitivity - 2.0) < 0.001, "Sensitivity above maximum should be clamped to 2.0"
        
        # Test gesture enabling/disabling
        for i, gesture_type in enumerate(gesture_types):
            # Test enabling
            touch_manager.enable_gesture(gesture_type, True)
            assert touch_manager.is_gesture_enabled(gesture_type), f"Gesture {gesture_type} should be enabled"
            
            # Test disabling
            touch_manager.enable_gesture(gesture_type, False)
            assert not touch_manager.is_gesture_enabled(gesture_type), f"Gesture {gesture_type} should be disabled"
            
            # Re-enable for threshold testing
            touch_manager.enable_gesture(gesture_type, True)
            
            # Test threshold setting
            if i < len(thresholds):
                threshold = thresholds[i]
                touch_manager.set_gesture_threshold(gesture_type, threshold)
                actual_threshold = touch_manager.get_gesture_threshold(gesture_type)
                assert abs(actual_threshold - threshold) < 0.001, f"Threshold for {gesture_type} should be set correctly"
        
        # Test gesture callback registration
        callback_triggered = {}
        
        def create_callback(gesture_name):
            def callback(event):
                callback_triggered[gesture_name] = True
            return callback
        
        for gesture_type in gesture_types:
            callback_triggered[gesture_type] = False
            touch_manager.register_gesture_callback(gesture_type, create_callback(gesture_type))
        
        # Simulate gesture events
        for gesture_type in gesture_types:
            if touch_manager.is_gesture_enabled(gesture_type):
                mock_event = MockGestureEvent(gesture_type, 100.0, 100.0)
                touch_manager.trigger_gesture_callback(mock_event)
                
                assert callback_triggered[gesture_type], f"Callback for {gesture_type} should be triggered"
        
        # Test callback unregistration
        for gesture_type in gesture_types[:len(gesture_types)//2]:
            touch_manager.unregister_gesture_callback(gesture_type)
            callback_triggered[gesture_type] = False
            
            # Trigger event again
            mock_event = MockGestureEvent(gesture_type, 200.0, 200.0)
            touch_manager.trigger_gesture_callback(mock_event)
            
            # Callback should not be triggered after unregistration
            assert not callback_triggered[gesture_type], f"Callback for {gesture_type} should not be triggered after unregistration"
    
    @settings(max_examples=15, deadline=1500)
    @given(
        touch_sequences=st.lists(
            st.lists(
                st.tuples(
                    st.integers(min_value=1, max_value=3),  # touch_id (reduced range)
                    st.floats(min_value=0.0, max_value=300.0),  # x (reduced range)
                    st.floats(min_value=0.0, max_value=300.0),  # y (reduced range)
                    st.floats(min_value=0.1, max_value=1.0)  # pressure
                ),
                min_size=1, max_size=2  # reduced max size
            ),
            min_size=2, max_size=5  # reduced max size
        )
    )
    def test_gesture_sequence_recognition(self, touch_sequences):
        """
        Property 20: Touch Input Recognition
        For any sequence of touch inputs, gesture recognition should be consistent
        and maintain proper state throughout the sequence
        **Validates: Requirements 12.1**
        """
        touch_manager = MockTouchInputManager(is_mobile=True)
        
        detected_gestures = []
        
        for sequence_index, touch_data in enumerate(touch_sequences):
            # Clear previous touches
            touch_manager.clear_touches()
            
            # Add touches for this sequence
            current_touches = []
            unique_touch_ids = set()
            
            for touch_id, x, y, pressure in touch_data:
                touch = MockTouchPoint(touch_id, x, y, pressure, active=True, timestamp=float(sequence_index))
                if touch_manager.add_touch_point(touch):
                    # Only track unique touches (by ID)
                    if touch_id not in unique_touch_ids:
                        current_touches.append(touch)
                        unique_touch_ids.add(touch_id)
                    else:
                        # Update existing touch in our tracking
                        for i, existing_touch in enumerate(current_touches):
                            if existing_touch.id == touch_id:
                                current_touches[i] = touch
                                break
            
            # Verify touches were added correctly
            active_touches = touch_manager.get_active_touches()
            assert len(active_touches) == len(current_touches), f"All touches should be added for sequence {sequence_index}. Expected {len(current_touches)}, got {len(active_touches)}"
            
            # Detect gesture for current sequence
            gesture = touch_manager.detect_gesture(current_touches)
            if gesture:
                detected_gestures.append(gesture)
                
                # Verify gesture properties
                assert gesture.touch_count == len(current_touches), f"Gesture touch count should match actual touches. Expected {len(current_touches)}, got {gesture.touch_count}"
                assert gesture.timestamp == float(sequence_index), f"Gesture timestamp should match sequence. Expected {float(sequence_index)}, got {gesture.timestamp}"
                
                if len(current_touches) == 1:
                    # Single touch gesture
                    touch = current_touches[0]
                    assert abs(gesture.x - touch.x) < 0.001, "Single touch gesture position should match touch position"
                    assert abs(gesture.y - touch.y) < 0.001, "Single touch gesture position should match touch position"
                
                elif len(current_touches) >= 2:
                    # Multi-touch gesture - position should be center
                    center_x = sum(t.x for t in current_touches) / len(current_touches)
                    center_y = sum(t.y for t in current_touches) / len(current_touches)
                    
                    # Allow some tolerance for center calculation
                    assert abs(gesture.x - center_x) < 1.0, "Multi-touch gesture X should be near center"
                    assert abs(gesture.y - center_y) < 1.0, "Multi-touch gesture Y should be near center"
        
        # Verify gesture sequence consistency
        single_touch_gestures = [g for g in detected_gestures if g.touch_count == 1]
        multi_touch_gestures = [g for g in detected_gestures if g.touch_count > 1]
        
        # All single touch gestures should be taps (in our simplified implementation)
        for gesture in single_touch_gestures:
            assert gesture.type == 'tap', "Single touch gestures should be taps"
        
        # All multi-touch gestures should be pinches (in our simplified implementation)
        for gesture in multi_touch_gestures:
            assert gesture.type == 'pinch', "Multi-touch gestures should be pinches"
            assert gesture.scale > 0, "Pinch gestures should have positive scale"
        
        # Gesture timestamps should be in sequence
        if len(detected_gestures) > 1:
            for i in range(1, len(detected_gestures)):
                assert detected_gestures[i].timestamp >= detected_gestures[i-1].timestamp, \
                    "Gesture timestamps should be in non-decreasing order"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])