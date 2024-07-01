#!/bin/bash

PERIA_DIR=$(cd $(dirname $0) && pwd)
BASE_DIR=$(dirname $(dirname $(dirname $PERIA_DIR)))
DATA_DIR=${BASE_DIR}/data
SPACESHIP_DIR=${DATA_DIR}/courses/spaceship
PROBLEMS_DIR=${SPACESHIP_DIR}/problems
SOLUTIONS_DIR=${SPACESHIP_DIR}/solutions
SOLVER=${PERIA_DIR}/spaceship

for i in {1..10};do
    problem=${PROBLEMS_DIR}/spaceship${i}.txt
    solution=${SOLUTIONS_DIR}/spaceship${i}.txt
    time ${SOLVER} ${i} < ${problem} | tee ${solution}
    wc ${solution}
done