#include <gflags/gflags.h>
#include <glog/logging.h>

#include <algorithm>
#include <cstdio>
#include <iostream>
#include <map>
#include <memory>
#include <queue>
#include <set>
#include <string>
#include <vector>

using Point = std::pair<int, int>;

Point operator+(const Point &lhs, const Point &rhs) {
  return {lhs.first + rhs.first, lhs.second + rhs.second};
}

std::ostream &operator<<(std::ostream &os, const Point &point) {
  return os << "(" << point.first << ", " << point.second << ")";
}

static const std::vector<std::pair<char, Point>> kAccels{
    {'7', {-1, 1}},  {'8', {0, 1}},  {'9', {1, 1}},
    {'4', {-1, 0}},  {'5', {0, 0}},  {'6', {1, 0}},
    {'1', {-1, -1}}, {'2', {0, -1}}, {'3', {1, -1}},
};

class Solver {
 public:
  Solver(const std::vector<Point> &points) : points_(points) {
    GetStatistics();

    std::sort(points_.begin(), points_.end());
    points_.erase(std::unique(points_.begin(), points_.end()), points_.end());
    for (int i = 0; i < points_.size(); ++i) {
      indexs_[points_[i]] = i;
    }
  }

  std::string Solve() {
    Point point(0, 0);
    Point velocity(0, 0);
    std::vector<bool> visited(points_.size(), false);

    if (Search(point, velocity, visited, points_.size())) {
      std::reverse(control_.begin(), control_.end());
      return control_;
    }
    return "Fail";
  }

 private:
  bool Search(const Point &point, const Point &velocity,
              std::vector<bool> &visited, int n) {
    if (n == 0) {
      return true;
    }
    --n;

    Point destination{point + velocity};
    for (auto &&acc : kAccels) {
      Point landing{destination + acc.second};
      auto iter = indexs_.find(landing);
      if (iter == indexs_.end()) {
        continue;
      }
      const int id = iter->second;
      if (visited[id]) {
        continue;
      }

      auto vel{velocity + acc.second};
      visited[id] = true;
      if (Search(landing, vel, visited, n)) {
        control_.push_back(acc.first);
        return true;
      }
      visited[id] = false;
    }

    return false;
  }

  void GetStatistics() {
    int min_x = 1e9, max_x = -1e9, min_y = 1e9, max_y = -1e9;
    for (const auto &point : points_) {
      min_x = std::min(min_x, static_cast<int>(point.first));
      max_x = std::max(max_x, static_cast<int>(point.first));
      min_y = std::min(min_y, static_cast<int>(point.second));
      max_y = std::max(max_y, static_cast<int>(point.second));
    }
    LOG(INFO) << "(" << min_x << ", " << min_y << ") - (" << max_x << ", "
              << max_y << ")\n";
    LOG(INFO) << "# Points: " << points_.size() << "\n";
  }

  std::vector<Point> points_;
  std::map<Point, int> indexs_;
  std::string control_;
};

int main(int argc, char *argv[]) {
  gflags::ParseCommandLineFlags(&argc, &argv, /* remove_flags */ true);
  google::InitGoogleLogging(argv[0]);
  google::InstallFailureSignalHandler();
  google::SetStderrLogging(google::INFO);
  google::SetLogDestination(google::INFO, "spaceship.log.");

  std::ios::sync_with_stdio(false);
  std::cin.tie(NULL);

  std::vector<Point> points;
  for (int x, y; std::cin >> x >> y;) {
    points.emplace_back(x, y);
  }

  Solver solver(points);
  points.clear();

  std::string solution = solver.Solve();
  if (argc > 1) {
    std::cout << "solve spaceship" << argv[1] << " ";
  }
  std::cout << solution << std::endl;

  return 0;
}
