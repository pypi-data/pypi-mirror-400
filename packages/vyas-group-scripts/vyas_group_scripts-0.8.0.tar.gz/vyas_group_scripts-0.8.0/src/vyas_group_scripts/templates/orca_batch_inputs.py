orca_template = r"""#!/bin/bash -x

# --------------------------------------------------------------------------------------------------------------
#
# This script will submit the input file specified to ORCA via the slurm scheduler. The script will automatically
# create a new output directory with the same title as the input file and send all files there. Script timing 
# will be recorded in the slurm.out file which will be copied to the output directory only when the job has 
# completed. Email status updates will be sent if configured in the config.toml.
#
# --------------------------------------------------------------------------------------------------------------

# must set the account number as an env variable manually - gab will automatically use this
#SBATCH --account={ACTNUM} # you can find the account number by running $ sacctmgr show Account
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=36
#SBATCH --ntasks=36
#SBATCH --export=ALL
#SBATCH --time={TIME} # time when job will automatically terminate- want the smallest possible overestimate{BENCHMARKING_LINE}
maxtime=3590 # buffer time to allow cleanup, should be ~10 seconds less than auto termination time

# --------------------------------------------------------------------------------------------------------------

INPUT_FILE="{INPUT_FILE_NAME}"

# --------------------------------------------------------------------------------------------------------------

ml purge 

# record submission time
mystart=$(date +%Y-%m-%d %H:%M:%S)

# make a new output folder with the job name as the title and direct the output there
OUTPUT_DIR="${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME: 0:-2}}"
mkdir -p "${{OUTPUT_DIR}}_IN-PROGRESS"

# copy the input orca file to the output folder and delete the copy in the submit directory
cp "${{SLURM_SUBMIT_DIR}}/${{INPUT_FILE}}" "${{OUTPUT_DIR}}_IN-PROGRESS/${{INPUT_FILE}}"
rm "${{SLURM_SUBMIT_DIR}}/${{INPUT_FILE}}"

# copy the input xyz file to the output folder and delete the copy in the submit directory
cp "${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME: 0:-2}}.xyz" "${{OUTPUT_DIR}}_IN-PROGRESS/${{SLURM_JOB_NAME: 0:-2}}.xyz" || echo "NO XYZ INPUT FOR THIS JOB"
rm "${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME: 0:-2}}.xyz" || echo "NO XYZ FILE TO REMOVE"

# copy the input script to the output folder and delete the copy in the submit directory
cp "${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME}}" "${{OUTPUT_DIR}}_IN-PROGRESS/${{SLURM_JOB_NAME}}"
rm "${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME}}"

# load and export NBO path
eval "$VGS_LOAD_NBO"

# load ORCA path
eval "$VGS_LOAD_ORCA"

# load the mpi module and print JOBID to slurm out for debugging
eval "$VGS_LOAD_MPI"
JOBID=`echo $SLURM_JOBID`

# configure and pass OMP parameters
#export OMP_NUM_THREADS=1

# go the output folder
cd "${{OUTPUT_DIR}}_IN-PROGRESS"


#################################################################################################
# run the input file and generate an output file of the same name
# if the timeout is reached it will return exit 124, otherwise it returns the calc exit status
start=`date +%s.%N`
OUTPUT_FILE="${{INPUT_FILE: 0:-4}}.out"
timeout -s SIGTERM $maxtime $VGS_ORCA_PATH "${{OUTPUT_DIR}}_IN-PROGRESS/${{INPUT_FILE}}">"${{OUTPUT_FILE}}"
CALC_STATUS=$?
end=`date +%s.%N`
#################################################################################################


# try to generate the orbital *.cube files and *.html files if the ORCA job was successful
# also try to extract the NBO output (not always called, will pass if no NBO)
if [[ $CALC_STATUS == 0 ]]; then 
	cubegen="${{VGSPATH}}/orca_orbital_cubegen.s"
	chmod +x "${{cubegen}}"
	"${{cubegen}}" -f "${{INPUT_FILE: 0:-4}}.gbw" || echo "MO VISUALIZATION FAILED"

	sed -n '/Now starting NBO\.\.\./,/returned from  NBO  program/p' "${{OUTPUT_FILE}}" | tail -n +2 | head -n -1 > "${{INPUT_FILE: 0:-4}}.nbout" || echo "NBO SCRAPING FAILED"
fi


# get the job status
# get the job status
if [[ $CALC_STATUS == 124 ]]; then 
    status="TIMEOUT"
elif [[ $CALC_STATUS != 0 ]]; then
    status="ERROR"
elif [[ $CALC_STATUS == 0 ]]; then
    # check if the words "ORCA TERMINATED NORMALLY" appear in the last 10 lines of the output file
    if tail -n 10 "$OUTPUT_FILE" | grep -q "****ORCA TERMINATED NORMALLY****"; then
        status="NORMAL"
    else
        CALC_STATUS=2
        status="INCOMPLETE"
    fi
fi


# log the time for benchmarking in the outputfile
runtime=$( echo "$end - $start" | bc -l )
echo $runtime
exec 3>>"${{OUTPUT_FILE}}"
echo "">&3
echo "slurmID:    ${{SLURM_JOBID}}">&3
echo "totalRuntime[s]:    ${{runtime}}">&3
exec 3>&-

# get the number of basis functions used in the first calculation by the SHARK package
myBasis=$(grep -m 1 "Number of basis functions" "${{OUTPUT_FILE}}" | awk '{{print $NF}}' | tr -d '[:space:]')
myBasis=($myBasis)

# record the completion time
myend=$(date +%Y-%m-%d %H:%M:%S)

# write the total job timing to the job_timings file in the submit directory as a CSV
cd "${{SLURM_SUBMIT_DIR}}"
if [ ! -f job_timings.csv ]; then
	echo "filename,slurmID,nbasisfuncs,start,end,runtime[s],jobstatus" > job_timings.csv
fi
exec 3>>job_timings.csv
echo "${{INPUT_FILE}},${{SLURM_JOBID}},${{myBasis}},${{mystart}},${{myend}},${{runtime}},${{status}}">&3
exec 3>&-



# copy the slurm output to the output folder and delete from the submit directory
cp "${{SLURM_SUBMIT_DIR}}/slurm-${{SLURM_JOBID}}.out" "${{OUTPUT_DIR}}_IN-PROGRESS/slurm-${{SLURM_JOBID}}-${{INPUT_FILE: 0:-4}}.out"
rm "${{SLURM_SUBMIT_DIR}}/slurm-${{SLURM_JOBID}}.out"


# rename the output directory appropriately
if [[ $status == "TIMEOUT" ]]; then 

	mv "${{OUTPUT_DIR}}_IN-PROGRESS" "${{OUTPUT_DIR}}_TIMEOUT"
	exit 124

elif [[ $status == "ERROR" ]]; then

	mv "${{OUTPUT_DIR}}_IN-PROGRESS" "${{OUTPUT_DIR}}_ERROR"
	exit 2

elif [[ $status == "INCOMPLETE" ]]; then

	mv "${{OUTPUT_DIR}}_IN-PROGRESS" "${{OUTPUT_DIR}}_INCOMPLETE"
	exit 2

elif [[ $status == "NORMAL" ]]; then

	mv "${{OUTPUT_DIR}}_IN-PROGRESS" "${{OUTPUT_DIR}}"
	cd "${{OUTPUT_DIR}}"
	# cleanup empty files
	if [[ -e "2" && ! -s "2" ]]; then
		rm "2"
	fi
	for nbout_file in *.nbout; do
		if [[ -e "$nbout_file" && ! -s "$nbout_file" ]]; then
			rm "${{nbout_file}}"
		fi
	done
	cd ..

	exit 0
fi"""

