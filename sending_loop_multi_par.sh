#!/bin/bash
#SBATCH --time=00:10:00
#SBATCH --mem=500MB
#SBATCH --job-name=bt_sending_loop
#SBATCH --output=bt_sending_loop%j.log



# Declare arrays 
DEV=("1.0" "0.1" "0.01" "0.001")
META=("1.0" "0.1" "0.01" "0.001") 
GRAMMAR=("True" "False")

# Nested loops to iterate over permutations
for dev in "${DEV[@]}"
do
  for meta in "${META[@]}"
  do 
    for gram in "${GRAMMAR[@]}"
    do
      echo "$dev $meta $gram"
	  sbatch sending_trillions.sh $dev $meta $gram
    done
  done
done
