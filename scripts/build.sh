#!/bin/bash

set -euxo pipefail
cd "$(dirname $(dirname "$0"))"
BASE_DIR=$(pwd)
LIBS_DIR=${BASE_DIR}/libs

BUILD_LIBS=0

while (( $# > 0 ))
do
  case $1 in
    -l | --libs)
      BUILD_LIBS=1
      ;;
  esac
  shift
done

if [ ${BUILD_LIBS} -eq 1 ]; then
  ${LIBS_DIR}/build.sh
fi

make -j8 -B -C src dirs solver test
mkdir -p out
cp src/solver out/
