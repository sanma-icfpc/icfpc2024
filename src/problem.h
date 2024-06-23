#pragma once

#include <filesystem>
#include <nlohmann/json.hpp>
#include <string>

class Problem {
 public:
  Problem() = default;
  Problem(const nlohmann::json& json);

  static Problem read_json_file(const std::filesystem::path&);
  static Problem parse_json(const std::string& json);

  int problem_id() const { return problem_id_; }

 private:
  int problem_id_;
};