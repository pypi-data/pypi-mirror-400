#!/usr/bin/env python3
# Copyright (C) 2025 Otter Brown
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 only.

import numpy as np
import pandas as pd
import math
import os
from Bio.PDB import *
import urllib.request
import re
from pathlib import Path

# LAST MODIFIED ON 250811

aa3_1 = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLU': 'E', 'GLN': 'Q', 'GLY': 'G', 'HIS': 'H',
         'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W',
         'TYR': 'Y', 'VAL': 'V', 'MSE': 'M'}

cif_strings = {
    'ala': '''data_pdb
#
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_entity_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.auth_seq_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM 1 N N  . ALA A ? 1 ? -4.159 -3.129 -53.416 1.0 19.59 8 A 1 
ATOM 2 C CA . ALA A ? 1 ? -3.864 -4.191 -54.380 1.0 21.19 8 A 1 
ATOM 3 C C  . ALA A ? 1 ? -2.454 -4.127 -54.958 1.0 23.2  8 A 1 
ATOM 4 O O  . ALA A ? 1 ? -1.962 -5.111 -55.507 1.0 24.95 8 A 1 
ATOM 5 C CB . ALA A ? 1 ? -4.885 -4.166 -55.511 1.0 19.24 8 A 1 
#
''',
    'guanine': '''data_new_structure
#
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_entity_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.auth_seq_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM 1  C 'C1'' . G A ? 1 ? -8.050 3.242 11.526 1.0 0.0 12 A 1 
ATOM 2  N N9    . G A ? 1 ? -6.695 2.703 11.271 1.0 0.0 12 A 1 
ATOM 3  C C8    . G A ? 1 ? -6.324 1.421 10.980 1.0 0.0 12 A 1 
ATOM 4  N N7    . G A ? 1 ? -5.036 1.226 10.937 1.0 0.0 12 A 1 
ATOM 5  C C5    . G A ? 1 ? -4.503 2.467 11.269 1.0 0.0 12 A 1 
ATOM 6  C C6    . G A ? 1 ? -3.145 2.874 11.442 1.0 0.0 12 A 1 
ATOM 7  O O6    . G A ? 1 ? -2.128 2.192 11.334 1.0 0.0 12 A 1 
ATOM 8  N N1    . G A ? 1 ? -3.032 4.222 11.779 1.0 0.0 12 A 1 
ATOM 9  C C2    . G A ? 1 ? -4.106 5.079 11.938 1.0 0.0 12 A 1 
ATOM 10 N N2    . G A ? 1 ? -3.842 6.352 12.248 1.0 0.0 12 A 1 
ATOM 11 N N3    . G A ? 1 ? -5.383 4.692 11.798 1.0 0.0 12 A 1 
ATOM 12 C C4    . G A ? 1 ? -5.514 3.379 11.467 1.0 0.0 12 A 1 
ATOM 13 H H8    . G A ? 1 ? -7.055 0.644 10.850 1.0 0.0 12 A 1 
ATOM 14 H H1    . G A ? 1 ? -2.093 4.574 11.920 1.0 0.0 12 A 1 
ATOM 15 H H21   . G A ? 1 ? -2.887 6.670 12.338 1.0 0.0 12 A 1 
ATOM 16 H H22   . G A ? 1 ? -4.606 7.000 12.373 1.0 0.0 12 A 1 
#
''',
    'cytosine': '''data_new_structure
#
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_entity_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.auth_seq_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM 1  C 'C1'' . C A ? 1 ? 6.026 4.683 0.140 1.0 0.0 16 A 1 
ATOM 2  N N1    . C A ? 1 ? 4.731 4.004 0.441 1.0 0.0 16 A 1 
ATOM 3  C C2    . C A ? 1 ? 4.749 2.614 0.577 1.0 0.0 16 A 1 
ATOM 4  O O2    . C A ? 1 ? 5.810 1.997 0.622 1.0 0.0 16 A 1 
ATOM 5  N N3    . C A ? 1 ? 3.563 1.942 0.607 1.0 0.0 16 A 1 
ATOM 6  C C4    . C A ? 1 ? 2.394 2.595 0.534 1.0 0.0 16 A 1 
ATOM 7  N N4    . C A ? 1 ? 1.260 1.889 0.563 1.0 0.0 16 A 1 
ATOM 8  C C5    . C A ? 1 ? 2.347 4.028 0.479 1.0 0.0 16 A 1 
ATOM 9  C C6    . C A ? 1 ? 3.532 4.681 0.445 1.0 0.0 16 A 1 
ATOM 10 H H41   . C A ? 1 ? 1.306 0.882 0.638 1.0 0.0 16 A 1 
ATOM 11 H H42   . C A ? 1 ? 0.367 2.358 0.534 1.0 0.0 16 A 1 
ATOM 12 H H5    . C A ? 1 ? 1.427 4.594 0.477 1.0 0.0 16 A 1 
ATOM 13 H H6    . C A ? 1 ? 3.508 5.757 0.447 1.0 0.0 16 A 1 
#
''',
    'adenine': '''data_new_structure
#
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_entity_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.auth_seq_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM 1  C 'C1'' . A A ? 1 ? -5.581 -5.427 16.282 1.0 0.0 10 A 1 
ATOM 2  N N9    . A A ? 1 ? -4.574 -4.383 15.962 1.0 0.0 10 A 1 
ATOM 3  C C8    . A A ? 1 ? -3.258 -4.525 15.584 1.0 0.0 10 A 1 
ATOM 4  N N7    . A A ? 1 ? -2.546 -3.436 15.684 1.0 0.0 10 A 1 
ATOM 5  C C5    . A A ? 1 ? -3.453 -2.493 16.148 1.0 0.0 10 A 1 
ATOM 6  C C6    . A A ? 1 ? -3.339 -1.125 16.471 1.0 0.0 10 A 1 
ATOM 7  N N6    . A A ? 1 ? -2.191 -0.449 16.385 1.0 0.0 10 A 1 
ATOM 8  N N1    . A A ? 1 ? -4.439 -0.468 16.884 1.0 0.0 10 A 1 
ATOM 9  C C2    . A A ? 1 ? -5.589 -1.129 16.976 1.0 0.0 10 A 1 
ATOM 10 N N3    . A A ? 1 ? -5.824 -2.413 16.718 1.0 0.0 10 A 1 
ATOM 11 C C4    . A A ? 1 ? -4.697 -3.052 16.299 1.0 0.0 10 A 1 
ATOM 12 H H8    . A A ? 1 ? -2.819 -5.457 15.266 1.0 0.0 10 A 1 
ATOM 13 H H61   . A A ? 1 ? -2.149 0.520  16.672 1.0 0.0 10 A 1 
ATOM 14 H H62   . A A ? 1 ? -1.357 -0.926 16.075 1.0 0.0 10 A 1 
ATOM 15 H H2    . A A ? 1 ? -6.429 -0.551 17.328 1.0 0.0 10 A 1 
#
''',
    'thymine': '''data_new_structure
#
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_entity_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.auth_seq_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM 1  C 'C1'' . DT A ? 1 ? 7.498 -1.376 4.352 1.0 0.0 2 A 1 
ATOM 2  N N1    . DT A ? 1 ? 6.032 -1.145 4.383 1.0 0.0 2 A 1 
ATOM 3  C C2    . DT A ? 1 ? 5.548 0.132  4.096 1.0 0.0 2 A 1 
ATOM 4  O O2    . DT A ? 1 ? 6.271 1.106  3.898 1.0 0.0 2 A 1 
ATOM 5  N N3    . DT A ? 1 ? 4.170 0.267  4.048 1.0 0.0 2 A 1 
ATOM 6  C C4    . DT A ? 1 ? 3.243 -0.738 4.276 1.0 0.0 2 A 1 
ATOM 7  O O4    . DT A ? 1 ? 2.043 -0.483 4.214 1.0 0.0 2 A 1 
ATOM 8  C C5    . DT A ? 1 ? 3.827 -2.029 4.601 1.0 0.0 2 A 1 
ATOM 9  C C7    . DT A ? 1 ? 2.922 -3.207 4.902 1.0 0.0 2 A 1 
ATOM 10 C C6    . DT A ? 1 ? 5.175 -2.187 4.645 1.0 0.0 2 A 1 
ATOM 11 H H3    . DT A ? 1 ? 3.822 1.195  3.850 1.0 0.0 2 A 1 
ATOM 12 H H71   . DT A ? 1 ? 2.019 -3.149 4.294 1.0 0.0 2 A 1 
ATOM 13 H H72   . DT A ? 1 ? 3.429 -4.147 4.684 1.0 0.0 2 A 1 
ATOM 14 H H73   . DT A ? 1 ? 2.644 -3.187 5.956 1.0 0.0 2 A 1 
ATOM 15 H H6    . DT A ? 1 ? 5.606 -3.151 4.885 1.0 0.0 2 A 1 
#
''',
    'uracil': '''data_new_structure
#
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_entity_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.auth_seq_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM 1  C 'C1'' . U A ? 1 ? -7.964 -1.483 13.892 1.0 0.0 11 A 1 
ATOM 2  N N1    . U A ? 1 ? -6.500 -1.326 13.638 1.0 0.0 11 A 1 
ATOM 3  C C2    . U A ? 1 ? -5.956 -0.047 13.773 1.0 0.0 11 A 1 
ATOM 4  O O2    . U A ? 1 ? -6.624 0.946  14.055 1.0 0.0 11 A 1 
ATOM 5  N N3    . U A ? 1 ? -4.588 0.066  13.582 1.0 0.0 11 A 1 
ATOM 6  C C4    . U A ? 1 ? -3.734 -0.939 13.161 1.0 0.0 11 A 1 
ATOM 7  O O4    . U A ? 1 ? -2.531 -0.714 13.061 1.0 0.0 11 A 1 
ATOM 8  C C5    . U A ? 1 ? -4.352 -2.248 13.143 1.0 0.0 11 A 1 
ATOM 9  C C6    . U A ? 1 ? -5.676 -2.401 13.391 1.0 0.0 11 A 1 
ATOM 10 H H3    . U A ? 1 ? -4.203 0.994  13.681 1.0 0.0 11 A 1 
ATOM 11 H H5    . U A ? 1 ? -3.741 -3.119 12.954 1.0 0.0 11 A 1 
ATOM 12 H H6    . U A ? 1 ? -6.059 -3.402 13.476 1.0 0.0 11 A 1 
#
''',
    'inosine': '''data_new_structure
#
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_entity_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.auth_seq_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM 1  C 'C1'' . DI A ? 1 ? 25.617 45.130 10.842 1.0 30.92 8 A 1 
ATOM 2  N N9    . DI A ? 1 ? 24.562 44.444 11.593 1.0 30.11 8 A 1 
ATOM 3  C C8    . DI A ? 1 ? 23.478 43.756 11.105 1.0 29.4  8 A 1 
ATOM 4  N N7    . DI A ? 1 ? 22.704 43.256 12.037 1.0 29.52 8 A 1 
ATOM 5  C C5    . DI A ? 1 ? 23.319 43.638 13.224 1.0 32.17 8 A 1 
ATOM 6  C C6    . DI A ? 1 ? 22.989 43.403 14.582 1.0 32.43 8 A 1 
ATOM 7  O O6    . DI A ? 1 ? 22.011 42.770 14.999 1.0 34.82 8 A 1 
ATOM 8  N N1    . DI A ? 1 ? 23.855 43.934 15.531 1.0 31.44 8 A 1 
ATOM 9  C C2    . DI A ? 1 ? 24.936 44.633 15.099 1.0 29.05 8 A 1 
ATOM 10 N N3    . DI A ? 1 ? 25.318 44.903 13.860 1.0 32.28 8 A 1 
ATOM 11 C C4    . DI A ? 1 ? 24.467 44.371 12.964 1.0 31.55 8 A 1 
#
'''
}


# Freqeunted snippets
def Gly_add_CB(s, output=''):
    global cif_strings
    from Bio.PDB import MMCIFParser
    import io

    # Wrap the string in a file-like object
    cif_io = io.StringIO(cif_strings['ala'])
    ala = MMCIFParser().get_structure('ala', cif_io)
    # s1 = ala.copy()

    # Wrap the string in a file-like object
    cif_io = io.StringIO(cif_strings['ala'])

    gly = [x for x in s.get_residues() if x.resname in aa3_1.keys()]
    # gly = [x for x in resi if x.resname == 'GLY']

    for x in gly:
        if not 'CB' in [y.id for y in x.get_atoms()]:
            if all((atom_id in x) for atom_id in ("CA", "N", "C")):
                fixed = [x['CA'], x['N'], x['C']]

                s1 = ala.copy()
                y = [a for a in s1.get_residues()][0]
                moving = [y['CA'], y['N'], y['C']]

                sup = Superimposer()
                sup.set_atoms(fixed, moving)
                sup.apply([x for x in y.get_atoms()])

                y['CB'].detach_parent()
                s[x.full_id[1]][x.full_id[2]][x.full_id[3]].add(y['CB'])

    if output != '':
        io = MMCIFIO()
        io.set_structure(s)
        io.save(output)
    return s

