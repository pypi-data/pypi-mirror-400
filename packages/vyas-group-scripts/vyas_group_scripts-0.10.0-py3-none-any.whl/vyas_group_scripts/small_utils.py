import os

def my_queue():
    os.system("squeue --format=\"%.18i %.9p %.30j %.10u %.8T %.10M %.10l %.6D %.10R %Z\" --me")

