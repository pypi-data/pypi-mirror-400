/**
 * Property-Based Tests for UI System
 * Feature: pywrkgame-library, Property 21-26
 * Validates: Requirements 5.1-5.8
 */

#include <gtest/gtest.h>
#include "pywrkgame/ui/UISystem.h"
#include <cmath>
#include <algorithm>
#include <random>

using namespace pywrkgame::ui;

class UISystemTest : public ::testing::Test {
protected:
    void SetUp() override {
        uiSystem = std::make_unique<UISystem>();
        ASSERT_TRUE(uiSystem->Initialize());
    }
    
    void TearDown() override {
        uiSystem->Shutdown();
    }
    
    std::unique_ptr<UISystem> uiSystem;
};

// Unit test: UI System initialization
TEST_F(UISystemTest, UISystemInitialized) {
    EXPECT_NE(uiSystem->GetRootElement(), nullptr);
}

// Unit test: Create UI element
TEST_F(UISystemTest, CreateUIElement) {
    auto element = std::make_shared<UIElement>();
    EXPECT_NE(element, nullptr);
    EXPECT_TRUE(element->IsVisible());
    EXPECT_TRUE(element->IsEnabled());
}

// Unit test: Element hierarchy
TEST_F(UISystemTest, ElementHierarchy) {
    auto parent = std::make_shared<UIElement>();
    auto child1 = std::make_shared<UIElement>();
    auto child2 = std::make_shared<UIElement>();
    
    parent->AddChild(child1);
    parent->AddChild(child2);
    
    EXPECT_EQ(parent->GetChildren().size(), 2u);
    EXPECT_EQ(child1->GetParent(), parent.get());
    EXPECT_EQ(child2->GetParent(), parent.get());
    
    parent->RemoveChild(child1);
    EXPECT_EQ(parent->GetChildren().size(), 1u);
    EXPECT_EQ(child1->GetParent(), nullptr);
}

// Unit test: Dialog System
TEST_F(UISystemTest, DialogSystem) {
    auto dialogSystem = std::make_shared<DialogSystem>();
    
    EXPECT_FALSE(dialogSystem->IsActive());
    
    // Create dialog nodes
    DialogNode node1(1, "NPC", "Hello, traveler!");
    node1.options.push_back(DialogOption("Who are you?", 2));
    node1.options.push_back(DialogOption("Goodbye", -1));
    
    DialogNode node2(2, "NPC", "I am a merchant.");
    node2.options.push_back(DialogOption("What do you sell?", 3));
    node2.options.push_back(DialogOption("Goodbye", -1));
    
    DialogNode node3(3, "NPC", "I sell potions and weapons.");
    node3.options.push_back(DialogOption("Thanks!", -1));
    
    dialogSystem->AddNode(node1);
    dialogSystem->AddNode(node2);
    dialogSystem->AddNode(node3);
    
    // Start dialog
    dialogSystem->StartDialog(1);
    EXPECT_TRUE(dialogSystem->IsActive());
    EXPECT_EQ(dialogSystem->GetCurrentNode(), 1);
    
    // Select first option
    dialogSystem->SelectOption(0);
    EXPECT_EQ(dialogSystem->GetCurrentNode(), 2);
    
    // Select first option again
    dialogSystem->SelectOption(0);
    EXPECT_EQ(dialogSystem->GetCurrentNode(), 3);
    
    // End dialog
    dialogSystem->SelectOption(0);
    EXPECT_FALSE(dialogSystem->IsActive());
}

