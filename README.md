# Snapper Sniffer
A standalone pipeline for differentiating *Lutjanus campechanus* and *Lutjanus purpureus*

Dr. Robert Literman
Dr. Mayara Matos

#### How this works?  
This repository contains a SNP-based pipeline designed to identify samples as either *Lutjanus campechanus*  or *L. purpureus*. The pipeline uses pieces of the SISRS bioinformatics package that have been specifically tailored for this purpose. The major steps include:  

1. Read trimming (optional)  
2. Mapping reads onto an informative subset of the *L. campechanus* [reference genome](https://pubmed.ncbi.nlm.nih.gov/32348345/)  
3. Stripping informative SNP positions as assessing the alleles present  
4. Classifying results and outputting a small report  
