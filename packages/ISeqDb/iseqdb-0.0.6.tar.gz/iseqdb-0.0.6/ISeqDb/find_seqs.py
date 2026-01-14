# ISeqDb - Identify Sequences in Databases
# version 0.0.6
# module find_seqs
# Nico Salmaso, FEM, nico.salmaso@fmach.it
# This program is distributed under the GNU General Public License (GNU GPL v.3) https://www.gnu.org/licenses/

import pandas as pd
import os
import sys
import tarfile
from pandas import DataFrame


def run(args):

    dirquery, file_query = os.path.split(args.queryfile)
    if len(dirquery) == 0:
        print(" ")
        print("query directory not indicated")
        print(" ")
        sys.exit(1)
    if len(file_query) == 0:
        print(" ")
        print("name query file not indicated")
        print(" ")
        sys.exit(1)
    if any(c in " ;&|$-" for c in dirquery):
        print(" ")
        print(dirquery)
        print(" ")
        print("Error: spaces or characters ;&|$- in dir names are not allowed")
        print(" ")
        sys.exit(1)
    if any(c in " ;&|$-" for c in file_query):
        print(" ")
        print(file_query)
        print(" ")
        print("Error: spaces or characters ;&|$- in file names are not allowed")
        print(" ")
        sys.exit(1)

    dirtarget, file_name_db = os.path.split(args.targetdb)
    if len(dirtarget) == 0:
        print(" ")
        print("db directory not indicated")
        print(" ")
        sys.exit(1)
    if len(file_name_db) == 0:
        print(" ")
        print("database.tar.gz name not indicated")
        print(" ")
        sys.exit(1)
    if any(c in " ;&|$-" for c in dirtarget):
        print(" ")
        print(dirtarget)
        print(" ")
        print("Error: spaces or characters ;&|$- in dir names are not allowed")
        print(" ")
        sys.exit(1)
    if any(c in " ;&|$-" for c in file_name_db):
        print(" ")
        print(file_name_db)
        print(" ")
        print("Error: spaces or characters ;&|$- in archive names are not allowed")
        print(" ")
        sys.exit(1)

    diroutput, file_name_ou_1 = os.path.split(args.outputfile)
    if len(diroutput) == 0:
        print(" ")
        print("output directory not indicated")
        print(" ")
        sys.exit(1)
    if len(file_name_ou_1) == 0:
        print(" ")
        print("output file name not indicated")
        print(" ")
        sys.exit(1)
    if any(c in " ;&|$-" for c in diroutput):
        print(" ")
        print(diroutput)
        print(" ")
        print("spaces or characters ;&|$- in dir names are not allowed")
        print(" ")
        sys.exit(1)
    if any(c in " ;&|$-" for c in file_name_ou_1):
        print(" ")
        print(file_name_ou_1)
        print(" ")
        print("spaces or characters ;&|$- in file names are not allowed")
        print(" ")
        sys.exit(1)

    # ##############################################

    # check if the query file has the correct extensions
    file_exte = ['.fasta', '.fas', '.fa', '.fna', '.ffn', '.faa']
    exte = os.path.splitext(args.queryfile)[1]
    if exte.lower() in file_exte:
        print("fasta ext pass")
    else:
        print(f"{args.queryfile} does not have a valid file extension .fasta .fas .fa .fna .ffn .faa")
        sys.exit(1)

    # check if the subject database has the correct extension
    if args.targetdb.endswith('.tar.gz'):
        print("db ext pass")
    else:
        print(f"{args.targetdb} does not have a valid file extension .tar.gz")
        sys.exit(1)

    # check if the query file begins with > (greater-than)
    def check_char_1(filename):
        try:
            with open(filename, 'r') as file:
                char_1 = file.read(1)
                return char_1 == '>'
        except FileNotFoundError:
            print(f"{filename} does not exist")
            return False
        except UnicodeDecodeError:
            print("")
            print(f"{filename} is binary or contains invalid data")
            sys.exit(1)

    if check_char_1(args.queryfile):
        print("ch_1 pass")
    else:
        print("")
        print(f"{args.queryfile}: line 1 is not compatible with the structure of a fasta file")
        sys.exit(1)

    # ##############################################

    # Other check

    if not (1 <= args.minpident <= 100):
        print(f"Error: pident {args.minpident} is not in the range 1:100")
        sys.exit(1)

    # ##############################################

    file_name_ou = file_name_ou_1.split('.')[0]

    # open and extract database
    datseqtar = tarfile.open(args.targetdb)
    # extracting file
    datseqtar.extractall(dirtarget)
    datseqtar.close()

    datseq = args.targetdb.split('.')[0]

    if (args.task == "megablast") or (args.task == "blastn"):
        define_cmd: str = (
            f'blastn -query {args.queryfile} -db {datseq} -task {args.task} '
            f'-perc_identity {args.minpident} -dust no -evalue {args.minevalue} '
            f'-outfmt \'6 delim=  qacc sacc pident nident mismatch gaps length '
            f'qstart qend sstart send qlen slen bitscore evalue stitle qseq sseq\' '
            f'-max_target_seqs {args.maxtargseq} -num_threads {args.threads} '
            f'| tee -i {args.outputfile}_nh.txt'
        )
        os.system(define_cmd)
    elif args.task == "blastx":
        define_cmd: str = (
            f'blastx -query {args.queryfile} -db {datseq} -task {args.task} '
            f'-evalue {args.minevalue} '
            f'-outfmt \'6 delim=  qacc sacc pident nident mismatch gaps length '
            f'qstart qend sstart send qlen slen bitscore evalue stitle qseq sseq\' '
            f'-max_target_seqs {args.maxtargseq} -num_threads {args.threads} '
            f'| tee -i {args.outputfile}_nh.txt'
        )
        os.system(define_cmd)
    else:
        print(" ")
        print("allowed task: megablast, blastn, blastx")
        sys.exit(1)

    # cleaning 1

    if (args.task == "megablast") or (args.task == "blastn"):
        chartask = ".n"
    elif args.task == "blastx":
        chartask = ".p"
    else:
        print(" ")
        print("allowed tasks are megablast, blastn or blastx")
        sys.exit(1)

    os.remove("".join([datseq, chartask, 'db']))
    os.remove("".join([datseq, chartask, 'hr']))
    os.remove("".join([datseq, chartask, 'in']))
    os.remove("".join([datseq, chartask, 'js']))
    os.remove("".join([datseq, chartask, 'og']))
    os.remove("".join([datseq, chartask, 'os']))
    os.remove("".join([datseq, chartask, 'ot']))
    os.remove("".join([datseq, chartask, 'sq']))
    os.remove("".join([datseq, chartask, 'tf']))
    os.remove("".join([datseq, chartask, 'to']))

    column_names: list[str] = ['query_id', 'subject_accession', 'pident', 'n_ident_match', 'n_diff_match',
                               'n_gaps', 'alignment_length', 'query_start_al', 'query_end_al', 'subj_start_al',
                               'subj_end_al', 'qlen', 'slen', 'bitscore', 'evalue', 'subject_seq_title',
                               'align_query_seq', 'align_subj_seq']

    file_header = f"{args.outputfile}_nh.txt"
    output_file = f"{args.outputfile}"

    # when the file is empty (no matches)
    if os.stat(file_header).st_size == 0:
        with open(file_header, 'w') as f:
            column_names_str = '\t'.join(map(str, column_names))
            f.write(column_names_str)
            print("")
            print('_____________________________________')
            print("")
            print("No matches between query and subject sequences")
            print('_____________________________________')

    # Read the file into a DataFrame; do not consider the first line in the form of header
    dframe = pd.read_csv(file_header, delimiter='\t', header=None)
    # Convert the dframe (list of lists) and add column names in the first row
    data = dframe.values.tolist()
    data.insert(0, column_names)
    dataf: DataFrame = pd.DataFrame(data)
    dataf.to_csv(output_file, sep='\t', index=False, header=False)

    # sort file
    outputfile = pd.read_csv(args.outputfile, sep='\t')
    outputfile_sorted = outputfile.sort_values(by=args.sortoutput, ascending=False)

    if args.delimiter == "semicolon":
        sorted_file_name = os.path.join(diroutput, file_name_ou + '_sorted.csv2')
        sorted_file_name = str(sorted_file_name)
        outputfile_sorted.to_csv(sorted_file_name, sep=";", index=False)
    elif args.delimiter == "tab":
        sorted_file_name = os.path.join(diroutput, file_name_ou + '_sorted.tsv')
        sorted_file_name = str(sorted_file_name)
        outputfile_sorted.to_csv(sorted_file_name, sep="\t", index=False)
    else:
        sorted_file_name = os.path.join(diroutput, file_name_ou + '_sorted.csv')
        sorted_file_name = str(sorted_file_name)
        outputfile_sorted.to_csv(sorted_file_name, sep=",", index=False)

    print(' ')
    print('_____________________________________')
    print(' ')
    print("queryfile:", args.queryfile)
    print('')
    print("targetdb:", args.targetdb)
    print('')
    print("outputfile:", args.outputfile)
    print('')
    print("outputfile (sorted):", sorted_file_name)
    print('')
    print("minpident:", args.minpident)
    print('')
    print("task:", args.task)
    print('')
    print("minevalue:", args.minevalue)
    print('_____________________________________')
    print(' ')

    if args.task == "blastx":
        print('')
        print("minpident not defined in blastx")

    # cleaning 2
    os.remove(args.outputfile + '_nh.txt')
