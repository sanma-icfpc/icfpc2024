// include guard instead of pragma once: workaround for g++ bug
#ifndef __SANMA_STDAFX_H__
#define __SANMA_STDAFX_H__

#include <fstream>
#include <iostream>
#include <random>
#include <thread>

#ifdef _MSC_VER
#define NOMINMAX
#include <windows.h>
#undef ERROR
#else
#include <sys/time.h>
#include <time.h>
#endif

#include <gflags/gflags.h>
#include <glog/logging.h>

#endif  // __SANMA_STDAFX_H__