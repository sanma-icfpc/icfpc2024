#include "util.h"

#include <glog/logging.h>

DEFINE_string(problems_dir, "data/problems/",
              "Path to the directory that contains problem files.");
DEFINE_string(solutions_dir, "data/solutions/",
              "Path to the directory to store solution files.");

namespace util {

// Returns a list of file paths under `dir_path`.
std::vector<std::string> list_files(const std::string& dir_path) { return {}; }
}  // namespace util