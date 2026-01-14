/**
 * Property-based tests for Advanced Network Features
 * Feature: pywrkgame-library, Property 41: Lag Compensation
 * Feature: pywrkgame-library, Property 44: Anti-cheat Protection
 * Feature: pywrkgame-library, Property 45: Cloud Save Synchronization
 * Validates: Requirements 8.3, 8.6, 8.7
 */

#include <gtest/gtest.h>
#include "pywrkgame/network/NetworkManager.h"
#include <vector>
#include <random>
#include <algorithm>
#include <string>

using namespace pywrkgame::network;

class AdvancedNetworkPropertiesTest : public ::testing::Test {
protected:
    void SetUp() override {
        network = std::make_unique<NetworkManager>();
        rng.seed(std::random_device{}());
    }
    
    void TearDown() override {
        if (network) {
            network->Shutdown();
        }
    }
    
    std::vector<uint8_t> GenerateRandomData(size_t size) {
        std::vector<uint8_t> data(size);
        std::uniform_int_distribution<int> dist(0, 255);
        for (size_t i = 0; i < size; ++i) {
            data[i] = static_cast<uint8_t>(dist(rng));
        }
        return data;
    }
    
    std::string GenerateRandomSaveId() {
        std::uniform_int_distribution<int> dist(1000, 9999);
        return "save_" + std::to_string(dist(rng));
    }
    
    std::unique_ptr<NetworkManager> network;
    std::mt19937 rng;
};

/**
 * Property 41: Lag Compensation
 * For any network session with artificial lag, compensation algorithms should
 * maintain smooth gameplay
 * 
 * This test verifies that:
 * 1. Lag compensation can be enabled/disabled
 * 2. Game state can be rewound to compensate for lag
 * 3. Client prediction can be enabled/disabled
 * 4. Client movement can be predicted
 * 5. Latency is affected by compensation
 */
TEST_F(AdvancedNetworkPropertiesTest, LagCompensation) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
        ASSERT_TRUE(network->StartServer(12345));
        
        // Test lag compensation enable/disable
        bool enableLagComp = (i % 2 == 0);
        network->EnableLagCompensation(enableLagComp);
        EXPECT_EQ(network->IsLagCompensationEnabled(), enableLagComp);
        
        // Test client prediction enable/disable
        bool enablePrediction = (i % 3 == 0);
        network->SetClientPrediction(enablePrediction);
        EXPECT_EQ(network->IsClientPredictionEnabled(), enablePrediction);
        
        // Test game state rewind
        std::uniform_real_distribution<float> timeOffsetDist(0.0f, 1.0f);
        float timeOffset = timeOffsetDist(rng);
        
        float latencyBefore = network->GetAverageLatency();
        network->RewindGameState(timeOffset);
        
        // If lag compensation is enabled, latency should be adjusted
        if (enableLagComp) {
            float latencyAfter = network->GetAverageLatency();
            EXPECT_LE(latencyAfter, latencyBefore)
                << "Lag compensation should reduce or maintain latency";
        }
        
        // Test client movement prediction
        uint32_t localPlayerId = network->GetLocalPlayerId();
        std::uniform_real_distribution<float> deltaDist(0.016f, 0.1f);
        float deltaTime = deltaDist(rng);
        
        network->PredictClientMovement(localPlayerId, deltaTime);
        
        // Prediction should work without errors
        EXPECT_TRUE(network->IsConnected());
        
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}

/**
 * Property 41: Lag Compensation - Invalid Time Offset Handling
 * For any invalid time offset, the system should handle it gracefully
 */
TEST_F(AdvancedNetworkPropertiesTest, InvalidTimeOffsetHandling) {
    const int NUM_ITERATIONS = 50;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->StartServer(12345));
    network->EnableLagCompensation(true);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate invalid time offsets
        std::uniform_real_distribution<float> invalidDist(-10.0f, -0.1f);
        float negativeOffset = invalidDist(rng);
        
        std::uniform_real_distribution<float> largeDist(1.1f, 100.0f);
        float largeOffset = largeDist(rng);
        
        float latencyBefore = network->GetAverageLatency();
        
        // Try negative offset
        network->RewindGameState(negativeOffset);
        float latencyAfterNegative = network->GetAverageLatency();
        
        // Latency should not change for invalid offset
        EXPECT_EQ(latencyAfterNegative, latencyBefore)
            << "Invalid negative time offset should be ignored";
        
        // Try large offset
        network->RewindGameState(largeOffset);
        float latencyAfterLarge = network->GetAverageLatency();
        
        // Latency should not change for invalid offset
        EXPECT_EQ(latencyAfterLarge, latencyBefore)
            << "Invalid large time offset should be ignored";
    }
}

