# ISeqDb - Identify Sequences in Databases
# version 0.0.6
# module, create_db
# Nico Salmaso, FEM, nico.salmaso@fmach.it
# This program is distributed under the GNU General Public License (GNU GPL v.3) https://www.gnu.org/licenses/

import os
import sys
import tarfile


def run(args):

    print('_____________________________________')
    print(' ')
    print("Database:", args.targetfasta)
    print('_____________________________________')
    print(' ')

    dirfasta, file_name_fs = os.path.split(args.targetfasta)
    datseq = file_name_fs.split('.')[0]

    if len(dirfasta) == 0:
        print(" ")
        print("input directory not indicated; full path should be indicated")
        print(" ")
        sys.exit(1)
    if len(file_name_fs) == 0:
        print(" ")
        print("fasta file name not indicated")
        print(" ")
        sys.exit(1)
    if any(c in " ;&|$-" for c in dirfasta):
        print(" ")
        print(dirfasta)
        print(" ")
        print("Error: spaces or characters ;&|$- in dir names are not allowed")
        print(" ")
        sys.exit(1)
    if any(c in " ;&|$-" for c in file_name_fs):
        print(" ")
        print(file_name_fs)
        print(" ")
        print("Error: spaces or characters ;&|$- in file names are not allowed")
        print(" ")
        sys.exit(1)

    # ##############################################
    # check if the query file has the correct extensions
    file_exte = ['.fasta', '.fas', '.fa', '.fna', '.ffn', '.faa']
    exte = os.path.splitext(args.targetfasta)[1]
    if exte.lower() in file_exte:
        print("fasta ext pass")
    else:
        print(f"{args.targetfasta} does not have a valid file extension .fasta .fas .fa .fna .ffn .faa")
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

    if check_char_1(args.targetfasta):
        print("ch_1 pass")
    else:
        print("")
        print(f"{args.targetfasta}: line 1 is not compatible with the structure of a fasta file")
        sys.exit(1)

    # ##############################################

    outdir = os.path.join(str(dirfasta), str(datseq) + '_out')

    if os.path.isdir(outdir):
        print("Cannot write an existing directory: ", outdir)
        print(" ")
        sys.exit(1)
    else:
        os.mkdir(outdir)

    define_cmd_1: str = (
        f'makeblastdb -in {args.targetfasta} -input_type fasta -dbtype {args.moltype} '
        f'-parse_seqids -out {dirfasta}"/"{datseq} '
    )
    os.system(define_cmd_1)

    if args.moltype == "nucl":
        chartask = ".n"
    elif args.moltype == "prot":
        chartask = ".p"
    else:
        print(" ")
        print("allowed moltype are nucl (nucleotides) or prot (proteins)")
        sys.exit(1)

    elements_db = [
        ("".join([datseq, chartask, 'db'])),
        ("".join([datseq, chartask, 'hr'])),
        ("".join([datseq, chartask, 'in'])),
        ("".join([datseq, chartask, 'js'])),
        ("".join([datseq, chartask, 'og'])),
        ("".join([datseq, chartask, 'os'])),
        ("".join([datseq, chartask, 'ot'])),
        ("".join([datseq, chartask, 'sq'])),
        ("".join([datseq, chartask, 'tf'])),
        ("".join([datseq, chartask, 'to']))
    ]

    for fileelem in elements_db:
        os.rename(os.path.join(dirfasta, fileelem), os.path.join(outdir, fileelem))

    filetargz = (datseq + '.tar.gz')
    output_targz = os.path.join(dirfasta, filetargz)

    with tarfile.open(output_targz, "w:gz") as tar:
        for fileelem in elements_db:
            direl = os.path.join(outdir, fileelem)
            tar.add(direl, arcname=fileelem)
            os.remove(direl)

    os.rmdir(outdir)