// Unit test: Minimap
TEST_F(UISystemTest, Minimap) {
    auto minimap = std::make_shared<Minimap>();
    
    EXPECT_EQ(minimap->GetMapObjectCount(), 0);
    
    // Add map objects
    Minimap::MapObject obj1(Vec2(100.0f, 100.0f), Color(1.0f, 0.0f, 0.0f, 1.0f));
    Minimap::MapObject obj2(Vec2(200.0f, 200.0f), Color(0.0f, 1.0f, 0.0f, 1.0f));
    
    int id1 = minimap->AddMapObject(obj1);
    int id2 = minimap->AddMapObject(obj2);
    
    EXPECT_EQ(minimap->GetMapObjectCount(), 2);
    
    // Update object position
    minimap->UpdateMapObject(id1, Vec2(150.0f, 150.0f));
    
    // Set object visibility
    minimap->SetMapObjectVisible(id2, false);
    
    // Remove object
    minimap->RemoveMapObject(id1);
    EXPECT_EQ(minimap->GetMapObjectCount(), 1);
    
    // Clear all objects
    minimap->ClearMapObjects();
    EXPECT_EQ(minimap->GetMapObjectCount(), 0);
}

// Property Test 24: Dialog System Branching
TEST_F(UISystemTest, DialogSystemBranching) {
    /*
     * Feature: pywrkgame-library, Property 24: Dialog System Branching
     * For any dialog tree with branching conversations, navigation should follow correct logic paths
     */
    
    auto dialogSystem = std::make_shared<DialogSystem>();
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> nodeDist(3, 10);
    
    // Test with multiple random dialog chains
    for (int test = 0; test < 10; ++test) {
        int numNodes = nodeDist(gen);
        
        // Create a linear dialog chain
        for (int i = 0; i < numNodes; ++i) {
            DialogNode node(i, "Speaker", "Dialog text " + std::to_string(i));
            
            if (i < numNodes - 1) {
                node.options.push_back(DialogOption("Continue", i + 1));
            } else {
                node.options.push_back(DialogOption("End", -1));
            }
            
            dialogSystem->AddNode(node);
        }
        
        // Start dialog at first node
        dialogSystem->StartDialog(0);
        ASSERT_TRUE(dialogSystem->IsActive());
        ASSERT_EQ(dialogSystem->GetCurrentNode(), 0);
        
        // Navigate through all nodes
        for (int i = 0; i < numNodes - 1; ++i) {
            const DialogNode* currentNode = dialogSystem->GetCurrentNodeData();
            ASSERT_NE(currentNode, nullptr);
            ASSERT_EQ(currentNode->id, i);
            ASSERT_FALSE(currentNode->options.empty());
            
            dialogSystem->SelectOption(0);
            ASSERT_EQ(dialogSystem->GetCurrentNode(), i + 1);
        }
        
        // Select final option to end dialog
        dialogSystem->SelectOption(0);
        ASSERT_FALSE(dialogSystem->IsActive());
    }
}

// Property Test 24: Dialog Branching with Multiple Options
TEST_F(UISystemTest, DialogBranchingMultipleOptions) {
    /*
     * Feature: pywrkgame-library, Property 24: Dialog System Branching
     * Verifies multiple dialog options work correctly
     */
    
    auto dialogSystem = std::make_shared<DialogSystem>();
    
    // Create branching dialog
    DialogNode root(0, "NPC", "Choose your path");
    root.options.push_back(DialogOption("Path A", 1));
    root.options.push_back(DialogOption("Path B", 2));
    root.options.push_back(DialogOption("Leave", -1));
    
    DialogNode pathA(1, "NPC", "You chose path A");
    pathA.options.push_back(DialogOption("End", -1));
    
    DialogNode pathB(2, "NPC", "You chose path B");
    pathB.options.push_back(DialogOption("End", -1));
    
    dialogSystem->AddNode(root);
    dialogSystem->AddNode(pathA);
    dialogSystem->AddNode(pathB);
    
    // Test path A
    dialogSystem->StartDialog(0);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 0);
    dialogSystem->SelectOption(0);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 1);
    dialogSystem->SelectOption(0);
    ASSERT_FALSE(dialogSystem->IsActive());
    
    // Test path B
    dialogSystem->StartDialog(0);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 0);
    dialogSystem->SelectOption(1);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 2);
    dialogSystem->SelectOption(0);
    ASSERT_FALSE(dialogSystem->IsActive());
    
    // Test direct exit
    dialogSystem->StartDialog(0);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 0);
    dialogSystem->SelectOption(2);
    ASSERT_FALSE(dialogSystem->IsActive());
}

