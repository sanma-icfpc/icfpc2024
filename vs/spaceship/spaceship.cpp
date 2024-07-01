#include <algorithm>
#include <array>
#include <chrono>
#include <deque>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <set>
#include <stack>
#include <vector>

struct State {
    int position;
    int velocity;
    int num_steps;
};

struct Position {
    int x;
    int y;

    bool operator<(const Position& rh) const {
        if (x != rh.x) {
            return x < rh.x;
        }
        else {
            return y < rh.y;
        }
    }
};

struct Acceleration {
    int x;
    int y;

    int ToDigit() const {
        return 1 + (x + 1) + (y + 1) * 3;
    }
};

int MAX_DISTANCE = 0;

// 距離に対する、移動にかかるターン数。
std::vector<int> NUM_STEPS;
std::vector<Position> POSITIONS;

int CalculateNumAccelerations(int distance) {
    // [left,right]
    // left回以上加速すると、distanceを超えるという状況を仮定する。
    // left - 1が加速回数になる。
    int64_t left = 0;
    int64_t right = distance + 10;
    while (left < right) {
        int64_t middle = left + (right - left) / 2;
        if (middle * middle <= distance) {
            left = middle + 1;
        }
        else {
            right = middle;
        }
    }

    return static_cast<int>(left - 1);
}

int CalculateNumStepsDirectly(int distance) {
    int num_accelerations = CalculateNumAccelerations(distance);
    if (num_accelerations == 0) {
        return 0;
    }

    int top_speed = num_accelerations;
    int remainder_distance = distance - (num_accelerations * num_accelerations);
    return num_accelerations * 2 + (remainder_distance + top_speed - 1) / top_speed;
}

void InitializeTable() {
    while (NUM_STEPS.size() <= MAX_DISTANCE) {
        int distance = NUM_STEPS.size();
        NUM_STEPS.push_back(CalculateNumStepsDirectly(distance));
    }
}

int GetNumSteps1D(int start, int goal) {
    int distance = std::abs(start - goal);
    return NUM_STEPS[distance];
}

void GetPath1D(int start, int goal, std::vector<int>& accelerations) {
    accelerations.clear();

    int distance = std::abs(start - goal);
    int num_accelerations = CalculateNumAccelerations(distance);
    accelerations.insert(accelerations.end(), num_accelerations, 1);

    int remainder_distance = distance - (num_accelerations * num_accelerations);
    for (int velocity = num_accelerations; velocity > 0; --velocity) {
        while (remainder_distance >= velocity) {
            accelerations.push_back(0);
            remainder_distance -= velocity;
        }
        accelerations.push_back(-1);
    }

    if (start > goal) {
        for (auto& acceleration : accelerations) {
            acceleration *= -1;
        }
    }
}

void TestGetPath1D(int start, int goal) {
    std::vector<int> accelerations;
    GetPath1D(start, goal, accelerations);

    int position = 0;
    int velocity = 0;
    std::printf("(position, velocity) = (%d, %d)\n", position, velocity);
    for (int acceleration : accelerations) {
        velocity += acceleration;
        position += velocity;
        std::printf("(position, velocity) = (%d, %d)\n", position, velocity);
    }

    std::printf("\n");
}

void TestGetPath1D() {
    TestGetPath1D(0, 0);
    TestGetPath1D(0, 1);
    TestGetPath1D(0, 2);
    TestGetPath1D(0, 3);
    TestGetPath1D(0, 4);
    TestGetPath1D(0, 5);
    TestGetPath1D(0, 6);
    TestGetPath1D(0, 7);
    TestGetPath1D(0, 8);
    TestGetPath1D(0, 9);
    TestGetPath1D(0, 10);
    TestGetPath1D(0, 11);
}

