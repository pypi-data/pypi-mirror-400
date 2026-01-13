#!/usr/bin/env python3
# Copyright (C) 2025 Otter Brown
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 only.

import numpy as np
import pandas as pd
import math
import os
import json
from Bio.PDB import *
import urllib.request

# LAST MODIFIED ON 250811


# preloaded dictionary
IUPC_code_to_bases = {'A': 'A', 'T': 'T', 'C': 'C', 'G': 'G', 'M': 'AC', 'R': 'AG', 'W': 'AT', 'S': 'GC', 'Y': 'CT',
                      'K': 'GT', 'V': 'AGC', 'H': 'ACT', 'D': 'AGT', 'B': 'GCT', 'N': 'AGCT'}
IUPC_bases_to_code = {'A': 'A', 'T': 'T', 'C': 'C', 'G': 'G', 'AC': 'M', 'AG': 'R', 'AT': 'W', 'GC': 'S', 'CT': 'Y',
                      'GT': 'K', 'AGC': 'V', 'ACT': 'H', 'AGT': 'D', 'GCT': 'B', 'AGCT': 'N'}
aa3_1 = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLU': 'E', 'GLN': 'Q', 'GLY': 'G', 'HIS': 'H',
         'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W',
         'TYR': 'Y', 'VAL': 'V', 'MSE':'M'}
aa1_3 = {'A': 'ALA', 'R': 'ARG', 'N': 'ASN', 'D': 'ASP', 'C': 'CYS', 'E': 'GLU', 'Q': 'GLN', 'G': 'GLY', 'H': 'HIS',
         'I': 'ILE', 'L': 'LEU', 'K': 'LYS', 'M': 'MET', 'F': 'PHE', 'P': 'PRO', 'S': 'SER', 'T': 'THR', 'W': 'TRP',
         'Y': 'TYR', 'V': 'VAL'}


def Fetch_and_parse_cif(pdb_id, wd = None, add_CB = False, must_cif = False):  # version 251229
    import warnings
    from Bio import BiopythonWarning
    warnings.simplefilter('ignore', BiopythonWarning)       # only silence the warning during parsing

    import os
    if wd is None:
        wd = os.getcwd()

    if not '{}.cif'.format(pdb_id) in os.listdir(wd):

        if ('{}.pdb'.format(pdb_id) in os.listdir(wd)) and (must_cif == False):
            from Bio.PDB.PDBParser import PDBParser
            print('{}.pdb from local'.format(pdb_id))
            struc = PDBParser(PERMISSIVE=1).get_structure(pdb_id, '{}/{}.pdb'.format(wd, pdb_id))

        else:
            urllib.request.urlretrieve('https://files.rcsb.org/view/{}.cif'.format(pdb_id),
                                       '{}/{}.cif'.format(wd, pdb_id))
            print('{}.cif from url'.format(pdb_id))
            struc = MMCIFParser().get_structure(pdb_id, '{}/{}.cif'.format(wd, pdb_id))
    else:

        print('{}.cif from local'.format(pdb_id))
        struc = MMCIFParser().get_structure(pdb_id, '{}/{}.cif'.format(wd, pdb_id))



    if add_CB == True:
        # ala = MMCIFParser().get_structure(pdb_id, '{}/{}.cif'.format(wd, 'ala'))
        struc = Gly_add_CB(struc)
    return struc


