#pragma once

#include <vector>
#include <memory>
#include <functional>
#include <unordered_map>
#include <queue>
#include <string>
#include <random>
#include <algorithm>

namespace pywrkgame {

// Forward declarations
struct Vector3 {
    float x, y, z;
    Vector3(float x = 0, float y = 0, float z = 0) : x(x), y(y), z(z) {}
    float Distance(const Vector3& other) const;
    Vector3 operator+(const Vector3& other) const;
    Vector3 operator-(const Vector3& other) const;
    Vector3 operator*(float scalar) const;
    float Length() const;
    Vector3 Normalized() const;
};

// Behavior Tree Node Types
enum class BehaviorNodeStatus {
    Success,
    Failure,
    Running
};

class BehaviorNode {
public:
    virtual ~BehaviorNode() = default;
    virtual BehaviorNodeStatus Execute() = 0;
    virtual void Reset() {}
};

// Composite Nodes
class SequenceNode : public BehaviorNode {
public:
    void AddChild(std::shared_ptr<BehaviorNode> child);
    BehaviorNodeStatus Execute() override;
    void Reset() override;

private:
    std::vector<std::shared_ptr<BehaviorNode>> children;
    size_t currentChild = 0;
};

class SelectorNode : public BehaviorNode {
public:
    void AddChild(std::shared_ptr<BehaviorNode> child);
    BehaviorNodeStatus Execute() override;
    void Reset() override;

private:
    std::vector<std::shared_ptr<BehaviorNode>> children;
    size_t currentChild = 0;
};

// Decorator Nodes
class InverterNode : public BehaviorNode {
public:
    explicit InverterNode(std::shared_ptr<BehaviorNode> child);
    BehaviorNodeStatus Execute() override;
    void Reset() override;

private:
    std::shared_ptr<BehaviorNode> child;
};

class RepeaterNode : public BehaviorNode {
public:
    RepeaterNode(std::shared_ptr<BehaviorNode> child, int maxRepeats = -1);
    BehaviorNodeStatus Execute() override;
    void Reset() override;

private:
    std::shared_ptr<BehaviorNode> child;
    int maxRepeats;
    int currentRepeats = 0;
};

// Leaf Nodes
class ActionNode : public BehaviorNode {
public:
    using ActionFunc = std::function<BehaviorNodeStatus()>;
    explicit ActionNode(ActionFunc action);
    BehaviorNodeStatus Execute() override;

private:
    ActionFunc action;
};

class ConditionNode : public BehaviorNode {
public:
    using ConditionFunc = std::function<bool()>;
    explicit ConditionNode(ConditionFunc condition);
    BehaviorNodeStatus Execute() override;

private:
    ConditionFunc condition;
};

// Behavior Tree
class BehaviorTree {
public:
    void SetRoot(std::shared_ptr<BehaviorNode> root);
    BehaviorNodeStatus Execute();
    void Reset();

private:
    std::shared_ptr<BehaviorNode> root;
};

// Pathfinding
struct PathNode {
    Vector3 position;
    float gCost = 0.0f;  // Cost from start
    float hCost = 0.0f;  // Heuristic cost to goal
    float fCost() const { return gCost + hCost; }
    PathNode* parent = nullptr;
    
    PathNode(const Vector3& pos) : position(pos) {}
};

struct NavMeshTriangle {
    Vector3 vertices[3];
    Vector3 center;
    std::vector<int> neighbors;
    
    NavMeshTriangle(const Vector3& v0, const Vector3& v1, const Vector3& v2);
    bool Contains(const Vector3& point) const;
};

class NavMesh {
public:
    void AddTriangle(const Vector3& v0, const Vector3& v1, const Vector3& v2);
    void BuildConnections();
    int FindTriangle(const Vector3& position) const;
    std::vector<int> GetNeighbors(int triangleIndex) const;
    Vector3 GetTriangleCenter(int triangleIndex) const;
    size_t GetTriangleCount() const { return triangles.size(); }

private:
    std::vector<NavMeshTriangle> triangles;
};

class Pathfinder {
public:
    // A* pathfinding on grid
    std::vector<Vector3> FindPathAStar(
        const Vector3& start,
        const Vector3& goal,
        std::function<bool(const Vector3&)> isWalkable,
        float gridSize = 1.0f
    );
    
