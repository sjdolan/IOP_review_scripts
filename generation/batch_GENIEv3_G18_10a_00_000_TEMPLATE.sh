#!/bin/bash
#SBATCH --image=docker:wilkinsonnu/nuisance_project:genie_v3.2.0
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --time=720
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

## Output file name
TUNE=G18_10a_00_000
NEVENTS=1000000
E_MIN=0.1
E_MAX=__E_MAX__

## Where to temporarily save files
TEMPDIR=${SCRATCH}/${OUTFILE/.root/}_${THIS_SEED}

echo "Moving to SCRATCH: ${TEMPDIR}"
mkdir ${TEMPDIR}
cd ${TEMPDIR}

## Get the splines that are now needed...
cp $CFS/dune/users/cwilk/MC_inputs/${TUNE}_v320_splines.xml .

## Get the flux file
cp $CFS/dune/users/cwilk/MC_inputs/${FLUX_FILE} .

echo "Starting gevgen..."
shifter -V ${PWD}:/output --entrypoint gevgen -n ${NEVENTS} -t ${TARG} -p ${NU_PDG} \
	--cross-sections ${TUNE}_v320_splines.xml \
	--tune ${TUNE} --seed ${THIS_SEED} \
	-f ${FLUX_FILE},${FLUX_HIST} -e ${E_MIN},${E_MAX} -o ${OUTFILE}

echo "Starting PrepareGENIE..."
shifter -V ${PWD}:/output --entrypoint PrepareGENIE -i $OUTFILE -f ${FLUX_FILE},${FLUX_HIST} \
	-t $TARG -o ${OUTFILE/.root/_NUIS.root}

shifter -V ${PWD}:/output --entrypoint nuisflat -f GenericVectors -i GENIE:${OUTFILE/.root/_NUIS.root} -o ${OUTFILE/.root/_NUISFLAT.root} -q "nuisflat_SaveSignalFlags=false"
echo "Complete"

## Copy back the important files
cp ${TEMPDIR}/${OUTFILE/.root/_NUIS.root} ${OUTDIR}/.
cp ${TEMPDIR}/${OUTFILE/.root/_NUISFLAT.root} ${OUTDIR}/.

## Clean up
rm -r ${TEMPDIR}

