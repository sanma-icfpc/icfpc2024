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

DEFINE_string(solver, "sample", "The name of a solver to use.");

int main(int argc, char *argv[])
{
  gflags::ParseCommandLineFlags(&argc, &argv, /* remove_flags */ true);
  google::InitGoogleLogging(argv[0]);
  google::InstallFailureSignalHandler();
  google::SetStderrLogging(google::INFO);
  google::SetLogDestination(google::INFO, "main.log.");

  std::ios::sync_with_stdio(false);
  std::cin.tie(NULL);

  // TODO: Do something here. This is a sample main() code.

  return 0;
}
