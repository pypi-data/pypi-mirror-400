#include <gtest/gtest.h>
#include <random>
#include <set>
#include <algorithm>
#include "pywrkgame/core/EntityManager.h"
#include "pywrkgame/core/ComponentManager.h"

using namespace pywrkgame::core;

class ECSFrameworkTest : public ::testing::Test {
protected:
    void SetUp() override {
        entityManager = std::make_unique<EntityManager>();
        componentManager = std::make_unique<ComponentManager>();
    }
    
    std::unique_ptr<EntityManager> entityManager;
    std::unique_ptr<ComponentManager> componentManager;
};

TEST_F(ECSFrameworkTest, CreateAndDestroyEntity) {
    EXPECT_EQ(entityManager->GetEntityCount(), 0);
    
    EntityID entity = entityManager->CreateEntity();
    EXPECT_NE(entity, INVALID_ENTITY);
    EXPECT_TRUE(entityManager->IsEntityValid(entity));
    EXPECT_EQ(entityManager->GetEntityCount(), 1);
    
    entityManager->DestroyEntity(entity);
    EXPECT_FALSE(entityManager->IsEntityValid(entity));
    EXPECT_EQ(entityManager->GetEntityCount(), 0);
}

TEST_F(ECSFrameworkTest, CreateMultipleEntities) {
    std::vector<EntityID> entities;
    
    for (int i = 0; i < 10; ++i) {
        EntityID entity = entityManager->CreateEntity();
        entities.push_back(entity);
        EXPECT_TRUE(entityManager->IsEntityValid(entity));
    }
    
    EXPECT_EQ(entityManager->GetEntityCount(), 10);
    
    // All entities should be unique
    std::set<EntityID> uniqueEntities(entities.begin(), entities.end());
    EXPECT_EQ(uniqueEntities.size(), entities.size());
}

TEST_F(ECSFrameworkTest, InvalidEntityOperations) {
    // Operations on invalid entity should not crash
    EXPECT_FALSE(entityManager->IsEntityValid(INVALID_ENTITY));
    EXPECT_NO_THROW(entityManager->DestroyEntity(INVALID_ENTITY));
    EXPECT_NO_THROW(entityManager->DestroyEntity(999999)); // Non-existent entity
}

// Simple test component
struct TestComponent {
    int value = 42;
    float data = 3.14f;
};

TEST_F(ECSFrameworkTest, ComponentOperations) {
    componentManager->RegisterComponent<TestComponent>();
    
    EntityID entity = entityManager->CreateEntity();
    
    // Initially should not have component
    EXPECT_FALSE(componentManager->HasComponent<TestComponent>(entity));
    
    // Add component
    TestComponent component{100, 2.71f};
    componentManager->AddComponent<TestComponent>(entity, component);
    
    // Should now have component
    EXPECT_TRUE(componentManager->HasComponent<TestComponent>(entity));
    
    // Get component and verify data
    auto& retrievedComponent = componentManager->GetComponent<TestComponent>(entity);
    EXPECT_EQ(retrievedComponent.value, 100);
    EXPECT_FLOAT_EQ(retrievedComponent.data, 2.71f);
    
    // Remove component
    componentManager->RemoveComponent<TestComponent>(entity);
    EXPECT_FALSE(componentManager->HasComponent<TestComponent>(entity));
}

// Property-Based Tests for ECS Framework

class ECSPropertyTest : public ::testing::Test {
protected:
    void SetUp() override {
        entityManager = std::make_unique<EntityManager>();
        componentManager = std::make_unique<ComponentManager>();
        componentManager->RegisterComponent<TestComponent>();
        
        // Initialize random number generator with fixed seed for reproducibility
        rng.seed(42);
    }
    
    std::unique_ptr<EntityManager> entityManager;
    std::unique_ptr<ComponentManager> componentManager;
    std::mt19937 rng;
    
    // Helper to generate random entities
    std::vector<EntityID> GenerateRandomEntities(size_t count) {
        std::vector<EntityID> entities;
        for (size_t i = 0; i < count; ++i) {
            entities.push_back(entityManager->CreateEntity());
        }
        return entities;
    }
    