/**
 * Property 41: Lag Compensation - Prediction for Non-existent Player
 * For any non-existent player, prediction should handle it gracefully
 */
TEST_F(AdvancedNetworkPropertiesTest, PredictionNonExistentPlayer) {
    const int NUM_ITERATIONS = 100;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->StartServer(12345));
    network->SetClientPrediction(true);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate random non-existent player ID
        std::uniform_int_distribution<uint32_t> playerDist(100000, 999999);
        uint32_t fakePlayerId = playerDist(rng);
        
        // Ensure it's not the local player
        while (fakePlayerId == network->GetLocalPlayerId()) {
            fakePlayerId = playerDist(rng);
        }
        
        // Try to predict movement for non-existent player
        network->PredictClientMovement(fakePlayerId, 0.016f);
        
        // Should not crash or cause errors
        EXPECT_TRUE(network->IsConnected());
    }
}

/**
 * Property 44: Anti-cheat Protection
 * For any attempted cheating method, the system should detect and prevent or
 * report the violation
 * 
 * This test verifies that:
 * 1. Anti-cheat can be enabled/disabled
 * 2. Player actions are validated
 * 3. Suspicious activity is reported
 * 4. Players are flagged after multiple violations
 * 5. Flagged players can be retrieved
 */
TEST_F(AdvancedNetworkPropertiesTest, AntiCheatProtection) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
        ASSERT_TRUE(network->StartServer(12345));
        
        // Test anti-cheat enable/disable
        bool enableAntiCheat = (i % 2 == 0);
        network->EnableAntiCheat(enableAntiCheat);
        EXPECT_EQ(network->IsAntiCheatEnabled(), enableAntiCheat);
        
        uint32_t localPlayerId = network->GetLocalPlayerId();
        
        // Test valid action validation
        std::uniform_int_distribution<size_t> sizeDist(10, 1000);
        size_t validSize = sizeDist(rng);
        std::vector<uint8_t> validAction = GenerateRandomData(validSize);
        
        bool validResult = network->ValidatePlayerAction(localPlayerId, validAction);
        EXPECT_TRUE(validResult)
            << "Valid action should pass validation";
        
        // Test invalid action (empty)
        std::vector<uint8_t> emptyAction;
        bool emptyResult = network->ValidatePlayerAction(localPlayerId, emptyAction);
        
        if (enableAntiCheat) {
            EXPECT_FALSE(emptyResult)
                << "Empty action should fail validation when anti-cheat is enabled";
        } else {
            EXPECT_TRUE(emptyResult)
                << "Empty action should pass when anti-cheat is disabled";
        }
        
        // Test invalid action (too large)
        std::vector<uint8_t> largeAction(20000, 0xFF);
        bool largeResult = network->ValidatePlayerAction(localPlayerId, largeAction);
        
        if (enableAntiCheat) {
            EXPECT_FALSE(largeResult)
                << "Oversized action should fail validation when anti-cheat is enabled";
        } else {
            EXPECT_TRUE(largeResult)
                << "Oversized action should pass when anti-cheat is disabled";
        }
        
        // Test suspicious activity reporting
        if (enableAntiCheat) {
            // Report multiple suspicious activities
            for (int j = 0; j < 3; ++j) {
                network->ReportSuspiciousActivity(localPlayerId, "Test violation");
            }
            
            // Player should be flagged
            std::vector<uint32_t> flaggedPlayers = network->GetFlaggedPlayers();
            bool isFlagged = std::find(flaggedPlayers.begin(), flaggedPlayers.end(), 
                                      localPlayerId) != flaggedPlayers.end();
            EXPECT_TRUE(isFlagged)
                << "Player should be flagged after multiple violations";
        }
        
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}

/**
 * Property 44: Anti-cheat Protection - Non-existent Player Validation
 * For any non-existent player, action validation should fail
 */
TEST_F(AdvancedNetworkPropertiesTest, AntiCheatNonExistentPlayer) {
    const int NUM_ITERATIONS = 100;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->StartServer(12345));
    network->EnableAntiCheat(true);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate random non-existent player ID
        std::uniform_int_distribution<uint32_t> playerDist(100000, 999999);
        uint32_t fakePlayerId = playerDist(rng);
        
        // Ensure it's not the local player
        while (fakePlayerId == network->GetLocalPlayerId()) {
            fakePlayerId = playerDist(rng);
        }
        
        // Try to validate action for non-existent player
        std::vector<uint8_t> action = GenerateRandomData(100);
        bool result = network->ValidatePlayerAction(fakePlayerId, action);
        
        EXPECT_FALSE(result)
            << "Action validation should fail for non-existent player";
    }
}

