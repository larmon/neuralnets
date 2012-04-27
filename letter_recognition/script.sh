#!/usr/bin/env/bash

for rate in {1..9}; do
  for hidden in {1..30}; do
    python nn.py --rounds=10 --learning_rate=.$rate --hidden=$hidden >> output2.txt
    echo -e "\n \n" >> output2.txt
  done
done

exit 0
