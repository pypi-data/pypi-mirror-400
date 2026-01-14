#include "pywrkgame/ai/AIFramework.h"
#include <cmath>
#include <algorithm>
#include <set>
#include <limits>

namespace pywrkgame {

// Vector3 implementation
float Vector3::Distance(const Vector3& other) const {
    float dx = x - other.x;
    float dy = y - other.y;
    float dz = z - other.z;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

Vector3 Vector3::operator+(const Vector3& other) const {
    return Vector3(x + other.x, y + other.y, z + other.z);
}

Vector3 Vector3::operator-(const Vector3& other) const {
    return Vector3(x - other.x, y - other.y, z - other.z);
}

Vector3 Vector3::operator*(float scalar) const {
    return Vector3(x * scalar, y * scalar, z * scalar);
}

float Vector3::Length() const {
    return std::sqrt(x * x + y * y + z * z);
}

Vector3 Vector3::Normalized() const {
    float len = Length();
    if (len > 0.0001f) {
        return Vector3(x / len, y / len, z / len);
    }
    return Vector3(0, 0, 0);
}

// SequenceNode implementation
void SequenceNode::AddChild(std::shared_ptr<BehaviorNode> child) {
    children.push_back(child);
}

BehaviorNodeStatus SequenceNode::Execute() {
    while (currentChild < children.size()) {
        auto status = children[currentChild]->Execute();
        
        if (status == BehaviorNodeStatus::Failure) {
            Reset();
            return BehaviorNodeStatus::Failure;
        }
        
        if (status == BehaviorNodeStatus::Running) {
            return BehaviorNodeStatus::Running;
        }
        
        currentChild++;
    }
    
    Reset();
    return BehaviorNodeStatus::Success;
}

void SequenceNode::Reset() {
    currentChild = 0;
    for (auto& child : children) {
        child->Reset();
    }
}

// SelectorNode implementation
void SelectorNode::AddChild(std::shared_ptr<BehaviorNode> child) {
    children.push_back(child);
}

BehaviorNodeStatus SelectorNode::Execute() {
    while (currentChild < children.size()) {
        auto status = children[currentChild]->Execute();
        
        if (status == BehaviorNodeStatus::Success) {
            Reset();
            return BehaviorNodeStatus::Success;
        }
        
        if (status == BehaviorNodeStatus::Running) {
            return BehaviorNodeStatus::Running;
        }
        
        currentChild++;
    }
    
    Reset();
    return BehaviorNodeStatus::Failure;
}

void SelectorNode::Reset() {
    currentChild = 0;
    for (auto& child : children) {
        child->Reset();
    }
}

// InverterNode implementation
InverterNode::InverterNode(std::shared_ptr<BehaviorNode> child) : child(child) {}

BehaviorNodeStatus InverterNode::Execute() {
    auto status = child->Execute();
    
    if (status == BehaviorNodeStatus::Success) {
        return BehaviorNodeStatus::Failure;
    } else if (status == BehaviorNodeStatus::Failure) {
        return BehaviorNodeStatus::Success;
    }
    
    return BehaviorNodeStatus::Running;
}

void InverterNode::Reset() {
    child->Reset();
}

// RepeaterNode implementation
RepeaterNode::RepeaterNode(std::shared_ptr<BehaviorNode> child, int maxRepeats)
    : child(child), maxRepeats(maxRepeats) {}

BehaviorNodeStatus RepeaterNode::Execute() {
    if (maxRepeats > 0 && currentRepeats >= maxRepeats) {
        Reset();
        return BehaviorNodeStatus::Success;
    }
    
    auto status = child->Execute();
    
    if (status == BehaviorNodeStatus::Success || status == BehaviorNodeStatus::Failure) {
        currentRepeats++;
        child->Reset();
        
        if (maxRepeats > 0 && currentRepeats >= maxRepeats) {
            Reset();
            return BehaviorNodeStatus::Success;
        }
        
        return BehaviorNodeStatus::Running;
    }
    
    return BehaviorNodeStatus::Running;
}

void RepeaterNode::Reset() {
    currentRepeats = 0;
    child->Reset();
}

// ActionNode implementation
ActionNode::ActionNode(ActionFunc action) : action(action) {}

BehaviorNodeStatus ActionNode::Execute() {
    return action();
}

// ConditionNode implementation
ConditionNode::ConditionNode(ConditionFunc condition) : condition(condition) {}

BehaviorNodeStatus ConditionNode::Execute() {
    return condition() ? BehaviorNodeStatus::Success : BehaviorNodeStatus::Failure;
}

// BehaviorTree implementation
void BehaviorTree::SetRoot(std::shared_ptr<BehaviorNode> root) {
    this->root = root;
}

BehaviorNodeStatus BehaviorTree::Execute() {
    if (root) {
        return root->Execute();
    }
    return BehaviorNodeStatus::Failure;
}

void BehaviorTree::Reset() {
    if (root) {
        root->Reset();
    }
}

// NavMeshTriangle implementation
NavMeshTriangle::NavMeshTriangle(const Vector3& v0, const Vector3& v1, const Vector3& v2) {
    vertices[0] = v0;
    vertices[1] = v1;
    vertices[2] = v2;
    center = Vector3(
        (v0.x + v1.x + v2.x) / 3.0f,
        (v0.y + v1.y + v2.y) / 3.0f,
        (v0.z + v1.z + v2.z) / 3.0f
    );
}

bool NavMeshTriangle::Contains(const Vector3& point) const {
    // Simple 2D point-in-triangle test (ignoring Y for now)
    auto sign = [](const Vector3& p1, const Vector3& p2, const Vector3& p3) {
        return (p1.x - p3.x) * (p2.z - p3.z) - (p2.x - p3.x) * (p1.z - p3.z);
    };
    
    float d1 = sign(point, vertices[0], vertices[1]);
    float d2 = sign(point, vertices[1], vertices[2]);
    float d3 = sign(point, vertices[2], vertices[0]);
    
    bool hasNeg = (d1 < 0) || (d2 < 0) || (d3 < 0);
    bool hasPos = (d1 > 0) || (d2 > 0) || (d3 > 0);
    
    return !(hasNeg && hasPos);
}

// NavMesh implementation
void NavMesh::AddTriangle(const Vector3& v0, const Vector3& v1, const Vector3& v2) {
    triangles.emplace_back(v0, v1, v2);
}

void NavMesh::BuildConnections() {
    // Build neighbor connections between triangles
    for (size_t i = 0; i < triangles.size(); i++) {
        for (size_t j = i + 1; j < triangles.size(); j++) {
            // Check if triangles share an edge
            float distThreshold = 0.1f;
            int sharedVertices = 0;
            
            for (int vi = 0; vi < 3; vi++) {
                for (int vj = 0; vj < 3; vj++) {
                    if (triangles[i].vertices[vi].Distance(triangles[j].vertices[vj]) < distThreshold) {
                        sharedVertices++;
                    }
                }
            }
            
            if (sharedVertices >= 2) {
                triangles[i].neighbors.push_back(j);
                triangles[j].neighbors.push_back(i);
            }
        }
    }
}

int NavMesh::FindTriangle(const Vector3& position) const {
    for (size_t i = 0; i < triangles.size(); i++) {
        if (triangles[i].Contains(position)) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

std::vector<int> NavMesh::GetNeighbors(int triangleIndex) const {
    if (triangleIndex >= 0 && triangleIndex < static_cast<int>(triangles.size())) {
        return triangles[triangleIndex].neighbors;
    }
    return {};
}

Vector3 NavMesh::GetTriangleCenter(int triangleIndex) const {
    if (triangleIndex >= 0 && triangleIndex < static_cast<int>(triangles.size())) {
        return triangles[triangleIndex].center;
    }
    return Vector3();
}

// Pathfinder implementation
float Pathfinder::Heuristic(const Vector3& a, const Vector3& b) {
    return a.Distance(b);
}

int Pathfinder::PositionToKey(const Vector3& pos, float gridSize) {
    int x = static_cast<int>(std::floor(pos.x / gridSize));
    int y = static_cast<int>(std::floor(pos.y / gridSize));
    int z = static_cast<int>(std::floor(pos.z / gridSize));
    // Use a simpler key that can be reversed
    // Limit to reasonable grid bounds to avoid overflow
    const int GRID_OFFSET = 10000;
    return ((x + GRID_OFFSET) * 100000000) + ((y + GRID_OFFSET) * 10000) + (z + GRID_OFFSET);
}

Vector3 Pathfinder::KeyToPosition(int key, float gridSize) {
    const int GRID_OFFSET = 10000;
    int z = (key % 10000) - GRID_OFFSET;
    int y = ((key / 10000) % 10000) - GRID_OFFSET;
    int x = (key / 100000000) - GRID_OFFSET;
    return Vector3(x * gridSize, y * gridSize, z * gridSize);
}

std::vector<Vector3> Pathfinder::FindPathAStar(
    const Vector3& start,
    const Vector3& goal,
    std::function<bool(const Vector3&)> isWalkable,
    float gridSize
) {
    std::vector<Vector3> path;
    
    auto compare = [](PathNode* a, PathNode* b) {
        return a->fCost() > b->fCost();
    };
    
    std::priority_queue<PathNode*, std::vector<PathNode*>, decltype(compare)> openSet(compare);
    std::unordered_map<int, std::unique_ptr<PathNode>> allNodes;
    std::set<int> closedSet;
    
    int startKey = PositionToKey(start, gridSize);
    auto startNode = std::make_unique<PathNode>(start);
    startNode->gCost = 0;
    startNode->hCost = Heuristic(start, goal);
    
    PathNode* startPtr = startNode.get();
    allNodes[startKey] = std::move(startNode);
    openSet.push(startPtr);
    
    while (!openSet.empty()) {
        PathNode* current = openSet.top();
        openSet.pop();
        
        int currentKey = PositionToKey(current->position, gridSize);
        
        if (closedSet.count(currentKey)) {
            continue;
        }
        
        closedSet.insert(currentKey);
        
        if (current->position.Distance(goal) < gridSize) {
            // Reconstruct path
            PathNode* node = current;
            while (node != nullptr) {
                path.push_back(node->position);
                node = node->parent;
            }
            std::reverse(path.begin(), path.end());
            return path;
        }
        
        // Check neighbors
        Vector3 directions[] = {
            Vector3(gridSize, 0, 0), Vector3(-gridSize, 0, 0),
            Vector3(0, gridSize, 0), Vector3(0, -gridSize, 0),
            Vector3(0, 0, gridSize), Vector3(0, 0, -gridSize)
        };
        
        for (const auto& dir : directions) {
            Vector3 neighborPos = current->position + dir;
            
            if (!isWalkable(neighborPos)) {
                continue;
            }
            
            int neighborKey = PositionToKey(neighborPos, gridSize);
            
            if (closedSet.count(neighborKey)) {
                continue;
            }
            
            float tentativeG = current->gCost + gridSize;
            
            if (!allNodes.count(neighborKey)) {
                auto neighborNode = std::make_unique<PathNode>(neighborPos);
                neighborNode->gCost = tentativeG;
                neighborNode->hCost = Heuristic(neighborPos, goal);
                neighborNode->parent = current;
                
                PathNode* neighborPtr = neighborNode.get();
                allNodes[neighborKey] = std::move(neighborNode);
                openSet.push(neighborPtr);
            } else {
                PathNode* neighborNode = allNodes[neighborKey].get();
                if (tentativeG < neighborNode->gCost) {
                    neighborNode->gCost = tentativeG;
                    neighborNode->parent = current;
                    openSet.push(neighborNode);
                }
            }
        }
    }
    
    return path;
}

std::vector<Vector3> Pathfinder::FindPathNavMesh(
    const Vector3& start,
    const Vector3& goal,
    const NavMesh& navMesh
) {
    std::vector<Vector3> path;
    
    int startTriangle = navMesh.FindTriangle(start);
    int goalTriangle = navMesh.FindTriangle(goal);
    
    if (startTriangle < 0 || goalTriangle < 0) {
        return path;
    }
    
    if (startTriangle == goalTriangle) {
        path.push_back(start);
        path.push_back(goal);
        return path;
    }
    
    // A* on triangle graph
    std::unordered_map<int, float> gCost;
    std::unordered_map<int, float> fCost;
    std::unordered_map<int, int> cameFrom;
    std::set<int> closedSet;
    
    auto compare = [&fCost](int a, int b) {
        return fCost[a] > fCost[b];
    };
    
    std::priority_queue<int, std::vector<int>, decltype(compare)> openSet(compare);
    
    gCost[startTriangle] = 0;
    fCost[startTriangle] = navMesh.GetTriangleCenter(startTriangle).Distance(goal);
    openSet.push(startTriangle);
    
    while (!openSet.empty()) {
        int current = openSet.top();
        openSet.pop();
        
        if (closedSet.count(current)) {
            continue;
        }
        
        closedSet.insert(current);
        
        if (current == goalTriangle) {
            // Reconstruct path
            path.push_back(goal);
            int tri = current;
            while (cameFrom.count(tri)) {
                path.push_back(navMesh.GetTriangleCenter(tri));
                tri = cameFrom[tri];
            }
            path.push_back(start);
            std::reverse(path.begin(), path.end());
            return path;
        }
        
        for (int neighbor : navMesh.GetNeighbors(current)) {
            if (closedSet.count(neighbor)) {
                continue;
            }
            
            Vector3 currentCenter = navMesh.GetTriangleCenter(current);
            Vector3 neighborCenter = navMesh.GetTriangleCenter(neighbor);
            float tentativeG = gCost[current] + currentCenter.Distance(neighborCenter);
            
            if (!gCost.count(neighbor) || tentativeG < gCost[neighbor]) {
                cameFrom[neighbor] = current;
                gCost[neighbor] = tentativeG;
                fCost[neighbor] = tentativeG + neighborCenter.Distance(goal);
                openSet.push(neighbor);
            }
        }
    }
    
    return path;
}

Pathfinder::FlowField Pathfinder::GenerateFlowField(
    const Vector3& goal,
    std::function<bool(const Vector3&)> isWalkable,
    float gridSize,
    float maxDistance
) {
    FlowField field;
    field.gridSize = gridSize;
    
    std::unordered_map<int, float> costField;
    std::queue<int> openSet;
    
    int goalKey = PositionToKey(goal, gridSize);
    costField[goalKey] = 0;
    openSet.push(goalKey);
    
    Vector3 directions[] = {
        Vector3(gridSize, 0, 0), Vector3(-gridSize, 0, 0),
        Vector3(0, gridSize, 0), Vector3(0, -gridSize, 0),
        Vector3(0, 0, gridSize), Vector3(0, 0, -gridSize)
    };
    
    while (!openSet.empty()) {
        int currentKey = openSet.front();
        openSet.pop();
        
        float currentCost = costField[currentKey];
        
        if (currentCost >= maxDistance) {
            continue;
        }
        
        // Reconstruct position from key
        Vector3 currentPos = KeyToPosition(currentKey, gridSize);
        
        for (const auto& dir : directions) {
            Vector3 neighborPos = currentPos + dir;
            
            if (!isWalkable(neighborPos)) {
                continue;
            }
            
            int neighborKey = PositionToKey(neighborPos, gridSize);
            float newCost = currentCost + gridSize;
            
            if (!costField.count(neighborKey) || newCost < costField[neighborKey]) {
                costField[neighborKey] = newCost;
                openSet.push(neighborKey);
            }
        }
    }
    
    // Generate flow directions
    for (const auto& [key, cost] : costField) {
        Vector3 pos = KeyToPosition(key, gridSize);
        
        Vector3 bestDir(0, 0, 0);
        float lowestCost = cost;
        
        for (const auto& dir : directions) {
            Vector3 neighborPos = pos + dir;
            int neighborKey = PositionToKey(neighborPos, gridSize);
            
            if (costField.count(neighborKey) && costField[neighborKey] < lowestCost) {
                lowestCost = costField[neighborKey];
                bestDir = dir.Normalized();
            }
        }
        
        if (bestDir.Length() > 0.01f) {
            field.directions[key] = bestDir;
        }
    }
    
    return field;
}

Vector3 Pathfinder::GetFlowDirection(const FlowField& field, const Vector3& position) {
    int key = PositionToKey(position, field.gridSize);
    
    if (field.directions.count(key)) {
        return field.directions.at(key);
    }
    
    return Vector3(0, 0, 0);
}

// CrowdSimulation implementation
int CrowdSimulation::AddAgent(const Vector3& position, float radius, float maxSpeed) {
    int id = nextAgentId++;
    Agent agent(id, position);
    agent.radius = radius;
    agent.maxSpeed = maxSpeed;
    agents[id] = agent;
    return id;
}

void CrowdSimulation::RemoveAgent(int agentId) {
    agents.erase(agentId);
    agentGoals.erase(agentId);
}

void CrowdSimulation::SetAgentGoal(int agentId, const Vector3& goal) {
    agentGoals[agentId] = goal;
}

Vector3 CrowdSimulation::GetAgentPosition(int agentId) const {
    auto it = agents.find(agentId);
    if (it != agents.end()) {
        return it->second.position;
    }
    return Vector3();
}

Vector3 CrowdSimulation::GetAgentVelocity(int agentId) const {
    auto it = agents.find(agentId);
    if (it != agents.end()) {
        return it->second.velocity;
    }
    return Vector3();
}

std::vector<Agent*> CrowdSimulation::GetNeighbors(const Agent& agent, float radius) {
    std::vector<Agent*> neighbors;
    
    for (auto& [id, other] : agents) {
        if (other.id != agent.id) {
            float dist = agent.position.Distance(other.position);
            if (dist < radius) {
                neighbors.push_back(&other);
            }
        }
    }
    
    return neighbors;
}

Vector3 CrowdSimulation::CalculateSeparation(const Agent& agent) {
    Vector3 force(0, 0, 0);
    auto neighbors = GetNeighbors(agent, avoidanceRadius);
    
    for (Agent* other : neighbors) {
        Vector3 diff = agent.position - other->position;
        float dist = diff.Length();
        
        if (dist > 0.001f) {
            force = force + (diff.Normalized() * (1.0f / dist));
        }
    }
    
    return force;
}

Vector3 CrowdSimulation::CalculateAlignment(const Agent& agent) {
    Vector3 avgVelocity(0, 0, 0);
    auto neighbors = GetNeighbors(agent, avoidanceRadius * 2.0f);
    
    if (neighbors.empty()) {
        return Vector3(0, 0, 0);
    }
    
    for (Agent* other : neighbors) {
        avgVelocity = avgVelocity + other->velocity;
    }
    
    avgVelocity = avgVelocity * (1.0f / neighbors.size());
    return avgVelocity - agent.velocity;
}

Vector3 CrowdSimulation::CalculateCohesion(const Agent& agent) {
    Vector3 centerOfMass(0, 0, 0);
    auto neighbors = GetNeighbors(agent, avoidanceRadius * 2.0f);
    
    if (neighbors.empty()) {
        return Vector3(0, 0, 0);
    }
    
    for (Agent* other : neighbors) {
        centerOfMass = centerOfMass + other->position;
    }
    
    centerOfMass = centerOfMass * (1.0f / neighbors.size());
    return (centerOfMass - agent.position).Normalized();
}

Vector3 CrowdSimulation::CalculateGoalSeeking(const Agent& agent) {
    auto it = agentGoals.find(agent.id);
    if (it != agentGoals.end()) {
        Vector3 direction = it->second - agent.position;
        return direction.Normalized() * agent.maxSpeed;
    }
    return Vector3(0, 0, 0);
}

Vector3 CrowdSimulation::CalculateAvoidance(const Agent& agent) {
    Vector3 avoidance(0, 0, 0);
    auto neighbors = GetNeighbors(agent, agent.radius * 3.0f);
    
    for (Agent* other : neighbors) {
        Vector3 toOther = other->position - agent.position;
        float dist = toOther.Length();
        
        if (dist < agent.radius + other->radius) {
            Vector3 away = (agent.position - other->position).Normalized();
            avoidance = avoidance + away * (1.0f / (dist + 0.001f));
        }
    }
    
    return avoidance;
}

void CrowdSimulation::Update(float deltaTime) {
    // Calculate desired velocities for all agents
    for (auto& [id, agent] : agents) {
        Vector3 separation = CalculateSeparation(agent) * separationWeight;
        Vector3 alignment = CalculateAlignment(agent) * alignmentWeight;
        Vector3 cohesion = CalculateCohesion(agent) * cohesionWeight;
        Vector3 goalSeek = CalculateGoalSeeking(agent);
        Vector3 avoidance = CalculateAvoidance(agent) * 2.0f;
        
        agent.desiredVelocity = goalSeek + separation + alignment + cohesion + avoidance;
        
        // Limit to max speed
        float speed = agent.desiredVelocity.Length();
        if (speed > agent.maxSpeed) {
            agent.desiredVelocity = agent.desiredVelocity.Normalized() * agent.maxSpeed;
        }
    }
    
    // Update positions
    for (auto& [id, agent] : agents) {
        Vector3 steering = agent.desiredVelocity - agent.velocity;
        float steeringMag = steering.Length();
        
        if (steeringMag > agent.maxForce) {
            steering = steering.Normalized() * agent.maxForce;
        }
        
        agent.velocity = agent.velocity + steering * deltaTime;
        
        float velMag = agent.velocity.Length();
        if (velMag > agent.maxSpeed) {
            agent.velocity = agent.velocity.Normalized() * agent.maxSpeed;
        }
        
        agent.position = agent.position + agent.velocity * deltaTime;
    }
}

// AIFramework implementation
bool AIFramework::Initialize() {
    if (initialized) {
        return true;
    }
    
    initialized = true;
    return true;
}

void AIFramework::Shutdown() {
    behaviorTrees.clear();
    navMeshes.clear();
    crowdSimulations.clear();
    initialized = false;
}

int AIFramework::CreateBehaviorTree() {
    int id = nextTreeId++;
    behaviorTrees[id] = std::make_unique<BehaviorTree>();
    return id;
}

BehaviorTree* AIFramework::GetBehaviorTree(int treeId) {
    auto it = behaviorTrees.find(treeId);
    if (it != behaviorTrees.end()) {
        return it->second.get();
    }
    return nullptr;
}

void AIFramework::DestroyBehaviorTree(int treeId) {
    behaviorTrees.erase(treeId);
}

int AIFramework::CreateNavMesh() {
    int id = nextNavMeshId++;
    navMeshes[id] = std::make_unique<NavMesh>();
    return id;
}

NavMesh* AIFramework::GetNavMesh(int navMeshId) {
    auto it = navMeshes.find(navMeshId);
    if (it != navMeshes.end()) {
        return it->second.get();
    }
    return nullptr;
}

void AIFramework::DestroyNavMesh(int navMeshId) {
    navMeshes.erase(navMeshId);
}

int AIFramework::CreateCrowdSimulation() {
    int id = nextCrowdId++;
    crowdSimulations[id] = std::make_unique<CrowdSimulation>();
    return id;
}

CrowdSimulation* AIFramework::GetCrowdSimulation(int crowdId) {
    auto it = crowdSimulations.find(crowdId);
    if (it != crowdSimulations.end()) {
        return it->second.get();
    }
    return nullptr;
}

void AIFramework::DestroyCrowdSimulation(int crowdId) {
    crowdSimulations.erase(crowdId);
}

void AIFramework::Update(float deltaTime) {
    // Update all crowd simulations
    for (auto& [id, crowd] : crowdSimulations) {
        crowd->Update(deltaTime);
    }
}

} // namespace pywrkgame

