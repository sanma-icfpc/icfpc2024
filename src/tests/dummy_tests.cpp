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
