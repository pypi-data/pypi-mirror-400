
##################################################
# This a simple g16 batch file template python
# Is responsible for feeding in the following 
# information:
# JOB_NAME
# ACTNUM
# NUM_NODES
# TASKS_PER_NODE
# N_TASKS
# INPUT_FILE_NAME
# TIME
##################################################
simple_g16_template = r"""#!/bin/bash -x

#SBATCH --job-name={JOB_NAME}
#SBATCH --account={ACTNUM} # you can find the account number by running $ sacctmgr show Account
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=36
#SBATCH --ntasks=36
#SBATCH --export=ALL
#SBATCH --time={TIME} # time when job will automatically terminate- want the smallest possible overestimate{BENCHMARKING_LINE}

export KMP_AFFINITY=respect,verbose

module load apps/gaussian16/c01

cd $SLURM_SUBMIT_DIR

eval "$VGS_LOAD_G16"
INPUT_FILE="{INPUT_FILE_NAME}"

OUTPUT_FILE="${{INPUT_FILE: 0:-4}}.log"

JOBID=`echo $SLURM_JOBID`

#export OMP_NUM_THREADS=1
#export GAUSS_EXEDIR=/opt/g09/g09

echo "Running Job"


g16 <"${{INPUT_FILE}}">"${{OUTPUT_FILE}}"



echo "job has finished" """


##################################################
# This a more complex g16 batch file template python
# Is responsible for feeding in the following 
# information:
# JOB_NAME
# ACTNUM
# NUM_NODES
# TASKS_PER_NODE
# N_TASKS
# INPUT_FILE_NAME
# TIME
##################################################

complex_g16_template = r"""#!/bin/bash -x

# --------------------------------------------------------------------------------------------------------------
#
# This script will submit the input file specified to Gaussian 16 via the slurm scheduler. The script will 
# automatically create a new output directory with the same title as the input file and send all files there. 
# Script timing will be recorded in the slurm.out file which will be copied to the output directory only when 
# the job has completed. Email status updates will be sent if configured in the config.toml.
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

# record submission time
mystart=$(date +%Y-%m-%d %H:%M:%S)

# make a new output folder with the job name as the title and direct the output there
OUTPUT_DIR="${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME: 0:-2}}"
mkdir -p "${{OUTPUT_DIR}}_IN-PROGRESS"

# copy the input file to the output folder and delete the copy in the submit directory
cp "${{SLURM_SUBMIT_DIR}}/${{INPUT_FILE}}" "${{OUTPUT_DIR}}_IN-PROGRESS/${{INPUT_FILE}}"
rm "${{SLURM_SUBMIT_DIR}}/${{INPUT_FILE}}"

# copy the input script to the output folder and delete the copy in the submit directory
cp "${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME}}" "${{OUTPUT_DIR}}_IN-PROGRESS/${{SLURM_JOB_NAME}}"
rm "${{SLURM_SUBMIT_DIR}}/${{SLURM_JOB_NAME}}"


# configure KMP_AFFINITY to communicate hardware threads to OMP parallelizer
export KMP_AFFINITY=respect,verbose

# load the gaussian module and print JOBID to slurm out for debugging
eval "$VGS_LOAD_G16"
JOBID=`echo $SLURM_JOBID`

# configure and pass OMP parameters
#export OMP_NUM_THREADS=1
#export GAUSS_EXEDIR=/opt/g09/g09

# go the output folder
cd "${{OUTPUT_DIR}}_IN-PROGRESS"

# run the input file and generate an output file of the same name
# if the timeout is reached it will return exit 124, otherwise it returns the calc exit status
start=`date +%s.%N`
OUTPUT_FILE="${{INPUT_FILE: 0:-4}}.log"
timeout -s SIGTERM $maxtime g16 <"${{OUTPUT_DIR}}_IN-PROGRESS/${{INPUT_FILE}}">"${{OUTPUT_FILE}}"
CALC_STATUS=$?
end=`date +%s.%N`

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

# get the number of basis functions used in the first calculation
myBasis=$(grep -o -m 1 '[0-9]\+ basis functions' myFile | cut -d ' ' -f 1)
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
if [[ $CALC_STATUS == 124 ]]; then 

	mv "${{OUTPUT_DIR}}_IN-PROGRESS" "${{OUTPUT_DIR}}_TIMEOUT"
	exit 124

elif [[ $CALC_STATUS != 0 ]]; then

	mv "${{OUTPUT_DIR}}_IN-PROGRESS" "${{OUTPUT_DIR}}_ERROR"
	exit 2

elif [[ $CALC_STATUS == 0 ]]; then

	mv "${{OUTPUT_DIR}}_IN-PROGRESS" "${{OUTPUT_DIR}}"
	exit 0
fi"""