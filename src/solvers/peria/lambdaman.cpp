#include <gflags/gflags.h>
#include <glog/logging.h>

#include <iostream>
#include <memory>
#include <queue>
#include <string>
#include <vector>

using State = std::pair<int, std::pair<int, int>>;

class Field {
  static constexpr int kNotVisited = 1000000000;

 public:
  static std::unique_ptr<Field> Parse(std::istream &in) {
    std::vector<std::string> field;
    std::string line;
    while (std::getline(in, line)) {
      field.push_back(line);
    }
    return std::make_unique<Field>(field);
  }

  Field(const std::vector<std::string> &raw_field)
      : raw_field_(raw_field),
        width_(raw_field[0].size()),
        height_(raw_field.size()),
        distance_(height_, std::vector<int>(width_, kNotVisited)) {
    GetStatistics();

    std::cerr << "Size: " << width_ << " x " << height_ << "\n";
    std::cerr << "From: (" << current_x_ << ", " << current_y_ << ")\n";
    std::cerr << "Num pills: " << num_pills_ << "\n";
  }

  int width() const { return width_; }
  int height() const { return height_; }
  int current_x() const { return current_x_; }
  int current_y() const { return current_y_; }
  int num_pills() const { return num_pills_; }

  std::string GetNextMove() {
    auto &&[x, y] = SearchNextPill();
    std::string action;
    int dist = distance_[y][x];
    raw_field_[y][x] = ' ';
    current_x_ = x;
    current_y_ = y;
    while (dist) {
      --dist;
      if (y > 0 && distance_[y - 1][x] == dist) {
        action.push_back('D');
        --y;
      } else if (y < height() - 1 && distance_[y + 1][x] == dist) {
        action.push_back('U');
        ++y;
      } else if (x > 0 && distance_[y][x - 1] == dist) {
        action.push_back('R');
        --x;
      } else if (x < width() - 1 && distance_[y][x + 1] == dist) {
        action.push_back('L');
        ++x;
      }
    }
    std::reverse(action.begin(), action.end());
    return action;
  }

 private:
  std::pair<int, int> SearchNextPill() {
    Initialize();
    int cx = current_x();
    int cy = current_y();
    distance_[cy][cx] = 0;
    visited_.push_back({cx, cy});
    std::queue<State> q;
    q.push({0, {cx, cy}});
    while (!q.empty()) {
      auto [dist, p] = q.front();
      q.pop();
      // std::cerr << dist << " (" << p.first << ", " << p.second << ")\n";
      ++dist;
      for (auto &&dir : dirs) {
        int x = p.first + dir.first;
        int y = p.second + dir.second;
        if (x < 0 || x >= width() || y < 0 || y >= height()) {
          continue;
        }

        char c = raw_field_[y][x];
        if (c == '#' || distance_[y][x] < dist) {
          continue;
        }
        distance_[y][x] = dist;
        visited_.push_back({x, y});
        if (c == '.') {
          return {x, y};
        }
        q.push({dist, {x, y}});
      }
    }

    return {-1, -1};
  }

 private:
  void Initialize() {
    for (auto &&[x, y] : visited_) {
      distance_[y][x] = kNotVisited;
    }
    visited_.clear();
  }

  void GetStatistics() {
    num_pills_ = 0;
    std::vector<int> neighbors(5);
    for (int i = 0; i < height_; ++i) {
      for (int j = 0; j < width_; ++j) {
        char c = raw_field_[i][j];
        if (c == '#') {
          continue;
        }

        int num_neighbors = 0;
        for (auto &&dir : dirs) {
          int x = j + dir.first;
          int y = i + dir.second;
          if (x < 0 || x >= width() || y < 0 || y >= height()) {
            continue;
          }
          if (raw_field_[y][x] != '#') {
            ++num_neighbors;
          }
        }
        ++neighbors[num_neighbors];

        if (c == '.') {
          ++num_pills_;
        }
        if (c == 'L') {
          current_x_ = j;
          current_y_ = i;
        }
      }
    }
    std::cerr << "Neighbors: " << neighbors[1] << " " << neighbors[2] << " "
              << neighbors[3] << " " << neighbors[4] << "\n";
  }

  std::vector<std::string> raw_field_;
  const int width_;
  const int height_;
  int num_pills_ = 0;
  int current_x_ = -1;
  int current_y_ = -1;

  std::vector<std::vector<int>> distance_;
  std::vector<std::pair<int, int>> visited_;
  const std::vector<std::pair<int, int>> dirs{{0, -1}, {0, 1}, {-1, 0}, {1, 0}};
};

std::string Solve(Field &field) {
  std::string solution;
  for (int i = 0; i < field.num_pills(); ++i) {
    auto &&move = field.GetNextMove();
    // std::cerr << "Move: " << move << " to (" << field.current_x() << ", "
    //           << field.current_y() << ")\n";
    solution += move;
  }
  return solution;
}

int main(int argc, char *argv[]) {
  gflags::ParseCommandLineFlags(&argc, &argv, /* remove_flags */ true);
  google::InitGoogleLogging(argv[0]);
  google::InstallFailureSignalHandler();
  google::SetStderrLogging(google::INFO);
  google::SetLogDestination(google::INFO, "lambdaman.log.");

  std::ios::sync_with_stdio(false);
  std::cin.tie(NULL);

  std::unique_ptr<Field> field = Field::Parse(std::cin);
  std::string solution = Solve(*field);
  if (argc > 1) {
    std::cout << "solve lambdaman" << argv[1] << " ";
  }
  std::cout << solution << std::endl;

  return 0;
}
