#include "sample.h"

#include "problem.h"
#include "solution.h"

Solution SampleSolver::solve(const Problem& problem) {
  return std::move(Solution(problem.problem_id()));
}
