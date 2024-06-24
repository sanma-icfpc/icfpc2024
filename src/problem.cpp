#include "problem.h"

#include <filesystem>
#include <fstream>
#include <nlohmann/json.hpp>
#include <string>

using Json = nlohmann::json;

Problem::Problem(const nlohmann::json& json) {
  if (json.contains("problem_id")) {
    problem_id = json["problem_id"];
  }
  if (json.contains("dummy_data")) {
    dummy_data = json["dummy_data"];
  }
}

// static
Problem Problem::read_json_file(const std::filesystem::path& file_path) {
  std::ifstream ifs(file_path);
  Json data = Json::parse(ifs);
  return Problem(data);
}

// static
Problem Problem::parse_json(const std::string& json) {
  Json data = Json::parse(json);
  return Problem(data);
}