    // Helper to generate random component data
    TestComponent GenerateRandomComponent() {
        std::uniform_int_distribution<int> intDist(-1000, 1000);
        std::uniform_real_distribution<float> floatDist(-100.0f, 100.0f);
        return TestComponent{intDist(rng), floatDist(rng)};
    }
};

TEST_F(ECSPropertyTest, EntityLifecycleManagement) {
    /*
     * Feature: pywrkgame-library, Property 2: Entity lifecycle management
     * For any sequence of entity creation and destruction operations,
     * the entity manager should maintain consistent state
     * **Validates: Requirements 1.1**
     */
    
    // Test with various entity counts
    std::vector<size_t> testCounts = {1, 10, 50, 100, 500};
    
    for (size_t entityCount : testCounts) {
        // Create entities
        std::vector<EntityID> entities = GenerateRandomEntities(entityCount);
        
        // Verify all entities are valid and unique
        std::set<EntityID> uniqueEntities(entities.begin(), entities.end());
        EXPECT_EQ(uniqueEntities.size(), entities.size()) 
            << "All entities should be unique for count " << entityCount;
        
        for (EntityID entity : entities) {
            EXPECT_TRUE(entityManager->IsEntityValid(entity))
                << "Entity " << entity << " should be valid";
            EXPECT_NE(entity, INVALID_ENTITY)
                << "Entity should not be INVALID_ENTITY";
        }
        
        EXPECT_EQ(entityManager->GetEntityCount(), entityCount)
            << "Entity count should match created entities";
        
        // Randomly destroy half the entities
        std::shuffle(entities.begin(), entities.end(), rng);
        size_t destroyCount = entityCount / 2;
        
        for (size_t i = 0; i < destroyCount; ++i) {
            EntityID entityToDestroy = entities[i];
            entityManager->DestroyEntity(entityToDestroy);
            
            EXPECT_FALSE(entityManager->IsEntityValid(entityToDestroy))
                << "Destroyed entity " << entityToDestroy << " should be invalid";
        }
        
        EXPECT_EQ(entityManager->GetEntityCount(), entityCount - destroyCount)
            << "Entity count should reflect destroyed entities";
        
        // Verify remaining entities are still valid
        for (size_t i = destroyCount; i < entities.size(); ++i) {
            EXPECT_TRUE(entityManager->IsEntityValid(entities[i]))
                << "Remaining entity " << entities[i] << " should still be valid";
        }
        
        // Clean up remaining entities
        for (size_t i = destroyCount; i < entities.size(); ++i) {
            entityManager->DestroyEntity(entities[i]);
        }
        
        EXPECT_EQ(entityManager->GetEntityCount(), 0)
            << "All entities should be destroyed";
    }
}

