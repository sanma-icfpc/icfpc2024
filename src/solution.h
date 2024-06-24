#pragma once

#include <filesystem>
#include <nlohmann/json.hpp>
#include <string>

struct Solution {
 public:
  Solution(int problem_id);

  // Outputs as json file. File path is decided internally with some flags.
  void save_json_file();

 protected:
  // Converts int nlohman::json object.
  nlohmann::json as_json() const;

 public:
  // Parameters
  const int problem_id;
  std::string dummy_data;
};