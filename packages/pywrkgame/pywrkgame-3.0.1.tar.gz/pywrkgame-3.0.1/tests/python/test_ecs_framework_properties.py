"""
Property-based tests for ECS Framework
Feature: pywrkgame-library, Property 2: Entity lifecycle management
Feature: pywrkgame-library, Property 3: Component storage integrity
Validates: Requirements 1.1
"""

import pytest
from hypothesis import given, strategies as st, settings
import random


class MockEntityManager:
    """Mock EntityManager for property testing"""
    
    def __init__(self):
        self.entities = set()
        self.next_id = 1
        self.available_ids = []
    
    def create_entity(self):
        if self.available_ids:
            entity_id = self.available_ids.pop(0)
        else:
            entity_id = self.next_id
            self.next_id += 1
        
        self.entities.add(entity_id)
        return entity_id
    
    def destroy_entity(self, entity_id):
        if entity_id in self.entities:
            self.entities.remove(entity_id)
            self.available_ids.append(entity_id)
            return True
        return False
    
    def is_entity_valid(self, entity_id):
        return entity_id in self.entities
    
    def get_entity_count(self):
        return len(self.entities)


class MockComponentManager:
    """Mock ComponentManager for property testing"""
    
    def __init__(self):
        self.components = {}  # entity_id -> component_data
    
    def add_component(self, entity_id, component_data):
        self.components[entity_id] = component_data
    
    def remove_component(self, entity_id):
        if entity_id in self.components:
            del self.components[entity_id]
            return True
        return False
    
    def has_component(self, entity_id):
        return entity_id in self.components
    
    def get_component(self, entity_id):
        return self.components.get(entity_id)
    
    def entity_destroyed(self, entity_id):
        self.remove_component(entity_id)


