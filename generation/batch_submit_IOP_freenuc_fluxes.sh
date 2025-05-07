#!/bin/bash

## If I want to pile more on later
FIRST_JOB=0
LAST_JOB=9

FIRST_CONFIG=0
LAST_CONFIG=3

## (Omit the last two here)
name_arr=( "DUNEND_FHC_numu_neutron" "DUNEND_RHC_numubar_neutron" \
	   "DUNEND_FHC_numu_proton" "DUNEND_RHC_numubar_proton" )

nu_pdg_arr=( 14 -14 \
	     14 -14 \
	   )

emin_arr=( 0.1 0.1 \
	   0.1 0.1 \
         )

emax_arr=( 50 50 \
	   50 50 \
	 )

targ_arr=( "1000000010[1.00]" "1000000010[1.00]" \
	   "1000010010[1.00]" "1000010010[1.00]" \
	 )

flux_file_arr=( "DUNE_OptimizedEngineeredNov2017_REGULAR.root" "DUNE_OptimizedEngineeredNov2017_REGULAR.root" \
		"DUNE_OptimizedEngineeredNov2017_REGULAR.root" "DUNE_OptimizedEngineeredNov2017_REGULAR.root" \
	      )

flux_hist_arr=( "numu_NDFHC_flux" "numubar_NDRHC_flux" \
		"numu_NDFHC_flux" "numubar_NDRHC_flux" \
	      )

## Loop over templates
for GENERATOR in GENIEv3_G18_10a_00_000 
do
    for i in $(seq ${FIRST_CONFIG} ${LAST_CONFIG}); do
	
	OUTDIR="${CFS}/dune/users/cwilk/MC_IOP_review/${GENERATOR}"
	
	if [ ! -d "${OUTDIR}" ]; then
	    mkdir -p ${OUTDIR}
	fi
	
	TEMPLATE=batch_${GENERATOR}_TEMPLATE.sh

	for JOB in $(seq ${FIRST_JOB} ${LAST_JOB}); do
	    
	    printf -v PADJOB "%04d" $JOB
	    
	    OUTFILE="${name_arr[$i]}_${GENERATOR}_1M_${PADJOB}.root"
	    
	    ## Check if file has already been processed
	    if [ -f "${OUTDIR}/${OUTFILE/.root/_NUISFLAT.root}" ]; then
                continue
	    fi
	    echo "Processing ${OUTFILE}"
	    
	    ## Copy the template
	    THIS_TEMP=${TEMPLATE/_TEMPLATE/_${name_arr[$i]}_${PADJOB}}
	    cp ${TEMPLATE} ${THIS_TEMP}
	    
	    ## Set everything important...
	    sed -i "s/__THIS_SEED__/${RANDOM}/g" ${THIS_TEMP}
	    sed -i "s/__FILE_NUM__/${PADJOB}/g" ${THIS_TEMP}
	    sed -i "s/__NU_PDG__/${nu_pdg_arr[$i]}/g" ${THIS_TEMP}
	    sed -i "s/__OUTDIR__/${OUTDIR//\//\\/}/g" ${THIS_TEMP}
	    sed -i "s/__OUTFILE__/${OUTFILE}/g" ${THIS_TEMP}
	    sed -i "s/__FLUX_FILE__/${flux_file_arr[$i]}/g" ${THIS_TEMP}
	    sed -i "s/__FLUX_HIST__/${flux_hist_arr[$i]}/g" ${THIS_TEMP}
            sed -i "s/__TARG__/${targ_arr[$i]}/g" ${THIS_TEMP}
            sed -i "s/__ROOT_NAME__/${name_arr[$i]}/g" ${THIS_TEMP}
	    sed -i "s/__E_MAX__/${emax_arr[$i]}/g" ${THIS_TEMP}
            sed -i "s/__E_MIN__/${emin_arr[$i]}/g" ${THIS_TEMP}
	    echo "Submitting ${THIS_TEMP}"
	    
	    ## Submit the template
	    sbatch ${THIS_TEMP}
	    
	    ## No need to delete, so done
	    rm ${THIS_TEMP}
	done
    done
done
