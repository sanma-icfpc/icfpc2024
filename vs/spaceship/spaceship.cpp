#include <algorithm>
#include <deque>
#include <iostream>
#include <limits>
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

    int ToDigit() {
        return 1 + (x + 1) + (y + 1) * 3;
    }
};

//const constexpr int MAX_POSITION = 200000;
//const constexpr int MIN_POSITION = -MAX_POSITION;
//const constexpr int MAX_VELOCITY = 500;
//const constexpr int MIN_VELOCITY = -MAX_VELOCITY;
//const constexpr int POSITION_OFFSET = MAX_POSITION;
//const constexpr int VELOCITY_OFFSET = MAX_VELOCITY;
const constexpr int MAX_POSITION = 100;
const constexpr int MIN_POSITION = -MAX_POSITION;
const constexpr int MAX_VELOCITY = 20;
const constexpr int MIN_VELOCITY = -MAX_VELOCITY;
const constexpr int POSITION_OFFSET = MAX_POSITION;
const constexpr int VELOCITY_OFFSET = MAX_VELOCITY;
std::vector<std::vector<int>> NUM_STEPS(MAX_POSITION - MIN_POSITION + 1, std::vector<int>(MAX_VELOCITY - MIN_VELOCITY + 1, std::numeric_limits<int>::max() / 2));
std::vector<std::vector<int>> LAST_ACCELERATION(MAX_POSITION - MIN_POSITION + 1, std::vector<int>(MAX_VELOCITY - MIN_VELOCITY + 1));
std::vector<Position> POSITIONS;

void InitializeTable() {
    std::deque<State> q;
    q.push_back({ 0, 0, 0 });
    NUM_STEPS[POSITION_OFFSET][VELOCITY_OFFSET] = 0;

    while (!q.empty()) {
        State state = q.front();
        q.pop_front();

        for (int acceleration = -1; acceleration <= 1; ++acceleration) {
            State next_state = state;
            next_state.velocity += acceleration;
            next_state.position += next_state.velocity;
            next_state.num_steps += 1;

            if (!(MIN_POSITION <= next_state.position && next_state.position <= MAX_POSITION)) {
                continue;
            }

            if (!(MIN_VELOCITY <= next_state.velocity && next_state.velocity <= MAX_VELOCITY)) {
                continue;
            }

            if (NUM_STEPS[next_state.position + POSITION_OFFSET][next_state.velocity + VELOCITY_OFFSET] < next_state.num_steps) {
                continue;
            }

            NUM_STEPS[next_state.position + POSITION_OFFSET][next_state.velocity + VELOCITY_OFFSET] = next_state.num_steps;
            LAST_ACCELERATION[next_state.position + POSITION_OFFSET][next_state.velocity + VELOCITY_OFFSET] = acceleration;
            q.push_back(next_state);
        }
    }
}

int GetNumSteps1D(int start, int goal) {
    return NUM_STEPS[goal - start + POSITION_OFFSET][0];
}

void GetPath1D(int start, int goal, std::vector<int>& accelerations) {
    accelerations.clear();

    int position = goal - start;
    int velocity = 0;
    while (!(position == 0 && velocity == 0)) {
        int last_acceleration = LAST_ACCELERATION[position + POSITION_OFFSET][velocity + VELOCITY_OFFSET];
        accelerations.push_back(last_acceleration);
        position -= velocity;
        velocity -= last_acceleration;
    }

    std::reverse(accelerations.begin(), accelerations.end());
}

void TestGetPath1D() {
    std::vector<int> accelerations;
    int start = 0;
    int goal = 10;
    GetPath1D(start, goal, accelerations);

    int position = 0;
    int velocity = 0;
    for (int acceleration : accelerations) {
        velocity += acceleration;
        position += velocity;
        std::printf("(position, velocity) = (%d, %d)\n", position, velocity);
    }
}

void Input() {
    int x, y;
    while (std::cin >> x >> y) {
        POSITIONS.push_back({ x, y });
    }
}

int GetNumSteps2D(const Position& start, const Position& goal) {
    return std::max(GetNumSteps1D(start.x, start.y), GetNumSteps1D(goal.x, goal.y));
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

int main()
{
    InitializeTable();
    //TestGetPath();
    Input();
    TestGetPath2D();


    return 0;
}
