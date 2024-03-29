#!/bin/bash

# load in variables
gcdfile=$1
indir=$2
outdir=$3
design=$4
dataset=$5
part=$6
mod=$7

inputfile=${indir}/${dataset}/${design}/BaseProc/${dataset}_MUONGUN_.${part}_${design}_calibrated.i3.bz2
outfile=${dataset}_MUONGUN_.${part}_${design}_${mod}

# run the reconstruction script
ulimit -s 131072; /home/brianclark/Gen2/optical/gen2_optical_sims/analysis/2021.10_GCD_uncertainty/run_simple_reco.py -g ${gcdfile} -i ${inputfile} -p ${outfile}

# move the outputs
mv ${outfile}* ${outdir}/.