/**
 * Property 45: Cloud Save Synchronization
 * For any game save data, synchronization across devices should work correctly
 * without data loss
 * 
 * This test verifies that:
 * 1. Cloud saves can be enabled with a provider
 * 2. Save data can be uploaded
 * 3. Save data can be downloaded
 * 4. Downloaded data matches uploaded data (round-trip)
 * 5. Save list can be retrieved
 * 6. Saves can be deleted
 * 7. Synchronization works correctly
 */
TEST_F(AdvancedNetworkPropertiesTest, CloudSaveSynchronization) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
        
        // Test enabling cloud saves
        std::vector<std::string> providers = {"AWS", "Azure", "GCP", "Custom"};
        std::uniform_int_distribution<size_t> providerDist(0, providers.size() - 1);
        std::string provider = providers[providerDist(rng)];
        
        bool enableResult = network->EnableCloudSaves(provider);
        EXPECT_TRUE(enableResult);
        
        // Generate random save data
        std::string saveId = GenerateRandomSaveId();
        std::uniform_int_distribution<size_t> sizeDist(100, 5000);
        size_t saveSize = sizeDist(rng);
        std::vector<uint8_t> originalSaveData = GenerateRandomData(saveSize);
        
        // Test upload
        bool uploadResult = network->UploadSaveData(saveId, originalSaveData);
        EXPECT_TRUE(uploadResult)
            << "Save data upload should succeed";
        
        // Test download
        std::vector<uint8_t> downloadedSaveData;
        bool downloadResult = network->DownloadSaveData(saveId, downloadedSaveData);
        EXPECT_TRUE(downloadResult)
            << "Save data download should succeed";
        
        // Verify round-trip: downloaded data should match uploaded data
        EXPECT_EQ(downloadedSaveData.size(), originalSaveData.size())
            << "Downloaded save size should match uploaded size";
        
        EXPECT_EQ(downloadedSaveData, originalSaveData)
            << "Downloaded save data should match uploaded data (round-trip property)";
        
        // Test save list retrieval
        std::vector<std::string> saveList = network->GetCloudSaveList();
        EXPECT_GE(saveList.size(), 1u)
            << "Save list should contain at least the uploaded save";
        
        bool foundSave = std::find(saveList.begin(), saveList.end(), saveId) != saveList.end();
        EXPECT_TRUE(foundSave)
            << "Uploaded save should be in the save list";
        
        // Test synchronization
        bool syncResult = network->SynchronizeSaveData(saveId);
        EXPECT_TRUE(syncResult)
            << "Save synchronization should succeed for existing save";
        
        // Test deletion
        bool deleteResult = network->DeleteCloudSave(saveId);
        EXPECT_TRUE(deleteResult)
            << "Save deletion should succeed";
        
        // Verify save is deleted
        std::vector<std::string> saveListAfterDelete = network->GetCloudSaveList();
        bool stillExists = std::find(saveListAfterDelete.begin(), saveListAfterDelete.end(), 
                                     saveId) != saveListAfterDelete.end();
        EXPECT_FALSE(stillExists)
            << "Deleted save should not be in the save list";
        
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}

/**
 * Property 45: Cloud Save Synchronization - Empty Save ID Handling
 * For any empty save ID, operations should fail gracefully
 */
TEST_F(AdvancedNetworkPropertiesTest, CloudSaveEmptyIdHandling) {
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->EnableCloudSaves("TestProvider"));
    
    std::string emptySaveId = "";
    std::vector<uint8_t> saveData = GenerateRandomData(100);
    
    // Upload with empty ID should fail
    bool uploadResult = network->UploadSaveData(emptySaveId, saveData);
    EXPECT_FALSE(uploadResult)
        << "Upload with empty save ID should fail";
    
    // Download with empty ID should fail
    std::vector<uint8_t> downloadedData;
    bool downloadResult = network->DownloadSaveData(emptySaveId, downloadedData);
    EXPECT_FALSE(downloadResult)
        << "Download with empty save ID should fail";
    
    // Sync with empty ID should fail
    bool syncResult = network->SynchronizeSaveData(emptySaveId);
    EXPECT_FALSE(syncResult)
        << "Sync with empty save ID should fail";
    
    // Delete with empty ID should fail
    bool deleteResult = network->DeleteCloudSave(emptySaveId);
    EXPECT_FALSE(deleteResult)
        << "Delete with empty save ID should fail";
}

/**
 * Property 45: Cloud Save Synchronization - Empty Save Data Handling
 * For any empty save data, upload should fail
 */
