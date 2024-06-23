#include "util.h"

#include <glog/logging.h>

DEFINE_string(problem_dir, "data/problems/",
              "Path to the directory that contains problem files.");

namespace util {

std::vector<std::string> get_files() { return {}; }

}  // namespace util