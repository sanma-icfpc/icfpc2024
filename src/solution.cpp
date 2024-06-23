#include "solution.h"

#include <fmt/format.h>

#include <filesystem>
#include <fstream>
#include <nlohmann/json.hpp>

#include "util.h"

using Json = nlohmann::json;

Solution::Solution(int problem_id) : problem_id_(problem_id) {}

void Solution::save_json_file() {
  auto&& json = as_json();

  std::filesystem::path filepath =
      FLAGS_solutions_dir + fmt::format("/solution_%04d.json", problem_id_);
  std::ofstream ofs(filepath);
  ofs << json << "\n";
}

nlohmann::json Solution::as_json() const {
  Json json;
  json["problem_id"] = problem_id_;
  return json;
}
