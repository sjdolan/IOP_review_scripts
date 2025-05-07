#!/bin/bash
#SBATCH --image=docker:wilkinsonnu/nuisance_project:gibuu_2025p1
#SBATCH --account=dune
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --time=720
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=4GB
#SBATCH --module=none

## These change for each job
THIS_SEED=__THIS_SEED__
FILE_NUM=__FILE_NUM__
NU_PDG=__NU_PDG__
OUTDIR=__OUTDIR__
FLUX_FILE=__FLUX_FILE__
FLUX_HIST=__FLUX_HIST__
TARG=__TARG__
ROOT_NAME=__ROOT_NAME__
OUTFILE=__OUTFILE__
OUTFILEH=${OUTFILE/.root/_H.root}
OUTFILENUIS=${OUTFILE/.root/_NUISFLAT.root}

## Place for storing common inputs
INPUTS_DIR=${PWD}/MC_inputs
INCARD=${OUTFILE/.root/.job}
INCARDH=${OUTFILE/.root/_H.job}

## FIX this for now (5000 used previously, but need as many as possible... maybe needs to be target dependent
## 20k seems okay for 4GB RAM
NUM_ENSEMBLES=20000

## Where to temporarily save files
TEMP_DIR=${SCRATCH}/${outFile/.root/}_${THIS_SEED}

echo "Moving to SCRATCH: ${TEMP_DIR}"
mkdir ${TEMP_DIR}
cd ${TEMP_DIR}

## Sort out the flux
cp ${INPUTS_DIR}/make_gibuu_flux.py .
cp ${INPUTS_DIR}/${FLUX_FILE} .
shifter --entrypoint python3 make_gibuu_flux.py ${FLUX_FILE} ${FLUX_HIST} gibuu_flux.dat

## Assemble the input cards
cp ${INPUTS_DIR}/generic_GiBUU.job ${INCARD}
cp ${INPUTS_DIR}/generic_GiBUU.job ${INCARDH}

## GiBUU has some custom conventions, so work with them
## This assumes we only want CC...
PROC=$(( NU_PDG > 0 ? 2 : (NU_PDG < 0 ? -2 : 0) ))
ABS_NU_PDG=$(( NU_PDG < 0 ? -NU_PDG : NU_PDG ))
NU_FLAV=$(( ABS_NU_PDG == 12 ? 1 : (ABS_NU_PDG == 14 ? 2 : 3) ))

## Ugly way to parse the target
PROTONS=0
NUCLEONS=0
HYDROGEN=0
FLATINPUTSTRING=""

if [[ $TARG == "1000080160[0.8889],1000010010[0.1111]" ]]; then
    PROTONS=8
    NUCLEONS=16
    HYDROGEN=2
    FLATINPUTSTRING=${OUTFILE},${OUTFILEH},${OUTFILEH}
elif [[ $TARG == "1000060120[0.9231],1000010010[0.0769]" ]]; then
    PROTONS=6
    NUCLEONS=12
    HYDROGEN=1
    FLATINPUTSTRING=${OUTFILE},${OUTFILEH}
elif [[ $TARG == "1000180400[1.00]" ]]; then
    PROTONS=18
    NUCLEONS=40
    HYDROGEN=0
    FLATINPUTSTRING=${OUTFILE}
elif [[ $TARG == "1000060120[0.85714],1000010010[0.14286]" ]]; then
    PROTONS=6
    NUCLEONS=12
    HYDROGEN=2
    FLATINPUTSTRING=${OUTFILE},${OUTFILEH},${OUTFILEH}
elif [[ $TARG == "1000060120[1.00]" ]]; then
    PROTONS=6
    NUCLEONS=12
    HYDROGEN=0
    FLATINPUTSTRING=${OUTFILE}
elif [[ $TARG == "1000080160[1.00]" ]]; then
    PROTONS=8
    NUCLEONS=16
    HYDROGEN=0
    FLATINPUTSTRING=${OUTFILE}
else
    echo "Don't know how to parse target ${TARG}... exiting..."
    exit
fi

## Sort the main card
sed -i "s/_THIS_SEED_/${THIS_SEED}/g" ${INCARD}
sed -i "s/_THIS_FLUX_FILE_/gibuu_flux.dat/g" ${INCARD}
sed -i "s/_PROC_/${PROC}/g" ${INCARD}
sed -i "s/_NU_FLAV_/${NU_FLAV}/g" ${INCARD}
sed -i "s/_PROTONS_/${PROTONS}/g" ${INCARD}
sed -i "s/_NUCLEONS_/${NUCLEONS}/g" ${INCARD}
sed -i "s/_NUM_ENSEMBLES_/${NUM_ENSEMBLES}/g" ${INCARD}

## Sort a hydrogen card (may not be needed)
sed -i "s/_THIS_SEED_/$((THIS_SEED+1))/g" ${INCARDH}
sed -i "s/_THIS_FLUX_FILE_/gibuu_flux.dat/g" ${INCARDH}
sed -i "s/_PROC_/${PROC}/g" ${INCARDH}
sed -i "s/_NU_FLAV_/${NU_FLAV}/g" ${INCARDH}
sed -i "s/_PROTONS_/1/g" ${INCARDH}
sed -i "s/_NUCLEONS_/1/g" ${INCARDH}
sed -i "s/_NUM_ENSEMBLES_/${NUM_ENSEMBLES}/g" ${INCARDH}

## Process the main (nuclear) card
shifter -V ${PWD}:/output --entrypoint /opt/generators/GiBUU/GiBUU.x < ${INCARD}
shifter -V ${PWD}:/output --entrypoint PrepareGiBUU -i EventOutput.Pert.00000001.root -f gibuu_flux.dat -o ${OUTFILE} &> /dev/null

## If there's hydrogen in the target, also process that card
if (( ${HYDROGEN} != 0 )); then
    rm EventOutput.Pert.00000001.root
    shifter -V ${PWD}:/output --entrypoint /opt/generators/GiBUU/GiBUU.x < ${INCARDH}
    shifter -V ${PWD}:/output --entrypoint PrepareGiBUU -i EventOutput.Pert.00000001.root -f gibuu_flux.dat -o ${OUTFILEH} &> /dev/null
fi

## Need to set the input here depending on whether the hydrogen sample needs to be included...
shifter -V ${PWD}:/output --entrypoint nuisflat -f GenericVectors -i GiBUU:${FLATINPUTSTRING} -o ${OUTFILENUIS} -q "nuisflat_SaveSignalFlags=false"
echo "Complete"

## Copy back the important files
cp ${TEMP_DIR}/${OUTFILENUIS} ${OUTDIR}/.

## Clean up
rm -r ${TEMP_DIR}
