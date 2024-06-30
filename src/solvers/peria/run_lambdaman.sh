#!/bin/bash

PERIA_DIR=$(cd $(dirname $0) && pwd)
BASE_DIR=$(dirname $(dirname $(dirname $PERIA_DIR)))
DATA_DIR=${BASE_DIR}/data
LAMBDAMAN_DIR=${DATA_DIR}/courses/lambdaman
PROBLEMS_DIR=${LAMBDAMAN_DIR}/problems
SOLUTIONS_DIR=${LAMBDAMAN_DIR}/solutions
SOLVER=${PERIA_DIR}/lambdaman

for i in {1..20};do
    problem=${PROBLEMS_DIR}/lambdaman${i}.txt
    solution=${SOLUTIONS_DIR}/lambdaman${i}.txt
    time ${SOLVER} ${i} < ${problem} > ${solution}
    wc ${solution}
done