#include <iostream>
#include <set>
#include <utility>
#include <vector>

namespace FullSearch {
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
    };

    std::set<Position> POSITIONS;

    void Input() {
        POSITIONS.insert({ 0, 0 });

        int x, y;
        // ‰ŠúˆÊ’u‚ª(0,0)‚Ì‚½‚ßA0‚Å‰Šú‰»‚·‚éB
        int min_x = 0;
        int max_x = 0;
        int min_y = 0;
        int max_y = 0;
        while (std::cin >> x >> y) {
            min_x = std::min(x, min_x);
            max_x = std::max(x, max_x);
            min_y = std::min(y, min_y);
            max_y = std::max(y, max_y);
            POSITIONS.insert({ x, y });
        }

        std::cerr << "num_nodes=" << POSITIONS.size() << " min_x=" << min_x << " max_x=" << max_x << " min_y=" << min_y << " max_y=" << max_y << std::endl;
    }

    bool Traverse(int position_x, int position_y, int velocity_x, int velocity_y, std::vector<Acceleration>& accelerations, std::set<Position>& visited) {
        if (POSITIONS.size() == accelerations.size() + 1) {
            return true;
        }

        for (int acceleration_x = -1; acceleration_x <= 1; ++acceleration_x) {
            for (int acceleration_y = -1; acceleration_y <= 1; ++acceleration_y) {
                int next_velocity_x = velocity_x + acceleration_x;
                int next_velocity_y = velocity_y + acceleration_y;
                int next_position_x = position_x + next_velocity_x;
                int next_position_y = position_y + next_velocity_y;
                if (POSITIONS.find({ next_position_x, next_position_y }) == POSITIONS.end()) {
                    continue;
                }

                if (visited.find({ next_position_x, next_position_y }) != visited.end()) {
                    continue;
                }

                accelerations.push_back({ acceleration_x, acceleration_y });
                visited.insert({ next_position_x, next_position_y });
                if (Traverse(next_position_x, next_position_y, next_velocity_x, next_velocity_y, accelerations, visited)) {
                    return true;
                }
                visited.erase({ next_position_x, next_position_y });
                accelerations.pop_back();
            }
        }

        return false;
    }

    int ToDigit(int x, int y) {
        return 1 + (x + 1) + (y + 1) * 3;
    }
}

int main_full_search(int argc, char* argv[]) {
    using namespace FullSearch;

    Input();

    std::vector<Acceleration> accelerations;
    std::set<Position> visited = { { 0, 0 } };
    if (!Traverse(0, 0, 0, 0, accelerations, visited)) {
        return -1;
    }

    for (const auto& acceleration : accelerations) {
        std::cout << ToDigit(acceleration.x, acceleration.y);
    }
    std::cout << std::endl;

    return 0;
}