void Input() {
    POSITIONS.push_back({ 0, 0 });

    int x, y;
    // 初期位置が(0,0)のため、0で初期化する。
    int min_x = 0;
    int max_x = 0;
    int min_y = 0;
    int max_y = 0;
    while (std::cin >> x >> y) {
        min_x = std::min(x, min_x);
        max_x = std::max(x, max_x);
        min_y = std::min(y, min_y);
        max_y = std::max(y, max_y);
        POSITIONS.push_back({ x, y });
    }

    MAX_DISTANCE = std::max(max_x - min_x, max_y - min_y);

    std::cerr << "num_nodes=" << POSITIONS.size() << " min_x=" << min_x << " max_x=" << max_x << " min_y=" << min_y << " max_y=" << max_y << std::endl;
}

int GetNumSteps2D(const Position& start, const Position& goal) {
    return std::max(GetNumSteps1D(start.x, goal.x), GetNumSteps1D(start.y, goal.y));
}

void GetPath2D(const Position& start, const Position& goal, std::vector<Acceleration>& accelerations_2d) {
    accelerations_2d.clear();

    std::vector<int> accelerations_x;
    GetPath1D(start.x, goal.x, accelerations_x);
    std::vector<int> accelerations_y;
    GetPath1D(start.y, goal.y, accelerations_y);

    int num_steps = std::max(accelerations_x.size(), accelerations_y.size());
    accelerations_x.resize(num_steps);
    accelerations_y.resize(num_steps);

    for (int step = 0; step < num_steps; ++step) {
        int acceleration_x = accelerations_x[step];
        int acceleration_y = accelerations_y[step];
        accelerations_2d.push_back({ acceleration_x, acceleration_y });
    }
}

void TestGetPath2D() {
    Position start = { 0, 0 };
    Position goal = { 10, 5 };
    std::vector<Acceleration> accelerations_2d;
    GetPath2D(start, goal, accelerations_2d);
    int position_x = 0;
    int velocity_x = 0;
    int position_y = 0;
    int velocity_y = 0;
    for (const auto& acceleration : accelerations_2d) {
        velocity_x += acceleration.x;
        position_x += velocity_x;
        velocity_y += acceleration.y;
        position_y += velocity_y;
        std::printf("position=(%d, %d) velocity=(%d, %d) acceleration=(%d, %d)\n",
            position_x, position_y, velocity_x, velocity_y, acceleration.x, acceleration.y);
    }
}

std::vector<std::vector<int>> MINIMUM_SPANNING_TREE;

struct UnionFind {
    std::vector<int> parents;
    UnionFind(int n) : parents(n, -1) { }

    int Find(int i) {
        if (parents[i] < 0) {
            return i;
        }

        parents[i] = Find(parents[i]);
        return parents[i];
    }

    void Union(int i, int j) {
        int root_i = Find(i);
        int root_j = Find(j);
        if (root_i == root_j) {
            return;
        }

        if (root_i > root_j) {
            std::swap(root_i, root_j);
        }
        parents[root_i] += parents[root_j];
        parents[root_j] = root_i;
    }
};

struct Edge {
    int cost;
    int source;
    int destination;

    bool operator<(const Edge& rh) const {
        if (cost != rh.cost) {
            return cost < rh.cost;
        }
        else if (source != rh.source) {
            return source < rh.source;
        }
        else {
            return destination < rh.destination;
        }
    }
};

void InitializeMinimumSpanningTree() {
    // クラスカル法で最小全域木を求める。
    int num_nodes = POSITIONS.size();
    MINIMUM_SPANNING_TREE.resize(num_nodes);

    std::vector<Edge> edges;
    for (int source = 0; source < num_nodes; ++source) {
        for (int destination = source + 1; destination < num_nodes; ++destination) {
            int cost = GetNumSteps2D(POSITIONS[source], POSITIONS[destination]);
            edges.emplace_back(Edge{ cost, source, destination });
        }
    }

    std::sort(edges.begin(), edges.end());

    UnionFind components(num_nodes);
    for (const auto& edge : edges) {
        if (components.Find(edge.source) == components.Find(edge.destination)) {
            continue;
        }

        components.Union(edge.source, edge.destination);
        MINIMUM_SPANNING_TREE[edge.source].push_back(edge.destination);
        MINIMUM_SPANNING_TREE[edge.destination].push_back(edge.source);

        if (components.parents[0] == -num_nodes) {
            break;
        }
    }
}

