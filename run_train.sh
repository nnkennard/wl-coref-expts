#!/bin/bash
#SBATCH --job-name=train_wl_coref   # Job name
#SBATCH --mail-type=END,FAIL          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=nnayak@cs.umass.edu     # Where to send mail	
#SBATCH --mem=50GB                     # Job memory request
#SBATCH --output=logs/train_wl_coref_%j.log   # Standard output and error log
#SBATCH --gres=gpu:1
#SBATCH --partition=rtx8000-long

pwd; hostname; date
python run.py train roberta
date
