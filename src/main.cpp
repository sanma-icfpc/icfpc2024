#include <fmt/format.h>
#include <omp.h>

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

#include "util.h"

int main(int argc, char* argv[]) {
  gflags::ParseCommandLineFlags(&argc, &argv, /* remove_flags */ true);
  google::InitGoogleLogging(argv[0]);
  google::InstallFailureSignalHandler();
  google::SetStderrLogging(google::INFO);
  google::SetLogDestination(google::INFO, "main.log.");

  std::ios::sync_with_stdio(false);
  std::cin.tie(NULL);

  auto&& solver = Solver::GetSolver();
  for (auto&& problem_filepath : util::list_files(FLAGS_problem_dir)) {
    auto&& problem = Problem::ReadFile(problem_filepath);
    auto&& solution = solver.solve(problem);
    solution.dump(solution_filepath);
  }

  return 0;
}