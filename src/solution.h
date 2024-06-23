#pragma once

#include <filesystem>
#include <nlohmann/json.hpp>
#include <string>

class Solution {
 public:
  Solution() = default;
  Solution(int problem_id);

  // Output as json file. File path is decided internally with some flags.
  void save_json_file();

  nlohmann::json as_json() const;

 private:
  const int problem_id_;
};