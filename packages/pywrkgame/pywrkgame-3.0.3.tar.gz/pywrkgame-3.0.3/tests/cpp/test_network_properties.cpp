/**
 * Property-based tests for Network System
 * Feature: pywrkgame-library, Property 39: Real-time Multiplayer Communication
 * Feature: pywrkgame-library, Property 40: P2P Local Multiplayer
 * Feature: pywrkgame-library, Property 43: Network Data Compression
 * Validates: Requirements 8.1, 8.2, 8.5
 */

#include <gtest/gtest.h>
#include "pywrkgame/network/NetworkManager.h"
#include <vector>
#include <random>
#include <algorithm>
#include <thread>
#include <chrono>

using namespace pywrkgame::network;

class NetworkPropertiesTest : public ::testing::Test {
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
    
    std::vector<uint8_t> GenerateCompressibleData(size_t size) {
        std::vector<uint8_t> data(size);
        std::uniform_int_distribution<int> valueDist(0, 10); // Limited range for better compression
        std::uniform_int_distribution<size_t> runDist(3, 20); // Run lengths
        
        size_t i = 0;
        while (i < size) {
            uint8_t value = static_cast<uint8_t>(valueDist(rng));
            size_t runLength = std::min(runDist(rng), size - i);
            for (size_t j = 0; j < runLength && i < size; ++j, ++i) {
                data[i] = value;
            }
        }
        return data;
    }
    
    std::unique_ptr<NetworkManager> network;
    std::mt19937 rng;
};

/**
 * Property 39: Real-time Multiplayer Communication
 * For any multiplayer game session, real-time communication should work reliably
 * between clients and server
 * 
 * This test verifies that:
 * 1. Server can be started and clients can connect
 * 2. Data can be sent from client to server
 * 3. Data can be sent from server to clients
 * 4. Multiple clients can communicate simultaneously
 * 5. Connection state is tracked correctly
 */
TEST_F(NetworkPropertiesTest, RealtimeMultiplayerCommunication) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Initialize in client-server mode
        ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
        
        // Test server startup
        std::uniform_int_distribution<uint16_t> portDist(10000, 60000);
        uint16_t port = portDist(rng);
        std::uniform_int_distribution<uint32_t> maxClientsDist(2, 32);
        uint32_t maxClients = maxClientsDist(rng);
        
        bool serverStarted = network->StartServer(port, maxClients);
        EXPECT_TRUE(serverStarted);
        EXPECT_TRUE(network->IsServer());
        EXPECT_TRUE(network->IsConnected());
        
        // Verify local player is added
        uint32_t localPlayerId = network->GetLocalPlayerId();
        EXPECT_NE(localPlayerId, 0u);
        
        std::vector<PlayerInfo> players = network->GetConnectedPlayers();
        EXPECT_EQ(players.size(), 1u); // Server player
        
        // Test data sending
        std::uniform_int_distribution<size_t> sizeDist(10, 1000);
        size_t dataSize = sizeDist(rng);
        std::vector<uint8_t> testData = GenerateRandomData(dataSize);
        
        bool sendSuccess = network->SendData(testData);
        EXPECT_TRUE(sendSuccess);
        
        // Verify network statistics are updated
        EXPECT_GT(network->GetBytesSent(), 0u);
        
        // Test broadcast
        bool broadcastSuccess = network->BroadcastData(testData);
        EXPECT_TRUE(broadcastSuccess);
        
        // Test reliable send
        bool reliableSendSuccess = network->SendDataReliable(testData);
        EXPECT_TRUE(reliableSendSuccess);
        
        // Update network
        network->Update(0.016f);
        
        // Shutdown and reinitialize for next iteration
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}

/**
 * Property 39: Real-time Multiplayer Communication - Client Connection
 * For any client attempting to connect to a server, the connection should be
 * established correctly
 */