// Property Test 24: Dialog Conditional Options
TEST_F(UISystemTest, DialogConditionalOptions) {
    /*
     * Feature: pywrkgame-library, Property 24: Dialog System Branching
     * Verifies conditional options are evaluated correctly
     */
    
    auto dialogSystem = std::make_shared<DialogSystem>();
    
    bool conditionMet = false;
    
    DialogNode node(0, "NPC", "Test conditional");
    
    DialogOption conditionalOption("Conditional path", 1);
    conditionalOption.condition = [&conditionMet]() { return conditionMet; };
    
    node.options.push_back(conditionalOption);
    node.options.push_back(DialogOption("Always available", -1));
    
    DialogNode conditionalNode(1, "NPC", "Condition was met");
    conditionalNode.options.push_back(DialogOption("End", -1));
    
    dialogSystem->AddNode(node);
    dialogSystem->AddNode(conditionalNode);
    
    // Start dialog with condition false
    dialogSystem->StartDialog(0);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 0);
    
    // Try to select conditional option (should fail)
    dialogSystem->SelectOption(0);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 0); // Should stay at same node
    
    // Select always available option
    dialogSystem->SelectOption(1);
    ASSERT_FALSE(dialogSystem->IsActive());
    
    // Now test with condition true
    conditionMet = true;
    dialogSystem->StartDialog(0);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 0);
    
    // Select conditional option (should succeed)
    dialogSystem->SelectOption(0);
    ASSERT_EQ(dialogSystem->GetCurrentNode(), 1);
    
    dialogSystem->SelectOption(0);
    ASSERT_FALSE(dialogSystem->IsActive());
}

// Property Test 25: Real-time Minimap Updates
TEST_F(UISystemTest, MinimapRealTimeUpdates) {
    /*
     * Feature: pywrkgame-library, Property 25: Real-time Minimap Updates
     * For any minimap component, updates should reflect game state changes in real-time
     */
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> objDist(5, 20);
    std::uniform_real_distribution<float> posDist(0.0f, 1000.0f);
    
    for (int test = 0; test < 10; ++test) {
        auto minimap = std::make_shared<Minimap>();
        
        minimap->SetPosition(Vec2(0.0f, 0.0f));
        minimap->SetSize(Vec2(200.0f, 200.0f));
        minimap->SetWorldBounds(Rect(0.0f, 0.0f, 1000.0f, 1000.0f));
        
        int numObjects = objDist(gen);
        std::vector<int> objectIds;
        
        // Add objects at random positions
        for (int i = 0; i < numObjects; ++i) {
            float x = posDist(gen);
            float y = posDist(gen);
            
            Minimap::MapObject obj(Vec2(x, y), Color(1.0f, 0.0f, 0.0f, 1.0f));
            int id = minimap->AddMapObject(obj);
            objectIds.push_back(id);
        }
        
        // Verify all objects were added
        ASSERT_EQ(minimap->GetMapObjectCount(), numObjects);
        
        // Update random object positions
        std::uniform_int_distribution<int> updateDist(1, std::min(5, numObjects));
        int numUpdates = updateDist(gen);
        for (int i = 0; i < numUpdates; ++i) {
            std::uniform_int_distribution<int> objIndexDist(0, numObjects - 1);
            int objIndex = objIndexDist(gen);
            float newX = posDist(gen);
            float newY = posDist(gen);
            
            minimap->UpdateMapObject(objectIds[objIndex], Vec2(newX, newY));
        }
        
        // Remove random objects
        std::uniform_int_distribution<int> removalDist(1, std::min(3, numObjects));
        int numRemovals = removalDist(gen);
        for (int i = 0; i < numRemovals; ++i) {
            if (!objectIds.empty()) {
                std::uniform_int_distribution<int> objIndexDist(0, static_cast<int>(objectIds.size()) - 1);
                int objIndex = objIndexDist(gen);
                minimap->RemoveMapObject(objectIds[objIndex]);
                objectIds.erase(objectIds.begin() + objIndex);
            }
        }
        
        // Verify correct number of objects remain
        ASSERT_EQ(minimap->GetMapObjectCount(), static_cast<int>(objectIds.size()));
        
        // Clear all objects
        minimap->ClearMapObjects();
        ASSERT_EQ(minimap->GetMapObjectCount(), 0);
    }
}

