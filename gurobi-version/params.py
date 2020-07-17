import sys
from os import path
import os
import yaml
import re
import csv

from datetime import datetime, timedelta

data_path = sys.argv[1]
numSteps  = int(sys.argv[2])
dt        = int(sys.argv[3])

timestep = datetime.now()

# default configs which are merged with instance configuration
config = {
    # prefix for output filenames
    "name": "urmel",
    # debug mode with more output
    "debug": False,
    # write new initial state
    "new_init_scenario": False,
    # write problem files in the lp-format?
    "write_lp": False,
    # write solution files in the sol-format?
    "write_sol": False,
    # write irreducible infeasibility set if problem is infeasible?
    "write_ilp": True,
    # write wheel maps with gnuplot?
    "gnuplot": False,
    # console output?
    "urmel_console_output": False,
    # gurobi logfile
    "grb_logfile": "gurobi.log",
    # gurobi console output
    "grb_console": False,
    # contour output (net- and state-files in contour folder)
    "contour_output": False,
    # is the ai-part active?
    "ai" : True
}

# read manual file with configs
# the dictionary does not change during the process
if os.path.exists(os.path.join(data_path, "config.yml")):
    with open(os.path.join(data_path, 'config.yml')) as file:
        ymlConfig = yaml.load(file, Loader=yaml.FullLoader)
        merged = {**config, **ymlConfig}
        config = merged
        print(config)


# read manual file with compressor data
# the dictionary does not change during the process
with open(path.join(data_path, 'compressors.yml')) as file:
    compressors = yaml.load(file, Loader=yaml.FullLoader)
    #print(compressors)

def remove_da_fixed_decisions(agent_decisions):
    for key, value in agent_decisions.items():
        if re.search('va|zeta|gas|compressor', key):
            for key_1, value_1 in value.items():
                for key_2, value_2 in value_1.items():
                    for i,k in value_2.items():
                        if i > 0:
                            del value_2[i]
                            break
    return agent_decisions

def csv2csv_de(infile, outfile):
    reader = csv.reader(infile, delimiter = ',')
    writer = csv.writer(outfile, delimiter = ';')
    header = next(reader)
    newrow = [''.join('^' if c is ',' else c for c in entry) for entry in header]
    newrow = str(newrow)[1:-1]
    newrow = newrow.replace("'", '')
    writer.writerow(newrow.split(','))
    rows = [r for r in reader]
    for row in rows:
        row = str(row).replace(',',';')
        row = row.replace('.', ',')
        res = row[1:-1]
        res = res.replace("'", r'').replace(' ', r'')
        writer.writerow(res.split(';'))
