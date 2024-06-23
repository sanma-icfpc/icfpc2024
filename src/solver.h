#pragma once

#include "problem.h"
#include "solution.h"

// Interface of Solvers.
class Solver {
 public:
  Solver() = default;

  virtual Solution solve(const Problem&) = 0;
};