def Fetch_and_parse_cif(pdb_id, wd=None, add_CB=False, verbose=False):  # version 251231
    import warnings
    from Bio import BiopythonWarning
    from Bio.PDB.PDBParser import PDBParser
    from Bio.PDB import MMCIFParser

    warnings.simplefilter('ignore', BiopythonWarning)  # only silence the warning during parsing

    extension = pdb_id.split('.')[-1] if (pdb_id.endswith('.cif') or pdb_id.endswith('.pdb')) else None
    pdb_id = pdb_id.split('.cif')[0].split('.pdb')[0]

    import os
    if wd is None:
        wd = os.getcwd()

    if extension is None:  # both cif and pdb acceptable, prioritize cif
        if not '{}.cif'.format(pdb_id) in os.listdir(wd):

            if '{}.pdb'.format(pdb_id) in os.listdir(wd):
                if verbose: print('{}.pdb from local'.format(pdb_id))
                struc = PDBParser(PERMISSIVE=1).get_structure(pdb_id, '{}/{}.pdb'.format(wd, pdb_id))

            else:
                urllib.request.urlretrieve('https://files.rcsb.org/view/{}.cif'.format(pdb_id),
                                           '{}/{}.cif'.format(wd, pdb_id))
                if verbose: print('{}.cif from url'.format(pdb_id))
                struc = MMCIFParser().get_structure(pdb_id, '{}/{}.cif'.format(wd, pdb_id))
        else:

            if verbose: print('{}.cif from local'.format(pdb_id))
            struc = MMCIFParser().get_structure(pdb_id, '{}/{}.cif'.format(wd, pdb_id))

    elif extension == 'cif':  # must cif
        if not '{}.cif'.format(pdb_id) in os.listdir(wd):
            urllib.request.urlretrieve('https://files.rcsb.org/view/{}.cif'.format(pdb_id),
                                       '{}/{}.cif'.format(wd, pdb_id))
            if verbose: print('{}.cif from url'.format(pdb_id))
            struc = MMCIFParser().get_structure(pdb_id, '{}/{}.cif'.format(wd, pdb_id))

        else:
            if verbose: print('{}.cif from local'.format(pdb_id))
            struc = MMCIFParser().get_structure(pdb_id, '{}/{}.cif'.format(wd, pdb_id))

    elif extension == 'pdb':

        if not '{}.pdb'.format(pdb_id) in os.listdir(wd):
            urllib.request.urlretrieve('https://files.rcsb.org/view/{}.pdb'.format(pdb_id),
                                       '{}/{}.pdb'.format(wd, pdb_id))
            if verbose: print('{}.pdb from url'.format(pdb_id))
            struc = PDBParser().get_structure(pdb_id, '{}/{}.pdb'.format(wd, pdb_id))

        else:
            if verbose: print('{}.pdb from local'.format(pdb_id))
            struc = PDBParser(PERMISSIVE=1).get_structure(pdb_id, '{}/{}.pdb'.format(wd, pdb_id))

    if add_CB == True:
        # ala = MMCIFParser().get_structure(pdb_id, '{}/{}.cif'.format(wd, 'ala'))
        struc = Gly_add_CB(struc)

    return struc

def Biopython_residue(s, model, chain, resi):
    '''Because somehow I can no longer select a residue by resi number along, so comes this function'''
    # print(chain)
    # print([x for y in s for x in y])
    residue = [x for x in s[model][chain] if x.id[1] == resi]
    if residue != []:
        return residue[0]
    else:
        return

# def fetch_all_resi(pdb_id, chain='A', wd=None, extension='pdb'):
#     s = Fetch_and_parse_cif(pdb_id, add_CB=False)
#     RESIS = []
#     for x in s[0][chain]:
#         resi = x.id[1]
#         RESIS.append(resi)
#     return RESIS
#
#
# def briefing_struc(struc):  # version 0721 a
#     ''' stress on DNA and heteroatoms print a brief overview of the struc '''
#
#     print('\nmodels per structure {}'.format(len(struc)))
#     print('chains per model {}'.format(len(struc[0])))
#     for chain in struc[0].child_list:
#         print('chain {}, {} residues including het'.format(chain.get_id(), len(chain.child_list)))
#
#         # ppb = Polypeptide.PPBuilder().build_peptides(chain)
#         # pp = [x.get_sequence() for x in ppb]
#         # Output_text(pp)
#         # if len(pp) != 0:
#         #     print(pp, [len(x) for x in pp])
#         #     # print([x for x in ppb.get_phi_psi_list()])
#
#         oligo = [x.resname for x in chain if x.get_id()[0] == ' ' and len(x.resname) != 3]
#         if len(oligo) != 0:
#             print(oligo, len(oligo))
#
#         het = [x.get_id()[0] for x in chain if x.get_id()[0] not in [' ', 'W']]
#         if len(het) != 0:
#             print(het, len(het))


# Writing PML file

# Writing PML
''' Minimal pml load script
pml = Pml_load(t0[i], wd2)                         # wd2 is source of cif file
pml += Pml_select_resi(residue0, l0[i], color = 'yellow')
paste = Pml_end(pml, 'output', wd, print_pml =True)       # wd is the place where pml file and future pse file be saved
Output_text(paste, 'paste', mode = 'a')
'''

def Pml_load(t1, wd2, color='atomic', initialize=True, extension='cif'):  # version 240307
    '''t1 is a list of pdb_id to be loaded, color is their corresponding color, if color unspecified, white'''

    wd_string = wd2.replace('/mnt/d', 'D:').replace('/', '\\')  # convert wsl path to window

    pml = ''
    if initialize == True:
        pml += 'reinitialize\n'

    if isinstance(t1, str):
        t1 = [t1]

    if isinstance(color, str):
        color = repeat(color, len(t1))

    for i in range(len(t1)):
        pdb_id = t1[i]
        c = color[i]

        if '.' not in pdb_id:
            pml += "load {}\\{}.{}\n".format(wd_string, pdb_id, extension)
        else:
            pml += "load {}\\{}\n".format(wd_string, pdb_id)

        pml += "cmd.color_deep('{}', '{}', 0)\n".format(c, pdb_id.split('.')[0])  # color an object by a single color

    pml += "/cmd.set('seq_view',1,'',0)\n"  # pymol command line

    return pml

def Pml_end(pml, pml_file, wd, log_file='', print_pml=False, print_path=True, orient=None, save_pse = True):
    wd_string = wd.replace('/mnt/d', 'D:').replace('/', '\\')  # convert wsl path to window

    if orient: pml += f"orient {orient}\n"

    pml += "cmd.select('sele','none')\n"

    if save_pse:  pml += 'save {}\\{}.pse\n'.format(wd_string, pml_file.split('.')[0])
    if log_file != '':
        Output_text('', log_file, extension='log')
        pml += 'log_open {}\\{}.log\n'.format(wd_string, log_file)

    if print_pml == True:
        print('\n\n{}'.format(pml))

    Output_text(pml, '{}/{}'.format(wd, pml_file.split('.')[0]), extension='pml')

    a = '@{}\\{}.pml\n'.format(wd_string, pml_file.split('.')[0])
    if print_path:
        print(f'\n{"."*64} Paste the following line in PYMOL command prompt\n{a}')
    return a

def Pml_select_resi(a, name, color='',
                    show='', show_as='', create_obj=False):  # 0806
    '''a is a list of residue, name is selection name, output a string of pymol command
    residues in different chains are selected together
    color include "by element green/cyan/magenta/yellow/white"
    '''

    # print('a', a)
    if not isinstance(a, list):
        a = [a]

    # print('a', a)
    t = [x.get_full_id() for x in a if x is not None]
    id = ['{}//{}/{}/'.format(x[0], x[2], x[3][1]) for x in t]

    id = ' or '.join(id)
    id = '({})'.format(id)

    pml = 'select {}, {}\n'.format(name, id)

    if color != '':
        if color == 'spectrum':
            pml += 'cmd.spectrum("count", selection="({})&elem C")\n'.format(name)

        elif color == 'by element green':
            pml += 'util.cba(33,"{}",_self=cmd)\n'.format(name)
        elif color == 'by element cyan':
            pml += 'util.cba(5,"{}",_self=cmd)\n'.format(name)
        elif color == 'by element magenta':
            pml += 'util.cba(154,"{}",_self=cmd)\n'.format(name)
        elif color == 'by element yellow':
            pml += 'util.cba(6,"{}",_self=cmd)\n'.format(name)
        elif color == 'by element white':
            pml += 'util.cba(144,"{}",_self=cmd)\n'.format(name)
        elif color == 'by element orange':
            pml += 'util.cba(13,"{}",_self=cmd)\n'.format(name)
        # elif color == 'cba33':
        #     pml += 'util.cba(33,"{}",_self=cmd)\n'.format(name)
        # elif color == 'cba5':
        #     pml += 'util.cba(5,"{}",_self=cmd)\n'.format(name)
        # elif color == 'cba144':
        #     pml += 'util.cba(144,"{}",_self=cmd)\n'.format(name)
        else:
            pml += 'color {}, {}\n'.format(color, name)
    if show != '':
        pml += 'cmd.show("{}"    ,"{}")\n'.format(show, name)
    if show_as != '':
        pml += 'cmd.show_as("{}"    ,"{}")\n'.format(show_as, name)
    # if create_obj != False:
    #     pml += 'cmd.create("{}","{}",zoom=0)\n'.format(name, name)
    #     if color != '':
    #         pml += "cmd.color_deep('{}', '{}', 0)\n".format(color, name)  # color an object by a single color

    return pml

def Pml_select_atom(a, name, color='', show='sphere'):  # version 0721 b
    '''a is a list of atom, name is selection name, output a string of pymol command
    automatic detect if they are in the same chain, if not, output two selection, color both same'''
    if not isinstance(a, list):
        a = [a]

    t = [x.get_full_id() for x in a]
    # print(t)
    id = ['{}//{}/{}/{}'.format(x[0], x[2], x[3][1], x[4][0]) for x in t]

    id = ' or '.join(id)
    id = '({})'.format(id)

    pml = 'select {}, {}\n'.format(name, id)
    if show != '':
        pml += 'cmd.show("{}", "{}")\n'.format(show, name)

    if color != '':
        pml += 'cmd.color_deep("{}", "{}", 0)\n'.format(color, name)

    return pml

def delete_pml_files(folder):
    from pathlib import Path
    folder = Path(folder)
    for file in folder.glob("*.pml"):
        try:
            file.unlink()  # deletes the file
            print(f"Deleted: {file.name}")
        except Exception as e:
            print(f"Could not delete {file.name}: {e}")
    return

def delete_aln_files(folder):
    from pathlib import Path
    folder = Path(folder)
    for file in folder.glob("*_aligned.pdb"):
        try:
            file.unlink()  # deletes the file
            print(f"Deleted: {file.name}")
        except Exception as e:
            print(f"Could not delete {file.name}: {e}")

    for file in folder.glob("*_aligned.cif"):
        try:
            file.unlink()  # deletes the file
            print(f"Deleted: {file.name}")
        except Exception as e:
            print(f"Could not delete {file.name}: {e}")
    return


# general def

def group_into_ranges(nums):
    if not nums:
        return []

    nums = sorted(nums)
    ranges = []
    start = prev = nums[0]

    for n in nums[1:]:
        if n == prev + 1:
            # still consecutive
            prev = n
        else:
            # range ends here
            ranges.append(range(start, prev + 1))
            start = prev = n
    # append the last range
    ranges.append(range(start, prev + 1))

    return ranges

def repeat(value, n):
    x = []
    for i in range(n):
        x.append(value)
    return x

def DFdict(df):
    f = []
    columns = list(df.columns)
    for title in columns:
        f.append(list(df[title]))

    d = dict(zip(columns, f))
    return d

def Read_text(filepath, encode=''):
    '''Read file '''
    if encode == '':
        try:
            with open(filepath) as f1:
                file1 = f1.read()
                print('"{}" encoded in ansi\n'.format(filepath.split('\\')[-1]))

        except UnicodeDecodeError:  # if the input was invalid
            try:
                with open(filepath, encoding='utf8') as f1:
                    file1 = f1.read()
                    print('"{}" encoded in utf-8\n'.format(filepath.split('\\')[-1]))
            except UnicodeDecodeError:  # if the input was invalid
                print('UnicodeDecodeError_{}'.format(z))

        return file1
    else:
        try:
            with open(filepath, encoding=encode) as f1:
                file1 = f1.read()
                print('"{}" encoded in {}}\n'.format(filepath.split('\\')[-1], encode))
        except UnicodeDecodeError:  # if the input was invalid
            print('UnicodeDecodeError_{}'.format(z))

        return file1

def Output_text(text, filename='output', extension='txt', mode='w'):  # version 0724
    with open('{}.{}'.format(filename, extension), mode=mode) as w:
        if isinstance(text, str):
            w.write(text)
        elif isinstance(text, list):
            t = [str(x) for x in text]
            w.write('\n'.join(t))

def Output_csv(df, filename='output', index=False):
    df = pd.DataFrame(df)
    df.to_csv('{}.csv'.format(filename), index=index)

def str_dict(d, separator='= ', space=20):
    w = []
    if not isinstance(d, dict):
        return
    else:
        for key, value in d.items():
            if isinstance(value, str):
                text = '"{}"'.format(value)
            else:
                text = value
            line = '{}{}{}'.format(key.ljust(space), separator, text)
            w.append(line)

    w = '\n'.join(w)
    return w

