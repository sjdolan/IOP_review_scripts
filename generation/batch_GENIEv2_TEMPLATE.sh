#!/bin/bash
#SBATCH --image=docker:wilkinsonnu/nuisance_project:genie_v2.12.10
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --time=1440
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=4GB

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

## These are the same for all jobs
NEVENTS=1000000
E_MIN=__E_MIN__
E_MAX=__E_MAX__
CONFIG=ValenciaQEBergerSehgalCOHRES
GXMLPATH=/opt/generators/GENIE/R-2_12_10/genie_xsec/${CONFIG}
INPUTS_DIR=${PWD}/MC_inputs

## Where to temporarily save files
tempDir=${SCRATCH}/${OUTFILE/.root/}_${THIS_SEED}

echo "Moving to SCRATCH: ${tempDir}"
mkdir ${tempDir}
cd ${tempDir}

## Get the flux file
cp ${INPUTS_DIR}/${FLUX_FILE} .

echo "Starting gevgen..."
shifter -V ${PWD}:/output --entrypoint /bin/sh -c "export GXMLPATH=${GXMLPATH}; gevgen -n ${NEVENTS} -t ${TARG} -p ${nuType} --cross-sections ${GXMLPATH}/gxspl-FNALsmall.xml.gz --event-generator-list Default+CCMEC -f ${FLUX_FILE},${FLUX_HIST} -e ${E_MIN},${E_MAX} -o ${OUTFILE} --seed ${THIS_SEED}"

echo "Starting PrepareGENIE..."
shifter -V ${PWD}:/output --entrypoint PrepareGENIE -i $OUTFILE -f ${FLUX_FILE},${FLUX_HIST} \
	-t $TARG -o ${OUTFILE/.root/_NUIS.root}

shifter -V ${PWD}:/output --entrypoint nuisflat -f GenericVectors -i GENIE:${OUTFILE/.root/_NUIS.root} -o ${OUTFILE/.root/_NUISFLAT.root} -q "nuisflat_SaveSignalFlags=false"
echo "Complete"

## Copy back the important files
# cp ${tempDir}/${OUTFILE/.root/_NUIS.root} ${OUTDIR}/.
cp ${tempDir}/${OUTFILE/.root/_NUISFLAT.root} ${OUTDIR}/.

## Clean up
rm -r ${tempDir}
