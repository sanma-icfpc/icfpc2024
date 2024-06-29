﻿#include <algorithm>
#include <array>
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

    int ToDigit() const {
        return 1 + (x + 1) + (y + 1) * 3;
    }
};

int MAX_POSITION = 1000000;
int MIN_POSITION = -MAX_POSITION;
int MAX_VELOCITY = 500;
int MIN_VELOCITY = -MAX_VELOCITY;
int POSITION_OFFSET = MAX_POSITION;
int VELOCITY_OFFSET = MAX_VELOCITY;

std::vector<int> NUM_STEPS_RAW;
std::vector<int> LAST_ACCELERATION_RAW;

int& GetNumSteps(int position, int velocity) {
    return NUM_STEPS_RAW[(position + POSITION_OFFSET) * (MAX_VELOCITY - MIN_VELOCITY + 1) + (velocity + VELOCITY_OFFSET)];
}

int& GetLastAcceleration(int position, int velocity) {
    return LAST_ACCELERATION_RAW[(position + POSITION_OFFSET) * (MAX_VELOCITY - MIN_VELOCITY + 1) + (velocity + VELOCITY_OFFSET)];
}

std::vector<Position> POSITIONS;

void InitializeTable() {
    std::deque<State> q;
    q.push_back({ 0, 0, 0 });
    GetNumSteps(0, 0) = 0;

    int count = 0;
    while (!q.empty()) {
        if (++count % 10000000 == 0) {
            std::cerr << "q.size()=" << q.size() << " q.front().num_steps=" << q.front().num_steps << std::endl;
        }

        State state = q.front();
        q.pop_front();

        if (GetNumSteps(state.position, state.velocity) != state.num_steps) {
            continue;
        }

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

            if (GetNumSteps(next_state.position, next_state.velocity) <= next_state.num_steps) {
                continue;
            }

            GetNumSteps(next_state.position, next_state.velocity) = next_state.num_steps;
            GetLastAcceleration(next_state.position, next_state.velocity) = acceleration;
            q.push_back(next_state);
        }
    }
}

int GetNumSteps1D(int start, int goal) {
    return GetNumSteps(goal - start, 0);
}

void GetPath1D(int start, int goal, std::vector<int>& accelerations) {
    accelerations.clear();

    int position = goal - start;
    int velocity = 0;
    while (!(position == 0 && velocity == 0)) {
        int last_acceleration = GetLastAcceleration(position, velocity);
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
    POSITIONS.push_back({ 0, 0 });

    int x, y;
    int min_x = std::numeric_limits<int>::max();
    int max_x = std::numeric_limits<int>::min();
    int min_y = std::numeric_limits<int>::max();
    int max_y = std::numeric_limits<int>::min();
    while (std::cin >> x >> y) {
        min_x = std::min(x, min_x);
        max_x = std::max(x, max_x);
        min_y = std::min(y, min_y);
        max_y = std::max(y, max_y);
        POSITIONS.push_back({ x, y });
    }

    std::cerr << "min_x=" << min_x << " max_x=" << max_x << " min_y=" << min_y << " max_y=" << max_y << std::endl;

    MAX_POSITION = std::max(max_x - min_x, max_y - min_y);
    MIN_POSITION = -MAX_POSITION;
    MAX_VELOCITY = std::sqrt(MAX_POSITION) + 10;
    MIN_VELOCITY = -MAX_VELOCITY;
    POSITION_OFFSET = MAX_POSITION;
    VELOCITY_OFFSET = MAX_VELOCITY;

    NUM_STEPS_RAW.resize((MAX_POSITION - MIN_POSITION + 1) * (MAX_VELOCITY - MIN_VELOCITY + 1), std::numeric_limits<int>::max() / 2);
    LAST_ACCELERATION_RAW.resize((MAX_POSITION - MIN_POSITION + 1) * (MAX_VELOCITY - MIN_VELOCITY + 1));
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
    //TestGetPath();
    //TestGetPath2D();

    std::cerr << "Calling InitializeTable()" << std::endl;
    Input();
    std::cerr << "Called InitializeTable()" << std::endl;

    std::cerr << "Calling InitializeTable()" << std::endl;
    InitializeTable();
    std::cerr << "Called InitializeTable()" << std::endl;

    for (int position_index = 0; position_index + 1 < POSITIONS.size(); ++position_index) {
        const auto& start = POSITIONS[position_index];
        const auto& goal = POSITIONS[position_index + 1];
        std::vector<Acceleration> acceleration_2d;
        GetPath2D(start, goal, acceleration_2d);
        for (const auto& acceleration : acceleration_2d) {
            std::cout << acceleration.ToDigit();
        }
    }
    std::cout << std::endl;

    return 0;
}