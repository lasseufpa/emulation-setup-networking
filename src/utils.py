import os
import shutil
import time

def clean_previous_results(output):
    output = os.path.abspath(output)
    if os.path.isdir(output):
        shutil.rmtree(output)
    os.mkdir(output)

def register_current_time(output):
    with open(os.path.join(output, 'metadata.txt'), 'a') as f:
        f.write('Time now: ')
        f.write(str(time.time()) + '\n')