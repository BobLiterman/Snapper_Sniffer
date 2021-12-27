#!/usr/bin/env python3

# This script prepares data for a mapping run by setting the data up and creating mapping scripts
# Mapping scripts are generated from a template and saved to the Lutjanus_Mapping/<SAMPLE_ID> folder
# Arguments: (1) -p/--processors (OPTIONAL): Number of available processors; Default: 1
# Arguments: (2) --slurm (OPTIONAL): Append a SLURM header to the bash script
# Arguments: (3) --modules (OPTIONAL): Provide a path to a file containing any potential SLURM modules that need to be loaded

import os
from os import path
import sys
from glob import glob
import pandas as pd
import argparse
import re

# Set script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Fetch read directories based off of script folder location
trim_read_dir = path.dirname(path.abspath(script_dir))+"/Reads/Trimmed_Reads"
trim_read_sample_dirs = sorted(glob(trim_read_dir+"/*/"))

# Remove output folders from trimming/QC
trim_read_sample_dirs = [x for x in trim_read_sample_dirs if not x.endswith('trimOutput/')]
trim_read_sample_dirs = [x for x in trim_read_sample_dirs if not x.endswith('fastqcOutput/')]
trim_read_sample_dirs = sorted([x for x in trim_read_sample_dirs if not x.endswith('subsetOutput/')])

# Fetch mapping directories based off of script folder location
mapping_dir = path.dirname(path.abspath(script_dir))+"/Lutjanus_Mapping"

# Fetch reference folder + refrence SNPs
reference_dir = path.dirname(path.abspath(script_dir))+"/Reference_Data"
composite_dir = reference_dir+"/Composite_Genome"
ref_tab_snps = reference_dir+"/Tab_SNPs"
ref_snps = reference_dir+"/Reference_SNPs"

# Get arguments
my_parser = argparse.ArgumentParser()
my_parser.add_argument('-p','--processors',action='store',default=1)
my_parser.add_argument('--slurm',action='store_true')
my_parser.add_argument('--modules',action='store', required=False)

args = my_parser.parse_args()

processors = args.processors
check_slurm = args.slurm

with open(script_dir+'/Mapping_Template','r') as mapping:
    mapping_template = mapping.read()
    
with open(script_dir+'/Processing_Template','r') as processing:
    processing_template = processing.read()

slurm_header = """#!/bin/bash
#SBATCH --job-name="SAMPLE"
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=PROCESSORS
cd $SLURM_SUBMIT_DIR
"""

#Create links to trimmed read files in SISRS_Run directory
for sample_dir in trim_read_sample_dirs:

    sample = path.basename(sample_dir[:-1])

    new_mapping = mapping_template
    new_processing = processing_template
    new_slurm = slurm_header
        
    keyList = ['PROCESSORS','COMPOSITE_GENOME','SCRIPT_DIR','SAMPLE','MAPPING_DIR','COMPOSITE_DIR','READS']
    keyDict = {'PROCESSORS':str(processors),
               'COMPOSITE_GENOME':composite_dir+"/contigs.fa",
               'SCRIPT_DIR':script_dir,
               'SAMPLE':sample,
               'MAPPING_DIR':mapping_dir,
               'COMPOSITE_DIR':composite_dir,
               'READS':",".join(glob(sample_dir+"*.fastq.gz"))}
    
    for key in keyList:
        new_mapping = new_mapping.replace(key,keyDict[key])
        new_processing = new_processing.replace(key,keyDict[key])

    with open(mapping_dir+"/"+sample+"/"+sample+".sh", "w") as mapping_file:
            with open(mapping_dir+"/"+sample+"/Process_"+sample+".R", "w") as processing_file:
                
                # Save R script
                print(new_processing,file=processing_file)
                
                # Save mapping script
                if check_slurm: 
                    new_slurm = new_slurm.replace(key,keyDict[key])           
                    try: 
                        args.modules
                        with open(args.modules,'r') as modules:
                            slurm_modules = modules.read()
                        print(new_slurm+"\n"+slurm_modules+"\n"+new_mapping,file=mapping_file)
                    except:
                        print(new_slurm+"\n"+new_mapping,file=mapping_file)
                else:
                    print("#!/bin/bash"+"\n"+new_mapping,file=mapping_file)
                    os.system('chmod +x '+mapping_dir+"/"+sample+"/"+sample+".sh")