def To_dict(df_or_csv, key='', value='', keep_default_na=False):  # if number, True
    ''' detect whether input is a dataframe (type) or a csv file (string, without .csv)
    if it is a dictionary of numeric values, keep_defaut_na = True
    will convert first column to key and second column to value if unspecified '''
    if isinstance(df_or_csv, str):
        df = pd.read_csv('{}.csv'.format(df_or_csv), header=0, keep_default_na=keep_default_na)
    else:
        df = df_or_csv

    if key == '':
        db = df.set_index(df.columns[0]).to_dict()[df.columns[1]]
    else:
        db = df.set_index(key).to_dict()[value]
    return db

def flatten_list_int_range(a):
    if isinstance(a, int):
        a = [a]
        return a
    elif isinstance(a, range):
        a = list(a)
        return a
    elif isintance(a, list):
        a1 = []
        for x in a:
            if isinstance(x, int):
                a1.append(x)
            elif isinstance(x, range):
                a1 += list(x)
            else:
                print('Error: flatten_list_int_range failed')
                return
        return a1

#
# def Select_by_tuple_format(s, a):
#     # print('select', s, a)
#     '''
#     for the format ([],[]) or tuple of the format
#     for example
#     t0_align = (['A'], [141,143,210,214,259])
#
#     t1_align = (['A', 'A', 'A', 'A', 'A'],[18,20,125,129,154])
#
#     t0_sele = ([], [])          # all residues of all chains
#
#     t1_sele = ((['C'], []),
#             (['A'], [301,304]))    # all residues of chain 'C'; residue 301, 304 or chain 'A'
#
#     s is a biopython structure
#     '''
#
#     if not isinstance(a[0], tuple):  # A single format
#         a = tuple([a])
#
#     R = []
#     for (c, r) in a:
#         if c == [] and r == []:
#             R += [x for chain in s[0] for x in chain]
#
#         elif c != [] and r == []:
#             chains = [chain for chain in s[0] if chain.id in c]
#             for chain in chains:
#                 R += [x for x in chain]
#
#         elif c != [] and r != []:
#             if len(c) != len(r):
#                 c1 = repeat(c[0], len(r))
#             else:
#                 c1 = c
#             for i in range(len(r)):
#                 rr = Biopython_residue(s, 0, c1[i], r[i])
#                 if not rr is None:
#                     R.append(rr)
#
#     return R

def reformat_residues(r):
    '''
    r is a list of residues,
    return a dataframe with column names 'chain', 'resi', 'resn'
    '''

    a = []
    for x in r:
        a.append([x.parent.id, x.id[1], x.resname])
    a = pd.DataFrame(a, columns=['chain', 'resi', 'resn'])

    return a

# Structure editing tools

def handle_input_and_output_structure(t, t2 = None, add_CB = None, default_extension = 'pdb'): # input may be cif or pdb, default output pdb

    """ TO USE
    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)
    ......
    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse = False)

    """
    wd = os.getcwd()
    s = Fetch_and_parse_cif(t, wd, add_CB=add_CB)


    if t.endswith('.cif') or t.endswith('.pdb'): pdb_id, extension = t.split('.cif')[0].split('.pdb')[0], t.split('.')[-1]
    else: pdb_id, extension = t, default_extension  # if none specified in extension & t, default pdb


    if t2 is None: t2 = t   # overwrite

    if t2.endswith('.cif') or t2.endswith('.pdb'): pdb_id2, extension2 = t2.split('.cif')[0].split('.pdb')[0], t2.split('.')[-1]
    else: pdb_id2, extension2 = t2, default_extension # if none specified in extension & t, default pdb

    if extension2 == 'cif':  io2 = MMCIFIO()
    elif extension2 == 'pdb': io2 = PDBIO()

    return s, pdb_id, extension, pdb_id2, extension2, io2

def copy_structure_file(t, new_filename, verbose = False):
    wd = os.getcwd()
    s, pdb_id, extension, pdb_id2, extension2, io2= handle_input_and_output_structure(t, new_filename)

    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse = False)
    return s

def create_residue_cif(t, chain, resi, atoms_to_remove=[], new_filename = None, verbose = False):
    wd = os.getcwd()

    s = Fetch_and_parse_cif(t, wd)
    residue = Biopython_residue(s, 0, chain, resi).copy()

    from Bio.PDB import Structure, Model, Chain, Residue, Atom

    # 1. Create empty structure
    structure = Structure.Structure("new_structure")

    # 2. Create model (model_id = 0)
    model = Model.Model(0)
    structure.add(model)

    # 3. Create chain (chain_id = "A")
    chain = Chain.Chain("A")
    model.add(chain)

    if verbose: print('initial atoms', [a.id for a in residue])

    for x in atoms_to_remove:
        if x in residue:
            residue.detach_child(x)

    if verbose: print('after some removed', [a.id for a in residue])

    chain.add(residue.copy())
    if new_filename is None:
        new_filename = residue.resname
    else:
        new_filename= new_filename.replace('.cif', '').replace('.pdb', '')

    s.id = new_filename
    io = MMCIFIO()
    io.set_structure(structure)
    io.save(f"{new_filename}.cif")
    if verbose: print(f'{new_filename}.cif created')

    # Writing PML file
    if verbose:
        pml = Pml_load(f"{new_filename}.cif", wd)
        paste = Pml_end(pml, new_filename, wd,save_pse = False)  # wd is the place where pml file and future pse file be saved

    return

def rotate_atoms(t, chain, resi, atomAid, atomBid, atomsid_to_rotate, angle_deg=120, new_filename = None, verbose = False):
    '''
    :param pdb_id: e.g. 4I2B
    :param new_filename: e.g. test1
    :param chain_resi_from: e.g. (D,0)
    :param chain_resi_to: e.g. (B,1)
    :param atom_names: e.g. ['NN1', 'NN2']
    :return:
    '''

    def rotate_atoms_around_bond(atomA, atomB, atoms_to_rotate, angle_deg=120.0):
        """
        Rigidly rotate atoms around bond A–B using Bio.PDB.Superimposer.

        Parameters
        ----------
        atomA : Bio.PDB.Atom.Atom
            First atom defining the bond axis
        atomB : Bio.PDB.Atom.Atom
            Second atom defining the bond axis (pivot)
        atoms_to_rotate : list of Bio.PDB.Atom.Atom
            Atoms that will be rotated together as a rigid body
        angle_deg : float
            Rotation angle in degrees (default: 120)

        Returns
        -------
        sup : Bio.PDB.Superimposer
            Superimposer used for the transformation
        """

        import numpy as np
        from Bio.PDB import Superimposer
        from Bio.PDB.vectors import Vector, rotaxis

        # --- define rotation axis ---
        A = Vector(atomA.get_coord())
        B = Vector(atomB.get_coord())
        axis = (B - A).normalized()

        angle = np.deg2rad(angle_deg)
        R = rotaxis(angle, axis)

        # --- create rotated atom copies ---
        rotated_atoms = []

        for atom in atoms_to_rotate:
            atom_copy = atom.copy()

            v = Vector(atom.get_coord())
            v_rel = v - B
            v_rot = v_rel.left_multiply(R) + B

            atom_copy.set_coord(v_rot.get_array())
            rotated_atoms.append(atom_copy)

        # --- fit superimposer ---
        sup = Superimposer()
        sup.set_atoms(rotated_atoms, atoms_to_rotate)

        # --- apply rigid-body transform ---
        sup.apply(atoms_to_rotate)

        return sup

    # Transfer atoms from residue y to residue x

    wd = os.getcwd()

    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)


    x = Biopython_residue(s, 0, chain, resi)
    atomA = x[atomAid]
    atomB = x[atomBid]
    atoms_to_rotate = [a for a in x if a.id in atomsid_to_rotate]
    rotate_atoms_around_bond(atomA, atomB, atoms_to_rotate, angle_deg)

    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse=False)
    return

def transplant_atoms_btw_residues(t, chain_resi_from, chain_resi_to, atom_names, new_filename = None, verbose = False):
    '''
    :param pdb_id: e.g. 4I2B
    :param new_filename: e.g. test1
    :param chain_resi_from: e.g. (D,0)
    :param chain_resi_to: e.g. (B,1)
    :param atom_names: e.g. ['NN1', 'NN2']
    :return:
    '''

    # Transfer atoms from residue y to residue x

    wd = os.getcwd()
    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)


    x = Biopython_residue(s, 0, chain_resi_to[0], chain_resi_to[1])
    y = Biopython_residue(s, 0, chain_resi_from[0], chain_resi_from[1])


    stray_atom = []
    for atom in list(y.get_atoms()):
        if atom.get_name() in atom_names:
            atom.detach_parent()
            x.add(atom)

    # for atom in y:
    #
    #     if atom.get_name() in atom_names:
    #
    #         atom.detach_parent()
    #         print(atom.get_parent() is y)
    #         print(y.child_list)
    #         atom.id = atom.id+"t"
    #         x.add(atom)

    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        pml += Pml_select_resi(x, 'edit', show='stick', color='by element yellow')
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse=False)

    return

def base_substitution(t, chain, resi, change_to, new_filename = None, verbose = False):
    wd = os.getcwd()

    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)

    x = Biopython_residue(s, 0, chain, resi)  # target residue

    global cif_strings

    from Bio.PDB import MMCIFParser
    import io

    # Wrap the string in a file-like object
    cif_io = io.StringIO(cif_strings[change_to])
    s1 = MMCIFParser().get_structure(change_to, cif_io)

    y = [r for r in s1.get_residues()][0].copy()

    R_aln = ["C1'", "N9", "C4", "N3"]
    Y_aln = ["C1'", "N1", "C2", "O2"]

    # detect YR of original res
    if 'N9' in x:
        fixed = [x[k] for k in R_aln]
    else:
        fixed = [x[k] for k in Y_aln]

    # detect YR of new res
    if 'N9' in y:
        moving = [y[k] for k in R_aln]
    else:
        moving = [y[k] for k in Y_aln]

    sup = Superimposer()
    sup.set_atoms(fixed, moving)
    sup.apply([a for a in y.get_atoms()])

    # remove nucleobase from x'
    if verbose: print('initial atoms', [a.id for a in x])

    to_detach = []
    for a in x:
        if not any([a.get_name().endswith("'"), 'P' in a.get_name(), len(a.get_name()) > 2]):
            to_detach.append(a.id)

    for atom_name in to_detach:
        x.detach_child(atom_name)

    if verbose: print('after some removed', [a.id for a in x])

    # add nucleobase atoms from y to x
    for atom in y:
        if atom.get_name() != "C1'":
            atom.detach_parent()
            x.add(atom)

    if verbose: print('after some added', [a.id for a in x]); print('\n')

    # change x.resname
    x.resname = change_to[0].upper() + x.resname[1:]

    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse = False)

    return s

def rename_chains(t, initial_chain_id, new_chain_id, reindex=None, new_filename = None, verbose = False):
    '''initial_chain_id and new_chain_id could be either list or string
    reindex could be an int, a list of int, or none'''
    wd = os.getcwd()
    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)

    if isinstance(initial_chain_id, str):
        if isinstance(new_chain_id, str):
            initial_chain_id = [initial_chain_id]
            new_chain_id = [new_chain_id]

    for i in range(len(new_chain_id)):
        cid0 = initial_chain_id[i]
        cid1 = new_chain_id[i]

        if cid1 in [chain.id for chain in s[0]] and cid0 != cid1:

            lst = []
            for residue in s[0][cid1]:
                lst.append(residue.id[1])
            start_resi = max(lst) + 1

            if isinstance(reindex, int):
                if reindex >= start_resi:
                    start_resi = reindex

            text = f'chain {cid0} appended to chain {cid1}, starting from index {start_resi}'

            for residue in s[0][cid0]:  # automatically reindex
                t = (residue.id[0], start_resi, residue.id[2])
                residue.id = t
                start_resi += 1
            s[0][cid0].id = cid1

        elif cid0 == cid1 and isinstance(reindex, int):
            text = f'reindex chain {cid0}, starting from index {reindex}'
            start_resi = reindex
            for residue in s[0][cid0]:  # reindex from 1
                t = (residue.id[0], start_resi, residue.id[2])
                text += f'\n\tchain {cid0} {residue.id} -> {t}'
                residue.id = t
                start_resi += 1


        elif cid0 == cid1 and isinstance(reindex, list):
            text = f'reindex chain {cid0} according to {reindex}'
            j = 0
            for residue in s[0][cid0]:  # reindex from list
                t = (residue.id[0], reindex[j], residue.id[2])
                text += f'\n\tchain {cid0} {residue.id} -> {t}'
                residue.id = t
                j += 1

        else:
            text = f'chain {cid0} renamed as {cid1}'

            if isinstance(reindex, int):
                text += f', starting from index {reindex}'
                start_resi = reindex
                for residue in s[0][cid0]:  # reindex from 1
                    t = (residue.id[0], start_resi, residue.id[2])
                    text += f'\n\tchain {cid0} {residue.id} -> chain {cid1} {t}'
                    residue.id = t
                    start_resi += 1

            s[0][cid0].id = cid1

        if verbose: print(text)


    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse = False)

    return s

def delete_chains(t, chains_to_remove, new_filename = None, verbose = False):
    wd = os.getcwd()
    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)


    if verbose: print('initials', [chain.id for chain in s[0]])

    for target in chains_to_remove:
        if target in [chain.id for chain in s[0]]:
            s[0].detach_child(target)

    if verbose: print('after some removed', [chain.id for chain in s[0]]); print('\n')



    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse = False)

    return s

