#!/bin/bash
#SBATCH --image=docker:wilkinsonnu/nuisance_project:neut_5.6.2
#SBATCH --account=dune
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --time=1440
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

## Place for storing common inputs
INPUTS_DIR=${PWD}/MC_inputs
INCARD=generic_NEUT.card

## Where to temporarily save files
TEMPDIR=${SCRATCH}/${OUTFILE/.root/}_${THIS_SEED}

echo "Moving to SCRATCH: ${TEMPDIR}"
mkdir ${TEMPDIR}
cd ${TEMPDIR}

## Setup the random file for the job
echo "${THIS_SEED} $((THIS_SEED+1)) $((THIS_SEED+2)) $((THIS_SEED+3)) $((THIS_SEED+4))" > ranfile.txt
export RANFILE=ranfile.txt

## Sort out the inputs
cp ${INPUTS_DIR}/${FLUX_FILE} .
cp ${INPUTS_DIR}/${INCARD} .
sed -i "s/_NU_PDG_/${NU_PDG}/g" ${INCARD}
sed -i "s/_FLUX_FILE_/${FLUX_FILE}/g" ${INCARD}
sed -i "s/_FLUX_HIST_/${FLUX_HIST}/g" ${INCARD}

## NEUT target info
PROTONS=0
NEUTRONS=0
NUCLEONS=0
HYDROGEN=0
if [[ $TARG == "1000080160[0.8889],1000010010[0.1111]" ]]; then
    PROTONS=8
    NEUTRONS=8
    NUCLEONS=16
    HYDROGEN=2
elif [[ $TARG == "1000060120[0.9231],1000010010[0.0769]" ]]; then
    PROTONS=6
    NEUTRONS=6
    NUCLEONS=12
    HYDROGEN=1
elif [[ $TARG == "1000180400[1.00]" ]]; then
    PROTONS=18
    NEUTRONS=22
    NUCLEONS=40
    HYDROGEN=0
elif [[ $TARG == "1000060120[0.85714],1000010010[0.14286]" ]]; then
    PROTONS=6
    NEUTRONS=6
    NUCLEONS=12
    HYDROGEN=2
elif [[ $TARG == "1000060120[1.00]" ]]; then
    PROTONS=6
    NEUTRONS=6
    NUCLEONS=12
    HYDROGEN=0
else
    echo "Don't know how to parse target ${TARG}... exiting..."
    exit
fi
sed -i "s/_PROTONS_/${PROTONS}/g" ${INCARD}
sed -i "s/_NEUTRONS_/${NEUTRONS}/g" ${INCARD}
sed -i "s/_NUCLEONS_/${NUCLEONS}/g" ${INCARD}
sed -i "s/_HYDROGEN_/${HYDROGEN}/g" ${INCARD}

shifter -V ${PWD}:/output --entrypoint neutroot2 ${INCARD} ${OUTFILE} &> /dev/null
shifter -V ${PWD}:/output --entrypoint nuisflat -f GenericVectors -i NEUT:${OUTFILE} -o ${OUTFILE/.root/_NUISFLAT.root} -q "nuisflat_SaveSignalFlags=false"

echo "Complete"

## Copy back the important files
# cp ${TEMPDIR}/${OUTFILE} ${OUTDIR}/.
cp ${TEMPDIR}/${OUTFILE/.root/_NUISFLAT.root} ${OUTDIR}/.

## Clean up
rm -r ${TEMPDIR}
