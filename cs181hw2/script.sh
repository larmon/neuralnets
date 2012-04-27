#!/usr/bin/env bash
#NUMBER recognition automated testing

for rate in {1..9}; do
  for hidden in {1..30}; do 
    python nn.py --rounds=10 --learning_rate=.$rate --hidden=$hidden >> numout.txt
    echo -e "\n \n" >> numout.txt
  done
done  

exit 0