def atom_to_hetatm(t, chain_id, new_filename = None, verbose = False):
    wd = os.getcwd()
    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)

    chain = s[0][chain_id]

    for residue in chain:
        t = ('H_', residue.id[1], residue.id[2])
        residue.id = t


    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    return s

def edit_residue(t, initial_chain_resi, new_chain_resi=None, new_resname=None, remove_atoms=None, new_filename = None, verbose = False):

    wd = os.getcwd()
    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)

    cid0, resi0 = initial_chain_resi

    x = Biopython_residue(s, 0, cid0, resi0)  # target residue

    if new_chain_resi is not None:
        cid1, resi1 = new_chain_resi

        if verbose: print(f'initial residue full id {x.get_full_id()}')

        t = (x.id[0], resi1, x.id[2])
        x.id = t
        s[0][cid0].detach_child(x.id)

        if cid1 not in [c.id for c in s[0]]:
            new_chain = Chain.Chain(cid1)
            s[0].add(new_chain)

        s[0][cid1].add(x)
        if verbose: print(f'new residue full id {x.get_full_id()}')

    if new_resname is not None:
        x.resname = new_resname.upper()

    if isinstance(remove_atoms, str):
        remove_atoms = [remove_atoms]
    if isinstance(remove_atoms, list):
        if verbose: print('\ninitial atoms', [a.id for a in x])
        for atomid in remove_atoms:
            if atomid in x:
                x.detach_child(atomid)
        if verbose: print('after some removed', [a.id for a in x])


    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file
    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        pml += Pml_select_resi(x, 'edit', show='stick', color='by element yellow')
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse=False)

    return s

def chain_shrinking(t, chain, resi_to_retain=None, resi_to_remove=None, new_filename = None, verbose = False):
    # either specify list_to_retain or list_to_remove

    wd = os.getcwd()
    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)

    c = s[0][chain]

    if resi_to_retain is not None:
        resi_to_retain =  flatten_list_int_range(resi_to_retain)
        resi_to_remove = [x.id[1] for x in c if x.id[1] not in resi_to_retain]
    elif resi_to_remove is not None:
        resi_to_remove = flatten_list_int_range(resi_to_remove)
    else:
        print('Error: either resi_to_remove or resi_to_retain has to be int, range, or a list of int & range')
        return

    for k in resi_to_remove:
        x = Biopython_residue(s, 0, chain, k)
        if x:
            c.detach_child(x.id)
            del x




    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse=False)

    return s

def duplicate_residue(t, initial_chain_resi, new_filename = None, verbose = False):
    # the duplicated residue will be attached to the end of the same chain

    wd = os.getcwd()
    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, new_filename)

    cid0, resi0 = initial_chain_resi
    x = Biopython_residue(s, 0, cid0, resi0)  # target residue

    # find the largest resi in the chain
    resis = []
    for residue in s[0][cid0]:  # reindex from list
        resis.append(residue.id[1])
    next_resi = max(resis) + 1

    x2 = x.copy()
    x2.detach_parent()
    x2.id = (x2.id[0], next_resi, x2.id[2])
    print(f'new: {cid0} {next_resi}')
    s[0][cid0].add(x2)


    # Set and output structure
    s.id = pdb_id2
    io2.set_structure(s)
    io2.save(f"{pdb_id2}.{extension2}")

    # Writing PML file to quickly see
    if verbose:
        pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
        pml += Pml_select_resi(x2, 'duplicate', show='stick', color='by element yellow')
        Pml_end(pml, f"{pdb_id2}.{extension2}", wd, save_pse=False)

    return s


# Virtual screen related

def format_for_rfdaa(list_of_ranges, s, e, chain='A', verbose=True):  # (s:e)
    list_of_ranges.sort(key=lambda r: (r.start, r.stop))

    text = []
    s2 = s
    for r in list_of_ranges:
        if r.start > s2:
            text.append(f'{chain}{s2}-{r.start - 1}')

        text.append(f'{r.stop - r.start}-{r.stop - r.start}')
        s2 = r.stop

    if s2 < e:
        text.append(f'{chain}{s2}-{e - 1}')

    text = ','.join(text)
    text = r"[\'" + text + r"\']"
    if verbose: print(text)
    return text

def format_for_lmpnn(list_of_ranges, chain='A', verbose=True):
    list_of_ranges.sort(key=lambda r: (r.start, r.stop))

    text = []

    for r in list_of_ranges:
        for j in r:
            text.append(f'{chain}{j}')

    text = ' '.join(text)
    text = r'"' + text + r'"'
    if verbose: print(text)
    return text

def calculate_rmsd(pdb1, pdb2, chain_resi_str, atoms_of_interest=None, atoms_to_exclude=None, sub_dir=None,
                   verbose=False, write_pml=False):  # must be pdb file
    """
    Calculate RMSD between subsets of residues in two structures.
    """

    def parse_chain_residues(input_str):
        """
        Parse input like 'A160 L72 L71' into [('A',160), ('L',72), ('L',71)]
        """
        entries = input_str.strip().split()
        parsed = []
        for entry in entries:
            m = re.match(r"([A-Za-z])(\d+)", entry)
            if not m:
                raise ValueError(f"Invalid format: {entry}")
            chain, resi = m.groups()
            parsed.append((chain, int(resi)))
        return parsed

    wd = os.getcwd()

    if sub_dir is not None:
        wd2 = f"{wd}/{sub_dir}"
    else:
        wd2 = wd

    s1 = Fetch_and_parse_cif(pdb1, wd, add_CB=True)  # note s1 ref in main os
    s2 = Fetch_and_parse_cif(pdb2, wd2, add_CB=True)  # s2 in sub_dir

    pairs = parse_chain_residues(chain_resi_str)

    Y = []

    ATOMS1 = []
    ATOMS2 = []
    all_res1 = []
    all_res2 = []
    SD = 0
    NUM = 0
    rmsd_of_resi = []
    for chain, resi in pairs:
        atoms1, atoms2 = [], []

        res1 = Biopython_residue(s1, 0, chain, resi)
        res2 = Biopython_residue(s2, 0, chain, resi)

        # calculate all shared atoms
        lst1 = [x.id for x in res1]
        lst2 = [x.id for x in res2]
        shared_atoms = [x for x in lst1 if x in lst2]

        if isinstance(atoms_of_interest, str):
            atoms_of_interest = [atoms_of_interest]

        if isinstance(atoms_to_exclude, str):
            atoms_to_exclude = [atoms_to_exclude]

        if isinstance(atoms_of_interest, list):
            shared_atoms = [x for x in shared_atoms if x in atoms_of_interest]

        if isinstance(atoms_to_exclude, list):
            shared_atoms = [x for x in shared_atoms if x not in atoms_to_exclude]

        if len(shared_atoms) == 0:
            continue

        sd = 0
        for atom_id in shared_atoms:
            d = (res1[atom_id] - res2[atom_id])
            sd += d ** 2
        rmsd = round(np.sqrt(sd / len(shared_atoms)), 3)

        Y.append([f"{chain}{resi}", rmsd])
        if verbose: print(f'{chain}{resi}\t{rmsd:.3f}\t{shared_atoms}')

        SD += sd
        NUM += len(shared_atoms)

        all_res1.append(res1)
        all_res2.append(res2)
        rmsd_of_resi.append(rmsd)

    RMSD_atom = round(np.sqrt(SD / NUM), 3)  # per atom
    RMSD_res = round(np.mean(rmsd_of_resi), 3)  # per atom

    if verbose:
        print(f'RMSD_atom\t{RMSD_atom:.3f}')
        print(f'RMSD_res\t{RMSD_res:.3f}')

    Y = pd.DataFrame(Y, columns=['chain_resi', 'rmsd'])
    if verbose: print('Y', Y)

    # Writing PML file
    if write_pml:
        pml = Pml_load([pdb1, pdb2], wd, extension='pdb')
        pml += Pml_select_resi(all_res1, 'res1', show='stick', color='by element yellow')
        pml += Pml_select_resi(all_res2, 'res2', show='stick', color='by element green')
        Pml_end(pml, f'rmsd', wd, print_pml=False)  # wd is the place where pml file and future pse file be saved

    # Calculate RMSD resi (average RMSD over residues, such that residues with multiple atoms weigh equally with those small)

    return Y, RMSD_atom, RMSD_res

def extract_bfactor_per_resi(pdb1, resi, chain='A', model=0):  # plddt of alphafold is output as bfactor (per residue)
    wd = os.getcwd()
    s = Fetch_and_parse_cif(pdb1, wd, add_CB=False)  # note s1 ref in main os

    residue = Biopython_residue(s, model, chain, resi)
    if "CA" in residue:
        atom = residue['CA']  # exported alphafold exports, plddt (per resi) is stored as bfactor in the pdb file.
        return round(atom.bfactor, 2)

    return None

def average_bfactors_per_chain(pdb1, chain='A', model=0, verbose=False):
    wd = os.getcwd()
    s = Fetch_and_parse_cif(pdb1, wd, add_CB=False)  # note s1 ref in main os

    x = []
    for residue in s[model][chain]:
        if "CA" in residue:
            atom = residue['CA']
            x.append(atom.bfactor)

    if verbose: print(f'pLDDT averaged over {len(x)} residues = {np.mean(x)}')
    return round(np.mean(x), 2)

def align_placer_output(ref_pdb, aln_start, aln_end, wd):
    def align_and_apply(ref_file, mob_file, others, res_start, res_end):

        from Bio.PDB import PDBParser, PDBIO, Superimposer
        parser = PDBParser(QUIET=True)
        io = PDBIO()

        # Load structures
        ref_structure = parser.get_structure("ref", ref_file)
        mob_structure = parser.get_structure("mob", mob_file)

        # Select CA atoms in the desired residue range
        def get_ca_atoms(structure, start, end):
            return [
                res["CA"]
                for res in structure.get_residues()
                if "CA" in res and start <= res.id[1] <= end
            ]

        ref_atoms = get_ca_atoms(ref_structure, res_start, res_end)
        mob_atoms = get_ca_atoms(mob_structure, res_start, res_end)

        # Superimpose mob -> ref
        sup = Superimposer()
        sup.set_atoms(ref_atoms, mob_atoms)
        sup.apply(mob_structure.get_atoms())  # apply to structure 1

        io.set_structure(mob_structure)
        # io.save(f"{output_prefix}_1.pdb")
        io.save(mob_file)  # over-write

        # Apply the same transformation to others
        for i, other_file in enumerate(others, start=2):
            other_struct = parser.get_structure(f"other{i}", other_file)
            sup.apply(other_struct.get_atoms())
            io.set_structure(other_struct)
            # io.save(f"{output_prefix}_{i}.pdb"
            io.save(other_file)  # over-write
        return sup

    os.chdir(wd)
    files = [f for f in os.listdir(wd) if f.endswith('.pdb')]

    pattern = re.compile(r'(.+?)_id(\d+)\.pdb$')

    basenames = []
    for f in files:
        match = pattern.match(f)
        if match:
            base = f"{match.group(1)}_id{match.group(2)}"
            basenames.append(f.split('.pdb')[0])

    print('basenames', basenames)

    for name in basenames:
        mob = f"{name}.pdb"
        others = [f"{name}_f.pdb", f"{name}_z.pdb"]
        align_and_apply(ref_pdb, mob, others, res_start=aln_start, res_end=aln_end)

    return

def align_and_rename_alphafold_pdbs(ref_pdb, aln_start, aln_end, input_folder, output_folder):
    os.chdir(output_folder)

    import re
    import shutil
    from pathlib import Path
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    pattern = re.compile(
        r"^(.*?)_unrelaxed_rank_(\d+)_alphafold2_model_(\d+)_seed_(\d+)$"
    )

    for file in input_folder.glob("*.pdb"):
        match = pattern.match(file.stem)
        if match:

            prefix, rank, model, seed = match.groups()
            # new_name = f"{prefix}_rank_{int(rank)}_model_{model}_seed_{int(seed)}.pdb"

            new_name = f"{prefix}_rank_{int(rank)}.pdb"
            new_file = output_folder / new_name
            shutil.copy(file, new_file)
            print(f"Copied: {file.name} -> {new_file.name}")

            # align the structure to a ref_pdb in the output_folder.
            t0 = ref_pdb
            t0_align = [(['A'], list(range(aln_start, aln_end)))]
            t0_sele = [(['A'], [])]

            t1 = new_name.split('.pdb')[0]
            t1_align = t0_align
            t1_sele = (['A'], [])

            make_chimera(t0, t1, t0_align, t1_align, t0_sele, t1_sele,
                         aln_atomID='aa',
                         new_filename='temp',
                         extension='pdb')

            delete_chains('temp', ['A'], 'temp')
            rename_chains('temp',
                          initial_id=['B'],
                          new_id=['A'],
                          new_filename=new_name.split('.pdb')[0],
                          extension='pdb')


        else:
            print(f"Skipped (pattern not matched): {file.name}")

    delete_pml_files(output_folder)
    delete_aln_files(output_folder)
    return