std::vector<int> VISITING_ORDER;

void InitializeVisitingOrder() {
    int num_nodes = POSITIONS.size();
    std::stack<int> stk;
    stk.push(0);
    std::vector<bool> visited(num_nodes);
    visited[0] = true;

    while (!stk.empty()) {
        int node = stk.top();
        stk.pop();

        VISITING_ORDER.push_back(node);

        for (int destination : MINIMUM_SPANNING_TREE[node]) {
            if (visited[destination]) {
                continue;
            }
            visited[destination] = true;

            stk.push(destination);
        }
    }
}

namespace
{
    static constexpr int TIME_LIMIT_MS = 10 * 1000;

    // https://ja.wikipedia.org/wiki/Xorshift
    uint32_t xor64(void) {
        static uint64_t x = 88172645463325252ULL;
        x = x ^ (x << 13); x = x ^ (x >> 7);
        return x = x ^ (x << 17);
    }

    int64_t elapsedMs(const std::chrono::system_clock::time_point& startTime) {
        const auto now = std::chrono::system_clock::now();
        return std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime).count();
    }
}

//TODO:状態を表す型/構造体を作成する
class STATE {
public:
    //TODO:コンストラクタに必要な引数を追加する
    explicit STATE();
    void next();
    void prev();
    double energy();

    std::vector<int> visiting_order;
private:
    // TODO(nodchip): 3-optに対応する。
    int swapped0;
    int swapped1;
    int swapped2;
    int opt;
};

class SimulatedAnnealing {
public:
    //TODO:コンストラクタに必要な引数を追加する
    SimulatedAnnealing();
    STATE run();
private:
    double calculateProbability(double score, double scoreNeighbor, double temperature);
};

//TODO:コンストラクタに必要な引数を追加する
SimulatedAnnealing::SimulatedAnnealing() {
}

STATE SimulatedAnnealing::run() {
    const auto startTime = std::chrono::system_clock::now();
    STATE state;
    double energy = state.energy();
    STATE result = state;
    double minEnergy = energy;
    int counter = 0;
    int64_t timeCurrent;
    while (elapsedMs(startTime) < TIME_LIMIT_MS) {
        for (int loop = 0; loop < 100; ++loop) {
            state.next();
            const double energyNeighbor = state.energy();
            const double random = xor64() * 0.00000000023283064365386962890625;
            const double probability = calculateProbability(energy, energyNeighbor, elapsedMs(startTime) / double(TIME_LIMIT_MS) + 1e-8);
            if (random < probability) {
                //Accept
                if (minEnergy > energyNeighbor) {
#ifdef _MSC_VER
                    fprintf(stderr, "minEnergy updated! %.5lf -> %.5lf\n", minEnergy, energyNeighbor);
#endif
                    minEnergy = energyNeighbor;
                    result = state;
                }
                //fprintf(stderr, "Accepted %.5lf -> %.5lf : minEnergy=%.5lf\n", energy, energyNeighbor, minEnergy);
                energy = energyNeighbor;
            }
            else {
                //Decline
                state.prev();
                //fprintf(stderr, "Declined\n");
            }
            ++counter;
        }
    }
    fprintf(stderr, "counter:%d minEnergy:%.5lf\n", counter, minEnergy);
    return result;
}

double SimulatedAnnealing::calculateProbability(double energy, double energyNeighbor, double temperature) {
    if (energyNeighbor < energy) {
        return 1;
    }
    else {
        const double result = exp((energy - energyNeighbor) / (temperature + 1e-9) * 1.0);
        //fprintf(stderr, "%lf -> %lf * %lf = %lf\n", energy, energyNeighbor, temperature, result);
        return result;
    }
}

//TODO:初期状態を作る関数を記述する
STATE::STATE() {
    visiting_order = VISITING_ORDER;
}

