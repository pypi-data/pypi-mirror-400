#include "pywrkgame/network/NetworkManager.h"
#include <algorithm>
#include <random>
#include <cstring>

namespace pywrkgame {
namespace network {

NetworkManager::NetworkManager() = default;

NetworkManager::~NetworkManager() {
    if (initialized) {
        Shutdown();
    }
}

bool NetworkManager::Initialize(NetworkMode mode) {
    if (initialized) {
        return false;
    }
    
    currentMode = mode;
    localPlayerId = GeneratePlayerId();
    initialized = true;
    
    return true;
}

void NetworkManager::Shutdown() {
    if (!initialized) return;
    
    if (isConnected) {
        DisconnectFromServer();
    }
    
    if (isMatchmaking) {
        StopMatchmaking();
    }
    
    connectedPlayers.clear();
    availableMatches.clear();
    
    initialized = false;
}

void NetworkManager::Update(float deltaTime) {
    if (!initialized) return;
    
    ProcessIncomingPackets();
    UpdateNetworkStatistics(deltaTime);
}

// Client-Server Architecture
bool NetworkManager::StartServer(uint16_t port, uint32_t maxClients) {
    if (!initialized || isServer) {
        return false;
    }
    
    serverPort = port;
    isServer = true;
    isConnected = true;
    
    // Add local player as server
    PlayerInfo serverPlayer;
    serverPlayer.playerId = localPlayerId;
    serverPlayer.playerName = "Server";
    serverPlayer.skillLevel = 0;
    serverPlayer.latency = 0.0f;
    connectedPlayers[localPlayerId] = serverPlayer;
    
    NotifyEvent(NetworkEvent::Connected, localPlayerId);
    
    return true;
}

bool NetworkManager::ConnectToServer(const std::string& address, uint16_t port) {
    if (!initialized || isConnected) {
        return false;
    }
    
    serverAddress = address;
    serverPort = port;
    isConnected = true;
    
    // Add local player
    PlayerInfo localPlayer;
    localPlayer.playerId = localPlayerId;
    localPlayer.playerName = "Player_" + std::to_string(localPlayerId);
    localPlayer.skillLevel = 1000;
    localPlayer.latency = 0.0f;
    connectedPlayers[localPlayerId] = localPlayer;
    
    NotifyEvent(NetworkEvent::Connected, localPlayerId);
    
    return true;
}

void NetworkManager::DisconnectFromServer() {
    if (!initialized || !isConnected) return;
    
    NotifyEvent(NetworkEvent::Disconnected, localPlayerId);
    
    isConnected = false;
    isServer = false;
    connectedPlayers.clear();
}

// Peer-to-Peer Networking
bool NetworkManager::StartP2PSession(const std::string& sessionName) {
    if (!initialized || currentMode != NetworkMode::PeerToPeer) {
        return false;
    }
    
    isConnected = true;
    
    // Add local player
    PlayerInfo localPlayer;
    localPlayer.playerId = localPlayerId;
    localPlayer.playerName = "Player_" + std::to_string(localPlayerId);
    localPlayer.skillLevel = 1000;
    localPlayer.latency = 0.0f;
    connectedPlayers[localPlayerId] = localPlayer;
    
    NotifyEvent(NetworkEvent::Connected, localPlayerId);
    
    return true;
}

bool NetworkManager::JoinP2PSession(const std::string& sessionName) {
    if (!initialized || currentMode != NetworkMode::PeerToPeer) {
        return false;
    }
    
    isConnected = true;
    
    // Add local player
    PlayerInfo localPlayer;
    localPlayer.playerId = localPlayerId;
    localPlayer.playerName = "Player_" + std::to_string(localPlayerId);
    localPlayer.skillLevel = 1000;
    localPlayer.latency = 0.0f;
    connectedPlayers[localPlayerId] = localPlayer;
    
    NotifyEvent(NetworkEvent::Connected, localPlayerId);
    
    return true;
}

void NetworkManager::LeaveP2PSession() {
    if (!initialized || !isConnected) return;
    
    NotifyEvent(NetworkEvent::Disconnected, localPlayerId);
    
    isConnected = false;
    connectedPlayers.clear();
}

std::vector<PlayerInfo> NetworkManager::GetP2PPeers() const {
    std::vector<PlayerInfo> peers;
    for (const auto& pair : connectedPlayers) {
        if (pair.first != localPlayerId) {
            peers.push_back(pair.second);
        }
    }
    return peers;
}

// Data transmission
bool NetworkManager::SendData(const std::vector<uint8_t>& data, uint32_t recipientId) {
    if (!initialized || !isConnected) {
        return false;
    }
    
    std::vector<uint8_t> finalData = data;
    
    // Apply compression if enabled
    if (compressionEnabled && data.size() > 64) {
        finalData = CompressData(data);
    }
    
    bytesSent += finalData.size();
    
    // Create packet
    NetworkPacket packet;
    packet.senderId = localPlayerId;
    packet.recipientId = recipientId;
    packet.data = finalData;
    packet.timestamp = static_cast<uint32_t>(bytesSent); // Simple timestamp
    packet.compressed = compressionEnabled && data.size() > 64;
    
    // Simulate sending (in real implementation, this would use actual networking)
    
    return true;
}

bool NetworkManager::SendDataReliable(const std::vector<uint8_t>& data, uint32_t recipientId) {
    // For now, same as SendData but would use TCP or reliable UDP in real implementation
    return SendData(data, recipientId);
}

bool NetworkManager::BroadcastData(const std::vector<uint8_t>& data) {
    return SendData(data, 0); // 0 means broadcast
}

// Automatic data compression
std::vector<uint8_t> NetworkManager::CompressData(const std::vector<uint8_t>& data) {
    if (data.empty()) {
        return data;
    }
    
    // Simple run-length encoding for demonstration
    std::vector<uint8_t> compressed;
    compressed.reserve(data.size());
    
    size_t i = 0;
    while (i < data.size()) {
        uint8_t current = data[i];
        size_t count = 1;
        
        // Count consecutive identical bytes
        while (i + count < data.size() && data[i + count] == current && count < 255) {
            count++;
        }
        
        if (count > 2) {
            // Use RLE for runs of 3 or more
            compressed.push_back(0xFF); // Marker for RLE
            compressed.push_back(static_cast<uint8_t>(count));
            compressed.push_back(current);
            i += count;
        } else {
            // Store literal
            compressed.push_back(current);
            i++;
        }
    }
    
    bytesUncompressed += data.size();
    bytesCompressed += compressed.size();
    
    return compressed;
}

std::vector<uint8_t> NetworkManager::DecompressData(const std::vector<uint8_t>& data) {
    if (data.empty()) {
        return data;
    }
    
    std::vector<uint8_t> decompressed;
    decompressed.reserve(data.size() * 2);
    
    size_t i = 0;
    while (i < data.size()) {
        if (data[i] == 0xFF && i + 2 < data.size()) {
            // RLE sequence
            uint8_t count = data[i + 1];
            uint8_t value = data[i + 2];
            for (uint8_t j = 0; j < count; j++) {
                decompressed.push_back(value);
            }
            i += 3;
        } else {
            // Literal byte
            decompressed.push_back(data[i]);
            i++;
        }
    }
    
    return decompressed;
}

// Matchmaking system
bool NetworkManager::StartMatchmaking(uint32_t playerSkillLevel) {
    if (!initialized || isMatchmaking) {
        return false;
    }
    
    isMatchmaking = true;
    
    // Update local player skill level
    if (connectedPlayers.find(localPlayerId) != connectedPlayers.end()) {
        connectedPlayers[localPlayerId].skillLevel = playerSkillLevel;
    }
    
    // Simulate finding matches (in real implementation, this would query a matchmaking server)
    availableMatches.clear();
    
    // Create some sample matches
    for (uint32_t i = 0; i < 3; i++) {
        MatchInfo match;
        match.matchId = 1000 + i;
        match.matchName = "Match_" + std::to_string(match.matchId);
        match.maxPlayers = 8;
        match.currentPlayers = 2 + (i * 2);
        match.averageSkillLevel = playerSkillLevel + (i * 100) - 100;
        availableMatches.push_back(match);
    }
    
    return true;
}

void NetworkManager::StopMatchmaking() {
    if (!initialized) return;
    isMatchmaking = false;
    availableMatches.clear();
}

std::vector<MatchInfo> NetworkManager::GetAvailableMatches() const {
    return availableMatches;
}

bool NetworkManager::JoinMatch(uint32_t matchId) {
    if (!initialized || !isMatchmaking) {
        return false;
    }
    
    // Find the match
    auto it = std::find_if(availableMatches.begin(), availableMatches.end(),
        [matchId](const MatchInfo& match) { return match.matchId == matchId; });
    
    if (it == availableMatches.end()) {
        return false;
    }
    
    // Join the match
    isMatchmaking = false;
    isConnected = true;
    
    // Simulate adding other players
    for (uint32_t i = 0; i < it->currentPlayers; i++) {
        uint32_t playerId = GeneratePlayerId();
        PlayerInfo player;
        player.playerId = playerId;
        player.playerName = "Player_" + std::to_string(playerId);
        player.skillLevel = it->averageSkillLevel;
        player.latency = 50.0f + (i * 10.0f);
        connectedPlayers[playerId] = player;
    }
    
    return true;
}

void NetworkManager::LeaveMatch() {
    if (!initialized) return;
    
    DisconnectFromServer();
}

// Player management
std::vector<PlayerInfo> NetworkManager::GetConnectedPlayers() const {
    std::vector<PlayerInfo> players;
    for (const auto& pair : connectedPlayers) {
        players.push_back(pair.second);
    }
    return players;
}

PlayerInfo NetworkManager::GetPlayerInfo(uint32_t playerId) const {
    auto it = connectedPlayers.find(playerId);
    if (it != connectedPlayers.end()) {
        return it->second;
    }
    return PlayerInfo{};
}

// Network statistics
float NetworkManager::GetCompressionRatio() const {
    if (bytesUncompressed == 0) {
        return 1.0f;
    }
    return static_cast<float>(bytesCompressed) / static_cast<float>(bytesUncompressed);
}

// Internal methods
void NetworkManager::ProcessIncomingPackets() {
    // In a real implementation, this would process incoming network packets
    // For now, this is a placeholder
}

void NetworkManager::UpdateNetworkStatistics(float deltaTime) {
    // Update average latency
    if (!connectedPlayers.empty()) {
        float totalLatency = 0.0f;
        for (const auto& pair : connectedPlayers) {
            totalLatency += pair.second.latency;
        }
        averageLatency = totalLatency / connectedPlayers.size();
    }
}

uint32_t NetworkManager::GeneratePlayerId() {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_int_distribution<uint32_t> dis(1, 0xFFFFFFFF);
    return dis(gen);
}

void NetworkManager::NotifyEvent(NetworkEvent event, uint32_t playerId) {
    if (eventCallback) {
        eventCallback(event, playerId);
    }
}

// Advanced networking features

// Lag compensation and prediction
void NetworkManager::RewindGameState(float timeOffset) {
    if (!initialized || !lagCompensationEnabled) return;
    
    // In a real implementation, this would rewind the game state to compensate for lag
    // For now, this is a placeholder that validates the time offset
    if (timeOffset < 0.0f || timeOffset > 1.0f) {
        return; // Invalid time offset
    }
    
    // Simulate state rewind by adjusting latency
    averageLatency = std::max(0.0f, averageLatency - timeOffset * 1000.0f);
}

void NetworkManager::PredictClientMovement(uint32_t playerId, float deltaTime) {
    if (!initialized || !clientPredictionEnabled) return;
    
    // In a real implementation, this would predict client movement based on velocity
    // For now, this validates the player exists
    auto it = connectedPlayers.find(playerId);
    if (it == connectedPlayers.end()) {
        return;
    }
    
    // Simulate prediction by updating latency estimate
    it->second.latency = std::max(0.0f, it->second.latency - deltaTime * 10.0f);
}

// Anti-cheat protection
bool NetworkManager::ValidatePlayerAction(uint32_t playerId, const std::vector<uint8_t>& actionData) {
    if (!initialized || !antiCheatEnabled) {
        return true; // Pass through if anti-cheat is disabled
    }
    
    // Check if player exists
    auto it = connectedPlayers.find(playerId);
    if (it == connectedPlayers.end()) {
        return false;
    }
    
    // Simple validation: check if action data is reasonable size
    if (actionData.empty() || actionData.size() > 10000) {
        ReportSuspiciousActivity(playerId, "Invalid action data size");
        return false;
    }
    
    // Check for suspicious patterns (e.g., too many actions in short time)
    // In a real implementation, this would be more sophisticated
    
    return true;
}

void NetworkManager::ReportSuspiciousActivity(uint32_t playerId, const std::string& reason) {
    if (!initialized || !antiCheatEnabled) return;
    
    // Increment suspicious activity count
    suspiciousActivityCount[playerId]++;
    
    // Flag player if they have too many suspicious activities
    if (suspiciousActivityCount[playerId] >= 3) {
        auto it = std::find(flaggedPlayers.begin(), flaggedPlayers.end(), playerId);
        if (it == flaggedPlayers.end()) {
            flaggedPlayers.push_back(playerId);
        }
    }
}

std::vector<uint32_t> NetworkManager::GetFlaggedPlayers() const {
    return flaggedPlayers;
}

// Cloud save synchronization
bool NetworkManager::EnableCloudSaves(const std::string& provider) {
    if (!initialized) {
        return false;
    }
    
    cloudProvider = provider;
    return true;
}

bool NetworkManager::UploadSaveData(const std::string& saveId, const std::vector<uint8_t>& saveData) {
    if (!initialized || cloudProvider.empty()) {
        return false;
    }
    
    if (saveId.empty() || saveData.empty()) {
        return false;
    }
    
    // Store save data in cloud storage (simulated)
    cloudSaves[saveId] = saveData;
    
    return true;
}

bool NetworkManager::DownloadSaveData(const std::string& saveId, std::vector<uint8_t>& saveData) {
    if (!initialized || cloudProvider.empty()) {
        return false;
    }
    
    if (saveId.empty()) {
        return false;
    }
    
    // Retrieve save data from cloud storage
    auto it = cloudSaves.find(saveId);
    if (it == cloudSaves.end()) {
        return false;
    }
    
    saveData = it->second;
    return true;
}

bool NetworkManager::SynchronizeSaveData(const std::string& saveId) {
    if (!initialized || cloudProvider.empty()) {
        return false;
    }
    
    if (saveId.empty()) {
        return false;
    }
    
    // In a real implementation, this would sync local and cloud saves
    // For now, we just verify the save exists
    auto it = cloudSaves.find(saveId);
    return it != cloudSaves.end();
}

std::vector<std::string> NetworkManager::GetCloudSaveList() const {
    std::vector<std::string> saveList;
    for (const auto& pair : cloudSaves) {
        saveList.push_back(pair.first);
    }
    return saveList;
}

bool NetworkManager::DeleteCloudSave(const std::string& saveId) {
    if (!initialized || cloudProvider.empty()) {
        return false;
    }
    
    if (saveId.empty()) {
        return false;
    }
    
    auto it = cloudSaves.find(saveId);
    if (it == cloudSaves.end()) {
        return false;
    }
    
    cloudSaves.erase(it);
    return true;
}

} // namespace network
} // namespace pywrkgame