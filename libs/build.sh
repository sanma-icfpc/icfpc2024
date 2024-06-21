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

echo "building glog"
pushd $(dirname $0)
# do not build in glog/build since it is not listed in glog/.gitignore and thus leads to a dirty state.
mkdir -p glog_build
cmake -DBUILD_TESTING:BOOL=OFF -DWITH_GFLAGS:BOOL=OFF \
      -S glog \
      -B glog_build \
      --install-prefix $(pwd)/glog_build \
      -G "Unix Makefiles" || exit 1
pushd glog_build
make install
popd
