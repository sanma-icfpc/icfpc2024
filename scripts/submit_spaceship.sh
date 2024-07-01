#!/bin/sh
for i in {25..25}
do
  echo "${i}"

  echo "Sending raw solution."
  cat data/courses/spaceship/solutions/spaceship${i}.txt | python ./scripts/command.py

  # python scripts/icfp_compression.py data/courses/spaceship/solutions/spaceship${i}.txt

  # echo "Sending base9 solution."
  # cat data/courses/spaceship/solutions/spaceship${i}.base9.txt | python ./scripts/command.py --no-send-translate

  # echo "Sending rle solution."
  # cat data/courses/spaceship/solutions/spaceship${i}.rle.txt | python ./scripts/command.py --no-send-translate
done
