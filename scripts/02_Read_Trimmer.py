#!/usr/bin/env python3

# This is a wrapper script for trimming reads for use in SISRS
# This script calls bbduk.sh, which must be installed and in your path
# All reads for all samples should be in .fastq.gz format (To change this, the -f/--format option accepts "fastq","fq","fastq.gz [default]","fq.gz"
# Paired-end read files must be identically basenamed and end in _1/_2
#
# Arguments: (1) -p/--processors (OPTIONAL): Number of available processors for FastQC/SLURM; Default: 1
# Arguments: (1) -f/--format (OPTIONAL): Number of available processors for FastQC/SLURM; Default: 1
# Arguments: (3) --skipqc (OPTIONAL): Flag to skip FastQC step
# Arguments: (4) --bash (OPTIONAL): Instead of executing trim scripts, save BASH script for trimming in 'scripts' directory
# Arguments: (5) --slurm (OPTIONAL): Instead of executing trim scripts, save SLURM script for trimming in 'scripts' directory
#
# Output if trimming is exectuted (i.e. no --bash or --slurm argument):
# Output: (1) Trimmed Reads (in <base_dir>/Reads/Trimmed_Reads/<Sample_ID>/<Sample_ID>_Trim_<1/2>.fastq.gz
# Output: (2) Trim Log (in <base_dir>/Reads/Raw_Reads/trimOutput)
# Output: (3) FastQC output [unless disabled via --skipqc] for all raw + trimmed read sets (in <base_dir>/Reads/Raw_Reads/fastqcOutput & <base_dir>/Reads/Trimmed_Reads/fastqcOutput)
#
# Output if trim scripts are requested (e.g. through --bash or --slurm):
# --bash: Trim script (Trim_Script.sh) will be saved to 'scripts' directory as a BASH script
# --slurm: Trim script with SLURM header (Trim_Script.sh) will be saved to 'scripts' directory as a SLURM script [Note: SLURM script has a default time of 48h; Change if necessary]

import os
from os import path
import sys
from glob import glob
import subprocess
from subprocess import check_call
import argparse

# Set cwd to script location
script_dir = os.path.dirname(os.path.abspath(__file__))

# Find BBDuk + Adapter File
cmd = ['which', 'bbduk.sh']
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
o, e = proc.communicate()
bbduk_adapter = path.dirname(o.decode('ascii'))+"/resources/adapters.fa"

# Set RawRead and TrimRead directories based off of script folder location
raw_read_dir = path.dirname(path.abspath(script_dir))+"/Reads/Raw_Reads"
trim_read_dir = path.dirname(path.abspath(script_dir))+"/Reads/Trimmed_Reads"

# Find sample folders within Raw_Reads folder
raw_read_sample_dirs = sorted(glob(raw_read_dir+"/*/"))

# Process arguments
my_parser = argparse.ArgumentParser()
my_parser.add_argument('-p','--processors',action='store',default=1)
my_parser.add_argument('-f','--format',action='store',default="fastq.gz")
my_parser.add_argument('--skipqc',action='store_true')
my_parser.add_argument('--bash',action='store_true')
my_parser.add_argument('--slurm',action='store_true')

args = my_parser.parse_args()

processors = args.processors
read_format = str(args.format)
run_qc = not args.skipqc
check_bash = args.bash
check_slurm = args.slurm

# Ensure format is valid
if read_format not in ['fq','fastq','fq.gz','fastq.gz']:
    sys.exit("-f/--format must be fq, fastq,fq.gz, or fastq.gz")

# Create script file
if check_slurm or check_bash:
    f= open(script_dir+"/Trim_Script.sh","w+")

if check_slurm: # Generate SLURM header

    slurm_header = """#!/bin/bash
#SBATCH --job-name="Lutjanus_Trim"
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=PROCESSORS
cd $SLURM_SUBMIT_DIR
"""
    keyList = ['PROCESSORS']
    keyDict = {'PROCESSORS':str(int(processors))}

    for key in keyList:
        slurm_header = slurm_header.replace(key,keyDict[key])
    f.write(slurm_header)
    f.write("\n")

elif check_bash:
    f.write("#!/bin/bash")
    f.write("\n")

# Create folder for BBDuk StdOut
if(not path.isdir(raw_read_dir+"/trimOutput")):
    os.mkdir(raw_read_dir+"/trimOutput")
trim_output = raw_read_dir+"/trimOutput/"    

if run_qc:
    # Create folder for Raw FastQC output
    if(not path.isdir(raw_read_dir+"/fastqcOutput")):
        os.mkdir(raw_read_dir+"/fastqcOutput")
    raw_fastqc_output = raw_read_dir+"/fastqcOutput/"

    # Create folder for Trimmed FastQC output
    if(not path.isdir(trim_read_dir+"/fastqcOutput")):
        os.mkdir(trim_read_dir+"/fastqcOutput")
    trim_fastqc_output = trim_read_dir+"/fastqcOutput/"
    