// Property Test 25: Minimap Coordinate Conversion
TEST_F(UISystemTest, MinimapCoordinateConversion) {
    /*
     * Feature: pywrkgame-library, Property 25: Real-time Minimap Updates
     * Verifies world coordinates are correctly converted to minimap coordinates
     */
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> minimapPosDist(0.0f, 500.0f);
    std::uniform_real_distribution<float> minimapSizeDist(100.0f, 300.0f);
    std::uniform_real_distribution<float> worldSizeDist(500.0f, 5000.0f);
    
    for (int test = 0; test < 10; ++test) {
        auto minimap = std::make_shared<Minimap>();
        
        float minimapX = minimapPosDist(gen);
        float minimapY = minimapPosDist(gen);
        float minimapWidth = minimapSizeDist(gen);
        float minimapHeight = minimapSizeDist(gen);
        float worldWidth = worldSizeDist(gen);
        float worldHeight = worldSizeDist(gen);
        
        minimap->SetPosition(Vec2(minimapX, minimapY));
        minimap->SetSize(Vec2(minimapWidth, minimapHeight));
        minimap->SetWorldBounds(Rect(0.0f, 0.0f, worldWidth, worldHeight));
        
        // Test corner positions
        Vec2 worldOrigin(0.0f, 0.0f);
        Vec2 minimapOrigin = minimap->WorldToMinimapPosition(worldOrigin);
        EXPECT_NEAR(minimapOrigin.x, minimapX, 0.01f);
        EXPECT_NEAR(minimapOrigin.y, minimapY, 0.01f);
        
        Vec2 worldMax(worldWidth, worldHeight);
        Vec2 minimapMax = minimap->WorldToMinimapPosition(worldMax);
        EXPECT_NEAR(minimapMax.x, minimapX + minimapWidth, 0.01f);
        EXPECT_NEAR(minimapMax.y, minimapY + minimapHeight, 0.01f);
        
        // Test center position
        Vec2 worldCenter(worldWidth * 0.5f, worldHeight * 0.5f);
        Vec2 minimapCenter = minimap->WorldToMinimapPosition(worldCenter);
        EXPECT_NEAR(minimapCenter.x, minimapX + minimapWidth * 0.5f, 0.01f);
        EXPECT_NEAR(minimapCenter.y, minimapY + minimapHeight * 0.5f, 0.01f);
        
        // Test random positions
        std::uniform_real_distribution<float> worldXDist(0.0f, worldWidth);
        std::uniform_real_distribution<float> worldYDist(0.0f, worldHeight);
        
        for (int i = 0; i < 10; ++i) {
            float worldX = worldXDist(gen);
            float worldY = worldYDist(gen);
            
            Vec2 worldPos(worldX, worldY);
            Vec2 minimapPos = minimap->WorldToMinimapPosition(worldPos);
            
            // Verify minimap position is within minimap bounds
            EXPECT_GE(minimapPos.x, minimapX);
            EXPECT_LE(minimapPos.x, minimapX + minimapWidth);
            EXPECT_GE(minimapPos.y, minimapY);
            EXPECT_LE(minimapPos.y, minimapY + minimapHeight);
            
            // Verify proportional mapping
            float normalizedX = worldX / worldWidth;
            float normalizedY = worldY / worldHeight;
            float expectedMinimapX = minimapX + normalizedX * minimapWidth;
            float expectedMinimapY = minimapY + normalizedY * minimapHeight;
            
            EXPECT_NEAR(minimapPos.x, expectedMinimapX, 0.01f);
            EXPECT_NEAR(minimapPos.y, expectedMinimapY, 0.01f);
        }
    }
}
