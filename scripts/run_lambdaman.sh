#!/bin/bash

SCRIPT_DIR=$(dirname $(realpath $0))
BASE_DIR=$(dirname $SCRIPT_DIR)
DATA_DIR=${BASE_DIR}/data/courses/lambdaman
PROBLEM_DIR=${DATA_DIR}/problems
SOLUTION_DIR=${DATA_DIR}/solutions
SCRIPT=${SCRIPT_DIR}/lambdaman_greedy.py

problems=(14 15 16 17 18 19 20)
#problems=(6 9 10)
#for i in $(seq 1 20); do
for i in ${problems[@]}; do
    problem=${PROBLEM_DIR}/lambdaman${i}.txt
    solution=${SOLUTION_DIR}/lambdaman${i}.txt
    echo "Lambdaman ${i}"
    echo -n "solve lambdaman" > ${solution}
    echo -n ${i} >> ${solution}
    echo -n " " >> ${solution}
    python3 ${SCRIPT} < ${problem} >> ${solution}
    python3 icfp_compression.py ${solution}
done