    // NavMesh pathfinding
    std::vector<Vector3> FindPathNavMesh(
        const Vector3& start,
        const Vector3& goal,
        const NavMesh& navMesh
    );
    
    // Flow field pathfinding
    struct FlowField {
        std::unordered_map<int, Vector3> directions;
        float gridSize;
    };
    
    FlowField GenerateFlowField(
        const Vector3& goal,
        std::function<bool(const Vector3&)> isWalkable,
        float gridSize = 1.0f,
        float maxDistance = 100.0f
    );
    
    Vector3 GetFlowDirection(const FlowField& field, const Vector3& position);

private:
    float Heuristic(const Vector3& a, const Vector3& b);
    int PositionToKey(const Vector3& pos, float gridSize);
    Vector3 KeyToPosition(int key, float gridSize);
};

// Crowd Simulation
struct Agent {
    Vector3 position;
    Vector3 velocity;
    Vector3 desiredVelocity;
    float radius = 0.5f;
    float maxSpeed = 5.0f;
    float maxForce = 10.0f;
    int id = -1;
    
    Agent() = default;
    Agent(int id, const Vector3& pos) : id(id), position(pos) {}
};

class CrowdSimulation {
public:
    int AddAgent(const Vector3& position, float radius = 0.5f, float maxSpeed = 5.0f);
    void RemoveAgent(int agentId);
    void SetAgentGoal(int agentId, const Vector3& goal);
    void Update(float deltaTime);
    
    Vector3 GetAgentPosition(int agentId) const;
    Vector3 GetAgentVelocity(int agentId) const;
    size_t GetAgentCount() const { return agents.size(); }
    
    // Crowd behavior parameters
    void SetSeparationWeight(float weight) { separationWeight = weight; }
    void SetAlignmentWeight(float weight) { alignmentWeight = weight; }
    void SetCohesionWeight(float weight) { cohesionWeight = weight; }
    void SetAvoidanceRadius(float radius) { avoidanceRadius = radius; }

private:
    std::unordered_map<int, Agent> agents;
    std::unordered_map<int, Vector3> agentGoals;
    int nextAgentId = 0;
    
    // Crowd behavior parameters
    float separationWeight = 1.5f;
    float alignmentWeight = 1.0f;
    float cohesionWeight = 1.0f;
    float avoidanceRadius = 2.0f;
    
    Vector3 CalculateSeparation(const Agent& agent);
    Vector3 CalculateAlignment(const Agent& agent);
    Vector3 CalculateCohesion(const Agent& agent);
    Vector3 CalculateGoalSeeking(const Agent& agent);
    Vector3 CalculateAvoidance(const Agent& agent);
    std::vector<Agent*> GetNeighbors(const Agent& agent, float radius);
};

// AI Framework Manager
class AIFramework {
public:
    bool Initialize();
    void Shutdown();
    
    // Behavior Tree Management
    int CreateBehaviorTree();
    BehaviorTree* GetBehaviorTree(int treeId);
    void DestroyBehaviorTree(int treeId);
    
    // Pathfinding
    Pathfinder& GetPathfinder() { return pathfinder; }
    
    // NavMesh Management
    int CreateNavMesh();
    NavMesh* GetNavMesh(int navMeshId);
    void DestroyNavMesh(int navMeshId);
    
    // Crowd Simulation
    int CreateCrowdSimulation();
    CrowdSimulation* GetCrowdSimulation(int crowdId);
    void DestroyCrowdSimulation(int crowdId);
    
    void Update(float deltaTime);

private:
    std::unordered_map<int, std::unique_ptr<BehaviorTree>> behaviorTrees;
    std::unordered_map<int, std::unique_ptr<NavMesh>> navMeshes;
    std::unordered_map<int, std::unique_ptr<CrowdSimulation>> crowdSimulations;
    Pathfinder pathfinder;
    
    int nextTreeId = 0;
    int nextNavMeshId = 0;
    int nextCrowdId = 0;
    bool initialized = false;
};

// Machine Learning Integration
struct MLModel {
    std::string name;
    std::vector<float> weights;
    std::vector<float> biases;
    int inputSize;
    int outputSize;
    