orca_restart_template = r"""#!/bin/bash -x

# --------------------------------------------------------------------------------------------------------------
#
# This script will re-submit the input file specified to ORCA via the slurm scheduler. This script automatically  
# edits the last input file to ensure that the previous geometry and wavefunction is read. All output will be 
# generated in the same directory as the original calculation that timed out. Script timing will be recorded in 
# the slurm.out file which will be copied to the original output directory only when the job has completed. Email
# status updates will be sent if configured in the config.toml.
#
# --------------------------------------------------------------------------------------------------------------

# must set the account number as an env variable manually - gab will automatically use this
#SBATCH --account={ACTNUM} # you can find the account number by running $ sacctmgr show Account
#SBATCH --nodes={NUM_NODES}
#SBATCH --ntasks-per-node={TASKS_PER_NODE}
#SBATCH --ntasks={N_TASKS}
#SBATCH --export=ALL
#SBATCH --time={TIME} # time when job will automatically terminate- want the smallest possible overestimate{BENCHMARKING_LINE}
maxtime=3590 # buffer time to allow cleanup, should be ~10 seconds less than auto termination time

# --------------------------------------------------------------------------------------------------------------

INPUT_FILE="{INPUT_FILE_NAME}"
OLD_JOB_DIR="my_old_job"

# --------------------------------------------------------------------------------------------------------------

# record submission time
mystart=$(date +%Y-%m-%d %H:%M:%S)

# make a new output folder with the job name as the title and direct the output there
OUTPUT_DIR="${{SLURM_SUBMIT_DIR}}/${{OLD_JOB_DIR}}"
mv "${{OUTPUT_DIR}}" "${{OUTPUT_DIR}}_RESTARTED"

# copy the input script to the output folder and delete the copy in the submit directory
cp "${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME}}" "${{OUTPUT_DIR}}_RESTARTED/${{SLURM_JOB_NAME}}"
rm "${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME}}"
cp "${{SLURM_SUBMIT_DIR}}/${{INPUT_FILE}}" "${{OUTPUT_DIR}}_RESTARTED/${{INPUT_FILE}}"
rm "${{SLURM_SUBMIT_DIR}}/${{INPUT_FILE}}"

# load and export NBO path
eval "$VGS_LOAD_NBO"

# load the mpi module and print JOBID to slurm out for debugging
eval "$VGS_LOAD_MPI"
JOBID=`echo $SLURM_JOBID`

# go the output folder
cd "${{OUTPUT_DIR}}_RESTARTED"


#################################################################################################
# run the input file and generate an output file of the same name
# if the timeout is reached it will return exit 124, otherwise it returns the calc exit status
start=`date +%s.%N`
OUTPUT_FILE="${{INPUT_FILE: 0:-4}}.out"
timeout -s SIGTERM $maxtime $SS_ORCA_PATH "${{OUTPUT_DIR}}_RESTARTED/${{INPUT_FILE}}">"${{OUTPUT_FILE}}"
CALC_STATUS=$?
end=`date +%s.%N`
#################################################################################################


# try to generate the orbital *.cube files and *.html files if the ORCA job was successful
# also try to extract the NBO output (not always called, will pass if no NBO)
if [[ $CALC_STATUS == 0 ]]; then 
	cubegen="${{VGSPATH}}/orca_orbital_cubegen.s"
	chmod +x "${{cubegen}}"
	"${{cubegen}}" -f "${{INPUT_FILE: 0:-4}}.gbw" || echo "MO VISUALIZATION FAILED"

	sed -n '/Now starting NBO\.\.\./,/returned from  NBO  program/p' "${{OUTPUT_FILE}}" | tail -n +2 | head -n -1 > "${{INPUT_FILE: 0:-4}}.nbout" || echo "NBO SCRAPING FAILED"
fi


# get the job status
if [[ $CALC_STATUS == 124 ]]; then 
	status="TIMEOUT"
elif [[ $CALC_STATUS != 0 ]]; then
	status="ERROR"
elif [[ $CALC_STATUS == 0 ]]; then
	status="NORMAL"
fi


# log the time for benchmarking in the outputfile
runtime=$( echo "$end - $start" | bc -l )
echo $runtime
exec 3>>"${{OUTPUT_FILE}}"
echo "">&3
echo "slurmID:    ${{SLURM_JOBID}}">&3
echo "totalRuntime[s]:    ${{runtime}}">&3
exec 3>&-

# get the number of basis functions used in the first calculation by the SHARK package
myBasis=$(grep -m 1 "Number of basis functions" "${{OUTPUT_FILE}}" | awk '{{print $NF}}' | tr -d '[:space:]')
myBasis=($myBasis)

# record the completion time
myend=$(date +%Y-%m-%d %H:%M:%S)

# write the total job timing to the job_timings file in the submit directory as a CSV
cd "${{SLURM_SUBMIT_DIR}}"
if [ ! -f job_timings.csv ]; then
	echo "filename,slurmID,nbasisfuncs,start,end,runtime[s],jobstatus" > job_timings.csv
fi
exec 3>>job_timings.csv
echo "${{INPUT_FILE}},${{SLURM_JOBID}},${{myBasis}},${{mystart}},${{myend}},${{runtime}},${{status}}">&3
exec 3>&-



# copy the slurm output to the output folder and delete from the submit directory
cp "${{SLURM_SUBMIT_DIR}}/slurm-${{SLURM_JOBID}}.out" "${{OUTPUT_DIR}}_RESTARTED/slurm-${{SLURM_JOBID}}-${{INPUT_FILE: 0:-4}}.out"
rm "${{SLURM_SUBMIT_DIR}}/slurm-${{SLURM_JOBID}}.out"


# rename the output directory appropriately
if [[ $CALC_STATUS == 124 ]]; then 

	mv "${{OUTPUT_DIR}}_RESTARTED" "${{OUTPUT_DIR}}_TIMEOUT"
	exit 124

elif [[ $CALC_STATUS != 0 ]]; then

	mv "${{OUTPUT_DIR}}_RESTARTED" "${{OUTPUT_DIR}}_ERROR"
	exit 2

elif [[ $CALC_STATUS == 0 ]]; then

	FINAL_OUTPUT="${{OUTPUT_DIR%_TIMEOUT}}"
	mv "${{OUTPUT_DIR}}_RESTARTED" "${{FINAL_OUTPUT}}"
	cd "${{OUTPUT_DIR}}"
	# cleanup empty files
	if [[ -e "2" && ! -s "2" ]]; then
		rm "2"
	fi
	for nbout_file in *.nbout; do
		if [[ -e "$nbout_file" && ! -s "$nbout_file" ]]; then
			rm "${{nbout_file}}"
		fi
	done
	cd ..

	exit 0
fi"""

