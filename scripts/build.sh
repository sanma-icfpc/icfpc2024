#!/bin/bash

set -euxo pipefail
cd "$(dirname $(dirname "$0"))"
BASE_DIR=$(pwd)
LIBS_DIR=${BASE_DIR}/libs

${LIBS_DIR}/build.sh
make -j8 -B -C src dirs solver test

mkdir -p out
cp src/solver out/
