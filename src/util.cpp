#include "util.h"

#include <glog/logging.h>

#include <filesystem>

DEFINE_string(problems_dir, "data/problems/",
              "Path to the directory that contains problem files.");
DEFINE_string(solutions_dir, "data/solutions/",
              "Path to the directory to store solution files.");

namespace util {

// Returns a list of file paths under `dir_path`.
std::vector<std::string> list_files(const std::string& dir_path) {
  std::vector<std::string> file_paths;
  for (auto& path : std::filesystem::directory_iterator(dir_path)) {
    file_paths.push_back(path.path().string());
  }
  return file_paths;
}

}  // namespace util