# Analyses & Bond calculation
def Calculate_residue_dist(r1, r2, atom=['CA', 'CB', 'N', 'O']):
    ''' x1 and x2 are each a single residue Calculate the nearest distance between atom specified  '''

    atom1 = [r1[a] for a in atom]
    atom2 = [r2[a] for a in atom]

    dist = []
    for a1 in atom1:
        for a2 in atom2:
            dist.append(a1 - a2)

    return min(dist)

def Calculate_residue_overlap(r1, r2, atom=['CA', 'CB', 'N', 'O'], dist_cutoff=3):
    ''' r1 and r2 are each a list of residues. Calculate residue pair within distance cut_off
    return True for overlap and False for separate '''

    for x in r1:
        for y in r2:
            dist = Calculate_residue_dist(x, y, atom=atom)
            if dist < dist_cutoff:
                return True
    return False

def Bond_matrix(wd, t,
                H_bond_cutoff=[2.2, 3.5],
                Metal_bond_cutoff=[1.5, 2.5],
                cc_bond_cutoff=[3, 4.5], minimum_cc_bond=2, ss_bond_cutoff=[1.8, 2.3],
                limit_pp_chains=['A', 'B', 'C', 'D']):
    '''
    Changes: make a comprehensive interaction list
    limit_pp_chains to prevent massive homo-polymeric structure
    '''

    global aa3_1

    wd3 = wd + '/input_Bond_matrices'
    if not os.path.isdir(wd3):
        print(f'create folder {wd3}')
        os.mkdir(wd3)

    def Lewis_conjugate_detector2(residues, note='', bond_cutoff=[2.2, 3.5], confine_target_atom=[], consider_resi=True,
                                  include_metal=True, printout=False):
        ''' Provide a list of residues, the first of which is target and others queries,
            O atoms are assumed H-bond acceptor (conjugate base)
            N atoms are assume H-bond donor (conjugate acid)
            Unless specified otherwise AS below'''

        # for dna bases

        acceptor_only = ['DA,N1', 'DA,N3', 'DA,N7', 'DA,N9',
                         'DC,N1', 'DC,N3',
                         'DG,N3', 'DG,N7', 'DG,N9',
                         'DT,N1', 'DU,N1',
                         'A,N1', 'A,N3', 'A,N7', 'A,N9',
                         'C,N1', 'C,N3',
                         'G,N3', 'G,N7', 'G,N9',
                         'T,N1', 'U,N1']

        donor_and_acceptor = ['SER,OG', 'THR,OG1', 'TYR,OH', 'HIS,ND1', 'HIS,NE2', 'CYS,SG',
                              'A,O2', 'T,O2', 'C,O2', 'G,O2', 'U,O2']

        donor_only = []
        if include_metal == True:
            donor_only = ['NA,NA', 'K,K', 'CA,CA', 'MG,MG', 'MN,MN', 'NI,NI', 'CO,CO', 'ZN,ZN', 'CU,CU', 'FE,FE']

        # additional donor: those with positive charge and vacancy, e.g., cations.
        # additional acceptor : those with negative charge and lone pair electron, e.g. the flanking N of azide
        # with metal donor, the bond_cutoff shall be reduced to e.g. 1.8 ~ 2.5 (lewis conjugate without H)

        dmin, dmax = bond_cutoff
        r = residues[0]  # target residue
        donor_atoms0 = [x for x in r if (x.id.startswith('N') or
                                         '{},{}'.format(r.resname, x.id) in donor_and_acceptor + donor_only) and
                        '{},{}'.format(r.resname, x.id) not in acceptor_only]
        if printout == True:
            print('donor_atom0', donor_atoms0)

        accep_atoms0 = [x for x in r if (x.id.startswith('O') or
                                         '{},{}'.format(r.resname, x.id) in donor_and_acceptor + acceptor_only) and
                        '{},{}'.format(r.resname, x.id) not in donor_only]
        if printout == True:
            print('accep_atom0', accep_atoms0)

        if confine_target_atom != []:
            donor_atoms0 = [x for x in donor_atoms0 if x.id in confine_target_atom]
            accep_atoms0 = [x for x in accep_atoms0 if x.id in confine_target_atom]

        # print('donor_atoms0', ['{},{}'.format(r.resname, x.id) for x in donor_atoms0])
        # print('accep_atoms0', ['{},{}'.format(r.resname, x.id) for x in accep_atoms0])

        donor_atoms1 = []
        accep_atoms1 = []
        for j in range(1, len(residues)):
            r = residues[j]
            donor = [x for x in r if (x.id.startswith('N') or
                                      '{},{}'.format(r.resname, x.id) in donor_and_acceptor + donor_only) and
                     '{},{}'.format(r.resname, x.id) not in acceptor_only]

            accep = [x for x in r if (x.id.startswith('O') or
                                      '{},{}'.format(r.resname, x.id) in donor_and_acceptor + acceptor_only) and
                     '{},{}'.format(r.resname, x.id) not in donor_only]

            # donor_atom1 = donor_atom1 + donor
            donor_atoms1 += donor
            accep_atoms1 += accep

        atom_pair = []
        for x in donor_atoms0:
            for y in accep_atoms1:
                dist = x - y
                if dist >= dmin and dist <= dmax:
                    atom_pair.append([x, y])

        for x in accep_atoms0:
            for y in donor_atoms1:
                dist = x - y
                if dist >= dmin and dist <= dmax:
                    atom_pair.append([x, y])

        atom_pair1 = []
        for (x, y) in atom_pair:
            if consider_resi == True and x.full_id[2] == y.full_id[2]:
                if not ((y.parent.id[1] - x.parent.id[1] == 1 and x.id + y.id == 'ON') or
                        (x.parent.id[1] - y.parent.id[1] == 1 and y.id + x.id == 'ON') or
                        (x.parent.id[1] - y.parent.id[1] == 0)):
                    atom_pair1.append((x, y))
            else:
                atom_pair1.append((x, y))

        h = []
        for (x, y) in atom_pair1:
            distance = round(x - y, 2)
            if 'CB' in [o.id for o in y.parent] and 'CA' in [o.id for o in y.parent]:
                CB = y.parent['CB']
                CA = y.parent['CA']
                vector1 = x.get_vector()
                vector2 = CB.get_vector()
                vector3 = CA.get_vector()
                dist_CB = round(x - CB, 2)
                angle_CB = int(calc_angle(vector1, vector2, vector3) * 180 / np.pi)

            else:
                dist_CB = np.nan
                angle_CB = np.nan

            if x.parent.resname in aa3_1.keys() and y.parent.resname in aa3_1.keys():
                if len(x.id) == 1 and len(y.id) == 1:
                    note1 = 'bo-bo'
                elif len(x.id) == 1 and len(y.id) > 1:
                    note1 = 'bo-si'
                elif len(x.id) > 1 and len(y.id) == 1:
                    note1 = 'si-bo'
                elif len(x.id) > 1 and len(y.id) > 1:
                    note1 = 'si-si'
            else:
                note1 = ''

            h.append([x.full_id[0], x.full_id[2], x.parent.resname, x.parent.id[1], x.id, x.full_id,
                      y.full_id[0], y.full_id[2], y.parent.resname, y.parent.id[1], y.id, y.full_id,
                      distance, dist_CB, angle_CB, note, note1])

        h_df = pd.DataFrame(h, columns=[
            'x_struc', 'x_chain', 'x_resn', 'x_resi', 'x_atom', 'x_full_id',
            'y_struc', 'y_chain', 'y_resn', 'y_resi', 'y_atom', 'y_full_id',
            'distance', 'dist_CB', 'angle_CB', 'note', 'note1'])
        # print(h)
        return h_df, h, atom_pair1

    def C_interaction_detector(residues, note='', bond_cutoff=[3, 4.5], minimum_delta_resi=2, minimum_bond=2):
        ''' Output format same as Lewis_conjugate_detector
            consider side chain C only, consider residues whose resi - resi >1
            '''

        # donor_and_acceptor += ['SER,OG', 'THR,OG1', 'TYR,OH', 'HIS,ND1', 'HIS,NE2', 'CYS,SG']

        dmin, dmax = bond_cutoff

        r0 = residues[0]
        atoms0 = [x for x in r0 if x.id.startswith('C') and x.id not in ['C', 'CA']]

        atom_pair1 = []
        for r in residues[1:]:

            if not (r0.full_id[2] == r.full_id[2] and abs(r0.id[1] - r.id[1]) < minimum_delta_resi):
                atom_pair = []
                atoms1 = [x for x in r if x.id.startswith('C') and x.id not in ['C', 'CA']]
                for x in atoms0:
                    for y in atoms1:
                        dist = x - y
                        if dist >= dmin and dist <= dmax:
                            atom_pair.append([x, y])
                if len(atom_pair) >= minimum_bond:
                    atom_pair1 += atom_pair

        h = []
        for (x, y) in atom_pair1:
            distance = round(x - y, 2)
            if 'CB' in [o.id for o in y.parent] and 'CA' in [o.id for o in y.parent]:
                CB = y.parent['CB']
                CA = y.parent['CA']
                vector1 = x.get_vector()
                vector2 = CB.get_vector()
                vector3 = CA.get_vector()
                dist_CB = round(x - CB, 2)
                angle_CB = int(calc_angle(vector1, vector2, vector3) * 180 / np.pi)

            else:
                dist_CB = np.nan
                angle_CB = np.nan

            note1 = 'C-C'

            h.append([x.full_id[0], x.full_id[2], x.parent.resname, x.parent.id[1], x.id, x.full_id,
                      y.full_id[0], y.full_id[2], y.parent.resname, y.parent.id[1], y.id, y.full_id,
                      distance, dist_CB, angle_CB, note, note1])

        h_df = pd.DataFrame(h, columns=[
            'x_struc', 'x_chain', 'x_resn', 'x_resi', 'x_atom', 'x_full_id',
            'y_struc', 'y_chain', 'y_resn', 'y_resi', 'y_atom', 'y_full_id',
            'distance', 'dist_CB', 'angle_CB', 'note', 'note1'])
        # print(h)
        return h_df, h, atom_pair1

    def disulfide_bond_detector(residues, note='', bond_cutoff=[1.8, 2.3], minimum_delta_resi=2):
        ''' Output format same as Lewis_conjugate_detector
            consider side chain C only, consider residues whose resi - resi >1
            '''

        # donor_and_acceptor += ['SER,OG', 'THR,OG1', 'TYR,OH', 'HIS,ND1', 'HIS,NE2', 'CYS,SG']

        dmin, dmax = bond_cutoff

        r0 = residues[0]
        atoms0 = [x for x in r0 if x.id == 'SG']

        atom_pair1 = []
        for r in residues[1:]:

            if not (r0.full_id[2] == r.full_id[2] and abs(r0.id[1] - r.id[1]) < minimum_delta_resi):
                atom_pair = []
                atoms1 = [x for x in r if x.id == 'SG']
                for x in atoms0:
                    for y in atoms1:
                        dist = x - y
                        if dist >= dmin and dist <= dmax:
                            atom_pair.append([x, y])
                if len(atom_pair) >= 1:
                    atom_pair1 += atom_pair

        h = []
        for (x, y) in atom_pair1:
            distance = round(x - y, 2)
            if 'CB' in [o.id for o in y.parent] and 'CA' in [o.id for o in y.parent]:
                CB = y.parent['CB']
                CA = y.parent['CA']
                vector1 = x.get_vector()
                vector2 = CB.get_vector()
                vector3 = CA.get_vector()
                dist_CB = round(x - CB, 2)
                angle_CB = int(calc_angle(vector1, vector2, vector3) * 180 / np.pi)

            else:
                dist_CB = np.nan
                angle_CB = np.nan

            note1 = 'disulfide'

            h.append([x.full_id[0], x.full_id[2], x.parent.resname, x.parent.id[1], x.id, x.full_id,
                      y.full_id[0], y.full_id[2], y.parent.resname, y.parent.id[1], y.id, y.full_id,
                      distance, dist_CB, angle_CB, note, note1])

        h_df = pd.DataFrame(h, columns=[
            'x_struc', 'x_chain', 'x_resn', 'x_resi', 'x_atom', 'x_full_id',
            'y_struc', 'y_chain', 'y_resn', 'y_resi', 'y_atom', 'y_full_id',
            'distance', 'dist_CB', 'angle_CB', 'note', 'note1'])
        # print(h)
        return h_df, h, atom_pair1

    # Create/search for Bond matrix

    if t.endswith('.cif') or t.endswith('.pdb'):
        pdb_id, extension = t.split('.cif')[0].split('.pdb')[0], t.split('.')[-1]
    else:
        pdb_id, extension = t, 'cif'  # if none specified in extension & t, default cif

    # --------------------------------------------------- making a comprehensive csv list of interactions
    if '{}_bond.csv'.format(pdb_id) not in os.listdir(wd3):

        print('writing bond matrix, please wait')

        s = Fetch_and_parse_cif(t, wd)

        Metal_list = ['H_NA', 'H_K', 'H_MG', 'H_CA', 'H_MN', 'H_NI', 'H_CO', 'H_ZN', 'H_CU', 'H_FE']
        other_entity = list(set([x.id[0] for chain in s[0] for x in chain]))
        other_entity = [x for x in other_entity if x not in Metal_list + [' ', 'W']]

        list_of_s, pml = Fetch_and_view(wd, t, NTP_list=other_entity, print_path=False)
        s, metal, entity_el, dna_p, dna_el = list_of_s[0]
        covered = metal + dna_p + dna_el + entity_el

        # query residues aa and water
        query_residues = [x for y in s[0] for x in y if x not in covered]
        query_residues = [x for x in query_residues if x.parent.id in limit_pp_chains]

        # print('here', [x for x in covered if x in query_residues])

        R0 = covered + query_residues

        # --------------------------------------------------- start all-to-all analysis
        h0 = []
        for i in range(len(R0)):

            rs = R0[i:]
            if rs[0].id[0] in Metal_list:
                h_df, h, atom_pair = Lewis_conjugate_detector2(rs, note='metal bond', bond_cutoff=Metal_bond_cutoff)
            else:
                h_df, h, atom_pair = Lewis_conjugate_detector2(rs, note='H-bond', bond_cutoff=H_bond_cutoff,
                                                               include_metal=False)
                h_df1, h1, atom_pair1 = C_interaction_detector(rs, note='C-C', bond_cutoff=cc_bond_cutoff,
                                                               minimum_bond=minimum_cc_bond)

                h_df2, h2, atom_pair2 = disulfide_bond_detector(rs, note='disulfide', bond_cutoff=ss_bond_cutoff)

                h += h1;
                h += h2
                atom_pair += atom_pair1;
                atom_pair += atom_pair2
            h0 += h

        # print(len(h0))
        # --------------------------------------------------- ake a duplicate with inversed x y
        h0 = pd.DataFrame(h0)
        h1 = h0.iloc[:, [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 12, 13, 14, 15, 16]]  # reorder the columns
        h1 = h1.T.reset_index(drop=True).T
        h0_df = pd.concat([h0, h1],
                          axis=0)  # h0 consist only of resi_small-> resi_large. h1 consist of resi_large -> resi_small
        h0_df.columns = [
            'x_struc', 'x_chain', 'x_resn', 'x_resi', 'x_atom', 'x_full_id',
            'y_struc', 'y_chain', 'y_resn', 'y_resi', 'y_atom', 'y_full_id',
            'distance', 'dist_CB', 'angle_CB', 'note', 'note1']

        h0_df = h0_df.sort_values(by=['x_struc', 'x_chain', 'x_resi'])
        h0_df = h0_df.reset_index(drop=True)
        h0_df['bond_index'] = range(h0_df.shape[0])

        Output_csv(h0_df, '{}/{}_bond'.format(wd3, pdb_id))
        print('{}_bond.csv created'.format(pdb_id))


    else:
        print('{} bond_matrix available'.format(pdb_id))

    return