TEST_F(ECSPropertyTest, ComponentStorageIntegrity) {
    /*
     * Feature: pywrkgame-library, Property 3: Component storage integrity
     * For any sequence of component operations, the component storage
     * should maintain data integrity and correct associations
     * **Validates: Requirements 1.1**
     */
    
    // Test with various entity and component combinations
    std::vector<size_t> testCounts = {1, 10, 50, 100};
    
    for (size_t entityCount : testCounts) {
        // Create entities
        std::vector<EntityID> entities = GenerateRandomEntities(entityCount);
        
        // Store expected component data
        std::map<EntityID, TestComponent> expectedComponents;
        
        // Add components to random subset of entities
        std::uniform_int_distribution<size_t> entityDist(0, entities.size() - 1);
        size_t componentsToAdd = entityCount / 2 + 1;
        
        for (size_t i = 0; i < componentsToAdd; ++i) {
            EntityID entity = entities[entityDist(rng)];
            TestComponent component = GenerateRandomComponent();
            
            componentManager->AddComponent<TestComponent>(entity, component);
            expectedComponents[entity] = component;
            
            EXPECT_TRUE(componentManager->HasComponent<TestComponent>(entity))
                << "Entity " << entity << " should have component after adding";
        }
        
        // Verify all added components have correct data
        for (const auto& pair : expectedComponents) {
            EntityID entity = pair.first;
            const TestComponent& expected = pair.second;
            
            EXPECT_TRUE(componentManager->HasComponent<TestComponent>(entity))
                << "Entity " << entity << " should have component";
            
            const auto& actual = componentManager->GetComponent<TestComponent>(entity);
            EXPECT_EQ(actual.value, expected.value)
                << "Component value should match for entity " << entity;
            EXPECT_FLOAT_EQ(actual.data, expected.data)
                << "Component data should match for entity " << entity;
        }
        
        // Verify entities without components don't have them
        for (EntityID entity : entities) {
            if (expectedComponents.find(entity) == expectedComponents.end()) {
                EXPECT_FALSE(componentManager->HasComponent<TestComponent>(entity))
                    << "Entity " << entity << " should not have component";
            }
        }
        
        // Remove components from random subset
        std::vector<EntityID> entitiesWithComponents;
        for (const auto& pair : expectedComponents) {
            entitiesWithComponents.push_back(pair.first);
        }
        
        std::shuffle(entitiesWithComponents.begin(), entitiesWithComponents.end(), rng);
        size_t componentsToRemove = entitiesWithComponents.size() / 2;
        
        for (size_t i = 0; i < componentsToRemove; ++i) {
            EntityID entity = entitiesWithComponents[i];
            componentManager->RemoveComponent<TestComponent>(entity);
            expectedComponents.erase(entity);
            
            EXPECT_FALSE(componentManager->HasComponent<TestComponent>(entity))
                << "Entity " << entity << " should not have component after removal";
        }
        
        // Verify remaining components still have correct data
        for (const auto& pair : expectedComponents) {
            EntityID entity = pair.first;
            const TestComponent& expected = pair.second;
            
            EXPECT_TRUE(componentManager->HasComponent<TestComponent>(entity))
                << "Remaining entity " << entity << " should still have component";
            
            const auto& actual = componentManager->GetComponent<TestComponent>(entity);
            EXPECT_EQ(actual.value, expected.value)
                << "Remaining component value should match for entity " << entity;
            EXPECT_FLOAT_EQ(actual.data, expected.data)
                << "Remaining component data should match for entity " << entity;
        }
        
        // Test entity destruction removes components
        for (EntityID entity : entities) {
            componentManager->EntityDestroyed(entity);
            EXPECT_FALSE(componentManager->HasComponent<TestComponent>(entity))
                << "Component should be removed when entity " << entity << " is destroyed";
        }
        
        // Clean up entities
        for (EntityID entity : entities) {
            entityManager->DestroyEntity(entity);
        }
    }
}

TEST_F(ECSPropertyTest, EntityReuseProperty) {
    /*
     * Feature: pywrkgame-library, Property 2: Entity lifecycle management
     * For any destroyed entity, its ID should be reused correctly
     * without affecting other entities
     * **Validates: Requirements 1.1**
     */
    
    // Create and destroy entities multiple times
    std::vector<EntityID> firstBatch = GenerateRandomEntities(10);
    
    // Destroy all entities
    for (EntityID entity : firstBatch) {
        entityManager->DestroyEntity(entity);
    }
    
    EXPECT_EQ(entityManager->GetEntityCount(), 0);
    
    // Create new entities - should reuse IDs
    std::vector<EntityID> secondBatch = GenerateRandomEntities(10);
    
    // All new entities should be valid
    for (EntityID entity : secondBatch) {
        EXPECT_TRUE(entityManager->IsEntityValid(entity))
            << "Reused entity " << entity << " should be valid";
    }
    
    // Old entities should still be invalid
    for (EntityID entity : firstBatch) {
        EXPECT_FALSE(entityManager->IsEntityValid(entity))
            << "Old entity " << entity << " should remain invalid";
    }
    
    EXPECT_EQ(entityManager->GetEntityCount(), 10);
    
    // Clean up
    for (EntityID entity : secondBatch) {
        entityManager->DestroyEntity(entity);
    }
}