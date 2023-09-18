#!/bin/bash
#SBATCH --time=00:10:00
#SBATCH --mem=500MB
#SBATCH --job-name=bt_sending_loop
#SBATCH --output=bt_sending_loop%j.log



# Declare arrays 
DEV=("1.0" "0.1" "0.01" "0.001")
META=("1.0" "0.1" "0.01" "0.001") 
DELAY=("true" "false" "original")

# Nested loops to iterate over permutations
for dev in "${DEV[@]}"
do
  for meta in "${META[@]}"
  do 
    for delay in "${DELAY[@]}"
    do
      echo "$dev $meta $gram"
      sbatch sending_trillions.sh $dev $meta $delay 
    done
  done
done
