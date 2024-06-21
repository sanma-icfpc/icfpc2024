#include <fmt/format.h>
#include <omp.h>

#include <CLI/CLI.hpp>
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
  google::InitGoogleLogging(argv[0]);
  google::InstallFailureSignalHandler();
  google::SetStderrLogging(google::INFO);
  google::SetLogDestination(google::INFO, "main.log.");

  std::ios::sync_with_stdio(false);
  std::cin.tie(NULL);

  CLI::App app{"main module"};
  app.require_subcommand(0, 1);

  auto sub_problem_to_png = app.add_subcommand("problem-to-png");
  std::string problem_file;
  std::string output_file;
  sub_problem_to_png->add_option("problem_file", problem_file,
                                 "problem file path (JSON)");
  sub_problem_to_png->add_option("output_file", output_file,
                                 "output file path (PNG)");

  auto sub_solution_to_png = app.add_subcommand("solution-to-png");
  std::string solution_file;
  sub_solution_to_png->add_option("solution_file", solution_file,
                                  "solution file path (JSON)");
  sub_solution_to_png->add_option("output_file", output_file,
                                  "output file path (PNG)");

  auto sub_eval = app.add_subcommand("eval");
  sub_eval->add_option("solution_file", solution_file,
                       "solution file path (JSON)");

  CLI11_PARSE(app, argc, argv);

#ifndef HAVE_OPENCV_HIGHGUI
  LOG(ERROR) << "no OpenCV highgui!";
#else
  if (sub_problem_to_png->parsed()) {
    Problem problem = Problem::from_file(problem_file);
    cv::Mat img = problem.to_mat();
    cv::imwrite(output_file, img);
  }
  if (sub_solution_to_png->parsed()) {
    if (auto problem_id = guess_problem_id(solution_file)) {
      Problem problem = Problem::from_file(*problem_id);
      Solution solution = Solution::from_file(solution_file);
      cv::Mat img = solution.to_mat(problem);
      cv::imwrite(output_file, img);
    } else {
      LOG(ERROR) << "Could not guess the problem id!";
      return 1;
    }
  }
#endif

  if (sub_eval->parsed()) {
    if (auto problem_id = guess_problem_id(solution_file)) {
      Problem problem = Problem::from_file(*problem_id);
      LOG(INFO) << "Extension " << problem.extension.stringify();
      Solution solution = Solution::from_file(solution_file);
      int64_t score = compute_score(problem, solution);
      if (is_valid_solution(problem, solution, true)) {
        std::cout << format("[  VALID] score = %lld (%s)", score,
                            int_to_delimited_string(score).c_str())
                  << std::endl;
      } else {
        std::cout << format("[INVALID] score = %lld (%s)", score,
                            int_to_delimited_string(score).c_str())
                  << std::endl;
      }
      set_optimal_volumes(problem, solution);
      score = compute_score(problem, solution);
      std::cout << format("[ OPTVOL] score = %lld (%s)", score,
                          int_to_delimited_string(score).c_str())
                << std::endl;
    }
  }

  return 0;
}