TEST_F(AdvancedNetworkPropertiesTest, CloudSaveEmptyDataHandling) {
    const int NUM_ITERATIONS = 50;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->EnableCloudSaves("TestProvider"));
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        std::string saveId = GenerateRandomSaveId();
        std::vector<uint8_t> emptyData;
        
        // Upload with empty data should fail
        bool uploadResult = network->UploadSaveData(saveId, emptyData);
        EXPECT_FALSE(uploadResult)
            << "Upload with empty save data should fail";
    }
}

/**
 * Property 45: Cloud Save Synchronization - Non-existent Save Handling
 * For any non-existent save, download and sync should fail gracefully
 */
TEST_F(AdvancedNetworkPropertiesTest, CloudSaveNonExistentHandling) {
    const int NUM_ITERATIONS = 100;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->EnableCloudSaves("TestProvider"));
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate random non-existent save ID
        std::string nonExistentId = "nonexistent_" + std::to_string(i);
        
        // Download non-existent save should fail
        std::vector<uint8_t> downloadedData;
        bool downloadResult = network->DownloadSaveData(nonExistentId, downloadedData);
        EXPECT_FALSE(downloadResult)
            << "Download of non-existent save should fail";
        
        // Sync non-existent save should fail
        bool syncResult = network->SynchronizeSaveData(nonExistentId);
        EXPECT_FALSE(syncResult)
            << "Sync of non-existent save should fail";
        
        // Delete non-existent save should fail
        bool deleteResult = network->DeleteCloudSave(nonExistentId);
        EXPECT_FALSE(deleteResult)
            << "Delete of non-existent save should fail";
    }
}

/**
 * Property 45: Cloud Save Synchronization - Multiple Saves
 * For any number of saves, all should be managed correctly
 */
TEST_F(AdvancedNetworkPropertiesTest, CloudSaveMultipleSaves) {
    const int NUM_SAVES = 50;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->EnableCloudSaves("TestProvider"));
    
    std::vector<std::string> saveIds;
    std::vector<std::vector<uint8_t>> saveDatas;
    
    // Upload multiple saves
    for (int i = 0; i < NUM_SAVES; ++i) {
        std::string saveId = "save_" + std::to_string(i);
        std::vector<uint8_t> saveData = GenerateRandomData(100 + i * 10);
        
        bool uploadResult = network->UploadSaveData(saveId, saveData);
        EXPECT_TRUE(uploadResult);
        
        saveIds.push_back(saveId);
        saveDatas.push_back(saveData);
    }
    
    // Verify all saves are in the list
    std::vector<std::string> saveList = network->GetCloudSaveList();
    EXPECT_EQ(saveList.size(), NUM_SAVES);
    
    for (const auto& saveId : saveIds) {
        bool found = std::find(saveList.begin(), saveList.end(), saveId) != saveList.end();
        EXPECT_TRUE(found)
            << "Save " << saveId << " should be in the list";
    }
    
    // Download and verify each save
    for (size_t i = 0; i < saveIds.size(); ++i) {
        std::vector<uint8_t> downloadedData;
        bool downloadResult = network->DownloadSaveData(saveIds[i], downloadedData);
        EXPECT_TRUE(downloadResult);
        EXPECT_EQ(downloadedData, saveDatas[i])
            << "Downloaded data should match original for save " << saveIds[i];
    }
    
    // Delete all saves
    for (const auto& saveId : saveIds) {
        bool deleteResult = network->DeleteCloudSave(saveId);
        EXPECT_TRUE(deleteResult);
    }
    
    // Verify all saves are deleted
    std::vector<std::string> saveListAfterDelete = network->GetCloudSaveList();
    EXPECT_EQ(saveListAfterDelete.size(), 0u)
        << "All saves should be deleted";
}

/**
 * Property 45: Cloud Save Synchronization - Without Enabling Cloud Saves
 * For any cloud save operation without enabling cloud saves first, it should fail
 */
TEST_F(AdvancedNetworkPropertiesTest, CloudSaveWithoutEnabling) {
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    
    // Don't enable cloud saves
    
    std::string saveId = "test_save";
    std::vector<uint8_t> saveData = GenerateRandomData(100);
    
    // All operations should fail without enabling cloud saves
    bool uploadResult = network->UploadSaveData(saveId, saveData);
    EXPECT_FALSE(uploadResult)
        << "Upload should fail without enabling cloud saves";
    
    std::vector<uint8_t> downloadedData;
    bool downloadResult = network->DownloadSaveData(saveId, downloadedData);
    EXPECT_FALSE(downloadResult)
        << "Download should fail without enabling cloud saves";
    
    bool syncResult = network->SynchronizeSaveData(saveId);
    EXPECT_FALSE(syncResult)
        << "Sync should fail without enabling cloud saves";
    
    bool deleteResult = network->DeleteCloudSave(saveId);
    EXPECT_FALSE(deleteResult)
        << "Delete should fail without enabling cloud saves";
}
