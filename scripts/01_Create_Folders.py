#!/usr/bin/env python3

# This script preps the folder architecture for a Lutjanus identification run. Fill in Sample_IDs file in scripts directory to create subfolders.
# Output: Script will create lots of folders, including folders for holding raw reads, trimmed reads, and the mapping runs

import sys
import os
from os import path
import argparse

# Set script dir and SISRS dir location 
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = path.dirname(path.abspath(script_dir))

# Get taxon ID file location
my_parser = argparse.ArgumentParser()
my_parser.add_argument('--id',action='store',default=script_dir+"/Sample_IDs",nargs="?")
args = my_parser.parse_args()
sample_ID_file = args.id

# Read taxon IDs from file
sample_list = [line.rstrip('\n') for line in open(sample_ID_file)]

# Make directories
os.mkdir(base_dir+"/Reads")
os.mkdir(base_dir+"/Reads/Raw_Reads")
os.mkdir(base_dir+"/Reads/Trimmed_Reads")
os.mkdir(base_dir+"/SISRS_Run")

for x in sample_list:
    os.mkdir(base_dir+"/Reads/Raw_Reads/"+x)
    os.mkdir(base_dir+"/Reads/Trimmed_Reads/"+x)
    os.mkdir(base_dir+"/SISRS_Run/"+x)