class TestECSFrameworkProperties:
    """Property-based tests for ECS Framework"""
    
    @settings(max_examples=100, deadline=5000)
    @given(entity_counts=st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=10))
    def test_entity_lifecycle_management(self, entity_counts):
        """
        Property 2: Entity lifecycle management
        For any sequence of entity creation and destruction operations,
        the entity manager should maintain consistent state
        **Validates: Requirements 1.1**
        """
        entity_manager = MockEntityManager()
        
        for count in entity_counts:
            # Create entities
            created_entities = []
            for _ in range(count):
                entity_id = entity_manager.create_entity()
                created_entities.append(entity_id)
                
                # Entity should be valid after creation
                assert entity_manager.is_entity_valid(entity_id), f"Entity {entity_id} should be valid after creation"
                assert entity_id != 0, "Entity ID should not be 0 (INVALID_ENTITY)"
            
            # All entities should be unique
            assert len(set(created_entities)) == len(created_entities), "All created entities should be unique"
            
            # Entity count should match
            assert entity_manager.get_entity_count() == len(created_entities), "Entity count should match created entities"
            
            # Randomly destroy some entities
            entities_to_destroy = random.sample(created_entities, k=min(count // 2, len(created_entities)))
            
            for entity_id in entities_to_destroy:
                assert entity_manager.destroy_entity(entity_id), f"Should be able to destroy entity {entity_id}"
                assert not entity_manager.is_entity_valid(entity_id), f"Entity {entity_id} should be invalid after destruction"
            
            # Remaining entities should still be valid
            remaining_entities = [e for e in created_entities if e not in entities_to_destroy]
            for entity_id in remaining_entities:
                assert entity_manager.is_entity_valid(entity_id), f"Remaining entity {entity_id} should still be valid"
            
            # Entity count should reflect destroyed entities
            expected_count = len(created_entities) - len(entities_to_destroy)
            assert entity_manager.get_entity_count() == expected_count, "Entity count should reflect destroyed entities"
            
            # Clean up remaining entities
            for entity_id in remaining_entities:
                entity_manager.destroy_entity(entity_id)
            
            assert entity_manager.get_entity_count() == 0, "All entities should be destroyed"
    
    @settings(max_examples=100, deadline=5000)
    @given(
        entity_count=st.integers(min_value=1, max_value=50),
        component_data=st.lists(
            st.tuples(st.integers(min_value=-1000, max_value=1000), st.floats(min_value=-100.0, max_value=100.0)),
            min_size=1, max_size=50
        )
    )
    def test_component_storage_integrity(self, entity_count, component_data):
        """
        Property 3: Component storage integrity
        For any sequence of component operations, the component storage
        should maintain data integrity and correct associations
        **Validates: Requirements 1.1**
        """
        entity_manager = MockEntityManager()
        component_manager = MockComponentManager()
        
        # Create entities
        entities = []
        for _ in range(entity_count):
            entities.append(entity_manager.create_entity())
        
        # Add components to entities
        entity_component_map = {}
        for i, (int_val, float_val) in enumerate(component_data[:entity_count]):
            entity_id = entities[i % len(entities)]
            component = {"value": int_val, "data": float_val}
            
            component_manager.add_component(entity_id, component)
            entity_component_map[entity_id] = component
            
            # Component should be added correctly
            assert component_manager.has_component(entity_id), f"Entity {entity_id} should have component after adding"
            
            retrieved_component = component_manager.get_component(entity_id)
            assert retrieved_component == component, f"Retrieved component should match added component for entity {entity_id}"
        
        # Verify all components have correct data
        for entity_id, expected_component in entity_component_map.items():
            assert component_manager.has_component(entity_id), f"Entity {entity_id} should have component"
            
            actual_component = component_manager.get_component(entity_id)
            assert actual_component["value"] == expected_component["value"], f"Component value should match for entity {entity_id}"
            assert actual_component["data"] == expected_component["data"], f"Component data should match for entity {entity_id}"
        
        # Verify entities without components don't have them
        for entity_id in entities:
            if entity_id not in entity_component_map:
                assert not component_manager.has_component(entity_id), f"Entity {entity_id} should not have component"
        
        # Remove components from random subset
        entities_with_components = list(entity_component_map.keys())
        if entities_with_components:
            entities_to_remove = random.sample(entities_with_components, k=len(entities_with_components) // 2)
            
            for entity_id in entities_to_remove:
                assert component_manager.remove_component(entity_id), f"Should be able to remove component from entity {entity_id}"
                assert not component_manager.has_component(entity_id), f"Entity {entity_id} should not have component after removal"
                del entity_component_map[entity_id]
        
        # Verify remaining components still have correct data
        for entity_id, expected_component in entity_component_map.items():
            assert component_manager.has_component(entity_id), f"Remaining entity {entity_id} should still have component"
            
            actual_component = component_manager.get_component(entity_id)
            assert actual_component["value"] == expected_component["value"], f"Remaining component value should match for entity {entity_id}"
            assert actual_component["data"] == expected_component["data"], f"Remaining component data should match for entity {entity_id}"
        
        # Test entity destruction removes components
        for entity_id in entities:
            component_manager.entity_destroyed(entity_id)
            assert not component_manager.has_component(entity_id), f"Component should be removed when entity {entity_id} is destroyed"
    
    @settings(max_examples=50, deadline=3000)
    @given(
        create_count=st.integers(min_value=2, max_value=20),
        destroy_count=st.integers(min_value=1, max_value=10)
    )
    def test_entity_reuse_property(self, create_count, destroy_count):
        """
        Property 2: Entity lifecycle management
        For any destroyed entity, its ID should be reused correctly
        and the entity manager should maintain consistent state
        **Validates: Requirements 1.1**
        """
        entity_manager = MockEntityManager()
        
        # Create first batch of entities
        first_batch = []
        for _ in range(create_count):
            first_batch.append(entity_manager.create_entity())
        
        # Record initial state
        initial_count = entity_manager.get_entity_count()
        assert initial_count == create_count, "Initial entity count should match created entities"
        
        # Destroy some entities
        entities_to_destroy = first_batch[:min(destroy_count, len(first_batch))]
        destroyed_ids = set(entities_to_destroy)
        
        for entity_id in entities_to_destroy:
            assert entity_manager.destroy_entity(entity_id), f"Should be able to destroy entity {entity_id}"
            assert not entity_manager.is_entity_valid(entity_id), f"Entity {entity_id} should be invalid after destruction"
        
        # Count should decrease
        after_destroy_count = entity_manager.get_entity_count()
        expected_after_destroy = initial_count - len(entities_to_destroy)
        assert after_destroy_count == expected_after_destroy, "Entity count should decrease after destruction"
        
        # Create new entities - should reuse IDs efficiently
        second_batch = []
        for _ in range(len(entities_to_destroy)):
            new_entity = entity_manager.create_entity()
            second_batch.append(new_entity)
            assert entity_manager.is_entity_valid(new_entity), f"New entity {new_entity} should be valid"
        
        # Count should increase back
        final_count = entity_manager.get_entity_count()
        assert final_count == initial_count, "Entity count should return to initial value after reuse"
        
        # All entities in second batch should be valid
        for entity_id in second_batch:
            assert entity_manager.is_entity_valid(entity_id), f"Reused entity {entity_id} should be valid"
        
        # Remaining entities from first batch should still be valid
        remaining_first_batch = [e for e in first_batch if e not in destroyed_ids]
        for entity_id in remaining_first_batch:
            assert entity_manager.is_entity_valid(entity_id), f"Remaining entity {entity_id} should still be valid"
        
        # Verify no duplicate entities exist
        all_valid_entities = set()
        for entity_id in remaining_first_batch + second_batch:
            if entity_manager.is_entity_valid(entity_id):
                assert entity_id not in all_valid_entities, f"Entity {entity_id} should not be duplicated"
                all_valid_entities.add(entity_id)
        
        # Total valid entities should match entity count
        assert len(all_valid_entities) == entity_manager.get_entity_count(), "Valid entity count should match manager count"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])