def Abbr_bond_matrix(df, verbose=False):
    '''df is the bond matrix created by function Bond_matrix()
    create an abbreviation one row per resi-resi pair'''
    if verbose: print('df', df)
    x_chain = list(df['x_chain'])
    x_resi = list(df['x_resi'])
    x_resn = list(df['x_resn'])
    y_chain = list(df['y_chain'])
    y_resi = list(df['y_resi'])
    y_resn = list(df['y_resn'])

    # descript = ['{}_{}_{}_{}_{}_{}'.format(x_chain[i], x_resi[i], x_resn[i], y_chain[i], y_resi[i], y_resn[i]) for i in range(df.shape[0])]

    descript = ['{}|{}|{}|{}|{}|{}'.format(x_chain[i], x_resi[i], x_resn[i], y_chain[i], y_resi[i], y_resn[i]) for i in
                range(df.shape[0])]
    df['descript'] = descript

    a2 = list(set(descript))
    f2 = []
    for d in a2:
        slice = df[df['descript'] == d]

        x_atom = list(slice['x_atom'])
        y_atom = list(slice['y_atom'])
        xy_atom = ['{}~{}'.format(x_atom[i], y_atom[i]) for i in range(slice.shape[0])]
        all_bond = ';'.join(xy_atom)
        # descript = d.split('_')
        f2.append(d.split('|') + [all_bond])

    # print('f2', f2)
    f2 = pd.DataFrame(f2, columns=['x_chain', 'x_resi', 'x_resn', 'y_chain', 'y_resi', 'y_resn', 'all_bond'])
    f2 = f2.sort_values(by=['x_chain', 'x_resi', 'y_chain', 'y_resi'])
    f2 = f2.reset_index(drop=True)

    return f2

def Fetch_and_view(wd, t,
                   sele_head='pdb_id',
                   load_and_end=True, print_path=True,
                   Metal_list=['H_NA', 'H_K', 'H_MG', 'H_CA', 'H_MN', 'H_NI', 'H_CO', 'H_ZN', 'H_CU', 'H_FE'],
                   NTP_list=['H_ATP', 'H_GTP', 'H_DGT', 'H_DG3', 'H_2DA', 'H_DTP', 'H_B9X', 'H_PPV',
                             'H_FFC'], save_pse = False):  # version 251231
    '''
    Generate a pymol script per structure for initial visualization of the pol structure,
    with log_open to track selected residue id
    sele_head is the header of selection used in pml
    return list_of_s, concat_pml'''

    list_of_s = []

    paste = ''
    concat_pml = ''



    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, None, default_extension = 'cif')


    if load_and_end == True:
        pml = Pml_load(pdb_id, wd, extension=extension, color = 'white')
    else:
        pml = ''

    # format header
    if sele_head == 'pdb_id':
        header = pdb_id + '_'
    else:
        header = sele_head

    # Find potential catalytic metal
    a = []
    for chain in s[0]:
        for resi in chain:
            if resi.id[0] in Metal_list:
                a.append(resi)
    metal = a
    if len(metal) > 0:
        pml += Pml_select_resi(metal, '{}metal'.format(header), 'magenta', show_as='sphere')

    #  Find ntp substrates, especially non-CH atoms
    a = []
    for chain in s[0]:
        for resi in chain:
            if resi.id[0] in NTP_list:
                a.append(resi)
    ntp = a
    if len(ntp) > 0:
        pml += Pml_select_resi(ntp, '{}other_entity'.format(header), 'limon', show_as='sticks')

    dna_p = []
    dna_else = []
    # Find nucleotide DNA residues
    for chain in s[0].child_list:
        dna = [x for x in chain if x.id[0] == ' ' and x.get_resname() not in aa3_1.keys()]
        if len(dna) > 0:

            if chain.id.startswith('P'):
                pml += Pml_select_resi(dna, '{}dna_{}'.format(header, chain.id), 'by element white', show_as='sticks')
                dna_p += dna
            else:
                pml += Pml_select_resi(dna, '{}dna_{}'.format(header, chain.id), 'by element white', show_as='sticks')
                dna_else += dna

    list_of_s.append([s, metal, ntp, dna_p, dna_else])
    concat_pml += pml

    if load_and_end == True:
        paste += Pml_end(pml, pdb_id, wd, print_path=print_path, save_pse = save_pse)

    return list_of_s, concat_pml

def Shell_analyses(wd, t, target_chain, target_resi, coi = [],
                   shell=1, analyze_potential=False,
                   potential_cutoff=5,
                   limit_pp_chains=['A', 'B', 'C', 'D'],
                   dismiss_backbone_H_bond=False, dismiss_backbone_H_bond2=False,
                         output_csv =False, output_txt = True,
                   show_combine = True, combine_categories=['shell1', 'potent1', 'shell2'], neighbor_expand=2
                   ):  # version 260101

    def process_shell_analysis_result(df, filename):
        ''' remove non-amino acid shell'''


        rs = {'t0_target_residue': [],
              't0_shell1_residue': []}

        data = {}
        for index, row in df.iterrows():
            namex = '{}_{}_{}'.format(row['x_chain'], row['x_resi'], row['x_resn'])
            if namex not in data.keys():
                data.update({namex: {}})
            namey = '{}_{}_{}'.format(row['y_chain'], row['y_resi'], row['y_resn'])
            data[namex].update({namey: row['all_bond']})

        data = {}
        for index, row in df.iterrows():
            if row['x_resn'] in aa3_1.keys():
                namex = '{} {}'.format(aa3_1[row['x_resn']], row['x_resi'])
                rs['t0_target_residue'].append(row['x_resi'])
            else:
                namex = '{}_{}_{}'.format(row['x_chain'], row['x_resi'], row['x_resn'])

            if namex not in data.keys():
                data.update({namex: {}})

            if row['y_resn'] in aa3_1.keys():
                namey = '{} {}'.format(aa3_1[row['y_resn']], row['y_resi'])
                data[namex].update({namey: row['all_bond']})
                rs['t0_shell1_residue'].append(row['y_resi'])

        rs['t0_target_residue'] = sorted(list(set(rs['t0_target_residue'])))
        rs['t0_shell1_residue'] = sorted(list(set(rs['t0_shell1_residue'])))

        data1 = data

        m = False
        writer = '{} {}'.format('=' * 64, filename.split('_')[0])
        for key, value in data1.items():
            writer += '\n{}'.format(key)

            for k2, v2 in value.items():
                writer += '\n\t\t{}\t{}'.format(k2, v2)

        Output_text(writer, filename.split('.')[0])
        return writer, rs


    def Combine_amino_acid_neighbors(D, categories=['target', 'shell1', 'potent1', 'shell2'], expand=2, verbose=False,
                          is_aa=True):  # take Analyze_pol_8b output as input
        ''' outputL: neighbor listed in categories, expanded neighbor, expanded neighbor re-expressed in list of ranges'''

        neighbor = []

        t2 = f'\n{"." * 64} Combine_amino_acid_neighbors\nCategories detected:'
        for key, value in D.items():
            # print(key,value)
            for key2, value2 in value.items():
                if key2 in categories:
                    # print('key2', key2)
                    t2 += f' {key2}'
                    for x in value2:
                        if x.id[0] == ' ':
                            if is_aa:
                                if x.resname in aa3_1.keys():
                                    neighbor.append(x.id[1])
                                    # print(f'\t{x}')
                            else:
                                if x.resname not in aa3_1.keys():
                                    neighbor.append(x.id[1])
                                    # print(f'\t{x}')

        neighbor = sorted(set(neighbor))

        t2 += f'\n\nneighbors matching listed categories (d): {neighbor}'

        neighbor2 = []
        for x in neighbor:
            for j in range(-expand, expand + 1, 1):
                neighbor2.append(x + j)

        neighbor2 = list(set(neighbor2))
        neighbor2.sort()
        t2 += f'\nneighbors expanded by {expand} residues (n): {neighbor2}'

        neighbor3 = group_into_ranges(neighbor2)
        t2 += f'\nneighbors expanded and grouped (N): {neighbor3}'

        if verbose: print(t2)

        return neighbor, neighbor2, neighbor3

    if isinstance(coi, str):
        coi = [coi]

    Bond_matrix(wd, t,
                limit_pp_chains=limit_pp_chains)  # within the def, will navigate to the subfolder input_Bond_matrices



    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, None)

    target_resi = list(set(target_resi))
    target_resi.sort()
    descript = {
        't': t,
        'target_chain': target_chain,
        'target_resi': target_resi,
        'coi': coi,
        'shell': shell,
        'analyze_potential': analyze_potential,
        'potential_cutoff': potential_cutoff
    }



    base_filename = f"{pdb_id}_shell_analyses"

    Metal_list = ['H_NA', 'H_K', 'H_MG', 'H_CA', 'H_MN', 'H_NI', 'H_CO', 'H_ZN', 'H_CU', 'H_FE']
    D = dict()
    paste = ''

    # if verbose: print('start analyze {}'.format(pdb_id))
    other_entity = [x.id[0] for chain in s[0] for x in chain]
    other_entity = list(set(other_entity))
    other_entity = [x for x in other_entity if x not in Metal_list + [' ', 'W']]

    list_of_s, pml = Fetch_and_view(wd, t, NTP_list=other_entity, print_path=False)
    s, metal, entity_el, dna_p, dna_el = list_of_s[0]

    target = [Biopython_residue(s, 0, target_chain, i) for i in target_resi]
    pml += Pml_select_resi(target, 'target', show='stick', color='by element yellow')

    keys = ['s', 'dna_P', 'dna_else', 'other_entity', 'metal', 'target']
    values = [s, dna_p, dna_el, entity_el, metal, target]

    d = dict(zip(keys, values))

    # --------------------------------------------------- start shell1 analysis
    f = pd.read_csv('{}/input_Bond_matrices/{}_bond.csv'.format(wd, pdb_id), header=0)
    Examined = []
    target0 = target

    f1s = []
    for reiterate in range(shell):
        # find the next shell
        # if verbose: print("analyse shell {}".format(reiterate + 1))

        f1 = pd.DataFrame()
        target = [x for x in target if x is not None]
        for r in target:

            slice = f[f['x_chain'] == r.parent.id]
            slice = slice[slice['x_resi'] == r.id[1]]

            if coi:
                slice = slice[slice['y_chain'].isin(coi)]

            if dismiss_backbone_H_bond == True:
                slice = slice[slice['note1'] != 'bo-bo']

            if slice.shape[0] != 0:
                f1 = pd.concat([f1, slice])

        t = []
        t_new = []

        if f1.shape[0] > 0:
            chains = list(set(f1['y_chain']))
            for c in chains:
                slice = f1[f1['y_chain'] == c]
                t += [Biopython_residue(s, 0, c, resi) for resi in list(slice['y_resi'])]

            t_new = [x for x in t if x not in target + Examined]
            t_new = list(set(t_new))
            d['shell{}'.format(reiterate + 1)] = t_new
            if reiterate + 1 == 1:
                pml += Pml_select_resi(t_new, 'shell{}'.format(reiterate + 1), show='stick',
                                       color='by element green')
            elif reiterate + 1 == 2:
                pml += Pml_select_resi(t_new, 'shell{}'.format(reiterate + 1), show='stick',
                                       color='by element cyan')
            else:
                pml += Pml_select_resi(t_new, 'shell{}'.format(reiterate + 1), show='stick',
                                       color='by element white')

            f1s.append(f1)

            # Output shell analysis result
            a, b = Abbr_bond_matrix(f1), f'{base_filename}_sh{reiterate + 1}'
            if output_csv == True:
                Output_csv(f1, f'{b}_full')
                Output_csv(a, b)
            if output_txt:
                process_shell_analysis_result(a, b)

        if analyze_potential == True:  # from 6b
            # find potential H-bonding partner (i.e., residues whose CB is within e.g. 8 A)
            t = []
            h = []
            pp = [x for y in s[0] for x in y if x.resname in aa3_1.keys()]

            if coi: pp = [x for x in pp if x.parent.id in coi]

            for residue in target:
                for atom in residue:
                    if atom.id[0] in ['N', 'O', 'S', 'C', 'P', 'M']:
                        for x in pp:
                            for atom2 in x.get_atoms():
                                dist = atom - atom2
                                # if dist <= potential_cutoff and x != residue:
                                if (dist <= potential_cutoff) and (x != residue) and (x not in t):
                                    t.append(x)
                                    h.append([residue.parent.id, residue.id[1], residue.resname, atom.id,
                                              x.parent.id, x.id[1], x.resname, atom2.id, dist])

            potential = [x for x in t if x not in Examined + target + t_new]
            d['potent{}'.format(reiterate + 1)] = potential

            if reiterate + 1 == 1:
                pml += Pml_select_resi(potential, 'potent{}'.format(reiterate + 1), show='stick',
                                       color='by element cyan')
            else:
                pml += Pml_select_resi(potential, 'potent{}'.format(reiterate + 1))

            f1 = pd.DataFrame(h,
                              columns=['x_chain', 'x_resi', 'x_resn', 'x_atom', 'y_chain', 'y_resi', 'y_resn', 'y_atom',
                                       'dist'])

            # Output shell analysis result
            b = f'{base_filename}_pt{reiterate + 1}'
            if output_csv== True:
                Output_csv(f1, f'{b}_full')
                Output_csv(Abbr_bond_matrix(f1), b)

        Examined += target
        target = t_new

    for f1 in f1s:
        d1 = DFdict(f1)
        for i in range(f1.shape[0]):
            idx = '{}//{}/{}/{}'.format(pdb_id, d1['x_chain'][i], d1['x_resi'][i], d1['x_atom'][i])
            idy = '{}//{}/{}/{}'.format(pdb_id, d1['y_chain'][i], d1['y_resi'][i], d1['y_atom'][i])

            pml += 'distance meas{}, {}, {}\n'.format(d1['bond_index'][i], idx, idy)

    D[pdb_id] = d
    paste = Pml_end(pml, base_filename, wd, print_path=False, orient='target')
    # paste += t2


    text = f'\n{"." * 64} {base_filename}\n'

    text += '{}'.format(str_dict(descript))
    print(text)

    t2 = ''
    for key, value in D.items():
        for key2, value2 in value.items():
            if key2.startswith('shell') or key2.startswith('potent'):
                # print('key2', key2)
                t2 += f'\n{key2}: '
                chains_involved = sorted(set([x.parent.id for x in value2]))
                for c in chains_involved:
                    sub_resi = sorted(set([x.id[1] for x in value2 if x.parent.id == c]))
                    t2 += f'\n\tchain {c} {sub_resi}'
    print(t2)

    d, n, N = Combine_amino_acid_neighbors(D, categories=combine_categories, expand=neighbor_expand, verbose=show_combine)

    print(f'\n{"."*64} Paste the following line in PYMOL command prompt\n{paste}')

    return D, d, n, N

