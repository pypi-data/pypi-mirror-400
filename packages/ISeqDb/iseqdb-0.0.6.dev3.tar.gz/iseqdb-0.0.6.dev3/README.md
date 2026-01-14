## ISeqDb - Identify Sequences in Databases

Screening of query dna sequences for the presence of specific target genes or proteins.

*Query sequences* can be metagenome assembles genomes (MAGs), contigs/scaffolds, multifasta and fasta files. Typically, *databases* contain multifasta homologous sequences. Databases are queried using megablast, blastn and blastx.

ISeqDd was tested to search for target genes or proteins in bacterial MAGs. ISeqDb was written primarily to search for the presence of genes encoding cyanotoxins and other genes encoding metabolites harmful to human health in cyanobacterial MAGs. Currently available databases obtained from NCBI (www.ncbi.nlm.nih.gov) include DNA sequences of genes encoding microcystins (*mcyB*, *mcyD*, *mcyE*), anatoxins (*anaC*, *anaF*), cylindrospermopsins (*cyrJ*), saxitoxins (*sxtA*, *sxtI*), and geosmin (*geoA*).

Any other database of homologous sequences can be used. This includes, for example, the *rbcL* gene used to classify diatoms (included). Additional nucleotide or protein databases may be created using the *create_db* module.



## Installation

### Requirements

python>=3.10, pandas, blast=2.15, pip

conda/mamba should be already installed (https://mamba.readthedocs.io/en/latest/)

### conda and pip

- Create the conda environment and install dependencies (through conda or mamba)

*conda create -y -n ISeqDb -c conda-forge -c bioconda python pip blast=2.15*

*conda activate ISeqDb*

- Install ISeqDb from PyPI

*pip install ISeqDb*


### Uninstalling

To uninstall, or before installing new versions:

*conda deactivate*

*conda env remove -y -n ISeqDb*

### Databases

Databases have a short description under their directory. New nucleotide and protein subject databases can be created using the create_db module. Databases work only with blast >=2.15 (after activating ISeqDb, check: blastn -version).



## Basic usage

ISeqDb has three modules:

**find_seqs**: Identify sequences in databases using megablast (default), blastn or blastx
*ISeqDb find_seqs /path_to/queryfile.fasta /path_to/targetdatabase.tar.gz /path_to/outputfile.txt*

**inspect_db**: Inspect or save the sequence database
*ISeqDb inspect_db /path_to/arch.tar.gz*  -- (inspect database)
*ISeqDb inspect_db /path_to/arch.tar.gz -d /outdir* -- (inspect and save a copy arch.fasta)

**create_db**: Create a database from a fasta/multifasta file using makeblast
*ISeqDb create_db /path_to/arch.fasta -m "nucl"* -- (nucleotide archives)
*ISeqDb create_db /path_to/arch.fasta -m "prot"* -- (protein archives)



## Usage

#### find_seqs

###### positional arguments:

*queryfile*            path/file with extension .fasta .fas .fa .fna .ffn .faa; e.g. /dir/query.fasta

*targetdb*             Database for the blast analysis (with path and file extension .tar.gz) - e.g. /dir/arch.tar.gz

*outputfile*           Output name file (with path) - e.g. /dir/out.txt

###### options:

-h, --help            show this help message and exit

-k {megablast,blastn,blastx}, --task {megablast,blastn,blastx}
Task: megablast (nucl), blastn (nucl), blastx (prot); default=megablast

-m MAXTARGSEQ, --maxtargseq MAXTARGSEQ
-Keep max target sequences >= maxtargseq; default=100

-e MINEVALUE, --minevalue MINEVALUE
Keep hits with evalue <= minevalue; default=1e-6

-p MINPIDENT, --minpident MINPIDENT
Keep hits with pident >= minpident (only megablast/blastn); default=85

-t THREADS, --threads THREADS
Number of threads to use; default=1

-s {bitscore,pident,evalue,subject_seq_title}, --sortoutput {bitscore,pident,evalue,subject_seq_title}
Sort output by colname; default=bitscore

-d {comma,semicolon,tab}, --delimiter {comma,semicolon,tab}
Output delimiter: comma, semicolon, tab; default=comma

###### Output legend (in square brackets, the blast codes)

- *query_id*:		         query/sequence identifier [qacc]
- *subject_accession*:	  accession number or subject identifier in the database [sacc]
- *pident*:			     percentage of identical matches in query and subject sequences [pident]
- *n_ident_match*:               number of identical bases/matches [nident]
- *n_diff_match*:                  number of different bases/matches [mismatch]
- *n_gaps*:                            total number of gaps [gaps]
- *alignment_length*:           length of the alignment between query and subject sequences [length]
- *query_start_al*:                start of alignment in query [qstart]
- *query_end_al*:                 end of alignment in query [qend]
- *subj_start_al*:                  start of alignment in subject [sstart]
- *subj_end_al*:                    end of alignment in subject [send]
- *qlen*:                    	    query sequence length [qlen]
- *slen*:                    	     subject sequence length [slen]
- *bitscore*:                          bit score [bitscore]
- *evalue*:                            expect value [evalue]
- *subject_seq_title*:            title of subject sequence in database [stitle]
- *align_query_seq*:            aligned part of query sequence [qseq]
- *align_subj_seq*:               ligned part of subject sequence [sseq]

###### example:

ISeqDb find_seqs ``\``

-k "megablast" -p 95 -e 1e-16 -t 8 -d tab -s pident  ``\``

/inputdir/file_nucleotide.fna ``\``

/archdir/mcyE_2403.tar.gz ``\``

/outdir/ISeqDb_output.txt



When comparing a DNA (nucleotide) fasta query with a protein sequence database, blastx must be used. The protein sequence database can be created using create_db with the option -m prot (see below).



#### inspect_db

###### positional arguments:

*targetdb_inspect*              Database for the blast analysis  (with path and file extension .tar.gz) - e.g. /dir/arch.tar.gz

###### options:

-h, --help            show this help message and exit

-d SAVEDB, --savedb SAVEDB
Output directory (with path) - e.g. /dir/; if not indicated, default=nosave

###### example:

ISeqDb inspect_db ``\``

-d /outdir/ ``\``

/archdir/mcyB_2403.tar.gz



#### create_db

###### positional arguments:

*targetfasta*           path/file with extension .fasta .fas .fa .fna .ffn .faa; e.g. /dir/arch.fasta

###### options:

-h, --help            show this help message and exit

-m {nucl,prot}, --moltype {nucl,prot}
Molecule type in fasta file, nucl (nucleotide) or prot (protein)

###### example:

ISeqDb create_db ``\``

-m prot ``\``

/inputdir/geneseq.faa




___
#### ISeqDb relies on BLAST®:

   -   BLAST® Command Line Applications User Manual [Internet]. Bethesda (MD): National Center
       for Biotechnology Information (US); 2008-.
   -   Camacho C., Coulouris G., Avagyan V., Ma N., Papadopoulos J., Bealer K., Madden T.L. (2008)
       “BLAST+: architecture and applications.” BMC Bioinformatics 10:421. PubMed

___
#### Acknowledgements

HORIZON-MSCA-2021-SE-01, AlgaeNet4AV, Project ID 101086437

