#!/bin/bash
#SBATCH --time=00:10:00
#SBATCH --mem=500MB
#SBATCH --job-name=bt_sending_loop
#SBATCH --output=bt_sending_loop%j.log



# Declare arrays 
DEV=("1.0" "0.1" "0.01" "0.001")
META=("1.0" "0.1" "0.01" "0.001") 
DELAY=("True" "False")
REMAP=("True" "False")

# Nested loops to iterate over permutations
for dev in "${DEV[@]}"
do
  for meta in "${META[@]}"
  do 
    for delay in "${DELAY[@]}"
    do
      for remap in "${REMAP[@]}"
      do
        echo "$dev $meta $gram"
	      sbatch sending_trillions.sh $dev $meta $dealy $remap
      done
    done
  done
done
