LIB_PATH=$(abspath ../libs)
BUILD_PATH=build
GTEST_DIR=$(LIB_PATH)/gtest/googletest

CXXFLAGS+=-O2 -Wall -Wno-sign-compare -std=c++2a -march=native
CXXFLAGS+=-Wno-unused-variable -Wno-unused-function -Wno-deprecated-anon-enum-enum-conversion
CXXFLAGS+=-I.
CXXFLAGS+=-MMD -MP -fopenmp
CXXFLAGS+=-include stdafx.h


# header-only libraries
CXXFLAGS+=-I$(LIB_PATH)/json/include

# pre-built libraries
CXXFLAGS+=-I$(LIB_PATH)/fmt/include
LDFLAGS+=-L$(LIB_PATH)/fmt/build -lfmt

CXXFLAGS+=-I$(LIB_PATH)/gflags_build/include
LDFLAGS+=-L$(LIB_PATH)/gflags_build/lib -lgflags

CXXFLAGS+=-DGLOG_USE_GLOG_EXPORT=1 -I$(LIB_PATH)/glog_build/include
LDFLAGS+=-L$(LIB_PATH)/glog_build/lib -lglog

CXXFLAGS+=-I/usr/include/opencv4 -I/mingw64/include/opencv4 -DUSE_OPENCV -fopenmp
LDFLAGS+=-lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs

# Debug
LDFLAGS+=-lpthread
#CXXFLAGS+=-g
#CXXFLAGS+=-pg
#CXXFLAGS+=-DNDEBUG

# add your cpp files here:
SRCS+=util.cpp problem.cpp solution.cpp solver.cpp icfp.cpp
OBJS=$(SRCS:%.cpp=$(BUILD_PATH)/%.o)
DEPS=$(SRCS:%.cpp=$(BUILD_PATH)/%.d)

# add your stable header files here to include them in the precompiled header:
PCH_HEADERS=
PCH_SRC=
PCH_OUT=

# do not edit below:
MAIN_SRCS=$(SRCS) main.cpp
MAIN_OBJS=$(MAIN_SRCS:%.cpp=$(BUILD_PATH)/%.o)
MAIN_DEPS=$(MAIN_SRCS:%.cpp=$(BUILD_PATH)/%.d)

SOLVER_SRCS=$(wildcard solvers/*.cpp)
SOLVER_OBJS=$(SOLVER_SRCS:%.cpp=$(BUILD_PATH)/%.o)
SOLVER_DEPS=$(SOLVER_SRCS:%.cpp=$(BUILD_PATH)/%.d)
SOLVER_BUILD_PATH=build/solvers

GTEST_SRCS=$(GTEST_DIR)/src/gtest-all.cc $(GTEST_DIR)/src/gtest_main.cc
TEST_BUILD_PATH=build/tests
TEST_CXXFLAGS=-I$(GTEST_DIR) -I$(GTEST_DIR)/include -fopenmp
TEST_LDFLAGS=$(LDFLAGS) -lpthread
TEST_SRCS=$(wildcard tests/*.cpp) $(SRCS)
TEST_OBJS=$(TEST_SRCS:%.cpp=$(BUILD_PATH)/%.o)
TEST_DEPS=$(TEST_SRCS:%.cpp=$(BUILD_PATH)/%.d)
$(TEST_OBJS): CXXFLAGS+=$(TEST_CXXFLAGS)

TARGETS+=solver test

.PHONY: all
all: dirs $(TARGETS)

.PHONY: clean
clean:
	rm -fr $(BUILD_PATH) $(TARGETS) $(PCH_OUT)

.PHONY: dirs
dirs:
	@mkdir -p $(BUILD_PATH) $(TEST_BUILD_PATH) $(SOLVER_BUILD_PATH) $(K3SOLVER_BUILD_PATH) $(TSSOLVER_BUILD_PATH)

$(PCH_OUT): $(PCH_SRC) $(PCH_HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@
$(BUILD_PATH)/%.o: %.cpp $(PCH_OUT)
	$(CXX) $(CXXFLAGS) -c $< -o $@

k3solver: $(K3SOLVER_OBJS)
	$(CXX) $(CXXFLAGS) -Wall $^ -o $@ $(LDFLAGS)

tssolver: $(TSSOLVER_OBJS)
	$(CXX) $(CXXFLAGS) -Wall $^ -o $@ $(LDFLAGS)

solver: $(MAIN_OBJS) $(SOLVER_OBJS)
	$(CXX) $(CXXFLAGS) -Wall $^ -o $@ $(LDFLAGS)

test: $(GTEST_SRCS) $(TEST_OBJS) $(OBJS)
	$(CXX) $(TEST_CXXFLAGS) $^ -o $@ $(TEST_LDFLAGS)

-include $(DEPS) $(MAIN_DEPS) $(SOLVER_DEPS)
