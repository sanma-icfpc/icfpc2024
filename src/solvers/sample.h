#pragma once

#include "solver.h"

class SampleSolver : public Solver {
 public:
  SampleSolver() = default;

  Solution solve(const Problem&) override;
};