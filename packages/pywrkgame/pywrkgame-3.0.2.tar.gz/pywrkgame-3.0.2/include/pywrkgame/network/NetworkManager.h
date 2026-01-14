#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <unordered_map>
#include <cstdint>

namespace pywrkgame {
namespace network {

// Network architecture types
enum class NetworkMode {
    ClientServer,
    PeerToPeer,
    Offline
};

// Connection types
enum class ConnectionType {
    TCP,
    UDP,
    WebSocket
};

// Network events
enum class NetworkEvent {
    Connected,
    Disconnected,
    DataReceived,
    Error
};

// Player info structure
struct PlayerInfo {
    uint32_t playerId;
    std::string playerName;
    uint32_t skillLevel;
    float latency;
};

// Match info structure
struct MatchInfo {
    uint32_t matchId;
    std::string matchName;
    uint32_t maxPlayers;
    uint32_t currentPlayers;
    uint32_t averageSkillLevel;
};

// Network packet structure
struct NetworkPacket {
    uint32_t senderId;
    uint32_t recipientId; // 0 for broadcast
    std::vector<uint8_t> data;
    uint32_t timestamp;
    bool compressed;
};

// Callback types
using NetworkEventCallback = std::function<void(NetworkEvent, uint32_t playerId)>;
using DataReceivedCallback = std::function<void(const NetworkPacket&)>;

class NetworkManager {
public:
    NetworkManager();
    ~NetworkManager();

    // Core initialization
    bool Initialize(NetworkMode mode = NetworkMode::ClientServer);
    void Shutdown();
    void Update(float deltaTime);

    // Client-Server Architecture
    bool StartServer(uint16_t port, uint32_t maxClients = 32);
    bool ConnectToServer(const std::string& address, uint16_t port);
    void DisconnectFromServer();
    bool IsServer() const { return isServer; }
    bool IsConnected() const { return isConnected; }

    // Peer-to-Peer Networking
    bool StartP2PSession(const std::string& sessionName);
    bool JoinP2PSession(const std::string& sessionName);
    void LeaveP2PSession();
    std::vector<PlayerInfo> GetP2PPeers() const;

    // Data transmission
    bool SendData(const std::vector<uint8_t>& data, uint32_t recipientId = 0);
    bool SendDataReliable(const std::vector<uint8_t>& data, uint32_t recipientId = 0);
    bool BroadcastData(const std::vector<uint8_t>& data);

    // Automatic data compression
    void EnableCompression(bool enable) { compressionEnabled = enable; }
    bool IsCompressionEnabled() const { return compressionEnabled; }
    std::vector<uint8_t> CompressData(const std::vector<uint8_t>& data);
    std::vector<uint8_t> DecompressData(const std::vector<uint8_t>& data);

    // Matchmaking system
    bool StartMatchmaking(uint32_t playerSkillLevel);
    void StopMatchmaking();
    bool IsMatchmaking() const { return isMatchmaking; }
    std::vector<MatchInfo> GetAvailableMatches() const;
    bool JoinMatch(uint32_t matchId);
    void LeaveMatch();

    // Player management
    uint32_t GetLocalPlayerId() const { return localPlayerId; }
    std::vector<PlayerInfo> GetConnectedPlayers() const;
    PlayerInfo GetPlayerInfo(uint32_t playerId) const;

    // Network statistics
    float GetAverageLatency() const { return averageLatency; }
    uint64_t GetBytesSent() const { return bytesSent; }
    uint64_t GetBytesReceived() const { return bytesReceived; }
    float GetCompressionRatio() const;

    // Event callbacks
    void SetEventCallback(NetworkEventCallback callback) { eventCallback = callback; }
    void SetDataReceivedCallback(DataReceivedCallback callback) { dataCallback = callback; }

    // Advanced networking features
    
    // Lag compensation and prediction
    void EnableLagCompensation(bool enable) { lagCompensationEnabled = enable; }
    bool IsLagCompensationEnabled() const { return lagCompensationEnabled; }
    void SetClientPrediction(bool enable) { clientPredictionEnabled = enable; }
    bool IsClientPredictionEnabled() const { return clientPredictionEnabled; }
    void RewindGameState(float timeOffset); // Rewind to compensate for lag
    void PredictClientMovement(uint32_t playerId, float deltaTime);
    
    // Anti-cheat protection
    void EnableAntiCheat(bool enable) { antiCheatEnabled = enable; }
    bool IsAntiCheatEnabled() const { return antiCheatEnabled; }
    bool ValidatePlayerAction(uint32_t playerId, const std::vector<uint8_t>& actionData);
    void ReportSuspiciousActivity(uint32_t playerId, const std::string& reason);
    std::vector<uint32_t> GetFlaggedPlayers() const;
    
    // Cloud save synchronization
    bool EnableCloudSaves(const std::string& cloudProvider);
    bool UploadSaveData(const std::string& saveId, const std::vector<uint8_t>& saveData);
    bool DownloadSaveData(const std::string& saveId, std::vector<uint8_t>& saveData);
    bool SynchronizeSaveData(const std::string& saveId);
    std::vector<std::string> GetCloudSaveList() const;
    bool DeleteCloudSave(const std::string& saveId);

private:
    bool initialized = false;
    NetworkMode currentMode = NetworkMode::Offline;
    bool isServer = false;
    bool isConnected = false;
    bool compressionEnabled = true;
    bool isMatchmaking = false;

    // Advanced features flags
    bool lagCompensationEnabled = true;
    bool clientPredictionEnabled = true;
    bool antiCheatEnabled = true;
    std::string cloudProvider;

    uint32_t localPlayerId = 0;
    std::string serverAddress;
    uint16_t serverPort = 0;

    // Network statistics
    float averageLatency = 0.0f;
    uint64_t bytesSent = 0;
    uint64_t bytesReceived = 0;
    uint64_t bytesCompressed = 0;
    uint64_t bytesUncompressed = 0;

    // Connected players
    std::unordered_map<uint32_t, PlayerInfo> connectedPlayers;
    std::vector<MatchInfo> availableMatches;

    // Anti-cheat data
    std::vector<uint32_t> flaggedPlayers;
    std::unordered_map<uint32_t, uint32_t> suspiciousActivityCount;

    // Cloud save data
    std::unordered_map<std::string, std::vector<uint8_t>> cloudSaves;

    // Callbacks
    NetworkEventCallback eventCallback;
    DataReceivedCallback dataCallback;

    // Internal methods
    void ProcessIncomingPackets();
    void UpdateNetworkStatistics(float deltaTime);
    uint32_t GeneratePlayerId();
    void NotifyEvent(NetworkEvent event, uint32_t playerId);
};

} // namespace network
} // namespace pywrkgame