//TODO:遷移後の状態を作る関数を記述する
void STATE::next() {
    opt = xor64() % 2 + 2;

    switch (opt)
    {
    case 2:
        swapped0 = xor64() % (visiting_order.size() - 1) + 1;
        do {
            swapped1 = xor64() % (visiting_order.size() - 1) + 1;
        } while (swapped0 == swapped1);

        std::swap(visiting_order[swapped0], visiting_order[swapped1]);
        break;

    case 3:
        swapped0 = xor64() % (visiting_order.size() - 1) + 1;
        do {
            swapped1 = xor64() % (visiting_order.size() - 1) + 1;
        } while (swapped0 == swapped1);
        do {
            swapped2 = xor64() % (visiting_order.size() - 1) + 1;
        } while (swapped0 == swapped2 && swapped1 == swapped2);

        std::swap(visiting_order[swapped0], visiting_order[swapped1]);
        std::swap(visiting_order[swapped1], visiting_order[swapped2]);
        break;

    default:
        break;
    }
}

//TODO:遷移前の状態を作る関数を記述する
//     高々一つ前の状態までに戻れれば良い
void STATE::prev() {
    switch (opt)
    {
    case 2:
        std::swap(visiting_order[swapped0], visiting_order[swapped1]);
        break;

    case 3:
        std::swap(visiting_order[swapped1], visiting_order[swapped2]);
        std::swap(visiting_order[swapped0], visiting_order[swapped1]);
        break;

    default:
        break;
    }
}

//TODO:状態のエネルギーを計算する関数を記述する
//     状態はエネルギーの低い所に遷移する点に注意する
double STATE::energy() {
    int num_steps = 0;
    for (int order_index = 0; order_index + 1 < visiting_order.size(); ++order_index) {
        // 本当はすでに通ったsquareはスキップしたいが、
        // 経路を1ターンずつシミュレーションすると時間がかかるため、
        // シミュレーションは省く。
        const auto& source = POSITIONS[visiting_order[order_index]];
        const auto& destination = POSITIONS[visiting_order[order_index + 1]];
        num_steps += GetNumSteps2D(source, destination);
    }
    return num_steps;
}

void OutputStrictPath(const std::vector<int>& visiting_order) {
    std::set<Position> visited = { { 0, 0 } };
    int position_x = 0;
    int velocity_x = 0;
    int position_y = 0;
    int velocity_y = 0;
    auto source = POSITIONS[0];

    for (int order_index = 1; order_index < POSITIONS.size(); ++order_index) {
        const auto& destination = POSITIONS[visiting_order[order_index]];

        if (visited.find(destination) != visited.end()) {
            continue;
        }

        std::vector<Acceleration> acceleration_2d;
        GetPath2D(source, destination, acceleration_2d);

        for (const auto& acceleration : acceleration_2d) {
            velocity_x += acceleration.x;
            position_x += velocity_x;
            velocity_y += acceleration.y;
            position_y += velocity_y;

            visited.insert({ position_x, position_y });

            std::cout << acceleration.ToDigit();
        }

        source = destination;
    }
    std::cout << std::endl;
}