def Detect_disulfide_and_cysteine(wd, t, limit_pp_chains=['A', 'B', 'C', 'D'], verbose=True):


    s, pdb_id, extension, pdb_id2, extension2, io2 = handle_input_and_output_structure(t, None)

    Bond_matrix(wd, t,
                limit_pp_chains=limit_pp_chains)  # within the def, will navigate to the subfolder input_Bond_matrices

    # detect cysteine
    all_res = [x for chain in s[0] for x in chain]
    resi0 = [x.id[1] for x in all_res if x.resname == 'CYS']
    resi0 = sorted(set(resi0))

    if len(resi0) > 0:
        if verbose: print(f'{"." * 64} Detect_disulfide_and_cysteine\nCys detected: {resi0},')

    else:
        if verbose: print(f'{"." * 40} Detect_disulfide_and_cysteine\nCys undetected')
        return

    # detect disulfide
    df = pd.read_csv('{}/input_Bond_matrices/{}_bond.csv'.format(wd, pdb_id), header=0)
    df_disulfide = df[df["note"] == "disulfide"]
    result = df_disulfide[["x_resi", "y_resi"]]

    resi1 = []
    # print(result)
    if result.shape[0] > 0:
        descrip = []

        for idx, row in result.iterrows():
            r1, r2 = int(row['x_resi']), int(row['y_resi'])
            if r1 > r2:
                continue
            else:
                if f'Cys {r1} ~ Cys {r2}' not in descrip:
                    descrip.append(f'Cys {r1} ~ Cys {r2}')
                    resi1 += [r1, r2]

    resi2 = [x for x in resi0 if x not in resi1]

    if verbose: print(f'among which Cys {resi1} form dissulfide bond, & Cys {resi2} remain cysteine.')

    if verbose and (result.shape[0] > 0):
        print(f'\n{len(descrip)} disulfide bond(s) detected:')
        for x in descrip:
            print(f'\t{x}')

    return resi1, resi2  # cystine, cysteine

#  Make chimera
# def make_chimera_copy(t0, t1, t0_align=(), t1_align=(), t0_sele=([], []), t1_sele=([], []), aln_atomID='',
#                  new_filename='chimera.pdb'):
#     # wd = None
#     # extension = extension.replace('.', '').replace(' ', '')
#     # t0 = t0.split('.')[0]
#     # t1 = t1.split('.')[0]
#     # if new_filename is not None: new_filename = new_filename.split('.')[0]
#
#     def Select_by_tuple_format(s, a):
#         # print('select', s, a)
#         '''
#         for the format ([],[]) or tuple of the format
#         for example
#         t0_align = (['A'], [141,143,210,214,259])
#
#         t1_align = (['A', 'A', 'A', 'A', 'A'],[18,20,125,129,154])
#
#         t0_sele = ([], [])          # all residues of all chains
#
#         t1_sele = ((['C'], []),
#                 (['A'], [301,304]))    # all residues of chain 'C'; residue 301, 304 or chain 'A'
#
#         s is a biopython structure
#         '''
#
#         if not isinstance(a[0], tuple):  # A single format
#             a = tuple([a])
#
#         R = []
#         for (c, r) in a:
#             if c == [] and r == []:
#                 R += [x for chain in s[0] for x in chain]
#
#             elif c != [] and r == []:
#                 chains = [chain for chain in s[0] if chain.id in c]
#                 for chain in chains:
#                     R += [x for x in chain]
#
#             elif c != [] and r != []:
#                 if len(c) != len(r):
#                     c1 = repeat(c[0], len(r))
#                 else:
#                     c1 = c
#                 for i in range(len(r)):
#                     rr = Biopython_residue(s, 0, c1[i], r[i])
#                     if not rr is None:
#                         R.append(rr)
#
#         return R
#
#     def reformat_residues(r):
#         '''
#         r is a list of residues,
#         return a dataframe with column names 'chain', 'resi', 'resn'
#         '''
#
#         a = []
#         for x in r:
#             a.append([x.parent.id, x.id[1], x.resname])
#         a = pd.DataFrame(a, columns=['chain', 'resi', 'resn'])
#
#         return a
#
#
#     wd = os.getcwd()
#
#     s1, pdb_id1, extension1, pdb_id2, extension2, io2  = handle_input_and_output_structure(t1, new_filename)
#     s0, pdb_id0, extension0, pdb_id3, extension3, io3  = handle_input_and_output_structure(t0, f'{pdb_id1}_aln.{extension2}')
#
#     sele0 = Select_by_tuple_format(s0, t0_sele)
#     sele1 = Select_by_tuple_format(s1, t1_sele)
#
#     descript2 = {'new_filename': f'{pdb_id2}.{extension2}'}
#
#     if len(t0_align) == 0:
#         # filename1 = pdb_id1
#
#         descript = {
#             'aln_atomID': None,
#             't0': t0,
#             't0_align': None,
#             't0_sele': t0_sele,
#             't1': t1,
#             't1_align': None,
#             't1_sele': t1_sele
#         }
#
#
#     else:
#         filename3 = f'{pdb_id3}.{extension3}'
#         descript2.update({'new_aligned_file': filename3})
#
#         descript = {
#             'aln_atomID': aln_atomID,
#             't0': t0,
#             't0_align': t0_align,
#             't0_sele': t0_sele,
#             't1': t1,
#             't1_align': t1_align,
#             't1_sele': t1_sele
#         }
#
#         dna_aln = ["C1'", "C2'", "C3'", "C4'", "O4'"] # the ribose ring
#         aa_aln = ["N", "CA", "C"]   # the backbone
#
#         if not isinstance(aln_atomID, list):
#             if aln_atomID.startswith('dna'):
#                 aln_atomID = dna_aln
#             else:
#                 aln_atomID = aa_aln
#
#         aln0 = Select_by_tuple_format(s0, t0_align)
#         aln1 = Select_by_tuple_format(s1, t1_align)
#
#         # Align the two cif
#         fix = []
#         move = []
#         if len(aln0) != len(aln1):
#             print('non-equal alignment residue number')
#         else:
#             for i in range(len(aln0)):
#                 r0 = aln0[i]
#                 r1 = aln1[i]
#                 atomID = [x for x in aln_atomID if x in [a.id for a in r0] and x in [a.id for a in r1]]
#                 # print(atomID)
#                 fix += [r0[atom] for atom in atomID]
#                 move += [r1[atom] for atom in atomID]
#
#         sup = Superimposer()
#         sup.set_atoms(fix, move)
#         sup.apply([x for x in s1.get_atoms()])
#
#         # Set and output structure
#         s1.id = pdb_id3
#         io3.set_structure(s1)
#         io3.save(f"{pdb_id3}.{extension3}")
#
#
#     #  combine the selected region, extend chainID with pdbID as suffix.
#
#     df0 = reformat_residues(sele0)
#     d0 = DFdict(df0)
#     df1 = reformat_residues(sele1)
#     d1 = DFdict(df1)
#
#     S = s0.copy()
#     S.id = pdb_id2
#
#     for model in s0:
#         if model.id != 0:
#             S.detach_child(model.id)
#
#     s0_new_chain_identifiers = []
#
#     the26 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
#     c_index = 0
#     text = ''
#
#     for chain in s0[0]:
#         chainID = chain.id
#         if chainID not in d0['chain']:
#             S[0].detach_child(chainID)
#         else:
#             slice = df0[df0['chain'] == chainID]
#             d = DFdict(slice)
#             for residue in chain:
#                 if residue.id[1] not in d['resi']:
#                     S[0][chainID].detach_child(residue.id)
#
#             x1 = str(c_index)
#             x = the26[c_index]
#             S[0][chainID].id = x1
#             text += '{} chain {} is renamed as {} chain {}\n'.format(pdb_id0, chainID, pdb_id2, x)
#             c_index += 1
#
#             s0_new_chain_identifiers.append(x)
#
#     for chain in s1[0]:
#         chainID = chain.id
#         if chainID in d1['chain']:
#             chain.detach_parent()
#             S[0].add(chain)
#
#             slice = df1[df1['chain'] == chainID]
#             d = DFdict(slice)
#             dresi = d['resi']
#
#             chain = list(chain)
#             chain.reverse()
#
#             for residue in chain:
#                 if residue.id[1] not in dresi:
#                     S[0][chainID].detach_child(residue.id)
#
#             x1 = str(c_index)
#             x = the26[c_index]
#             S[0][chainID].id = x1
#             text += '{} chain {} is renamed as {} chain {}\n'.format(pdb_id1, chainID, pdb_id2, x)
#             c_index += 1
#
#     for i in range(c_index):
#         S[0][str(i)].id = the26[i]
#
#
#
#     # Set and output structure
#     S.id = pdb_id2
#     io2.set_structure(S)
#     io2.save(f"{pdb_id2}.{extension2}")
#
#     # Write PML
#     r0 = []
#     pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
#     for chain in S[0]:
#         if chain.id in s0_new_chain_identifiers:
#             pml += Pml_select_resi([r for r in chain], chain.id, color='by element cyan')
#         else:
#             pml += Pml_select_resi([r for r in chain], chain.id, color='by element white')
#
#     if r0 != []:
#         pml += Pml_select_resi(r0, 't0_ind', show='sticks', color='by element green')
#         pml += Pml_select_resi(r1, 't1_ind', show='sticks', color='by element orange')
#
#
#     a = Pml_end(pml, f"{pdb_id2}.{extension2}", wd, print_path = False, save_pse = True)
#
#     text = f'\n{"." * 64} {pdb_id2}.{extension2}\n' + text + '\n'
#     text += '{}\n'.format(str_dict(descript))
#     text += '\n{}\n'.format(str_dict(descript2))
#     print(text)
#
#     print(f'\n{"." * 64} Paste the following line in the pymol command prompt:\n{a}')
#
#
#     return S