    MLModel(const std::string& name, int inputSize, int outputSize);
    std::vector<float> Predict(const std::vector<float>& input);
    void Train(const std::vector<std::vector<float>>& inputs, 
               const std::vector<std::vector<float>>& outputs,
               int epochs = 100, float learningRate = 0.01f);
};

class AdaptiveAI {
public:
    void Initialize(int inputSize, int outputSize);
    std::vector<float> GetAction(const std::vector<float>& state);
    void UpdateFromExperience(const std::vector<float>& state, 
                             const std::vector<float>& action,
                             float reward);
    void SaveModel(const std::string& filepath);
    void LoadModel(const std::string& filepath);
    
private:
    std::unique_ptr<MLModel> model;
    std::vector<std::tuple<std::vector<float>, std::vector<float>, float>> experienceBuffer;
    int maxExperiences = 1000;
};

// Procedural Content Generation
enum class ContentType {
    Level,
    Quest,
    Item,
    Terrain,
    Dungeon
};

struct ProceduralLevel {
    int width;
    int height;
    std::vector<int> tiles; // Tile types
    std::vector<Vector3> spawnPoints;
    std::vector<Vector3> itemLocations;
    
    ProceduralLevel(int w, int h) : width(w), height(h), tiles(w * h, 0) {}
};

struct ProceduralQuest {
    std::string questType;
    std::string objective;
    std::vector<std::string> requirements;
    std::unordered_map<std::string, int> rewards;
    int difficulty;
    
    ProceduralQuest() : difficulty(1) {}
};

struct ProceduralItem {
    std::string name;
    std::string type;
    std::unordered_map<std::string, float> attributes;
    int rarity;
    
    ProceduralItem() : rarity(1) {}
};

class ProceduralGenerator {
public:
    void Initialize(unsigned int seed = 0);
    
    ProceduralLevel GenerateLevel(int width, int height, int difficulty);
    ProceduralQuest GenerateQuest(int difficulty, const std::string& questType = "");
    ProceduralItem GenerateItem(int level, const std::string& itemType = "");
    
    void SetSeed(unsigned int seed);
    unsigned int GetSeed() const { return currentSeed; }
    
private:
    unsigned int currentSeed;
    std::mt19937 rng;
    
    int RandomInt(int min, int max);
    float RandomFloat(float min, float max);
    std::string RandomQuestType();
    std::string RandomItemType();
};

// Natural Language Processing
struct DialogNode {
    std::string text;
    std::vector<int> responses;
    std::unordered_map<std::string, std::string> conditions;
    std::unordered_map<std::string, std::string> actions;
    
    DialogNode(const std::string& text) : text(text) {}
};

struct DialogResponse {
    std::string text;
    int nextNodeId;
    std::unordered_map<std::string, std::string> requirements;
    
    DialogResponse(const std::string& text, int nextId) : text(text), nextNodeId(nextId) {}
};

class DialogSystem {
public:
    int CreateDialogNode(const std::string& text);
    int CreateDialogResponse(const std::string& text, int nextNodeId);
    void AddResponseToNode(int nodeId, int responseId);
    void SetNodeCondition(int nodeId, const std::string& key, const std::string& value);
    void SetNodeAction(int nodeId, const std::string& key, const std::string& value);
    
    DialogNode* GetNode(int nodeId);
    DialogResponse* GetResponse(int responseId);
    std::vector<DialogResponse*> GetAvailableResponses(int nodeId);
    
private:
    std::unordered_map<int, DialogNode> nodes;
    std::unordered_map<int, DialogResponse> responses;
    int nextNodeId = 0;
    int nextResponseId = 0;
};

class NLPProcessor {
public:
    void Initialize();
    
    // Simple keyword-based intent recognition
    std::string RecognizeIntent(const std::string& input);
    
    // Extract entities from text
    std::unordered_map<std::string, std::string> ExtractEntities(const std::string& input);
    
    // Generate response based on intent and entities
    std::string GenerateResponse(const std::string& intent, 
                                const std::unordered_map<std::string, std::string>& entities);
    
    // Add training data
    void AddIntentExample(const std::string& intent, const std::string& example);
    
private:
    std::unordered_map<std::string, std::vector<std::string>> intentKeywords;
    std::unordered_map<std::string, std::vector<std::string>> responseTemplates;
    
    std::vector<std::string> Tokenize(const std::string& text);
    std::string ToLower(const std::string& text);
};

} // namespace pywrkgame