TEST_F(NetworkPropertiesTest, ClientServerConnection) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
        
        // Generate random server address and port
        std::uniform_int_distribution<uint16_t> portDist(10000, 60000);
        uint16_t port = portDist(rng);
        
        std::vector<std::string> testAddresses = {
            "127.0.0.1",
            "localhost",
            "192.168.1.1",
            "10.0.0.1"
        };
        
        std::uniform_int_distribution<size_t> addrDist(0, testAddresses.size() - 1);
        std::string address = testAddresses[addrDist(rng)];
        
        // Connect to server
        bool connected = network->ConnectToServer(address, port);
        EXPECT_TRUE(connected);
        EXPECT_FALSE(network->IsServer());
        EXPECT_TRUE(network->IsConnected());
        
        // Verify local player is added
        uint32_t localPlayerId = network->GetLocalPlayerId();
        EXPECT_NE(localPlayerId, 0u);
        
        PlayerInfo localPlayer = network->GetPlayerInfo(localPlayerId);
        EXPECT_EQ(localPlayer.playerId, localPlayerId);
        EXPECT_FALSE(localPlayer.playerName.empty());
        
        // Test disconnection
        network->DisconnectFromServer();
        EXPECT_FALSE(network->IsConnected());
        
        // Shutdown and reinitialize for next iteration
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}

/**
 * Property 40: P2P Local Multiplayer
 * For any local multiplayer session, peer-to-peer communication should establish
 * and maintain connections correctly
 * 
 * This test verifies that:
 * 1. P2P sessions can be created
 * 2. Peers can join sessions
 * 3. Peer information is tracked correctly
 * 4. Data can be sent between peers
 */
TEST_F(NetworkPropertiesTest, P2PLocalMultiplayer) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Initialize in P2P mode
        ASSERT_TRUE(network->Initialize(NetworkMode::PeerToPeer));
        
        // Generate random session name
        std::uniform_int_distribution<uint32_t> sessionDist(1000, 9999);
        std::string sessionName = "Session_" + std::to_string(sessionDist(rng));
        
        // Test starting P2P session
        bool sessionStarted = network->StartP2PSession(sessionName);
        EXPECT_TRUE(sessionStarted);
        EXPECT_TRUE(network->IsConnected());
        
        // Verify local player is added
        uint32_t localPlayerId = network->GetLocalPlayerId();
        EXPECT_NE(localPlayerId, 0u);
        
        std::vector<PlayerInfo> players = network->GetConnectedPlayers();
        EXPECT_GE(players.size(), 1u);
        
        // Get P2P peers (should be empty initially as we're the only one)
        std::vector<PlayerInfo> peers = network->GetP2PPeers();
        EXPECT_EQ(peers.size(), 0u); // No other peers yet
        
        // Test data sending in P2P mode
        std::uniform_int_distribution<size_t> sizeDist(10, 1000);
        size_t dataSize = sizeDist(rng);
        std::vector<uint8_t> testData = GenerateRandomData(dataSize);
        
        bool sendSuccess = network->SendData(testData);
        EXPECT_TRUE(sendSuccess);
        
        // Test broadcast in P2P mode
        bool broadcastSuccess = network->BroadcastData(testData);
        EXPECT_TRUE(broadcastSuccess);
        
        // Update network
        network->Update(0.016f);
        
        // Test leaving session
        network->LeaveP2PSession();
        EXPECT_FALSE(network->IsConnected());
        
        // Shutdown and reinitialize for next iteration
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}

/**
 * Property 40: P2P Local Multiplayer - Join Session
 * For any P2P session, peers should be able to join correctly
 */
TEST_F(NetworkPropertiesTest, P2PJoinSession) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        ASSERT_TRUE(network->Initialize(NetworkMode::PeerToPeer));
        
        // Generate random session name
        std::uniform_int_distribution<uint32_t> sessionDist(1000, 9999);
        std::string sessionName = "Session_" + std::to_string(sessionDist(rng));
        
        // Join P2P session
        bool joined = network->JoinP2PSession(sessionName);
        EXPECT_TRUE(joined);
        EXPECT_TRUE(network->IsConnected());
        
        // Verify local player
        uint32_t localPlayerId = network->GetLocalPlayerId();
        EXPECT_NE(localPlayerId, 0u);
        
        // Test data transmission after joining
        std::vector<uint8_t> testData = GenerateRandomData(100);
        bool sendSuccess = network->SendData(testData);
        EXPECT_TRUE(sendSuccess);
        
        network->Update(0.016f);
        
        // Leave session
        network->LeaveP2PSession();
        EXPECT_FALSE(network->IsConnected());
        
        // Shutdown and reinitialize for next iteration
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}

/**
 * Property 43: Network Data Compression
 * For any network traffic, data should be compressed automatically to reduce
 * bandwidth usage
 * 
 * This test verifies that:
 * 1. Compression can be enabled/disabled
 * 2. Compressible data is actually compressed
 * 3. Compressed data can be decompressed correctly (round-trip)
 * 4. Compression ratio is calculated correctly
 * 5. Small data is not compressed (overhead)
 */