# Ensure Trim Log/FastQC output directories not included in sample list
raw_read_sample_dirs = [x for x in raw_read_sample_dirs if not x.endswith('trimOutput/')]
raw_read_sample_dirs = [x for x in raw_read_sample_dirs if not x.endswith('fastqcOutput/')]
    
# Run FastQC on all raw read files, using all available processors
if run_qc:
    raw_fastqc_command = [
        'fastqc',
        '-t',
        '{}'.format(processors),
        '-o',
        '{}'.format(raw_fastqc_output),
        '{}/*/*.{}'.format(raw_read_dir,read_format)]

    if check_bash or check_slurm:
        f.write("# Raw FastQC\n")
        f.write(' '.join(raw_fastqc_command))
        f.write("\n\n# Trim Scripts\n")
    else:
        os.system(' '.join(raw_fastqc_command))

#For each sample directory...
for sample_dir in raw_read_sample_dirs:

    #List all files and set output dir
    files = sorted(glob(sample_dir+"*."+read_format))
    sample_ID = path.basename(sample_dir[:-1])
    out_trim_dir = trim_read_dir + "/" + sample_ID

    left_pairs = list()
    right_pairs = list()
    single_end = list()

    #Find files ending in _1/_2.fastq.gz
    left_files = [s for s in files if "_1."+read_format in s]
    right_files = [s for s in files if "_2."+read_format in s]

    #Strip _1.fastq.gz/_2.fastq.gz and identify pairs based on file name
    left_files = [x.replace('_1.'+read_format, '') for x in left_files]
    right_files = [x.replace('_2.'+read_format, '') for x in right_files]
    paired_files = list(set(left_files).intersection(right_files))

    #Reset file names and filter out single-end files
    for pair in paired_files:
        left_pairs.append(pair+"_1."+read_format)
        right_pairs.append(pair+"_2."+read_format)
    paired_files = sorted(left_pairs + right_pairs)

    single_end = [x for x in files if x not in paired_files]

    #Remove .fastq.gz from lists to make naming easier
    left_pairs = [x.replace('_1.'+read_format, '') for x in left_pairs]
    right_pairs = [x.replace('_2.'+read_format, '') for x in right_pairs]
    single_end = [x.replace('.'+read_format, '') for x in single_end]

    #Trim single-end files if present...
    if len(single_end) > 0:
        for x in single_end:
            se_trim_command = [
                'bbduk.sh',
                'maxns=0',
                'ref={}'.format(bbduk_adapter),
                'qtrim=w',
                'trimq=15',
                'minlength=35',
                'maq=25',
                'in={}.{}'.format(x,read_format),
                'out={}'.format(out_trim_dir+"/"+path.basename(x)+'_Trim.fastq.gz'),
                'k=23',
                'mink=11',
                'hdist=1',
                'hdist2=0',
                'ktrim=r',
                'ow=t',
                '&>',
                '{outDir}out_{fileName}_Trim'.format(outDir=trim_output,fileName=path.basename(x))]
            
            if not check_bash and not check_slurm:
                check_call(se_trim_command)
            else:
                f.write(' '.join(se_trim_command))
                f.write("\n")

    #Trim paired-end files if present...
    if(len(left_pairs) == len(right_pairs) & len(left_pairs) > 0):
        for x in range(len(left_pairs)):
            file_name = path.basename(left_pairs[x])
            pe_trim_command = [
                'bbduk.sh',
                'maxns=0',
                'ref={}'.format(bbduk_adapter),
                'qtrim=w',
                'trimq=15',
                'minlength=35',
                'maq=25',
                'in={}.{}'.format(left_pairs[x]+'_1',read_format),
                'in2={}.{}'.format(right_pairs[x]+'_2',read_format),
                'out={}'.format(out_trim_dir+"/"+path.basename(left_pairs[x])+'_Trim_1.fastq.gz'),
                'out2={}'.format(out_trim_dir+"/"+path.basename(right_pairs[x])+'_Trim_2.fastq.gz'),
                'k=23',
                'mink=11',
                'hdist=1',
                'hdist2=0',
                'ktrim=r',
                'ow=t',
                '&>',
                '{outDir}out_{fileName}_Trim'.format(outDir=trim_output,fileName=file_name)]
            
            if not check_bash and not check_slurm:
                check_call(pe_trim_command)
            else:
                f.write(' '.join(pe_trim_command))
                f.write("\n")

if run_qc: # Run FastQC on all trimmed files, using all available processors

    trim_fastqc_command = [
        'fastqc',
        '-t',
        '{}'.format(processors),
        '-o',
        '{}'.format(trim_fastqc_output),
        '{}/*/*.{}'.format(trim_read_dir,read_format)]

    if check_bash or check_slurm:
        f.write("\n# Trim FastQC\n")
        f.write(' '.join(trim_fastqc_command))
        f.write("\n")
    else:
        os.system(' '.join(trim_fastqc_command))

if check_slurm or check_bash:
    f.close()