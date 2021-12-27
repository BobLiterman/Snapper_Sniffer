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