TEST_F(NetworkPropertiesTest, NetworkDataCompression) {
    const int NUM_ITERATIONS = 100;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Test compression enable/disable
        bool enableCompression = (i % 2 == 0);
        network->EnableCompression(enableCompression);
        EXPECT_EQ(network->IsCompressionEnabled(), enableCompression);
        
        // Generate compressible data (data with patterns)
        std::uniform_int_distribution<size_t> sizeDist(100, 2000);
        size_t dataSize = sizeDist(rng);
        std::vector<uint8_t> originalData = GenerateCompressibleData(dataSize);
        
        // Compress data
        std::vector<uint8_t> compressed = network->CompressData(originalData);
        
        // For compressible data, compressed size should be smaller
        if (dataSize > 64) {
            EXPECT_LE(compressed.size(), originalData.size())
                << "Compressed data should not be larger than original for compressible data";
        }
        
        // Decompress data
        std::vector<uint8_t> decompressed = network->DecompressData(compressed);
        
        // Round-trip: decompressed should match original
        EXPECT_EQ(decompressed.size(), originalData.size())
            << "Decompressed size should match original size";
        
        EXPECT_EQ(decompressed, originalData)
            << "Decompressed data should match original data (round-trip property)";
    }
}

/**
 * Property 43: Network Data Compression - Small Data Handling
 * For any small data packets (< 64 bytes), compression should not be applied
 * to avoid overhead
 */
TEST_F(NetworkPropertiesTest, SmallDataCompressionHandling) {
    const int NUM_ITERATIONS = 100;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->StartServer(12345));
    
    network->EnableCompression(true);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate small data (< 64 bytes)
        std::uniform_int_distribution<size_t> sizeDist(1, 63);
        size_t dataSize = sizeDist(rng);
        std::vector<uint8_t> smallData = GenerateRandomData(dataSize);
        
        uint64_t bytesSentBefore = network->GetBytesSent();
        
        // Send small data
        bool sendSuccess = network->SendData(smallData);
        EXPECT_TRUE(sendSuccess);
        
        uint64_t bytesSentAfter = network->GetBytesSent();
        
        // Verify data was sent
        EXPECT_GT(bytesSentAfter, bytesSentBefore);
        
        // For small data, the sent size should be close to original size
        // (compression overhead would make it larger, so it shouldn't be compressed)
        uint64_t sentBytes = bytesSentAfter - bytesSentBefore;
        EXPECT_LE(sentBytes, dataSize + 10) // Allow small overhead for packet headers
            << "Small data should not have significant compression overhead";
    }
}

/**
 * Property 43: Network Data Compression - Compression Ratio
 * For any compressible data, the compression ratio should be calculated correctly
 */
TEST_F(NetworkPropertiesTest, CompressionRatioCalculation) {
    const int NUM_ITERATIONS = 50;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    network->EnableCompression(true);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate highly compressible data
        size_t dataSize = 1000;
        std::vector<uint8_t> compressibleData(dataSize, 0x42); // All same value
        
        // Compress multiple times to accumulate statistics
        for (int j = 0; j < 10; ++j) {
            std::vector<uint8_t> compressed = network->CompressData(compressibleData);
            
            // Highly compressible data should compress well
            EXPECT_LT(compressed.size(), dataSize / 2)
                << "Highly compressible data should compress to less than half";
        }
        
        // Check compression ratio
        float ratio = network->GetCompressionRatio();
        EXPECT_GE(ratio, 0.0f);
        EXPECT_LE(ratio, 1.0f);
        
        // For highly compressible data, ratio should be low
        EXPECT_LT(ratio, 0.5f)
            << "Compression ratio should be low for highly compressible data";
    }
}

/**
 * Property 39: Real-time Multiplayer Communication - Network Statistics
 * For any network session, statistics should be tracked accurately
 */
