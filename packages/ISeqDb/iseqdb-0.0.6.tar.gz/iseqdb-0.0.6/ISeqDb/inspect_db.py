# ISeqDb - Identify Sequences in Databases
# version 0.0.6
# module inspect_db
# Nico Salmaso, FEM, nico.salmaso@fmach.it
# This program is distributed under the GNU General Public License (GNU GPL v.3) https://www.gnu.org/licenses/

import os
import tarfile
import sys


def run(args):

    # ##############################################
    # check if the database has the correct extension
    if args.targetdb_inspect.endswith('.tar.gz'):
        print("db ext pass")
    else:
        print(f"{args.targetdb_inspect} does not have a valid file extension .tar.gz")
        sys.exit(1)
    # ##############################################

    print('_____________________________________')
    print(' ')
    print("Database:", args.targetdb_inspect)
    print('')
    print('_____________________________________')
    print(' ')

    dirtarget, file_name_db = os.path.split(args.targetdb_inspect)
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
        print("Error: spaces or characters ;&|$- in file names are not allowed")
        print(" ")
        sys.exit(1)

    # open and extract database
    datseqtar = tarfile.open(args.targetdb_inspect)
    # extracting file
    datseqtar.extractall(dirtarget)
    datseqtar.close()

    # remove extensions
    datseq = args.targetdb_inspect.split('.')[0]
    datseq_name = file_name_db.split('.')[0]

    define_cmd_1: str = (
        f'blastdbcmd -db {datseq} -entry all -outfmt %f'
    )
    os.system(define_cmd_1)

    define_cmd_2: str = (
        f'blastdbcmd -db {datseq} -info'
    )
    os.system(define_cmd_2)

    if args.savedb != "nosave":
        file_name = os.path.join(args.savedb, datseq_name + '.fasta')
        file_name = str(file_name)
        define_cmd_3: str = (
            f'blastdbcmd -db {datseq} -entry all -outfmt %f > {file_name}'
        )
        os.system(define_cmd_3)
        print(" ")
        print("db saved: ", file_name)
        print(" ")
    else:
        print(" ")
        print("db not saved")
        print(" ")

    # cleaning
    if os.path.isfile(datseq + '.njs'):
        chartask = ".n"
    elif os.path.isfile(datseq + '.pjs'):
        chartask = ".p"
    else:
        print(" ")
        print("unidentified molecule")
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