def Select_residue_by_string(s, a):
    '''
    s is a Biopython structure,
    a is a string specifying the chain & resi, e.g.
        A:      A chain all residues
        P2:     P chain resi 2
        B1~23:  B chain resi 1~23

        these can be joined by either space or comma, forming a =  "A P2 B1~23"
        if one wish to retain all chains & all resi, set a = "all"
        if a is None, return None
    '''

    R = []
    if a is None:
        return

    if a == 'all':
        R += [x for chain in s[0] for x in chain]
        return R

    else:
        a = a.replace(',', ' ').replace('  ', ' ').replace('-', '~').strip()
        a1 = a.split(' ')

        pattern1 = re.compile(r'^([A-Z]+)$')  # pattern1, substitution
        pattern2 = re.compile(r'^([A-Z]+)(\d+)$')  # pattern2, 1-aa deletion
        pattern3 = re.compile(r'^([A-Z]+)(\d+)~(\d+)$')  # pattern3 & 5, insertions

        for x in a1:
            if pattern1.fullmatch(x):
                m = pattern1.fullmatch(x)
                cid,*_ = m.groups()
                R += [x for x in s[0][cid]]

            elif pattern2.fullmatch(x):
                m = pattern2.fullmatch(x)
                cid, rid = m.groups()
                rid = int(rid)
                R.append( Biopython_residue(s, 0, cid, rid) )

            elif pattern3.fullmatch(x):
                m = pattern3.fullmatch(x)
                cid, start, end = m.groups()
                start = int(start)
                end = int(end)
                end +=1
                R += [x for x in s[0][cid] if x.id[1] in range(start, end )]
            else:
                print(f'Error decoding {x}')
                return
        return R



def make_chimera(t0, t1, t0_sele='all', t1_sele='all', t0_align=None, t1_align=None,
                 aln_atomID=["N", "CA", "C", "C1'", "C2'", "C3'", "C4'", "O4'"],
                 new_filename='chimera.pdb'):

    wd = os.getcwd()

    s1, pdb_id1, extension1, pdb_id2, extension2, io2  = handle_input_and_output_structure(t1, new_filename)
    s0, pdb_id0, extension0, pdb_id3, extension3, io3  = handle_input_and_output_structure(t0, f'{pdb_id1}_aln.{extension2}')

    sele0 = Select_residue_by_string(s0, t0_sele)
    sele1 = Select_residue_by_string(s1, t1_sele)

    descript2 = {'new_filename': f'{pdb_id2}.{extension2}'}

    if (t0_align is None) or (t1_align is None):
        t0_align = None
        t1_align = None

        descript = {
            't0': t0,
            't0_align': t0_align,
            't0_sele': t0_sele,
            't1': t1,
            't1_align': t1_align,
            't1_sele': t1_sele
        }

    else:
        filename3 = f'{pdb_id3}.{extension3}'
        descript2.update({'new_aligned_file': filename3})

        descript = {
            't0': t0,
            't0_align': t0_align,
            't0_sele': t0_sele,
            't1': t1,
            't1_align': t1_align,
            't1_sele': t1_sele
        }

        # dna_aln = ["C1'", "C2'", "C3'", "C4'", "O4'"] # the ribose ring
        # aa_aln = ["N", "CA", "C"]   # the backbone
        #
        # if not isinstance(aln_atomID, list):
        #     if aln_atomID.startswith('dna'):
        #         aln_atomID = dna_aln
        #     else:
        #         aln_atomID = aa_aln

        aln0 = Select_residue_by_string(s0, t0_align)
        aln1 = Select_residue_by_string(s1, t1_align)

        # Align the two cif
        fix = []
        move = []
        if len(aln0) != len(aln1):
            print('non-equal alignment residue number')
        else:
            for i in range(len(aln0)):
                r0 = aln0[i]
                r1 = aln1[i]
                atomID = [x for x in aln_atomID if x in [a.id for a in r0] and x in [a.id for a in r1]]
                # print(atomID)
                fix += [r0[atom] for atom in atomID]
                move += [r1[atom] for atom in atomID]

        sup = Superimposer()
        sup.set_atoms(fix, move)
        sup.apply([x for x in s1.get_atoms()])

        # Set and output structure
        s1.id = pdb_id3
        io3.set_structure(s1)
        io3.save(f"{pdb_id3}.{extension3}")


    #  combine the selected region, extend chainID with pdbID as suffix.

    df0 = reformat_residues(sele0)
    d0 = DFdict(df0)
    df1 = reformat_residues(sele1)
    d1 = DFdict(df1)

    S = s0.copy()
    S.id = pdb_id2

    for model in s0:
        if model.id != 0:
            S.detach_child(model.id)

    s0_new_chain_identifiers = []

    the26 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    c_index = 0
    text = ''

    for chain in s0[0]:
        chainID = chain.id
        if chainID not in d0['chain']:
            S[0].detach_child(chainID)
        else:
            slice = df0[df0['chain'] == chainID]
            d = DFdict(slice)
            for residue in chain:
                if residue.id[1] not in d['resi']:
                    S[0][chainID].detach_child(residue.id)

            x1 = str(c_index)
            x = the26[c_index]
            S[0][chainID].id = x1
            text += '{} chain {} is renamed as {} chain {}\n'.format(pdb_id0, chainID, pdb_id2, x)
            c_index += 1

            s0_new_chain_identifiers.append(x)

    for chain in s1[0]:
        chainID = chain.id
        if chainID in d1['chain']:
            chain.detach_parent()
            S[0].add(chain)

            slice = df1[df1['chain'] == chainID]
            d = DFdict(slice)
            dresi = d['resi']

            chain = list(chain)
            chain.reverse()

            for residue in chain:
                if residue.id[1] not in dresi:
                    S[0][chainID].detach_child(residue.id)

            x1 = str(c_index)
            x = the26[c_index]
            S[0][chainID].id = x1
            text += '{} chain {} is renamed as {} chain {}\n'.format(pdb_id1, chainID, pdb_id2, x)
            c_index += 1

    for i in range(c_index):
        S[0][str(i)].id = the26[i]



    # Set and output structure
    S.id = pdb_id2
    io2.set_structure(S)
    io2.save(f"{pdb_id2}.{extension2}")

    # Write PML
    r0 = []
    pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
    for chain in S[0]:
        if chain.id in s0_new_chain_identifiers:
            pml += Pml_select_resi([r for r in chain], chain.id, color='by element cyan')
        else:
            pml += Pml_select_resi([r for r in chain], chain.id, color='by element white')


    if r0 != []:
        pml += Pml_select_resi(r0, 't0_ind', show='sticks', color='by element green')
        pml += Pml_select_resi(r1, 't1_ind', show='sticks', color='by element orange')


    a = Pml_end(pml, f"{pdb_id2}.{extension2}", wd, print_path = False, save_pse = True)

    text = f'\n{"." * 64} {pdb_id2}.{extension2}\n' + text + '\n'
    text += '{}\n'.format(str_dict(descript))
    text += '\n{}\n'.format(str_dict(descript2))
    print(text)

    print(f'\n{"." * 64} Paste the following line in the pymol command prompt:\n{a}')


    return S

def make_chimera_by_atom_aln(t0, t1, t0_atoms, t1_atoms, t0_sele='all', t1_sele='all',
                             new_filename='chimera.pdb'):


    wd = os.getcwd()

    s1, pdb_id1, extension1, pdb_id2, extension2, io2  = handle_input_and_output_structure(t1, new_filename)
    s0, pdb_id0, extension0, pdb_id3, extension3, io3  = handle_input_and_output_structure(t0, f'{pdb_id1}_aln.{extension2}')

    sele0 = Select_residue_by_string(s0, t0_sele)
    sele1 = Select_residue_by_string(s1, t1_sele)

    descript2 = {'new_filename': f'{pdb_id2}.{extension2}'}

    filename3 = f'{pdb_id3}.{extension3}'
    descript2.update({'new_aligned_file': filename3})


    descript = {
        't0': t0,
        't0_atoms': t0_atoms,
        't0_sele': t0_sele,

        't1': t1,
        't1_atoms': t1_atoms,
        't1_sele': t1_sele
    }

    # Align the two cif

    fix = []
    move = []
    if len(t0_atoms) != len(t1_atoms):
        print('non-equal alignment residue number')
    else:
        for i in range(len(t0_atoms)):
            c0, resi0, id0 = t0_atoms[i]
            c1, resi1, id1 = t1_atoms[i]

            atom0 = Biopython_residue(s0, 0, c0, resi0)[id0]
            atom1 = Biopython_residue(s1, 0, c1, resi1)[id1]

            fix.append(atom0)
            move.append(atom1)

    sup = Superimposer()
    sup.set_atoms(fix, move)
    sup.apply([x for x in s1.get_atoms()])


    # Set and output structure
    s1.id = pdb_id3
    io3.set_structure(s1)
    io3.save(f"{pdb_id3}.{extension3}")


    #  combine the selected region, extend chainID with pdbID as suffix.
    df0 = reformat_residues(sele0)
    d0 = DFdict(df0)
    df1 = reformat_residues(sele1)
    d1 = DFdict(df1)

    S = s0.copy()

    S.id = pdb_id2

    for model in s0:
        if model.id != 0:
            S.detach_child(model.id)

    s0_new_chain_identifiers = []

    the26 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    c_index = 0
    text = ''

    for chain in s0[0]:
        chainID = chain.id
        if chainID not in d0['chain']:
            S[0].detach_child(chainID)
        else:
            slice = df0[df0['chain'] == chainID]
            d = DFdict(slice)
            for residue in chain:
                if residue.id[1] not in d['resi']:
                    S[0][chainID].detach_child(residue.id)

            x1 = str(c_index)
            x = the26[c_index]
            S[0][chainID].id = x1
            text += '{} chain {} is renamed as {} chain {}\n'.format(t0, chainID, new_filename, x)
            c_index += 1

            s0_new_chain_identifiers.append(x)

    for chain in s1[0]:
        chainID = chain.id
        if chainID in d1['chain']:
            chain.detach_parent()
            S[0].add(chain)

            slice = df1[df1['chain'] == chainID]
            d = DFdict(slice)
            dresi = d['resi']

            chain = list(chain)
            chain.reverse()

            for residue in chain:
                if residue.id[1] not in dresi:
                    S[0][chainID].detach_child(residue.id)

            x1 = str(c_index)
            x = the26[c_index]
            S[0][chainID].id = x1
            text += '{} chain {} is renamed as {} chain {}\n'.format(t1, chainID, new_filename, x)
            c_index += 1

    for i in range(c_index):
        S[0][str(i)].id = the26[i]



    # Set and output structure
    S.id = pdb_id2
    io2.set_structure(S)
    io2.save(f"{pdb_id2}.{extension2}")

    # Write PML
    r0 = []
    pml = Pml_load(f"{pdb_id2}.{extension2}", wd)
    for chain in S[0]:
        if chain.id in s0_new_chain_identifiers:
            pml += Pml_select_resi([r for r in chain], chain.id, color='by element cyan')
        else:
            pml += Pml_select_resi([r for r in chain], chain.id, color='by element white')

    if r0 != []:
        pml += Pml_select_resi(r0, 't0_ind', show='sticks', color='by element green')
        pml += Pml_select_resi(r1, 't1_ind', show='sticks', color='by element orange')


    a = Pml_end(pml, f"{pdb_id2}.{extension2}", wd, print_path = False, save_pse = True)

    text = f'\n{"." * 64} {pdb_id2}.{extension2}\n' + text + '\n'
    text += '{}\n'.format(str_dict(descript))
    text += '\n{}\n'.format(str_dict(descript2))
    print(text)

    print(f'\n{"." * 64} Paste the following line in the pymol command prompt:\n{a}')

    return S


# if __name__ == '__main__':

    # # { ........................................ transfer atoms from residue y to residue x
    # """ Only work when chain_resi_to do not contain the atom_names specifiedf """
    # filename1= 'temp'
    # StructureHH.transplant_atoms_btw_residues(input_id =  filename1,
    #                                           chain_resi_from = ['D', 0],
    #                                           chain_resi_to = ['B', 1],
    #                                           atom_names = ['CN', 'NN1', 'NN2', 'NN3'],
    #                                           new_filename=filename1)
    # # }
    #
    #
    # # { ........................................ rotate_atoms along an axis
    # """
    # Rotate certain atoms (atomsid_to_rotate) along an axis pointing from atomA to atomB (atomAid, atomBid)
    # """
    # filename1 = 'temp'
    # StructureHH.rotate_atoms(input_id =  filename1,
    #                          chain = 'L',
    #                          resi = 1,
    #                          atomAid = "CN",
    #                          atomBid = "NN1",
    #                          atomsid_to_rotate = ["NN2", "NN3"],
    #                          angle_deg=120,
    #                          new_filename=filename1)
    # # }