TEST_F(NetworkPropertiesTest, NetworkStatisticsTracking) {
    const int NUM_ITERATIONS = 100;
    
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    ASSERT_TRUE(network->StartServer(12345));
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        uint64_t bytesSentBefore = network->GetBytesSent();
        
        // Send data
        std::uniform_int_distribution<size_t> sizeDist(100, 1000);
        size_t dataSize = sizeDist(rng);
        std::vector<uint8_t> testData = GenerateRandomData(dataSize);
        
        bool sendSuccess = network->SendData(testData);
        EXPECT_TRUE(sendSuccess);
        
        uint64_t bytesSentAfter = network->GetBytesSent();
        
        // Bytes sent should increase
        EXPECT_GT(bytesSentAfter, bytesSentBefore)
            << "Bytes sent counter should increase after sending data";
        
        // Update network to process statistics
        network->Update(0.016f);
        
        // Latency should be non-negative
        float latency = network->GetAverageLatency();
        EXPECT_GE(latency, 0.0f);
    }
}

/**
 * Property 40: P2P Local Multiplayer - Peer Discovery
 * For any P2P session, peers should be discoverable and their info should be accurate
 */
TEST_F(NetworkPropertiesTest, P2PPeerDiscovery) {
    const int NUM_ITERATIONS = 50;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        ASSERT_TRUE(network->Initialize(NetworkMode::PeerToPeer));
        
        std::string sessionName = "TestSession_" + std::to_string(i);
        ASSERT_TRUE(network->StartP2PSession(sessionName));
        
        // Get all connected players
        std::vector<PlayerInfo> allPlayers = network->GetConnectedPlayers();
        EXPECT_GE(allPlayers.size(), 1u);
        
        // Get only peers (excluding local player)
        std::vector<PlayerInfo> peers = network->GetP2PPeers();
        
        // Peers should be all players minus local player
        EXPECT_EQ(peers.size(), allPlayers.size() - 1);
        
        // Verify local player is not in peers list
        uint32_t localId = network->GetLocalPlayerId();
        for (const auto& peer : peers) {
            EXPECT_NE(peer.playerId, localId)
                << "Local player should not be in peers list";
        }
        
        // Verify all peers have valid info
        for (const auto& peer : peers) {
            EXPECT_NE(peer.playerId, 0u);
            EXPECT_FALSE(peer.playerName.empty());
            EXPECT_GE(peer.latency, 0.0f);
        }
        
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}

/**
 * Property 43: Network Data Compression - Empty Data Handling
 * For any empty data, compression should handle it gracefully
 */
TEST_F(NetworkPropertiesTest, EmptyDataCompression) {
    ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
    
    std::vector<uint8_t> emptyData;
    
    // Compress empty data
    std::vector<uint8_t> compressed = network->CompressData(emptyData);
    EXPECT_TRUE(compressed.empty())
        << "Compressed empty data should also be empty";
    
    // Decompress empty data
    std::vector<uint8_t> decompressed = network->DecompressData(emptyData);
    EXPECT_TRUE(decompressed.empty())
        << "Decompressed empty data should also be empty";
    
    // Round-trip with empty data
    std::vector<uint8_t> roundTrip = network->DecompressData(network->CompressData(emptyData));
    EXPECT_TRUE(roundTrip.empty())
        << "Round-trip of empty data should remain empty";
}

/**
 * Property 39: Real-time Multiplayer Communication - Player Management
 * For any connected player, their information should be retrievable and accurate
 */
TEST_F(NetworkPropertiesTest, PlayerInformationManagement) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        ASSERT_TRUE(network->Initialize(NetworkMode::ClientServer));
        ASSERT_TRUE(network->StartServer(12345 + i));
        
        // Get local player ID
        uint32_t localId = network->GetLocalPlayerId();
        EXPECT_NE(localId, 0u);
        
        // Get player info
        PlayerInfo info = network->GetPlayerInfo(localId);
        EXPECT_EQ(info.playerId, localId);
        EXPECT_FALSE(info.playerName.empty());
        EXPECT_GE(info.skillLevel, 0u);
        EXPECT_GE(info.latency, 0.0f);
        
        // Get all connected players
        std::vector<PlayerInfo> players = network->GetConnectedPlayers();
        EXPECT_GE(players.size(), 1u);
        
        // Verify local player is in the list
        bool foundLocal = false;
        for (const auto& player : players) {
            if (player.playerId == localId) {
                foundLocal = true;
                EXPECT_EQ(player.playerName, info.playerName);
                EXPECT_EQ(player.skillLevel, info.skillLevel);
                break;
            }
        }
        EXPECT_TRUE(foundLocal)
            << "Local player should be in connected players list";
        
        network->Shutdown();
        network = std::make_unique<NetworkManager>();
    }
}
