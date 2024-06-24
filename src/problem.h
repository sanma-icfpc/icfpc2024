#pragma once

#include <filesystem>
#include <nlohmann/json.hpp>
#include <string>

struct Problem {
 public:
  Problem() = default;
  Problem(const nlohmann::json& json);

  static Problem read_json_file(const std::filesystem::path&);
  static Problem parse_json(const std::string& json);

  int problem_id = -1;
  std::string dummy_data;
};