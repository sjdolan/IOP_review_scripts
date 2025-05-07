#!/bin/bash
#SBATCH --image=docker:wilkinsonnu/nuisance_project:nuwro_19.02.2
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
INCARD=generic_NUWRO_SF.params

## Where to temporarily save files
TEMPDIR=${SCRATCH}/${OUTFILE/.root/}_${THIS_SEED}

echo "Moving to SCRATCH: ${TEMPDIR}"
mkdir ${TEMPDIR}
cd ${TEMPDIR}

## Get the flux file
cp ${INPUTS_DIR}/${FLUX_FILE} .

## Get and modify the card
cp ${INPUTS_DIR}/${INCARD} .
sed -i "s/_NU_PDG_/${NU_PDG}/g" ${INCARD}
sed -i "s/_THIS_SEED_/${THIS_SEED}/g" ${INCARD}
sed -i "s/_FLUX_FILE_/${FLUX_FILE}/g" ${INCARD}
sed -i "s/_FLUX_HIST_/${FLUX_HIST}/g" ${INCARD}

## Special target names for NuWro...
SHORT_TARG=""
if [[ $TARG == "1000080160[0.8889],1000010010[0.1111]" ]]; then
    SHORT_TARG="H2O"
elif [[ $TARG == "1000060120[0.9231],1000010010[0.0769]" ]]; then
    SHORT_TARG="CH"
elif [[ $TARG == "1000180400[1.00]" ]]; then
    SHORT_TARG="Ar"
elif [[ $TARG == "1000060120[0.85714],1000010010[0.14286]" ]]; then
    SHORT_TARG="CH2"
elif [[ $TARG == "1000060120[1.00]" ]]; then
    SHORT_TARG="C"
else
    echo "Don't know how to parse target ${TARG}... exiting..."
    exit
fi
sed -i "s/_SHORT_TARG_/${SHORT_TARG}/g" ${INCARD}

shifter -V ${PWD}:/output --entrypoint nuwro -i ${INCARD} -o ${OUTFILE} &> /dev/null
shifter -V ${PWD}:/output --entrypoint PrepareNuwro ${OUTFILE} -F ${FLUX_FILE},${FLUX_HIST},${NU_PDG}
shifter -V ${PWD}:/output --entrypoint nuisflat -f GenericVectors -i NUWRO:${OUTFILE} -o ${OUTFILE/.root/_NUISFLAT.root} -q "nuisflat_SaveSignalFlags=false"
echo "Complete"

## Copy back the important files
# cp ${TEMPDIR}/${OUTFILE} ${OUTDIR}/.
cp ${TEMPDIR}/${OUTFILE/.root/_NUISFLAT.root} ${OUTDIR}/.

## Clean up
rm -r ${TEMPDIR}