void OutputBeamSearchPath(const std::vector<int>& visiting_order) {
    std::set<Position> visited = { { 0, 0 } };
    auto source = POSITIONS[0];
    int last_velocity_x = 0;
    int last_velocity_y = 0;

    for (int order_index = 1; order_index < POSITIONS.size(); ++order_index) {
        const auto& destination = POSITIONS[VISITING_ORDER[order_index]];

        if (visited.find(destination) != visited.end()) {
            continue;
        }

        // ビームサーチ
        const constexpr int BEAM_WIDTH = 1000;
        struct State {
            int distance;
            int position_x;
            int velocity_x;
            int position_y;
            int velocity_y;
            int last_acceleration_x;
            int last_acceleration_y;
            const State* last_state;
            bool operator<(const State& rh) const {
                // 目標地点との距離が大きいものをpop()したい。
                return distance < rh.distance;
            }
        };
        State initial_state = {
            std::max(std::abs(destination.x - source.x), std::abs(destination.y - source.y)),
            source.x, last_velocity_x, source.y, last_velocity_y, 0, 0, nullptr
        };
        std::vector<std::vector<State>> history;
        std::priority_queue<State> q;
        q.push(initial_state);

        bool found = false;
        while (!found) {
            std::priority_queue<State> new_q;
            std::vector<State> states;

            while (!q.empty()) {
                states.push_back(q.top());
                q.pop();
            }

            history.push_back(states);

            // historyに代入したあと、Stateのポインターの値が変わらないことを利用する。
            for (const auto& state : history.back()) {
                for (int acceleration_x = -1; acceleration_x <= 1; ++acceleration_x) {
                    for (int acceleration_y = -1; acceleration_y <= 1; ++acceleration_y) {
                        auto new_state = state;
                        new_state.last_state = &state;
                        new_state.last_acceleration_x = acceleration_x;
                        new_state.last_acceleration_y = acceleration_y;
                        new_state.velocity_x += acceleration_x;
                        new_state.velocity_y += acceleration_y;
                        new_state.position_x += new_state.velocity_x;
                        new_state.position_y += new_state.velocity_y;
                        new_state.distance = std::max(std::abs(destination.x - new_state.position_x), std::abs(destination.y - new_state.position_y));
                        new_q.push(new_state);
                        if (new_q.size() > BEAM_WIDTH) {
                            new_q.pop();
                        }

                        if (destination.x == new_state.position_x && destination.y == new_state.position_y) {
                            found = true;
                        }
                    }
                }
            }

            std::swap(q, new_q);
        }

        {
            std::vector<State> states;
            while (!q.empty()) {
                states.push_back(q.top());
                q.pop();
            }
            history.push_back(states);
        }

        int position_x = source.x;
        int position_y = source.y;
        int velocity_x = last_velocity_x;
        int velocity_y = last_velocity_y;

        const State* state = nullptr;
        for (const auto& last_state : history.back()) {
            if (last_state.position_x == destination.x && last_state.position_y == destination.y) {
                state = &last_state;
                last_velocity_x = last_state.velocity_x;
                last_velocity_y = last_state.velocity_y;
                break;
            }
        }

        std::vector<Acceleration> acceleration_2d;
        while (state->last_state) {
            acceleration_2d.emplace_back(Acceleration{ state->last_acceleration_x, state->last_acceleration_y });
            state = state->last_state;
        }

        std::reverse(acceleration_2d.begin(), acceleration_2d.end());

        for (const auto& acceleration : acceleration_2d) {
            velocity_x += acceleration.x;
            position_x += velocity_x;
            velocity_y += acceleration.y;
            position_y += velocity_y;

            visited.insert({ position_x, position_y });

            std::cout << acceleration.ToDigit();
        }

        source = destination;
    }
    std::cout << std::endl;
}

int main_spaceship(int argc, char* argv[])
{
    //TestGetPath1D();
    //TestGetPath2D();

    std::cerr << "Calling Input()" << std::endl;
    Input();
    std::cerr << "Called Input()" << std::endl;

    std::cerr << "Calling InitializeTable()" << std::endl;
    InitializeTable();
    std::cerr << "Called InitializeTable()" << std::endl;

    std::cerr << "Calling InitializeMinimumSpanningTree()" << std::endl;
    InitializeMinimumSpanningTree();
    std::cerr << "Called InitializeMinimumSpanningTree()" << std::endl;

    std::cerr << "Calling InitializeVisitingOrder()" << std::endl;
    InitializeVisitingOrder();
    std::cerr << "Called InitializeVisitingOrder()" << std::endl;

    SimulatedAnnealing optimizer;
    auto optimized_state = optimizer.run();

    //OutputStrictPath(optimized_state.visiting_order);
    OutputBeamSearchPath(optimized_state.visiting_order);

    return 0;
}
