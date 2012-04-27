#!/usr/bin/env bash

for rate in {1..9}; do
  for hidden in {1..30}; do
    python nn.py --rounds=10 --learning_rate=.$rate --hidden=$hidden >> letterout.txt
    echo -e "\n \n" >> letterout.txt
  done
done

exit 0
