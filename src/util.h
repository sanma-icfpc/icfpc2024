#pragma once

#include <stdafx.h>

#include <string>
#include <vector>
#ifdef _MSC_VER
#include <ppl.h>
#endif

#include <gflags/gflags.h>

DECLARE_string(problems_dir);
DECLARE_string(solutions_dir);

namespace util {

// Returns a list of file paths under the directory.
std::vector<std::string> list_files(const std::string& dir_path);

}  // namespace util
