#!/usr/bin/env/bash

for rate in {1..4}; do
  for hidden in {1..30}; do
    echo $rate
    echo $hidden
    #python nn.py --rounds=10 --learning_rate=.$rate --hidden=$hidden >> output2.txt
    echo -e "\n \n" >> output2.txt
  done
done

exit 0