# -------------------------------------------------- CIF parser by hh
def parse_cif_entity_sequences(cif_id):
    cif_path = f'{cif_id}.cif'
    import pandas as pd
    from collections import defaultdict

    """
    Returns:
    {
      "A": [[nums...], [aa1...]],
      "B": [[nums...], [aa1...]]
    }
    """
    global aa3_1
    # ---------- helpers (defined locally on purpose) ----------

    def int_to_letters(n: int) -> str:
        result = ""
        while n > 0:
            n -= 1
            result = chr(ord("A") + (n % 26)) + result
            n //= 26
        return result

    required_tags = [
        "_entity_poly_seq.entity_id",
        "_entity_poly_seq.mon_id",
        "_entity_poly_seq.num",
    ]

    # ---------- parse CIF loop ----------

    rows = []
    in_loop = False
    collecting_tags = False
    tags = []

    with open(cif_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            if line == "loop_":
                in_loop = True
                collecting_tags = True
                tags = []
                continue

            if in_loop:
                if collecting_tags and line.startswith("_"):
                    tags.append(line)
                    continue

                if collecting_tags:
                    collecting_tags = False
                    if not set(required_tags).issubset(tags):
                        in_loop = False
                        tags = []
                        continue

                if line.startswith("#"):
                    break

                values = line.split()
                if len(values) != len(tags):
                    continue

                rows.append(dict(zip(tags, values)))

    if not rows:
        return {}

    # ---------- dataframe + filtering ----------

    df = pd.DataFrame(rows)[required_tags]
    df["_entity_poly_seq.entity_id"] = df["_entity_poly_seq.entity_id"].astype(int)
    df["_entity_poly_seq.num"] = df["_entity_poly_seq.num"].astype(int)

    df = df[df["_entity_poly_seq.mon_id"].isin(aa3_1)]

    # ---------- merge entities, convert, transpose ----------

    merged = defaultdict(list)

    for _, row in df.iterrows():
        entity_letter = int_to_letters(row["_entity_poly_seq.entity_id"])
        merged[entity_letter].append(
            (row["_entity_poly_seq.num"], aa3_1[row["_entity_poly_seq.mon_id"]])
        )

    result = {}

    for entity, seq in merged.items():
        dict2 = parse_cif_atom_site(cif_id)
        seq.sort(key=lambda x: x[0])
        nums = [n + dict2[entity] for n, _ in seq]
        aas = [aa for _, aa in seq]
        result[entity] = [nums, aas]

    return result

def parse_cif_atom_site(cif_id):
    cif_path = f'{cif_id}.cif'
    import pandas as pd
    from collections import defaultdict

    """
    Returns:  {'A': 110}  where 110 is the index shift betwee label_seq_id and auth_seq_id
    """
    global aa3_1
    # ---------- helpers (defined locally on purpose) ----------

    def int_to_letters(n: int) -> str:
        result = ""
        while n > 0:
            n -= 1
            result = chr(ord("A") + (n % 26)) + result
            n //= 26
        return result

    required_tags = [
        "_atom_site.label_comp_id",
        "_atom_site.label_seq_id",
        "_atom_site.label_entity_id",
        "_atom_site.auth_seq_id"
    ]

    # ---------- parse CIF loop ----------

    rows = []
    in_loop = False
    collecting_tags = False
    tags = []

    with open(cif_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            if line == "loop_":
                in_loop = True
                collecting_tags = True
                tags = []
                continue

            if in_loop:
                if collecting_tags and line.startswith("_"):
                    tags.append(line)
                    continue

                if collecting_tags:
                    collecting_tags = False
                    if not set(required_tags).issubset(tags):
                        in_loop = False
                        tags = []
                        continue

                if line.startswith("#"):
                    break

                values = line.split()
                if len(values) != len(tags):
                    continue

                rows.append(dict(zip(tags, values)))

    if not rows:
        return {}

    # ---------- dataframe + filtering ----------

    df = pd.DataFrame(rows)[required_tags]

    df = df[df["_atom_site.label_comp_id"].isin(aa3_1)]
    # print('df', df.to_string())

    df["_atom_site.label_entity_id"] = df[ "_atom_site.label_entity_id"].astype(int)
    df["_atom_site.label_seq_id"] = df["_atom_site.label_seq_id"].astype(int)
    df["_atom_site.auth_seq_id"] = df[ "_atom_site.auth_seq_id"].astype(int)

    # ---------- merge entities, convert, transpose ----------

    merged = defaultdict(list)
    for _, row in df.iterrows():
        entity_letter = int_to_letters(row["_atom_site.label_entity_id"])
        merged[entity_letter].append(
            (row["_atom_site.label_seq_id"],row["_atom_site.auth_seq_id"])
        )

    result2 = dict()
    for key, value in merged.items():
        value2 = sorted(set(value))
        shift = [x[1]-x[0] for x in value2]
        shift = list(set(shift))
        if len(shift) >1:
            print('Nonlinear between label_seq_id and auth_seq_id')
            return
        else:
            result2[key] = shift[0]


    return result2

# -------------------------------------------------- RCSB alignment & index mapping between homolog
def consensus_from_fasta_string(fasta_str, threshold=0, verbose= False):
    """
    Calculate consensus sequence from a multiple sequence alignment (FASTA string).

    Parameters
    ----------
    fasta_str : str
        FASTA-formatted string containing aligned sequences.
    threshold : float, optional
        Minimum fraction (0–1) for a base/amino acid to be considered consensus (default = 0.5).

    Returns
    -------
    str
        Consensus sequence string.
    """

    from io import StringIO
    from collections import Counter
    from Bio import AlignIO, SeqIO

    # Clean input (remove leading spaces and blank lines)
    fasta_clean = "\n".join(line.strip() for line in fasta_str.strip().splitlines() if line.strip())

    # handle = StringIO(fasta_clean)
    # alignment = AlignIO.read(handle, "fasta")
    # n_seq = len(alignment)
    # length = alignment.get_alignment_length()



    # Read sequences manually (instead of AlignIO) to handle unequal lengths
    handle = StringIO(fasta_clean)
    records = list(SeqIO.parse(handle, "fasta"))

    if not records:
        raise ValueError("No sequences found in FASTA input")

    # Truncate all sequences to the same minimum length to avoid alignment length errors
    min_len = min(len(rec.seq) for rec in records)
    if verbose and any(len(rec.seq) != min_len for rec in records):
        print(f"⚠️ Truncating sequences to {min_len} residues (unequal lengths detected)")

    for rec in records:
        rec.seq = rec.seq[:min_len]

    # Convert to an alignment object
    from Bio.Align import MultipleSeqAlignment
    alignment = MultipleSeqAlignment(records)

    n_seq = len(alignment)
    length = alignment.get_alignment_length()


    consensus = []
    for i in range(length):
        # column = [rec.seq[i] for rec in alignment if rec.seq[i] != '-']
        # if not column:
        #     consensus.append('-')
        #     continue

        column = [rec.seq[i] for rec in alignment if rec.seq[i] != '-']
        if not column:
            consensus.append('-')
            continue


        counts = Counter(column)
        most_common, freq = counts.most_common(1)[0]
        if freq / n_seq >= threshold:
            consensus.append(most_common)
        else:
            consensus.append('x')  # ambiguous position

        if verbose:
            if  freq / n_seq ==1:
                print(f'{i+1}\t{most_common}')
            elif freq / n_seq <1:
                print(f'{i+1}\t{"".join(column)}')

    return ''.join(consensus)

def process_rcsbAln_output(aln_file):
    import re
    # Open the file and read all text into a string
    with open(aln_file, 'r') as file:
        file_text = file.read()

    lines = file_text.split('\n')

    if re.match(r"^\d+$", lines[0].strip()):
        lines = lines[1:]

    Row = []
    headers = []
    sequences = []
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace

        if re.match(r"^\d+$", line):
            Row.append(headers + sequences)
            headers = []
            sequences = []
            continue

        # Check if the line contains an ID
        if line.startswith('>'):
            headers.append(line[1:])
            sequences.append('')
            continue
        else:
            sequences[-1] += line

    Row.append(headers + sequences)
    seq = []
    for row in Row:
        seq.append(row[2].replace('-',''))

    df = pd.DataFrame(Row)
    df.columns = ['query_header', 'sbjct_header', 'query_aln','sbjct_aln']

    # df.to_csv('{}_processed.csv'.format(aln_file.split('.')[0]), index = False)
    # print('df', df)
    return df

def convert_aln_to_mapping_df(df, output_filename = 'mapping_df'):

    def aln_index_list_1229(sequence, pdb_id, s = None):
        ''' specify chain by e.g. pdb_id = "5OMF.A"
           All chains will be searched if  "." not in pdb_id
           If s is not none, it will over-write the pdb_id '''

        # print('pdb_id', pdb_id)
        if s is None:
            s = Fetch_and_parse_cif(pdb_id)


        output = []
        a = sequence.replace('-', ',_,').replace(',,', ',')
        a = a.split(',')

        curser = 1
        while len(a) > 0:
            x = a[0]
            if x == '_':
                output.append(np.nan)
                a = a[1:]
            else:
                i0 = index_start_aa(pdb_id, x, min_value = curser)
                if i0 is not None:
                    for j in range(len(x)):
                        output.append(i0 + j)
                    curser = output[-1] +1
                    a = a[1:]
                else:

                    j1 = None
                    for j in range(len(x), 2, -1):
                        i1 = index_start_aa(pdb_id, x[:j], min_value = curser)
                        if i1 is not None:
                            j1 = j
                            break

                    if j1 is not None:
                        for k in range(j1):
                            output.append(i1 + k)
                        curser = output[-1] +1

                        new_element = x[j1:]
                        a = [new_element] + a[1:]
                    else:
                        for k in range(len(x)):
                            output.append(np.nan)
                        a = a[1:]
        return output

    count = 0
    for i in range(df.shape[0]):

        qlst = aln_index_list_1229(df['query_aln'].iloc[i], df['query_header'].iloc[i] )
        slst = aln_index_list_1229(df['sbjct_aln'].iloc[i], df['sbjct_header'].iloc[i] )

        query_aln = list(df['query_aln'].iloc[i])
        sbjct_aln = list(df['sbjct_aln'].iloc[i])

        # df4 = pd.DataFrame({'{}_ind'.format(df['query_header'].iloc[i]): qlst,
        #                     '{}_aa'.format(df['query_header'].iloc[i]): query_aln,
        #                     '{}_ind'.format(df['sbjct_header'].iloc[i]): slst,
        #                     '{}_aa'.format(df['sbjct_header'].iloc[i]): sbjct_aln
        #                     })


        df4 = pd.DataFrame({'{}_ind'.format(df['query_header'].iloc[i]): pd.Series(
        [int(x) if pd.notna(x) else pd.NA for x in qlst], dtype="Int64"
    ),
                            '{}_aa'.format(df['query_header'].iloc[i]): query_aln,
                            '{}_ind'.format(df['sbjct_header'].iloc[i]): pd.Series(
        [int(x) if pd.notna(x) else pd.NA for x in slst], dtype="Int64"
    ),
                            '{}_aa'.format(df['sbjct_header'].iloc[i]): sbjct_aln
                            })
        # print(df4.to_string())

        if output_filename is not None and df.shape[0]==1:
            df4.to_csv(f'{output_filename}.csv', index = False)

        elif output_filename is not None and df.shape[0]>1:
            df4.to_csv(f'{output_filename}_{count}.csv', index = False)
            count +=1

    return df4

def convert_rcsbAln_output_to_mapping_df(wd, subdir, site_of_interest = None):

    def filter_df_for_resi(df, resi, forward=True):
        if forward:
            print(f'\nstructure 1 resi {resi} map to')
            df1 = df[df.iloc[:, 0].isin(resi)]

            a = list(df1.iloc[:, 2])
            a = [int(x) if not math.isnan(x) else x for x in a]
            print(f'structure 2 resi {a}')

        else:
            print(f'\nstructure 2 resi {resi} map to' )
            df1 = df[df.iloc[:, 2].isin(resi)]

            a = list(df1.iloc[:, 0])
            a = [int(x) if not math.isnan(x) else x for x in a]
            print(f'structure 1 resi {a}')

        # print('\ndf1', df1.to_string())
        df1.to_csv('df1.csv', index=False)

        return df1

    wd = f'{wd}/{subdir}' ; os.chdir(wd)
    subtitle = subdir.split("_")[1]
    df0 = process_rcsbAln_output(f'sequence_alignment_{subtitle}.fasta')
    df1 = convert_aln_to_mapping_df(df0, f'mapping_df_{subtitle}')


    # # Optional: if one is interested in certain residue of the first input
    if site_of_interest is not None:
        try:
            bo = (site_of_interest[0].lower() =='forward')
            filter_df_for_resi(df1, resi= site_of_interest[1], forward = bo)
        except:
            print("Format unmatch: site_of_interest shall be like this:\nsite_of_interest=('forward',[141, 406])")

    return df1

def index_start_aa(cif_id, query, s = None, chain = None, min_value = 1):

    if not os.path.isfile(f'{cif_id}.cif'):
        Fetch_and_parse_cif(cif_id, must_cif = True)

    dict1 = parse_cif_entity_sequences(cif_id)
    if '.' in cif_id:
        chain = cif_id.split('.')[1]

    # extract residue name and author index
    for key, value in dict1.items():
        if (chain is not None) and (key != chain):
            continue

        ind = value[0]
        seq = ''.join(value[1])

        try:
            curser = ind.index(min_value)
        except:
            curser = 0
        seq = seq[curser:]
        a = seq.find(query)
        if a != -1:
            a += curser
            return ind[a]
    return


# if __name__ == '__main__':
#
#     # { ........................................ Retrieve all polypeptide chains
#     a = Homolog.parse_cif_entity_sequences('4I2B'); print(a)
#     # }

