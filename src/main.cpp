#include <fmt/format.h>
#include <omp.h>

#include <memory>
#include <nlohmann/json.hpp>

#ifdef USE_OPENCV
#ifdef __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-enum-enum-conversion"
#endif
#include <opencv2/core.hpp>
#include <opencv2/core/utils/logger.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif
#endif

#include "problem.h"
#include "solution.h"
#include "solver.h"
#include "solvers/sample.h"
#include "util.h"

DEFINE_string(solver, "sample", "The name of a solver to use.");

std::unique_ptr<Solver> get_solver();

int main(int argc, char* argv[]) {
  gflags::ParseCommandLineFlags(&argc, &argv, /* remove_flags */ true);
  google::InitGoogleLogging(argv[0]);
  google::InstallFailureSignalHandler();
  google::SetStderrLogging(google::INFO);
  google::SetLogDestination(google::INFO, "main.log.");

  std::ios::sync_with_stdio(false);
  std::cin.tie(NULL);

  auto&& solver = get_solver();
  for (auto&& problem_filepath : util::list_files(FLAGS_problems_dir)) {
    auto&& problem = Problem::read_json_file(problem_filepath);
    auto&& solution = solver->solve(problem);
    solution.save_json_file();
  }

  return 0;
}

std::unique_ptr<Solver> get_solver() {
  auto& name = FLAGS_solver;
  if (name == "sample") {
    return std::make_unique<SampleSolver>();
  }

  // Fallback.
  return std::make_unique<SampleSolver>();
}