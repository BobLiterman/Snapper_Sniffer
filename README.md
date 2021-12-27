# Snapper Sniffer
A standalone pipeline for differentiating *Lutjanus campechanus* and *Lutjanus purpureus*

Dr. Robert Literman  
Dr. Mayara Matos  

### How this works?  
This repository contains a SNP-based pipeline designed to identify samples as either *Lutjanus campechanus*  or *L. purpureus*. The pipeline uses pieces of the [SISRS bioinformatics package](https://github.com/BobLiterman/SISRS_Walkthrough) that have been specifically tailored for this purpose. The major steps include:  

1. Read trimming (optional)  
2. Mapping reads onto an informative subset of the *L. campechanus* [reference genome](https://pubmed.ncbi.nlm.nih.gov/32348345/)  
3. Stripping informative SNP positions as assessing the alleles present  
4. Classifying results and outputting a small report  

### How-To  

#### 1. Clone repo  

```
git clone https://github.com/BobLiterman/Snapper_Sniffer.git
```

#### 2. Set up folders  
For each sample you want to ID, add a line with the desired sample ID to the **Sample_IDs** file found in the *scripts* directory. For example,  
```
> cat scripts/Sample_IDs

MySample_01
MySample_02
MySample_03
```

Once the **Sample_IDs** file has all the desired names, perform automated folder setup via:  
```
python 01_Create_Folders.py
```

This command will create folders for raw reads, trimmed reads, and for all downstream mapping steps.  

#### 3. Trim Reads (Optional)  
- If your reads are **already trimmed**, they should be the **fastq.gz** format. They can then be linked (e.g. via *cp -as*) into the newly created folder(s) (Snapper_Sniffer/Reads/Trimmed_Reads/<SAMPLE_ID>).  
- For **untrimmed reads**, to use the automated read trimming, link raw reads into your newly created folder(s) (Snapper_Sniffer/Reads/Raw_Reads/<SAMPLE_ID>) and then run the read trimming script **02_Read_Trimmer.py**.  
  - **Note:** To use this script, *bbduk* and *FastQC* (optional) must be installed in your path.  
  - Script can accept single-end reads, paired-end reads, or a mix of both.  
  - Paired-end reads must have the same file basename, and end with "_1" and "_2"
  - By default, this script assumes that raw reads are in the **fastq.gz** format, but using the *-f/--format* option, you can specify **fastq**, **fq**, or **fq.gz**.  
  - To skip FastQC, add the *--skipqc* flag  
  - To generate a bash script instead of running the trimming directly, add the *--bash* flag  
  - To generate a bash script with a SLURM header, add the *--slurm** flag  
  - To set the number of processors to use for FastQC/trimming, set the *-p/--processors* flag [Default: 1]  

```
# Run QC + Trimming with 1 processor
python 02_Read_Trimmer.py

# Run QC + Trimming with 10 processors, where raw reads are .fastq files
python 02_Read_Trimmer.py -f fastq -p 10

# Skip QC
python 02_Read_Trimmer.py --skipqc

# Don't run trimming/QC, but make a bash script
python 02_Read_Trimmer.py --bash

# Don't run trimming/QC, but make a SLURM script calling 15 processors
python 02_Read_Trimmer.py --slurm --processors 15
```

