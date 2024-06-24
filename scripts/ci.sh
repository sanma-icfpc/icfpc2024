#!/bin/bash

set -euxo pipefail

cd "$(dirname $(dirname "$0"))"
BASE_DIR=$(pwd)
LIBS_DIR=${BASE_DIR}/libs
SCRIPTS_DIR=${BASE_DIR}/scrips

# HACK: VS2022 と WSL で pwd を合わせる
pushd vs/ || echo ""
${SCRIPTS_DIR}/build.sh
../src/test --gtest_output=xml:test/test_result_ci.xml
popd
