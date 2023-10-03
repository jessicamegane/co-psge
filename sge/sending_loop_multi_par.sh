#!/bin/bash
#SBATCH --time=00:10:00
#SBATCH --mem=500MB
#SBATCH --job-name=bt_sending_loop
#SBATCH --output=bt_sending_loop%j.log



# Declare arrays 
DEV=("0.01" "0.001")
META=("1.0" "0.1") 
DELAY=("True" "False" "original")
MUT_R=("0.1" "0.01")
RUN=($(seq 0 1 30))
# Nested loops to iterate over permutations
for dev in "${DEV[@]}"
do
  for meta in "${META[@]}"
  do 
    for mut_r in "${MUT_R[@]}"
    do
      for delay in "${DELAY[@]}"
      do
        for run in "${RUN[@]}"
        do
          echo "dev: $dev, meta: $meta, delay: $delay, start_mut_rate: $mut_r, run: $run"
          sbatch sending_trillions.sh $dev $meta $delay $mut_r $run
        done
      done
    done
  done
done
