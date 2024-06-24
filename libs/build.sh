#!/bin/bash
# This script needs to be run on bash.

echo "building fmt"
pushd $(dirname $0)/fmt 
mkdir -p build
pushd build
cmake .. -G "Unix Makefiles" || exit 1
make fmt || exit 1
popd
popd

echo "building gflags"
pushd $(dirname $0)
mkdir -p gflags_build
cmake -S gflags \
      -B gflags_build \
      -DBUILD_SHARED_LIBS:BOOL=OFF \
      -DBUILD_STATIC_LIBS:BOOL=ON \
      -DBUILD_TESTING:BOOL=OFF \
      --install-prefix $(pwd)/gflags_build \
      -G "Unix Makefiles" || exit 1
pushd gflags_build
make install
popd
popd

echo "building glog"
pushd $(dirname $0)
# do not build in glog/build since it is not listed in glog/.gitignore and thus leads to a dirty state.
mkdir -p glog_build
cmake -S glog \
      -B glog_build \
      -DWITH_GFLAGS:BOOL=ON \
      -DBUILD_SHARED_LIBS:BOOL=OFF \
      -DBUILD_TESTING:BOOL=OFF \
      -DHAVE_LIB_GFLAGS=1 \
      --install-prefix $(pwd)/glog_build \
      -G "Unix Makefiles" || exit 1
pushd glog_build
make install
popd
popd
