#include <algorithm>
#include <array>
#include <deque>
#include <iostream>
#include <limits>
#include <map>
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

void InitializeMinimumSpanningTree() {
    // プリム法で最小全域木を求める。
    int num_nodes = POSITIONS.size();
    MINIMUM_SPANNING_TREE.resize(num_nodes);

    std::multimap<int, std::pair<int, int>> edges;
    std::vector<bool> visited(num_nodes);
    visited[0] = true;
    for (int destination = 1; destination < num_nodes; ++destination) {
        int cost = GetNumSteps2D(POSITIONS[0], POSITIONS[destination]);
        edges.insert(std::make_pair(cost, std::make_pair(0, destination)));
    }
    int num_visited = 1;

    int counter = 0;
    while (!edges.empty() && num_visited < num_nodes) {
        if (++counter % 10000 == 0) {
            std::cerr << "counter=" << counter << " edges.size()=" << edges.size() << std::endl;
        }

        int source = edges.begin()->second.first;
        int destination = edges.begin()->second.second;
        edges.erase(edges.begin());

        if (visited[destination]) {
            continue;
        }

        ++num_visited;

        visited[destination] = true;
        MINIMUM_SPANNING_TREE[source].push_back(destination);
        MINIMUM_SPANNING_TREE[destination].push_back(source);

        for (int new_destination = 0; new_destination < num_nodes; ++new_destination) {
            if (visited[new_destination]) {
                continue;
            }

            int cost = GetNumSteps2D(POSITIONS[destination], POSITIONS[new_destination]);
            edges.insert(std::make_pair(cost, std::make_pair(destination, new_destination)));
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

int main(int argc, char* argv[])
{
    std::cout << "solve spaceship" << argv[1] << " ";

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

    for (int order_index = 0; order_index + 1 < POSITIONS.size(); ++order_index) {
        const auto& source = POSITIONS[VISITING_ORDER[order_index]];
        const auto& destination = POSITIONS[VISITING_ORDER[order_index + 1]];
        std::vector<Acceleration> acceleration_2d;
        GetPath2D(source, destination, acceleration_2d);
        for (const auto& acceleration : acceleration_2d) {
            std::cout << acceleration.ToDigit();
        }
    }
    std::cout << std::endl;

    return 0;
}
