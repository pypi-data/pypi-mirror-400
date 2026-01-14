from glob import glob
from .templates.g16_batch_inputs import simple_g16_template, complex_g16_template
from .templates.orca_batch_inputs import orca_template, orca_restart_template
import os
import argparse



def process_g16_files(file_pattern="*.gjf",complex = False ,time=os.environ.get("DEFAULT_DFT_TIME") ,num_nodes=os.environ.get("NUM_NODES") ,benchmarking=False):

    benchmarking_line = ""
    batch_file = simple_g16_template
    if complex:
        batch_file = complex_g16_template
    if benchmarking:
        benchmarking_line = "\n#SBATCH --exclusive"

    for gjf_file in glob(file_pattern):
        if ".gjf" !=  gjf_file[-4:]:
            continue
        
        bash_file_name = gjf_file[:-4]+".s"
        print(bash_file_name)
        if  os.path.exists(bash_file_name):
            print(f"{bash_file_name} already exists, skipping.")
            continue

        this_file_string = batch_file.format(TIME=time,
                                             ACTNUM=os.environ.get("ACTNUM"),
                                             JOB_NAME=gjf_file[:-4],
                                             TASKS_PER_NODE=1,
                                             N_TASKS=num_nodes,
                                             INPUT_FILE_NAME=gjf_file.split("/")[-1][:-4],
                                             NUM_NODES=num_nodes,
                                             BENCHMARKING_LINE = benchmarking_line)
        with open(bash_file_name,"w") as bash_file:
            bash_file.write(this_file_string)
        
        apply_parallelization(gjf_file,num_nodes)



def process_inp_files(file_pattern="*.inp",complex = False ,time=os.environ.get("DEFAULT_DFT_TIME") ,num_nodes=os.environ.get("NUM_NODES") ,benchmarking=False,restart=False):

    # Select the bash template
    batch_file = orca_template

    # Set Benchmarking line
    benchmarking_line = ""
    if benchmarking:
        benchmarking_line = "\n#SBATCH --exclusive"

    # loop through input files
    for inp_file in glob(file_pattern):
        if ".inp" != inp_file[-4:]:
            continue
        bash_file_name = inp_file[:-4]+".s"

        if  os.path.exists(bash_file_name):
            print(f"{bash_file_name} already exists, skipping.")
            continue


        # Modify bash script 
        this_file_string = batch_file.format(TIME=time,
                                             ACTNUM=os.environ.get("ACTNUM"),
                                             JOB_NAME=inp_file[:-4],
                                             TASKS_PER_NODE=1,
                                             N_TASKS=num_nodes,
                                             INPUT_FILE_NAME=inp_file.split("/")[-1][:-4],
                                             NUM_NODES=num_nodes,
                                             BENCHMARKING_LINE = benchmarking_line)
        with open(bash_file_name,"w") as bash_file:
            bash_file.write(this_file_string)
        
        # Add parallelization to input file
        apply_parallelization(inp_file,num_nodes)


def apply_parallelization(input_file,nprocs = 36):

    if ".gjf" == input_file[-4:]:
        if nprocs != 0:
            print(f"Adding parallelization to {input_file}.")
            with open(input_file,"r") as file:
                file_string = file.read()
            file_string = f"%mem=5GB\n%nprocshared={nprocs}\n"+file_string

            with open(input_file,"w") as file:
                file.write(file_string)
        
    if ".inp" ==  input_file[-4:]:
        if nprocs != 0:
            if not nprocs in [6,10,30,36]:
                print("invalid nprocs selected.")
                return None
            memory = int(144000/nprocs)
            file_string = f"%maxcore {memory}\n%pal nprocs {nprocs} end\n"
            with open(input_file,"r") as file:
                file_list = file.readlines()
            lastinput_line = 1
            for index,line in enumerate(file_list): 
                if len(line.strip())>0 and line.strip()[0] == "!":
                    lastinput_line = index
            file_list.insert(lastinput_line+1,file_string)
            with open(input_file,"w") as file:
                file.writelines(file_list)



        







def gen_all_batch():

    parser = argparse.ArgumentParser(prog="gab")
    parser.add_argument("-t",default=os.environ.get("DEFAULT_DFT_TIME"),help="Set the time limit for the batch script (format: HH:MM:SS)." \
    " If not specified, the default from the DFT_DEFAULT_TIME environment variable is used.")
    parser.add_argument("-b",action="store_true",help="Enable benchmarking mode. This sets the node allocation" \
    " to exclusive to ensure consistent performance for benchmarking runs.")
    parser.add_argument("-k",default="*",help="Provide a comma seperated regex pattern to match input files. " \
    "Only batch files for matching input files will be generated.\nExample: -k 'xyz,*mol' (quotes reccomended)")
    parser.add_argument("-p",default=-1,type=int,choices=[0,6,10,30,36],help="Specify the number of processors to use"\
    " Acceptable values 36, 30, 10, 6, or 0." \
    " Memory sttings will be adjusted based on this value. Use 0 to skip adding parallelization directives entirely." \
    " When the -p flag is not called the default options in DFT_DEFAULT_MEM and DFT_DEFAULT_PROCESSORS environment variables" \
    " are used for all calculations.\n\tOrca jobs:\n\t\tInsert content after first '!' in input file.\n\tGaussian Jobs:\n\t\tAppends" \
    " parralleliszation options to the top of input file\n\t\tOnly '36' and '0' options are available for gaussian jobs.")
    parser.add_argument("-r",default="*",help="Restart ORCA jobs from one or more specified folders. Provide a comma-seperated list of" \
    " folder names.\n\tExample: -r 'job1_TIMEOUT,job2_TIMEOUT")
    parser.add_argument("-v",default=None,help="Specify the quantum chemistry software version to use." \
    " Currently only downgrading to ORCA 5 is supported.")
    parser.add_argument("-c",action="store_false",help="Uses a more simple .s file for gaussian jobs that does not create a bunch of subdirectories.")
    args = parser.parse_args()

    patterns_to_search = args.k.split(",")
    complex_choice = args.c
    time_choice = args.t
    processors_choice = args.p
    benchmarking_choice = args.b
    orca_version = args.v
    restarts = args.r
    if processors_choice == -1:
        processors_choice = os.environ.get("DEFAULT_DFT_NUM_NODES")

    for file_pattern in patterns_to_search:

        for file in glob(file_pattern):

            process_g16_files(file,complex_choice,time_choice,processors_choice,benchmarking_choice)
            process_inp_files(file,complex_choice,time_choice,processors_choice,benchmarking_choice)



if __name__ == "__main__":
    gen_all_batch()