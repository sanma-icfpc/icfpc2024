#include "sample.h"

#include "problem.h"
#include "solution.h"

Solution SampleSolver::solve(const Problem& problem) {
  LOG(INFO) << "Solving problem #" << problem.problem_id;
  // TODO: Measure running time in solve().
  Solution solution(problem.problem_id);
  solution.dummy_data = problem.dummy_data;
  return solution;
}
