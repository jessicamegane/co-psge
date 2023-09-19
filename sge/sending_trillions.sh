#!/bin/bash
#SBATCH --time=12:10:00
#SBATCH --mem=500MB
#SBATCH --job-name=co-psge_job
#SBATCH --output=logs/co-psge_job%j.log


export PATH=$HOME/.local/bin:$PATH
module load Python
pip install numpy
pip install PyYAML
pip install tqdm

python -m examples.symreg --experiment_name /scratch/p288427/megalomania/co-psge --seed 1 --parameters mut_params/mut_level_1.0_0.0025.yml --grammars/regression.pybnf --gauss_sd $1 --prob_mutation_probs $2 --delay $3
