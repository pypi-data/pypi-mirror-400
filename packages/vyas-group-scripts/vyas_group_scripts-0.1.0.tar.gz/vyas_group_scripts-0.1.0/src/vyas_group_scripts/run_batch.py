import os
from glob import glob
from rich import print
import argparse


def check_file_has_pair(s_file:str):
    if os.path.exists(s_file[:-3]+"inp"):
        return True
    if os.path.exists(s_file[:-3]+"gjf"):
        return True
    print(f"[red]Matching file not found for {s_file}")
    return False

def submit_job_pattern(sfile_pattern:str="*.s"):
    for s_file in glob(sfile_pattern):
        if check_file_has_pair(s_file):
            os.system(f"sbatch {s_file}")


def run_all_batch():

    parser = argparse.ArgumentParser(prog="rab")
    parser.add_argument("-k",default="*.s",help="provide a regesx pattern for .s files to submit")
    
    args = parser.parse_args()

    patterns_to_submit = args.k
    
    submit_job_pattern(patterns_to_submit)


if __name__ == "__main__":
    run_all_batch()