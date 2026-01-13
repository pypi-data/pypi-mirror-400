#!/usr/bin/env python3
# Copyright (C) 2025 Otter Brown
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 only.

import numpy as np
import pandas as pd
import math
import os
import scipy.optimize as opt
import matplotlib.pyplot as plt
import re
import json
import primer3
from time import perf_counter
import sys
import itertools

# preloaded dictionary
IUPC_code_to_bases = {'A': 'A', 'T': 'T', 'C': 'C', 'G': 'G', 'M': 'AC', 'R': 'AG', 'W': 'AT', 'S': 'GC', 'Y': 'CT',
                      'K': 'GT', 'V': 'AGC', 'H': 'ACT', 'D': 'AGT', 'B': 'GCT', 'N': 'AGCT'}
IUPC_bases_to_code = {'A': 'A', 'T': 'T', 'C': 'C', 'G': 'G', 'AC': 'M', 'AG': 'R', 'AT': 'W', 'GC': 'S', 'CT': 'Y',
                      'GT': 'K', 'AGC': 'V', 'ACT': 'H', 'AGT': 'D', 'GCT': 'B', 'AGCT': 'N'}
iupac_df = pd.DataFrame({
    'IUPAC Code': ['A', 'C', 'G', 'T', 'M', 'R', 'W', 'S', 'Y', 'K', 'V', 'H', 'D', 'B', 'N'],
    'Meaning': ['A', 'C', 'G', 'T', 'AC', 'AG', 'AT', 'CG', 'CT', 'GT', 'ACG', 'ACT', 'AGT', 'CGT', 'GATC'],
    'Complement': ['T', 'G', 'C', 'A', 'K', 'Y', 'W', 'S', 'R', 'M', 'B', 'D', 'H', 'V', 'N']
})

aa3_1 = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLU': 'E', 'GLN': 'Q', 'GLY': 'G', 'HIS': 'H',
         'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W',
         'TYR': 'Y', 'VAL': 'V'}
aa1_3 = {'A': 'ALA', 'R': 'ARG', 'N': 'ASN', 'D': 'ASP', 'C': 'CYS', 'E': 'GLU', 'Q': 'GLN', 'G': 'GLY', 'H': 'HIS',
         'I': 'ILE', 'L': 'LEU', 'K': 'LYS', 'M': 'MET', 'F': 'PHE', 'P': 'PRO', 'S': 'SER', 'T': 'THR', 'W': 'TRP',
         'Y': 'TYR', 'V': 'VAL'}

colors_dictionary = {
    "lawngreen": "#b1ff67",
    "yellow": "#ffef86",
    "palegreen": "#b7e6d7",
    "blue": "#e5fcff",
    "pink": "#ff9ccd",
    "purple": "#c7b0e3",
    "grey": "#c6c9d1"
}
empty_gb = '''LOCUS       empty_gb                   0 bp ds-DNA     circular     20-MAY-2024
DEFINITION  synthetic DNA construct
SOURCE      synthetic DNA construct
  ORGANISM  synthetic DNA construct
FEATURES             Location/Qualifiers
ORIGIN

//'''


def reverse_complement(input_string, reverse=True):
    if reverse == True:
        sequence = input_string[::-1]
    else:
        sequence = input_string
    sequence = sequence.upper()

    iupac_df = pd.DataFrame({
        'IUPAC Code': ['A', 'C', 'G', 'T', 'M', 'R', 'W', 'S', 'Y', 'K', 'V', 'H', 'D', 'B', 'N'],
        'Meaning': ['A', 'C', 'G', 'T', 'AC', 'AG', 'AT', 'CG', 'CT', 'GT', 'ACG', 'ACT', 'AGT', 'CGT', 'GATC'],
        'Complement': ['T', 'G', 'C', 'A', 'K', 'Y', 'W', 'S', 'R', 'M', 'B', 'D', 'H', 'V', 'N']
    })

    # Create a dictionary mapping IUPAC Code to Complement
    iupac_mapping = dict(zip(iupac_df['IUPAC Code'], iupac_df['Complement']))

    # Convert the string based on the mapping
    complemented_string = ''.join(iupac_mapping.get(base, base) for base in sequence)

    # Print the result
    # print(f"Input string: {input_string}")
    # print(f"Complemented string: {complemented_string}")

    return complemented_string


# ------------------------------------------  Primer design and analysis tool

def Parse_primer3_output_th(p, seq_id='', print_json=False, verbose=True):
    ''' print & csv output included'''

    product_size = []
    pair_any_th = []
    pair_end_th = []

    F_start = []
    F_len = []
    F_Tm = []
    F_gc = []
    F_any_th = []
    F_end_th = []
    F_hp_th = []
    F_seq = []

    R_start = []
    R_len = []
    R_Tm = []
    R_gc = []
    R_any_th = []
    R_end_th = []
    R_hp_th = []
    R_seq = []

    if print_json == True:
        p2 = json.dumps(p, cls=BytesEncoder, indent=2)
        print(p2)

    for pair in p.get("PRIMER_PAIR", []):
        product_size.append(pair.get("PRODUCT_SIZE"))
        pair_any_th.append(round(pair.get("COMPL_ANY_TH"), 1))
        pair_end_th.append(round(pair.get("COMPL_END_TH"), 1))

    for primer in p.get("PRIMER_LEFT", []):
        F_start.append(primer.get("COORDS")[0])
        F_len.append(primer.get("COORDS")[1])
        F_Tm.append(round(primer.get("TM"), 1))
        F_gc.append(round(primer.get("GC_PERCENT"), 1))
        F_any_th.append(round(primer.get("SELF_ANY_TH"), 1))
        F_end_th.append(round(primer.get("SELF_END_TH"), 1))
        F_hp_th.append(round(primer.get("HAIRPIN_TH"), 1))
        F_seq.append(primer.get("SEQUENCE"))

    for primer in p.get("PRIMER_RIGHT", []):
        R_start.append(primer.get("COORDS")[0])
        R_len.append(primer.get("COORDS")[1])
        R_Tm.append(round(primer.get("TM"), 1))
        R_gc.append(round(primer.get("GC_PERCENT"), 1))
        R_any_th.append(round(primer.get("SELF_ANY_TH"), 1))
        R_end_th.append(round(primer.get("SELF_END_TH"), 1))
        R_hp_th.append(round(primer.get("HAIRPIN_TH"), 1))
        R_seq.append(primer.get("SEQUENCE"))

    w = ''
    for i in range(len(F_start)):
        w += f'{i}\t\tstart\tlen\tTm\tgc%\tany_th\tend_th\thp_th\tSeq\n'
        w += 'primer_F\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
            F_start[i],
            F_len[i],
            F_Tm[i],
            F_gc[i],
            F_any_th[i],
            F_end_th[i],
            F_hp_th[i],
            F_seq[i]
        )
        if len(F_start) == len(R_start):
            w += 'primer_R\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                R_start[i],
                R_len[i],
                R_Tm[i],
                R_gc[i],
                R_any_th[i],
                R_end_th[i],
                R_hp_th[i],
                R_seq[i]
            )

            w += 'PRODUCT SIZE: {}, PAIR COMPL ANY_TH: {}, PAIR COMPL 3{}_TH: {}\n'.format(
                product_size[i], pair_any_th[i], "'", pair_end_th[i]
            )

    if verbose: print(w)

    if len(F_start) == len(R_start):
        dict = {
            'product_size': product_size,
            'pair_any_th': pair_any_th,
            'pair_end_th': pair_end_th,

            'F_seq': F_seq,
            'F_start': F_start,
            'F_len': F_len,
            'F_Tm': F_Tm,
            'F_gc': F_gc,
            'F_any_th': F_any_th,
            'F_end_th': F_end_th,
            'F_hp_th': F_hp_th,

            'R_seq': R_seq,
            'R_start': R_start,
            'R_len': R_len,
            'R_Tm': R_Tm,
            'R_gc': R_gc,
            'R_any_th': R_any_th,
            'R_end_th': R_end_th,
            'R_hp_th': R_hp_th

        }
        df = pd.DataFrame(dict)
        return w, df

    else:
        return w, None


def Parse_primer3_output(p, seq_id='', print_json=False,
                         verbose=True, oligo_label=[]):
    ''' print & csv output included'''
    # print(p)
    product_size = []
    pair_any = []
    pair_end = []

    F_start = []
    F_len = []
    F_Tm = []
    F_gc = []
    F_any = []
    F_end = []
    F_seq = []
    F_label = []

    R_start = []
    R_len = []
    R_Tm = []
    R_gc = []
    R_any = []
    R_end = []
    R_seq = []
    R_label = []

    if len(oligo_label) == 2:
        label0, label1 = oligo_label
    else:
        label0, label1 = ['', '']

    if print_json == True:
        p2 = json.dumps(p, cls=BytesEncoder, indent=2)
        print(p2)

    for pair in p.get("PRIMER_PAIR", []):
        product_size.append(pair.get("PRODUCT_SIZE"))
        pair_any.append(round(pair.get("COMPL_ANY"), 2))
        pair_end.append(round(pair.get("COMPL_END"), 2))

    i = 0
    for primer in p.get("PRIMER_LEFT", []):
        F_start.append(primer.get("COORDS")[0])
        F_len.append(primer.get("COORDS")[1])
        F_Tm.append(round(primer.get("TM"), 1))
        F_gc.append(round(primer.get("GC_PERCENT"), 1))
        F_any.append(round(primer.get("SELF_ANY"), 1))
        # F_end.append(round(primer.get("END_STABILITY"),1))
        F_end.append(p.get("PRIMER_LEFT_{}_SELF_END".format(i), 1))
        F_seq.append(primer.get("SEQUENCE"))
        F_label.append(label0)
        i += 1

    i = 0
    for primer in p.get("PRIMER_RIGHT", []):
        R_start.append(primer.get("COORDS")[0])
        R_len.append(primer.get("COORDS")[1])
        R_Tm.append(round(primer.get("TM"), 1))
        R_gc.append(round(primer.get("GC_PERCENT"), 1))
        R_any.append(round(primer.get("SELF_ANY"), 1))
        # R_end.append(round(primer.get("END_STABILITY"),1))
        R_end.append(p.get("PRIMER_RIGHT_{}_SELF_END".format(i), 1))
        R_seq.append(primer.get("SEQUENCE"))
        R_label.append(label1)
        i += 1

    w = ''

    # # for i in range(len(product_size)):
    # for i in range(len(F_start)):
    #     w += '{}\t\tstart\tlen\tTm\tgc%\tany\t3{}\tSeq\tlabel\n'.format(i, "'")
    #     w += 'primer_F\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
    #         F_start[i],
    #         F_len[i],
    #         F_Tm[i],
    #         F_gc[i],
    #         F_any[i],
    #         F_end[i],
    #         F_seq[i],
    #         F_label[i]
    #     )
    #
    #     if len(F_start) == len(R_start):
    #         w += 'primer_R\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
    #             R_start[i],
    #             R_len[i],
    #             R_Tm[i],
    #             R_gc[i],
    #             R_any[i],
    #             R_end[i],
    #             R_seq[i],
    #             R_label[i]
    #         )
    #
    #         w += 'PRODUCT SIZE: {}, PAIR COMPL ANY: {}, PAIR COMPL 3{}: {}\n'.format(
    #             product_size[i], pair_any[i], "'", pair_end[i]
    #         )
    # if verbose: print(w)

    def l8(s):
        s = str(s)
        return s.ljust(8, ' ')

    def l32(s):
        s = str(s)
        return s.ljust(32, ' ')

    for i in range(len(F_start)):
        w += f"\n{l8(i)}{' ' * 8}{l8('start')}{l8('len')}{l8('Tm')}{l8('gc%')}{l8('any')}{l8('end')}{l32('Seq')}"
        if (F_label[i] != '') or (R_label[i] != ''): w += f"{l8('label')}"
        w += '\n'

        w += f"primer_F{' ' * 8}{l8(F_start[i])}{l8(F_len[i])}{l8(F_Tm[i])}{l8(F_gc[i])}{l8(F_any[i])}{l8(F_end[i])}{l32(F_seq[i])}{l8(F_label[i])}\n"

        if len(F_start) == len(R_start):
            w += f"primer_R{' ' * 8}{l8(R_start[i])}{l8(R_len[i])}{l8(R_Tm[i])}{l8(R_gc[i])}{l8(R_any[i])}{l8(R_end[i])}{l32(R_seq[i])}{l8(R_label[i])}\n"
            w += 'PRODUCT SIZE: {}, PAIR COMPL ANY: {}, PAIR COMPL 3{}: {}\n'.format(
                product_size[i], pair_any[i], "'", pair_end[i]
            )
    if verbose: print(w)

    if len(F_start) == len(R_start):
        dict = {
            'product_size': product_size,
            'pair_any': pair_any,
            'pair_end': pair_end,

            'F_seq': F_seq,
            'F_start': F_start,
            'F_len': F_len,
            'F_Tm': F_Tm,
            'F_gc': F_gc,
            'F_any': F_any,
            'F_end': F_end,
            'F_label': F_label,

            'R_seq': R_seq,
            'R_start': R_start,
            'R_len': R_len,
            'R_Tm': R_Tm,
            'R_gc': R_gc,
            'R_any': R_any,
            'R_end': R_end,
            'R_label': R_label
        }

        # print('dict',dict)
        df = pd.DataFrame(dict)
        return w, df
    else:
        return w, None


def Primer3_analysis_250617(left_primer, right_primer=None, thermodynamic=1, monovalent_cation=1.5, divalent_cation=50,
                            verbose=False, horizontal=True):
    left_primer = left_primer.replace(' ', '').upper()

    if right_primer is None:
        seq_args = {

            "PRIMER_PICK_ANYWAY": 1,
            'SEQUENCE_TEMPLATE': left_primer,
            'PRIMER_MAX_SIZE': 36,
            'PRIMER_PICK_LEFT_PRIMER': 1,
            'PRIMER_PICK_RIGHT_PRIMER': 0,
            'SEQUENCE_PRIMER': left_primer,

            'PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT': thermodynamic,
            'PRIMER_THERMODYNAMIC_TEMPLATE_ALIGNMENT': thermodynamic,
            'PRIMER_TM_FORMULA': 1,
            'PRIMER_SALT_CORRECTIONS': 1,
            'PRIMER_SALT_MONOVALENT ': monovalent_cation,
            'PRIMER_SALT_DIVALENT': divalent_cation,
            'PRIMER_DNA_CONC': 50.0,
        }
    else:
        right_primer = right_primer.replace(' ', '').upper()
        mock_template = left_primer + 'A' * (100 - len(left_primer) - len(right_primer)) + reverse_complement(
            right_primer)
        seq_args = {

            "PRIMER_PICK_ANYWAY": 1,
            'SEQUENCE_TEMPLATE': mock_template,
            'PRIMER_MAX_SIZE': 27,
            'PRIMER_PICK_LEFT_PRIMER': 1,
            'PRIMER_PICK_RIGHT_PRIMER': 1,
            'SEQUENCE_PRIMER': left_primer,
            'SEQUENCE_PRIMER_REVCOMP': right_primer,

            'PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT': thermodynamic,
            'PRIMER_THERMODYNAMIC_TEMPLATE_ALIGNMENT': thermodynamic,
            'PRIMER_TM_FORMULA': 1,
            'PRIMER_SALT_CORRECTIONS': 1,
            'PRIMER_SALT_MONOVALENT ': monovalent_cation,
            'PRIMER_SALT_DIVALENT': divalent_cation,
            'PRIMER_DNA_CONC': 50.0,
        }

    global_args = {
        'PRIMER_PICK_INTERNAL_OLIGO': 0,
        'PRIMER_INTERNAL_MAX_SELF_END': 8,
        'PRIMER_MIN_SIZE': 5,

        'PRIMER_OPT_TM': 57,
        'PRIMER_MIN_TM': 53,
        'PRIMER_MAX_TM': 72.0,
        'PRIMER_MIN_GC': 20.0,
        'PRIMER_MAX_GC': 80.0,

        'PRIMER_MAX_POLY_X': 8,
        'PRIMER_MAX_NS_ACCEPTED': 8,

        'PRIMER_MAX_SELF_ANY': 8,
        'PRIMER_MAX_SELF_END': 3,
        'PRIMER_MAX_END_STABILITY': 9.0,
        'PRIMER_PAIR_MAX_COMPL_ANY': 8,
        'PRIMER_PAIR_MAX_COMPL_END': 3,

        'PRIMER_EXPLAIN_FLAG': 1,
        'PRIMER_LIBERAL_BASE': 1,
        'PRIMER_FIRST_BASE_INDEX': 0,
        'PRIMER_MAX_HAIRPIN_TH': 40.00,

        'PRIMER_MAX_TEMPLATE_MISPRIMING': 12.00,
        'PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING': 24.00,
        'PRIMER_MAX_TEMPLATE_MISPRIMING_TH': 40.00,
        'PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING_TH': 40.00
    }

    p0 = primer3.bindings.design_primers(
        seq_args=seq_args,
        global_args=global_args)

    def print_dictionary(p1, horizontal=True):
        if horizontal:
            a = ''
            b = ''
            for key, value in p1.items():
                a = a + f'\t{key}'
                if isinstance(value, float):
                    b = b + f'\t{value:.2f}'
                else:
                    b = b + f'\t{value}'
            print(a)
            print(b)
            return
        else:
            for key, value in p1.items():
                if isinstance(value, float):
                    print(f"{key}\t{value:.2f}")
                else:
                    print(f"{key}\t{value}")
            return

    # if verbose:
    #     print(f'Under monovalent cation {monovalent} mM, divalent cation {divalent} mM,')
    #     print_dictionary(p0, horizontal)
    #     print('\nForward primer')
    #     p1 = p0['PRIMER_LEFT'][0]
    #     print_dictionary(p1, horizontal)
    #
    #     if right_primer is not None:
    #         print('\nReverse primer')
    #         p1 = p0['PRIMER_RIGHT'][0]
    #         print_dictionary(p1, horizontal)
    #
    #         print('\nPair')
    #         p1 = p0['PRIMER_PAIR'][0]
    #         print_dictionary(p1, horizontal)

    if verbose:
        if thermodynamic == 0:
            Parse_primer3_output(p0)
        elif thermodynamic == 1:
            Parse_primer3_output_th(p0)

    return p0


def Primer3_design(template, mode=1, primer_pick_anyway=0, seq_id='', thermodynamic=0,
                   left_primer=None, right_primer=None,
                   pick_left=1, pick_right=1,
                   product_size_range=None, ns_accepted=0,
                   primer_min_tm=53, primer_opt_tm=57,
                   primer_min_size=16, primer_opt_size=18, primer_max_size=25,
                   end_throw=25, end_throw_left=None, end_throw_right=None,
                   head_throw=0, head_throw_left=None, head_throw_right=None,
                   print_explain=True, print_all_pairs=True, oligo_label=[],
                   preset=None, verbose=True):
    ''' Mode 1: pick_cloning_primer, take argument primer_max_size
        Mode 2: pick_by_ok_region, take argument end_throw(s), head_throw(s)
        Mode 0: general
        thermodynamic = 0, old output; thermodynamic = 1, _th output
        '''
    ''' preset 0 for homology cloning
        preset 1 for PCR and primer walking '''

    class BytesEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, bytes):
                return obj.decode('utf-8')
            return json.JSONEncoder.default(self, obj)

    if preset is not None:
        if preset == 0:
            primer_min_tm = 48
            primer_opt_tm = 52

            primer_min_size = 15
            primer_opt_size = 18
            primer_max_size = 25

        elif preset == 1:
            primer_min_tm = 55
            primer_opt_tm = 57

            primer_min_size = 16
            primer_opt_size = 18
            primer_max_size = 25


        elif preset == 2:  # in case the primer designed using preset 1 has high secondary structure
            primer_min_tm = 50
            primer_opt_tm = 54

            primer_min_size = 15
            primer_opt_size = 16
            primer_max_size = 25

    if not end_throw_left:
        end_throw_left = end_throw
    if not end_throw_right:
        end_throw_right = end_throw
    if not head_throw_left:
        head_throw_left = head_throw
    if not head_throw_right:
        head_throw_right = head_throw

    seq_args = {
        'SEQUENCE_TEMPLATE': template,
        'PRIMER_MAX_SIZE': primer_max_size,
        # 'PRIMER_PRODUCT_SIZE_RANGE': '40-{}'.format(len(template)),
        # 'PRIMER_PRODUCT_SIZE_RANGE': '{}-{}'.format(primer_max_size, len(template)),
        'PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT': thermodynamic,
        'PRIMER_PICK_LEFT_PRIMER': pick_left,
        'PRIMER_PICK_RIGHT_PRIMER': pick_right
        # 'PRIMER_PICK_RIGHT_PRIMER': 0
    }
    if pick_left == 1 and pick_right == 1:
        if product_size_range is None:
            seq_args.update({
                'PRIMER_PRODUCT_SIZE_RANGE': '{}-{}'.format(primer_max_size, len(template))
            })
        else:
            a = min(product_size_range)
            b = max(product_size_range) + 1
            seq_args.update({
                'PRIMER_PRODUCT_SIZE_RANGE': '{}-{}'.format(a, b)
            })

    if left_primer is not None:
        seq_args['SEQUENCE_PRIMER'] = left_primer

    if right_primer is not None:
        seq_args['SEQUENCE_PRIMER_REVCOMP'] = right_primer

    if mode == 1:
        seq_args['PRIMER_TASK'] = "pick_cloning_primers"

    elif mode == 2:

        seq_args['PRIMER_TASK'] = "generic"
        seq_args['SEQUENCE_PRIMER_PAIR_OK_REGION_LIST'] = (
            head_throw_left,
            end_throw_left - head_throw_left,
            len(template) - (end_throw_right),
            end_throw_right - head_throw_right)

        a = seq_args['SEQUENCE_PRIMER_PAIR_OK_REGION_LIST']
        print('SEQUENCE_PRIMER_PAIR_OK_REGION_LIST = left {}~{}, right {}~{}'.format(
            a[0],
            a[0] + a[1] - 1,
            a[2],
            a[2] + a[3] - 1))

    elif mode == 0:
        seq_args['PRIMER_TASK'] = "generic"
    else:
        return None

    global_args = {
        "PRIMER_PICK_ANYWAY": primer_pick_anyway,
        'PRIMER_OPT_SIZE': primer_opt_size,
        'PRIMER_PICK_INTERNAL_OLIGO': 0,
        'PRIMER_INTERNAL_MAX_SELF_END': 8,
        'PRIMER_MIN_SIZE': primer_min_size,

        'PRIMER_OPT_TM': primer_opt_tm,
        'PRIMER_MIN_TM': primer_min_tm,
        'PRIMER_MAX_TM': 72.0,
        'PRIMER_MIN_GC': 20.0,
        'PRIMER_MAX_GC': 80.0,

        'PRIMER_MAX_POLY_X': 5,
        'PRIMER_MAX_NS_ACCEPTED': ns_accepted,

        'PRIMER_SALT_MONOVALENT': 50.0,
        'PRIMER_DNA_CONC': 50.0,

        'PRIMER_MAX_SELF_ANY': 8,
        'PRIMER_MAX_SELF_END': 3,
        'PRIMER_MAX_END_STABILITY': 9.0,
        'PRIMER_PAIR_MAX_COMPL_ANY': 8,
        'PRIMER_PAIR_MAX_COMPL_END': 3,

        'PRIMER_SALT_CORRECTIONS': 1,  # SantaLucia JR (1998)
        'PRIMER_SALT_CORRECTIONS': 1,  # SantaLucia JR (1998)

        'PRIMER_EXPLAIN_FLAG': 1,
        'PRIMER_LIBERAL_BASE': 1,
        # 'PRIMER_FIRST_BASE_INDEX': 1,
        'PRIMER_FIRST_BASE_INDEX': 0,

        # 'PRIMER_MAX_HAIRPIN_TH': 47.00,
        # 'PRIMER_INTERNAL_MAX_HAIRPIN_TH': 47.00,
        'PRIMER_MAX_HAIRPIN_TH': 40.00,
        # 'PRIMER_INTERNAL_MAX_HAIRPIN_TH': 24.00,

        'PRIMER_MAX_TEMPLATE_MISPRIMING': 12.00,
        'PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING': 24.00,
        'PRIMER_MAX_TEMPLATE_MISPRIMING_TH': 40.00,
        'PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING_TH': 40.00

    }

    # print('seq_args', seq_args)
    # print('global_args', global_args)
    primers = primer3.bindings.design_primers(
        seq_args=seq_args,
        global_args=global_args)

    if verbose and print_explain:
        print('PRIMER_LEFT_EXPLAIN: {}\nPRIMER_RIGHT_EXPLAIN: {}\nPRIMER_PAIR_EXPLAIN: {}\n'.format(
            primers.get('PRIMER_LEFT_EXPLAIN', 'na'), primers.get('PRIMER_RIGHT_EXPLAIN', 'na'),
            primers.get('PRIMER_PAIR_EXPLAIN', 'na')))

    if thermodynamic == 0:
        w, df = Parse_primer3_output(primers, seq_id=seq_id,
                                     oligo_label=oligo_label, verbose=verbose)

    elif thermodynamic == 1:
        w, df = Parse_primer3_output_th(primers, seq_id=seq_id, verbose=verbose)

    return primers, df


def extract_primer3_design_0223(p, rf, number_picked=1, print_result=False):
    if rf[0].lower() in ['f', 'l']:
        direction = 'LEFT'
    elif rf[0].lower() in ['r']:
        direction = 'RIGHT'
    else:
        print('direction unspecified, function extract_primer_pick ')
        return

    result = []
    for i in range(min(len(p.get(f"PRIMER_{direction}", [])), number_picked)):
        oligolen = p.get(f"PRIMER_{direction}_{i}")[1]
        Tm = round(p.get(f"PRIMER_{direction}_{i}_TM"), 1)
        gc = p.get(f"PRIMER_{direction}_{i}_GC_PERCENT")

        self_any = p.get(f"PRIMER_{direction}_{i}_SELF_ANY")
        self_end = p.get(f"PRIMER_{direction}_{i}_SELF_END")
        seq = p.get(f"PRIMER_{direction}_{i}_SEQUENCE")

        result.append(
            {'direction': direction,
             'oligolen': oligolen,
             'Tm': Tm,
             'gc': round(gc, 1),
             'self_any': round(self_any, 1),
             'self_end': round(self_end, 1),
             'seq': seq
             }
        )
        if print_result == True:
            print(result)

    return result


def Primer3_pick_one_side(template, primer=None, thermodynamic=0, mode=1,
                          primer_min_tm=55, primer_opt_tm=57,
                          primer_min_size=16, primer_opt_size=18, primer_max_size=25,
                          rf='f', anyway=True, number_picked=1,
                          ns_accepted=0,
                          print_explain=False,
                          print_result=False):
    '''

    :param template:
    :param thermodynamic:
    :param primer_min_tm:
    :param primer_opt_tm:
    :param primer_min_size:
    :param primer_opt_size:
    :param primer_max_size:
    :param rf: if rf[0] in ['f','l'], pick left. elif rf[1] == 'r', pick right
    :param anyway: if anyway == True, first test primer_pick_anyway = 0, if none, then pick_anyway = 1
                    if anyway == False, test primer_pick_anyway = 0, if none, return none
    :return:
    '''

    if rf[0].lower() in ['f', 'l']:
        direction = 'LEFT'
    elif rf[0].lower() in ['r']:
        direction = 'RIGHT'
    else:
        print('direction unspecified, function extract_primer_pick ')
        return

    seq_args = {
        'SEQUENCE_TEMPLATE': template,
        'PRIMER_MIN_SIZE': primer_min_size,
        'PRIMER_OPT_SIZE': primer_opt_size,
        'PRIMER_MAX_SIZE': primer_max_size,

        'PRIMER_OPT_TM': max(primer_opt_tm, primer_min_tm),
        'PRIMER_MIN_TM': primer_min_tm,

        'PRIMER_MAX_NS_ACCEPTED': ns_accepted,

        'PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT': thermodynamic
        # 'PRIMER_PICK_LEFT_PRIMER': 1,
        # 'PRIMER_PICK_RIGHT_PRIMER': 0
        # 'PRIMER_TASK': "pick_cloning_primers"

    }

    if mode == 1:
        seq_args.update({'PRIMER_TASK': "pick_cloning_primers"})
    elif mode == 0:
        seq_args.update({'PRIMER_TASK': "generic"})

    if direction == 'RIGHT':  # reverse
        seq_args.update(
            {'PRIMER_PICK_LEFT_PRIMER': 0,
             'PRIMER_PICK_RIGHT_PRIMER': 1}
        )
        if primer is not None:
            seq_args.update({'SEQUENCE_PRIMER_REVCOMP': primer})
    else:
        seq_args.update(
            {'PRIMER_PICK_LEFT_PRIMER': 1,
             'PRIMER_PICK_RIGHT_PRIMER': 0}
        )
        if primer is not None:
            seq_args.update({'SEQUENCE_PRIMER': primer})

    # print(seq_args)

    global_args = {
        "PRIMER_PICK_ANYWAY": 0,
        'PRIMER_PICK_INTERNAL_OLIGO': 0,
        'PRIMER_INTERNAL_MAX_SELF_END': 8,

        # 'PRIMER_OPT_TM': max(primer_opt_tm,primer_min_tm),
        # 'PRIMER_MIN_TM': primer_min_tm,
        'PRIMER_MAX_TM': 72.0,
        'PRIMER_MIN_GC': 20.0,
        'PRIMER_MAX_GC': 80.0,

        'PRIMER_MAX_POLY_X': 5,

        'PRIMER_SALT_MONOVALENT': 50.0,
        'PRIMER_DNA_CONC': 50.0,

        'PRIMER_MAX_SELF_ANY': 8,
        'PRIMER_MAX_SELF_END': 3,
        'PRIMER_MAX_END_STABILITY': 9.0,
        'PRIMER_PAIR_MAX_COMPL_ANY': 8,
        'PRIMER_PAIR_MAX_COMPL_END': 3,

        'PRIMER_SALT_CORRECTIONS': 1,  # SantaLucia JR (1998)

        'PRIMER_EXPLAIN_FLAG': 1,
        'PRIMER_LIBERAL_BASE': 1,
        # 'PRIMER_FIRST_BASE_INDEX': 1,
        'PRIMER_FIRST_BASE_INDEX': 0,

        # 'PRIMER_MAX_HAIRPIN_TH': 47.00,
        # 'PRIMER_INTERNAL_MAX_HAIRPIN_TH': 47.00,
        'PRIMER_MAX_HAIRPIN_TH': 40.00,
        # 'PRIMER_INTERNAL_MAX_HAIRPIN_TH': 24.00,

        'PRIMER_MAX_TEMPLATE_MISPRIMING': 12.00,
        'PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING': 24.00,
        'PRIMER_MAX_TEMPLATE_MISPRIMING_TH': 40.00,
        'PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING_TH': 40.00

    }

    p = primer3.bindings.design_primers(
        seq_args=seq_args,
        global_args=global_args)

    if print_explain == True:
        print('\nPRIMER_{}_EXPLAIN: {}'.format(direction, p.get(f'PRIMER_{direction}_EXPLAIN', 'na')))

    if anyway == False:
        return extract_primer3_design_0223(p, rf, number_picked, print_result=print_result)
    else:
        if extract_primer3_design_0223(p, rf, number_picked) != []:
            return extract_primer3_design_0223(p, rf, number_picked, print_result=print_result)
        else:
            # print('primer_pick_anyway')

            global_args = {
                "PRIMER_PICK_ANYWAY": 1,
                'PRIMER_PICK_INTERNAL_OLIGO': 0,
                'PRIMER_INTERNAL_MAX_SELF_END': 8,

                # 'PRIMER_OPT_TM': max(primer_opt_tm, primer_min_tm),
                # 'PRIMER_MIN_TM': primer_min_tm,
                'PRIMER_MAX_TM': 72.0,
                'PRIMER_MIN_GC': 20.0,
                'PRIMER_MAX_GC': 80.0,

                'PRIMER_MAX_POLY_X': 5,
                # 'PRIMER_MAX_NS_ACCEPTED': 5,

                'PRIMER_SALT_MONOVALENT': 50.0,
                'PRIMER_DNA_CONC': 50.0,

                'PRIMER_MAX_SELF_ANY': 8,
                'PRIMER_MAX_SELF_END': 3,
                'PRIMER_MAX_END_STABILITY': 9.0,
                'PRIMER_PAIR_MAX_COMPL_ANY': 8,
                'PRIMER_PAIR_MAX_COMPL_END': 3,

                'PRIMER_SALT_CORRECTIONS': 1,  # SantaLucia JR (1998)

                'PRIMER_EXPLAIN_FLAG': 1,
                'PRIMER_LIBERAL_BASE': 1,
                # 'PRIMER_FIRST_BASE_INDEX': 1,
                'PRIMER_FIRST_BASE_INDEX': 0,

                # 'PRIMER_MAX_HAIRPIN_TH': 47.00,
                # 'PRIMER_INTERNAL_MAX_HAIRPIN_TH': 47.00,
                'PRIMER_MAX_HAIRPIN_TH': 40.00,
                # 'PRIMER_INTERNAL_MAX_HAIRPIN_TH': 24.00,

                'PRIMER_MAX_TEMPLATE_MISPRIMING': 12.00,
                'PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING': 24.00,
                'PRIMER_MAX_TEMPLATE_MISPRIMING_TH': 40.00,
                'PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING_TH': 40.00

            }
            p = primer3.bindings.design_primers(
                seq_args=seq_args,
                global_args=global_args)

            return extract_primer3_design_0223(p, rf, number_picked, print_result=print_result)


def primer_truncation_analysis(primer0, monovalent_cation=50, divalent_cation=1.5):
    # analyze 5' truncation of the primer (Taqman probe)
    print("\nAnalyze 5' truncation of the primer (Taqman probe)")
    for i in range(len(primer0) - 5):
        primer = primer0[i:]
        p = Primer3_analysis_250617(left_primer=primer, thermodynamic=1,
                                    monovalent_cation=monovalent_cation, divalent_cation=divalent_cation, verbose=False)
        Tm = p['PRIMER_LEFT'][0]['TM']
        print(f'{primer}, Tm = {Tm:.2f}, length = {len(primer)}')

    # analyze 3' truncation of the primer (Taqman probe)
    print("\nAnalyze 3' truncation of the primer (Taqman probe)")
    for i in range(len(primer0), 5, -1):
        primer = primer0[:i]
        p = Primer3_analysis_250617(left_primer=primer, thermodynamic=1,
                                    monovalent_cation=monovalent_cation, divalent_cation=divalent_cation, verbose=False)
        Tm = p['PRIMER_LEFT'][0]['TM']
        print(f'{primer}, Tm = {Tm:.2f}, length = {len(primer)}')
    return


def analyze_single_seq(seq, verbose=False):  # applicable to sequence <= 60 nt
    seq = seq.upper()
    seq = seq.replace('I', 'G').replace('U', 'T').replace(' ', '')

    # Hairpin
    hairpin = primer3.bindings.calc_hairpin(seq)
    hairpin_dg = round(hairpin.dg / 1000, 2)
    hairpin_tm = round(hairpin.tm, 2)

    # Self-dimer (any)
    homodimer = primer3.bindings.calc_homodimer(seq)
    any_dg = round(homodimer.dg / 1000, 2)
    any_tm = round(homodimer.tm, 2)

    # Self-dimer (3' end) via designPrimers
    sub_seq = seq[-36:]
    seq_args = {
        'SEQUENCE_ID': 'test',
        'SEQUENCE_TEMPLATE': sub_seq,
        'SEQUENCE_INCLUDED_REGION': [0, len(sub_seq)],
        'PRIMER_PICK_LEFT_PRIMER': 1,
        'PRIMER_PICK_RIGHT_PRIMER': 0,
        'PRIMER_OPT_SIZE': len(sub_seq),
        'PRIMER_MIN_SIZE': len(sub_seq),
        'PRIMER_MAX_SIZE': len(sub_seq),
    }
    global_args = {}  # required second argument
    result = primer3.bindings.design_primers(seq_args, global_args)

    end_tm = result.get('PRIMER_LEFT_0_SELF_END_TH', 0.0)  # 3' dimer Tm
    end_tm = round(end_tm, 2)

    if verbose:
        # Hairpin analysis
        print(f"Input seq: {seq}")
        print(f"length: {len(seq)}")

        print(f"Any Tm: {any_tm:.2f} °C")
        print(f"End Tm: {end_tm:.2f} °C")
        print(f"H.p Tm: {hairpin_tm:.2f} °C")

        print(f"Any ΔG: {any_dg:.2f} kcal/mol")
        print(f"H.p ΔG: {hairpin_dg:.2f} kcal/mol")

    return seq, any_tm, end_tm, hairpin_tm, any_dg, hairpin_dg,


def secondary_structure_analysis(seq1, seq2=None, Extensions=[]):
    seq1 = seq1.upper().replace('I', 'G').replace('U', 'T').replace(' ', '')
    seq2 = seq2.upper().replace('I', 'G').replace('U', 'T').replace(' ', '') if seq2 else None

    def secondary_structure_analysis_flat(seq1, seq2=None):
        # seq1 results
        res1 = analyze_single_seq(seq1)

        # seq2 results
        res2 = analyze_single_seq(seq2) if seq2 else [None] * 4

        # heterodimer
        if seq2:
            hetero = primer3.bindings.calc_heterodimer(seq1.upper(), seq2.upper())
            hetero_res = tuple([round(hetero.tm, 2), round(hetero.dg / 1000, 2)])
        else:
            hetero_res = tuple([None, None])

        # Combine all values into one list: 4 + 4 + 2 = 10
        combined = res1 + res2 + hetero_res
        return combined

    for k in range(len(Extensions)):
        extension = Extensions[k]

        all_results = []
        for i in range(len(extension)):
            s1 = seq1 + extension[:i]
            s2 = seq2 + extension[:i] if seq2 else none

            # hairpin_dg, hairpin_tm, homodimer_dg, homodimer_tm =  GBparser.secondary_structure_analysis(seq2, verbose= False)
            # print('{}\t{}\t{}\t{}\t{}\t{}'.format( i, seq2, hairpin_dg, hairpin_tm, homodimer_dg, homodimer_tm))

            flat_list = secondary_structure_analysis_flat(s1, s2)
            all_results.append(flat_list)

        df = pd.DataFrame(all_results, columns=[
            'seq1', 'seq1_any_tm', 'seq1_end_tm', 'seq1_hairpin_tm', 'seq1_any_dg', 'seq1_hairpin_dg',
            'seq2', 'seq2_any_tm', 'seq2_end_tm', 'seq2_hairpin_tm', 'seq2_any_dg', 'seq2_hairpin_dg',
            'hetero_tm', 'hetero_dg'
        ])
        print(f'Extension Seq ID {k + 1}')
        print(df.to_csv(sep='\t', index=False))
        # df.to_csv(f"analysis_id_{k+1}.csv", index=False)
    return


# ------------------------------------------ Cloning design tool

def check_against_IIS_site(gb_str, IIS_site='GGTCTC', display=True):
    IIS_site = IIS_site.upper()
    IIS_site_r = reverse_complement(IIS_site)

    # check against BsaI site
    gb = gb_parse0(gb_str)
    sequence = origin_parse0(gb['ORIGIN']).upper()
    sequence2 = sequence + sequence

    record = []


    curser = 0
    substr = sequence2[curser:]
    while substr.find(IIS_site) != -1:
        rf = 'f'
        j0 = curser + substr.find(IIS_site)
        j1 = j0 + len(IIS_site)
        if j0 > len(sequence):
            break
        record.append([j0, j1, 'forward'])

        gb_str = gb_add_feature(gb_str, s=j0, e=j1, rf=rf, type='misc_structure', annotation='IIS_site')
        curser = j1
        substr = sequence2[curser:]

    curser = 0
    substr = sequence2[curser:]
    while substr.find(IIS_site_r) != -1:
        rf = 'r'
        j0 = curser + substr.find(IIS_site_r)
        j1 = j0 + len(IIS_site_r)
        if j0 > len(sequence):
            break
        record.append([j0, j1, 'reverse'])

        gb_str = gb_add_feature(gb_str, s=j0, e=j1, rf=rf, type='misc_structure', annotation='IIS_site')
        curser = j1
        substr = sequence2[curser:]

    if record:
        print(f'\nThe plasmid sequence contain IIS_site: {IIS_site} at ')
        for x, y, z in record:
            print(f'\t({x}, {y}) in {z}')

        print(f'\tEdit the sequence or try another TypeIIS enzyme\n')

        if display: gb_display(gb_str)
        return False

    else:
        return True


def cloning_design_wrapper_1(base_filename, feature_select, mutation_codon_no=None, replacement_codon=None,
                             notations=None, species='Escherichia coli K-12',
                             index0='0', index1='1',
                             plasmid_prefix='h', oligo_prefix='E',
                             cloning_method='GG', IIS_site='GGTCTC', IIS_prefix='aaGGTCTCn', IIS_side='u',
                             N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0, verbose=True
                             ):
    if index1 is None:
        index1 = index0

    plasmid_file_path = f'Plasmid_list_{index0}.csv'
    plasmid_file_path2 = f'Plasmid_list_{index1}.csv'

    if plasmid_file_path in os.listdir():
        print(check_encode(plasmid_file_path))
        plasmid_list = import_oligo_list(plasmid_file_path)
    else:
        plasmid_list = []

    oligo_file_path = f'Oligo_list_{index0}.csv'
    oligo_file_path2 = f'Oligo_list_{index1}.csv'

    if oligo_file_path in os.listdir():
        print(check_encode(oligo_file_path))
        oligo_list = import_oligo_list(oligo_file_path)
    else:
        oligo_list = []

    gb_str = Read_gb(base_filename, False, True)
    if gb_str is None: return

    if not check_against_IIS_site(gb_str, IIS_site): return

    codon_table, *_ = extract_kazusa()

    oligo_list2, plasmid_list2, t, printout_name = \
        multi_cloning_desiigns_250901(gb_str, feature_select, mutation_codon_no, replacement_codon, notations,
                                      species=species,
                                      oligo_list=oligo_list,
                                      plasmid_list=plasmid_list,
                                      oligo_prefix=oligo_prefix,
                                      plasmid_prefix=plasmid_prefix,
                                      cloning_method=cloning_method,
                                      IIS_site=IIS_site,
                                      IIS_prefix=IIS_prefix,
                                      IIS_side=IIS_side,
                                      N_match_cutoff=N_match_cutoff,
                                      YR_match_cutoff=YR_match_cutoff,
                                      GC_threshold=GC_threshold,
                                      verbose=verbose)
    if t is None:
        print(f'cloning design aborted.\n{"!" * 60}\n')
        return

    export_oligo_list(oligo_list2, oligo_file_path2)
    export_oligo_list(plasmid_list2, plasmid_file_path2)
    return


def cloning_design_wrapper_0(initial_filename, mutation_site, pcr_source=None, new_filename=None,
                             index0='0', index1='1',
                             oligo_prefix='E', plasmid_prefix='h',
                             cloning_method='GG', IIS_site='GGTCTC', IIS_prefix='aaGGTCTCn', IIS_side='u',
                             N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
                             gb_display_feature=None, verbose=True):
    '''

    :param initial_filename:  the initial gb filename (without .gb extension)
    :param mutation_site: a list of ranges
    :param pcr_source: the PCR template, if unspecified, = the initial gb filename
    :param new_filename: the new gb filename (sequence unchanged, primer annotations added)
    :param index0: to import oligo_list_{index0}.csv and plasmid_list_{index0}.csv (allow for primer reuse)
    :param index1: to export updated information into oligo_list_{index1}.csv and plasmid_list_{index1}.csv
    :param oligo_prefix: oligo names will be assigned automatically with the prefix
    (e.g. if oligo_prefix = 'E' and the oligo_list_{index0}.csv contain E01 ~ E10, the new oligos will be named starting from E01 be named E11)
    :param plasmid_prefix: plasmid names will be assigned automatically with the prefix
    (e.g. if  plasmid_prefix = 'h' and the plasmid_list_{index0}.csv contain h001 ~ h023, the new plasmid will be named h024)
    :param cloning_method: 'GG' for golden gate cloning; 'HotF' for homology-based cloning (including Gibson assembly, Hot Fusion, NEBuilder HiFi assembly)
    :param IIS_site: TypeIIS restriction enzyme recognition site, 'GGTCTC' for BsaI
    :param IIS_prefix: Sequence containing the TypeIIS enzyme recognition site to be placed immediately upstream the annealing region.
    :param IIS_side: for example, set ['l3', 'r5'] to design annealing region on the left side & within 3-nt away from the first linkage and
                    design the annealing region on the right side & within 5-nt away from the second linkage
    :param N_match_cutoff:
    :param YR_match_cutoff:
    :param GC_threshold:
    :param gb_display_feature:
    :return:
    '''
    # do not create new gb file or new plasmid name
    # input: ready-made gb file

    if new_filename is None:
        new_filename = initial_filename
    printout_prefix = new_filename + '_'

    if index1 is None:
        index1 = index0

    if pcr_source is None:
        pcr_source = [initial_filename]
    plasmid_file_path = f'Plasmid_list_{index0}.csv'
    plasmid_file_path2 = f'Plasmid_list_{index1}.csv'

    if plasmid_file_path in os.listdir():
        # print(check_encode(plasmid_file_path))
        plasmid_list = import_oligo_list(plasmid_file_path)
    else:
        plasmid_list = []

    oligo_file_path = f'Oligo_list_{index0}.csv'
    oligo_file_path2 = f'Oligo_list_{index1}.csv'

    if oligo_file_path in os.listdir():
        oligo_list = import_oligo_list(oligo_file_path)
    else:
        oligo_list = []

    gb_str = Read_gb(initial_filename, False, True)

    if not check_against_IIS_site(gb_str, IIS_site): return

    mutation_site_label = None
    gb_str = gb_rename_locus(gb_str, new_filename)

    gb_str, oligo_list2, cloning_guide_df, descrip2 = cloning_design_251223(
        gb_str, mutation_site, pcr_source,
        oligo_list=oligo_list,
        oligo_prefix=oligo_prefix,
        plasmid_prefix=plasmid_prefix,
        cloning_method=cloning_method,
        IIS_site=IIS_site,
        IIS_prefix=IIS_prefix,
        IIS_side=IIS_side,
        N_match_cutoff=N_match_cutoff,
        YR_match_cutoff=YR_match_cutoff,
        GC_threshold=GC_threshold,
        verbose=verbose,
    )

    if gb_str is None:
        print(f'cloning design aborted.\n{"!" * 60}\n')
        return

    export_oligo_list(oligo_list2, oligo_file_path2)
    export_oligo_list(plasmid_list, plasmid_file_path2)

    output_gb(gb_str, new_filename)
    if gb_display_feature == 'all':
        gb_display(gb_str,
                   automatic_feature_sort=False,
                   display_feature_list=False
                   )
    elif gb_display_feature:
        gb_display(gb_str,
                   feature_select=gb_display_feature,  # will overwrite display_range
                   type_filter=['CDS', 'variation', 'primer'],
                   automatic_feature_sort=False,
                   display_feature_list=False
                   )

    return


def multi_cloning_desiigns_250901(gb_str, feature_select,
                                  mutation_codon_no=None, replacement_codon=None, notations=None,
                                  species='Escherichia coli K-12',
                                  oligo_list=[], plasmid_list=[], oligo_prefix='E', plasmid_prefix='h',
                                  cloning_method='GG', IIS_site='GGTCTC', IIS_prefix='aaGGTCTCn', IIS_side=['l', 'r'],
                                  N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0, verbose=True):
    ''' adapted from Directed_mutagenesis_250726
    allow either provision of
    a. mutation_codon_no and replacement_codon
    b. notations

    '''

    replacement_note = None
    codon_table, *_ = extract_kazusa()
    triplet_to_aa = dict(zip(codon_table['triplet'], codon_table['amino acid']))
    # replacement_codon = replacement_codon.replace(' ','')

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])
    sequence = origin_parse0(gb['ORIGIN']).lower()
    sequence2 = sequence + sequence
    feat = retrieve_feature(gb_str, feature_select)

    locus = gb["LOCUS"]
    initial_locus_name = locus[12:35].rstrip()

    if feat['rf'][0] == 'r':  # make the target feature forward
        gb_str = gb_reverse(gb_str)

        gb = gb_parse0(gb_str)
        features = feature_parse0(gb['FEATURES'])
        sequence = origin_parse0(gb['ORIGIN']).lower()
        sequence2 = sequence + sequence
        feat = retrieve_feature(gb_str, feature_select)

    definition0 = extract_gb_elements(gb_str, header='DEFINITION')

    s = feat['a'] - 1
    e = feat['b']
    rf = feat['rf']
    codon_start = feat.get('codon_start', 1)
    aa_start_index = feat.get('aa_start_index', 1)
    cds_sequence = sequence2[s:e]
    peptide_sequence = translate_0220(cds_sequence, rf=rf, codon_start=codon_start, aa_start=aa_start_index)[0]

    guides = []
    descrips = []
    locus_names = []
    definitions = []

    if mutation_codon_no and replacement_codon:
        new_gb_str, new_mutation_site, new_locus_name, new_definition, plasmid_list = \
            gb_edit_variation(gb_str, feature_select, mutation_codon_no, replacement_codon, plasmid_list,
                              plasmid_prefix)
    elif notations:
        new_gb_str, new_mutation_site, new_locus_name, new_definition, plasmid_list = \
            gb_edit_by_notations(gb_str, feature_select, notations, species, plasmid_list, plasmid_prefix)
    else:
        print('''
One has to provide either
    a. mutation_codon_no and replacement_codon, or
    b. notations
    ''')
        return None, None, None, None

    for i in range(len(new_gb_str)):
        gb_str2 = new_gb_str[i]
        mutation_site = new_mutation_site[i]
        locus_name = new_locus_name[i]
        definition = new_definition[i]

        # print('mutation_site', mutation_site)

        gb_str2, oligo_list2, cloning_guide_df, descrip2 = cloning_design_251223(
            gb_str2, mutation_site, pcr_source=initial_locus_name,
            oligo_list=oligo_list,
            oligo_prefix=oligo_prefix,
            plasmid_prefix=plasmid_prefix,
            cloning_method=cloning_method,
            IIS_site=IIS_site,
            IIS_prefix=IIS_prefix,
            IIS_side=IIS_side,
            N_match_cutoff=N_match_cutoff,
            YR_match_cutoff=YR_match_cutoff,
            GC_threshold=GC_threshold,
            verbose=verbose,
        )

        if gb_str2 is None:
            return None, None, None, None

        guides.append(cloning_guide_df)
        descrips.append(descrip2)
        locus_names.append(locus_name)
        definitions.append(definition)

        # update new oligo_list
        oligo_list = oligo_list2

        # output gb
        output_gb(gb_str2, locus_name)

    t = ''
    for i in range(len(guides)):
        df = guides[i]
        descrip2 = descrips[i]
        formatted_df = dataframe_to_tab_separated_string(df, preceding_tab=1)
        # formatted_df = df.to_string(index=False, col_space=16, justify='left')
        t += '\n{} {}'.format('-' * 64, locus_names[i])
        t += '\n{}'.format(definitions[i])
        t += '\n{}'.format(formatted_df)
        if descrip2:
            t += '\n{}'.format(descrip2)

    if len(new_gb_str) > 1:
        print('================================================================ Overview')
        print(t)
        print('---------------------------------')
        print('base_filename = "{}"'.format(initial_locus_name))
        print('mutation_codon_no =', mutation_codon_no)
        # # print('blunt_end_ligation =', blunt_end_ligation)

    # prepare printout header
    if len(locus_names) == 1:
        printout_name = locus_names[0] + '_printout.txt'
    else:
        printout_name = '{}-{}_printout.txt'.format(locus_names[0], locus_names[-1])

    return oligo_list, plasmid_list, t, printout_name


def cloning_design_251223(gb_str, mutation_site, pcr_source=[], mutation_site_label=None,
                          oligo_list=[], oligo_prefix='D', plasmid_prefix='h',
                          cloning_method='GG', IIS_site='GGTCTC', IIS_prefix='aaGGTCTCn', IIS_side=['l', 'r'],
                          N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
                          preset=1, verbose=True
                          ):
    '''

    :param gb_str: the gb file name (without .gb extension)
    :param mutation_site: a list of ranges
    :param pcr_source: pcr template, if unspecified, = the gb filename
    :param mutation_site_label:
    :param oligo_list:
    :param oligo_prefix:
    :param plasmid_prefix:
    :param cloning_method:
    :param IIS_site:
    :param IIS_prefix:
    :param IIS_side:
    :param N_match_cutoff:
    :param YR_match_cutoff:
    :param GC_threshold:
    :return:
    '''
    '''
    cloning_design_251223
        based on  cloning_design_250530,
        remove features: colony PCR design, RFOF, DPL cloning method
        added features: with GG, allow assigning the adhesive site: on the left, right, or unspecified
                        with GG, allow primer walk

        the return would be in the same format'''

    def finding_gap(lst, n):
        ''' only return the gaps within min(lst) to max(lst)'''
        result0, result_range, result_list = group_integers_within_distance(lst, n)
        # print(result0, result_range, result_list)
        a = [x for x in range(min(lst), max(lst) + 1) if x not in result_list]
        # print(a)
        result0, result_range, result_list = group_integers_within_distance(a, 1)
        return result0, result_range, result_list

    def Lst0(mutation_site):
        if isinstance(mutation_site, int):
            lst0 = [mutation_site]

        elif isinstance(mutation_site, range):
            lst0 = list(mutation_site)

        elif all(isinstance(item, int) for item in mutation_site):
            lst0 = mutation_site

        elif all(isinstance(item, range) for item in mutation_site):
            from itertools import chain
            lst0 = list(chain.from_iterable(mutation_site))

        elif isinstance(mutation_site, list):
            lst0 = []
            for x in mutation_site:
                if isinstance(x, int):
                    lst0.append(x)
                elif isinstance(x, range):
                    lst0 += list(x)
                else:
                    print('mutation_site has to be either an integer, a range, or a list of integers & ranges')
                    return None

        else:
            print('mutation_site has to be either an integer, a range, or a list of integers & ranges')
            return None
        return lst0

    def linking_seg_HotF_0223(gb_str, segment_info, mutation_site, oligo_list=[], scenario=None,
                              max_primer_len=60, min_gaplen=10, preset=1  # this row is set
                              ):

        def primer_walk_HotF(sequence2, t, a, oligo_list=[], mutation_site=None, distance0=None,
                             max_primer_len=60, min_assembly_oligolen=36, min_advance=20, min_gaplen=16,
                             # this row is set
                             ):

            def reverse_rf(rf):
                if rf == 'f':
                    return 'r'
                else:
                    return 'f'

            t0, t1, t2, t3 = t
            a0, a1, a2, a3 = a

            ''' to design two new primers, 
            a. allow overlap within t1 ~ t2, ns_accepted = 0, FF pair
            b. allow overlap within t0 ~ t3, ns_accepted = 0, FF pair
            c. allow overlap within t1 ~ t2, ns_accepted = 0, FTTF pair
            b. allow overlap within t0 ~ t3, ns_accepted = 0, FTTF pair
            e./f.  allow overlap within t0 ~ t3, ns_accepted = 1, FF pair -> FTTF pair '''

            ls_out = []  # rev
            ls_in = []  # for
            rs_out = []  # for
            rs_in = []  # rev

            substring = sequence2[a1 - 40:a2 + 40]
            internal_oligo = []

            for oligo in oligo_list:
                bases = oligo.get("Bases").upper()
                if substring.find(bases) != -1:

                    j0 = sequence2.find(bases)
                    j1 = j0 + len(bases)

                    temp, [fpo, rpo] = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                    internal_oligo.append({'Name': oligo.get('Name'),
                                           'rf': 'f',
                                           'j0': j0,
                                           'j1': j1,
                                           'len': j1 - j0,
                                           'fpo': fpo,
                                           'rpo': rpo})

                    if j0 <= t0 and len(bases) >= min_assembly_oligolen:
                        ls_in.append(new_primer_0222('f', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name')))
                    elif j0 >= t2:
                        rs_out.append((new_primer_0222('f', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name'))))

                elif substring.find(reverse_complement(bases)) != -1:

                    j0 = sequence2.find(reverse_complement(bases))
                    j1 = j0 + len(bases)

                    temp, [fpo, rpo] = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                    internal_oligo.append({'Name': oligo.get('Name'),
                                           'rf': 'r',
                                           'j0': j0,
                                           'j1': j1,
                                           'len': j1 - j0,
                                           'fpo': fpo,
                                           'rpo': rpo})

                    if j1 >= t3 and len(bases) >= min_assembly_oligolen:
                        rs_in.append(new_primer_0222('r', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name')))
                    elif j1 <= t1:
                        ls_out.append((new_primer_0222('r', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name'))))
            print('internal_oligo', internal_oligo)
            #  Trim to one
            if len(ls_in) > 1:
                mylist = [x['j1'] for x in ls_in]
                target_index = mylist.index(max(mylist))
                ls_in = [ls_in[target_index]]

            if len(rs_in) > 1:
                mylist = [x['j0'] for x in rs_in]
                target_index = mylist.index(min(mylist))
                rs_in = [rs_in[target_index]]

            if len(ls_out) > 1:
                mylist = [x['j1'] for x in ls_out]
                target_index = mylist.index(max(mylist))
                ls_out = [ls_out[target_index]]

            if len(rs_out) > 1:
                mylist = [x['j0'] for x in rs_out]
                target_index = mylist.index(min(mylist))
                rs_out = [rs_out[target_index]]

            # Trim if incompatible
            if ls_in != [] and ls_out != []:
                fp = ls_in[0]
                rp = ls_out[0]
                temp, [fp_fpo, fp_rpo] = Calculate_fpo_and_rpo(sequence2, fp['j0'], fp['j1'], preset=0)
                temp, [rp_fpo, rp_rpo] = Calculate_fpo_and_rpo(sequence2, rp['j0'], rp['j1'], preset=0)
                if not rp['j1'] >= fp_fpo or fp['j0'] <= rp_rpo:
                    ls_out = []  # retain in primer first

            if rs_in != [] and rs_out != []:
                fp = rs_out[0]
                rp = rs_in[0]
                temp, [fp_fpo, fp_rpo] = Calculate_fpo_and_rpo(sequence2, fp['j0'], fp['j1'], preset=0)
                temp, [rp_fpo, rp_rpo] = Calculate_fpo_and_rpo(sequence2, rp['j0'], rp['j1'], preset=0)
                if not rp['j1'] >= fp_fpo or fp['j0'] <= rp_rpo:
                    rs_out = []  # retain in primer first

            # ls, rs, starting c0, c1
            if ls_in != []:
                p = ls_in[0]
                temp, [fpo, rpo] = Calculate_fpo_and_rpo(sequence2, p['j0'], p['j1'], preset=0)
                c0 = rpo
                c1 = p['j1']

                if ls_out != []:
                    ls = [ls_out[0], ls_in[0]]
                else:
                    ls = [new_primer_0222('r', t0, t1, sequence2, av=False), ls_in[0]]
            else:
                if ls_out != []:
                    p = ls_out[0]
                elif ls_out == []:
                    p = new_primer_0222('r', t0, t1, sequence2, av=False)
                temp, [fpo, rpo] = Calculate_fpo_and_rpo(sequence2, p['j0'], p['j1'], preset=0)
                c0 = rpo
                c1 = p['j1']
                ls = [p, None]

            if rs_in != []:
                p = rs_in[0]
                temp, [fpo, rpo] = Calculate_fpo_and_rpo(sequence2, p['j0'], p['j1'], preset=0)
                d0 = p['j0']
                d1 = fpo
                if rs_out != []:
                    rs = [rs_in[0], rs_out[0]]
                else:
                    rs = [rs_in[0], new_primer_0222('f', t2, t3, sequence2, av=False)]
            else:
                if rs_out != []:
                    p = rs_out[0]
                elif rs_out == []:
                    p = new_primer_0222('f', t2, t3, sequence2, av=False)

                temp, [fpo, rpo] = Calculate_fpo_and_rpo(sequence2, p['j0'], p['j1'], preset=0)
                d0 = p['j0']
                d1 = fpo
                rs = [None, p]

            if mutation_site is None or distance0 is None:
                Pairs = Calculate_all_po_pairs(sequence2, t0, t3, preset=1, ns_accepted=0)  # Pair = FF_pair, FTTF_pair
                Pairs += Calculate_all_po_pairs(sequence2, t0, t3, preset=1, ns_accepted=1)
            else:
                lst = Lst0(mutation_site)
                lst = [x for x in lst if x in range(a1, a2)]
                ga, gb, gc = finding_gap(lst, min_gaplen)
                print('gap ranges', gb)

                def filter_pairs_in_region(po_pairs, gb):
                    filtered_pairs = []
                    for j0, j1 in po_pairs:
                        match = [x for x in gb if j0 in x and j1 - 1 in x]
                        if len(match) > 0:
                            filtered_pairs.append([j0, j1])
                    return filtered_pairs

                FF_pairs, FTTF_pairs = Calculate_all_po_pairs(sequence2, t0, t3, preset=1, ns_accepted=0)
                FF_pairs0 = filter_pairs_in_region(FF_pairs, gb)
                FF_pairs1 = [x for x in FF_pairs if x not in FF_pairs0]
                FTTF_pairs0 = filter_pairs_in_region(FTTF_pairs, gb)
                FTTF_pairs1 = [x for x in FTTF_pairs if x not in FTTF_pairs0]

                FF_pairs2, FTTF_pairs2 = Calculate_all_po_pairs(sequence2, t0, t3, preset=1, ns_accepted=1)
                FF_pairs2 = [x for x in FF_pairs2 if x not in FF_pairs]
                FTTF_pairs2 = [x for x in FTTF_pairs2 if x not in FTTF_pairs]

                Pairs = [FF_pairs0, FF_pairs1, FTTF_pairs0, FTTF_pairs1, FF_pairs2, FTTF_pairs2]

            # for x in Pairs:
            #     print(x)

            next_rf = 'r'
            mid = []
            while c1 < d1:  # if c1 >= d1, no additional primer needed but it is unnlikely
                curser = c0 + max_primer_len
                # first check if direct stride to d1
                if curser >= d1:
                    j0 = c0
                    j1 = d1
                    potential_oligo = []
                    for oligo in internal_oligo:
                        if c0 >= oligo['j0'] and oligo['fpo'] <= curser and oligo[
                            'j1'] == d1:  # forward advance by 20 mer or more
                            potential_oligo.append(oligo)

                    if ls[1] is None and rs[0] is None:
                        print('contradict 0')
                        print('ls, mid, rs', ls, mid, rs)
                        return None, None, None

                    elif ls[1] is None and rs[0] is not None:
                        potential_oligo = [x for x in potential_oligo if x['rf'][0] == 'f']
                        if len(potential_oligo) > 0:
                            x = potential_oligo[0]
                            p = new_primer_0222('f', x['j0'], x['j1'], sequence2, av=True, oligo_name=x['Name'])
                        else:
                            p = new_primer_0222('f', j0, j1, sequence2, av=False)
                        ls[1] = p
                        # mid.append(p)
                        print('ls, mid, rs', ls, mid, rs)
                        return ls, mid, rs

                    elif ls[1] is not None and rs[0] is None:

                        potential_oligo = [x for x in potential_oligo if x['rf'][0] == 'r']
                        if len(potential_oligo) > 0:
                            x = potential_oligo[0]
                            p = new_primer_0222('r', x['j0'], x['j1'], sequence2, av=True, oligo_name=x['Name'])
                        else:
                            p = new_primer_0222('r', j0, j1, sequence2, av=False)

                        rs[0] = p
                        # mid.append(p)
                        print('ls, mid, rs', ls, mid, rs)
                        return ls, mid, rs
                    else:

                        if len(potential_oligo) > 0:
                            x = potential_oligo[0]
                            p = new_primer_0222(x['rf'], x['j0'], x['j1'], sequence2, av=True, oligo_name=x['Name'])
                        else:
                            p = new_primer_0222(next_rf, j0, j1, sequence2, av=False)
                        mid.append(p)
                        print('ls, mid, rs', ls, mid, rs)
                        return ls, mid, rs
                else:  # not final
                    potential_oligo = []
                    for oligo in internal_oligo:

                        # if oligo['fpo']<= curser and oligo['j1']-c1 >= min_advance:  # forward advance by 20 mer or more
                        if c0 >= oligo['j0'] and oligo['fpo'] <= curser and oligo[
                            'j1'] - c1 >= min_advance:  # forward advance by 20 mer or more
                            potential_oligo.append(oligo)
                    # print('curser', curser)
                    # print('potential oligo', potential_oligo)

                    if ls[1] is None:
                        # print('ls1 is none')
                        potential_oligo = [x for x in potential_oligo if x['rf'] == 'f']

                    if len(potential_oligo) > 0:
                        # mylist = [x['len'] for x in potential_oligo]
                        mylist = [x['j1'] for x in potential_oligo]
                        target_index = mylist.index(max(mylist))
                        oligo = potential_oligo[target_index]

                        # print('oligo',oligo)

                        p = new_primer_0222(oligo['rf'], oligo['j0'], oligo['j1'], sequence2, av=True,
                                            oligo_name=oligo['Name'])
                        next_rf = reverse_rf(oligo['rf'])
                        if ls[1] is None:
                            ls[1] = p
                            c0, c1 = oligo['rpo'], oligo['j1']
                            continue
                        else:
                            mid.append(p)
                            c0, c1 = oligo['rpo'], oligo['j1']
                            continue

                    # new stride
                    cycle_break = False
                    for i1 in range(len(Pairs)):
                        po_pair = Pairs[i1]
                        potential_pair = [x for x in po_pair if
                                          x[1] <= curser and x[
                                              1] - c1 >= min_advance]  # at least advance 20 in this cycle
                        if len(potential_pair) > 1:
                            mylist = [x[1] for x in potential_pair]
                            target_index = mylist.index(max(mylist))
                            potential_pair = [potential_pair[target_index]]

                        if potential_pair != []:
                            j0, j1 = potential_pair[0]
                            if ls[1] is None:
                                p = new_primer_0222('f', c0, j1, sequence2, av=False)
                                ls[1] = p
                                next_rf = 'r'
                                c0, c1 = j0, j1
                                cycle_break = True
                                break
                            else:
                                p = new_primer_0222(next_rf, c0, j1, sequence2, av=False)
                                mid.append(p)
                                next_rf = reverse_rf(next_rf)
                                c0, c1 = j0, j1
                                cycle_break = True
                                break
                    if cycle_break == False:
                        print('cycle terminate in between')
                        return
            # ref250829
            return ls, mid, rs

        def filter_pairs_in_region(po_pairs, gb):
            filtered_pairs = []
            for j0, j1 in po_pairs:
                match = [x for x in gb if j0 in x and j1 - 1 in x]
                if len(match) > 0:
                    filtered_pairs.append([j0, j1])
            return filtered_pairs

        gb = gb_parse0(gb_str)
        sequence = origin_parse0(gb['ORIGIN']).upper()
        sequence2 = sequence + sequence

        if scenario is None:
            scenario = list(range(8))
        elif isinstance(scenario, int):
            scenario = [scenario]
        elif isinstance(scenario, list):
            scenario = scenario

        link_info = []

        for i in range(len(segment_info)):
            # print(f'\n------------------------------------------------------------ Link{i}')
            seg0 = segment_info[i - 1]
            seg1 = segment_info[i]

            t = [seg0["rpbs_ind"][0], seg0["rpbs_ind"][1], seg1["fpbs_ind"][0], seg1["fpbs_ind"][1]]
            t = [x % len(sequence) for x in t]
            t0, t1, t2, t3 = t
            print('t', t)

            a = [t0,
                 max(seg0["segment_range"]) + 1,
                 seg1["segment_starting_index"],
                 t3]
            a = [x % len(sequence) for x in a]
            a0, a1, a2, a3 = a

            substring = sequence2[a1 - 40:a2 + 40]

            fps = []
            rps = []

            for oligo in oligo_list:
                bases = oligo.get("Bases").upper()
                # print(reverse_complement(bases))
                if substring.find(bases) != -1:
                    # print('potential fp')
                    j0 = sequence2.find(bases)
                    j1 = j0 + len(bases)
                    # print('j0,j1', j0, j1)
                    # if j1 > a2: # no variations to the right of the forward primer
                    if j1 >= t3 - 1:
                        fps.append(new_primer_0222('f', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name')))

                elif substring.find(reverse_complement(bases)) != -1:
                    # print('potential rp', oligo.get("Name"))
                    j0 = sequence2.find(reverse_complement(bases))
                    j1 = j0 + len(bases)

                    # print('j0',j0)
                    # print('t0', t0)
                    # if j0 < a[1]:  # no variations to the left of the reverse primer
                    if j0 <= t0 + 1:
                        # print('append')

                        rps.append(new_primer_0222('r', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name')))

            '''
            if two forward primers found, take the one with smallest j0
            if two reverse primers found, take the one with the largest j1
            if both a forward primer and a reverse primer is available, check if they overlap by min_overlap_length,
                if not, retain the longer primer.
            '''

            if len(fps) > 1:
                j0_list = [x['j0'] for x in fps]
                target_index = j0_list.index(min(j0_list))
                fps = [fps[target_index]]

            if len(rps) > 1:
                j1_list = [x['j1'] for x in rps]
                target_index = j1_list.index(max(j1_list))
                rps = [rps[target_index]]

            if fps != [] and rps != []:
                fp = fps[0]
                rp = rps[0]

                temp, [fp_fpo, fp_rpo] = Calculate_fpo_and_rpo(sequence2, fp['j0'], fp['j1'], preset=preset)
                temp, [rp_fpo, rp_rpo] = Calculate_fpo_and_rpo(sequence2, rp['j0'], rp['j1'], preset=preset)

                if rp['j1'] >= fp_fpo - 1 or fp['j0'] <= rp_rpo + 1:
                    print('scenario 1\n\tuse existing forward and reverse primer')
                    print_linking_primers([rp, fp])
                    link_info.append([rp, fp])
                    continue

                else:
                    cost0 = fp_fpo - t0  # cost when keep fp
                    cost1 = t3 - rp_rpo  # cost when keep rp
                    if cost0 < cost1:
                        rps = []
                    else:
                        fps = []

            # print('trimmed fps, rps', fps, rps)

            ''' in case the retained primer require that the other primer be larger than opc_oligo len, redesign the two '''

            if fps != [] and rps == [] and (2 in scenario):
                fp = fps[0]
                temp, [fp_fpo, fp_rpo] = Calculate_fpo_and_rpo(sequence2, fp['j0'], fp['j1'], preset=preset)
                # temp, [rp_fpo, rp_rpo] = Calculate_fpo_and_rpo(sequence2, rp['j0'], rp['j1'], preset=preset)

                if fp_fpo - t0 > max_primer_len:
                    print('forward primer available but unused')
                    fps = []
                else:
                    # create rp, mission done
                    j0 = t0
                    j1 = fp_fpo
                    rp = new_primer_0222('r', j0, j1, sequence2, av=False)

                    print('scenario 2\n\tuse existing forward primer')
                    print_linking_primers([rp, fp])
                    link_info.append([rp, fp])
                    continue

            elif rps != [] and fps == [] and (3 in scenario):
                rp = rps[0]
                # temp, [fp_fpo, fp_rpo] = Calculate_fpo_and_rpo(sequence2, fp['j0'], fp['j1'], preset=preset)
                temp, [rp_fpo, rp_rpo] = Calculate_fpo_and_rpo(sequence2, rp['j0'], rp['j1'], preset=preset)

                if t3 - rp_rpo > max_primer_len:
                    print('reverse primer available but unused')
                    rps = []
                else:
                    # create fp, mission done
                    j1 = t3
                    j0 = rp_rpo
                    fp = new_primer_0222('f', j0, j1, sequence2, av=False)

                    print('scenario 3\n\tuse existing reverse primer')
                    print_linking_primers([rp, fp])
                    link_info.append([rp, fp])
                    continue

            ''' to design two new primers, ideally, allow overlap on either sides, that is, t0~t1 or t2~t3'''
            # print('design two new primers')
            temp, [ls_fpo, ls_rpo] = Calculate_fpo_and_rpo(sequence2, t0, t1, preset=preset)
            temp, [rs_fpo, rs_rpo] = Calculate_fpo_and_rpo(sequence2, t2, t3, preset=preset)

            print('left side rpo', ls_rpo)
            print('right side fpo', rs_fpo)

            # print('ls_fpo, ls_rpo', ls_fpo, ls_rpo)
            # print('rs_fpo, rs_rpo', rs_fpo, rs_rpo)
            if t3 - ls_rpo <= max_primer_len and (
                    4 in scenario):  # try extend the forward primer and overlap to the left of target region
                j0 = t0
                j1 = t1
                rp = new_primer_0222('r', j0, j1, sequence2, av=False)

                j0 = ls_rpo
                j1 = t3
                fp = new_primer_0222('f', j0, j1, sequence2, av=False)
                print('scenario 4\n\tBoth primers new, overlap to the left of the target region')
                print_linking_primers([rp, fp])
                link_info.append([rp, fp])
                continue

            elif rs_fpo - t0 <= max_primer_len and (
                    5 in scenario):  # try extend the reverse primer and overlap to the right of the target region
                j0 = t2
                j1 = t3
                fp = new_primer_0222('f', j0, j1, sequence2, av=False)

                j0 = t0
                j1 = rs_fpo
                rp = new_primer_0222('r', j0, j1, sequence2, av=False)

                print('scenario 5\n\tBoth primers new, overlap to the right of the target region')
                print_linking_primers([rp, fp])
                link_info.append([rp, fp])
                continue

            ''' to design two new primers,
            a. allow overlap within t1 ~ t2, ns_accepted = 0, FF pair
            b. allow overlap within t0 ~ t3, ns_accepted = 0, FF pair
            c. allow overlap within t1 ~ t2, ns_accepted = 0, FTTF pair
            b. allow overlap within t0 ~ t3, ns_accepted = 0, FTTF pair
            e./f.  allow overlap within t0 ~ t3, ns_accepted = 1, FF pair -> FTTF pair '''

            # print(mutation_site)
            lst = Lst0(mutation_site)

            lst = [x for x in lst if x in range(a1, a2)]

            ga, gb, gc = finding_gap(lst, min_gaplen)

            FF_pairs, FTTF_pairs = Calculate_all_po_pairs(sequence2, t0, t3, preset=preset, ns_accepted=0)
            FF_pairs0 = filter_pairs_in_region(FF_pairs, gb)
            FF_pairs1 = [x for x in FF_pairs if x not in FF_pairs0]
            FTTF_pairs0 = filter_pairs_in_region(FTTF_pairs, gb)
            FTTF_pairs1 = [x for x in FTTF_pairs if x not in FTTF_pairs0]

            FF_pairs2, FTTF_pairs2 = Calculate_all_po_pairs(sequence2, t0, t3, preset=preset, ns_accepted=1)
            FF_pairs2 = [x for x in FF_pairs2 if x not in FF_pairs]
            FTTF_pairs2 = [x for x in FTTF_pairs2 if x not in FTTF_pairs]

            six_pairs = [FF_pairs0, FF_pairs1, FTTF_pairs0, FTTF_pairs1, FF_pairs2, FTTF_pairs2]
            # for x in six_pairs:
            #     print(x)

            found = False
            for i1 in range(6):
                pairs = six_pairs[i1]
                for (k0, k1) in pairs:
                    if t3 - k0 <= max_primer_len and k1 - t0 <= max_primer_len:
                        fp = new_primer_0222('f', k0, t3, sequence2, av=False)
                        rp = new_primer_0222('r', t0, k1, sequence2, av=False)
                        print(f'six_pair {i1} for homology cloning', pairs)
                        print('scenario 6_{}\n\tBoth primers new, overlap within target region'.format(i1))
                        print_linking_primers([rp, fp])
                        link_info.append([rp, fp])
                        found = True
                        break

                if found == True:
                    break

            ''' update oligo list '''

            if found == False:
                print('scenario 7\n\ttry primer walk')
                ls, mid, rs = primer_walk_HotF(sequence2, t, a, oligo_list=oligo_list,
                                               mutation_site=mutation_site)

                print_linking_primers(ls + mid + rs)
                link_info.append(ls + mid + rs)
            print(link_info[-1])

        return link_info

    def print_linking_primers(list_of_primers, do_print=False):
        if do_print == False:
            return
        for p in list_of_primers:
            print('\n---------------------------')
            for key, value in p.items():
                print(f'{key}:   {value}')
        return

    def Linking_seg_GG_250828(gb_str, segment_info, oligo_list=[],
                              IIS_site='GGTCTC', IIS_prefix='aaGGTCTCn', IIS_side=['l', 'r'],
                              N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
                              IIS_throw=5, max_gg_primer_len=60, max_primer_len=60, min_overlap=14,
                              # this row is set
                              min_advance=10, ideal_advance=25, min_linking_primer_len=18,  # this row is set
                              ):
        # modified from Linking_seg

        ''' adhesive side:
        l: only on the left
        r: only on the right
        f: either on the left or right
        u: unspecified, could even be in the middle of the mutation region
        IIS_throw = 0: demand that the adhesive region adjoin the target site
        IIS_throw = 4: allow the adhesive region to be 0~ 4-nt apart from the target site

        max_gg_primer_len include the 9-nt 5' prefix encoding the TypeIIs site
        max_primer_len = 60

        modified on 250901, check for eligible annealing region before designing
        store frpo pairs for reuse'''

        IIS_prefix_len = len(IIS_prefix)

        def pick_a_po_pair(pairs1, pairs2, pairs3, a, b,
                           extreme='left'):  # where a is left_boundary, b is right_boundary

            pairs1 = [x for x in pairs1 if x[0] >= a and x[1] <= b]
            pairs2 = [x for x in pairs2 if x[0] >= a and x[1] <= b]
            pairs3 = [x for x in pairs3 if x[0] >= a and x[1] <= b]

            pairs2 = pairs2 if pairs2 else pairs3
            pairs = pairs1 if pairs1 else pairs2

            if pairs:
                if extreme == 'left':
                    pr = min(pairs, key=lambda l: l[0])
                else:
                    pr = max(pairs, key=lambda l: l[1])
                return pr
            elif b - a < 30:
                return [a, b]

            else:
                return

        def linkage_cost(RPS, FPS, IIS_prefix_len):
            ''' linkage is a sublist in wrapper0 '''
            cost = 0
            for i in range(len(RPS)):
                p = RPS[i]
                if p['av'] == False:
                    cost += p['len']
                    if i == 0:
                        cost += IIS_prefix_len
            for i in range(len(FPS)):
                p = FPS[i]
                if p['av'] == False:
                    cost += p['len']
                    if i == 0:
                        cost += IIS_prefix_len
            return cost

        gb = gb_parse0(gb_str)
        sequence = origin_parse0(gb['ORIGIN']).upper()
        sequence2 = sequence + sequence

        if isinstance(IIS_side, str):
            IIS_side = [IIS_side for i in range(len(segment_info))]

        elif (isinstance(IIS_side, list)) and (len(IIS_side) < len(segment_info)):
            IIS_side = ['u' for i in range(len(segment_info))]
            print(f"(len(IIS_side) < len(segment_info)), use default IIS_side = {IIS_side}")

        ''' wrapper0 is a list of lists the length of which = len(segment); 
        1st layer expanded: per segment
        2nd layer expanded: primer pairs considered : [fp/rp/(rp,fp)/None, annealing_start_position, annealing_candidates]
        '''

        ''' 250829 new indicator wrapper0 is a list of lists the length of which = len(segment); 
              each element in the 1st layer correspond to a segment
              each element in the 2nd layer correspond to an adhesive site [j0, gg primers, full-match primers, total cost]
              '''

        wrapper0 = []
        link_ts = []
        for i in range(len(segment_info)):
            aside = IIS_side[i]
            wrapper0.append([])
            # print(f'\n------------------------------------------------------------ Link{i}')
            seg0 = segment_info[i - 1]
            seg1 = segment_info[i]

            t = [seg0["rpbs_ind"][0], seg0["rpbs_ind"][1], seg1["fpbs_ind"][0], seg1["fpbs_ind"][1]]
            t = [x % len(sequence) for x in t]
            t0, t1, t2, t3 = t
            # print('t', t)
            link_ts.append(t)

            pairs1, pairs2 = Calculate_all_po_pairs(sequence2, t0, t3, anywayanyway=False)
            _, pairs3 = Calculate_all_po_pairs(sequence2, t0, t3, anywayanyway=True)

            # for each segment, there will be n adhesive site choice. Design full-match or GG primer per adhesive site
            # Collect full-match primers

            full_match = []
            for oligo in oligo_list:
                bases = oligo.get("Bases").upper()
                if len(bases) >= min_linking_primer_len:
                    if sequence2[t0 - 10:t3 + 10].find(bases) != -1:  # forward
                        j0 = sequence2.find(bases)
                        j1 = j0 + len(bases)
                        p = new_primer_0222('f', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name'))
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        full_match.append(p)

                    elif sequence2[t0 - 10:t3 + 10].find(reverse_complement(bases)) != -1:
                        j0 = sequence2.find(reverse_complement(bases))
                        j1 = j0 + len(bases)
                        p = new_primer_0222('r', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name'))
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        full_match.append(p)

            gg_forward = []
            gg_reverse = []
            for oligo in oligo_list:
                bases0 = oligo.get("Bases").upper()
                bases = ''
                if IIS_site.upper() in bases0[1:]:
                    bases = bases0.split(IIS_site)[1][1:]

                    if sequence2[t0 - 10: t3 + 10].find(bases) != -1:
                        j0 = sequence2.find(bases)
                        j1 = j0 + len(bases)
                        p = new_primer_0222('f', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name'))
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        gg_forward.append(p)


                    elif sequence2[t0 - 10: t3 + 10].find(reverse_complement(bases)) != -1:
                        j0 = sequence2.find(reverse_complement(bases))
                        j1 = j0 + len(bases)
                        p = new_primer_0222('r', j0, j1, sequence2, av=True, oligo_name=oligo.get('Name'))
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        gg_reverse.append(p)

            # print('gg_forward av', gg_forward)
            # print('gg_reverse av', gg_reverse)

            # here, iterate over all eligible adhesive site and design primer essemble for each adhesive site

            k = int(aside[1:]) if len(aside) > 1 else IIS_throw
            u_to_f = (max(t2 - t0, t3 - t1) + IIS_throw + len(IIS_prefix) <= max_gg_primer_len)

            if aside[0] == 'l':
                k0_range = list(range(t1 - 4, t1 - 5 - k, -1))
            elif aside[0] == 'r':
                k0_range = list(range(t2, t2 + k + 1))
            elif aside[0] == 'f':
                k0_range = list(range(t1 - 4, t1 - 5 - k, -1)) + list(range(t2, t2 + k + 1))

            elif aside[0] == 'u' and u_to_f:
                k0_range = list(range(t1 - 4, t1 - 5 - k, -1)) + list(range(t2, t2 + k + 1))

            elif aside[0] == 'u':
                k0_range = list(range(t1 - 4 - k, t2 + k + 1))

            # iterate over each adhesive site

            for k0 in k0_range:
                # print(k0)
                k1 = k0 + 4

                ''' Walk toward left, check for available or create new gg_reverse '''
                ''' First check for 
                        o. available gg primer (take the largest stride)
                    Before creating new gg primer, check for
                        a. availalbe next linking primer (take the smallest stride)
                        b. if one can reach in one stride, if one cannot,
                        c. stay ideal_advance nt away from desitnation'''
                RPS = []
                while RPS == []:
                    # o. available gg_rp primer (take the largest stride)
                    av = []
                    for p in gg_reverse:
                        if p['j1'] == k1:
                            av.append(p)
                    gg_rp = min(av, key=lambda d: d['j0']) if av else None
                    if len(av) > 1:
                        print(f"{gg_rp['oligo_name']} chosen among {[(x['oligo_name'], x['seq']) for x in av]}")
                    if gg_rp:
                        RPS.append(gg_rp)
                        continue

                    #  a. availalbe next linking primer (take the smallest stride)
                    av = []
                    for p in full_match:
                        if p['rpo'] >= k1 - (max_gg_primer_len - IIS_prefix_len) and p['j1'] <= k1:
                            av.append(p)
                    nextp = max(av, key=lambda d: d['rpo']) if av else None
                    if nextp is not None:
                        j0, j1 = nextp['rpo'], k1
                        p = new_primer_0222('r', j0, j1, sequence2)
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        gg_rp = p
                        RPS.append(gg_rp)
                        RPS.append(nextp)
                        continue
                    #  b. if one can reach in one stride, if one cannot,
                    #  c. stay ideal_advance nt away from desitnation
                    if k1 - t0 <= max_gg_primer_len - IIS_prefix_len:
                        j0 = t0
                        j1 = k1
                        p = new_primer_0222('r', j0, j1, sequence2)
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        gg_rp = p
                        RPS.append(gg_rp)
                        continue

                    else:

                        # left (a) & right (b) bound
                        a, b = max(t0 + ideal_advance, k1 - (max_gg_primer_len - IIS_prefix_len)), k1
                        pr = pick_a_po_pair(pairs1, pairs2, pairs3, a, b, 'left')
                        j0, j1 = pr[0], k1
                        p = new_primer_0222('r', j0, j1, sequence2)
                        p['fpo'] = pr[1]
                        _, (_, p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        gg_rp = p
                        RPS.append(gg_rp)
                RPS[0]['ggprimer'] = True

                ''' Walk toward left, finish the primer walk'''
                ''' First check for 
                        o. available current linking primer (take the largest stride)
                    Before creating new linking primer, check for
                        a. availalbe next linking primer (take the smallest stride)
                        b. if one can reach in one stride, if one cannot,
                        c. stay ideal_advance nt away from desitnation'''

                while RPS[-1]['j0'] > t0 + 3:
                    #  o. available current linking primer (take the largest stride)
                    lastp = RPS[-1]
                    av = []
                    for p in full_match:
                        # if p['rpo'] >= lastp['j0'] and p['j0'] <= lastp['j0'] - min_advance:
                        if p['j1'] - lastp['j0'] >= min_overlap and p['j0'] <= lastp['j0'] - min_advance:
                            av.append(p)
                    p = min(av, key=lambda d: d['j0']) if av else None
                    if p:
                        RPS.append(p)
                        continue

                    #  a. availalbe next linking primer (take the smallest stride)
                    av = []
                    for p in full_match:
                        if p['rpo'] >= lastp['fpo'] - max_primer_len and \
                                p['j0'] <= lastp['j0'] - 2 * min_advance:
                            av.append(p)
                    nextp = max(av, key=lambda d: d['rpo']) if av else None
                    if nextp is not None:
                        j0, j1 = nextp['rpo'], lastp['fpo']
                        p = new_primer_0222('r', j0, j1, sequence2)
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        RPS.append(p)
                        RPS.append(nextp)
                        continue

                    #  b. if one can reach in one stride, if one cannot,
                    #  c. stay ideal_advance nt away from desitnation
                    if lastp['fpo'] - t0 <= max_primer_len:
                        j0, j1 = t0, lastp['fpo']
                        p = new_primer_0222('r', j0, j1, sequence2)
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        RPS.append(p)
                        continue

                    else:
                        # left (a) & right (b) bound
                        a, b = max(t0 + ideal_advance, lastp['fpo'] - max_primer_len), lastp['fpo']
                        pr = pick_a_po_pair(pairs1, pairs2, pairs3, a, b, 'left')
                        j0, j1 = pr[0], lastp['fpo']
                        p = new_primer_0222('r', j0, j1, sequence2)
                        p['fpo'] = pr[1]
                        _, (_, p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        RPS.append(p)
                for p in RPS:
                    p["side"] = 'rps'

                ''' Walk toward right, check for available or create new gg_forward '''
                ''' First check for 
                        o. available gg primer (take the largest stride)
                    Before creating new gg primer, check for
                        a. availalbe next linking primer (take the smallest stride)
                        b. if one can reach in one stride, if one cannot,
                        c. stay ideal_advance nt away from desitnation'''

                FPS = []
                while FPS == []:
                    # o. available gg_fp primer (take the largest stride)
                    av = []
                    for p in gg_forward:
                        # print(p)
                        if p['j0'] == k0:
                            av.append(p)
                    gg_fp = max(av, key=lambda d: d['j1']) if av else None
                    if len(av) > 1:
                        print(f"{gg_fp['oligo_name']} chosen among {[(x['oligo_name'], x['seq']) for x in av]}")
                    if gg_fp:
                        FPS.append(gg_fp)
                        continue

                    #  a. availalbe next linking primer (take the smallest stride)
                    av = []
                    for p in full_match:
                        if p['fpo'] <= k0 + (max_gg_primer_len - IIS_prefix_len) and p['j0'] >= k0:
                            av.append(p)
                    nextp = min(av, key=lambda d: d['fpo']) if av else None
                    if nextp is not None:
                        j0, j1 = k0, nextp['fpo']
                        p = new_primer_0222('f', j0, j1, sequence2)
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        gg_fp = p
                        FPS.append(gg_fp)
                        FPS.append(nextp)
                        continue

                    #  b. if one can reach in one stride, if one cannot,
                    #  c. stay ideal_advance nt away from desitnation
                    if t3 - k0 <= max_gg_primer_len - IIS_prefix_len:
                        j0 = k0
                        j1 = t3
                        p = new_primer_0222('f', j0, j1, sequence2)
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        gg_fp = p
                        FPS.append(gg_fp)
                        continue

                    else:
                        # left (a) & right (b) bound
                        a, b = k0, min(t3 - ideal_advance, k0 + (max_gg_primer_len - IIS_prefix_len)),
                        # print('pairs1', pairs1)
                        # print('pairs2', pairs2)
                        # print(f'{pairs3} , {a}, {b}')
                        pr = pick_a_po_pair(pairs1, pairs2, pairs3, a, b, 'right')
                        j0, j1 = k0, pr[1]
                        p = new_primer_0222('f', j0, j1, sequence2)
                        p['rpo'] = pr[0]
                        _, (p['fpo'], _) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        gg_fp = p
                        FPS.append(gg_fp)
                FPS[0]['ggprimer'] = True

                ''' Walk toward right, finish the primer walk'''
                ''' First check for 
                        o. available current linking primer (take the largest stride)
                    Before creating new linking primer, check for
                        a. availalbe next linking primer (take the smallest stride)
                        b. if one can reach in one stride, if one cannot,
                        c. stay ideal_advance nt away from desitnation'''

                while FPS[-1]['j1'] < t3 - 3:
                    #  o. available current linking primer (take the largest stride)
                    lastp = FPS[-1]
                    av = []
                    for p in full_match:
                        # if p['fpo'] <= lastp['j1'] and p['j1'] >= lastp['j1'] + min_advance:
                        if lastp['j1'] - p['j0'] >= min_overlap and p['j1'] >= lastp['j1'] + min_advance:
                            av.append(p)
                    p = max(av, key=lambda d: d['j1']) if av else None
                    if p:
                        FPS.append(p)
                        continue

                    #  a. availalbe next linking primer (take the smallest stride)
                    av = []
                    for p in full_match:
                        if p['fpo'] <= lastp['rpo'] + max_primer_len and \
                                p['j1'] >= lastp['j1'] + 2 * min_advance:
                            av.append(p)
                    nextp = min(av, key=lambda d: d['fpo']) if av else None
                    if nextp is not None:
                        j0, j1 = lastp['rpo'], nextp['fpo']
                        p = new_primer_0222('f', j0, j1, sequence2)
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        FPS.append(p)
                        FPS.append(nextp)
                        continue

                    #  b. if one can reach in one stride, if one cannot,
                    #  c. stay ideal_advance nt away from desitnation
                    if t3 - lastp['rpo'] <= max_primer_len:
                        j0, j1 = lastp['rpo'], t3
                        p = new_primer_0222('f', j0, j1, sequence2)
                        _, (p['fpo'], p['rpo']) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        FPS.append(p)
                        continue

                    else:
                        # left (a) & right (b) bound
                        a, b = lastp['rpo'], min(t3 - ideal_advance, lastp['rpo'] + max_primer_len),
                        pr = pick_a_po_pair(pairs1, pairs2, pairs3, a, b, 'right')
                        j0, j1 = lastp['rpo'], pr[1]
                        p = new_primer_0222('f', j0, j1, sequence2)
                        p['rpo'] = pr[0]
                        _, (p['fpo'], _) = Calculate_fpo_and_rpo(sequence2, j0, j1, preset=1)
                        FPS.append(p)
                for p in FPS:
                    p["side"] = 'fps'

                wrapper0[-1].append([k0,
                                     sequence2[k0: k1],
                                     RPS,
                                     FPS,
                                     linkage_cost(RPS, FPS, IIS_prefix_len)])

        ''' 
        Store the linking-site-wise annealing-end combinations (called a design) that pass a certain threshold. 
        Design primers for each design. 
        Calculate cost for each design and choose the cheapest one
        '''
        indexed_lists = [[(i, val) for i, val in enumerate(sublist)] for sublist in wrapper0]
        # print('indexed_lists len', len(indexed_lists))
        # for x in indexed_lists:
        #     print('sublist len', len(x))
        #     for y in x:
        #         print(y)
        Designs = []
        k = 0
        # print('GC_threshold', GC_threshold)
        for combo in itertools.product(*indexed_lists):

            # indexes = [idx for idx, val in combo]
            values = [val for idx, val in combo]
            list_of_str = [val[1] for val in values]

            Y = choose_golden_gate(list_of_str, N_match_cutoff, YR_match_cutoff, GC_threshold,
                                   print_out=False)
            if len(Y) > 0:  # pass
                cost = 0
                link_info = []
                for i in range(len(values)):  # per linkage  = len(link_ts) = len(link_info)
                    _, _, RPS, FPS, c = values[i]

                    # linking_p = RPS[1:] + FPS[1:]
                    cost += c

                    # x = [RPS[0]] + linking_p + [FPS[0]]
                    x = RPS + FPS[::-1]
                    link_info.append(x)

                entry = {
                    "idx": k,
                    "anneal_info": values,
                    "GG_combo": Y[0],
                    "link_info": link_info,
                    "cost": cost,
                    "Y": Y[0]
                }
                Designs.append(entry)
                k += 1

        # print('Designs', Designs)
        if Designs:
            selected_design = min(Designs, key=lambda x: x['cost'])
            print(f'Golden gate annealing region analyses: {selected_design["Y"]}')
            return selected_design['link_info']
        else:
            print('''
    No compatible annealing regions found. Try to relax the golden gate parameters by 
        increasing N_match_cutoff (e.g., 2 -> 3)
        ''')
            return None

    def create_pcr_fragment(sequence, mutation_site, locus='',
                            distance0=50, circular=True, verbose=True  # this row is setv
                            ):

        '''
        The mutation_site can be an integer, a range, a list of integers, or a list of ranges
        Group mutation_site within distance0 to each other so as to avoid internal primers that requier 2-step PCR.
         '''

        def second_level_walk_and_handshake(seg, distance0=50):
            new_seg = []
            i = 0
            while i < len(seg):
                a = seg[i].start
                j = len(seg) - i - 1
                while j > 0:
                    b = seg[i + j].stop
                    if b - a < distance0:
                        break
                    else:
                        j -= 1
                if j > 0:
                    new_seg.append(range(a, b))
                else:
                    new_seg.append(seg[i])
                i += 1
                i += j

            new_seg_flatten = [x for y in new_seg for x in y]
            return new_seg, new_seg_flatten

        lst0 = Lst0(mutation_site)
        if lst0 is None:
            return

        group, seg0, seg_flatten0 = group_integers_within_distance(lst0, 1)

        seg, seg_flatten = second_level_walk_and_handshake(seg0, distance0)

        print(f'\n{"=" * 80}Cloning design {locus}')
        if seg0 != seg:
            print(f'initial mutation_site: {seg0}')
        print(f'grouped mutation_sites: {seg}')

        lst2 = [x for x in range(len(sequence)) if x not in seg_flatten]
        group2, seg2, seg2_flatten = group_integers_within_distance(lst2, 1)
        # print(group2, seg2, seg2_flatten)
        # print(f'cloning_fragment_index {seg2}')

        # extract sequence of seg2
        frag2 = []
        for seg in seg2:
            current_frag = ''
            for i in seg:
                current_frag += sequence[i]
            frag2.append(current_frag)

        if circular == True:
            frag2[-1] += frag2[0]
            frag2 = frag2[1:]

            seg2[-1] = range(min(seg2[-1]), max(seg2[-1]) + 1 + max(seg2[0]) + 1)
            seg2 = seg2[1:]
            # print(len(seg2[-1]))

        return frag2, seg2, len(sequence), lst0

    def Create_primer_binding_site(gb_str, mutation_site, oligo_list=[], preset=1, verbose=True):
        gb = gb_parse0(gb_str)
        features = feature_parse0(gb['FEATURES'])
        sequence = origin_parse0(gb['ORIGIN']).lower()
        locus = extract_gb_locus(gb_str)
        sequence2 = sequence + sequence
        # print(sequence)

        fragment, f_index, sequence_total_len, lst0 = create_pcr_fragment(sequence, mutation_site, locus,
                                                                          verbose=verbose)
        segment_info = []

        for i in range(len(fragment)):
            if verbose:  print('------------------------------------------------------------ Fragment{}'.format(i))
            f = fragment[i].lower()
            id0 = min(f_index[i])

            left_primer = None
            right_primer = None

            primers, df = Primer3_design(f, mode=1, seq_id=i, primer_pick_anyway=0,
                                         left_primer=left_primer, right_primer=right_primer,
                                         preset=preset, verbose=verbose)
            # print('primers', primers)
            if primers['PRIMER_PAIR'] == []:
                if verbose: print('primer_pick_anyway')
                primers, df = Primer3_design(f, mode=1, seq_id=i, primer_pick_anyway=1,
                                             left_primer=left_primer, right_primer=right_primer,
                                             preset=preset, verbose=verbose)

            # print(primers)
            # print(df.to_string())

            def select_one(df):
                Score = []
                # print(type(df))
                for i in range(df.shape[0]):
                    s = (
                            max(df.at[i, 'F_any'] - 6, 1) *
                            max(df.at[i, 'F_end'] - 4, 1) *
                            max(df.at[i, 'R_any'] - 6, 1) *
                            max(df.at[i, 'R_end'] - 4, 1) *
                            max(df.at[i, 'pair_any'] - 4, 1) *
                            max(df.at[i, 'pair_end'] - 2, 1)
                    )
                    Score.append(s)
                # print(Score)
                return Score.index(min(Score))

            selected = select_one(df)
            if verbose: print('selected pair id', selected)

            segment_info.append(
                {"fpbs_ind": [df.at[selected, 'F_start'] + id0,
                              df.at[selected, 'F_start'] + df.at[selected, 'F_len'] + id0],
                 "rpbs_ind": [df.at[selected, 'R_start'] - df.at[selected, 'R_len'] + 1 + id0,
                              df.at[selected, 'R_start'] + 1 + id0],
                 "left_primer_available": left_primer,
                 "right_primer_available": right_primer,
                 "segment_seq": f,
                 "segment_starting_index": id0,
                 "segment_len": len(f),
                 "segment_range": range(id0, id0 + len(f))
                 }
            )
        return segment_info

    def new_primer_0222(rf, j0, j1, sequence2, av=False, oligo_name=None):
        if rf == 'f':

            return {'rf': 'f',
                    'av': av,
                    'oligo_name': oligo_name,
                    'j0': j0,
                    'j1': j1,
                    'len': j1 - j0,
                    'ind_range': range(j0, j1),
                    'seq': sequence2[j0:j1].upper()
                    }

        else:
            return {'rf': 'r',
                    'av': av,
                    'oligo_name': oligo_name,
                    'j0': j0,
                    'j1': j1,
                    'len': j1 - j0,
                    'ind_range': range(j0, j1),
                    'seq': reverse_complement(sequence2[j0:j1])
                    }

    def primer_end_without_ns(seq):
        seq = seq.upper()
        a = 0
        for i in range(len(seq) - 1, -1, -1):
            x = seq[i]
            if x not in ['A', 'T', 'C', 'G']:
                return seq[i + 1:]

        return seq

    if not check_against_IIS_site(gb_str, IIS_site): return None, None, None

    gb = gb_parse0(gb_str)
    sequence = origin_parse0(gb['ORIGIN']).upper()
    sequence2 = sequence + sequence

    seq_len = len(sequence)
    locus_name = gb["LOCUS"][12:35].rstrip()
    definition = extract_gb_elements(gb_str, header='DEFINITION')

    primer_note = 'designed on {} for construction of {}'.format(current_date_gb(), locus_name)

    gb_str = filter_feature(gb_str, remove='source')
    gb_str = filter_feature(gb_str, remove='primer', by='type')

    seg_info = Create_primer_binding_site(gb_str, mutation_site, oligo_list, preset=preset, verbose=verbose)

    # print('seg_info', seg_info)

    if cloning_method in [0, 'HotF']:
        link_info = linking_seg_HotF_0223(gb_str=gb_str, segment_info=seg_info, mutation_site=mutation_site,
                                          oligo_list=oligo_list)
    elif cloning_method == 'GG':
        link_info = Linking_seg_GG_250828(gb_str, seg_info, oligo_list,
                                          IIS_site, IIS_prefix, IIS_side,
                                          N_match_cutoff, YR_match_cutoff, GC_threshold)
        if link_info is None:
            return None, None, None

    list_of_text = [p['Name'] for p in oligo_list]
    j0 = find_latest_int(list_of_text, prefix=oligo_prefix) + 1
    next_name = oligo_prefix + str(j0).rjust(2, '0')

    # Update the oligo list with newly named oligos, create gb file with primers annotated
    cost = 0
    link_info2 = []
    oligo_list2 = oligo_list
    for x in link_info:
        link_info2.append([])

        for p in x:
            # print(p)
            if p['av'] == True:
                p2 = p
                link_info2[-1].append(p2)
            else:
                p2 = p
                p2['oligo_name'] = next_name
                link_info2[-1].append(p2)

                j0 += 1
                next_name = oligo_prefix + str(j0).rjust(2, '0')

                # update oligo list
                if cloning_method == 'GG' and p.get('ggprimer', False):  # appending GG mer without changing j0 j1
                    if IIS_prefix[-1].lower() == 'n':
                        if p2['rf'] == 'f':
                            append = IIS_prefix[:-1].lower() + reverse_complement(sequence2[p2['j0'] - 1]).lower()
                        else:
                            append = IIS_prefix[:-1].lower() + sequence2[p2['j1']].lower()
                    else:
                        append = IIS_prefix

                    oligo_list2.append({
                        'Name': p2['oligo_name'],
                        'Length': p2['len'] + len(append),
                        'Bases': append + p2['seq'],
                        'Note': primer_note
                    })
                    cost += p2['len'] + len(append)
                else:
                    oligo_list2.append({
                        'Name': p2['oligo_name'],
                        'Length': p2['len'],
                        'Bases': p2['seq'],
                        'Note': primer_note
                    })
                    cost += p2['len']
                # print('appended', p2['oligo_name'])
            gb_str = gb_add_feature(gb_str, p2['j0'], p2['j1'], p2['rf'], 'primer', p2['oligo_name'])
    if verbose: print(f'new primer cost: total {cost} nt')

    # Update the gb file with mutation sites

    if isinstance(mutation_site_label, str):
        mutation_site_label = mutation_site_label.split(',')
        mutation_site_label = [x.lstrip() for x in mutation_site_label]

    if not all(isinstance(item, range) for item in mutation_site):
        mutation_site = Lst0(mutation_site)
        mutation_site = group_integers_within_distance(mutation_site, 1)[1]

    if mutation_site_label is not None:
        if len(mutation_site_label) == len(mutation_site):
            for j in range(len(mutation_site)):
                if mutation_site_label[j] != '':
                    r = mutation_site[j]
                    gb_str = gb_add_feature(gb_str, min(r), max(r) + 1, 'f', 'variation',
                                            {'label': mutation_site_label[j],
                                             'ApEinfo_revcolor': "#b1ff67",
                                             'ApEinfo_fwdcolor': "#b1ff67"})
        else:
            for r in mutation_site:
                gb_str = gb_add_feature(gb_str, min(r), max(r) + 1, 'f', 'variation',
                                        {'label': mutation_site_label[j],
                                         'ApEinfo_revcolor': "#b1ff67",
                                         'ApEinfo_fwdcolor': "#b1ff67"})

    # print('======================================== renamed oligo')
    print(f'{"-" * 60} Proof read (primer end)')
    pcr_fragment_len = []
    pcr_primer_pair = []
    pcr_template = []
    seg_ind = []
    for i in range(len(link_info2)):
        node0, node1 = link_info2[i - 1], link_info2[i]
        j0 = node0[-1]['j0']  # the forward primer of the left link
        j1 = node1[0]['j1']  # the reverse primer of the right link
        seg_ind.append([j0 % seq_len, j1 % seq_len])

        # check if node1 is on the right of node0, if not, or if node1 = node0, node1 + seq_len
        if node1[0]['j1'] <= node0[0]['j1']:
            j1 += seq_len

        if cloning_method == 'GG':
            pcr_fragment_len.append(j1 - j0 + 2 * len(IIS_prefix))
        else:
            pcr_fragment_len.append(j1 - j0)

        pcr_primer_pair.append(', '.join([node0[-1]['oligo_name'], node1[0]['oligo_name']]))
        if pcr_source == []:
            pcr_template.append(locus_name)

        elif isinstance(pcr_source, str):
            pcr_template.append(pcr_source)
        elif len(pcr_source) == len(link_info2):
            pcr_template.append(pcr_source[i])
        else:
            pcr_template.append(pcr_source[0])

        # 240229 proof read the result
        template = sequence2[j0:j1].upper()

        #  proof read PCR primer pair
        lp = node0[-1]['seq'][-min(node0[-1]['len'], 25):]
        lp = primer_end_without_ns(lp)

        rp = node1[0]['seq'][-min(node1[0]['len'], 25):]
        rp = primer_end_without_ns(rp)

        Primer3_design(template, mode=0, seq_id='seg{}'.format(i), primer_max_size=25,
                       left_primer=lp, right_primer=rp,
                       oligo_label=[node0[-1]['oligo_name'], node1[0]['oligo_name']],
                       print_explain=False, primer_pick_anyway=1, ns_accepted=5
                       )

        if cloning_method == 'HotF':
            #  proof read homology region:
            homology_region = []
            for i in range(len(node1) - 1):
                a = node1[i + 1]['j0']
                b = node1[i]['j1']
                homology_region.append([a, b])
            for (a, b) in homology_region:
                overlap_left = sequence2[a: min(b, a + 36)]
                overlap_right = sequence2[max(b - 36, a): b]
                Primer3_pick_one_side(template=overlap_right,
                                      primer=overlap_right,
                                      mode=0, rf='f', print_result=True)

                Primer3_pick_one_side(template=overlap_left,
                                      primer=reverse_complement(overlap_left),
                                      mode=0, rf='r', print_result=True)
                print('\n')

    cloning_guide_df = pd.DataFrame(
        {'Primer pair': pcr_primer_pair, 'Template': pcr_template, 'Product (bp)': pcr_fragment_len})

    # collecting internal primer information
    descrip2 = ''
    for lst in link_info2:
        # print(lst)
        if len(lst) > 2:  # has internal primers
            rps = []
            fps = []
            for p in lst:  # these are internal primers
                if p.get('side', None) == 'rps':
                    rps.append(p)

            for p in lst[::-1]:
                if p.get('side', None) == 'fps':
                    fps.append(p)
            if len(rps) > 1:
                descrip2 += f"internal primer associated with {rps[0]['oligo_name']}: {[p['oligo_name'] for p in rps[1:]]}\n"
            if len(fps) > 1:
                descrip2 += f"internal primer associated with {fps[0]['oligo_name']}: {[p['oligo_name'] for p in fps[1:]]}\n"

            if len(rps) > 1 or len(fps) > 1:
                descrip2 += 'Single-round nested PCR: mix 0.005 µM each internal primer with 0.5 µM each Primer pair\n'

    print(f'{"-" * 60} {locus_name} cloning design')
    print(definition)
    print(dataframe_to_tab_separated_string(cloning_guide_df, preceding_tab=1))
    print(descrip2)

    return gb_str, oligo_list2, cloning_guide_df, descrip2


def choose_golden_gate(lst_of_seq, N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0, print_out=True):
    def GC_content(t):
        ''' t can be a string or a list of string. The output will be a list of 1 or multi elements'''
        if isinstance(t, str):
            t = [t]

        if not isinstance(t, list):
            return

        k = []
        for y in t:
            t1 = list(y.upper())
            a = 0
            b = 0
            for x in t1:
                if x in ['G', 'C']:
                    a += 1
                else:
                    b += 1
            k.append(a / (a + b))
        return k

    def count_same_chars(t1, t2):
        count = 0
        for i in range(min(len(t1), len(t2))):
            if t1[i] == t2[i]:
                count += 1
        return count

    def count_same_chars_pairwise_iteration(lst):
        ''' x is a list of strings. return the maximal and minimal same_chars'''
        minimal_same_char = 4
        maximal_same_char = 0

        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                x = count_same_chars(lst[i].upper(), lst[j].upper())
                minimal_same_char = min(minimal_same_char, x)
                maximal_same_char = max(maximal_same_char, x)

        return minimal_same_char, maximal_same_char

    def to_YR(seq1):
        if isinstance(seq1, str):
            t = seq1.upper().replace('A', 'R').replace('G', 'R').replace('T', 'Y').replace('C', 'Y')
            return t
        elif isinstance(seq1, list):
            lst2 = []
            for x in seq1:
                lst2.append(to_YR(x))
            return lst2
        else:
            return

    lst2 = []
    for s in lst_of_seq:
        x = s.upper()
        lst2.append([])
        for i in range(len(x) - 3):
            lst2[-1].append(x[i:i + 4])

    from itertools import product
    from itertools import combinations

    if print_out == True:
        print('Copy and paste the following lines to Excel to facilitate visualization')
        print('regions\toverhangs\toverhangs_YR\tmax_N_match\tmax_YR_match\tgc_content')

    combinations = list(product(*lst2))

    Y = []
    for combo in combinations:
        x1 = list(combo)
        x2 = list(combo)
        for x in combo:
            x2.append(reverse_complement(x))

        # pairs = list(combinations(x2, 2))

        a, b = count_same_chars_pairwise_iteration(x2)
        c, d = count_same_chars_pairwise_iteration(to_YR(x2))
        e = GC_content(x1)

        y = f'{x1}\t{x2}\t{to_YR(x2)}\t{b}\t{d}\t{e}'

        if b <= N_match_cutoff and d <= YR_match_cutoff and min(e) >= GC_threshold:
            if print_out == True:
                print(y)
            Y.append({
                "combo": x1,
                "overhangs": x2,
                "overhangs_YR": to_YR(x2),
                "max_N_match": b,
                "max_YR_match": d,
                "gc_content": e,
                "score": b * d
            })

    return Y


def Calculate_fpo_and_rpo(sequence, j0, j1, preset=None,
                          primer_min_tm=55, primer_opt_tm=57,
                          primer_min_size=16, primer_opt_size=18, primer_max_size=30,
                          anyway=True,
                          ns_accepted=0):
    '''  preset = 0 for homology cloning'''

    ''' preset 0 for homology cloning 
            preset 1 for primer walking'''

    if preset is not None:
        if preset == 0:
            primer_min_tm = 48
            primer_opt_tm = 52

            primer_min_size = 15
            primer_opt_size = 18
            primer_max_size = 25

        elif preset == 1:
            primer_min_tm = 51
            primer_opt_tm = 57

            primer_min_size = 16
            primer_opt_size = 18
            primer_max_size = 25

    template = sequence[j0:j1]
    a = Primer3_pick_one_side(template, thermodynamic=0,
                              primer_min_tm=primer_min_tm, primer_opt_tm=primer_opt_tm,
                              primer_min_size=primer_min_size, primer_opt_size=primer_opt_size,
                              primer_max_size=primer_max_size,
                              rf='f', anyway=anyway, number_picked=1,
                              ns_accepted=ns_accepted)
    if a == []:
        fp = None
        fpo = j1
    else:
        fp = a[0]
        fpo = j0 + fp['oligolen']

    b = Primer3_pick_one_side(template, thermodynamic=0,
                              primer_min_tm=primer_min_tm, primer_opt_tm=primer_opt_tm,
                              primer_min_size=primer_min_size, primer_opt_size=primer_opt_size,
                              primer_max_size=primer_max_size,
                              rf='r', anyway=anyway, number_picked=1,
                              ns_accepted=ns_accepted)

    if b == []:
        rp = None
        rpo = j0
    else:
        rp = b[0]
        rpo = j1 - rp['oligolen']

    return [fp, rp], [fpo, rpo]


def Calculate_all_po_pairs(sequence, j0, j1, preset=None,
                           primer_min_tm=55, primer_opt_tm=57,
                           primer_min_size=16, primer_opt_size=18, primer_max_size=30,
                           ns_accepted=0, anywayanyway=False):
    def Calculate_po_pairs(sequence, j0, j1, preset=None,
                           primer_min_tm=55, primer_opt_tm=57,
                           primer_min_size=16, primer_opt_size=18, primer_max_size=30,
                           anyways=[False, False],
                           ns_accepted=0):
        ''' preset 0 for homology cloning
        preset 1 for primer walking'''

        if preset is not None:
            if preset == 0:
                primer_min_tm = 48
                primer_opt_tm = 52

                primer_min_size = 15
                primer_opt_size = 18
                primer_max_size = 25

            elif preset == 1:
                primer_min_tm = 55
                primer_opt_tm = 57

                primer_min_size = 16
                primer_opt_size = 18
                primer_max_size = 25

        fpo_list = []
        for k0 in range(j0, j1 - primer_min_size):
            k1 = min(j1, k0 + primer_max_size)
            temp, [fpo, rpo] = Calculate_fpo_and_rpo(sequence, k0, k1,
                                                     preset=preset,
                                                     primer_min_tm=primer_min_tm,
                                                     primer_opt_tm=primer_opt_tm,
                                                     primer_min_size=primer_min_size,
                                                     primer_opt_size=primer_opt_size,
                                                     primer_max_size=primer_max_size,
                                                     anyway=anyways[0],
                                                     ns_accepted=ns_accepted)
            if fpo is not None:
                fpo_list.append(fpo)

        fpo_list = list(set(fpo_list))
        fpo_list.sort()

        po_pairs = []
        for k1 in fpo_list:
            k0 = max(j0, k1 - primer_max_size)
            temp, [fpo, rpo] = Calculate_fpo_and_rpo(sequence, k0, k1,
                                                     preset=preset,
                                                     primer_min_tm=primer_min_tm,
                                                     primer_opt_tm=primer_opt_tm,
                                                     primer_min_size=primer_min_size,
                                                     primer_opt_size=primer_opt_size,
                                                     primer_max_size=primer_max_size,
                                                     anyway=anyways[1],
                                                     ns_accepted=ns_accepted)
            if rpo is not None:
                po_pairs.append([rpo, k1])

        return po_pairs

    FF = Calculate_po_pairs(sequence, j0, j1, preset,
                            primer_min_tm, primer_opt_tm,
                            primer_min_size, primer_opt_size, primer_max_size,
                            anyways=[False, False],
                            ns_accepted=ns_accepted)

    FT = Calculate_po_pairs(sequence, j0, j1, preset,
                            primer_min_tm, primer_opt_tm,
                            primer_min_size, primer_opt_size, primer_max_size,
                            anyways=[False, True],
                            ns_accepted=ns_accepted)

    TF = Calculate_po_pairs(sequence, j0, j1, preset,
                            primer_min_tm, primer_opt_tm,
                            primer_min_size, primer_opt_size, primer_max_size,
                            anyways=[True, False],
                            ns_accepted=ns_accepted)

    TT = Calculate_po_pairs(sequence, j0, j1, preset,
                            primer_min_tm, primer_opt_tm,
                            primer_min_size, primer_opt_size, primer_max_size,
                            anyways=[True, True],
                            ns_accepted=ns_accepted)

    po_pairs = FF
    if po_pairs != []:
        mylist = [x[1] - x[0] for x in po_pairs]
        zipped_lists = list(zip(po_pairs, mylist))
        sorted_zipped_lists = sorted(zipped_lists, key=lambda x: x[1])
        FF_pairs, temp = zip(*sorted_zipped_lists)
    else:
        FF_pairs = []

    po_pairs = TF + FT
    po_pairs = [x for x in po_pairs if x not in FF_pairs]

    if po_pairs != []:
        mylist = [x[1] - x[0] for x in po_pairs]
        zipped_lists = list(zip(po_pairs, mylist))
        sorted_zipped_lists = sorted(zipped_lists, key=lambda x: x[1])
        FTTF_pairs, temp = zip(*sorted_zipped_lists)
    else:
        FTTF_pairs = []

    if anywayanyway == False:
        return FF_pairs, FTTF_pairs
    else:
        return FF_pairs, TT


def Show_po_pairs(substring, exact=False, preset=0):  # version 240313
    if exact == False:
        a = Calculate_all_po_pairs(substring, 0, len(substring), preset=preset)[0]
    else:
        a = [(0, len(substring))]

    s2 = []
    print('substring:\n{}'.format(substring))
    for j0, j1 in a:
        print(' ' * j0 + '>' * (j1 - j0))

    for j0, j1 in a:
        text = substring[j0:j1]
        Primer3_pick_one_side(template=substring,
                              primer=text,
                              mode=0, rf='f', print_result=True)

        Primer3_pick_one_side(template=substring,
                              primer=reverse_complement(text),
                              mode=0, rf='r', print_result=True)
        print('\n')
        s2.append(text)
    return s2


# ------------------------------------------   Translation related
def extract_kazusa(species='ecoli', fraction_cutoff=0):
    """
    species could either be 'ecoli', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    """

    import re

    kazusa_dict = {
        'ecoli': '''
    https://www.kazusa.or.jp/codon/cgi-bin/showcodon.cgi?species=37762&aa=1&style=Codon (p.s. taxid 37762, B strain)

    Escherichia coli [gbbct]: 8087 CDS's (2330943 codons)
    fields: [triplet] [amino acid] [fraction] [frequency: per thousand] ([number])

    UUU F 0.64 24.4 ( 56791)  UCU S 0.18 13.1 ( 30494)  UAU Y 0.65 21.6 ( 50400)  UGU C 0.52  5.9 ( 13662)
    UUC F 0.36 13.9 ( 32513)  UCC S 0.14  9.7 ( 22637)  UAC Y 0.35 11.7 ( 27239)  UGC C 0.48  5.5 ( 12777)
    UUA L 0.18 17.4 ( 40627)  UCA S 0.18 13.1 ( 30502)  UAA * 0.58  2.0 (  4664)  UGA * 0.33  1.1 (  2674)
    UUG L 0.13 12.9 ( 30084)  UCG S 0.11  8.2 ( 19071)  UAG * 0.09  0.3 (   751)  UGG W 1.00 13.4 ( 31207)

    CUU L 0.15 14.5 ( 33816)  CCU P 0.24  9.5 ( 22121)  CAU H 0.63 12.4 ( 28919)  CGU R 0.30 15.9 ( 37134)
    CUC L 0.10  9.5 ( 22074)  CCC P 0.16  6.2 ( 14379)  CAC H 0.37  7.3 ( 17117)  CGC R 0.26 14.0 ( 32720)
    CUA L 0.06  5.6 ( 12951)  CCA P 0.23  9.1 ( 21237)  CAA Q 0.35 14.4 ( 33607)  CGA R 0.09  4.8 ( 11216)
    CUG L 0.38 37.4 ( 87261)  CCG P 0.37 14.5 ( 33795)  CAG Q 0.65 26.7 ( 62329)  CGG R 0.15  7.9 ( 18434)

    AUU I 0.47 29.6 ( 68942)  ACU T 0.22 13.1 ( 30518)  AAU N 0.59 29.3 ( 68348)  AGU S 0.18 13.2 ( 30749)
    AUC I 0.31 19.4 ( 45213)  ACC T 0.31 18.9 ( 44139)  AAC N 0.41 20.3 ( 47233)  AGC S 0.20 14.3 ( 33255)
    AUA I 0.21 13.3 ( 31065)  ACA T 0.25 15.1 ( 35293)  AAA K 0.71 37.2 ( 86726)  AGA R 0.13  7.1 ( 16583)
    AUG M 1.00 23.7 ( 55356)  ACG T 0.22 13.6 ( 31794)  AAG K 0.29 15.3 ( 35652)  AGG R 0.07  4.0 (  9238)

    GUU V 0.32 21.6 ( 50261)  GCU A 0.22 18.9 ( 44034)  GAU D 0.65 33.7 ( 78663)  GGU G 0.34 23.7 ( 55283)
    GUC V 0.19 13.1 ( 30515)  GCC A 0.26 21.6 ( 50411)  GAC D 0.35 17.9 ( 41619)  GGC G 0.29 20.6 ( 47962)
    GUA V 0.19 13.1 ( 30461)  GCA A 0.27 23.0 ( 53619)  GAA E 0.64 35.1 ( 81727)  GGA G 0.19 13.6 ( 31729)
    GUG V 0.29 19.9 ( 46309)  GCG A 0.25 21.1 ( 49169)  GAG E 0.36 19.4 ( 45154)  GGG G 0.18 12.3 ( 28720)''',
        'bacillus': '''
    https://www.kazusa.or.jp/codon/cgi-bin/showcodon.cgi?species=1423&aa=1&style=N

    Bacillus subtilis [gbbct]: 2529 CDS's (815445 codons)
    fields: [triplet] [amino acid] [fraction] [frequency: per thousand] ([number])

    UUU F 0.68 30.0 ( 24450)  UCU S 0.20 12.7 ( 10320)  UAU Y 0.65 23.3 ( 18967)  UGU C 0.46  3.6 (  2939)
    UUC F 0.32 14.3 ( 11677)  UCC S 0.13  8.3 (  6766)  UAC Y 0.35 12.6 ( 10290)  UGC C 0.54  4.3 (  3472)
    UUA L 0.21 19.8 ( 16167)  UCA S 0.23 14.6 ( 11874)  UAA * 0.61  1.9 (  1562)  UGA * 0.24  0.8 (   621)
    UUG L 0.16 15.8 ( 12914)  UCG S 0.10  6.5 (  5266)  UAG * 0.15  0.5 (   381)  UGG W 1.00 10.7 (  8765)

    CUU L 0.23 21.8 ( 17772)  CCU P 0.28 10.6 (  8640)  CAU H 0.68 15.7 ( 12832)  CGU R 0.18  7.2 (  5903)
    CUC L 0.11 10.7 (  8697)  CCC P 0.09  3.5 (  2850)  CAC H 0.32  7.5 (  6141)  CGC R 0.20  8.2 (  6720)
    CUA L 0.05  4.9 (  3975)  CCA P 0.19  7.1 (  5796)  CAA Q 0.52 20.4 ( 16620)  CGA R 0.10  4.3 (  3537)
    CUG L 0.24 23.0 ( 18757)  CCG P 0.44 16.3 ( 13316)  CAG Q 0.48 18.5 ( 15089)  CGG R 0.17  6.9 (  5664)

    AUU I 0.49 36.2 ( 29487)  ACU T 0.16  8.7 (  7082)  AAU N 0.56 22.9 ( 18702)  AGU S 0.11  6.8 (  5577)
    AUC I 0.37 27.2 ( 22167)  ACC T 0.17  9.0 (  7342)  AAC N 0.44 17.8 ( 14522)  AGC S 0.23 14.4 ( 11766)
    AUA I 0.13  9.8 (  7960)  ACA T 0.40 21.6 ( 17642)  AAA K 0.70 48.4 ( 39449)  AGA R 0.25 10.5 (  8561)
    AUG M 1.00 26.3 ( 21424)  ACG T 0.27 14.9 ( 12110)  AAG K 0.30 20.8 ( 16997)  AGG R 0.10  4.1 (  3341)

    GUU V 0.28 18.6 ( 15193)  GCU A 0.24 18.6 ( 15150)  GAU D 0.64 33.2 ( 27108)  GGU G 0.19 13.0 ( 10566)
    GUC V 0.26 17.3 ( 14067)  GCC A 0.22 16.5 ( 13433)  GAC D 0.36 19.0 ( 15485)  GGC G 0.34 23.3 ( 18967)
    GUA V 0.20 13.0 ( 10638)  GCA A 0.28 21.1 ( 17205)  GAA E 0.68 48.1 ( 39217)  GGA G 0.31 21.8 ( 17743)
    GUG V 0.26 17.3 ( 14105)  GCG A 0.26 19.8 ( 16176)  GAG E 0.32 22.6 ( 18429)  GGG G 0.16 11.2 (  9094)''',

        'yeast': '''
    https://www.kazusa.or.jp/codon/cgi-bin/showcodon.cgi?species=4932&aa=1&style=N

    Saccharomyces cerevisiae [gbpln]: 14411 CDS's (6534504 codons)
    fields: [triplet] [amino acid] [fraction] [frequency: per thousand] ([number])

    UUU F 0.59 26.1 (170666)  UCU S 0.26 23.5 (153557)  UAU Y 0.56 18.8 (122728)  UGU C 0.63  8.1 ( 52903)
    UUC F 0.41 18.4 (120510)  UCC S 0.16 14.2 ( 92923)  UAC Y 0.44 14.8 ( 96596)  UGC C 0.37  4.8 ( 31095)
    UUA L 0.28 26.2 (170884)  UCA S 0.21 18.7 (122028)  UAA * 0.47  1.1 (  6913)  UGA * 0.30  0.7 (  4447)
    UUG L 0.29 27.2 (177573)  UCG S 0.10  8.6 ( 55951)  UAG * 0.23  0.5 (  3312)  UGG W 1.00 10.4 ( 67789)

    CUU L 0.13 12.3 ( 80076)  CCU P 0.31 13.5 ( 88263)  CAU H 0.64 13.6 ( 89007)  CGU R 0.14  6.4 ( 41791)
    CUC L 0.06  5.4 ( 35545)  CCC P 0.15  6.8 ( 44309)  CAC H 0.36  7.8 ( 50785)  CGC R 0.06  2.6 ( 16993)
    CUA L 0.14 13.4 ( 87619)  CCA P 0.42 18.3 (119641)  CAA Q 0.69 27.3 (178251)  CGA R 0.07  3.0 ( 19562)
    CUG L 0.11 10.5 ( 68494)  CCG P 0.12  5.3 ( 34597)  CAG Q 0.31 12.1 ( 79121)  CGG R 0.04  1.7 ( 11351)

    AUU I 0.46 30.1 (196893)  ACU T 0.35 20.3 (132522)  AAU N 0.59 35.7 (233124)  AGU S 0.16 14.2 ( 92466)
    AUC I 0.26 17.2 (112176)  ACC T 0.22 12.7 ( 83207)  AAC N 0.41 24.8 (162199)  AGC S 0.11  9.8 ( 63726)
    AUA I 0.27 17.8 (116254)  ACA T 0.30 17.8 (116084)  AAA K 0.58 41.9 (273618)  AGA R 0.48 21.3 (139081)
    AUG M 1.00 20.9 (136805)  ACG T 0.14  8.0 ( 52045)  AAG K 0.42 30.8 (201361)  AGG R 0.21  9.2 ( 60289)

    GUU V 0.39 22.1 (144243)  GCU A 0.38 21.2 (138358)  GAU D 0.65 37.6 (245641)  GGU G 0.47 23.9 (156109)
    GUC V 0.21 11.8 ( 76947)  GCC A 0.22 12.6 ( 82357)  GAC D 0.35 20.2 (132048)  GGC G 0.19  9.8 ( 63903)
    GUA V 0.21 11.8 ( 76927)  GCA A 0.29 16.2 (105910)  GAA E 0.70 45.6 (297944)  GGA G 0.22 10.9 ( 71216)
    GUG V 0.19 10.8 ( 70337)  GCG A 0.11  6.2 ( 40358)  GAG E 0.30 19.2 (125717)  GGG G 0.12  6.0 ( 39359)''',

        'pichia': '''
    https://www.kazusa.or.jp/codon/cgi-bin/showcodon.cgi?species=4922&aa=1&style=N

    Pichia pastoris [gbpln]: 137 CDS's (81301 codons)
    fields: [triplet] [amino acid] [fraction] [frequency: per thousand] ([number])

    UUU F 0.54 24.1 (  1963)  UCU S 0.29 24.4 (  1983)  UAU Y 0.47 16.0 (  1300)  UGU C 0.64  7.7 (   626)
    UUC F 0.46 20.6 (  1675)  UCC S 0.20 16.5 (  1344)  UAC Y 0.53 18.1 (  1473)  UGC C 0.36  4.4 (   356)
    UUA L 0.16 15.6 (  1265)  UCA S 0.18 15.2 (  1234)  UAA * 0.51  0.8 (    69)  UGA * 0.20  0.3 (    27)
    UUG L 0.33 31.5 (  2562)  UCG S 0.09  7.4 (   598)  UAG * 0.29  0.5 (    40)  UGG W 1.00 10.3 (   834)

    CUU L 0.16 15.9 (  1289)  CCU P 0.35 15.8 (  1282)  CAU H 0.57 11.8 (   960)  CGU R 0.17  6.9 (   564)
    CUC L 0.08  7.6 (   620)  CCC P 0.15  6.8 (   553)  CAC H 0.43  9.1 (   737)  CGC R 0.05  2.2 (   175)
    CUA L 0.11 10.7 (   873)  CCA P 0.42 18.9 (  1540)  CAA Q 0.61 25.4 (  2069)  CGA R 0.10  4.2 (   340)
    CUG L 0.16 14.9 (  1215)  CCG P 0.09  3.9 (   320)  CAG Q 0.39 16.3 (  1323)  CGG R 0.05  1.9 (   158)

    AUU I 0.50 31.1 (  2532)  ACU T 0.40 22.4 (  1820)  AAU N 0.48 25.1 (  2038)  AGU S 0.15 12.5 (  1020)
    AUC I 0.31 19.4 (  1580)  ACC T 0.26 14.5 (  1175)  AAC N 0.52 26.7 (  2168)  AGC S 0.09  7.6 (   621)
    AUA I 0.18 11.1 (   906)  ACA T 0.24 13.8 (  1118)  AAA K 0.47 29.9 (  2433)  AGA R 0.48 20.1 (  1634)
    AUG M 1.00 18.7 (  1517)  ACG T 0.11  6.0 (   491)  AAG K 0.53 33.8 (  2748)  AGG R 0.16  6.6 (   539)

    GUU V 0.42 26.9 (  2188)  GCU A 0.45 28.9 (  2351)  GAU D 0.58 35.7 (  2899)  GGU G 0.44 25.5 (  2075)
    GUC V 0.23 14.9 (  1210)  GCC A 0.26 16.6 (  1348)  GAC D 0.42 25.9 (  2103)  GGC G 0.14  8.1 (   655)
    GUA V 0.15  9.9 (   804)  GCA A 0.23 15.1 (  1228)  GAA E 0.56 37.4 (  3043)  GGA G 0.33 19.1 (  1550)
    GUG V 0.19 12.3 (   998)  GCG A 0.06  3.9 (   314)  GAG E 0.44 29.0 (  2360)  GGG G 0.10  5.8 (   468)''',

        'mouse': '''
    https://www.kazusa.or.jp/codon/cgi-bin/showcodon.cgi?species=10090&aa=1&style=N

    Mus musculus [gbrod]: 53036 CDS's (24533776 codons)
    fields: [triplet] [amino acid] [fraction] [frequency: per thousand] ([number])

    UUU F 0.44 17.2 (422153)  UCU S 0.20 16.2 (398250)  UAU Y 0.43 12.2 (298518)  UGU C 0.48 11.4 (279729)
    UUC F 0.56 21.8 (535439)  UCC S 0.22 18.1 (444041)  UAC Y 0.57 16.1 (394074)  UGC C 0.52 12.3 (301384)
    UUA L 0.07  6.7 (165150)  UCA S 0.14 11.8 (289799)  UAA * 0.28  1.0 ( 23403)  UGA * 0.49  1.6 ( 40148)
    UUG L 0.13 13.4 (329668)  UCG S 0.05  4.2 (103815)  UAG * 0.23  0.8 ( 19126)  UGG W 1.00 12.5 (306619)

    CUU L 0.13 13.4 (329757)  CCU P 0.31 18.4 (450637)  CAU H 0.41 10.6 (260637)  CGU R 0.08  4.7 (114854)
    CUC L 0.20 20.2 (495018)  CCC P 0.30 18.2 (446868)  CAC H 0.59 15.3 (375626)  CGC R 0.17  9.4 (229758)
    CUA L 0.08  8.1 (198032)  CCA P 0.29 17.3 (423707)  CAA Q 0.26 12.0 (293318)  CGA R 0.12  6.6 (161412)
    CUG L 0.39 39.5 (969515)  CCG P 0.10  6.2 (151521)  CAG Q 0.74 34.1 (836320)  CGG R 0.19 10.2 (250836)

    AUU I 0.34 15.4 (377698)  ACU T 0.25 13.7 (335039)  AAU N 0.43 15.6 (382284)  AGU S 0.15 12.7 (311331)
    AUC I 0.50 22.5 (552184)  ACC T 0.35 19.0 (465115)  AAC N 0.57 20.3 (499149)  AGC S 0.24 19.7 (483013)
    AUA I 0.16  7.4 (180467)  ACA T 0.29 16.0 (391437)  AAA K 0.39 21.9 (537723)  AGA R 0.22 12.1 (297135)
    AUG M 1.00 22.8 (559953)  ACG T 0.10  5.6 (138180)  AAG K 0.61 33.6 (825270)  AGG R 0.22 12.2 (299472)

    GUU V 0.17 10.7 (262535)  GCU A 0.29 20.0 (491093)  GAU D 0.45 21.0 (515049)  GGU G 0.18 11.4 (280522)
    GUC V 0.25 15.4 (377902)  GCC A 0.38 26.0 (637878)  GAC D 0.55 26.0 (638504)  GGC G 0.33 21.2 (520069)
    GUA V 0.12  7.4 (182733)  GCA A 0.23 15.8 (388723)  GAA E 0.41 27.0 (661498)  GGA G 0.26 16.8 (411344)
    GUG V 0.46 28.4 (696158)  GCG A 0.09  6.4 (157124)  GAG E 0.59 39.4 (965963)  GGG G 0.23 15.2 (372099)''',

        'hamster': '''
    https://www.kazusa.or.jp/codon/cgi-bin/showcodon.cgi?species=10029&aa=1&style=N

    Cricetulus griseus [gbrod]: 331 CDS's (153527 codons)
    fields: [triplet] [amino acid] [fraction] [frequency: per thousand] ([number])

    UUU F 0.47 19.6 (  3005)  UCU S 0.22 16.0 (  2450)  UAU Y 0.44 13.1 (  2017)  UGU C 0.47  9.1 (  1397)
    UUC F 0.53 22.0 (  3381)  UCC S 0.22 16.5 (  2529)  UAC Y 0.56 16.4 (  2519)  UGC C 0.53 10.3 (  1589)
    UUA L 0.06  6.4 (   978)  UCA S 0.14 10.3 (  1577)  UAA * 0.26  0.6 (    93)  UGA * 0.50  1.2 (   177)
    UUG L 0.14 14.1 (  2169)  UCG S 0.05  3.4 (   529)  UAG * 0.24  0.5 (    84)  UGG W 1.00 13.1 (  2012)

    CUU L 0.13 13.2 (  2023)  CCU P 0.31 16.7 (  2563)  CAU H 0.44 10.2 (  1563)  CGU R 0.11  5.6 (   863)
    CUC L 0.19 18.4 (  2818)  CCC P 0.32 17.0 (  2608)  CAC H 0.56 12.9 (  1980)  CGC R 0.18  9.3 (  1429)
    CUA L 0.08  7.6 (  1174)  CCA P 0.29 15.6 (  2388)  CAA Q 0.24 10.3 (  1587)  CGA R 0.14  7.2 (  1102)
    CUG L 0.39 38.8 (  5955)  CCG P 0.08  4.3 (   657)  CAG Q 0.76 33.4 (  5122)  CGG R 0.19 10.1 (  1558)

    AUU I 0.35 17.4 (  2673)  ACU T 0.26 14.1 (  2172)  AAU N 0.45 17.4 (  2671)  AGU S 0.15 11.4 (  1756)
    AUC I 0.51 24.8 (  3808)  ACC T 0.37 20.3 (  3118)  AAC N 0.55 21.2 (  3248)  AGC S 0.22 16.4 (  2521)
    AUA I 0.14  6.9 (  1053)  ACA T 0.29 15.7 (  2418)  AAA K 0.39 24.6 (  3782)  AGA R 0.19 10.1 (  1557)
    AUG M 1.00 23.0 (  3538)  ACG T 0.08  4.5 (   685)  AAG K 0.61 38.4 (  5895)  AGG R 0.19 10.2 (  1570)

    GUU V 0.18 11.6 (  1780)  GCU A 0.32 22.4 (  3432)  GAU D 0.47 24.6 (  3781)  GGU G 0.20 12.8 (  1968)
    GUC V 0.24 15.7 (  2408)  GCC A 0.37 25.9 (  3973)  GAC D 0.53 28.1 (  4310)  GGC G 0.34 21.3 (  3268)
    GUA V 0.12  7.8 (  1202)  GCA A 0.23 16.3 (  2497)  GAA E 0.41 28.4 (  4355)  GGA G 0.25 15.8 (  2425)
    GUG V 0.46 30.1 (  4628)  GCG A 0.07  5.0 (   765)  GAG E 0.59 41.1 (  6311)  GGG G 0.21 13.4 (  2063)''',

        'human': '''
    https://www.kazusa.or.jp/codon/cgi-bin/showcodon.cgi?species=9606&aa=1&style=N

    Homo sapiens [gbpri]: 93487 CDS's (40662582 codons)
    fields: [triplet] [amino acid] [fraction] [frequency: per thousand] ([number])

    UUU F 0.46 17.6 (714298)  UCU S 0.19 15.2 (618711)  UAU Y 0.44 12.2 (495699)  UGU C 0.46 10.6 (430311)
    UUC F 0.54 20.3 (824692)  UCC S 0.22 17.7 (718892)  UAC Y 0.56 15.3 (622407)  UGC C 0.54 12.6 (513028)
    UUA L 0.08  7.7 (311881)  UCA S 0.15 12.2 (496448)  UAA * 0.30  1.0 ( 40285)  UGA * 0.47  1.6 ( 63237)
    UUG L 0.13 12.9 (525688)  UCG S 0.05  4.4 (179419)  UAG * 0.24  0.8 ( 32109)  UGG W 1.00 13.2 (535595)

    CUU L 0.13 13.2 (536515)  CCU P 0.29 17.5 (713233)  CAU H 0.42 10.9 (441711)  CGU R 0.08  4.5 (184609)
    CUC L 0.20 19.6 (796638)  CCC P 0.32 19.8 (804620)  CAC H 0.58 15.1 (613713)  CGC R 0.18 10.4 (423516)
    CUA L 0.07  7.2 (290751)  CCA P 0.28 16.9 (688038)  CAA Q 0.27 12.3 (501911)  CGA R 0.11  6.2 (250760)
    CUG L 0.40 39.6 (1611801)  CCG P 0.11  6.9 (281570)  CAG Q 0.73 34.2 (1391973)  CGG R 0.20 11.4 (464485)

    AUU I 0.36 16.0 (650473)  ACU T 0.25 13.1 (533609)  AAU N 0.47 17.0 (689701)  AGU S 0.15 12.1 (493429)
    AUC I 0.47 20.8 (846466)  ACC T 0.36 18.9 (768147)  AAC N 0.53 19.1 (776603)  AGC S 0.24 19.5 (791383)
    AUA I 0.17  7.5 (304565)  ACA T 0.28 15.1 (614523)  AAA K 0.43 24.4 (993621)  AGA R 0.21 12.2 (494682)
    AUG M 1.00 22.0 (896005)  ACG T 0.11  6.1 (246105)  AAG K 0.57 31.9 (1295568)  AGG R 0.21 12.0 (486463)

    GUU V 0.18 11.0 (448607)  GCU A 0.27 18.4 (750096)  GAU D 0.46 21.8 (885429)  GGU G 0.16 10.8 (437126)
    GUC V 0.24 14.5 (588138)  GCC A 0.40 27.7 (1127679)  GAC D 0.54 25.1 (1020595)  GGC G 0.34 22.2 (903565)
    GUA V 0.12  7.1 (287712)  GCA A 0.23 15.8 (643471)  GAA E 0.42 29.0 (1177632)  GGA G 0.25 16.5 (669873)
    GUG V 0.46 28.1 (1143534)  GCG A 0.11  7.4 (299495)  GAG E 0.58 39.6 (1609975)  GGG G 0.25 16.5 (669768)'''

    }

    input_string = kazusa_dict[species]

    # Define a regular expression pattern to match each part
    pattern = re.compile(r'(\S+)\s+(\S+)\s+([\d.]+)\s+([\d.]+)\s+\(\s*(\d+)\)')

    # Find all matches in the input string
    matches = pattern.findall(input_string)

    # Create a DataFrame from the matches
    columns = ['triplet', 'amino acid', 'fraction', 'frequency per thousand', 'number']
    df = pd.DataFrame(matches, columns=columns)
    df['fraction'] = pd.to_numeric(df['fraction'], downcast='float')
    df['frequency per thousand'] = pd.to_numeric(df['frequency per thousand'], downcast='float')
    df['number'] = pd.to_numeric(df['number'], downcast='integer')

    df['triplet'] = df['triplet'].replace('U', 'T', regex=True)

    # Filter rows where 'fraction' > fraction_cutoff
    df1 = df[df['fraction'] >= fraction_cutoff]

    # Make a dictionary where key is amino acid, value is the most common triplet
    idx = df1.groupby('amino acid')['fraction'].idxmax()
    dc1 = df1.loc[idx][['amino acid', 'triplet']].set_index('amino acid')['triplet'].to_dict()  # preferred_triplet
    return df1, dc1


def preferred_triplet(species='ecoli'):
    """
    species could either be 'ecoli', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    """
    df, dc = extract_kazusa(species)

    return dc


translate_degenerate_triplets = None
translate_degenerate_triplets_all = None


def Translate_degenerate_triplets(codon_table):  # copy from '230615 codon use'
    global translate_degenerate_triplets
    global translate_degenerate_triplets_all

    def Index_combinations(d0):
        ''' e.g. [2,3,2] -> [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [1, 0, 0], [1, 0, 1],
        [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1]]'''
        N = 1
        for i in range(len(d0)):
            N = N * d0[i]

        n = []
        t = N
        for i in range(len(d0)):
            n.append(t / d0[i])
            t = t / d0[i]

        d1 = []
        for i in range(N):
            y = []
            for j in range(len(d0)):
                y.append(math.floor(i / n[j]))
                i = i % n[j]
            d1.append(y)
        return d1

    def Triplet_combinations(lt):  # input 2D list       # copy from '230615 codon use'
        '''e.g.  Triplet_combinations([['A','B'],['C','D','E'],['F','G']])
        -> ['ACF', 'ACG', 'ADF', 'ADG', 'AEF', 'AEG', 'BCF', 'BCG', 'BDF', 'BDG', 'BEF', 'BEG']'''

        d0 = []
        for i in range(len(lt)):
            d0.append(len(lt[i]))
        c = Index_combinations(d0)

        y1 = []
        for i in range(len(c)):
            y = ''
            for j in range(len(c[i])):
                x = c[i][j]
                y = y + lt[j][x]
            y1.append(y)
        return y1

    if len(codon_table) == 64 and translate_degenerate_triplets_all is not None:
        return translate_degenerate_triplets_all

    elif len(codon_table) < 64 and translate_degenerate_triplets is not None:
        return translate_degenerate_triplets

    else:
        # print('once')
        IUPC_code_to_bases = {'A': 'A', 'T': 'T', 'C': 'C', 'G': 'G', 'M': 'AC', 'R': 'AG', 'W': 'AT', 'S': 'GC',
                              'Y': 'CT',
                              'K': 'GT', 'V': 'AGC', 'H': 'ACT', 'D': 'AGT', 'B': 'GCT', 'N': 'AGCT'}

        Triplet = list(codon_table['triplet'])
        AA = list(codon_table['amino acid'])
        # print('len AA', len(AA))
        code = list(IUPC_code_to_bases.keys())
        d = Triplet_combinations([code, code, code])

        d3 = []
        for i in d:  # i is a triplet string including redundant base, there's total 3375
            k = []
            for j in list(i):
                t = IUPC_code_to_bases[j]
                k.append(list(t))
            t0 = Triplet_combinations(k)  # t is a list of triplet strings with the redundant base unraveled
            t1 = [x for x in t0 if x in Triplet]  # ignore the triplet of low frequency
            t2 = [AA[Triplet.index(x)] for x in t1]
            t3 = sorted(list(set(t2)))
            t4 = [[x, round(t2.count(x) / len(t0), 2)] for x in t3]

            if len(t1) > 0:
                d3.append([i, t4])
        df = pd.DataFrame(d3)
        df = df.set_axis(['degenerate triplet', 'translate'], axis=1)

        # Output_csv(translate_degenerate_triplets,'translate_degenerate_triplets')
        if len(codon_table) == 64:
            translate_degenerate_triplets_all = df
            return translate_degenerate_triplets_all
        else:
            translate_degenerate_triplets = df
            return translate_degenerate_triplets


triplet_dict_0220 = None
triplet_dict_0220_all = None


def translate_triplet_0220(triplet, fraction_cutoff=0):
    global triplet_dict_0220
    global triplet_dict_0220_all

    # Create triplet dict 0220 once per run
    if (fraction_cutoff == 0 and triplet_dict_0220_all is None) or (fraction_cutoff > 0 and triplet_dict_0220 is None):
        # print('dict_0222 created once')
        df1 = Translate_degenerate_triplets(extract_kazusa(fraction_cutoff=fraction_cutoff)[0])
        dict2 = df1.set_index('degenerate triplet')['translate'].to_dict()

        if fraction_cutoff == 0:
            triplet_dict_0220_all = dict()
        else:
            triplet_dict_0220 = dict()

        for key, value in dict2.items():
            # Convert list to DataFrame
            df = pd.DataFrame(value, columns=['Symbol', 'Probability'])

            if df.shape[0] == 1:
                t0 = df.iloc[0, 0]
                formatted_strings = []
            else:

                df_sorted = df.sort_values(by='Probability', ascending=False)
                t0 = ''.join(list(df_sorted['Symbol']))
                formatted_strings = df_sorted.apply(lambda row: f"{row['Symbol']}.{row['Probability']:.2f}",
                                                    axis=1).tolist()
                formatted_strings = [x.replace('.0.', '.') for x in formatted_strings]

            if fraction_cutoff == 0:
                triplet_dict_0220_all[key] = (t0, formatted_strings)
            else:
                triplet_dict_0220[key] = (t0, formatted_strings)

    triplet = triplet.upper()
    triplet = triplet.replace('U', 'T')
    if len(triplet) != 3:
        print('triplet size != 3')
        return None
    else:
        if fraction_cutoff == 0:
            return triplet_dict_0220_all.get(triplet, [None, None])
        else:
            return triplet_dict_0220.get(triplet, [None, None])


def translate(sequence, forward=True, codon_start=1):
    sequence = sequence.upper()

    df, *_ = extract_kazusa()
    df['triplet'] = df['triplet'].apply(lambda x: x.replace('U', 'T'))  # Convert 'U' to 'T' in the 'triplet' column
    triplet_to_amino = dict(zip(df['triplet'], df['amino acid']))

    if forward == False:
        sequence = reverse_complement(sequence)

    sequence = sequence[codon_start - 1:]

    # Convert the sequence to amino acids

    result = ''.join(triplet_to_amino.get(sequence[i:i + 3], 'X') for i in range(0, len(sequence), 3))
    return result


def translate_0220(sequence, rf='f', codon_start=1, aa_start=1):
    sequence = sequence.upper()

    df, *_ = extract_kazusa()
    df['triplet'] = df['triplet'].apply(lambda x: x.replace('U', 'T'))  # Convert 'U' to 'T' in the 'triplet' column
    triplet_to_amino = dict(zip(df['triplet'], df['amino acid']))

    if rf == 'r':
        sequence = reverse_complement(sequence)

    sequence = sequence[codon_start - 1:]

    ''' 
    result0 e.g.    ASSxx
    result1 e.g.    ASS[NK][ETR]

    result2 e.g.    A  S  S  _  _
                             N  E
                             K  T
                                R


    result3 e.g.    A  S  S  _  _
                             N.05
                             K.05
                                E.33
                                T.33
                                R.33
    '''

    result0 = ''
    result1 = ''
    blank = ' ' * (len(sequence) + 3)
    result2 = [blank]
    result3 = [blank]

    for i in range(0, len(sequence), 3):
        if i + 3 <= len(sequence):
            aa, formated_string = translate_triplet_0220(sequence[i:i + 3])
            if aa is None:
                print('not IUPAC code')
                return
            elif len(aa) == 1:
                result0 += aa
                result1 += aa
                result2[0] = result2[0][:i] + f'{aa}' + result2[0][i + 1:]
                result3[0] = result3[0][:i] + f'{aa}' + result3[0][i + 1:]
            else:
                result0 += 'x'
                result1 += f'[{aa}]'

                result2[0] = result2[0][:i] + '_' + result2[0][i + 1:]
                if 1 + len(aa) > len(result2):
                    for k in range(len(result2), 1 + len(aa)):
                        result2.append(blank)
                for j in range(1, 1 + len(aa)):
                    tt = result2[j]
                    result2[j] = tt[:i] + aa[j - 1] + tt[i + 1:]

                result3[0] = result3[0][:i] + '_' + result3[0][i + 1:]
                # start = len(result3)
                start = 1
                # for j in range(1, len(result3)):
                #     if result3[j][i:i + 4] == ' ' * 4:
                #         start = j
                #         break
                for j in range(len(result3) - 1, 0, -1):
                    if result3[j][i:i + 4] != ' ' * 4:
                        start = j + 1
                        break

                if start + len(aa) > len(result3):
                    for k in range(len(result3), start + len(aa)):
                        result3.append(blank)

                for j in range(start, start + len(aa)):
                    tt = result3[j]
                    result3[j] = tt[:i] + formated_string[j - start] + tt[i + 4:]

    result4 = ''
    for i in range(aa_start, len(sequence) // 3, 5):
        result4 += f'{str(i).ljust(15)}'
    result4 = result4[:len(sequence)]

    result5 = ''
    for i in range(aa_start, len(sequence) // 3, 5):
        result5 += '.' + ' ' * 5 + '.' + ' ' * 8
    result5 = result5[:len(sequence)]

    return result0, result1, result2, result3, result4, result5


def Degenerate_Chooser(codon_table, target,
                       output_filename=None, printout=True, allow_stop=True,
                       ):  # copy from '230615 codon use'
    ''' Given a set of intended aa(s), return degenerate triplets encompassing all the intended aa(s) and sorted by
    highest total occurrence of intended aa(s). Later will consider minimizing the probability of premature termination
    '''
    df1 = Translate_degenerate_triplets(codon_table=codon_table)

    target = list(target)
    degenerate_triplet = list(df1.iloc[:, 0])
    translate = list(df1.iloc[:, 1])

    df2 = []

    for i in range(len(translate)):
        y = pd.DataFrame(translate[i])
        aa_list = list(y.iloc[:, 0])
        aa_prob = list(y.iloc[:, 1])

        hit = 1
        P_sum = 0
        P_product = 1
        for j in target:
            if j not in aa_list:
                hit = 0
                P_product = 0
            else:
                P_sum = P_sum + aa_prob[aa_list.index(j)]
                P_product = P_product * aa_prob[aa_list.index(j)]

        if hit == 1:
            if '*' in aa_list:
                P_terminate = aa_prob[aa_list.index('*')]
            else:
                P_terminate = 0
            df2.append([degenerate_triplet[i], translate[i], ''.join(aa_list), P_sum, P_product, P_terminate])

    df2 = pd.DataFrame(df2)

    df2 = df2.set_axis(['degenerate triplet', 'translate', 'possible aa', 'P_sum', 'P_product', 'P_terminate'], axis=1)
    df2 = df2.sort_values(by=['P_product'], ascending=False)
    if allow_stop == False:
        col = [x for x in range(df2.shape[0]) if list(df2['P_terminate'])[x] == 0]
        df2 = df2.iloc[col, :]
        # print(df2)

    codon_detail = df2.iloc[0]
    codon = df2.iloc[0].tolist()[0]

    if printout:
        print(f"TARGET: {''.join(target)}")
        print(codon_detail)
        # print('\t{}'.format(codon))
        # print('\ti.e. {}'.format(expand_degenerate_codon(codon)))
        # print('\t\t{}'.format(codon_detail['translate']))

    return df2, codon_detail, codon


def Degenerate_chooser_partition(codon_table, target,
                                 output_filename=None, printout=True, allow_stop=True):
    from itertools import combinations

    my_list = list(target)

    # Generate all possible ways to separate the list into two groups
    all_separations = []
    j0 = int(len(my_list) / 2)
    for i in range(j0 - 1, j0 + 1):
        separations = list(combinations(my_list, i))
        # print(separations)
        all_separations.extend([(set(group), set(my_list) - set(group)) for group in separations])

    df_evaluate = pd.DataFrame(columns=['partition_a', 'codon_a', 'translate_a',
                                        'partition_b', 'codon_b', 'translate_b', 'product'])

    for partition in all_separations:
        a, b = partition
        a = ''.join(a)
        b = ''.join(b)
        df, codon_detail_a, codon_a = Degenerate_Chooser(codon_table, target=a,
                                                         allow_stop=allow_stop, printout=False)
        df, codon_detail_b, codon_b = Degenerate_Chooser(codon_table, target=b,
                                                         allow_stop=allow_stop, printout=False)

        data_a = codon_detail_a['translate']
        data_b = codon_detail_b['translate']
        data = data_a + data_b
        df = pd.DataFrame(data, columns=['amino acid', 'P'])

        # Combine rows with the same amino acid and sum up the values of P
        df = df.groupby('amino acid', as_index=False).sum()
        mydict = dict(zip(df['amino acid'], df['P']))

        p = 1
        for j in target:
            p = p * mydict[j]

        # New row data
        new_row = {'partition_a': a,
                   'codon_a': codon_a,
                   'translate_a': codon_detail_a['translate'],
                   'partition_b': b,
                   'codon_b': codon_b,
                   'translate_b': codon_detail_b['translate'],
                   'product': p}

        # Add the new row to the DataFrame using loc
        df_evaluate.loc[len(df_evaluate)] = new_row

    if output_filename is not None:
        Output_csv(df_evaluate, output_filename)

    # Find the index of the row with the largest 'product' value
    max_index = df_evaluate['product'].idxmax()

    # Retrieve the row with the largest 'product' value using loc
    df2 = df_evaluate.loc[max_index]
    codon_a = df2['codon_a']
    codon_b = df2['codon_b']

    if printout:
        print(f"============================================ Partition {target}")
        print(f'\n\n{df2}')
        print('\t{}'.format(codon_a))
        # print('\ti.e. {}'.format(expand_degenerate_codon(codon_a)))
        print('\t{}'.format(codon_b))
        # print('\ti.e. {}'.format(expand_degenerate_codon(codon_b)))

    df4 = pd.DataFrame(columns=['partition', 'codon', 'codon_expand', 'translate'])

    new_row = {'partition': df2['partition_a'],
               'codon': df2['codon_a'],
               # 'codon_expand': expand_degenerate_codon(codon_a),
               'translate': codon_detail_a['translate']}
    df4.loc[len(df4)] = new_row

    new_row = {'partition': df2['partition_b'],
               'codon': df2['codon_b'],
               # 'codon_expand': expand_degenerate_codon(codon_b),
               'translate': codon_detail_b['translate']}
    df4.loc[len(df4)] = new_row

    # return df4
    return df2, codon_a, codon_b, df4


# ------------------------------------------  codon_optimization & diagnosis (from source string

def extract_cocoputs(species='ecoli', save_csv=False):
    """
    species could either be 'ecoli', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    these will be converted to scientic names
    """

    dict0 = {'ecoli': 'Escherichia coli B',
             'ecoliK': 'Escherichia coli K-12',
             'bacillus': 'Bacillus subtilis',
             'yeast': 'Saccharomyces cerevisiae',
             'pichia': 'Komagataella phaffii',
             'mouse': 'Mus musculus',
             'hamster': 'Cricetulus griseus',
             'human': 'Homo sapiens'}
    if species in dict0.keys():
        species = dict0[species]  # convert common name to scientific name

    output_dir = 'dataset'
    import pandas as pd
    from io import StringIO

    # Step 1: load the CSV string directly into a dataframe
    source_string = '''SPECIES,TAXID,ORGANELLE,SOURCE,#CODON PAIRS,#CDS,GC%,GC1%,GC2%,GC3%,TTTTTT,TTTTTC,TTTTTA,TTTTTG,TTTCTT,TTTCTC,TTTCTA,TTTCTG,TTTATT,TTTATC,TTTATA,TTTATG,TTTGTT,TTTGTC,TTTGTA,TTTGTG,TTTTAT,TTTTAC,TTTTAA,TTTTAG,TTTCAT,TTTCAC,TTTCAA,TTTCAG,TTTAAT,TTTAAC,TTTAAA,TTTAAG,TTTGAT,TTTGAC,TTTGAA,TTTGAG,TTTTCT,TTTTCC,TTTTCA,TTTTCG,TTTCCT,TTTCCC,TTTCCA,TTTCCG,TTTACT,TTTACC,TTTACA,TTTACG,TTTGCT,TTTGCC,TTTGCA,TTTGCG,TTTTGT,TTTTGC,TTTTGA,TTTTGG,TTTCGT,TTTCGC,TTTCGA,TTTCGG,TTTAGT,TTTAGC,TTTAGA,TTTAGG,TTTGGT,TTTGGC,TTTGGA,TTTGGG,TTCTTT,TTCTTC,TTCTTA,TTCTTG,TTCCTT,TTCCTC,TTCCTA,TTCCTG,TTCATT,TTCATC,TTCATA,TTCATG,TTCGTT,TTCGTC,TTCGTA,TTCGTG,TTCTAT,TTCTAC,TTCTAA,TTCTAG,TTCCAT,TTCCAC,TTCCAA,TTCCAG,TTCAAT,TTCAAC,TTCAAA,TTCAAG,TTCGAT,TTCGAC,TTCGAA,TTCGAG,TTCTCT,TTCTCC,TTCTCA,TTCTCG,TTCCCT,TTCCCC,TTCCCA,TTCCCG,TTCACT,TTCACC,TTCACA,TTCACG,TTCGCT,TTCGCC,TTCGCA,TTCGCG,TTCTGT,TTCTGC,TTCTGA,TTCTGG,TTCCGT,TTCCGC,TTCCGA,TTCCGG,TTCAGT,TTCAGC,TTCAGA,TTCAGG,TTCGGT,TTCGGC,TTCGGA,TTCGGG,TTATTT,TTATTC,TTATTA,TTATTG,TTACTT,TTACTC,TTACTA,TTACTG,TTAATT,TTAATC,TTAATA,TTAATG,TTAGTT,TTAGTC,TTAGTA,TTAGTG,TTATAT,TTATAC,TTATAA,TTATAG,TTACAT,TTACAC,TTACAA,TTACAG,TTAAAT,TTAAAC,TTAAAA,TTAAAG,TTAGAT,TTAGAC,TTAGAA,TTAGAG,TTATCT,TTATCC,TTATCA,TTATCG,TTACCT,TTACCC,TTACCA,TTACCG,TTAACT,TTAACC,TTAACA,TTAACG,TTAGCT,TTAGCC,TTAGCA,TTAGCG,TTATGT,TTATGC,TTATGA,TTATGG,TTACGT,TTACGC,TTACGA,TTACGG,TTAAGT,TTAAGC,TTAAGA,TTAAGG,TTAGGT,TTAGGC,TTAGGA,TTAGGG,TTGTTT,TTGTTC,TTGTTA,TTGTTG,TTGCTT,TTGCTC,TTGCTA,TTGCTG,TTGATT,TTGATC,TTGATA,TTGATG,TTGGTT,TTGGTC,TTGGTA,TTGGTG,TTGTAT,TTGTAC,TTGTAA,TTGTAG,TTGCAT,TTGCAC,TTGCAA,TTGCAG,TTGAAT,TTGAAC,TTGAAA,TTGAAG,TTGGAT,TTGGAC,TTGGAA,TTGGAG,TTGTCT,TTGTCC,TTGTCA,TTGTCG,TTGCCT,TTGCCC,TTGCCA,TTGCCG,TTGACT,TTGACC,TTGACA,TTGACG,TTGGCT,TTGGCC,TTGGCA,TTGGCG,TTGTGT,TTGTGC,TTGTGA,TTGTGG,TTGCGT,TTGCGC,TTGCGA,TTGCGG,TTGAGT,TTGAGC,TTGAGA,TTGAGG,TTGGGT,TTGGGC,TTGGGA,TTGGGG,CTTTTT,CTTTTC,CTTTTA,CTTTTG,CTTCTT,CTTCTC,CTTCTA,CTTCTG,CTTATT,CTTATC,CTTATA,CTTATG,CTTGTT,CTTGTC,CTTGTA,CTTGTG,CTTTAT,CTTTAC,CTTTAA,CTTTAG,CTTCAT,CTTCAC,CTTCAA,CTTCAG,CTTAAT,CTTAAC,CTTAAA,CTTAAG,CTTGAT,CTTGAC,CTTGAA,CTTGAG,CTTTCT,CTTTCC,CTTTCA,CTTTCG,CTTCCT,CTTCCC,CTTCCA,CTTCCG,CTTACT,CTTACC,CTTACA,CTTACG,CTTGCT,CTTGCC,CTTGCA,CTTGCG,CTTTGT,CTTTGC,CTTTGA,CTTTGG,CTTCGT,CTTCGC,CTTCGA,CTTCGG,CTTAGT,CTTAGC,CTTAGA,CTTAGG,CTTGGT,CTTGGC,CTTGGA,CTTGGG,CTCTTT,CTCTTC,CTCTTA,CTCTTG,CTCCTT,CTCCTC,CTCCTA,CTCCTG,CTCATT,CTCATC,CTCATA,CTCATG,CTCGTT,CTCGTC,CTCGTA,CTCGTG,CTCTAT,CTCTAC,CTCTAA,CTCTAG,CTCCAT,CTCCAC,CTCCAA,CTCCAG,CTCAAT,CTCAAC,CTCAAA,CTCAAG,CTCGAT,CTCGAC,CTCGAA,CTCGAG,CTCTCT,CTCTCC,CTCTCA,CTCTCG,CTCCCT,CTCCCC,CTCCCA,CTCCCG,CTCACT,CTCACC,CTCACA,CTCACG,CTCGCT,CTCGCC,CTCGCA,CTCGCG,CTCTGT,CTCTGC,CTCTGA,CTCTGG,CTCCGT,CTCCGC,CTCCGA,CTCCGG,CTCAGT,CTCAGC,CTCAGA,CTCAGG,CTCGGT,CTCGGC,CTCGGA,CTCGGG,CTATTT,CTATTC,CTATTA,CTATTG,CTACTT,CTACTC,CTACTA,CTACTG,CTAATT,CTAATC,CTAATA,CTAATG,CTAGTT,CTAGTC,CTAGTA,CTAGTG,CTATAT,CTATAC,CTATAA,CTATAG,CTACAT,CTACAC,CTACAA,CTACAG,CTAAAT,CTAAAC,CTAAAA,CTAAAG,CTAGAT,CTAGAC,CTAGAA,CTAGAG,CTATCT,CTATCC,CTATCA,CTATCG,CTACCT,CTACCC,CTACCA,CTACCG,CTAACT,CTAACC,CTAACA,CTAACG,CTAGCT,CTAGCC,CTAGCA,CTAGCG,CTATGT,CTATGC,CTATGA,CTATGG,CTACGT,CTACGC,CTACGA,CTACGG,CTAAGT,CTAAGC,CTAAGA,CTAAGG,CTAGGT,CTAGGC,CTAGGA,CTAGGG,CTGTTT,CTGTTC,CTGTTA,CTGTTG,CTGCTT,CTGCTC,CTGCTA,CTGCTG,CTGATT,CTGATC,CTGATA,CTGATG,CTGGTT,CTGGTC,CTGGTA,CTGGTG,CTGTAT,CTGTAC,CTGTAA,CTGTAG,CTGCAT,CTGCAC,CTGCAA,CTGCAG,CTGAAT,CTGAAC,CTGAAA,CTGAAG,CTGGAT,CTGGAC,CTGGAA,CTGGAG,CTGTCT,CTGTCC,CTGTCA,CTGTCG,CTGCCT,CTGCCC,CTGCCA,CTGCCG,CTGACT,CTGACC,CTGACA,CTGACG,CTGGCT,CTGGCC,CTGGCA,CTGGCG,CTGTGT,CTGTGC,CTGTGA,CTGTGG,CTGCGT,CTGCGC,CTGCGA,CTGCGG,CTGAGT,CTGAGC,CTGAGA,CTGAGG,CTGGGT,CTGGGC,CTGGGA,CTGGGG,ATTTTT,ATTTTC,ATTTTA,ATTTTG,ATTCTT,ATTCTC,ATTCTA,ATTCTG,ATTATT,ATTATC,ATTATA,ATTATG,ATTGTT,ATTGTC,ATTGTA,ATTGTG,ATTTAT,ATTTAC,ATTTAA,ATTTAG,ATTCAT,ATTCAC,ATTCAA,ATTCAG,ATTAAT,ATTAAC,ATTAAA,ATTAAG,ATTGAT,ATTGAC,ATTGAA,ATTGAG,ATTTCT,ATTTCC,ATTTCA,ATTTCG,ATTCCT,ATTCCC,ATTCCA,ATTCCG,ATTACT,ATTACC,ATTACA,ATTACG,ATTGCT,ATTGCC,ATTGCA,ATTGCG,ATTTGT,ATTTGC,ATTTGA,ATTTGG,ATTCGT,ATTCGC,ATTCGA,ATTCGG,ATTAGT,ATTAGC,ATTAGA,ATTAGG,ATTGGT,ATTGGC,ATTGGA,ATTGGG,ATCTTT,ATCTTC,ATCTTA,ATCTTG,ATCCTT,ATCCTC,ATCCTA,ATCCTG,ATCATT,ATCATC,ATCATA,ATCATG,ATCGTT,ATCGTC,ATCGTA,ATCGTG,ATCTAT,ATCTAC,ATCTAA,ATCTAG,ATCCAT,ATCCAC,ATCCAA,ATCCAG,ATCAAT,ATCAAC,ATCAAA,ATCAAG,ATCGAT,ATCGAC,ATCGAA,ATCGAG,ATCTCT,ATCTCC,ATCTCA,ATCTCG,ATCCCT,ATCCCC,ATCCCA,ATCCCG,ATCACT,ATCACC,ATCACA,ATCACG,ATCGCT,ATCGCC,ATCGCA,ATCGCG,ATCTGT,ATCTGC,ATCTGA,ATCTGG,ATCCGT,ATCCGC,ATCCGA,ATCCGG,ATCAGT,ATCAGC,ATCAGA,ATCAGG,ATCGGT,ATCGGC,ATCGGA,ATCGGG,ATATTT,ATATTC,ATATTA,ATATTG,ATACTT,ATACTC,ATACTA,ATACTG,ATAATT,ATAATC,ATAATA,ATAATG,ATAGTT,ATAGTC,ATAGTA,ATAGTG,ATATAT,ATATAC,ATATAA,ATATAG,ATACAT,ATACAC,ATACAA,ATACAG,ATAAAT,ATAAAC,ATAAAA,ATAAAG,ATAGAT,ATAGAC,ATAGAA,ATAGAG,ATATCT,ATATCC,ATATCA,ATATCG,ATACCT,ATACCC,ATACCA,ATACCG,ATAACT,ATAACC,ATAACA,ATAACG,ATAGCT,ATAGCC,ATAGCA,ATAGCG,ATATGT,ATATGC,ATATGA,ATATGG,ATACGT,ATACGC,ATACGA,ATACGG,ATAAGT,ATAAGC,ATAAGA,ATAAGG,ATAGGT,ATAGGC,ATAGGA,ATAGGG,ATGTTT,ATGTTC,ATGTTA,ATGTTG,ATGCTT,ATGCTC,ATGCTA,ATGCTG,ATGATT,ATGATC,ATGATA,ATGATG,ATGGTT,ATGGTC,ATGGTA,ATGGTG,ATGTAT,ATGTAC,ATGTAA,ATGTAG,ATGCAT,ATGCAC,ATGCAA,ATGCAG,ATGAAT,ATGAAC,ATGAAA,ATGAAG,ATGGAT,ATGGAC,ATGGAA,ATGGAG,ATGTCT,ATGTCC,ATGTCA,ATGTCG,ATGCCT,ATGCCC,ATGCCA,ATGCCG,ATGACT,ATGACC,ATGACA,ATGACG,ATGGCT,ATGGCC,ATGGCA,ATGGCG,ATGTGT,ATGTGC,ATGTGA,ATGTGG,ATGCGT,ATGCGC,ATGCGA,ATGCGG,ATGAGT,ATGAGC,ATGAGA,ATGAGG,ATGGGT,ATGGGC,ATGGGA,ATGGGG,GTTTTT,GTTTTC,GTTTTA,GTTTTG,GTTCTT,GTTCTC,GTTCTA,GTTCTG,GTTATT,GTTATC,GTTATA,GTTATG,GTTGTT,GTTGTC,GTTGTA,GTTGTG,GTTTAT,GTTTAC,GTTTAA,GTTTAG,GTTCAT,GTTCAC,GTTCAA,GTTCAG,GTTAAT,GTTAAC,GTTAAA,GTTAAG,GTTGAT,GTTGAC,GTTGAA,GTTGAG,GTTTCT,GTTTCC,GTTTCA,GTTTCG,GTTCCT,GTTCCC,GTTCCA,GTTCCG,GTTACT,GTTACC,GTTACA,GTTACG,GTTGCT,GTTGCC,GTTGCA,GTTGCG,GTTTGT,GTTTGC,GTTTGA,GTTTGG,GTTCGT,GTTCGC,GTTCGA,GTTCGG,GTTAGT,GTTAGC,GTTAGA,GTTAGG,GTTGGT,GTTGGC,GTTGGA,GTTGGG,GTCTTT,GTCTTC,GTCTTA,GTCTTG,GTCCTT,GTCCTC,GTCCTA,GTCCTG,GTCATT,GTCATC,GTCATA,GTCATG,GTCGTT,GTCGTC,GTCGTA,GTCGTG,GTCTAT,GTCTAC,GTCTAA,GTCTAG,GTCCAT,GTCCAC,GTCCAA,GTCCAG,GTCAAT,GTCAAC,GTCAAA,GTCAAG,GTCGAT,GTCGAC,GTCGAA,GTCGAG,GTCTCT,GTCTCC,GTCTCA,GTCTCG,GTCCCT,GTCCCC,GTCCCA,GTCCCG,GTCACT,GTCACC,GTCACA,GTCACG,GTCGCT,GTCGCC,GTCGCA,GTCGCG,GTCTGT,GTCTGC,GTCTGA,GTCTGG,GTCCGT,GTCCGC,GTCCGA,GTCCGG,GTCAGT,GTCAGC,GTCAGA,GTCAGG,GTCGGT,GTCGGC,GTCGGA,GTCGGG,GTATTT,GTATTC,GTATTA,GTATTG,GTACTT,GTACTC,GTACTA,GTACTG,GTAATT,GTAATC,GTAATA,GTAATG,GTAGTT,GTAGTC,GTAGTA,GTAGTG,GTATAT,GTATAC,GTATAA,GTATAG,GTACAT,GTACAC,GTACAA,GTACAG,GTAAAT,GTAAAC,GTAAAA,GTAAAG,GTAGAT,GTAGAC,GTAGAA,GTAGAG,GTATCT,GTATCC,GTATCA,GTATCG,GTACCT,GTACCC,GTACCA,GTACCG,GTAACT,GTAACC,GTAACA,GTAACG,GTAGCT,GTAGCC,GTAGCA,GTAGCG,GTATGT,GTATGC,GTATGA,GTATGG,GTACGT,GTACGC,GTACGA,GTACGG,GTAAGT,GTAAGC,GTAAGA,GTAAGG,GTAGGT,GTAGGC,GTAGGA,GTAGGG,GTGTTT,GTGTTC,GTGTTA,GTGTTG,GTGCTT,GTGCTC,GTGCTA,GTGCTG,GTGATT,GTGATC,GTGATA,GTGATG,GTGGTT,GTGGTC,GTGGTA,GTGGTG,GTGTAT,GTGTAC,GTGTAA,GTGTAG,GTGCAT,GTGCAC,GTGCAA,GTGCAG,GTGAAT,GTGAAC,GTGAAA,GTGAAG,GTGGAT,GTGGAC,GTGGAA,GTGGAG,GTGTCT,GTGTCC,GTGTCA,GTGTCG,GTGCCT,GTGCCC,GTGCCA,GTGCCG,GTGACT,GTGACC,GTGACA,GTGACG,GTGGCT,GTGGCC,GTGGCA,GTGGCG,GTGTGT,GTGTGC,GTGTGA,GTGTGG,GTGCGT,GTGCGC,GTGCGA,GTGCGG,GTGAGT,GTGAGC,GTGAGA,GTGAGG,GTGGGT,GTGGGC,GTGGGA,GTGGGG,TATTTT,TATTTC,TATTTA,TATTTG,TATCTT,TATCTC,TATCTA,TATCTG,TATATT,TATATC,TATATA,TATATG,TATGTT,TATGTC,TATGTA,TATGTG,TATTAT,TATTAC,TATTAA,TATTAG,TATCAT,TATCAC,TATCAA,TATCAG,TATAAT,TATAAC,TATAAA,TATAAG,TATGAT,TATGAC,TATGAA,TATGAG,TATTCT,TATTCC,TATTCA,TATTCG,TATCCT,TATCCC,TATCCA,TATCCG,TATACT,TATACC,TATACA,TATACG,TATGCT,TATGCC,TATGCA,TATGCG,TATTGT,TATTGC,TATTGA,TATTGG,TATCGT,TATCGC,TATCGA,TATCGG,TATAGT,TATAGC,TATAGA,TATAGG,TATGGT,TATGGC,TATGGA,TATGGG,TACTTT,TACTTC,TACTTA,TACTTG,TACCTT,TACCTC,TACCTA,TACCTG,TACATT,TACATC,TACATA,TACATG,TACGTT,TACGTC,TACGTA,TACGTG,TACTAT,TACTAC,TACTAA,TACTAG,TACCAT,TACCAC,TACCAA,TACCAG,TACAAT,TACAAC,TACAAA,TACAAG,TACGAT,TACGAC,TACGAA,TACGAG,TACTCT,TACTCC,TACTCA,TACTCG,TACCCT,TACCCC,TACCCA,TACCCG,TACACT,TACACC,TACACA,TACACG,TACGCT,TACGCC,TACGCA,TACGCG,TACTGT,TACTGC,TACTGA,TACTGG,TACCGT,TACCGC,TACCGA,TACCGG,TACAGT,TACAGC,TACAGA,TACAGG,TACGGT,TACGGC,TACGGA,TACGGG,TAATTT,TAATTC,TAATTA,TAATTG,TAACTT,TAACTC,TAACTA,TAACTG,TAAATT,TAAATC,TAAATA,TAAATG,TAAGTT,TAAGTC,TAAGTA,TAAGTG,TAATAT,TAATAC,TAATAA,TAATAG,TAACAT,TAACAC,TAACAA,TAACAG,TAAAAT,TAAAAC,TAAAAA,TAAAAG,TAAGAT,TAAGAC,TAAGAA,TAAGAG,TAATCT,TAATCC,TAATCA,TAATCG,TAACCT,TAACCC,TAACCA,TAACCG,TAAACT,TAAACC,TAAACA,TAAACG,TAAGCT,TAAGCC,TAAGCA,TAAGCG,TAATGT,TAATGC,TAATGA,TAATGG,TAACGT,TAACGC,TAACGA,TAACGG,TAAAGT,TAAAGC,TAAAGA,TAAAGG,TAAGGT,TAAGGC,TAAGGA,TAAGGG,TAGTTT,TAGTTC,TAGTTA,TAGTTG,TAGCTT,TAGCTC,TAGCTA,TAGCTG,TAGATT,TAGATC,TAGATA,TAGATG,TAGGTT,TAGGTC,TAGGTA,TAGGTG,TAGTAT,TAGTAC,TAGTAA,TAGTAG,TAGCAT,TAGCAC,TAGCAA,TAGCAG,TAGAAT,TAGAAC,TAGAAA,TAGAAG,TAGGAT,TAGGAC,TAGGAA,TAGGAG,TAGTCT,TAGTCC,TAGTCA,TAGTCG,TAGCCT,TAGCCC,TAGCCA,TAGCCG,TAGACT,TAGACC,TAGACA,TAGACG,TAGGCT,TAGGCC,TAGGCA,TAGGCG,TAGTGT,TAGTGC,TAGTGA,TAGTGG,TAGCGT,TAGCGC,TAGCGA,TAGCGG,TAGAGT,TAGAGC,TAGAGA,TAGAGG,TAGGGT,TAGGGC,TAGGGA,TAGGGG,CATTTT,CATTTC,CATTTA,CATTTG,CATCTT,CATCTC,CATCTA,CATCTG,CATATT,CATATC,CATATA,CATATG,CATGTT,CATGTC,CATGTA,CATGTG,CATTAT,CATTAC,CATTAA,CATTAG,CATCAT,CATCAC,CATCAA,CATCAG,CATAAT,CATAAC,CATAAA,CATAAG,CATGAT,CATGAC,CATGAA,CATGAG,CATTCT,CATTCC,CATTCA,CATTCG,CATCCT,CATCCC,CATCCA,CATCCG,CATACT,CATACC,CATACA,CATACG,CATGCT,CATGCC,CATGCA,CATGCG,CATTGT,CATTGC,CATTGA,CATTGG,CATCGT,CATCGC,CATCGA,CATCGG,CATAGT,CATAGC,CATAGA,CATAGG,CATGGT,CATGGC,CATGGA,CATGGG,CACTTT,CACTTC,CACTTA,CACTTG,CACCTT,CACCTC,CACCTA,CACCTG,CACATT,CACATC,CACATA,CACATG,CACGTT,CACGTC,CACGTA,CACGTG,CACTAT,CACTAC,CACTAA,CACTAG,CACCAT,CACCAC,CACCAA,CACCAG,CACAAT,CACAAC,CACAAA,CACAAG,CACGAT,CACGAC,CACGAA,CACGAG,CACTCT,CACTCC,CACTCA,CACTCG,CACCCT,CACCCC,CACCCA,CACCCG,CACACT,CACACC,CACACA,CACACG,CACGCT,CACGCC,CACGCA,CACGCG,CACTGT,CACTGC,CACTGA,CACTGG,CACCGT,CACCGC,CACCGA,CACCGG,CACAGT,CACAGC,CACAGA,CACAGG,CACGGT,CACGGC,CACGGA,CACGGG,CAATTT,CAATTC,CAATTA,CAATTG,CAACTT,CAACTC,CAACTA,CAACTG,CAAATT,CAAATC,CAAATA,CAAATG,CAAGTT,CAAGTC,CAAGTA,CAAGTG,CAATAT,CAATAC,CAATAA,CAATAG,CAACAT,CAACAC,CAACAA,CAACAG,CAAAAT,CAAAAC,CAAAAA,CAAAAG,CAAGAT,CAAGAC,CAAGAA,CAAGAG,CAATCT,CAATCC,CAATCA,CAATCG,CAACCT,CAACCC,CAACCA,CAACCG,CAAACT,CAAACC,CAAACA,CAAACG,CAAGCT,CAAGCC,CAAGCA,CAAGCG,CAATGT,CAATGC,CAATGA,CAATGG,CAACGT,CAACGC,CAACGA,CAACGG,CAAAGT,CAAAGC,CAAAGA,CAAAGG,CAAGGT,CAAGGC,CAAGGA,CAAGGG,CAGTTT,CAGTTC,CAGTTA,CAGTTG,CAGCTT,CAGCTC,CAGCTA,CAGCTG,CAGATT,CAGATC,CAGATA,CAGATG,CAGGTT,CAGGTC,CAGGTA,CAGGTG,CAGTAT,CAGTAC,CAGTAA,CAGTAG,CAGCAT,CAGCAC,CAGCAA,CAGCAG,CAGAAT,CAGAAC,CAGAAA,CAGAAG,CAGGAT,CAGGAC,CAGGAA,CAGGAG,CAGTCT,CAGTCC,CAGTCA,CAGTCG,CAGCCT,CAGCCC,CAGCCA,CAGCCG,CAGACT,CAGACC,CAGACA,CAGACG,CAGGCT,CAGGCC,CAGGCA,CAGGCG,CAGTGT,CAGTGC,CAGTGA,CAGTGG,CAGCGT,CAGCGC,CAGCGA,CAGCGG,CAGAGT,CAGAGC,CAGAGA,CAGAGG,CAGGGT,CAGGGC,CAGGGA,CAGGGG,AATTTT,AATTTC,AATTTA,AATTTG,AATCTT,AATCTC,AATCTA,AATCTG,AATATT,AATATC,AATATA,AATATG,AATGTT,AATGTC,AATGTA,AATGTG,AATTAT,AATTAC,AATTAA,AATTAG,AATCAT,AATCAC,AATCAA,AATCAG,AATAAT,AATAAC,AATAAA,AATAAG,AATGAT,AATGAC,AATGAA,AATGAG,AATTCT,AATTCC,AATTCA,AATTCG,AATCCT,AATCCC,AATCCA,AATCCG,AATACT,AATACC,AATACA,AATACG,AATGCT,AATGCC,AATGCA,AATGCG,AATTGT,AATTGC,AATTGA,AATTGG,AATCGT,AATCGC,AATCGA,AATCGG,AATAGT,AATAGC,AATAGA,AATAGG,AATGGT,AATGGC,AATGGA,AATGGG,AACTTT,AACTTC,AACTTA,AACTTG,AACCTT,AACCTC,AACCTA,AACCTG,AACATT,AACATC,AACATA,AACATG,AACGTT,AACGTC,AACGTA,AACGTG,AACTAT,AACTAC,AACTAA,AACTAG,AACCAT,AACCAC,AACCAA,AACCAG,AACAAT,AACAAC,AACAAA,AACAAG,AACGAT,AACGAC,AACGAA,AACGAG,AACTCT,AACTCC,AACTCA,AACTCG,AACCCT,AACCCC,AACCCA,AACCCG,AACACT,AACACC,AACACA,AACACG,AACGCT,AACGCC,AACGCA,AACGCG,AACTGT,AACTGC,AACTGA,AACTGG,AACCGT,AACCGC,AACCGA,AACCGG,AACAGT,AACAGC,AACAGA,AACAGG,AACGGT,AACGGC,AACGGA,AACGGG,AAATTT,AAATTC,AAATTA,AAATTG,AAACTT,AAACTC,AAACTA,AAACTG,AAAATT,AAAATC,AAAATA,AAAATG,AAAGTT,AAAGTC,AAAGTA,AAAGTG,AAATAT,AAATAC,AAATAA,AAATAG,AAACAT,AAACAC,AAACAA,AAACAG,AAAAAT,AAAAAC,AAAAAA,AAAAAG,AAAGAT,AAAGAC,AAAGAA,AAAGAG,AAATCT,AAATCC,AAATCA,AAATCG,AAACCT,AAACCC,AAACCA,AAACCG,AAAACT,AAAACC,AAAACA,AAAACG,AAAGCT,AAAGCC,AAAGCA,AAAGCG,AAATGT,AAATGC,AAATGA,AAATGG,AAACGT,AAACGC,AAACGA,AAACGG,AAAAGT,AAAAGC,AAAAGA,AAAAGG,AAAGGT,AAAGGC,AAAGGA,AAAGGG,AAGTTT,AAGTTC,AAGTTA,AAGTTG,AAGCTT,AAGCTC,AAGCTA,AAGCTG,AAGATT,AAGATC,AAGATA,AAGATG,AAGGTT,AAGGTC,AAGGTA,AAGGTG,AAGTAT,AAGTAC,AAGTAA,AAGTAG,AAGCAT,AAGCAC,AAGCAA,AAGCAG,AAGAAT,AAGAAC,AAGAAA,AAGAAG,AAGGAT,AAGGAC,AAGGAA,AAGGAG,AAGTCT,AAGTCC,AAGTCA,AAGTCG,AAGCCT,AAGCCC,AAGCCA,AAGCCG,AAGACT,AAGACC,AAGACA,AAGACG,AAGGCT,AAGGCC,AAGGCA,AAGGCG,AAGTGT,AAGTGC,AAGTGA,AAGTGG,AAGCGT,AAGCGC,AAGCGA,AAGCGG,AAGAGT,AAGAGC,AAGAGA,AAGAGG,AAGGGT,AAGGGC,AAGGGA,AAGGGG,GATTTT,GATTTC,GATTTA,GATTTG,GATCTT,GATCTC,GATCTA,GATCTG,GATATT,GATATC,GATATA,GATATG,GATGTT,GATGTC,GATGTA,GATGTG,GATTAT,GATTAC,GATTAA,GATTAG,GATCAT,GATCAC,GATCAA,GATCAG,GATAAT,GATAAC,GATAAA,GATAAG,GATGAT,GATGAC,GATGAA,GATGAG,GATTCT,GATTCC,GATTCA,GATTCG,GATCCT,GATCCC,GATCCA,GATCCG,GATACT,GATACC,GATACA,GATACG,GATGCT,GATGCC,GATGCA,GATGCG,GATTGT,GATTGC,GATTGA,GATTGG,GATCGT,GATCGC,GATCGA,GATCGG,GATAGT,GATAGC,GATAGA,GATAGG,GATGGT,GATGGC,GATGGA,GATGGG,GACTTT,GACTTC,GACTTA,GACTTG,GACCTT,GACCTC,GACCTA,GACCTG,GACATT,GACATC,GACATA,GACATG,GACGTT,GACGTC,GACGTA,GACGTG,GACTAT,GACTAC,GACTAA,GACTAG,GACCAT,GACCAC,GACCAA,GACCAG,GACAAT,GACAAC,GACAAA,GACAAG,GACGAT,GACGAC,GACGAA,GACGAG,GACTCT,GACTCC,GACTCA,GACTCG,GACCCT,GACCCC,GACCCA,GACCCG,GACACT,GACACC,GACACA,GACACG,GACGCT,GACGCC,GACGCA,GACGCG,GACTGT,GACTGC,GACTGA,GACTGG,GACCGT,GACCGC,GACCGA,GACCGG,GACAGT,GACAGC,GACAGA,GACAGG,GACGGT,GACGGC,GACGGA,GACGGG,GAATTT,GAATTC,GAATTA,GAATTG,GAACTT,GAACTC,GAACTA,GAACTG,GAAATT,GAAATC,GAAATA,GAAATG,GAAGTT,GAAGTC,GAAGTA,GAAGTG,GAATAT,GAATAC,GAATAA,GAATAG,GAACAT,GAACAC,GAACAA,GAACAG,GAAAAT,GAAAAC,GAAAAA,GAAAAG,GAAGAT,GAAGAC,GAAGAA,GAAGAG,GAATCT,GAATCC,GAATCA,GAATCG,GAACCT,GAACCC,GAACCA,GAACCG,GAAACT,GAAACC,GAAACA,GAAACG,GAAGCT,GAAGCC,GAAGCA,GAAGCG,GAATGT,GAATGC,GAATGA,GAATGG,GAACGT,GAACGC,GAACGA,GAACGG,GAAAGT,GAAAGC,GAAAGA,GAAAGG,GAAGGT,GAAGGC,GAAGGA,GAAGGG,GAGTTT,GAGTTC,GAGTTA,GAGTTG,GAGCTT,GAGCTC,GAGCTA,GAGCTG,GAGATT,GAGATC,GAGATA,GAGATG,GAGGTT,GAGGTC,GAGGTA,GAGGTG,GAGTAT,GAGTAC,GAGTAA,GAGTAG,GAGCAT,GAGCAC,GAGCAA,GAGCAG,GAGAAT,GAGAAC,GAGAAA,GAGAAG,GAGGAT,GAGGAC,GAGGAA,GAGGAG,GAGTCT,GAGTCC,GAGTCA,GAGTCG,GAGCCT,GAGCCC,GAGCCA,GAGCCG,GAGACT,GAGACC,GAGACA,GAGACG,GAGGCT,GAGGCC,GAGGCA,GAGGCG,GAGTGT,GAGTGC,GAGTGA,GAGTGG,GAGCGT,GAGCGC,GAGCGA,GAGCGG,GAGAGT,GAGAGC,GAGAGA,GAGAGG,GAGGGT,GAGGGC,GAGGGA,GAGGGG,TCTTTT,TCTTTC,TCTTTA,TCTTTG,TCTCTT,TCTCTC,TCTCTA,TCTCTG,TCTATT,TCTATC,TCTATA,TCTATG,TCTGTT,TCTGTC,TCTGTA,TCTGTG,TCTTAT,TCTTAC,TCTTAA,TCTTAG,TCTCAT,TCTCAC,TCTCAA,TCTCAG,TCTAAT,TCTAAC,TCTAAA,TCTAAG,TCTGAT,TCTGAC,TCTGAA,TCTGAG,TCTTCT,TCTTCC,TCTTCA,TCTTCG,TCTCCT,TCTCCC,TCTCCA,TCTCCG,TCTACT,TCTACC,TCTACA,TCTACG,TCTGCT,TCTGCC,TCTGCA,TCTGCG,TCTTGT,TCTTGC,TCTTGA,TCTTGG,TCTCGT,TCTCGC,TCTCGA,TCTCGG,TCTAGT,TCTAGC,TCTAGA,TCTAGG,TCTGGT,TCTGGC,TCTGGA,TCTGGG,TCCTTT,TCCTTC,TCCTTA,TCCTTG,TCCCTT,TCCCTC,TCCCTA,TCCCTG,TCCATT,TCCATC,TCCATA,TCCATG,TCCGTT,TCCGTC,TCCGTA,TCCGTG,TCCTAT,TCCTAC,TCCTAA,TCCTAG,TCCCAT,TCCCAC,TCCCAA,TCCCAG,TCCAAT,TCCAAC,TCCAAA,TCCAAG,TCCGAT,TCCGAC,TCCGAA,TCCGAG,TCCTCT,TCCTCC,TCCTCA,TCCTCG,TCCCCT,TCCCCC,TCCCCA,TCCCCG,TCCACT,TCCACC,TCCACA,TCCACG,TCCGCT,TCCGCC,TCCGCA,TCCGCG,TCCTGT,TCCTGC,TCCTGA,TCCTGG,TCCCGT,TCCCGC,TCCCGA,TCCCGG,TCCAGT,TCCAGC,TCCAGA,TCCAGG,TCCGGT,TCCGGC,TCCGGA,TCCGGG,TCATTT,TCATTC,TCATTA,TCATTG,TCACTT,TCACTC,TCACTA,TCACTG,TCAATT,TCAATC,TCAATA,TCAATG,TCAGTT,TCAGTC,TCAGTA,TCAGTG,TCATAT,TCATAC,TCATAA,TCATAG,TCACAT,TCACAC,TCACAA,TCACAG,TCAAAT,TCAAAC,TCAAAA,TCAAAG,TCAGAT,TCAGAC,TCAGAA,TCAGAG,TCATCT,TCATCC,TCATCA,TCATCG,TCACCT,TCACCC,TCACCA,TCACCG,TCAACT,TCAACC,TCAACA,TCAACG,TCAGCT,TCAGCC,TCAGCA,TCAGCG,TCATGT,TCATGC,TCATGA,TCATGG,TCACGT,TCACGC,TCACGA,TCACGG,TCAAGT,TCAAGC,TCAAGA,TCAAGG,TCAGGT,TCAGGC,TCAGGA,TCAGGG,TCGTTT,TCGTTC,TCGTTA,TCGTTG,TCGCTT,TCGCTC,TCGCTA,TCGCTG,TCGATT,TCGATC,TCGATA,TCGATG,TCGGTT,TCGGTC,TCGGTA,TCGGTG,TCGTAT,TCGTAC,TCGTAA,TCGTAG,TCGCAT,TCGCAC,TCGCAA,TCGCAG,TCGAAT,TCGAAC,TCGAAA,TCGAAG,TCGGAT,TCGGAC,TCGGAA,TCGGAG,TCGTCT,TCGTCC,TCGTCA,TCGTCG,TCGCCT,TCGCCC,TCGCCA,TCGCCG,TCGACT,TCGACC,TCGACA,TCGACG,TCGGCT,TCGGCC,TCGGCA,TCGGCG,TCGTGT,TCGTGC,TCGTGA,TCGTGG,TCGCGT,TCGCGC,TCGCGA,TCGCGG,TCGAGT,TCGAGC,TCGAGA,TCGAGG,TCGGGT,TCGGGC,TCGGGA,TCGGGG,CCTTTT,CCTTTC,CCTTTA,CCTTTG,CCTCTT,CCTCTC,CCTCTA,CCTCTG,CCTATT,CCTATC,CCTATA,CCTATG,CCTGTT,CCTGTC,CCTGTA,CCTGTG,CCTTAT,CCTTAC,CCTTAA,CCTTAG,CCTCAT,CCTCAC,CCTCAA,CCTCAG,CCTAAT,CCTAAC,CCTAAA,CCTAAG,CCTGAT,CCTGAC,CCTGAA,CCTGAG,CCTTCT,CCTTCC,CCTTCA,CCTTCG,CCTCCT,CCTCCC,CCTCCA,CCTCCG,CCTACT,CCTACC,CCTACA,CCTACG,CCTGCT,CCTGCC,CCTGCA,CCTGCG,CCTTGT,CCTTGC,CCTTGA,CCTTGG,CCTCGT,CCTCGC,CCTCGA,CCTCGG,CCTAGT,CCTAGC,CCTAGA,CCTAGG,CCTGGT,CCTGGC,CCTGGA,CCTGGG,CCCTTT,CCCTTC,CCCTTA,CCCTTG,CCCCTT,CCCCTC,CCCCTA,CCCCTG,CCCATT,CCCATC,CCCATA,CCCATG,CCCGTT,CCCGTC,CCCGTA,CCCGTG,CCCTAT,CCCTAC,CCCTAA,CCCTAG,CCCCAT,CCCCAC,CCCCAA,CCCCAG,CCCAAT,CCCAAC,CCCAAA,CCCAAG,CCCGAT,CCCGAC,CCCGAA,CCCGAG,CCCTCT,CCCTCC,CCCTCA,CCCTCG,CCCCCT,CCCCCC,CCCCCA,CCCCCG,CCCACT,CCCACC,CCCACA,CCCACG,CCCGCT,CCCGCC,CCCGCA,CCCGCG,CCCTGT,CCCTGC,CCCTGA,CCCTGG,CCCCGT,CCCCGC,CCCCGA,CCCCGG,CCCAGT,CCCAGC,CCCAGA,CCCAGG,CCCGGT,CCCGGC,CCCGGA,CCCGGG,CCATTT,CCATTC,CCATTA,CCATTG,CCACTT,CCACTC,CCACTA,CCACTG,CCAATT,CCAATC,CCAATA,CCAATG,CCAGTT,CCAGTC,CCAGTA,CCAGTG,CCATAT,CCATAC,CCATAA,CCATAG,CCACAT,CCACAC,CCACAA,CCACAG,CCAAAT,CCAAAC,CCAAAA,CCAAAG,CCAGAT,CCAGAC,CCAGAA,CCAGAG,CCATCT,CCATCC,CCATCA,CCATCG,CCACCT,CCACCC,CCACCA,CCACCG,CCAACT,CCAACC,CCAACA,CCAACG,CCAGCT,CCAGCC,CCAGCA,CCAGCG,CCATGT,CCATGC,CCATGA,CCATGG,CCACGT,CCACGC,CCACGA,CCACGG,CCAAGT,CCAAGC,CCAAGA,CCAAGG,CCAGGT,CCAGGC,CCAGGA,CCAGGG,CCGTTT,CCGTTC,CCGTTA,CCGTTG,CCGCTT,CCGCTC,CCGCTA,CCGCTG,CCGATT,CCGATC,CCGATA,CCGATG,CCGGTT,CCGGTC,CCGGTA,CCGGTG,CCGTAT,CCGTAC,CCGTAA,CCGTAG,CCGCAT,CCGCAC,CCGCAA,CCGCAG,CCGAAT,CCGAAC,CCGAAA,CCGAAG,CCGGAT,CCGGAC,CCGGAA,CCGGAG,CCGTCT,CCGTCC,CCGTCA,CCGTCG,CCGCCT,CCGCCC,CCGCCA,CCGCCG,CCGACT,CCGACC,CCGACA,CCGACG,CCGGCT,CCGGCC,CCGGCA,CCGGCG,CCGTGT,CCGTGC,CCGTGA,CCGTGG,CCGCGT,CCGCGC,CCGCGA,CCGCGG,CCGAGT,CCGAGC,CCGAGA,CCGAGG,CCGGGT,CCGGGC,CCGGGA,CCGGGG,ACTTTT,ACTTTC,ACTTTA,ACTTTG,ACTCTT,ACTCTC,ACTCTA,ACTCTG,ACTATT,ACTATC,ACTATA,ACTATG,ACTGTT,ACTGTC,ACTGTA,ACTGTG,ACTTAT,ACTTAC,ACTTAA,ACTTAG,ACTCAT,ACTCAC,ACTCAA,ACTCAG,ACTAAT,ACTAAC,ACTAAA,ACTAAG,ACTGAT,ACTGAC,ACTGAA,ACTGAG,ACTTCT,ACTTCC,ACTTCA,ACTTCG,ACTCCT,ACTCCC,ACTCCA,ACTCCG,ACTACT,ACTACC,ACTACA,ACTACG,ACTGCT,ACTGCC,ACTGCA,ACTGCG,ACTTGT,ACTTGC,ACTTGA,ACTTGG,ACTCGT,ACTCGC,ACTCGA,ACTCGG,ACTAGT,ACTAGC,ACTAGA,ACTAGG,ACTGGT,ACTGGC,ACTGGA,ACTGGG,ACCTTT,ACCTTC,ACCTTA,ACCTTG,ACCCTT,ACCCTC,ACCCTA,ACCCTG,ACCATT,ACCATC,ACCATA,ACCATG,ACCGTT,ACCGTC,ACCGTA,ACCGTG,ACCTAT,ACCTAC,ACCTAA,ACCTAG,ACCCAT,ACCCAC,ACCCAA,ACCCAG,ACCAAT,ACCAAC,ACCAAA,ACCAAG,ACCGAT,ACCGAC,ACCGAA,ACCGAG,ACCTCT,ACCTCC,ACCTCA,ACCTCG,ACCCCT,ACCCCC,ACCCCA,ACCCCG,ACCACT,ACCACC,ACCACA,ACCACG,ACCGCT,ACCGCC,ACCGCA,ACCGCG,ACCTGT,ACCTGC,ACCTGA,ACCTGG,ACCCGT,ACCCGC,ACCCGA,ACCCGG,ACCAGT,ACCAGC,ACCAGA,ACCAGG,ACCGGT,ACCGGC,ACCGGA,ACCGGG,ACATTT,ACATTC,ACATTA,ACATTG,ACACTT,ACACTC,ACACTA,ACACTG,ACAATT,ACAATC,ACAATA,ACAATG,ACAGTT,ACAGTC,ACAGTA,ACAGTG,ACATAT,ACATAC,ACATAA,ACATAG,ACACAT,ACACAC,ACACAA,ACACAG,ACAAAT,ACAAAC,ACAAAA,ACAAAG,ACAGAT,ACAGAC,ACAGAA,ACAGAG,ACATCT,ACATCC,ACATCA,ACATCG,ACACCT,ACACCC,ACACCA,ACACCG,ACAACT,ACAACC,ACAACA,ACAACG,ACAGCT,ACAGCC,ACAGCA,ACAGCG,ACATGT,ACATGC,ACATGA,ACATGG,ACACGT,ACACGC,ACACGA,ACACGG,ACAAGT,ACAAGC,ACAAGA,ACAAGG,ACAGGT,ACAGGC,ACAGGA,ACAGGG,ACGTTT,ACGTTC,ACGTTA,ACGTTG,ACGCTT,ACGCTC,ACGCTA,ACGCTG,ACGATT,ACGATC,ACGATA,ACGATG,ACGGTT,ACGGTC,ACGGTA,ACGGTG,ACGTAT,ACGTAC,ACGTAA,ACGTAG,ACGCAT,ACGCAC,ACGCAA,ACGCAG,ACGAAT,ACGAAC,ACGAAA,ACGAAG,ACGGAT,ACGGAC,ACGGAA,ACGGAG,ACGTCT,ACGTCC,ACGTCA,ACGTCG,ACGCCT,ACGCCC,ACGCCA,ACGCCG,ACGACT,ACGACC,ACGACA,ACGACG,ACGGCT,ACGGCC,ACGGCA,ACGGCG,ACGTGT,ACGTGC,ACGTGA,ACGTGG,ACGCGT,ACGCGC,ACGCGA,ACGCGG,ACGAGT,ACGAGC,ACGAGA,ACGAGG,ACGGGT,ACGGGC,ACGGGA,ACGGGG,GCTTTT,GCTTTC,GCTTTA,GCTTTG,GCTCTT,GCTCTC,GCTCTA,GCTCTG,GCTATT,GCTATC,GCTATA,GCTATG,GCTGTT,GCTGTC,GCTGTA,GCTGTG,GCTTAT,GCTTAC,GCTTAA,GCTTAG,GCTCAT,GCTCAC,GCTCAA,GCTCAG,GCTAAT,GCTAAC,GCTAAA,GCTAAG,GCTGAT,GCTGAC,GCTGAA,GCTGAG,GCTTCT,GCTTCC,GCTTCA,GCTTCG,GCTCCT,GCTCCC,GCTCCA,GCTCCG,GCTACT,GCTACC,GCTACA,GCTACG,GCTGCT,GCTGCC,GCTGCA,GCTGCG,GCTTGT,GCTTGC,GCTTGA,GCTTGG,GCTCGT,GCTCGC,GCTCGA,GCTCGG,GCTAGT,GCTAGC,GCTAGA,GCTAGG,GCTGGT,GCTGGC,GCTGGA,GCTGGG,GCCTTT,GCCTTC,GCCTTA,GCCTTG,GCCCTT,GCCCTC,GCCCTA,GCCCTG,GCCATT,GCCATC,GCCATA,GCCATG,GCCGTT,GCCGTC,GCCGTA,GCCGTG,GCCTAT,GCCTAC,GCCTAA,GCCTAG,GCCCAT,GCCCAC,GCCCAA,GCCCAG,GCCAAT,GCCAAC,GCCAAA,GCCAAG,GCCGAT,GCCGAC,GCCGAA,GCCGAG,GCCTCT,GCCTCC,GCCTCA,GCCTCG,GCCCCT,GCCCCC,GCCCCA,GCCCCG,GCCACT,GCCACC,GCCACA,GCCACG,GCCGCT,GCCGCC,GCCGCA,GCCGCG,GCCTGT,GCCTGC,GCCTGA,GCCTGG,GCCCGT,GCCCGC,GCCCGA,GCCCGG,GCCAGT,GCCAGC,GCCAGA,GCCAGG,GCCGGT,GCCGGC,GCCGGA,GCCGGG,GCATTT,GCATTC,GCATTA,GCATTG,GCACTT,GCACTC,GCACTA,GCACTG,GCAATT,GCAATC,GCAATA,GCAATG,GCAGTT,GCAGTC,GCAGTA,GCAGTG,GCATAT,GCATAC,GCATAA,GCATAG,GCACAT,GCACAC,GCACAA,GCACAG,GCAAAT,GCAAAC,GCAAAA,GCAAAG,GCAGAT,GCAGAC,GCAGAA,GCAGAG,GCATCT,GCATCC,GCATCA,GCATCG,GCACCT,GCACCC,GCACCA,GCACCG,GCAACT,GCAACC,GCAACA,GCAACG,GCAGCT,GCAGCC,GCAGCA,GCAGCG,GCATGT,GCATGC,GCATGA,GCATGG,GCACGT,GCACGC,GCACGA,GCACGG,GCAAGT,GCAAGC,GCAAGA,GCAAGG,GCAGGT,GCAGGC,GCAGGA,GCAGGG,GCGTTT,GCGTTC,GCGTTA,GCGTTG,GCGCTT,GCGCTC,GCGCTA,GCGCTG,GCGATT,GCGATC,GCGATA,GCGATG,GCGGTT,GCGGTC,GCGGTA,GCGGTG,GCGTAT,GCGTAC,GCGTAA,GCGTAG,GCGCAT,GCGCAC,GCGCAA,GCGCAG,GCGAAT,GCGAAC,GCGAAA,GCGAAG,GCGGAT,GCGGAC,GCGGAA,GCGGAG,GCGTCT,GCGTCC,GCGTCA,GCGTCG,GCGCCT,GCGCCC,GCGCCA,GCGCCG,GCGACT,GCGACC,GCGACA,GCGACG,GCGGCT,GCGGCC,GCGGCA,GCGGCG,GCGTGT,GCGTGC,GCGTGA,GCGTGG,GCGCGT,GCGCGC,GCGCGA,GCGCGG,GCGAGT,GCGAGC,GCGAGA,GCGAGG,GCGGGT,GCGGGC,GCGGGA,GCGGGG,TGTTTT,TGTTTC,TGTTTA,TGTTTG,TGTCTT,TGTCTC,TGTCTA,TGTCTG,TGTATT,TGTATC,TGTATA,TGTATG,TGTGTT,TGTGTC,TGTGTA,TGTGTG,TGTTAT,TGTTAC,TGTTAA,TGTTAG,TGTCAT,TGTCAC,TGTCAA,TGTCAG,TGTAAT,TGTAAC,TGTAAA,TGTAAG,TGTGAT,TGTGAC,TGTGAA,TGTGAG,TGTTCT,TGTTCC,TGTTCA,TGTTCG,TGTCCT,TGTCCC,TGTCCA,TGTCCG,TGTACT,TGTACC,TGTACA,TGTACG,TGTGCT,TGTGCC,TGTGCA,TGTGCG,TGTTGT,TGTTGC,TGTTGA,TGTTGG,TGTCGT,TGTCGC,TGTCGA,TGTCGG,TGTAGT,TGTAGC,TGTAGA,TGTAGG,TGTGGT,TGTGGC,TGTGGA,TGTGGG,TGCTTT,TGCTTC,TGCTTA,TGCTTG,TGCCTT,TGCCTC,TGCCTA,TGCCTG,TGCATT,TGCATC,TGCATA,TGCATG,TGCGTT,TGCGTC,TGCGTA,TGCGTG,TGCTAT,TGCTAC,TGCTAA,TGCTAG,TGCCAT,TGCCAC,TGCCAA,TGCCAG,TGCAAT,TGCAAC,TGCAAA,TGCAAG,TGCGAT,TGCGAC,TGCGAA,TGCGAG,TGCTCT,TGCTCC,TGCTCA,TGCTCG,TGCCCT,TGCCCC,TGCCCA,TGCCCG,TGCACT,TGCACC,TGCACA,TGCACG,TGCGCT,TGCGCC,TGCGCA,TGCGCG,TGCTGT,TGCTGC,TGCTGA,TGCTGG,TGCCGT,TGCCGC,TGCCGA,TGCCGG,TGCAGT,TGCAGC,TGCAGA,TGCAGG,TGCGGT,TGCGGC,TGCGGA,TGCGGG,TGATTT,TGATTC,TGATTA,TGATTG,TGACTT,TGACTC,TGACTA,TGACTG,TGAATT,TGAATC,TGAATA,TGAATG,TGAGTT,TGAGTC,TGAGTA,TGAGTG,TGATAT,TGATAC,TGATAA,TGATAG,TGACAT,TGACAC,TGACAA,TGACAG,TGAAAT,TGAAAC,TGAAAA,TGAAAG,TGAGAT,TGAGAC,TGAGAA,TGAGAG,TGATCT,TGATCC,TGATCA,TGATCG,TGACCT,TGACCC,TGACCA,TGACCG,TGAACT,TGAACC,TGAACA,TGAACG,TGAGCT,TGAGCC,TGAGCA,TGAGCG,TGATGT,TGATGC,TGATGA,TGATGG,TGACGT,TGACGC,TGACGA,TGACGG,TGAAGT,TGAAGC,TGAAGA,TGAAGG,TGAGGT,TGAGGC,TGAGGA,TGAGGG,TGGTTT,TGGTTC,TGGTTA,TGGTTG,TGGCTT,TGGCTC,TGGCTA,TGGCTG,TGGATT,TGGATC,TGGATA,TGGATG,TGGGTT,TGGGTC,TGGGTA,TGGGTG,TGGTAT,TGGTAC,TGGTAA,TGGTAG,TGGCAT,TGGCAC,TGGCAA,TGGCAG,TGGAAT,TGGAAC,TGGAAA,TGGAAG,TGGGAT,TGGGAC,TGGGAA,TGGGAG,TGGTCT,TGGTCC,TGGTCA,TGGTCG,TGGCCT,TGGCCC,TGGCCA,TGGCCG,TGGACT,TGGACC,TGGACA,TGGACG,TGGGCT,TGGGCC,TGGGCA,TGGGCG,TGGTGT,TGGTGC,TGGTGA,TGGTGG,TGGCGT,TGGCGC,TGGCGA,TGGCGG,TGGAGT,TGGAGC,TGGAGA,TGGAGG,TGGGGT,TGGGGC,TGGGGA,TGGGGG,CGTTTT,CGTTTC,CGTTTA,CGTTTG,CGTCTT,CGTCTC,CGTCTA,CGTCTG,CGTATT,CGTATC,CGTATA,CGTATG,CGTGTT,CGTGTC,CGTGTA,CGTGTG,CGTTAT,CGTTAC,CGTTAA,CGTTAG,CGTCAT,CGTCAC,CGTCAA,CGTCAG,CGTAAT,CGTAAC,CGTAAA,CGTAAG,CGTGAT,CGTGAC,CGTGAA,CGTGAG,CGTTCT,CGTTCC,CGTTCA,CGTTCG,CGTCCT,CGTCCC,CGTCCA,CGTCCG,CGTACT,CGTACC,CGTACA,CGTACG,CGTGCT,CGTGCC,CGTGCA,CGTGCG,CGTTGT,CGTTGC,CGTTGA,CGTTGG,CGTCGT,CGTCGC,CGTCGA,CGTCGG,CGTAGT,CGTAGC,CGTAGA,CGTAGG,CGTGGT,CGTGGC,CGTGGA,CGTGGG,CGCTTT,CGCTTC,CGCTTA,CGCTTG,CGCCTT,CGCCTC,CGCCTA,CGCCTG,CGCATT,CGCATC,CGCATA,CGCATG,CGCGTT,CGCGTC,CGCGTA,CGCGTG,CGCTAT,CGCTAC,CGCTAA,CGCTAG,CGCCAT,CGCCAC,CGCCAA,CGCCAG,CGCAAT,CGCAAC,CGCAAA,CGCAAG,CGCGAT,CGCGAC,CGCGAA,CGCGAG,CGCTCT,CGCTCC,CGCTCA,CGCTCG,CGCCCT,CGCCCC,CGCCCA,CGCCCG,CGCACT,CGCACC,CGCACA,CGCACG,CGCGCT,CGCGCC,CGCGCA,CGCGCG,CGCTGT,CGCTGC,CGCTGA,CGCTGG,CGCCGT,CGCCGC,CGCCGA,CGCCGG,CGCAGT,CGCAGC,CGCAGA,CGCAGG,CGCGGT,CGCGGC,CGCGGA,CGCGGG,CGATTT,CGATTC,CGATTA,CGATTG,CGACTT,CGACTC,CGACTA,CGACTG,CGAATT,CGAATC,CGAATA,CGAATG,CGAGTT,CGAGTC,CGAGTA,CGAGTG,CGATAT,CGATAC,CGATAA,CGATAG,CGACAT,CGACAC,CGACAA,CGACAG,CGAAAT,CGAAAC,CGAAAA,CGAAAG,CGAGAT,CGAGAC,CGAGAA,CGAGAG,CGATCT,CGATCC,CGATCA,CGATCG,CGACCT,CGACCC,CGACCA,CGACCG,CGAACT,CGAACC,CGAACA,CGAACG,CGAGCT,CGAGCC,CGAGCA,CGAGCG,CGATGT,CGATGC,CGATGA,CGATGG,CGACGT,CGACGC,CGACGA,CGACGG,CGAAGT,CGAAGC,CGAAGA,CGAAGG,CGAGGT,CGAGGC,CGAGGA,CGAGGG,CGGTTT,CGGTTC,CGGTTA,CGGTTG,CGGCTT,CGGCTC,CGGCTA,CGGCTG,CGGATT,CGGATC,CGGATA,CGGATG,CGGGTT,CGGGTC,CGGGTA,CGGGTG,CGGTAT,CGGTAC,CGGTAA,CGGTAG,CGGCAT,CGGCAC,CGGCAA,CGGCAG,CGGAAT,CGGAAC,CGGAAA,CGGAAG,CGGGAT,CGGGAC,CGGGAA,CGGGAG,CGGTCT,CGGTCC,CGGTCA,CGGTCG,CGGCCT,CGGCCC,CGGCCA,CGGCCG,CGGACT,CGGACC,CGGACA,CGGACG,CGGGCT,CGGGCC,CGGGCA,CGGGCG,CGGTGT,CGGTGC,CGGTGA,CGGTGG,CGGCGT,CGGCGC,CGGCGA,CGGCGG,CGGAGT,CGGAGC,CGGAGA,CGGAGG,CGGGGT,CGGGGC,CGGGGA,CGGGGG,AGTTTT,AGTTTC,AGTTTA,AGTTTG,AGTCTT,AGTCTC,AGTCTA,AGTCTG,AGTATT,AGTATC,AGTATA,AGTATG,AGTGTT,AGTGTC,AGTGTA,AGTGTG,AGTTAT,AGTTAC,AGTTAA,AGTTAG,AGTCAT,AGTCAC,AGTCAA,AGTCAG,AGTAAT,AGTAAC,AGTAAA,AGTAAG,AGTGAT,AGTGAC,AGTGAA,AGTGAG,AGTTCT,AGTTCC,AGTTCA,AGTTCG,AGTCCT,AGTCCC,AGTCCA,AGTCCG,AGTACT,AGTACC,AGTACA,AGTACG,AGTGCT,AGTGCC,AGTGCA,AGTGCG,AGTTGT,AGTTGC,AGTTGA,AGTTGG,AGTCGT,AGTCGC,AGTCGA,AGTCGG,AGTAGT,AGTAGC,AGTAGA,AGTAGG,AGTGGT,AGTGGC,AGTGGA,AGTGGG,AGCTTT,AGCTTC,AGCTTA,AGCTTG,AGCCTT,AGCCTC,AGCCTA,AGCCTG,AGCATT,AGCATC,AGCATA,AGCATG,AGCGTT,AGCGTC,AGCGTA,AGCGTG,AGCTAT,AGCTAC,AGCTAA,AGCTAG,AGCCAT,AGCCAC,AGCCAA,AGCCAG,AGCAAT,AGCAAC,AGCAAA,AGCAAG,AGCGAT,AGCGAC,AGCGAA,AGCGAG,AGCTCT,AGCTCC,AGCTCA,AGCTCG,AGCCCT,AGCCCC,AGCCCA,AGCCCG,AGCACT,AGCACC,AGCACA,AGCACG,AGCGCT,AGCGCC,AGCGCA,AGCGCG,AGCTGT,AGCTGC,AGCTGA,AGCTGG,AGCCGT,AGCCGC,AGCCGA,AGCCGG,AGCAGT,AGCAGC,AGCAGA,AGCAGG,AGCGGT,AGCGGC,AGCGGA,AGCGGG,AGATTT,AGATTC,AGATTA,AGATTG,AGACTT,AGACTC,AGACTA,AGACTG,AGAATT,AGAATC,AGAATA,AGAATG,AGAGTT,AGAGTC,AGAGTA,AGAGTG,AGATAT,AGATAC,AGATAA,AGATAG,AGACAT,AGACAC,AGACAA,AGACAG,AGAAAT,AGAAAC,AGAAAA,AGAAAG,AGAGAT,AGAGAC,AGAGAA,AGAGAG,AGATCT,AGATCC,AGATCA,AGATCG,AGACCT,AGACCC,AGACCA,AGACCG,AGAACT,AGAACC,AGAACA,AGAACG,AGAGCT,AGAGCC,AGAGCA,AGAGCG,AGATGT,AGATGC,AGATGA,AGATGG,AGACGT,AGACGC,AGACGA,AGACGG,AGAAGT,AGAAGC,AGAAGA,AGAAGG,AGAGGT,AGAGGC,AGAGGA,AGAGGG,AGGTTT,AGGTTC,AGGTTA,AGGTTG,AGGCTT,AGGCTC,AGGCTA,AGGCTG,AGGATT,AGGATC,AGGATA,AGGATG,AGGGTT,AGGGTC,AGGGTA,AGGGTG,AGGTAT,AGGTAC,AGGTAA,AGGTAG,AGGCAT,AGGCAC,AGGCAA,AGGCAG,AGGAAT,AGGAAC,AGGAAA,AGGAAG,AGGGAT,AGGGAC,AGGGAA,AGGGAG,AGGTCT,AGGTCC,AGGTCA,AGGTCG,AGGCCT,AGGCCC,AGGCCA,AGGCCG,AGGACT,AGGACC,AGGACA,AGGACG,AGGGCT,AGGGCC,AGGGCA,AGGGCG,AGGTGT,AGGTGC,AGGTGA,AGGTGG,AGGCGT,AGGCGC,AGGCGA,AGGCGG,AGGAGT,AGGAGC,AGGAGA,AGGAGG,AGGGGT,AGGGGC,AGGGGA,AGGGGG,GGTTTT,GGTTTC,GGTTTA,GGTTTG,GGTCTT,GGTCTC,GGTCTA,GGTCTG,GGTATT,GGTATC,GGTATA,GGTATG,GGTGTT,GGTGTC,GGTGTA,GGTGTG,GGTTAT,GGTTAC,GGTTAA,GGTTAG,GGTCAT,GGTCAC,GGTCAA,GGTCAG,GGTAAT,GGTAAC,GGTAAA,GGTAAG,GGTGAT,GGTGAC,GGTGAA,GGTGAG,GGTTCT,GGTTCC,GGTTCA,GGTTCG,GGTCCT,GGTCCC,GGTCCA,GGTCCG,GGTACT,GGTACC,GGTACA,GGTACG,GGTGCT,GGTGCC,GGTGCA,GGTGCG,GGTTGT,GGTTGC,GGTTGA,GGTTGG,GGTCGT,GGTCGC,GGTCGA,GGTCGG,GGTAGT,GGTAGC,GGTAGA,GGTAGG,GGTGGT,GGTGGC,GGTGGA,GGTGGG,GGCTTT,GGCTTC,GGCTTA,GGCTTG,GGCCTT,GGCCTC,GGCCTA,GGCCTG,GGCATT,GGCATC,GGCATA,GGCATG,GGCGTT,GGCGTC,GGCGTA,GGCGTG,GGCTAT,GGCTAC,GGCTAA,GGCTAG,GGCCAT,GGCCAC,GGCCAA,GGCCAG,GGCAAT,GGCAAC,GGCAAA,GGCAAG,GGCGAT,GGCGAC,GGCGAA,GGCGAG,GGCTCT,GGCTCC,GGCTCA,GGCTCG,GGCCCT,GGCCCC,GGCCCA,GGCCCG,GGCACT,GGCACC,GGCACA,GGCACG,GGCGCT,GGCGCC,GGCGCA,GGCGCG,GGCTGT,GGCTGC,GGCTGA,GGCTGG,GGCCGT,GGCCGC,GGCCGA,GGCCGG,GGCAGT,GGCAGC,GGCAGA,GGCAGG,GGCGGT,GGCGGC,GGCGGA,GGCGGG,GGATTT,GGATTC,GGATTA,GGATTG,GGACTT,GGACTC,GGACTA,GGACTG,GGAATT,GGAATC,GGAATA,GGAATG,GGAGTT,GGAGTC,GGAGTA,GGAGTG,GGATAT,GGATAC,GGATAA,GGATAG,GGACAT,GGACAC,GGACAA,GGACAG,GGAAAT,GGAAAC,GGAAAA,GGAAAG,GGAGAT,GGAGAC,GGAGAA,GGAGAG,GGATCT,GGATCC,GGATCA,GGATCG,GGACCT,GGACCC,GGACCA,GGACCG,GGAACT,GGAACC,GGAACA,GGAACG,GGAGCT,GGAGCC,GGAGCA,GGAGCG,GGATGT,GGATGC,GGATGA,GGATGG,GGACGT,GGACGC,GGACGA,GGACGG,GGAAGT,GGAAGC,GGAAGA,GGAAGG,GGAGGT,GGAGGC,GGAGGA,GGAGGG,GGGTTT,GGGTTC,GGGTTA,GGGTTG,GGGCTT,GGGCTC,GGGCTA,GGGCTG,GGGATT,GGGATC,GGGATA,GGGATG,GGGGTT,GGGGTC,GGGGTA,GGGGTG,GGGTAT,GGGTAC,GGGTAA,GGGTAG,GGGCAT,GGGCAC,GGGCAA,GGGCAG,GGGAAT,GGGAAC,GGGAAA,GGGAAG,GGGGAT,GGGGAC,GGGGAA,GGGGAG,GGGTCT,GGGTCC,GGGTCA,GGGTCG,GGGCCT,GGGCCC,GGGCCA,GGGCCG,GGGACT,GGGACC,GGGACA,GGGACG,GGGGCT,GGGGCC,GGGGCA,GGGGCG,GGGTGT,GGGTGC,GGGTGA,GGGTGG,GGGCGT,GGGCGC,GGGCGA,GGGCGG,GGGAGT,GGGAGC,GGGAGA,GGGAGG,GGGGGT,GGGGGC,GGGGGA,GGGGGG
Escherichia coli B,37762,genomic,RefSeq,13068340,42583,51.78,59,40.79,55.67,4726,4846,4788,3888,3140,3646,449,6471,13121,11464,1335,9528,7311,7798,2079,6399,5786,3253,466,70,3180,1835,1220,4663,6557,8132,8302,2614,11705,7002,11352,4722,3482,3737,2729,2307,1655,1472,1077,3430,3948,10288,1547,3397,7625,16084,3663,6927,1581,1987,201,1003,3438,4226,364,511,2210,4483,304,134,12081,12158,1044,1459,6344,6554,1201,1053,2786,5458,146,10552,3587,4218,382,2315,3366,2915,1142,2361,3439,3274,162,23,2832,2856,379,7400,3629,5474,5739,1460,6534,5033,4878,2019,3340,4105,2079,3055,2023,1518,1264,7921,2751,7188,1180,2031,3100,6481,1900,3024,1663,2343,693,7551,5770,6978,340,1147,3225,6386,915,736,6047,5910,773,1376,4007,2358,4527,4193,2848,2831,740,10173,6344,4501,1182,6149,1720,2002,848,2519,1807,739,158,48,2118,1426,3481,5970,3706,2405,6583,1776,2510,923,2340,1189,1645,1703,1523,2291,2438,2729,1661,6225,2072,6649,1652,4702,1480,2975,1873,3492,1218,1353,312,2906,4694,5561,715,1216,3947,5928,816,368,4229,3896,1080,2027,4767,3420,3666,5189,3629,3498,1521,18319,7926,4335,1031,6681,2091,1238,1037,2831,2486,1197,260,112,3036,1780,4250,9647,3160,1795,4509,1683,1735,392,996,536,1234,780,1578,2584,2324,1929,2854,6516,1234,2843,930,2432,1651,1120,2226,3034,1127,1110,120,3070,5220,5079,858,1401,2081,2381,298,236,2088,2222,1172,1987,3529,2160,1926,1511,1467,1211,265,2849,3649,4350,575,975,1829,1520,613,1262,4423,2626,369,71,1673,920,659,2962,4763,4545,3574,1804,8877,2772,6575,5057,5018,5671,2852,2909,1660,1457,753,2054,1304,2883,780,1065,3158,6608,2503,3776,1426,1582,113,1134,1495,1712,217,308,839,2935,159,60,3788,6197,1000,1819,2777,1757,553,341,713,471,52,1627,3109,2855,320,1101,1381,1241,429,890,4250,3245,117,8,982,739,292,2006,5815,6289,3951,1826,8814,7951,5198,1186,4083,4242,1648,1711,805,1116,256,1258,2097,5335,849,1609,2400,6117,2000,3105,1263,1662,197,3058,700,842,154,465,2002,2933,427,359,7096,8928,1346,2207,1754,739,1344,1306,938,952,385,3240,1246,1004,364,1397,203,162,115,295,578,368,113,6,965,669,2222,1829,1259,1180,2754,677,290,143,396,262,424,358,402,653,915,893,827,2286,542,1355,629,917,217,391,302,447,314,338,172,1197,1668,2193,389,599,856,1183,229,146,317,349,202,250,16429,10887,7398,8709,6975,6561,2637,35841,19714,12458,2620,19864,14120,11265,9411,31832,7193,4825,844,85,9066,5445,14649,5694,11295,11513,25321,6937,24067,9735,34384,14143,3067,1671,3174,5435,4897,3733,6374,17065,6522,16213,5738,12412,13550,10316,26140,45761,2449,3477,130,7592,17280,16489,2009,3081,3238,5059,585,332,10709,14057,5076,9527,7537,7260,4525,6335,5218,6089,557,15508,12620,11703,974,7990,8799,9331,1903,8592,7069,4383,505,51,5239,3654,3046,12408,7479,8986,10637,3959,15277,6608,17470,7948,4540,4615,3142,3348,4282,3449,3166,8746,4335,10439,1857,3923,9370,20128,5469,10680,2138,2955,133,1653,8345,9516,642,945,1672,4130,387,99,13496,15206,1200,2034,4275,6023,1304,1094,3077,6635,280,9650,8166,10379,627,6932,6734,7303,1680,5523,3809,4485,280,28,2877,3229,1160,6118,6846,11331,10630,3619,10103,12164,11298,3865,3532,4893,1410,2156,2685,2633,2048,8011,4824,13137,1523,3213,6928,16324,4148,6717,1643,2504,282,7206,5884,8236,411,1170,5166,9642,904,858,9710,11494,1100,2270,2312,1295,1499,1307,867,716,215,1725,1415,1115,774,1316,853,817,422,868,884,462,154,48,592,340,841,1147,2137,1420,3505,1039,1717,865,2230,1003,878,765,871,591,680,577,586,1187,791,1887,928,1215,846,1679,1142,1240,432,337,68,651,779,898,249,281,663,1276,516,225,1170,1123,368,583,6349,5768,3557,6448,3801,5153,1495,21001,9828,8951,1449,11774,5859,5124,2883,11548,4222,3277,390,43,3456,3312,5487,10933,7302,7845,13358,5287,9996,5576,11962,4767,3248,2719,2797,4344,3069,1935,4019,8673,3416,9992,3335,6963,6227,5091,8761,17245,1458,1533,121,3691,7776,7913,1180,1425,4636,6675,769,374,4872,10763,3327,5923,4626,3656,2661,2487,2088,2227,407,7749,7277,8434,693,2870,5079,3986,1762,3715,6764,4173,473,76,2672,2617,1143,6132,4717,7602,6580,2829,12058,5296,12740,6848,5153,5014,2520,3059,2410,1787,1286,5078,2217,4822,1198,2287,6277,9795,3993,6264,1568,1960,141,823,4087,4289,445,555,1018,2368,221,84,6602,8791,998,2308,4884,3413,967,742,1013,944,93,3237,7804,5428,745,4154,3984,2899,1431,3885,3502,2360,91,11,1722,937,334,2306,4804,4332,4999,883,11422,3061,6693,3495,2237,2198,915,1453,932,864,370,1890,3647,8184,1737,3829,4191,8116,3093,5835,1496,1982,268,7007,2355,2253,239,833,4870,8344,1226,954,7990,8020,1511,3524,4124,2599,3526,3755,1975,1488,571,10590,3069,1951,868,4711,1573,1359,1216,3832,1123,939,191,35,1610,1067,2511,4766,2930,2922,7214,1328,3291,1690,5747,2533,1142,1145,1061,1684,1096,868,1387,5020,1589,3086,1547,3514,1390,2068,2259,4226,764,581,216,1993,3828,3409,516,805,1398,1904,596,279,2720,2366,852,1517,6187,4462,3926,5978,3738,3681,1542,28196,14504,9372,1636,15383,8454,6224,4644,19052,2991,1248,318,77,4076,1522,4243,9210,6191,4777,14371,5292,8988,3203,10105,4819,1306,819,1261,2326,2532,1153,3185,9531,3304,6674,2713,6655,4441,3254,7725,17354,955,1296,161,2932,8382,7526,1038,2226,2688,3412,515,366,4924,5127,1822,3558,4707,4830,3434,3079,3420,4953,756,12675,4770,5808,827,4593,3835,4479,1397,4258,2908,4538,392,26,2320,3702,4350,10431,1721,5337,5666,1668,4009,6453,7709,3267,1360,2790,1899,1475,1785,2050,1670,6374,953,6082,916,1897,2581,7572,3029,5256,906,1574,163,796,4406,7065,794,1351,619,2318,201,71,4503,6529,1230,1088,2790,3748,671,608,1364,1675,146,6745,3513,4639,380,2672,2663,2224,1040,2219,2066,3291,277,20,1695,1737,1060,4977,1767,5329,4790,1263,5388,4839,4758,1911,1411,2159,963,1213,850,828,926,3535,1433,6319,871,1460,2430,5367,2213,3588,852,1844,133,5112,3557,4204,521,1243,2102,5877,462,310,5891,7084,1070,1540,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4248,3201,2690,2636,3120,2407,591,9012,6031,4841,649,4013,2731,2485,1213,3487,3131,3225,774,34,3145,2456,2730,7253,2482,4228,5347,1539,3601,3512,6672,2927,1084,1198,1218,1062,2287,1557,1925,6087,1422,4006,805,1727,2413,4445,2131,4391,772,1089,186,557,3030,4170,461,1088,760,1880,165,49,3156,3671,871,895,2850,2878,655,547,1127,887,133,4589,3134,2751,294,1520,2985,2359,1326,414,2932,2464,457,18,2059,1631,685,3669,2028,2880,2839,1029,4742,3149,3789,1650,1232,1415,907,931,947,542,773,2951,959,3165,568,984,2117,4138,1848,2978,978,1413,199,4489,2797,2757,419,779,1730,3004,203,201,5459,5690,907,1448,3628,1815,3167,2643,3638,3248,1041,13606,6366,6182,1478,4738,1529,1064,733,1934,4034,2410,957,94,3588,2157,7274,7506,4818,5715,9956,2975,2193,1232,3997,2782,1632,1768,1587,1473,2177,1456,1834,5150,2201,5864,2012,4037,1458,2963,1648,3025,958,887,432,3254,5372,4581,1544,1840,2799,4419,540,291,3137,3310,1461,2588,8168,6269,6105,7147,6974,3914,2381,10882,8325,6244,2067,8695,8644,5539,5400,12300,5272,4510,917,110,6133,3849,12733,14644,4119,6000,9430,3240,12741,6534,15751,7676,2317,1988,2767,3784,2920,1618,4290,8444,2488,5536,2539,4603,7664,8408,11837,20405,1374,1936,205,6147,10282,7090,2661,3143,2111,3885,491,278,5673,11101,4353,6960,4030,3604,3486,2641,3299,3676,718,9876,10090,8626,1363,6706,3793,4375,1621,4351,3558,3169,662,72,3076,2258,3593,8000,6223,6944,9309,2603,6754,5415,9950,4195,1355,1083,1443,956,2253,1814,2551,6359,2399,6626,1896,3316,3852,9094,3873,6786,723,881,150,450,3071,4097,703,1030,1658,2919,347,87,6043,7893,1575,1415,4839,6137,1847,1311,2730,3205,345,14018,6430,6687,685,4944,5542,6611,2657,6544,4806,5119,454,51,3303,2964,2066,8144,4389,6317,8268,2976,9215,6479,9850,3827,1795,2603,1753,2008,1800,1444,2587,9565,2109,7332,1412,2743,3885,10897,3733,6493,1519,2172,327,7799,6354,6895,915,1769,3784,7451,905,579,9996,11790,1973,2601,5457,5466,5287,3452,3719,5106,1547,20265,10535,11539,3463,9724,6715,7271,3767,13798,7266,5496,2306,202,4617,3435,6483,10537,10102,10446,15183,5967,15340,9186,15961,15349,3120,3815,3610,4527,3274,2726,3774,10499,3848,12116,5205,9144,5058,13407,9263,18746,1415,1863,614,4685,7790,9740,1566,2244,3546,5988,1355,640,10039,14258,3190,6303,3379,2099,1903,1912,1605,1943,1122,10554,4139,3150,933,3473,2435,1864,1405,3468,1924,1490,1190,152,2178,1743,3775,6378,2430,2509,8106,2467,2871,1395,2723,1886,1153,784,1125,1436,1513,1166,2298,4194,775,1652,1026,1227,1870,1737,2366,4202,526,621,205,1815,4191,4034,1134,1434,1161,1720,358,225,1028,2225,1047,1352,10326,8736,8019,6142,4602,7773,993,15771,16424,16325,1613,11094,8416,8459,3619,11652,8254,8438,853,81,3660,4139,4737,9207,7256,12766,17055,5125,13077,10512,21596,10271,2401,3031,2316,2300,3298,2949,3115,10103,3166,10373,2078,4513,7513,15222,6933,14385,1439,2131,112,721,5901,8491,636,1582,1855,4666,325,130,9343,12530,2308,1901,4055,4494,1750,1221,2279,2074,326,9914,5414,5709,532,4151,5765,4036,2498,5399,4124,4324,339,31,2736,2246,1373,6093,4064,6389,9375,3063,9524,5669,10769,4701,1620,2556,1470,1376,1080,822,1281,5950,2110,6552,1354,2970,4157,7828,3877,6463,1325,2397,342,9971,5606,5236,847,1497,4320,8904,1523,1089,8746,9485,1918,2719,8217,3590,5575,4284,4281,3854,1480,27129,13318,13950,3405,12041,8817,7715,4154,18426,7835,5643,1305,94,6359,4220,10138,13733,11069,14716,23818,6609,18665,8571,21522,19341,3242,3980,3124,2906,2839,2501,2496,8470,4157,14140,4667,9384,6875,14497,9619,21482,1979,2028,409,5847,9940,9838,1610,2994,4989,8630,1386,904,12886,14794,3806,8475,7781,5071,4320,4889,3569,907,1752,17884,7055,7561,1530,9345,2633,2057,1387,4451,4121,3227,1066,141,4578,3481,8154,13209,4013,4306,11291,4348,3331,1682,4698,2421,2017,1766,1929,2458,1676,499,2731,5733,894,751,1545,3182,2372,3034,3358,6968,1491,1752,345,4915,8167,7052,1844,2935,1899,3075,555,421,1692,2496,1216,1990,2568,2063,1665,1612,1649,1232,361,5040,3306,3065,402,1529,3234,2014,1709,1782,2337,1766,202,14,1415,1526,865,2250,1222,2594,1867,551,3806,4182,5403,1345,2105,2215,1657,1362,960,810,752,2361,1010,2497,716,1095,2567,4620,2705,4146,497,524,45,122,1894,2193,184,147,110,75,51,26,4670,5134,707,418,1963,1869,889,685,913,819,170,3367,3455,3488,396,2074,2511,1874,1608,2212,1103,1189,57,2,905,879,479,1975,1358,2266,1650,472,3625,2421,2306,1226,1116,1295,893,745,928,715,651,1584,1554,3854,917,1959,2046,3148,2739,2183,1237,1477,440,3507,2789,3444,628,781,2249,4435,561,277,6520,6802,1468,2544,2604,1539,2859,2007,1627,1575,865,6112,2137,1519,761,3267,1335,1149,1409,1779,741,554,178,34,1099,889,2391,2142,1291,1260,2983,771,2076,1238,3826,1458,1114,1056,1618,1447,1037,784,1505,3268,859,2325,1561,2098,1156,2115,2405,2532,326,536,367,1678,1486,2233,525,773,489,618,371,185,2249,2077,1329,1072,2854,1707,2290,2701,2307,2117,1528,13924,3494,1774,697,4553,2207,1856,2644,5014,819,376,167,69,1604,1101,3270,3399,1067,1008,3140,960,1487,806,2694,749,625,571,999,1004,1087,970,2454,3760,619,1747,987,1779,1345,1063,3306,4176,257,355,69,1188,2502,3137,592,1091,331,486,110,63,1421,1114,679,856,2606,1806,1551,1026,845,607,222,2131,1547,1552,275,786,3079,2082,1544,1960,3177,2110,169,29,1150,642,584,1221,1122,1607,1596,557,4546,3781,6389,2249,1863,1890,1683,1263,524,538,486,936,588,999,419,762,2706,4304,2888,4755,503,708,20,208,1038,1078,166,160,76,141,31,18,2829,4936,963,979,1631,1298,673,539,477,443,122,1224,2279,2046,396,854,2435,1831,898,1604,1392,1091,55,11,697,430,350,1019,1564,1399,1620,270,3805,1830,2136,840,668,816,714,513,403,287,222,402,643,1637,590,871,1737,3238,2305,2237,660,898,169,2239,923,1091,264,456,739,1760,338,112,2913,3760,1321,639,2197,1648,2527,2135,1179,1039,713,5177,2093,1952,607,3194,1336,944,1688,2521,982,784,149,21,1409,1213,3578,3374,1764,2127,3858,983,2972,2575,6741,2792,755,801,1356,1142,769,420,1350,2605,1011,3072,1587,2490,1342,2106,2174,2728,343,468,215,870,1639,2409,617,749,560,1086,269,80,2498,3639,1607,1342,7142,5873,4533,4998,3351,3758,2664,23720,7109,4002,1133,8228,7319,4174,7158,10805,3728,2303,298,26,4451,3237,8213,11313,3058,4181,8924,2682,10676,5851,18425,5805,1748,1418,2380,2361,1663,1190,3874,6053,2080,4272,2230,4218,3241,2114,8401,9137,588,1137,63,6429,6042,6357,961,536,893,1644,172,92,5247,6158,2909,3504,3111,2856,1547,1350,1241,1420,379,4574,3953,3738,359,1356,2356,2071,1341,1601,2449,2472,29,4,1698,1953,1632,4211,1769,3135,2788,741,4127,4372,6854,1850,1571,1784,1248,1175,829,908,793,2218,843,2298,559,1295,2311,3991,2656,4186,401,500,35,198,2110,2712,188,150,118,214,47,30,2894,5582,909,486,6819,6156,3009,2187,2309,2615,620,9645,10839,9748,825,7149,7444,4819,3543,6735,4349,3423,19,7,3057,2690,2146,6152,5099,7261,8424,1705,10864,7293,10169,3778,2568,2400,1807,2469,1254,922,1508,3124,3826,9555,2369,5445,5022,9414,5908,6933,2631,2835,97,8402,6035,7667,1240,1596,4499,8513,637,445,10715,10622,4902,5693,2607,1447,3097,2575,1766,1591,911,4798,1950,1367,824,2114,1294,917,1458,1840,863,619,68,14,1174,778,2276,2400,1404,1106,2921,936,2427,1379,4200,1795,827,884,1469,1202,1499,1017,2115,3899,1010,2089,1579,2010,1409,1856,2704,2559,306,284,37,1342,1239,1560,504,556,484,498,360,228,2562,2414,1499,1368,3077,2030,4247,4702,5106,4476,3001,26366,3653,1690,933,4229,3508,2603,3832,7072,1380,546,72,15,2793,1724,4689,4874,1369,887,2724,1108,3370,1772,5403,1768,981,735,1345,1507,2890,2016,6264,10815,1107,2216,1409,2183,2378,1555,5493,7791,200,163,43,1090,4817,4078,1158,1432,250,347,161,155,3004,3314,1627,2064,5270,3370,2558,2138,1503,1239,517,6339,6461,6864,840,2275,4423,3015,2933,3219,5528,4209,433,61,2229,2144,1564,5556,3396,6488,5731,1401,9344,7296,14323,3942,3053,2936,2268,2420,1048,989,1034,3156,1351,3183,984,1861,4901,8183,5815,8088,1316,1235,117,189,3278,3616,297,342,237,476,86,41,5316,7251,1816,1667,7370,4435,2701,2146,2112,1922,430,9842,13361,9109,1290,6055,6975,4755,3571,5951,5167,3226,69,10,2963,2250,1687,7188,6853,7850,9390,1281,15319,8284,11591,5112,3144,2873,2086,3265,1230,1552,994,2570,3239,8142,2382,5200,6720,11335,8467,8374,4646,4383,917,10793,7111,7479,1215,2037,8137,14516,2993,1101,9969,1657,8557,9039,7010,4024,6860,6098,2839,2433,1619,15773,6901,5151,1899,8649,3168,2512,3554,5276,1836,1288,697,61,2615,1808,6205,7186,3667,4121,11061,2630,7043,4256,14744,6660,1844,1843,2179,2878,2140,1100,3137,7891,2292,5963,3309,6183,4016,4393,6782,7804,922,528,635,4693,3959,4257,1342,1650,1843,2629,884,674,7578,8036,3336,3706,9773,4934,8822,9065,5859,4976,4356,43006,15662,7019,2777,17407,7723,4678,9285,16011,3419,1687,901,86,5901,3991,11395,15750,4994,4543,15474,6111,9656,3569,14224,5202,2121,1194,2256,2701,2555,1506,5170,9574,2589,6198,3560,6314,4982,3464,14205,19132,1035,935,246,5170,11094,8091,2617,3903,1286,2290,613,373,8797,9496,4048,4959,1906,1071,861,780,692,400,113,3383,2472,1663,309,1453,1091,1063,670,1690,1322,837,114,42,980,593,260,2121,1407,1293,1942,703,1942,1336,3330,1259,903,802,1019,900,316,180,342,1576,791,1539,492,1117,1169,1801,1485,2234,524,371,55,495,1039,878,264,761,543,788,103,36,2434,2360,671,651,1710,1403,486,422,932,820,84,4951,2033,1430,296,1211,1235,1243,1088,2323,1446,1283,112,0,1618,1297,671,3315,1083,1000,1813,347,2832,2038,3037,1181,694,697,683,741,658,357,802,3244,500,1632,484,652,1060,2503,1465,1910,744,1033,143,2186,2083,2097,292,692,616,1265,242,140,3130,3187,876,1085,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,26,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6341,3133,3647,3900,2747,1462,2074,16288,4455,4061,1641,5632,2795,1802,2871,4881,3709,2125,471,42,3515,2271,6046,10287,3078,3612,5255,1980,6153,2308,5758,2047,1058,895,2108,2685,1463,798,1501,4577,1129,2391,1342,2977,1995,1982,3242,6164,1406,1300,83,3357,5438,4473,1899,2207,1916,2595,244,88,2171,4696,3091,2164,9286,5417,3805,4120,3285,2258,473,18387,9774,6596,729,4716,3269,2287,1811,3786,7902,4995,1002,109,4444,3214,1701,12315,6235,7166,9987,4174,7661,6158,14570,5711,2804,2380,2157,2317,1663,849,1719,6818,2964,5783,1391,2012,3449,4620,3479,6336,1221,1642,192,2515,6587,6649,775,1928,1555,3346,225,141,6007,6455,1834,1971,7836,4850,2474,2008,1939,1669,257,13826,8685,5855,795,4664,5707,4606,4090,8062,6649,5053,674,67,5120,3323,1577,12931,5152,4795,7911,3212,12195,6993,11654,5884,1497,1673,1477,1886,1552,1168,1623,6120,2118,5511,1812,3088,3878,8314,4813,6121,1705,2433,302,8645,6549,6942,760,1559,3719,5535,743,631,6697,8514,2018,2662,1336,723,1326,1093,877,785,428,4123,2034,1146,426,1950,526,609,657,1194,684,417,273,55,890,367,1254,1300,1118,569,1771,470,898,407,1701,702,224,307,164,291,433,286,617,1029,462,1057,490,647,474,652,756,1095,131,152,178,426,1164,1214,366,459,279,475,238,108,463,545,382,379,1308,389,1511,1890,1305,565,642,5318,2392,1472,833,4111,1735,1171,2131,3923,710,277,131,33,1192,580,2217,2811,533,392,1176,597,2313,653,4800,1811,137,95,316,209,419,295,357,305,462,619,755,778,1115,1203,2478,4057,153,112,120,373,1743,1483,580,1298,259,253,148,81,692,881,938,743,3989,2282,1607,2110,1162,991,195,5328,3933,2593,443,2719,1583,1145,839,2072,3083,1903,495,42,1590,955,887,4341,3243,2663,4520,1859,4189,2340,7041,2719,1042,1067,1391,1288,493,345,538,1666,882,2268,802,1579,1841,3403,2312,3538,575,784,100,1302,1763,1998,358,838,1068,1809,149,32,3304,3192,1218,1141,3477,3226,1048,954,1902,2040,249,11023,4923,3330,579,3388,3757,3833,2718,5600,4212,3489,336,26,3559,2690,1662,9720,4200,4099,7183,2342,9083,4803,10210,4126,886,1295,844,979,769,637,1204,4410,1272,3825,1184,2067,1605,8160,3557,4435,748,1152,150,5177,5197,5229,738,1510,2743,3906,645,466,7315,8514,2452,2691,523,209,632,373,460,314,146,941,850,503,569,976,480,443,349,590,593,230,171,40,456,181,670,683,1295,638,1880,722,779,392,1421,763,101,73,152,157,255,141,279,359,346,689,714,838,427,381,665,794,123,84,97,312,528,459,259,199,544,353,403,264,454,457,393,329,273,178,305,398,461,235,219,1140,459,335,245,536,335,162,239,422,212,80,193,23,291,144,553,634,337,215,722,346,697,251,931,581,77,29,131,92,109,94,257,346,163,139,237,300,353,222,502,500,76,38,94,102,287,250,233,162,182,147,113,96,109,175,228,230,10670,5270,4895,4957,2505,566,413,16435,12408,9480,1027,6895,5918,4160,3496,7725,8795,5571,635,60,4974,4188,2439,10512,6391,8042,16215,4930,9436,5526,15798,6606,4550,3580,3311,4028,935,475,1017,4141,3761,3148,2555,6027,4286,7037,6200,9723,2143,2094,194,2727,6989,6301,588,1178,1933,4593,270,105,8767,7946,2137,2788,9290,6409,3444,2696,2425,1857,360,13877,13234,7949,1373,9066,10403,7753,8233,16302,7637,5654,385,11,2288,1715,957,4636,7297,8249,14507,4730,18099,8841,16946,8426,1869,2236,1763,2045,968,934,1387,5220,3332,8565,2625,5233,5900,552,12287,15079,3181,3706,285,11951,3327,3282,504,657,4964,8379,1036,879,14795,17568,3850,4924,4339,2505,3974,2456,1433,730,576,5160,3630,1313,1400,5094,824,683,809,1270,2730,1222,374,76,1770,990,2300,2493,2918,1665,5575,1399,2038,1109,3751,1909,546,270,620,1598,436,286,843,1876,1151,2315,1949,3119,915,1568,1832,2275,837,885,173,1466,3139,3006,934,1011,1443,1758,664,241,892,1180,1001,762,2401,1069,3377,2755,3389,419,1722,14141,7246,5822,1469,7332,1997,956,1920,3090,2106,656,431,62,3575,1241,6613,6932,2378,1079,5291,1341,2465,722,4272,2128,391,211,502,645,620,169,2210,4042,1114,938,1264,2063,1725,1938,3120,5410,550,294,182,644,5170,4545,1585,1669,1043,846,314,135,617,1200,942,606
Escherichia coli K-12,83333,genomic,RefSeq,107876824,347041,51.96,59.2,40.69,56.11,38160,39893,40758,33510,25731,30197,2954,51804,110482,96901,9902,81415,59038,66914,16949,53510,46522,28563,3705,487,25030,14618,9865,35892,52934,68733,68060,20061,94592,57011,93890,38793,26871,30339,21482,19071,12704,11347,8350,27766,32839,88931,11126,27538,63378,135774,28058,57862,11878,17709,1616,8192,29041,36403,2689,4829,17747,37630,1973,710,101279,103165,7809,11791,53972,55684,9920,9664,22438,47701,1033,88417,29379,35355,2435,18057,28417,24102,9039,21086,28635,28068,1415,170,23694,25126,2962,63661,29484,44941,47578,12775,55592,42364,41373,17417,27681,35941,16814,26311,15949,12210,10380,68571,23347,58871,7940,16746,25821,56512,14970,26382,12946,19842,5124,62316,48689,58782,2242,6834,23943,52936,4906,4778,52083,51331,5652,11020,33239,19723,37320,36291,22541,24097,5922,84775,53430,37668,8667,51925,14413,17254,6136,22500,14012,6121,1330,537,17535,11562,29015,49386,31828,18648,53701,13457,20474,7773,18691,9561,11948,13191,11338,19487,20253,22486,13773,52781,16807,57053,13235,40086,11660,25258,15336,30111,9362,11330,2418,22775,39673,47796,5409,9524,34217,49069,5745,2899,35566,32783,8952,17743,39630,30254,30957,44931,29874,30257,12490,157028,69427,36121,9230,57790,17724,10986,8923,23264,20231,10104,2170,915,24298,15266,36169,81440,25753,15178,39246,13240,13900,3117,8593,4214,9455,6814,13516,21810,20185,16712,24173,56500,10225,24593,7794,20617,13587,9727,18798,25101,9529,9726,1064,25599,43762,42691,7410,11072,17910,20464,1863,1313,17619,18765,10018,16216,27202,17119,15312,11515,10589,10269,2434,20682,29592,35443,3811,7175,13285,12055,4542,8722,35763,21587,2677,620,13394,6978,5225,21949,37759,37441,27078,14144,72171,22626,51318,41183,41626,47097,22133,23900,12313,11612,5389,17048,10145,24099,5278,8576,25092,51660,18965,29515,12030,12869,1046,9609,11662,13347,1344,2526,6690,25225,1266,471,29181,52031,7249,15400,23804,14684,4085,2761,5360,4338,390,12499,24894,22981,2288,8267,11354,10863,3495,7490,34997,27815,991,21,8589,6377,2710,16432,48965,53652,33025,14232,74117,68506,43802,10652,35449,34892,13485,14446,6240,8904,2084,9789,17924,46874,6603,13219,18486,52397,16072,26482,10501,14063,1617,24274,5311,6344,1379,3340,15479,22902,3099,2579,59195,78376,10558,18529,14351,5923,10772,11132,8180,8044,3081,27709,10689,7962,2558,10763,1675,1453,751,2047,5162,2944,810,23,8267,5795,19090,15128,9285,9954,23003,5179,2252,901,3234,1583,2993,2722,2946,5313,7557,7254,7249,19880,3922,11698,5216,7615,1502,3276,2172,3908,2736,2834,1313,9960,14303,19585,3067,4887,6667,10194,1779,996,2480,3145,993,1814,142599,91034,63743,74479,59371,55400,22271,305492,166607,106733,19864,166395,118312,94585,81075,274463,58765,40217,7583,747,76309,46675,127205,42667,91197,94121,210105,54823,199666,80217,290432,117116,25083,10941,25256,45716,39976,31153,54006,145717,52128,136746,44525,101248,110366,85546,219956,394854,20542,27996,762,65019,147869,139208,16358,23505,24402,40272,3325,2325,90632,120095,40956,78974,63063,61758,37350,54281,42208,51747,4133,132279,106322,99548,7417,67186,73767,80013,14694,72335,57245,36009,4267,493,43900,31825,24887,103745,59887,74397,88851,32450,122911,54063,145107,63526,36408,39000,24238,27689,34272,27703,26750,74587,35434,88916,13756,33058,78199,167362,42101,91723,18984,24915,1171,14313,70001,81610,5415,7652,13608,35234,3035,429,115159,133297,9299,16540,36890,51597,10913,9048,25451,58018,1591,80698,69101,88198,4439,59314,56727,63221,13995,46158,32941,38367,2299,260,23496,26699,10051,49806,54679,96375,90143,30909,86275,104734,97022,32959,30513,42067,11280,17624,22489,21466,17590,68915,39798,110179,10793,24730,58509,141915,34221,59499,13266,20511,2129,58612,50203,70090,2669,6310,41272,77662,5047,5186,83611,99627,7755,18288,19420,10042,11733,11292,6186,5328,1956,12776,10362,8072,5473,10691,6348,6872,3149,7134,7268,3346,1274,623,3943,2793,6162,7541,15359,10478,24803,7595,11796,5904,16869,7108,6220,4506,5670,4896,4508,4850,4124,9177,6192,14535,5908,9465,5722,13666,8491,9892,3433,2440,286,4355,6565,6591,1773,1801,4241,9740,3254,1147,8697,8993,2878,4880,51768,48474,31079,56086,30541,43015,13074,175024,83715,76568,11811,99707,47858,42412,24046,98390,34439,27072,3312,391,29171,27290,46237,89002,58729,63414,109015,43337,83254,46631,101294,38638,27559,22673,22309,35879,24879,16604,33724,72359,28498,85978,25367,57776,49325,39775,71741,146970,12034,13391,872,30182,66180,66506,9050,11108,38010,56441,5067,2806,41060,93107,26854,48965,35985,28797,22294,19966,15906,17874,3284,61400,59629,71824,4808,22765,41084,32016,13924,30620,55298,34838,3863,568,22188,21374,9550,48521,38954,63531,53131,22217,97608,44128,105793,57276,42374,40656,21249,25205,19271,14660,9569,43713,17435,40849,8528,18253,49837,84240,32215,52866,12723,17493,1427,6374,33305,35203,3786,4271,7649,19020,1539,415,55264,74507,7909,18866,41125,29105,8270,6339,7722,8080,589,25881,64785,46389,5780,34259,33294,25587,11660,33887,29781,19421,901,85,14750,7643,2803,19434,40456,36874,41831,6298,99278,26213,57686,29853,18323,17874,8256,12133,7748,7300,3175,14524,31413,68262,13358,29858,35366,67467,26170,50726,12347,16700,2194,58427,17881,18446,1489,5030,37740,69063,7843,5674,68190,67210,12494,29262,33678,21852,29718,33315,16001,12553,4686,88319,24925,15822,5676,39221,13020,12003,10376,32748,8981,7258,1478,260,13495,8510,20527,38297,22566,23058,57724,9849,26628,13997,48637,21587,8451,8859,8163,13602,9146,7145,10987,41737,12420,24595,11787,28810,11130,16928,18531,35868,6317,4765,1328,16912,33943,29338,4088,6475,10448,16396,4185,1652,22077,19045,6584,12946,51422,37247,32895,51712,31152,30487,13153,239579,122523,80953,13924,129453,70915,53260,39969,160490,24405,9931,2656,596,35438,13698,36519,75682,50491,39309,121419,44594,73873,25916,84917,38289,10700,5896,9073,19498,19281,10548,27796,80445,26856,55682,20747,55269,35741,25682,61561,149879,8025,11501,1247,24577,71356,64208,8562,18982,22172,29122,3940,2292,42539,43134,14346,29481,37739,38185,27338,26567,27811,41227,5818,106588,38576,47452,6343,37562,31675,35542,11366,34400,22845,37568,2983,203,20019,31230,35527,86477,12531,42715,45841,13262,31087,51543,62316,25515,11049,22350,14724,11726,13474,16292,12883,54207,7661,50675,6108,15277,19876,60960,23827,44057,7534,13026,1472,6325,36553,61201,6279,10735,4944,20598,1548,469,38267,53539,9305,7783,23255,32058,6248,5380,10426,13308,1192,55246,29229,37378,3036,22930,22468,19022,8012,19329,17637,28349,2385,104,14984,14557,8569,40441,13626,45595,40162,10704,45463,40387,40047,16251,12028,17338,6988,10174,6634,6647,7913,29545,11780,53706,6674,10672,20153,46480,18497,31086,6829,15505,868,41789,29281,34445,3634,8340,16142,45478,2907,1481,49572,60693,7591,12490,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35704,27164,23049,22779,24297,19048,5373,76394,51386,40897,4748,34422,23440,20843,9819,28892,25532,26930,6597,167,27050,20428,24434,62209,19942,35166,42971,12427,27745,28512,55580,23015,9088,9084,9074,8804,18857,13298,16515,51558,11776,33233,6451,15558,19115,35731,16541,37269,6342,9387,1932,4787,24709,35754,3641,9307,6085,15546,1529,176,25400,30941,7337,7565,24857,24279,5491,4150,9323,7412,803,39953,27404,22591,2056,11950,25416,20259,11522,3241,24547,20620,4581,160,17675,14014,6089,31160,16528,25775,23453,8009,40118,27822,32544,14081,10393,11895,7069,7689,7749,4073,6701,25327,7994,26796,4305,7697,17989,36238,15201,26232,8041,13061,1452,37571,22822,23220,3403,4822,14578,25200,1219,900,46679,49075,7211,11828,31248,14424,25833,22607,31325,28110,7970,115814,55526,52647,11834,40309,13181,9314,6531,16303,33716,20008,7985,660,30578,18750,61103,61537,40042,48434,82963,23917,18397,10083,33799,23984,13542,14373,12865,13257,17873,12367,14912,44813,18535,49300,17084,34702,12327,25580,13659,26596,7343,7447,3455,26590,46274,39387,11475,15306,22645,37741,3733,2156,27092,29695,12055,22658,65766,53968,49600,60264,54818,31598,19012,92581,67635,52754,13741,70519,71999,45016,44911,102541,43074,37076,7790,969,52778,32333,109786,120024,33033,47903,75256,25015,105402,54767,129259,60539,18791,15083,21313,30867,23693,12719,36124,71259,19959,44511,18162,36297,61731,66741,97159,172450,11365,15959,1564,52419,86385,57210,22602,25188,15959,31524,3550,1898,46597,92947,33009,57572,32164,30190,29464,21479,25512,30168,6388,82140,81634,70299,8818,54500,29944,35466,13265,34421,28074,26173,5221,502,23648,18482,30791,66295,49174,53992,74389,20936,52376,42753,79761,31515,9696,8121,10614,7864,17802,14121,19979,52811,18573,55722,12958,26985,30281,71640,30005,55369,5587,7238,1116,2784,25485,34605,5873,8475,12923,23223,2559,818,47314,66284,11043,10862,39198,51549,14948,11533,22299,26730,2831,118360,53839,56894,4964,40551,46893,54951,21769,54513,39403,42379,3962,557,27179,25562,17636,66383,35407,52761,69391,24558,78239,54895,83660,31640,13663,22190,13161,17180,14810,11522,21896,82295,16586,58466,10534,21458,31032,92783,28994,56441,12680,18131,2610,64612,54093,57345,7148,12194,28972,59354,6664,3813,82273,98829,15935,18521,45171,45427,42256,28916,31158,42504,11319,172240,87911,95767,25970,81495,54336,60922,29957,119087,57668,44072,19208,1313,37516,29447,51808,87384,78769,86036,121033,47153,128553,75428,132300,129514,23807,29316,27557,37524,26018,21843,30138,90386,30803,101826,41005,75738,40586,112866,76320,160763,11860,15390,4934,37120,65892,81563,10841,18038,27170,49270,9713,4241,85141,120609,23822,52298,26966,17010,15152,15496,12129,15821,8707,88032,34171,26994,6514,29447,17560,14197,12071,26684,15401,11821,10133,1108,17879,13643,31556,52400,19288,22056,66482,19078,20261,9108,19718,13551,8728,6099,8200,11614,10638,9297,18641,35118,5032,13788,7337,9479,13294,13743,16937,33636,4490,4718,1697,13808,34085,34011,9196,11689,9857,14336,2538,1424,7879,17646,7794,9551,81851,72870,65747,49018,37768,65431,8239,133521,134531,135839,11391,91220,67892,69427,28701,96738,67000,70342,7802,620,30885,35558,39278,78030,56530,106543,139510,39652,103484,86193,175558,81096,18518,24135,17707,18571,26294,23939,25811,84914,25587,85983,15985,38044,60594,124247,53654,118751,10864,18788,999,6381,49036,72078,5042,12577,13586,40173,2700,785,75507,105390,17760,15230,32194,37175,14732,9811,16826,18257,2533,80125,45814,49096,3883,33593,47817,34873,20461,45648,33487,35891,2890,245,22308,18692,12191,47647,31959,52779,80596,23929,80356,47101,91689,39055,13407,21345,11658,11404,8213,7026,10796,50636,16834,53922,9932,24350,33593,65881,31000,55429,10894,19303,2388,82969,46439,45863,6543,10853,33973,71923,11563,7372,70955,79024,13875,20954,67040,29722,45609,36384,33556,32849,11980,225993,109277,115740,25188,98567,72778,65819,34759,157498,63200,46321,11355,651,51733,35845,84462,113850,88217,122114,197027,50306,155761,70911,176327,166301,25666,31752,24958,24263,23988,20251,19260,73328,32419,121442,35428,78888,56934,119872,79466,184630,15277,16043,3332,47771,83352,81909,12304,23409,40699,71105,8911,6393,108609,125933,31320,70540,63258,42716,35425,39752,26621,7087,14461,148111,57704,63910,12063,79556,19757,16147,10790,36348,33498,27667,8623,1293,38148,30275,70262,107095,31648,35448,92714,35080,24627,12317,35534,20538,15495,14018,14688,20910,12925,3340,22167,47954,7375,5314,12026,25373,17063,24206,25920,55966,11834,14328,2859,40503,68740,59400,13966,23571,15601,25572,4714,2901,13341,20125,7947,14833,20302,16685,12373,13220,12178,8643,2943,42397,27658,25525,3604,12472,24747,15609,12924,14164,18657,14904,1858,100,11365,14006,7173,17199,10117,22341,14000,4032,29606,34888,43400,9397,17061,18109,13456,11179,7166,5953,6047,19469,7991,21844,5327,8700,20163,36620,21141,34737,4193,4340,311,732,15183,18995,1144,1355,613,490,347,324,39362,43170,5193,2666,16064,15675,6932,5894,6372,6737,1332,26312,27788,28718,2805,16673,19593,16171,12914,17422,8342,10050,474,1,7347,7426,3701,16383,10318,19674,13153,3986,30204,19955,19090,10063,8877,9751,6374,6490,7215,5846,5060,12671,13032,33930,7313,15392,17049,25375,21939,19013,9401,12215,3260,28713,20938,28764,4729,5359,18161,36942,3457,2071,53660,55892,10151,20019,20216,11522,23250,16245,12302,12544,7295,49939,17156,12415,5548,26428,9665,8960,10927,14403,5489,3790,1550,232,8704,7277,18649,16771,9613,9014,21543,5421,14877,9135,29725,9575,7999,7333,12311,11837,7670,6630,12034,26934,7008,18897,11226,17589,7375,16204,18111,20621,2319,4333,2646,12743,12197,19003,3557,6015,3774,4975,2649,1209,16618,16395,10181,8236,24146,14099,18850,23344,19363,17847,12695,116955,30469,15439,5936,39425,17805,14767,21277,42648,6505,2894,1332,475,13399,8991,28479,27521,9041,8541,25770,7359,11963,6419,21419,5569,4824,4482,7947,8415,8796,7853,21074,32167,4978,15508,7454,15610,10865,8577,25463,36663,1875,2783,359,9461,22547,26996,4975,9737,2800,3989,640,333,11321,9360,5040,6660,20161,14814,12391,7848,6315,4536,2002,16875,12854,13540,2249,5886,22795,16288,11394,14767,26770,18294,1217,88,9572,4487,4328,9075,8453,12608,12327,4006,34910,28649,49033,17122,15204,15326,13208,11207,3886,3985,4169,7062,4520,9077,3106,5914,21741,35372,22289,40703,4615,6236,177,1813,8866,9130,1192,1205,519,1270,166,89,21793,42916,7642,8503,13158,10523,5530,4970,3871,3168,872,9163,17959,16595,3281,6739,19425,14889,7054,13470,11575,8662,477,83,6289,3740,2783,8318,12471,11653,13735,2130,32175,14521,15820,6633,5220,6506,5163,4233,3008,2338,1519,3270,4979,12898,4736,6876,14627,27408,18841,18879,5035,7162,1460,17623,6900,8387,1740,2917,5994,15827,2460,997,23792,32245,9446,4611,18759,13294,20775,17825,9088,8518,6053,43091,17870,16679,4358,27387,10694,7609,13318,21490,7057,6419,1183,87,11398,10071,30330,29315,14219,17675,31290,7374,24526,21979,57105,23693,5619,6323,10204,9887,5936,3172,10364,21060,7865,26235,13018,21442,11135,16857,17432,21310,2423,3966,1628,7128,13187,20227,5336,6154,3813,9355,2020,675,21269,30614,13544,11741,61331,50274,39341,42557,27235,32421,22346,204526,60989,34301,9110,70891,61728,33501,59391,94048,31640,19424,2465,281,38564,28309,71249,96512,25902,36318,77394,22777,87535,48372,154815,47666,14792,11569,18650,18842,13510,10125,33135,50512,17836,36518,18215,35620,25864,16382,68692,77616,4813,9789,571,54722,53842,54180,7594,5011,7497,14728,1205,592,43992,53247,22588,29193,23755,23665,12753,11153,9264,12019,3049,37476,32045,31290,2779,11768,18351,15776,10486,13328,20142,19467,310,76,14012,15891,13702,34323,13328,26069,21723,5721,29867,34624,55055,13796,12557,14409,9948,10360,5951,6888,5645,19491,6601,20276,4456,10841,19257,32389,21074,34912,3323,4109,193,1483,17248,22833,1496,1053,1022,1732,303,110,24105,47038,7056,3846,57008,52871,25693,19330,19338,22469,5789,79525,92176,84363,6568,60945,61786,40482,29778,56427,35318,29098,230,4,26067,24269,18981,52327,42770,61031,71179,15211,91323,61378,84560,32283,21874,20151,13625,21185,9481,7306,13447,26113,31179,80733,18082,45221,42646,79496,49967,60003,22048,23546,786,70961,50115,64281,9829,10884,33733,71582,4967,3016,89962,90113,38678,47356,20360,10496,25648,20974,13450,12800,7338,37976,15545,11092,6314,16923,9219,7302,10607,15124,5413,4511,612,79,9331,5865,17463,17539,11198,8362,21093,6373,18134,10089,31660,13438,5857,6228,11113,9328,11443,7612,16379,30132,7503,15663,11435,15710,10472,13332,19803,21235,2614,2235,254,10400,10239,13063,3384,3839,3445,3723,2234,1571,19096,18519,12029,9933,25949,16037,35962,40041,41200,37799,26751,223252,30258,14597,6660,35289,27606,20637,31848,57789,10711,3809,574,151,22669,14930,40792,39417,9939,6616,21017,8546,25556,13530,43562,12293,7475,6042,10445,12658,23902,16004,53085,92032,8756,18275,10810,18036,18656,11884,44784,64077,1187,1160,307,8344,42005,35368,9935,11270,1618,2249,1071,1194,24918,26588,12128,15398,42648,27373,19864,17578,11320,9992,4004,51396,52277,59907,5496,18136,34421,23138,22619,24658,43996,33605,3913,484,17771,18119,11951,44877,26751,53451,47353,11151,73997,59855,114856,30747,25315,23275,17607,19970,7534,8158,7721,26191,10568,25396,7490,15433,38642,66275,45120,68813,11367,10156,1021,1471,27176,31035,2794,3307,1303,3930,251,217,42888,59336,13511,14226,61436,37345,22476,17668,16404,16592,3450,79378,109689,75479,9192,49597,57400,40086,30138,49261,43397,26063,499,92,25386,19290,14954,60979,56993,67828,80222,10744,128344,71120,97896,44499,27613,23552,16423,27002,10747,12393,8485,22213,26004,67367,17951,42645,54878,92148,71094,72256,37671,36918,7768,90495,56808,61924,8832,14580,65089,120814,21783,7885,80445,11238,68993,72974,57018,33273,55534,50736,22589,19163,14104,127654,56760,43278,14519,69747,24820,19616,28143,42734,13629,9100,5691,499,21216,14366,51897,56188,29094,33073,91334,19347,57965,31922,121487,52305,14064,12817,15398,23571,17622,9069,25886,66314,18065,48887,25349,52457,32216,34633,54643,65208,7242,4193,4695,37309,33178,36477,11251,12358,13628,21839,7019,4507,63322,67719,24842,30790,84656,41257,76716,76514,49358,41680,37874,370937,134534,61237,22408,150228,65560,39970,79263,137960,27799,13620,7512,614,50499,34105,98939,132815,42176,38164,133256,50759,81027,30598,122123,42130,17340,9789,16932,22964,21000,11325,44483,82050,21563,53089,28979,53219,40810,29559,116954,163438,8903,7997,2052,43917,97274,69774,22717,32420,10618,18989,4551,2762,76072,83089,32345,40404,15014,8578,7555,6079,5103,3253,835,28500,20664,13806,2560,12302,8775,9335,5513,13801,10166,6895,1062,248,8072,4608,2347,18158,10914,11209,15777,5118,15294,11123,27139,10337,7022,7306,8559,7915,2552,1010,2639,13215,6079,12877,3940,9258,8820,14672,11851,18625,4003,3086,506,4034,7899,7074,2009,6379,3893,6975,645,210,19020,19986,5060,5588,14373,12688,4073,3838,6830,7403,542,42165,17423,11893,2180,10546,10462,10304,8956,19959,12086,11321,954,6,13425,10942,5581,27088,8776,8169,15581,2572,23897,17677,26041,9620,5879,5915,5670,5793,5139,2503,6815,28145,3899,13770,3656,5010,8694,20698,12219,16495,6500,8576,1185,18124,17766,18277,2487,4884,4696,9887,1510,944,26589,28083,6908,8916,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,233,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,52093,25962,29829,32491,20725,11261,17216,139062,37220,34584,11817,45837,22731,15470,23630,41351,30611,18332,3895,408,29507,19284,52224,85920,23744,29518,43290,15735,49346,18772,47304,16389,8147,7003,17486,21553,11424,6496,12172,39118,8864,20055,10207,24237,16277,16207,26170,52913,11236,10590,725,26744,44269,36889,14592,18142,14509,21594,1738,407,18081,40305,25255,17336,76652,46051,32207,36530,25446,19179,4213,156922,82088,54800,5497,39946,27599,18866,15156,30044,65581,40681,8547,815,37571,27907,14429,104558,52478,59315,84893,33384,63386,50843,123466,46051,23707,20324,17411,18901,13374,6549,14779,58841,25166,49920,10384,17775,28322,36972,28485,55175,10617,13788,1534,20693,55433,57515,6106,15794,13231,29154,1675,1024,49114,55507,14462,16728,66546,40945,20659,17771,15164,13436,1944,115856,74682,51008,6009,38917,48516,39628,34853,69965,55587,42402,6079,506,42316,28375,13631,106146,42681,39420,67783,27227,103920,61357,99564,50582,12275,14092,11753,15764,11860,9765,13534,52251,17341,47046,15485,25066,33031,71377,42028,53109,13825,20352,1908,72195,56182,58219,6345,11060,29964,46653,5720,4303,56664,73312,16170,21632,10505,6103,10420,9075,6008,6021,3209,33954,16060,8723,3383,15979,4263,4616,5058,9968,6005,2929,2545,351,7436,2932,10179,9281,8440,3992,13721,3550,7309,3210,13840,5921,1677,2468,1114,2379,4182,2383,4400,8328,3328,8063,3874,4639,4057,5144,6127,9149,1018,995,1095,3519,9402,9477,2425,3498,1587,3587,1425,587,3848,3979,2994,3127,9618,2772,12617,14978,9192,4154,5181,42022,19582,11588,6231,34619,13505,9855,17918,31832,5272,2058,989,392,9023,4154,17631,22544,2930,2568,8882,4238,15322,4255,38084,12350,952,514,2195,1504,3026,1743,3020,2041,3357,4577,5500,5888,8954,9367,19509,32662,1259,819,782,2317,14416,11301,4518,9851,2319,1700,1282,612,5201,6979,6889,5104,31371,18542,12861,17944,9150,7700,1487,42796,29630,19756,3019,21345,10919,8790,5711,15534,25280,15524,4131,326,12880,7550,6964,33775,23865,21286,37214,14520,32218,17167,57925,19561,8061,8683,10319,10801,3744,2848,4276,13685,6580,17824,5923,12555,13295,26807,17268,29869,4434,7272,693,10925,14682,16234,2603,6591,8367,15061,1160,261,25160,26806,9119,9103,29338,27092,8884,8217,14196,17532,2333,92385,41121,28411,3918,28034,31179,32177,22489,46209,34069,28531,2625,198,29252,22418,14217,80594,33839,33913,60235,18736,76755,40146,88042,33772,6814,10590,5659,8695,6053,4890,9859,37229,10237,30078,8667,16863,11816,70247,27714,37368,5876,9437,1169,43002,43488,43689,5692,10631,20963,31578,4391,2617,61749,72899,20209,21052,3669,1228,4800,2796,3461,1875,959,7235,6672,3266,3642,6736,3748,3356,2658,4570,3658,1804,1381,222,3462,1372,4648,4499,8380,4312,12578,4902,5550,2572,9713,4438,1062,488,755,1124,1762,1359,1486,2937,1911,5410,4782,5573,2599,2609,4897,6416,1242,768,705,1873,3732,3613,2460,1528,4081,1768,3118,1513,3065,3397,2758,2342,1800,863,2032,3278,3562,1638,1582,7722,3008,2558,1416,2904,2330,1026,1052,3109,1554,464,1326,163,1949,832,3911,4409,2111,1405,4114,2399,4906,1478,5379,3548,675,274,714,557,568,895,1690,2637,938,968,1242,1512,2254,1433,3844,3339,449,219,629,605,2021,2216,1381,1074,1374,707,703,491,871,1332,1268,914,88756,45650,41800,42672,19787,4284,3484,140511,104157,79597,7239,56764,47734,35057,28220,62997,74165,46518,5592,339,41626,37143,20416,86964,51543,68291,138073,39411,74757,44757,130977,50615,37482,30847,26579,34517,7823,3388,8519,35116,30361,25427,22114,50071,34995,58588,49868,81631,17907,18242,1471,22872,59725,53578,4521,9789,14980,38614,2525,498,72311,65639,17161,23151,80170,55427,28619,24050,19259,15260,2804,118888,114242,68187,10989,77324,89554,65368,69748,140595,63644,48547,3180,88,19354,13826,7642,37665,61508,69347,123350,40693,152875,73915,148127,71407,14313,18186,13116,17603,7795,8162,11432,45435,27561,74129,21176,42930,48965,2943,103654,132350,27045,32467,2374,98993,27318,28380,4071,5406,39331,70459,7912,6173,125740,153676,31686,40804,34792,19669,32230,19570,11123,5483,4167,41073,30269,9824,10312,40270,6454,5643,6367,10064,20570,8978,3035,614,14344,8450,17689,18684,21910,11477,42695,9408,15419,8259,29114,14857,3741,1963,4944,13725,3437,2347,6678,15348,9368,18014,14414,25140,6129,12055,13947,18305,6380,6992,1213,11565,25410,25713,7256,8453,11331,13103,4927,1275,6033,9268,6431,4559,20381,9124,28920,24938,26248,2971,14153,118827,59641,48835,10806,62377,15905,8314,15349,24393,16371,5558,3830,490,29673,10110,56431,54976,18135,7562,40942,10719,18690,5484,33510,16446,2844,1752,3942,5806,5218,1143,18770,34958,9296,7648,9882,16837,12318,15108,23902,46461,4430,1853,1341,4588,41238,37004,13217,13326,8175,6391,1731,661,4860,9243,6245,4120
Bacillus subtilis,1423,genomic,RefSeq,4921127954,16891253,44.5,52.63,35.97,45.02,3937039,3496835,5349878,3752526,2238605,1878996,830220,2349702,6132702,5496294,1523437,3928181,3074409,3841063,1877767,2794492,3969126,1981812,372983,66851,2548674,1039957,3368512,2839502,2859710,2223230,5649953,2003168,5980527,3501286,8124439,3122929,2827829,1640050,3071841,1245521,1314544,489326,1036418,1971180,1358054,1661633,3547957,2437885,2467608,3076634,2894323,3144852,615855,614597,69914,1474906,579806,629843,351273,483351,464107,478425,662354,252375,1320383,3064995,2195735,1101775,2952740,1629791,1832593,949063,1185692,607757,322372,1151619,2363168,1800800,531703,1230677,1195962,910923,595380,553048,1395916,771903,145235,20178,1106597,582499,1494705,960938,1425255,1050399,2849651,1041863,1292196,707732,1641789,687315,1160732,687400,1247875,497384,1080648,243241,524665,1371047,955198,785242,1508737,796196,1056519,1105036,1108626,726183,367696,373365,14749,809860,969503,1068042,373795,541110,1010747,2396424,1380759,550608,1649960,3295017,2471212,1287253,3951926,1747743,2289951,1861135,793216,493345,366364,965053,3371161,2987508,1103454,2767397,1004482,921711,753260,987998,2500701,1058590,183378,59361,1075337,372578,1099181,1199173,3255789,2599317,7147931,3125614,2613423,1508133,3965298,2055729,1538991,1146436,1999426,900262,373901,120799,209086,314661,1259108,1366589,2782134,2287701,1295557,1197225,1518437,1442226,378796,614970,81253,1129166,265005,268875,184167,310530,913911,1849503,1234546,418107,1172022,1834728,1719151,1162173,3513231,1306434,1171964,541017,2860886,1268408,476955,3488546,3710922,2192552,709618,1769364,1285449,774355,439024,1059725,1395556,691835,168580,31300,965048,505118,1304622,1701626,2219885,1225591,4165602,2101746,2058385,996065,2353203,1349694,1152326,654706,1076055,412019,954685,231759,589221,1720808,925725,692120,1588649,1130716,1635046,817956,1926415,1602694,146881,292279,44104,545497,672452,770869,332306,630932,499157,730949,752801,253554,399138,872895,942726,516094,2367837,1468579,2560601,2772267,2550610,1529661,528112,1951893,2180383,1456514,524379,1115449,2888834,3441170,1763350,2603890,2856311,1466097,164472,13881,2462518,1451693,2853023,2693060,1134176,783521,1889254,775758,6374836,2273356,7519740,3726814,3142861,1557386,2250095,935339,1974365,590221,1085256,2568016,716801,627129,1207177,746656,3098936,3135955,2872809,2615128,496063,582227,33667,892889,1016013,1297679,353127,651463,254245,503387,478350,134785,1626441,3385968,2370134,1112328,1453835,570177,718849,788856,795163,479217,158501,655205,2635157,1611632,507446,1354677,1705008,1608285,742412,964481,1013045,465368,40316,7959,659355,258245,772212,573162,1218064,635171,1701917,781532,1764121,852579,1575912,548975,628096,390696,724871,282474,565070,203818,303081,821944,548874,609564,896767,450622,1243720,1146027,1048532,895227,215830,175503,17740,337811,508379,612122,170739,298178,653093,1460464,870614,224943,1821894,3376941,1992196,1084266,1119867,578883,907283,874289,151093,89810,84510,137786,476047,529986,254850,456719,333984,385174,256491,267107,806381,424733,127099,36453,175097,56332,206275,160987,716330,543860,1826205,891048,595667,289671,807314,556439,444419,370082,574799,332565,62763,21285,47808,74454,240701,314885,412054,260275,384380,357339,278647,302879,163760,227054,48728,450521,52954,36088,18740,41424,213805,535222,348319,141986,356283,565161,352547,248567,5071829,1693135,1887319,936234,4153330,2003210,550592,5172452,5419745,4171438,765205,3404254,1078868,917506,518301,987650,2296176,1249067,162540,34223,1774608,1004433,2807690,2221404,3119579,2030713,6324120,3101902,2670265,1299048,3441190,2206171,1823439,1155248,1894518,867140,1837151,504930,1180238,3146400,1890873,1371883,3833531,2482839,2183390,1497844,2395788,2391642,165376,365818,22291,797400,921378,1019259,354753,832540,561059,1089776,1022306,361967,600992,1337652,1144863,791392,4839137,3462682,6034149,4510735,3351104,2102495,858190,2553106,5914221,4579704,1265069,3845286,3565572,4241228,2724959,3747814,4324597,2274774,202534,46990,3395782,1876965,4586232,3779516,2558135,2312596,6163834,2332119,8276120,4187046,11169030,4138788,3816049,2168834,3517413,1295698,2395970,1005867,1862402,3947022,1257415,1630594,4219346,2862394,3387434,4491637,4138420,3924158,876489,1027670,48909,1678535,1194469,1443560,621635,762932,493262,434846,573944,211001,1565475,2626198,2214915,1166727,2645892,1323221,1527350,919848,2047320,932844,494724,1815583,6325812,4591062,1336868,3584044,2956543,2770112,2088767,2087812,1986504,873555,90423,12734,1569121,637513,1737649,1533251,3974870,2653607,6685036,2263404,2930394,1952774,4833705,1900264,1156362,804053,1372324,511585,1092034,472388,835767,1880804,1446633,1424562,3151174,1773953,2526394,2965924,2932562,2273450,479158,629618,44864,900572,1369242,1992527,479120,767444,1846670,4258792,2528788,965846,3704069,7110097,4832249,2818666,1385227,939429,1480125,1231634,632916,430562,251453,749285,419429,342246,333938,441462,259546,273168,273828,280918,950106,669679,182711,54826,664558,353301,1093051,916355,1052631,885781,3217062,1260228,1835617,1170903,2960556,1320776,675701,515827,839073,509588,545836,189641,395350,1039279,404500,512029,849098,616518,724503,634670,779232,835208,261024,326577,106425,767658,247652,322335,234910,300302,321051,503951,553021,248599,549209,888851,812945,557093,3779026,1728528,855645,584234,3848027,1869462,565948,5585476,5539157,3801057,1296896,4030015,2175372,1773395,1405056,2400413,2129733,1479375,229213,93242,1370039,730724,1649484,2519967,4384168,2884719,8341625,4481539,4020510,2354861,5218179,3027994,1530651,842873,1688141,839433,1489438,401416,818342,2464920,1394364,1163546,3562872,2475488,2902393,1523198,2879940,3314200,360818,473318,50819,833248,730794,700544,303654,610313,1342070,1992240,1984535,674768,1424583,2263856,2381640,1812363,2843441,1481760,2546945,2026981,2292190,1430245,485793,1952946,2686219,2041407,616511,1397816,2576897,3074183,1699093,2265634,2439638,1086575,135887,30126,2073175,1024216,2478705,2330333,1060342,917503,2048289,990980,4185415,2206463,5599443,2412920,2241562,1455608,1965771,714641,1603885,561369,898844,1964182,804501,603145,1459409,990328,1885031,1927243,1743207,1830155,531366,548008,51298,948138,675747,755855,295816,485980,225866,198808,310145,81655,895997,992611,1221518,492494,2060728,887512,862911,783992,1087690,555391,234891,1129747,6396284,4469722,1089416,3541115,2017060,1713235,1131132,1471253,1607599,548745,62334,13568,1018644,391043,877785,703767,2841359,1625166,4416503,1081672,2049841,796467,1724894,1004390,710138,547731,849746,373841,564522,156039,278182,783599,1056237,1200420,2172047,1385593,1368343,1121514,1351352,851732,352292,465991,39092,639111,743630,1077978,259452,478008,1254917,3293964,1963961,530794,2451117,4178330,2872575,1489891,2935977,1566947,1784893,1656480,812823,564278,304887,1193550,855560,1015465,370593,1086679,514812,558489,449854,540169,1638717,1182559,203274,43887,659090,373672,951447,1356010,1860561,1917823,5128951,2257605,1615800,1231100,2745648,1458940,1333929,950122,1565530,769853,462224,170319,295753,791647,635061,889127,1876767,1433699,921079,933421,1097892,1156901,411929,366500,111561,1023091,313835,370905,174346,276500,463848,1154282,923068,407554,728121,960069,994819,669888,3391948,1120753,1530465,786826,3806396,1626691,527858,5039790,4389502,2789026,849010,2575773,882072,757012,502216,991201,2058584,1199574,156206,27058,993752,580147,1264877,1842491,2617006,1577673,5840645,2842301,1884209,1019366,2849874,1411316,1006511,622366,1167813,505449,1393172,349472,719167,2652546,902863,921532,2994013,1815119,1320691,833408,1803812,1720509,202754,289404,51250,773152,628369,631969,255310,593221,433287,654083,748152,295503,283164,575217,643194,456112,3713846,2216341,3513909,3044551,1529797,1033132,547698,1543432,3455629,3115457,1109297,2790424,1737971,2278249,2013150,2465642,2872161,1539630,250329,35153,2090607,1120155,3406504,2766465,1663339,1529217,5048312,1819658,4305042,2784451,6635655,2497474,1264106,1057361,1692018,735328,1254061,474524,1091349,2463590,723891,811462,2627673,1968585,1505829,1791532,2105965,2274424,372987,491331,58725,1226607,725791,738726,574232,760595,317421,375702,461385,156119,801461,1664177,1677994,689452,1718920,852201,1143900,879941,833485,390013,247569,789727,1621046,1370547,770785,1283796,651156,646410,586308,759681,1449147,792313,54289,14498,799483,363737,955880,814111,1540979,1322086,2571755,1002595,1846862,916787,2099183,1112952,627604,399403,632633,344593,530842,120748,283225,850182,498551,528501,1427344,906604,939036,764418,1003003,1077509,257805,308084,30204,700234,846439,1009757,393239,719457,834309,2119553,1137342,493678,1253590,2734976,2420905,1214662,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2851701,1165136,2026951,1963111,1261886,757631,355337,1304862,3082524,2228999,709309,1848027,1225441,1534907,1163597,1681854,2093397,1146766,223530,40070,1757232,847892,1772503,1760007,1183720,1069906,2858495,1130846,2609179,1634009,3484774,1901637,973834,812968,1134623,448204,1179285,537965,862474,1838770,587542,654672,1869813,1246591,1054371,1234509,1324303,1409400,323876,334576,60381,773316,473694,472323,262133,389626,246485,344427,314108,104222,528894,1079721,895715,498389,1046685,547404,620744,605546,764623,337343,177668,622518,1388861,1009029,286733,857548,674180,608702,407218,514329,883907,378045,66594,19062,793971,406460,682911,639687,909840,583842,1152143,555606,1076618,446219,1210856,657588,396431,301621,390622,213165,519828,146605,368922,784471,274761,335646,615450,495239,672739,707232,581137,547698,155396,241304,20483,387578,476901,657372,174960,319527,441649,1008257,549113,210114,692290,1563894,1039878,573906,3246364,1463041,1705786,1352470,335656,209457,259917,476664,3779353,3564677,1019272,3900004,1097700,1558245,1236677,1888327,2875858,1653238,409962,98430,449428,248403,771952,707800,3147405,3224596,7482886,3729822,2236361,1613565,4067676,2494397,1194450,1037720,1672267,973488,185050,73520,191295,188468,904668,1787827,2765617,2223459,1615574,1570609,1921889,2001262,322207,444496,101720,1203777,159450,215071,187234,178565,669605,2084020,1165730,441291,1057837,2147725,1849794,1229056,2227327,888444,667600,498855,5473953,2233001,757038,5585843,2538025,1352115,391214,1475825,1558657,1156542,825661,1743250,1577324,703438,136536,26242,2784434,1348703,3366797,4354223,1065102,732385,2815974,1358297,3436258,1526409,4569393,2390743,863691,614354,982812,456192,1767904,530501,1035354,2733486,630658,531016,1580342,1325650,2079195,1176360,2384845,2485614,128224,192858,28452,687209,1211309,1289374,544424,1145328,207559,405578,431543,247175,463840,998928,1362437,797596,1800839,1279212,1848623,1472043,1736583,1073943,651537,1955061,3887031,3217759,1403358,2803510,1878589,2504076,2009716,2550524,1978753,1144867,270611,56861,2056695,876025,3368154,2496608,1770297,1641280,5235435,1843274,4086531,2511595,7986187,2698745,830611,557541,1301710,521403,1483167,642192,1320757,2511878,660646,901842,2505101,1978190,1747037,2207332,2258453,2414421,241703,268094,74378,1054403,729790,670567,545962,663474,416666,556962,538718,176029,1157476,1972005,2194093,1039181,1880293,1120305,1003141,778135,1742581,651403,451787,1877249,3031544,2290650,767443,2024024,1173310,1246899,1100458,1101453,1876264,957253,179031,60047,1153253,624762,1821557,1268391,2116515,1743948,4161439,1598876,2030771,1162418,3078032,1246584,655242,514653,847763,333018,978075,284196,587415,1465522,596854,653022,1591113,1128020,1084127,1216525,1465581,1367123,370614,437591,66995,1345672,1330505,1458310,635962,892045,1034750,2795794,1295450,648080,1774839,3665780,3299488,1531488,2661197,2214833,2690743,2175298,2042553,1316462,1018291,3533675,5390343,7121956,2825659,6352287,2114585,3054375,3504705,4673881,3864211,2735166,1419304,260876,2355158,1520783,5917324,5014979,5929402,6561625,15292148,7418904,6964460,6206589,17445086,7274560,1523088,1201934,3681251,1581143,1345168,508546,1496435,3130044,1338346,2736649,8506159,5338907,3386921,3875713,6336323,7174716,456058,615604,293888,3145193,1610395,2479297,1987888,2532067,1228273,4531681,2900644,1103331,2501844,6731757,5544531,3878205,1741095,793852,638611,386588,5110872,2067874,897656,6707007,2213211,1434383,776053,1411081,1920870,1452601,1394756,2161874,1586606,843148,371253,95993,2558471,1145450,2987755,3559289,1698204,1362372,6582892,2300322,4788410,2243111,6502969,2413856,749692,407978,861906,453963,1772460,460161,868254,2684161,489918,448845,1497218,1060261,1522142,849786,1681642,1965502,199510,195164,133139,1178197,1017479,1051768,622329,1478423,515468,916177,731823,350750,742534,1467449,1734983,904040,5221638,2520883,4422601,3840309,3267983,1602060,758716,3042931,6906876,5027935,1818255,4296285,3292784,3272270,2971610,3847442,4828342,2536047,282112,66181,2880259,1266257,4086813,4009913,2226660,1971823,7032901,2492219,5899852,3645940,11190670,4685076,1748616,1290224,2321349,988868,1798120,686029,1437612,3002661,1120272,1178455,3639409,2699238,2533790,2815961,3081243,3185443,505514,504754,130067,1679705,858907,782140,578029,813851,402736,438252,542739,210539,1090228,1836402,2024125,919570,2258392,972970,1459300,1220105,1587454,690374,298197,1410118,4243918,2739253,856404,2513282,1396583,1133427,1000776,1202809,1993600,963008,112553,43394,1665899,671471,1901283,1779205,1955664,1452581,4107864,1776302,2282587,1039547,3379953,1849386,658144,427540,621270,337151,1088573,254178,490493,1460924,753553,717612,1611734,1048628,1344785,1229844,1448660,1395545,374742,492678,67219,1390575,1634741,2016370,671962,1263826,1205818,3206746,1717187,784808,1976329,4163105,3437283,1665815,5263912,2642306,3691638,3547866,2435442,1405844,870910,4244552,6881847,7353314,2293454,6738552,2665353,3367692,2914401,5196702,4446392,3023831,762284,210451,2556903,1388223,5111952,5050979,6413608,6541090,17184718,7119098,6769493,4942280,14977013,7928489,1679788,1408883,3037359,1521541,1005338,379586,985106,2415478,1506809,2640727,7055715,4816747,3949955,3998348,6031314,7612763,695979,911971,240250,2875902,1492412,2039493,1439563,2145887,1369353,4152686,2783837,964715,2173916,5978826,4722346,2800938,2828785,965906,1068838,685316,7139089,1941534,907873,6699113,3535586,2161456,780777,2147142,2306544,1303508,1203871,1901862,2168201,1043439,223061,84029,3424726,1380549,2951066,3727357,2041358,1331241,5866925,2509281,4961483,2002823,6217473,2833343,791196,375263,938293,469756,1692926,427753,943422,2496988,616358,455649,1716640,1485495,1659336,864932,1991778,2195576,229499,319742,90026,1353006,1560047,1490528,616321,1761613,522353,944539,971456,290732,689593,1514114,1509048,870317,2108422,1017394,1833442,1109143,1747856,890417,414639,911228,2019809,1200044,500847,1067020,2489216,1948253,1294364,1052665,1862731,927118,231979,22037,1051571,547159,1500210,974241,915896,710718,2257874,829138,2739792,1417462,3654017,1533857,1419005,818789,1457447,502843,942023,328785,687357,995976,556170,299612,855642,379758,1707957,1167182,1493935,1151627,237003,235531,57649,594152,296691,191402,119696,133448,172854,148444,190374,89207,673887,751599,877536,338480,1845674,768429,717476,594889,775827,333729,152243,484971,2415263,1418774,410666,1024105,1100592,756120,465047,354641,1400219,597647,51879,8231,560081,299705,495389,407386,1006636,551562,1255747,504059,857610,397259,801405,543559,632011,386713,662755,239096,266830,81195,200163,281261,342708,287399,569472,281484,1119880,760198,839140,482720,209755,272599,60644,319662,430177,619322,162233,272290,408308,813759,692468,111150,1000082,1704783,1193585,598331,2735826,1209037,1739367,1366446,1497840,766425,428092,1211249,2093176,1670776,622901,1560581,1191276,1053854,760123,892124,1272054,786602,421702,85125,750313,408384,1135543,1016376,1771140,1418692,3954689,1640694,2055590,1355056,3113430,1708184,1157010,709844,1105951,442701,782045,178858,562789,870873,894885,721632,1578580,980605,1660479,1357360,1797386,1500534,174680,249003,205977,696882,308092,408220,187854,319435,575856,1465134,1036930,399529,1318800,2258264,1912029,885999,1642637,505130,713945,237396,1474221,580640,224538,1141765,1965897,964932,395043,743779,771946,453308,353262,451130,679076,316330,97722,1842,425253,173249,508074,369627,646463,319383,1344306,679541,788397,383686,1023071,475265,383819,216460,364512,105339,613203,148500,340465,627854,322880,204884,595446,309940,717685,397199,823456,556139,53064,71460,35856,232451,202893,160408,80904,161686,172753,208745,319110,98932,382568,541183,662681,324810,1903608,802881,1310072,761856,901613,415847,199637,445497,965176,553938,250278,499010,2253501,1749436,1143443,1044083,1991749,883581,61660,7718,978819,448684,850231,864643,748037,479194,1563554,630833,3459914,1701738,4394652,2111578,1063878,725159,1016366,462487,393394,102086,272704,500116,260152,196429,433379,192208,1337010,920500,1135625,1011909,205007,213384,13810,624547,271089,203036,95382,104313,152955,147893,160606,53731,742527,756147,785990,284041,472851,178783,198492,196582,250749,139073,59295,146682,553972,337643,102248,195602,563633,468533,243946,293302,399297,134320,5494,6957,311444,171231,250591,157697,381067,188352,322094,133706,792191,357402,723147,522518,189547,145211,206903,73555,114176,11556,77223,104208,109015,60227,129060,62416,711673,389121,456710,297596,31338,63996,1112,53867,203910,276683,82167,84855,97593,163674,97160,12758,475159,1043860,738136,254644,1801051,783126,801795,571842,235639,114447,72689,186642,1127172,1118196,292901,1039102,635029,595601,367017,421407,1057587,714236,52512,5740,184407,134466,233644,181747,1172732,1197338,2230965,1109777,1052864,716339,1474216,918126,698463,345886,687135,240244,76632,27637,105867,59639,347972,367715,547383,334747,646765,429245,500637,377277,112663,187518,24399,543909,92705,73874,39637,50570,437336,977101,593454,181600,535502,665229,438717,351981,3266334,1101298,936335,392614,3974402,1919829,503192,2767239,4499486,2347611,625578,1966289,2135674,1087227,822384,1081226,1415197,725340,59595,5259,1570144,745677,1600209,1405066,2079966,1211323,3482723,1653354,2263654,1204314,3670572,1636538,1037351,486370,992993,305319,969032,281641,692237,1225363,1098237,630268,1946744,941017,1724128,833609,1760875,1212450,132478,194149,25688,534002,579572,676620,285250,461481,490775,772966,813134,153034,917728,1389149,1769735,665219,1166280,538241,888113,643999,932636,257924,233550,372475,568303,259506,196558,293512,1890377,1381481,1152449,1037559,987195,589186,21808,12879,840053,437797,854479,580308,425331,256402,807901,327120,2214808,1353868,3373085,1430365,840999,402974,911282,271081,541981,138954,307475,567919,231805,125146,397631,167239,1551171,1067885,1444515,1015699,263930,175191,14974,551156,332624,205335,82415,97614,133316,164693,212964,78335,794984,960949,1009136,386183,1954268,776408,695286,659388,913427,353611,191464,676815,3441515,1631366,456972,769615,1497141,967153,752063,692108,1268270,463374,25895,1305,827383,293952,556540,480505,1106351,524041,1085048,436232,1434722,522681,1202845,653311,607180,358975,456195,332455,314416,88690,239702,394408,333189,284023,474970,223685,1190171,661766,1005326,643192,160756,197044,17925,232804,386484,427364,151471,253649,286360,400708,331896,113698,1002524,1644551,1682420,775151,3023911,1607661,1956430,1998994,1980362,1052572,419039,1796616,2705321,2460191,892555,2283777,1688614,1722367,1328485,1613833,2261347,1392540,131155,29110,1115029,685816,1417507,1477875,2789246,2704299,6246520,2758980,3514367,2332948,5335351,2807412,1312740,897123,1773609,737165,1216153,315292,774243,2017856,1155031,1047888,2363533,1514908,2655262,1986447,2734373,2480610,353831,437856,60998,1010225,470570,539299,271695,332415,951386,2223117,1741491,652298,1852062,3361208,2775504,1683974,2571159,1033546,1148081,451381,3089561,1166309,442357,2844551,4512974,2558654,1104772,2452313,2085961,1222648,977327,1183830,1927182,1009288,69438,8873,757663,377204,896071,672147,1551322,965968,3428332,1717257,2140513,855036,2515544,1118099,784146,442175,834775,302244,1304147,254948,838872,1822891,780534,462768,1627042,900726,1884222,822896,1883392,1345588,133550,279266,29450,585171,205510,242896,132171,199925,462047,739311,1001541,264123,775462,958046,1580532,609061,3826008,1520736,2831857,2147096,2187815,939770,449403,1062939,1920076,1075548,505935,1028324,4181061,3205841,2411338,2070901,2899598,1552007,147568,37324,1280385,689952,1582864,1129195,904588,791024,2468458,925192,4951978,2873725,6897216,3025381,2109760,1300943,2182176,731203,889257,327781,513567,1067172,459482,256162,939644,398500,3002691,2384727,2799602,2277611,428216,389395,62614,957955,443316,263790,101790,140732,217358,164416,309202,59670,1048846,1173410,1430154,548129,2439132,907493,1047474,1037992,1435226,614571,237527,1035249,4879936,2654746,796494,1962906,2231525,1645219,1106237,1159406,1867026,861699,54958,17477,1284358,516084,1199829,947918,2304305,1343697,3158882,1449594,2287125,1007530,2222803,1554025,867321,501183,762115,309977,394353,138255,230489,487051,632698,410843,959706,431727,2508432,1463135,2128628,1527726,505645,697471,46144,553470,825681,1098504,317516,539731,644278,1384354,1379700,231914,2253039,3350166,3401302,1395403,3527499,1365259,2247648,2004493,1921595,1071997,448410,1958425,2552648,2294996,798871,2549600,1974248,1896533,1261851,1684463,1979323,1342639,239693,50857,903563,544419,1520834,1658349,2554024,2320620,6838106,2762036,3137204,2179761,5309613,2532397,1321560,1006905,1494977,653151,727089,251241,542013,1061989,989654,923549,2021967,1135961,2644809,2532851,2957793,2325953,440206,537051,81988,960126,495233,641611,291798,398891,932034,1990615,1801260,603051,1786704,3054912,2516458,1476292,3611979,1035736,1544297,722174,4858050,1917169,620573,3920435,5530017,3040812,1006534,3264157,2810652,1665852,1430339,1785596,1633584,859497,141371,18023,1125872,537845,1663641,1357173,1902350,1078655,4978787,2394027,2855598,1563492,4442554,2083587,864647,470291,885168,281454,1245203,314431,814206,1895282,788828,483212,2067558,945120,2845704,1510591,3634518,2482001,306965,294412,17198,514797,647693,589401,334337,528711,446163,775184,1266520,238730,1333719,1919008,2551155,1267512,772134,256592,541136,401307,420205,265254,132953,455116,669890,638280,264924,437340,308848,506250,389767,457485,369532,155678,40127,7249,208710,116274,154039,235523,301957,124099,567437,219066,766095,459849,1053032,584666,240814,195690,401596,171769,274421,92293,152992,440401,114224,177861,377274,322493,250356,258006,436867,424866,52157,29025,9253,61104,36626,15227,10058,22606,29077,21788,26008,14336,94200,72079,150175,47644,636990,282949,310478,276672,363255,192141,71509,562197,524518,570860,166233,511093,165506,214561,163178,214612,449989,264758,43203,16612,408140,301920,393942,397678,429261,318595,663958,328780,383546,229286,456824,347983,219512,152318,293764,214852,169484,49788,135099,449153,116739,240506,350603,312280,249517,318187,318354,372632,217002,262418,31733,372479,317813,423033,175069,293841,197042,540411,223974,133626,459857,1089515,1205721,518362,0,31,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,31,0,0,0,0,0,0,0,0,0,0,0,31,0,0,0,0,0,0,0,0,0,0,0,0,0,1856242,785594,321607,134785,1643168,851366,268591,2310085,1998771,1334326,611175,1575423,825225,583530,562004,1181367,1037295,631377,74210,32339,757847,395466,553699,1176418,1466001,1040647,2323207,1508505,1716212,808893,1914718,1124670,626113,293308,607167,340486,376717,82105,149272,815450,348609,315932,1161567,941178,774046,488399,949245,1087435,196821,218288,24381,621721,257263,394775,153139,367072,375551,906165,730725,191469,389498,1021563,1303072,529973,2313584,961734,1191515,934321,1057837,630464,195845,967902,1116181,804387,228269,685283,774665,998397,725966,979249,1277617,585421,98407,20032,466114,242464,631408,516430,455381,277225,1220026,414452,1753814,1045911,2618218,1107150,830820,473249,864935,421573,486374,210058,302765,831904,223704,129971,652225,440504,590314,598956,650222,802572,52802,55025,29769,131473,174117,78956,27836,43669,34374,31796,41179,12544,128868,156422,198931,68603,1370639,643707,581914,575002,896556,430896,186019,1125232,1421570,1232555,291830,1025591,542328,703511,377086,585414,1435175,755876,75674,18348,981438,495096,931105,1198703,1103294,685897,1649479,870194,932342,549979,960500,783959,507708,392752,603127,247455,406110,149030,179022,687395,287783,398257,775185,542896,553765,540292,545619,663939,292653,337769,75323,778905,715252,857716,186799,406755,362750,850225,609673,201999,672234,1460792,1250395,507377,885010,497064,502608,389023,143252,81605,59917,198924,961067,810095,226557,864516,214885,268818,147340,394475,636041,290340,129172,34358,154309,60654,136965,142336,853731,770179,2009201,650861,420116,281562,673313,440567,183100,122064,204987,117106,39437,9542,38874,71251,161135,219155,480060,327685,217983,111307,173521,245998,54597,81961,53310,171536,46276,72234,42625,43523,165618,559602,329543,65099,139154,340533,251809,144049,1085913,341633,391086,154130,1335991,592764,138054,1631931,1691677,914021,307705,1092636,481114,426216,390311,751074,585129,298009,69616,14499,679123,298998,650440,756778,709699,294037,1376028,573482,1110894,608489,1764729,925116,224184,120053,358513,194490,391169,117379,157430,623889,264106,206802,940139,801267,508119,346904,781825,745704,51646,55954,13213,125123,240296,204677,125667,213033,109702,223071,268810,79861,136237,389279,519801,205066,1106540,359071,875494,685540,747525,368832,188876,684587,1327558,705578,446036,803382,901331,819823,722933,1046843,690383,260191,83429,15569,467138,131883,548202,435513,422191,198455,1300827,408799,1796368,1049400,2911325,1202714,397698,231140,671739,244746,342784,129378,248447,547549,164829,114233,573993,413809,616927,560425,788703,809970,48426,26861,16397,149247,47383,41442,73545,49532,56387,61518,81524,17747,185540,145198,289738,103277,2632707,959140,1077494,975909,1495586,705166,279648,1843197,2768005,1895135,722186,2064766,723697,741215,710382,881552,2120565,1086704,101385,26406,1135779,503001,1489808,1450035,1528045,1013773,3244086,1493520,1372157,774969,1834212,1080808,790802,472143,866447,511141,484906,155171,336705,1027436,611419,577876,1388097,967335,786290,918489,1006187,915498,339507,436796,169233,1255385,853342,880362,425816,726148,805942,1576586,981532,598880,1417037,2676608,2741992,1342084,909897,485959,625912,603269,554888,324466,129064,851448,1698799,1571131,612403,1644395,457652,674901,500465,962726,763192,541062,184294,46157,600352,311436,883005,1203219,1572308,1365620,4308562,1818037,1397967,1169682,3172875,1624806,294060,230439,465632,280528,319692,118911,175223,552734,330508,614884,1310458,1190999,597258,749476,996932,1309113,83783,170881,100246,626116,361635,504232,333935,497041,387928,1067895,1196762,513731,450820,1158499,1237074,734981,449014,187496,188477,108260,940307,502443,130125,1474924,508910,343830,161278,408294,314180,216045,214041,432526,346586,171121,32762,28731,409296,195035,409725,674667,319008,201463,713797,336939,672624,277512,941101,529551,131092,79593,184066,119533,242354,72313,159129,416577,84740,75736,280225,154704,270843,178862,323053,418463,31804,62698,60960,184119,159292,189263,114461,221495,92044,125477,245762,119933,87588,321919,469613,168412,3246215,1161026,2022705,1685212,1847830,681826,268631,996214,2284260,1521831,578218,1230402,2591526,2238423,1801798,2169243,1808388,678357,80496,9923,559620,267276,652117,606629,607128,458282,2187259,624110,2621108,1703790,4232105,1738055,1376434,586422,1791995,624981,508323,191298,290093,804588,543468,231180,1193302,821388,1403051,1100080,1671693,1674355,97252,72945,20826,210457,166418,94880,62870,84730,82392,100333,98371,34974,316298,299947,501269,189720,3485552,1709668,1582237,1581701,2314146,700928,346247,1910497,5717543,3881141,1168607,3453817,2681246,2144671,1766857,2009715,3589622,1999363,98853,20363,1630346,750069,1580676,1735192,2081989,1325833,4091963,2038621,2572865,1466236,3069970,1970515,1171797,830671,1261340,596255,761412,190768,338272,1159524,1132433,1090115,2574948,1689455,2201081,1782720,2161535,1915648,928990,993919,81969,2526909,1267401,1159071,475682,893809,1098997,2354224,1729715,721112,2782425,4910481,5689893,2192621,3477947,1478822,2004297,1912460,1782001,837360,354997,1829149,3868008,3284334,1004486,3252130,1061019,1035359,962655,1133860,2433232,1311668,214286,47735,1415325,754974,2057850,2123132,2845185,2718254,8053207,2621569,3050410,2528776,5366845,2312560,816547,173296,1636099,625502,644317,131327,373007,1086341,1184738,1340807,3388086,2701864,1562093,1462366,2160817,2616064,317884,458149,113040,924863,789301,1005686,450089,682046,879317,2714387,1592604,520587,604425,2035844,2086458,922234,1864605,494119,804249,458585,2866859,925019,315690,2806930,2974816,1459893,727395,1600031,1045185,588448,611952,686868,1098647,539717,80567,13115,1268297,513229,1084116,1272174,1322076,884151,3650968,1313466,1500889,716155,2276613,857978,406789,174066,470150,216864,664854,150536,422813,1121635,402910,333184,1205249,849290,914944,479449,1286653,1135196,129637,196904,61855,336359,430808,554757,222149,431016,340837,684900,551838,184421,195572,683606,1037556,259425
Saccharomyces cerevisiae,4932,genomic,RefSeq,2923358,5983,39.66,44.52,36.5,37.99,1968,1941,2394,2481,876,420,839,676,2359,1278,1066,1169,2285,1114,1005,836,1662,1435,99,51,1008,568,2145,885,1910,1298,2131,1227,3499,1884,4146,1553,1886,1134,1476,664,946,623,1103,390,1351,994,1008,579,1878,1416,1476,585,604,425,63,942,262,152,201,156,845,608,1203,543,2420,1058,1154,583,1283,1137,1283,1440,614,336,667,483,1976,1241,917,1145,841,501,347,332,844,825,47,23,954,567,1907,885,2557,1820,3196,2255,1581,850,1678,713,880,631,662,313,729,573,986,220,1278,877,918,439,551,396,456,151,387,256,23,555,378,155,149,79,832,576,1162,520,1120,370,364,197,2029,1295,2126,2002,1059,479,1337,1079,2010,1148,1289,1466,1310,732,790,813,1288,974,102,51,1045,613,2860,1313,2492,1795,3030,2351,2683,1447,3458,1498,1787,1097,1596,785,1227,548,1714,631,1562,960,1488,659,1244,833,1179,500,675,397,64,860,510,264,330,175,1193,766,1848,844,1507,616,834,433,1602,995,1435,1561,729,326,940,731,2516,1305,1427,1581,1706,926,928,898,1118,893,84,34,1112,614,2303,1016,3294,2550,4958,3544,2877,1558,3664,1534,1148,817,980,405,946,682,1368,368,1532,1095,1225,621,1799,1142,1426,555,438,299,23,423,461,195,227,127,1182,834,1964,851,1808,693,760,418,1150,1265,1527,1505,588,311,573,415,898,461,428,371,783,392,400,446,1064,732,31,21,591,309,1014,403,704,543,794,481,1380,704,1354,500,1234,889,972,453,593,343,810,271,553,304,411,217,783,483,596,269,468,274,30,465,239,100,229,90,236,174,360,159,854,396,506,235,500,384,376,392,199,92,195,159,548,334,382,293,288,167,182,150,348,242,20,6,209,110,295,174,716,438,760,536,648,296,515,279,433,286,303,177,204,134,264,65,387,290,307,154,241,159,181,75,199,124,11,153,82,51,72,21,314,203,250,130,404,134,142,83,1007,642,1214,1057,495,267,709,608,887,570,750,729,618,374,456,415,787,573,38,18,592,325,1268,642,1465,915,1594,1130,1346,699,1788,768,901,694,818,449,648,336,859,338,642,405,715,283,744,397,653,246,386,202,26,473,289,98,185,88,572,415,937,419,698,330,436,202,737,550,673,751,401,196,529,448,806,478,688,540,543,363,496,406,516,462,30,12,475,281,966,520,1160,829,1603,1017,1196,729,1506,706,467,316,496,268,389,345,511,203,461,288,451,266,528,471,634,283,217,160,22,242,174,106,175,101,372,305,551,290,604,347,426,189,2213,1886,2737,2465,1399,499,1102,836,2528,1508,1351,1312,2425,1371,1188,1181,1561,1136,84,42,1360,758,2584,1059,2231,1476,2550,1716,3877,2084,4526,1657,2333,1437,1699,696,1505,699,1950,684,1617,950,1208,540,2307,1552,1755,701,741,514,51,970,562,216,233,133,888,542,1326,579,2458,910,1070,641,1022,840,1037,1103,576,331,622,461,1743,1224,988,1187,847,522,418,410,665,644,46,16,675,323,1163,559,2342,1854,3162,2252,1806,996,1850,906,907,681,685,316,545,307,925,219,1294,836,994,426,696,446,540,219,377,254,13,462,264,140,118,73,902,521,1300,517,1010,430,432,287,1767,1035,1510,1303,698,251,829,716,1332,755,1243,1094,787,421,618,577,1231,920,97,38,689,446,1073,601,2166,1408,2318,1521,1876,1042,2004,991,1475,854,1440,655,759,434,1033,562,1010,529,1114,517,733,482,790,373,520,338,46,749,288,136,304,195,739,551,1227,592,706,420,488,282,1606,898,1112,1061,962,331,910,823,1812,918,1080,1371,1381,717,780,652,927,772,65,28,732,366,1614,598,2314,1566,2845,1792,2394,1434,2854,1107,1330,824,1140,549,728,435,877,257,1116,808,1368,563,1358,846,1253,473,414,299,35,543,335,113,144,97,1014,678,1311,558,1418,691,791,468,1474,1451,1882,1975,1020,416,689,537,1960,1070,899,967,1850,995,694,669,1323,1026,58,27,920,519,1639,593,1711,1172,1885,1303,2470,1301,2625,991,1924,1150,1343,540,1190,528,1458,357,1339,774,842,361,1648,1023,1119,409,607,382,42,679,543,184,144,89,656,452,924,344,1777,589,912,390,768,574,684,873,503,187,334,295,1405,837,571,740,742,373,321,278,433,502,20,7,473,278,717,280,1288,975,1665,1486,994,655,1128,422,696,491,448,209,386,231,605,103,947,687,700,256,618,360,516,125,281,151,10,289,214,92,52,38,555,350,739,316,803,272,336,182,1080,564,770,865,476,220,474,436,804,416,715,666,647,325,443,463,720,509,47,14,505,215,838,479,1303,803,1507,927,1510,726,1536,805,779,595,746,356,594,319,825,315,635,372,685,356,580,341,710,295,251,199,29,383,283,110,217,91,445,337,778,378,560,315,436,244,801,448,562,688,435,208,481,397,721,400,569,576,697,383,615,512,491,379,24,11,375,200,788,413,962,750,1467,1038,1369,773,1883,880,509,350,447,258,424,301,566,216,505,373,560,248,633,514,717,247,207,167,15,256,153,89,79,90,383,302,642,301,575,332,407,287,1689,1259,1626,1867,717,324,678,585,1694,994,788,1025,1273,740,487,696,1351,879,46,21,855,454,1543,573,1729,1120,1913,1204,2355,1379,2526,1050,1402,824,999,508,850,348,1120,375,857,569,880,485,1184,705,952,396,536,314,34,599,404,148,168,104,531,353,896,466,1592,612,790,451,1083,840,931,1248,456,250,544,502,1212,941,662,925,899,536,414,434,1055,919,53,22,691,450,1352,584,1614,1223,1912,1536,1627,923,1686,724,903,545,649,276,393,206,744,142,892,500,828,360,706,424,448,176,493,234,55,551,357,133,95,83,522,336,887,454,1061,378,432,257,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1,1,0,0,0,0,1,1,2,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1,0,0,0,1119,832,1408,1380,523,249,527,387,1190,754,684,644,890,430,448,411,930,546,35,60,893,506,1040,442,1218,756,1286,793,1532,813,1760,714,1097,612,858,423,800,283,914,375,680,383,639,243,793,549,617,280,435,208,45,480,334,143,258,84,430,286,696,304,1009,429,544,325,460,436,471,618,285,143,196,210,722,417,407,406,521,257,243,192,522,371,21,14,457,312,625,305,886,656,974,791,851,476,895,370,527,346,452,170,250,151,444,113,493,274,471,188,327,212,259,93,201,143,18,271,220,80,69,52,302,238,569,192,526,216,209,136,1912,1289,2270,2277,826,351,1182,1058,2291,1237,1577,1722,1488,756,962,940,1536,1138,90,39,1059,541,3250,1891,3032,1912,3059,2504,2854,1300,4104,1737,1501,779,1190,575,1021,356,1321,518,1497,792,1392,648,1491,842,1110,474,623,275,46,882,502,185,300,173,1319,751,2024,948,1667,719,744,431,1252,710,1013,1041,520,246,606,517,878,534,676,554,564,310,423,389,861,757,49,18,688,344,1910,1376,1290,756,1549,936,1253,744,1547,757,540,320,574,289,464,244,570,257,417,271,576,246,596,391,551,280,242,214,21,338,327,150,158,119,401,292,626,353,509,378,439,176,2701,1880,2660,2686,1046,550,1182,885,3422,1795,1906,1897,2527,1311,1290,1063,1874,1394,112,55,1378,683,2217,847,4854,3087,4135,2454,4854,2786,5815,2508,2427,1412,2202,975,1467,560,1685,635,1886,1214,1878,816,2254,1455,1883,804,735,440,69,1049,508,223,296,139,1789,1204,1610,821,2633,1527,1603,1015,1728,1231,1495,1832,849,413,800,651,2175,1311,1277,1287,1582,964,752,617,1454,1207,91,43,992,565,1863,844,3490,2689,3390,2604,2815,1488,3010,1203,1804,1122,1277,609,907,424,1159,298,1598,1002,1356,554,1194,678,864,278,596,311,69,895,434,185,139,100,1357,1061,1510,666,1535,699,747,423,3609,2283,3450,3018,1670,660,2342,1680,4067,2133,2785,2425,2852,1373,1533,1476,2872,2076,282,127,1404,745,2893,1413,4853,2983,5511,4175,4448,2266,5960,2751,2499,1384,2481,1077,1601,722,2064,691,2231,1285,2404,947,2073,1091,1691,563,1021,569,136,1571,713,271,443,284,2036,1420,3552,1772,2078,888,1135,617,2279,1440,1794,1975,1090,471,1364,1082,2346,1385,1472,1327,1759,963,910,722,1614,1425,72,45,1345,794,2602,1178,3137,2334,5870,4279,3389,2059,4910,2117,1247,766,1145,569,1081,556,1594,402,1524,1014,1593,734,2095,1136,1468,606,491,337,53,668,549,234,247,190,1097,809,2386,1063,1754,972,889,401,3221,2204,3318,3534,1368,622,1162,924,3958,2334,2148,2121,2769,1506,1307,1285,2328,1441,99,56,1221,665,2006,858,3617,2144,3775,2174,6165,3256,7112,3081,2625,1513,1949,934,1585,632,1711,643,1815,1148,1656,759,2615,1404,1782,745,764,385,49,1181,639,244,263,111,1349,913,1620,706,2607,1137,1279,769,1426,1065,1381,1674,769,326,668,606,1968,1213,1155,1158,1317,581,661,578,1280,1064,48,31,862,500,1470,705,2086,1614,2380,1970,2709,1477,3203,1290,1450,799,816,484,867,412,1026,281,1309,786,984,399,1029,607,720,223,527,283,31,671,516,189,150,88,908,652,1135,509,1205,540,492,297,3335,1792,3237,3397,1508,680,2099,1553,4432,2217,2725,2754,2870,1381,1543,1400,2527,1849,135,50,1360,810,3245,1532,5748,3708,6166,4873,5868,3053,8513,3626,2455,1431,1903,872,1292,553,1491,505,2784,1501,2494,1168,2653,1391,1919,754,904,467,77,1354,801,295,416,298,2373,1465,3196,1378,2716,1057,1241,683,1816,921,1431,1417,837,429,966,887,1546,823,908,885,1024,518,615,586,1157,976,62,33,923,476,1831,908,2107,1483,2870,1936,2393,1365,3501,1757,880,473,784,444,751,395,900,205,869,554,906,421,1048,679,1181,400,311,247,40,478,347,188,156,115,769,560,999,505,791,529,623,276,1445,1087,2119,2211,803,358,856,631,1802,1056,968,1124,1569,829,828,901,1033,770,35,17,1055,536,2321,808,2115,1284,2320,1504,2443,1146,2536,1003,2625,1498,2015,864,1046,625,1626,426,1752,973,1394,603,1748,993,1343,524,402,220,25,527,512,256,253,95,947,595,926,483,1728,650,768,416,1039,677,1006,956,423,184,475,355,1602,1020,882,1041,808,393,435,368,526,432,21,10,460,305,1068,418,1835,1290,2400,1815,993,482,1016,518,1296,784,952,496,394,229,499,123,1468,782,1045,446,651,378,494,159,232,142,13,304,275,106,141,52,926,644,906,385,803,286,337,166,1672,962,1744,1495,706,261,831,657,1278,678,1015,1144,815,344,706,525,1106,723,46,26,775,378,1527,842,2268,1400,2310,1576,1779,874,1994,825,1639,1011,1710,761,1021,459,1183,328,1187,572,1023,505,864,383,885,336,423,298,36,583,257,140,271,104,1003,741,1604,716,947,493,713,321,755,470,758,724,360,157,494,395,591,343,526,584,409,160,328,257,506,418,17,7,480,303,827,436,1030,649,1298,902,732,330,752,389,588,464,607,359,415,268,535,203,426,250,494,239,283,169,361,158,165,111,9,288,116,85,79,44,383,320,621,300,297,186,213,112,822,698,1123,1052,478,202,440,423,1053,628,609,579,1036,465,678,536,769,506,17,10,703,379,1512,571,1192,724,1192,729,1584,745,1963,860,1151,704,999,443,740,353,1131,315,702,557,685,331,1056,491,774,297,227,129,18,359,320,121,186,64,433,242,430,200,873,394,451,294,601,408,577,488,209,128,225,159,793,487,518,503,451,226,367,265,304,250,6,0,294,127,416,195,836,533,1038,775,531,286,683,280,717,354,434,198,225,97,324,62,526,359,512,226,350,170,248,65,118,67,7,170,106,48,48,25,368,257,372,165,325,150,158,62,1552,856,1476,1413,526,228,637,492,1536,767,1039,995,984,459,665,514,1042,685,22,10,689,366,1354,837,1931,1261,1985,1759,1636,770,2477,1114,1431,693,1176,473,930,307,1454,443,1297,690,1056,424,861,418,804,246,260,219,22,630,280,121,131,84,839,535,1414,557,1100,454,470,227,410,261,573,409,242,94,400,291,450,237,359,290,314,159,291,184,343,299,2,1,277,155,549,416,501,368,554,417,536,301,731,366,293,181,305,122,290,157,408,106,213,105,314,117,255,123,269,84,62,47,11,135,74,50,52,44,183,117,243,120,168,191,208,104,1677,1287,2157,2206,580,275,706,469,1615,943,910,740,1544,754,854,768,920,742,25,17,684,366,1435,549,1805,1033,1709,1224,2182,1050,2623,977,1883,1039,1487,553,849,424,1404,363,1650,1060,1225,554,1590,984,1292,440,385,194,28,609,263,102,116,81,825,447,835,326,1761,551,664,417,742,594,850,743,407,133,308,286,1435,899,825,737,814,483,445,394,526,471,15,6,359,238,789,300,1544,1269,1957,1570,1085,539,1102,500,913,490,714,272,385,236,669,154,1331,838,955,467,740,446,539,196,255,143,14,364,178,61,54,39,575,409,769,297,924,267,307,164,1537,754,1354,1073,556,237,649,477,1454,639,1054,1024,947,484,848,648,995,614,25,24,780,381,1099,579,2250,1455,2184,1727,1909,932,2216,967,1291,742,1181,465,1026,406,1169,329,1094,714,1384,512,812,530,994,379,411,277,20,612,265,118,148,96,952,589,1533,662,1085,513,720,354,631,382,579,601,347,142,409,360,479,292,513,410,421,246,420,345,474,317,21,6,404,217,617,343,903,555,1103,710,860,465,937,465,446,290,506,217,498,266,495,236,370,262,479,204,386,233,469,221,159,133,13,251,94,49,93,45,326,252,494,263,413,266,322,188,1128,887,1647,1958,805,297,694,438,1896,1025,757,982,1673,870,741,760,965,776,83,22,745,503,1767,594,1609,1176,1920,1377,1984,991,2638,930,1709,1229,1195,536,795,461,1197,232,1632,861,1019,430,2371,1217,1287,457,464,194,31,551,436,152,143,118,666,438,986,372,1957,618,612,282,864,589,742,824,483,214,429,293,1779,1001,701,962,826,412,348,326,557,400,23,13,407,201,861,310,1495,1002,1783,1754,793,409,930,332,929,532,512,249,315,202,564,84,1157,744,794,395,1007,543,542,149,345,146,16,277,269,80,46,38,586,402,710,353,878,251,230,109,1474,789,1275,1220,486,268,641,483,1231,704,747,1095,794,404,673,477,944,674,42,24,700,323,1219,571,1828,1187,1852,1357,1702,900,2175,882,1167,671,909,452,756,319,878,170,835,464,899,365,991,530,1009,276,420,347,32,463,290,135,114,60,798,571,1523,632,1065,500,602,254,552,344,521,519,305,141,393,297,415,217,275,340,319,155,320,218,413,305,11,4,327,156,566,314,511,420,698,567,606,361,714,333,383,235,369,161,277,175,381,95,308,145,300,150,421,247,413,149,121,105,10,185,88,62,32,33,206,137,298,136,297,225,242,95,668,475,673,736,323,171,312,262,763,462,410,395,615,354,270,252,462,311,33,12,342,219,573,212,599,448,791,453,847,465,839,417,552,327,459,203,381,239,354,111,404,274,315,176,550,294,368,173,290,187,22,258,177,66,85,39,211,163,308,169,823,341,318,220,537,303,381,329,216,121,176,163,488,261,354,330,266,125,193,125,360,261,8,5,251,155,475,201,432,267,550,403,394,219,374,172,369,237,251,110,165,123,210,64,258,176,235,98,186,124,157,69,241,146,8,180,142,46,54,44,189,158,255,144,325,140,136,108,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,0,0,1,0,1,2,0,0,0,0,0,0,0,2,0,1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,2,0,0,0,0,909,607,773,704,349,192,442,390,857,425,588,554,742,353,425,271,571,540,53,26,383,256,794,317,1177,763,1567,992,1173,750,1259,605,691,382,650,283,250,171,364,92,467,321,472,233,555,330,441,189,427,252,27,426,103,46,80,37,335,241,836,370,662,295,276,241,317,269,535,555,215,115,241,153,587,310,277,275,506,259,274,216,444,362,34,22,318,167,512,225,491,284,666,448,727,401,849,311,429,306,352,147,176,105,217,74,314,225,243,112,380,259,294,114,245,130,16,264,301,104,84,46,210,100,290,136,690,271,240,150,149,108,198,137,92,54,94,95,184,124,176,143,149,52,66,67,192,217,12,2,170,93,240,116,274,185,365,254,281,117,231,173,198,105,147,73,86,60,114,37,124,105,168,67,102,51,111,21,78,62,5,122,114,57,33,38,147,148,162,88,119,87,80,51,274,138,272,218,121,47,198,94,250,134,252,227,151,63,118,93,207,194,12,8,179,57,217,150,406,239,393,224,332,204,373,188,188,79,162,81,107,48,121,19,141,115,152,91,122,79,163,39,82,85,5,98,48,33,28,21,163,92,256,130,107,87,128,45,212,109,164,168,105,49,107,104,128,63,99,109,63,38,60,44,148,102,5,3,74,53,135,120,239,107,300,177,153,91,208,102,137,81,120,91,70,60,77,30,53,39,102,40,65,56,53,27,42,38,5,39,33,26,19,28,75,39,90,76,47,37,55,18,1059,791,1165,1127,438,182,328,304,1179,601,884,626,918,516,575,432,694,489,30,18,476,257,869,270,1711,1055,1854,932,2083,1074,2188,897,1098,618,1075,407,407,215,431,154,824,638,893,400,1042,654,883,370,350,215,29,369,192,102,117,69,835,578,650,348,1176,525,684,375,653,414,553,514,279,115,243,202,864,473,659,506,506,256,363,281,520,326,23,11,367,207,698,298,1393,973,1433,844,1152,592,1108,519,885,454,634,291,302,177,334,99,820,568,683,353,558,413,409,126,204,133,19,245,141,96,96,60,740,557,607,326,627,347,370,206,1740,935,1688,1489,540,240,841,623,1860,1018,1311,1225,1150,571,736,514,1083,780,41,28,811,493,1515,700,2539,1831,2867,2371,2303,1141,2792,1147,1126,601,1138,495,689,288,907,269,1243,722,1179,477,1186,705,930,328,441,227,26,604,400,159,178,132,951,656,2463,1007,1557,614,704,283,909,486,743,640,411,200,514,358,697,343,641,463,418,248,335,300,481,395,27,20,426,205,834,432,866,635,1763,1015,894,521,1170,528,535,283,546,270,405,234,549,187,501,286,507,216,582,332,487,191,155,128,23,252,230,103,142,104,317,242,727,332,371,235,250,97,1003,1035,1584,1639,732,335,815,400,2607,1441,1194,1418,2221,1264,897,838,1183,1037,33,10,743,469,1368,362,1892,1522,2595,2010,2624,1584,3039,1074,1639,952,1180,460,592,280,797,157,1489,971,1087,463,1870,1140,1036,402,571,344,21,732,428,122,95,43,730,600,1321,350,2963,842,824,542,641,397,610,568,362,190,359,297,782,441,598,482,583,285,317,270,673,550,13,5,562,342,900,456,1018,657,1136,860,939,518,1061,443,780,527,625,234,341,218,445,75,607,353,535,214,622,367,411,107,362,177,14,429,281,110,59,47,590,379,544,271,718,372,369,179,1353,626,883,749,387,180,444,381,927,439,711,715,482,222,329,266,797,470,15,7,405,324,777,371,1552,914,1620,1035,1011,529,1253,603,789,432,566,323,378,198,361,118,667,351,721,391,441,252,464,157,308,188,15,424,163,94,90,63,704,435,882,387,583,326,498,232,974,603,560,620,354,172,382,311,378,223,313,322,251,115,193,166,315,286,5,2,267,154,425,205,545,419,967,632,424,270,582,297,448,294,292,148,295,192,325,137,284,175,331,160,240,181,262,91,124,91,3,167,125,51,63,31,220,186,324,156,215,179,168,88
Komagataella phaffii,460519,genomic,RefSeq,2399330,5040,41.62,47.25,36.48,41.17,1383,1496,1054,2068,990,512,577,798,1572,1057,562,725,1948,1178,826,1144,981,970,52,57,811,540,1803,1012,927,885,964,787,3013,2170,3264,2147,1344,1015,1215,478,830,534,818,239,928,735,705,319,1762,1342,1337,377,417,298,35,763,277,97,320,132,621,376,796,309,1795,782,1968,597,1167,993,748,1334,721,407,453,643,1660,1134,755,1038,640,436,270,279,734,987,48,32,712,518,1163,900,2000,2178,2832,2742,860,659,1131,302,937,761,529,208,656,423,692,177,1157,865,856,361,226,251,246,14,363,210,16,505,358,140,248,82,876,628,1102,462,550,196,461,153,1116,804,768,1275,773,431,752,929,987,659,550,788,932,520,505,624,554,682,43,52,509,360,1207,883,808,918,1122,1266,1618,1098,1720,1366,991,733,900,473,717,444,909,270,880,629,693,342,912,571,797,214,316,207,29,492,265,127,323,136,576,396,827,389,692,339,850,305,1534,1027,890,1583,836,452,771,1037,2126,1441,1185,1315,1595,1016,963,1158,949,941,63,67,878,528,1719,973,2627,2495,3670,2962,2760,1805,3281,2374,1023,725,879,360,772,532,888,230,1415,1082,1152,515,1696,1169,1232,373,338,198,18,518,330,126,369,156,1186,746,1637,673,1169,523,1282,422,983,1002,972,1695,868,453,588,644,839,620,393,376,744,484,444,494,808,851,31,31,653,379,1619,728,704,628,894,627,1357,781,1636,835,1220,925,1112,455,980,568,1175,294,645,478,536,212,990,681,786,223,376,267,23,456,410,116,407,120,471,268,655,175,774,302,930,280,500,398,400,543,249,145,195,237,664,414,395,363,277,163,150,147,469,448,10,15,257,176,518,318,1042,921,1380,1217,350,205,223,248,533,472,447,160,300,214,323,84,452,307,456,183,211,118,212,18,213,124,7,160,145,61,133,45,495,329,489,186,205,77,229,68,759,564,645,851,567,307,545,632,731,477,508,492,586,375,373,408,414,403,39,26,347,242,889,573,696,670,876,847,1127,718,1156,872,635,473,628,262,481,263,574,164,542,352,433,203,599,402,556,147,217,148,17,305,190,76,256,110,472,267,600,280,497,230,588,203,967,656,619,1000,535,292,480,609,1095,808,743,670,897,512,636,594,543,513,27,15,419,218,880,421,1248,1091,2009,1366,1488,910,1693,1068,598,396,454,258,390,226,446,135,683,454,549,241,828,577,643,219,219,132,12,238,172,74,187,84,569,387,821,261,598,319,730,247,1467,1381,1322,2189,1412,706,924,1017,1676,1020,744,798,2027,1288,877,1239,1087,1064,48,44,1127,713,2164,1099,1211,978,1301,1105,3268,2313,3448,2112,1547,1204,1429,537,1464,805,1625,373,1067,817,810,353,2041,1459,1527,396,516,383,32,695,556,197,452,171,670,423,1034,356,1658,788,1801,561,878,664,663,985,616,345,431,573,1650,1110,770,984,736,425,293,377,696,893,36,20,563,391,983,778,2056,2119,2655,2716,1235,855,1299,726,950,764,714,236,656,396,709,183,1187,928,899,336,527,417,363,26,383,233,12,439,317,119,229,80,904,622,1176,444,565,234,558,153,1183,801,618,962,581,319,528,637,858,597,704,656,773,404,450,570,632,551,45,49,403,264,683,499,957,851,1152,1053,1311,950,1427,967,876,690,859,372,541,380,581,271,639,422,540,302,632,485,628,226,287,216,34,463,149,91,261,184,445,360,609,347,441,313,589,270,1213,849,684,1103,732,358,637,750,1299,831,712,966,1085,557,608,631,597,703,34,23,438,251,925,462,1276,1314,1745,1351,1609,1127,1617,1121,1074,725,961,396,602,340,541,162,879,663,753,259,1232,734,886,203,298,213,22,383,215,88,210,62,791,526,966,337,829,374,863,292,1127,1095,1064,1825,1144,564,702,737,1387,870,528,580,1694,1021,682,828,998,984,48,41,813,538,1604,907,926,903,1230,1024,2403,1631,2475,1551,1533,1125,1107,446,1252,577,1327,291,900,675,653,309,1620,1167,1034,297,428,318,40,619,504,132,332,131,521,330,811,253,1471,525,1473,410,688,498,439,753,460,218,248,333,1311,819,511,628,645,378,232,237,537,614,29,9,361,293,672,436,1390,1309,1651,1793,891,569,873,463,697,546,472,192,437,259,465,80,946,710,650,234,421,326,285,11,255,167,12,315,204,84,157,50,646,423,837,263,480,164,412,113,901,602,512,818,414,251,377,475,685,409,363,451,615,343,343,381,368,366,34,27,271,181,541,348,539,568,687,757,970,666,942,760,700,495,520,257,418,226,454,151,521,391,369,176,630,386,496,126,217,140,24,310,152,69,168,66,284,241,493,233,402,209,469,154,1081,701,481,794,505,295,452,543,1020,593,588,596,804,460,529,599,472,422,31,22,348,192,633,367,926,756,1386,990,1300,855,1473,1021,609,359,442,226,394,228,422,122,566,414,493,204,688,483,613,150,191,128,11,253,145,57,127,72,356,274,515,221,405,291,627,200,1139,883,763,1434,940,488,559,783,1041,763,312,540,1040,657,292,673,769,736,30,31,645,422,1164,799,779,633,875,711,1680,1160,1747,1179,872,604,736,382,710,415,764,192,514,452,461,232,1127,739,637,253,368,246,24,517,304,135,288,118,331,214,695,234,989,404,1050,378,991,820,568,1140,653,339,369,569,1341,832,395,812,811,452,234,386,841,967,37,27,578,432,943,763,1423,1406,1623,1682,1259,853,1204,864,924,626,662,291,447,277,542,108,820,577,679,264,568,417,318,53,373,194,21,470,242,104,220,88,563,379,982,340,621,233,629,205,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,914,745,719,1189,648,316,400,470,864,558,392,403,817,488,345,465,677,527,31,27,569,351,891,500,682,480,783,611,1119,698,1257,754,735,486,682,299,665,325,648,194,427,288,350,166,691,445,413,166,284,203,25,340,300,101,200,80,351,231,608,222,601,325,766,245,418,320,298,535,276,139,168,227,705,410,322,340,430,205,147,66,384,371,20,13,379,266,547,416,766,680,840,892,617,324,542,439,487,289,312,145,341,163,359,71,462,322,400,133,242,146,160,49,177,89,11,197,161,69,117,35,349,220,530,228,294,116,281,102,1354,948,1181,2087,998,452,991,1140,1542,961,984,1117,1572,698,661,794,981,847,53,44,784,455,2260,1789,1546,1237,1807,1935,2293,1193,2548,1873,1224,676,1085,563,827,352,1036,312,1192,608,998,494,1284,630,869,349,486,260,23,721,364,110,415,193,975,568,1395,648,1091,476,1008,435,1430,886,847,1249,739,391,697,747,1112,697,723,665,816,412,429,477,865,600,37,35,706,354,1660,1246,1389,928,1711,1173,1314,741,1547,1068,623,360,598,300,582,274,715,221,623,365,569,243,791,461,665,234,184,124,27,290,197,81,182,124,543,320,840,305,472,195,558,167,1559,1145,1081,1970,1234,600,735,938,1944,1258,866,943,1942,1182,701,1036,1158,957,59,61,901,511,1586,1014,1848,1457,1887,1530,2979,2019,3422,2210,1484,969,1219,578,1087,537,1122,365,1151,894,875,405,1857,1184,1115,455,481,305,45,747,352,147,343,160,940,665,1090,468,1502,790,1743,694,1804,1085,971,1913,977,460,555,861,1931,1239,885,1087,1205,688,445,546,1270,1303,79,58,793,577,1540,1045,2112,2019,2488,2246,1838,1088,2043,1447,1574,1073,1181,579,911,504,1041,255,1290,858,1155,395,804,401,495,110,540,244,46,739,342,137,265,108,1032,699,1382,546,913,396,817,311,1654,1168,1296,2101,1840,864,1498,1904,2120,1301,1241,1336,2449,1224,1054,1379,1397,1360,139,178,1072,769,2151,1865,1879,1511,2012,2768,3616,2118,4053,3131,1986,1130,1611,731,1427,670,1655,480,1801,919,1300,627,1898,977,1273,405,685,441,83,1189,644,215,750,385,1200,690,1914,920,1573,670,1370,557,2507,1574,1251,2027,1488,707,1157,1471,2650,1738,1248,1225,1693,919,763,899,1518,1384,61,59,1013,616,1852,1205,2837,2366,4292,4114,2583,1587,3197,2436,1444,857,1135,513,977,490,1170,269,1647,999,1211,535,1735,1059,1204,339,383,195,31,533,466,142,401,187,1030,731,2096,781,1108,567,1191,347,2321,1607,1557,2668,1751,895,1075,1398,2858,1919,1241,1246,2421,1446,870,1209,1659,1408,70,57,1042,634,1984,1213,1999,1508,2264,1830,4400,2711,4903,3132,2001,1238,1510,754,1477,728,1482,382,1360,1028,1024,497,2285,1369,1237,485,518,349,36,865,517,171,398,185,1053,691,1332,516,1754,811,1664,650,1649,885,724,1706,907,481,519,742,1886,1033,805,907,1068,567,349,455,1103,1159,56,26,747,462,1431,898,1898,1557,2100,2059,2295,1366,2356,1607,1530,960,985,507,838,438,881,223,1251,770,902,358,707,420,453,124,434,200,31,688,363,121,260,92,887,601,1104,456,718,348,670,240,1941,1190,1483,2440,1721,805,1417,1695,2728,1558,1486,1704,2301,1205,1043,1140,1371,1334,84,64,1073,681,2228,1694,2707,2242,3301,3721,4341,2619,5484,4083,1986,1054,1548,725,1097,517,1306,329,2215,1175,1607,752,2337,1202,1499,427,656,379,62,1145,600,217,646,230,1473,1001,2168,952,1747,790,1585,615,2380,1335,1190,1944,1380,658,1069,1332,2059,1275,1018,1045,1188,676,612,620,1392,1185,57,34,812,547,1691,1096,2380,1779,2966,2630,2297,1377,3131,2346,1380,742,1010,501,826,392,1065,208,1348,727,935,439,1422,861,1002,250,310,196,42,425,321,134,223,127,816,597,1405,489,747,412,889,262,1294,1065,1267,2164,1056,492,708,888,1329,870,555,687,1440,792,623,836,827,729,24,18,842,479,1671,992,1191,913,1240,1088,2011,1163,2111,1347,1679,1273,1393,706,1187,664,1284,398,1186,815,803,427,1550,881,939,298,320,185,30,525,572,114,243,126,573,388,833,343,1164,452,1202,353,770,598,638,916,526,229,345,477,1470,917,669,814,597,341,269,339,513,524,12,10,436,288,879,594,1646,1545,2338,2420,836,434,856,588,873,688,733,313,457,235,553,132,1085,795,811,338,476,243,291,43,198,115,13,302,236,98,240,85,873,569,1106,409,455,154,378,123,1334,807,959,1416,664,287,490,570,1460,756,661,922,980,446,515,586,611,535,34,36,493,279,890,755,1351,1147,1568,1553,1476,916,1528,1234,1185,785,968,508,587,351,739,235,1133,628,849,419,883,441,676,170,344,166,20,407,162,92,200,85,897,533,1128,511,648,381,868,336,824,512,582,983,300,134,187,312,594,380,405,345,461,224,316,343,409,298,10,6,289,134,451,383,579,422,748,663,603,314,613,467,677,400,538,274,298,166,330,104,433,242,340,161,330,223,297,106,116,70,4,222,56,8,6,7,238,99,209,119,287,147,312,123,737,673,785,1153,650,304,388,499,862,553,475,383,1008,528,469,543,579,568,12,13,619,305,1286,696,872,614,826,721,1332,721,1769,921,1045,740,951,429,1035,463,1076,302,673,418,558,272,905,525,644,201,161,137,13,356,317,87,140,85,366,213,451,174,706,278,676,224,456,345,303,481,221,98,188,219,663,392,414,404,328,170,165,187,315,279,9,3,250,157,556,382,897,713,1251,1018,530,229,595,399,460,324,444,160,306,127,363,89,500,353,490,181,229,128,166,30,93,59,5,164,109,43,118,41,389,233,457,185,216,75,182,45,1089,734,757,1208,486,219,436,450,1274,709,691,709,1061,503,559,648,610,511,19,12,390,218,809,609,1032,926,1336,1464,1612,816,1928,1375,855,536,720,376,609,286,780,206,1187,661,794,382,948,417,732,182,201,116,6,410,145,77,139,72,660,417,1058,365,813,326,827,272,437,289,290,466,160,76,176,185,310,192,224,185,294,111,196,161,237,182,3,2,132,57,314,179,312,218,407,331,349,186,464,323,277,155,254,100,202,92,227,66,185,113,173,87,187,119,190,42,47,24,5,92,39,9,7,15,103,75,159,80,124,88,171,74,1179,988,1098,1752,902,387,589,652,1233,835,603,559,1392,749,543,749,825,699,23,15,685,388,1298,716,1068,748,1160,864,1743,986,1992,1267,1247,898,1122,497,1043,549,1329,373,976,646,802,347,1371,846,920,300,371,262,17,478,332,100,250,103,571,396,829,303,1405,488,1179,354,589,530,455,691,454,208,300,332,1234,860,569,687,670,369,243,325,499,481,12,17,406,240,741,529,1325,1224,1702,1773,822,438,896,649,683,486,576,177,469,235,669,146,1101,707,789,307,494,247,320,54,223,122,11,311,173,57,165,57,663,442,919,312,520,158,452,114,1014,614,704,990,579,234,437,459,1132,718,653,722,989,458,542,655,564,420,35,28,458,254,676,600,1008,920,1268,1182,1353,873,1577,1202,848,552,672,306,569,305,643,214,872,559,760,318,821,432,755,212,285,161,16,340,114,54,137,75,622,370,834,325,726,420,879,295,598,343,405,579,282,117,279,274,475,310,420,292,356,173,223,300,327,214,15,7,232,102,310,253,524,397,619,549,584,319,624,461,369,230,303,165,238,155,286,132,308,172,268,141,307,188,269,124,83,52,17,140,62,21,37,57,208,162,293,177,227,130,329,131,992,897,1033,1824,1098,499,591,800,1391,940,637,676,1484,849,641,754,797,727,50,37,749,404,1594,847,973,829,1246,1187,1876,1100,2181,1390,1411,982,990,485,1010,442,1146,271,1148,719,799,342,2042,1151,1023,350,378,209,34,538,520,131,162,102,511,303,967,329,1581,402,1140,324,625,516,455,683,523,262,351,444,1368,848,560,736,601,325,239,297,546,557,20,11,424,281,895,562,1403,1168,1945,1691,790,456,847,543,744,536,537,187,355,164,482,94,939,567,582,271,618,332,332,57,306,129,11,244,332,116,169,59,598,343,911,284,507,138,345,98,1133,709,823,1197,548,251,381,500,1242,637,507,637,873,383,449,528,522,508,31,16,407,196,602,526,957,852,1194,1300,1217,748,1297,1019,886,515,651,324,513,216,550,162,889,491,659,295,1017,499,803,191,296,173,22,330,148,60,148,74,594,397,921,373,685,336,692,250,396,260,286,437,184,103,155,192,277,165,166,238,196,126,152,198,202,193,6,7,118,64,228,176,208,179,275,294,383,214,399,329,254,192,204,93,135,92,178,60,231,108,156,70,264,152,205,50,69,37,2,92,47,6,7,13,91,61,145,66,152,112,182,59,530,483,382,632,394,218,248,307,515,399,217,236,510,324,159,258,271,299,15,16,253,169,364,225,337,297,371,291,670,407,650,357,380,290,316,159,264,162,277,67,269,192,200,93,442,327,268,89,208,121,11,204,166,69,145,43,130,82,186,82,555,178,500,191,325,238,199,290,169,109,103,143,412,236,238,222,172,82,67,80,282,258,6,9,213,97,237,193,382,306,510,473,263,163,229,175,313,211,203,89,163,82,120,32,202,119,201,80,114,101,82,14,163,74,4,152,94,29,94,37,161,99,197,75,148,46,147,57,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,697,515,479,583,395,222,345,411,736,491,416,414,535,318,277,272,430,433,38,16,303,187,488,296,875,696,1181,855,1034,543,893,588,535,317,395,187,255,167,227,71,569,326,316,149,531,316,334,108,320,168,26,391,83,39,83,38,378,224,735,261,528,144,481,113,351,356,368,513,345,143,197,259,537,351,218,249,374,218,160,194,272,262,23,18,294,163,513,241,325,298,469,448,456,277,504,326,368,251,302,145,226,113,242,53,260,183,169,84,391,214,200,58,144,76,15,183,252,79,118,64,133,64,248,95,356,119,340,100,151,91,100,169,93,35,69,80,169,116,152,111,71,27,45,50,105,116,4,6,119,64,185,140,240,179,374,392,46,19,16,47,143,104,132,55,104,38,88,16,98,55,124,41,27,20,16,3,55,26,6,91,86,32,66,19,108,59,168,74,43,10,39,11,389,294,285,430,200,100,190,201,377,257,245,271,259,161,167,175,241,243,8,10,122,97,275,155,415,377,490,503,357,248,375,322,281,207,257,88,132,83,181,67,290,165,226,101,229,120,160,37,112,84,12,154,72,38,105,43,235,168,465,221,171,89,188,55,225,152,158,200,101,44,104,111,136,95,114,91,121,63,67,68,133,117,2,5,56,40,130,103,151,126,287,177,214,94,215,119,129,64,120,57,65,40,73,28,76,50,85,33,115,69,92,34,48,27,7,52,35,20,36,20,81,47,129,58,54,38,83,21,947,787,730,1069,576,311,349,418,921,625,487,334,863,497,394,468,651,491,33,32,415,248,842,419,774,691,906,763,1522,1039,1687,926,901,627,800,329,343,242,386,125,557,414,447,185,890,586,568,172,247,169,30,361,216,80,212,89,467,384,454,234,689,369,835,326,598,433,384,544,289,137,161,212,791,479,467,389,372,233,180,203,471,407,23,18,330,180,545,370,936,792,1050,950,625,359,416,430,786,515,576,254,296,163,221,62,549,372,483,196,260,195,223,26,185,109,26,256,135,61,129,50,505,349,493,226,268,159,322,114,1084,777,886,1358,684,349,543,675,1401,924,887,910,1111,616,486,607,843,736,41,24,573,426,1092,823,1466,1339,1913,1974,1952,1115,2063,1448,1038,601,810,379,643,332,758,193,1102,612,757,369,1234,650,744,214,382,220,30,521,297,111,364,163,673,469,1630,720,1016,451,897,319,619,386,425,557,375,213,301,419,447,295,412,310,404,247,241,260,391,280,20,23,277,144,500,338,604,448,1026,696,710,377,821,532,386,224,354,187,302,163,289,120,298,219,321,156,428,248,332,106,118,57,30,206,112,63,152,106,203,165,425,229,245,133,282,69,792,809,852,1229,861,407,462,572,1505,1060,553,690,1601,969,509,651,689,769,22,24,522,371,907,521,831,915,1326,1277,1679,1142,1694,1014,1107,741,786,327,591,238,551,136,858,676,485,239,1540,925,698,183,332,201,10,448,340,96,148,66,395,260,790,221,1500,421,1075,329,488,348,325,470,376,193,196,274,513,291,302,260,306,175,157,163,516,486,15,7,466,270,599,391,577,473,829,688,504,300,528,320,643,447,457,188,304,180,291,70,459,287,340,114,281,137,189,21,210,119,15,349,248,93,104,30,292,201,346,155,267,126,280,95,1444,1013,806,1077,642,301,481,602,1448,894,794,942,1026,551,534,564,798,727,17,11,446,281,682,469,1303,1252,1644,1653,1454,940,1552,1081,1168,658,793,354,481,223,494,116,1185,696,808,367,1047,557,691,158,417,229,8,539,216,90,200,62,639,476,1195,456,1017,481,1189,341,719,502,336,513,383,162,266,361,353,284,298,224,328,194,199,204,352,272,5,7,209,115,301,195,362,350,621,468,469,261,514,303,430,233,295,151,198,116,208,54,264,165,201,90,302,191,211,39,125,80,7,139,90,27,64,26,166,87,235,70,204,96,258,77
Mus musculus,10090,genomic,RefSeq,64447091,92967,51.88,55.89,42.84,56.91,12657,14942,8787,11598,15727,15629,9644,25273,14702,13556,7138,12412,19959,23308,14407,42599,13860,10624,506,378,11591,10225,12572,25041,14717,13743,19444,20348,41822,41104,49683,51702,20271,15267,13607,1894,19469,12771,16220,3038,11828,12740,13031,2303,31586,33442,27332,4926,8051,6050,538,7964,3367,3065,6369,5422,7731,8562,7478,5188,19283,26017,34383,26389,24102,41507,10417,19249,19791,32861,12398,62136,23858,41302,9520,29643,3955,7377,2367,14733,17848,27926,792,532,18240,24296,16973,57161,20520,31780,26762,40709,7894,10367,5995,14998,25446,33621,19427,5846,22281,20746,22319,7967,21230,31670,23844,9451,5549,9766,4561,2460,19731,23089,1792,20961,8460,15016,14729,18698,24322,35960,17657,15749,3979,8081,5230,6854,8579,4681,5084,5890,7627,5696,5079,12882,7258,5253,5836,9023,5231,4275,4226,8482,6708,4727,475,183,7128,6462,10828,20929,13968,8574,18667,18331,14325,10967,25309,18625,8720,6100,7216,1479,10985,6360,10204,1963,7491,5152,8860,1609,10573,8710,10817,1966,4196,2898,391,3748,1802,2188,3300,4239,7331,5510,8106,5677,5177,5351,8747,5020,12514,9028,6225,10291,12992,13861,8428,33340,10899,10034,6794,14735,10994,10975,8457,23947,8381,9250,445,436,9613,10400,13613,28079,16113,14045,24890,30129,31004,24832,39250,42967,14511,12783,11972,2800,19011,13573,16828,4661,11078,11698,12052,3496,25018,23432,19674,4910,7713,5994,673,7430,3275,4428,3837,6171,10052,10423,10687,9490,9962,14144,14271,11555,12937,15290,9325,14224,16884,19809,10502,36171,10821,10434,4787,9342,12227,14809,7898,22753,10790,8877,460,219,15407,14959,18961,45145,10013,9358,14592,15430,20028,18554,26297,24674,20861,17155,13322,3070,27148,18234,22139,5203,8870,10205,9027,2566,21069,19082,14965,3023,8753,7565,534,7290,7034,7357,14545,15109,8029,8588,6931,4690,13687,17952,19282,17047,26731,49465,9144,20394,16701,28802,9953,56859,26671,48734,8973,34952,3453,6910,2217,11367,20059,31075,542,475,16012,19631,17174,50602,22638,36150,25890,51792,6455,7122,4885,10725,27026,31055,19186,6789,21171,17427,20164,7722,22933,37108,25427,11782,5677,9176,4321,2063,19023,24455,1755,20051,7749,12087,13076,17458,24813,40868,15977,19811,4326,7751,4824,7594,6008,4303,2879,5076,6133,7507,3905,15223,6425,5033,3875,9167,4835,5517,3986,11678,3841,4522,314,363,6537,9335,12044,30621,11884,8831,12385,19811,15721,15153,26240,28947,5646,5690,4984,1200,10495,8805,8747,2171,7021,7787,8329,2508,11495,13574,10946,2676,4004,3466,583,4217,2331,4251,3896,6860,7446,8081,8088,7287,5736,10023,10330,8361,24972,25248,9770,24444,28120,50661,17380,112642,20906,26234,10886,39603,22056,32584,17756,74473,19538,26191,668,684,22817,39415,23985,119459,29310,37837,45799,94629,61781,78390,75267,144882,33030,40678,23126,9464,42079,50757,32145,13532,27026,39666,29773,13039,58734,78940,43416,17242,22635,23771,1779,24865,11091,26708,12039,30045,27780,46600,27240,36754,26220,58483,36100,34829,14822,13947,12384,16427,16421,17105,8248,24186,14332,11646,6169,10649,17508,21388,11727,32408,13436,11220,474,240,17620,15591,15464,33110,12166,11437,22736,18836,31938,32406,40944,41509,20879,14856,13696,1971,21602,16342,18929,3074,9925,9071,10773,2209,28336,28887,21776,4941,7819,6944,489,6779,5062,5865,8676,7187,6790,7787,6465,3742,13876,22193,23785,16779,23062,36193,10017,20874,19825,30108,11168,58744,29984,49124,11084,36319,5911,12105,3695,18304,18627,26568,437,506,17402,27253,17296,59608,25972,39617,35239,52046,11605,16789,11139,23712,23613,30502,18090,5293,25840,25411,25087,8256,25446,39143,29653,10821,9969,15726,7925,3607,18196,22002,968,17799,9733,17164,15277,18714,21837,33806,15186,14641,4926,10566,6123,8569,13547,8047,4464,5461,5516,4584,3628,9325,8623,5914,4879,9669,6298,5736,4782,9982,6337,5096,272,210,6653,5426,7564,13973,11420,9897,15695,17771,13920,15866,23864,20591,7765,6667,6934,1595,7892,5497,8708,1542,7978,6575,8834,1998,11592,11680,11181,2292,5088,3788,423,5236,1438,1275,2527,2660,5930,6223,6785,4846,5615,6632,9118,4993,22653,22111,8589,17270,17314,19854,10883,54593,18256,23508,8908,34095,16218,19976,11739,42263,15151,19866,529,478,13005,17716,15966,45898,26237,32874,34167,58331,39151,42601,51843,71291,23853,21160,17435,5436,23222,21561,21208,7921,19764,24283,21989,8389,35659,38595,28122,14316,12329,12429,1056,14623,4704,8873,5881,10846,16508,22962,18272,17889,14954,26843,20705,17406,11886,11999,9602,12991,14963,14607,7092,23747,10606,9551,5140,7728,14246,14381,9455,21233,10252,8951,308,218,12748,12202,12395,25775,9148,7829,13468,10260,17791,16266,23527,17451,18401,13313,11503,1780,21801,14219,16269,3369,9637,9026,8951,1669,18876,16478,12573,2842,6777,6374,366,6082,4330,5168,7934,6774,4713,5949,4886,3294,13244,15863,17613,12742,18713,31378,8352,15494,15975,25014,8867,41375,26097,44701,8685,28462,3330,6099,1995,8504,12910,19980,335,362,13329,18630,11053,35460,19872,27448,22472,34204,5194,4901,3645,5618,19951,25741,12086,4138,21542,19087,16481,5798,25071,39543,25088,7893,4351,7453,3197,1416,13394,16469,1262,12568,5774,9274,8814,11489,18279,29180,12438,11172,2919,5110,3294,4638,10203,6009,3951,5752,6179,5078,3604,11606,6841,4935,4397,6983,7090,6404,5547,11118,5702,5233,295,259,6065,6368,8504,19372,11159,8623,14723,15948,16157,15413,24270,22697,9207,7164,6437,1384,10481,9160,9998,2014,8311,7570,8528,2008,13747,15247,11841,2356,5103,3613,368,4001,1917,3103,3138,4156,4312,5019,5570,4161,4599,7419,8523,6012,27295,26045,8951,18255,17291,28096,12442,63453,20823,25878,9457,32047,22357,34432,18063,60375,15052,21156,485,641,12915,22879,13348,53535,25303,32372,36826,67062,49029,60640,54666,90754,29522,31607,17575,6236,29138,32320,23084,7413,26276,33739,28747,9409,47811,61798,33258,11785,18656,19490,1471,19528,6078,14847,6377,14887,14463,26143,15238,19181,17776,38313,22339,21229,13208,13858,6715,9433,8094,8841,4724,14892,10473,10878,4576,8003,12739,15916,8780,28157,8009,10360,316,221,7512,8286,8269,17728,10801,10937,16824,15384,26457,33214,41568,41767,11132,10140,8195,2063,9515,7922,10112,2149,7756,9359,9050,1893,17276,21659,18915,4226,4432,4216,274,4674,2752,3682,4606,4585,5438,7783,6054,4406,13154,21527,21341,17292,17718,26513,7004,14525,11875,20242,8242,43513,18343,32047,7503,25342,3718,6708,2692,15008,15062,21258,406,322,11620,19574,12544,39527,17443,27795,29313,38666,8330,11629,7847,16155,11975,17647,11706,5745,14117,12797,17297,5595,13587,21770,20961,9454,4743,8814,4925,2606,15349,17975,1487,16848,6068,13296,10092,12589,19218,30624,17068,15792,4245,9156,6103,6741,13,18,15,6,3,6,6,17,5,29,18,13,5,5,4,14,1,12,6,2,2,9,10,23,15,25,5,32,11,21,35,13,1,2,7,2,5,5,21,0,10,31,13,4,6,13,14,3,2,14,16,12,1,9,0,6,18,18,57,24,2,1,10,9,2,7,11,4,6,11,1,30,11,6,5,31,1,3,2,7,3,0,13,0,9,4,3,17,14,8,25,63,6,3,21,3,11,14,11,0,9,15,16,4,12,11,28,4,7,1,12,3,8,14,15,21,0,0,0,9,15,19,34,25,4,4,26,9,13304,12712,7186,11647,13121,14948,5875,21374,9231,9263,5193,8671,11820,15597,7725,25124,8478,9564,349,275,10179,13335,11110,26934,8230,8422,15022,13331,19694,22436,29495,31511,13348,12470,10526,3112,15377,11835,13865,4149,11565,7602,11025,2354,18383,20304,17103,4281,5482,5607,409,3935,3549,5071,5665,6996,6236,7751,5156,4101,12826,21295,18899,15665,16724,23981,7970,17196,14041,23106,8501,45462,17661,29918,9346,28095,4682,8787,2815,19004,13486,19336,454,387,15188,22530,11965,40281,15346,22860,23807,35031,6648,9102,8422,18835,13847,17294,13986,7353,19231,17870,19861,8643,18109,21649,23847,11448,6808,10732,6313,3749,16494,19220,1353,17129,6504,11571,9064,12558,22535,35169,18316,19062,4919,10475,6830,8743,7466,5953,3624,4734,11743,12241,6070,19807,11210,12535,8634,17161,13799,14561,10441,26631,7478,6983,410,223,10697,10789,17641,33295,16875,15486,18298,24622,30001,27170,46600,45419,6264,5747,6543,1470,12683,10838,12570,2769,11787,12212,14380,3534,23552,26824,23204,5323,8871,4816,398,5865,3252,3999,3592,5197,12103,15658,16620,14323,15173,22641,25318,16488,35707,37114,14231,23459,34499,54722,22443,105997,30013,45585,16977,53161,20913,28076,13061,56858,27055,33051,717,790,27285,40387,42266,139606,38419,48452,57752,95304,42485,57268,65524,107961,30822,30996,26012,8030,48763,47770,46918,15545,28886,38500,36782,13738,47578,60310,38450,14166,27267,25454,2001,28008,11749,22273,13728,26052,35891,51493,38584,42429,21121,40170,25423,20817,15917,14391,9683,13650,13740,14842,7615,20791,17631,16547,8269,15346,19798,26440,12756,38015,11043,12990,447,304,9948,11341,15411,23798,15591,16186,25676,21607,30627,40804,52764,50134,18313,14440,13918,2662,18471,13425,17098,3395,10961,11194,12804,3008,29706,35736,27091,5825,5818,5165,302,5616,3322,5489,5061,5522,9700,10440,7988,5023,19844,35161,37271,26640,23709,34541,10886,21533,19556,31274,11242,55892,27703,45748,12460,38578,5710,9446,3262,19684,18405,27871,807,469,16035,24152,20276,50374,23300,37833,36629,51398,8384,13709,11164,21809,20656,24658,18472,7160,26960,27089,25914,7935,21802,28579,28906,10953,8229,13562,7730,3645,19383,20746,1507,21508,6898,12378,9686,13897,26009,43925,23485,18862,5988,12892,9410,11015,21417,18598,13022,13511,22305,24973,13904,40183,26329,28137,17307,32818,22871,26370,18134,39000,19097,24338,1057,656,18221,20662,23992,40724,28536,28396,31805,53795,51072,47582,79064,68199,21797,20006,17750,3855,28047,25569,25478,5539,22916,26064,29438,7659,36643,49898,36475,6828,19120,15816,1126,14493,6467,9958,9761,11027,19256,22747,26540,20273,19784,32552,36694,21870,31631,34281,13550,21417,24962,38070,18266,84075,29968,47029,16205,52347,21206,28511,12332,52276,21803,31585,1002,793,21885,32505,32744,78747,37248,51320,91259,122979,48596,63120,77679,109489,30446,31631,27399,8563,39159,40143,40849,12332,28172,39358,36215,14615,41044,50950,34343,12574,21991,19744,1574,23184,8957,19738,14086,22110,26178,38553,34819,37194,18134,33908,22920,21705,22436,22176,12054,20060,19798,20126,8910,30975,23035,20407,10608,20003,29633,40972,18621,59675,17141,15390,417,339,11642,13423,15622,26446,16999,17081,29982,24141,60631,72445,81900,88393,26071,19162,15353,4385,25538,21079,20255,4963,13839,15056,16005,3646,48803,52061,32875,9407,8013,7220,356,7986,4919,6298,7504,8347,10673,12199,9508,6157,29381,49908,44893,39766,36684,48276,15418,31765,27248,43454,14939,80168,37329,55847,16049,50449,7185,13128,4000,23711,25722,33947,520,664,19522,29527,20685,58749,28741,43494,44968,67320,17035,23270,14083,33242,33819,36117,23219,12186,37038,38595,30899,11455,28448,38036,35515,16642,10499,16626,8190,5445,25821,26322,1682,29429,9611,16642,14123,19728,40341,58542,30564,28683,7510,18227,9834,12852,27290,23008,13726,16416,27195,25808,15841,48591,30815,35599,21511,40442,30274,31943,22010,49094,23665,19763,716,419,19719,21938,29402,48780,47653,42359,51637,72216,80636,74718,121807,124497,21349,18646,16095,4522,22955,21572,23480,5465,24579,25542,31906,7923,48420,57368,43312,10309,27156,15506,838,17401,7164,11030,10842,14350,27047,30068,32349,25928,26430,43342,43409,34160,35183,38241,14070,26935,30456,49425,23744,126154,36043,54299,16292,62363,21807,32523,15092,64891,23568,32094,625,622,23756,35475,33061,104692,42488,62040,86963,147784,60159,81202,101106,178565,33543,33498,24479,10365,43497,47749,43018,14949,32048,48516,40669,16754,51437,67551,38935,18474,26577,23325,1414,26555,11829,26283,16074,31601,34315,53565,37988,43030,21724,44770,24794,27730,13789,14881,9391,17524,15126,18887,9549,38052,8736,9843,5351,11230,18896,24770,12843,48228,7588,10731,487,398,13017,13535,13883,38523,9962,10513,16736,17539,32488,31903,41635,54466,29353,29080,26917,4392,32535,23097,37185,7650,12668,15357,16613,3311,33874,36139,30788,7539,7780,6752,494,8952,4519,5773,9112,11264,9781,11325,8229,5806,16783,26935,33403,26481,22990,35668,11453,24692,14784,24223,8793,48732,19723,38137,10048,35289,3530,6522,2610,16196,16748,24407,773,741,14017,19518,15041,50256,19041,29023,33058,46027,6148,9392,7459,15771,31111,41374,25781,10270,25017,18305,33134,12214,19975,30126,27344,11633,5123,7560,4404,2768,17900,20781,1652,22808,4799,11010,10024,15140,29118,46253,21029,23023,3825,7135,5243,7470,12597,8918,6269,9104,9065,10367,5951,22334,6530,4807,4862,9077,12640,13508,10732,26571,6229,5922,367,445,8299,9293,11109,25887,14433,10342,18814,20025,31768,32683,46226,50233,20978,17205,16425,3935,20112,17675,21122,5345,11466,9116,13895,2693,26535,31031,24310,6213,5107,4016,436,7294,2687,3433,3505,5785,13437,10773,12448,9753,13512,20058,25940,20673,3397,3309,1487,2858,2695,5702,1782,14203,1725,1682,1125,3462,3322,4799,2321,12415,1691,2574,108,66,1840,3193,2016,8646,2208,2755,3861,5929,8070,10197,10318,16709,5620,7795,4201,2335,6258,8436,6140,3024,2298,2636,2942,1286,7347,10353,5295,3837,2496,2071,140,3547,882,2194,717,1894,2499,3878,2966,3258,3424,8263,6387,7197,14521,19213,9908,19003,16554,20709,8658,40404,9619,10489,5244,12050,21994,28912,14570,53884,12299,16229,340,390,13807,17418,15700,46718,10121,10943,16127,17045,32706,36807,42555,65442,28265,29158,23938,5764,47664,35213,48080,13172,12220,15645,13696,3362,41369,45205,32279,9075,9671,8315,596,9327,5267,7653,10675,16288,8887,12114,6985,5863,25099,37598,40330,38083,20071,29796,7561,20251,11766,19757,6095,39162,20457,36391,7844,33446,3508,7196,2309,17567,18092,23565,459,624,11966,17485,14411,48059,21233,33187,35540,54755,7791,12183,8524,27503,22854,28335,20496,9681,27681,15390,36523,13951,22222,37504,28760,13112,7419,13848,6515,6005,14439,19389,1403,18037,5352,10594,9982,16801,29225,52600,17890,24307,4322,12118,8179,12136,15298,12322,6752,10608,12363,15491,7468,32981,10116,9149,6106,14869,18129,18502,12082,35291,10606,10978,311,376,11189,15578,13724,42373,18114,18104,19021,32379,37857,37607,53931,68413,22826,21854,19592,5179,41131,37251,42631,11920,16378,16627,19383,4349,37273,45751,34236,8328,7138,6861,685,8944,4004,7348,5796,10031,17387,18502,15180,14173,19831,33887,36725,29411,4976,5838,1677,3889,3758,8398,2233,17836,2613,3419,1289,5677,3729,5703,2289,13500,4177,5749,69,164,2841,5536,2723,14521,3478,3822,5119,9080,8028,10255,10016,19940,7173,9405,5448,3053,11771,15434,11163,9956,4129,5327,4164,1748,7820,13615,6407,4528,3838,4408,261,5286,1258,4459,1599,4395,4504,7285,4126,5706,5491,11610,7971,8864,13303,15026,8939,14840,12537,14639,8077,31914,9680,9688,4707,9546,17555,23951,13456,43794,6159,12428,448,251,10460,13878,11669,30071,7838,8300,13088,12961,22835,26512,34340,38335,20124,17084,16624,3758,23148,16852,26096,6100,10117,10372,12167,2769,27735,28158,23347,5801,7877,7386,380,7431,3452,5489,6848,9148,7225,7208,5455,4150,15447,22787,30482,20853,21219,36258,9249,21708,13072,23599,8244,49314,25798,48929,11311,38300,4813,9156,2711,19724,14698,25142,451,479,12125,19460,13975,44955,20470,35755,34011,55183,6375,10708,6814,17826,21679,27208,21949,7271,23003,17358,29073,9947,28963,43215,32975,13242,5303,10636,5890,3259,17965,22809,901,19467,4226,10239,7641,12955,23772,40279,15900,19013,3727,9001,6505,6979,17775,12217,8191,11143,11785,14134,8094,32149,11424,9948,7979,14763,16798,18333,12256,37202,8374,11537,425,358,13254,15710,12335,33866,15208,15916,21939,25492,36363,39544,49721,61376,21472,17211,17913,4240,21480,22739,25091,6297,16278,16944,16488,4395,31190,40521,29796,8452,8033,6498,524,10044,3285,5069,4116,6346,12949,14534,13898,11388,15319,24150,29766,20221,6096,7110,3100,4698,3843,7276,2892,19222,3366,4394,2028,6139,4371,7457,3169,16094,3299,5157,128,205,2614,5529,2528,11180,3275,4356,5132,8344,9335,11575,11539,21496,6298,6727,5934,2507,7504,8957,7842,3762,3668,4823,4566,1919,7889,12514,6728,4031,4429,5179,255,6404,1110,3153,1226,2733,3462,5152,3404,4248,4132,9219,6563,7584,18574,20885,10586,22085,18533,21995,9814,46641,13431,13264,5597,15008,24049,32907,16037,67589,10154,11195,316,247,11990,17061,14394,47586,10524,11007,16590,19620,35277,42723,46368,69761,25467,25113,18317,5090,27607,21691,24495,7446,13545,15402,15197,3608,56544,60739,41110,13631,9330,8904,431,8813,5058,8623,8796,13885,7989,9649,7017,5105,20958,35795,31135,32500,34247,51158,12710,34885,19785,31960,11165,75298,33268,59572,12091,55407,5094,11148,3108,23294,20256,27790,479,505,15749,24408,16869,75329,28278,44125,42596,82228,8322,15670,9359,32033,33310,42213,24301,13352,29172,23574,29103,13416,29168,49256,36732,15788,11332,23715,9750,7778,21553,26132,1464,26653,8159,17679,13043,25651,31636,53917,20582,29072,4457,13104,6280,10766,16007,10097,6678,10968,12283,12172,7306,32490,10233,9630,6817,16089,15949,16652,11785,34816,8424,7905,250,273,9997,13588,13651,35047,16711,15130,21130,28756,35452,36259,51852,72604,20044,19279,14379,4770,18834,18653,17788,5862,12179,11959,14845,4411,44630,52321,38554,12123,6283,5992,429,7773,3148,5421,4430,8221,12446,12265,14392,10597,16222,27378,25938,23988,4929,5957,2142,4131,4042,9753,2643,21326,3552,3554,1590,5613,3547,6076,2519,14348,3267,3921,35,53,2626,4807,2575,12997,2763,3409,3763,8541,7432,10068,8169,21481,5973,7392,4003,2208,6774,10422,5386,4732,2875,4859,3579,1900,10410,19142,8405,11378,2907,3783,187,4531,1191,5650,1577,5173,2804,5439,3450,4219,4432,12335,5978,8006,8409,8778,4757,7825,7642,9613,4119,16015,6531,8445,3926,7586,11747,16506,7640,29868,4562,6273,243,206,6726,9720,7712,17115,10837,11323,13754,13450,22956,32985,30132,36992,10185,11527,7986,1675,13249,13310,10330,2829,6967,9002,7382,1537,18173,24020,15681,4420,4357,4072,503,4334,2294,4225,3708,4258,7757,7446,4542,3764,17049,25634,20810,24788,15548,19814,5069,11146,11147,17346,5690,30643,12018,20468,5773,15955,2168,3586,1404,7861,9553,14242,396,469,10310,16162,10782,32021,13257,17226,20263,26305,3921,6561,4124,10283,13501,18807,10432,3798,14020,14311,13966,5709,10185,14736,13918,5086,3284,6080,2479,2027,13302,17213,1040,12817,4444,10333,6239,10212,16016,24643,12412,12810,2826,7308,3306,5909,12,31,5,32,11,29,50,56,16,14,17,76,14,4,5,18,3,8,12,3,22,9,32,28,15,18,68,73,4,25,28,38,36,9,20,13,20,50,42,11,34,40,28,21,7,26,50,10,16,26,17,27,14,4,10,9,26,62,86,47,20,32,50,36,13186,13143,3810,6949,11091,13276,6949,29556,11434,15288,5984,18242,7431,10431,6214,17553,7944,11752,278,450,7962,10823,8636,23610,15896,17383,20142,29540,18686,21400,23429,26800,9387,9681,8109,2256,9872,9541,10099,2762,10959,12948,14236,4820,13227,16687,12997,3632,7196,6933,784,10601,3069,5268,4464,5903,10689,15435,12359,13157,8549,14140,11301,6509,4970,6228,2146,4626,4740,5955,2745,10973,2689,3613,1065,2744,5206,7667,3381,14870,3276,4007,66,75,3277,4483,2931,9339,2413,2591,4084,4156,6813,9037,8736,14001,6307,6503,4026,1149,5862,5100,5138,1456,2231,3537,2399,480,7710,10717,6282,2281,2740,2903,96,2938,2109,3821,2557,3923,2315,3899,2219,2808,6267,11125,7033,7818,11175,21413,3305,7410,7875,16393,5664,31716,7218,18552,2507,13846,1090,3720,753,7396,10175,15873,143,218,7431,12415,6338,24297,5934,9992,9728,21909,2370,4100,1793,8027,10853,17024,8454,4922,7724,7667,7839,3362,5847,11437,9519,4793,2625,6548,2246,3330,11585,14764,456,14060,4814,11783,4537,10012,8527,19487,8479,13547,1648,5843,1997,4190,5550,5513,2547,3537,4928,6438,3527,10639,6735,7688,3510,8193,7126,8703,5118,15181,3683,5122,112,88,4532,6164,5408,12490,6896,7214,9165,12404,13681,15857,18573,25527,4998,4831,3631,1302,6444,6586,5385,1585,4572,5548,6724,1407,10780,15102,10017,3440,3389,3899,281,4252,1996,3637,2602,4244,7567,10733,9014,9164,7294,13644,12039,10287,6547,8343,3268,5521,7873,15659,6245,29428,7711,12515,4470,12589,4908,9537,4752,15042,4044,7726,129,114,6858,11940,7588,30323,8818,13445,17008,28757,13610,20897,21000,38534,6141,9111,5999,1585,13144,17112,13108,5673,7186,10825,10276,3638,13007,19766,11877,5132,4371,4565,307,5514,4511,11443,5015,12788,8319,15426,11051,15928,7586,16257,8652,5873,11728,12657,9157,12611,12423,13410,5700,21065,10371,10184,4877,9830,15428,20389,9516,32459,6877,11475,341,452,9985,13225,11361,25201,10951,13220,17826,13897,34106,45896,40928,49644,20193,15874,14450,2680,20910,17427,15957,3633,10208,10992,10925,2454,27341,33481,20404,6323,5842,4640,333,5320,3827,6318,5360,6803,10416,12910,6533,4977,19865,30934,25956,26617,21623,30387,8543,19231,20291,31490,9879,57447,21546,42150,8845,32197,4386,8838,2348,14880,15005,23403,602,611,17455,27672,19381,57686,23994,34888,36702,51946,10433,15861,9054,24539,29398,35786,22688,7832,33011,36227,29518,10623,23338,35359,29815,11755,8548,15821,6559,4670,19000,22712,1412,19626,7539,17494,11405,18690,38623,73249,21670,22461,5808,15024,6378,10742,11186,8834,5523,7227,10898,11558,6616,19847,16731,12614,9317,15226,11905,13207,7475,18098,7394,11304,558,419,10956,12675,12929,25007,20723,19655,27586,26645,25840,25763,37835,38659,10388,9024,9248,1854,14795,12455,14566,2957,14130,12277,16253,3901,18374,22419,18465,5058,6702,5932,864,7505,3136,4825,5291,6884,15861,18247,22569,15320,9954,17712,19205,13014,11425,11291,5196,8414,10804,14797,7485,31688,12273,16644,8015,20161,6470,10643,4407,14478,5998,8796,371,317,9613,11998,11224,32423,15776,23291,34012,46442,16012,22513,22534,32069,10544,10969,10692,2890,16263,15350,15680,5343,14836,16556,16355,5363,13628,15711,12767,4141,6116,6707,667,7608,3983,8073,5711,10062,12644,18571,18748,20539,7003,13406,8684,6274,10836,11463,5402,9941,10289,12381,4494,18263,7511,8318,3541,6732,14483,17757,8335,30173,8751,9586,139,159,8316,11052,8544,18836,5578,7557,13476,5177,21537,28236,24937,26099,15453,13945,8452,1831,19051,15376,12254,3047,8055,11309,8694,1696,23175,25665,15596,4246,5307,4409,204,5206,3980,5702,4961,5605,6016,8136,4478,2229,19323,32471,20971,18902,26332,41477,9766,20139,19674,31526,9419,50877,21143,39191,8106,32592,4595,9019,2432,16199,21517,32710,209,351,17431,26314,14820,48190,17587,28939,29077,47865,7644,10787,6772,21580,31106,41057,20947,8302,26736,26180,21224,8468,20887,32655,22609,8472,7615,13541,5227,5878,21174,26238,778,27299,9074,20226,11653,18632,29522,50534,16951,18001,6474,21346,6969,10443,17422,13433,6690,9629,13219,14380,7318,21723,16370,15846,9044,19719,14428,16969,8989,22283,9529,8930,191,196,11426,14909,15316,32384,24149,23589,29173,31790,33275,40859,47798,59273,13156,13656,10216,3089,19355,19129,17910,4354,15549,17448,20067,5186,26111,32733,23755,6559,6192,6126,305,8509,3843,6105,5998,7920,19193,24237,20153,13609,18417,31350,30748,20552,10451,9182,4810,7958,11315,18531,6921,36477,12523,16088,5844,20680,9493,15534,5344,19416,5649,8669,139,184,8705,11378,10265,34357,15894,23561,35229,47908,21388,35899,27575,46195,14092,14094,10487,3252,21598,22225,18665,7412,15624,21903,19265,5954,22228,26344,16552,7154,4904,4736,262,6106,4438,9269,5347,9441,11177,21706,13121,12546,12072,26135,13014,5586
Cricetulus griseus,10029,genomic,RefSeq,51382250,82201,50.86,55.58,42.18,54.83,11818,13237,8434,10681,13970,13258,7317,22047,13112,10430,6504,10629,17810,19326,12038,35934,12650,9059,634,324,10004,8150,10741,20991,13025,10607,16766,16827,37241,32994,43127,42777,18017,13423,12614,1544,17306,10734,14183,1915,10552,10014,10995,1486,28512,26943,23338,3260,7891,5201,531,6681,2999,2580,5340,4408,7208,7171,6046,4127,18033,21631,29246,22089,21439,32746,8666,16876,17114,26911,10262,50864,21829,32360,7882,24753,2558,5540,1823,10633,15500,22153,590,452,15367,18704,14804,45150,16838,24659,21898,32873,5589,6936,3800,9337,21586,25490,15743,3873,18458,16420,18681,5013,19042,25049,20148,5271,3978,6824,3161,1642,17739,18217,1472,16878,6579,11301,11787,14192,20601,28942,14090,13183,2846,6125,3214,4995,8202,4263,4488,5318,7306,4785,4631,10650,7111,4233,5098,7891,4821,3086,4342,7065,5818,3535,329,240,7114,5392,9574,17111,12455,6733,15724,15177,12488,7891,22119,15274,7748,4988,6488,940,9183,4866,8324,1298,6718,4333,7575,1383,8610,7164,9346,1363,3783,2312,354,3284,1819,1576,3363,3444,6413,4388,6656,4423,4327,3883,7559,4026,10876,7622,5207,9823,12255,11072,7157,28482,10200,8378,5703,12803,10190,9145,7193,21056,7773,7083,542,339,8772,8927,11866,24395,14216,11861,22771,25565,27339,21151,34384,35749,12928,10681,10654,1908,15170,11304,14820,3106,10605,9550,11935,2567,21589,18856,17637,3456,7001,4762,729,6658,2542,3554,3119,4645,9214,8552,9632,8220,9533,12267,13021,10053,12005,13662,7943,13804,14946,17288,9741,30281,10758,8883,4290,8657,11448,12250,7446,20328,9361,7044,415,314,14233,11700,17253,38669,9395,7408,13121,12351,17535,14735,22790,20825,18948,13334,11914,2251,22168,14743,18065,3129,8597,8511,8221,1320,18789,15755,13750,1920,8418,6194,613,6854,7452,5817,14083,13677,6759,6821,6039,4189,13074,14818,17834,13935,22782,39160,7502,17512,13972,22341,8342,44788,23783,39670,7703,26935,2607,4571,1507,7521,16292,23376,499,422,13148,14808,12729,38327,19831,28010,21461,40227,3990,4407,3219,6570,19841,24417,15033,4366,16727,13055,16020,5210,20715,27670,20590,6967,3716,5684,2666,1076,15491,18587,1434,15757,5894,8496,10663,12254,20507,32151,12391,15218,2429,4853,3128,4280,5744,3990,2448,4767,5690,6524,3757,13399,5742,4393,3421,7792,4838,4499,3943,10463,3812,3901,315,270,6550,6858,9702,24966,9266,7497,11652,17117,13045,12800,23445,23239,5039,4569,4029,926,8776,7396,7455,1549,6195,5706,6791,1620,9364,11017,9062,1584,3624,3250,518,4258,2095,3635,3362,5392,5809,6349,6859,5866,5254,8424,8711,6215,21550,20187,8000,20766,23911,40222,15609,88182,17941,19992,8911,31961,17753,25427,14925,60551,16592,19927,633,718,19548,28698,21656,90260,24540,29399,38456,72324,50528,57777,59723,110655,26772,31155,19692,6002,34538,38768,25473,8688,23302,29874,24413,8041,49077,60830,36169,11806,18655,18086,1544,20546,8022,19365,8523,20597,22964,34305,20677,27615,21893,45513,28440,27537,13279,13236,11026,14570,15243,13326,6919,21682,12737,9794,6054,9226,16143,17933,10877,29194,11649,9497,501,280,14316,12227,13079,27042,10686,9469,19872,15676,29839,27045,37361,34661,17291,12223,12423,1563,19940,12341,17378,2083,8562,7096,9115,1080,25665,24261,20351,3186,7263,6006,436,6469,4519,4349,7664,5732,5888,5972,5516,3261,13720,18528,20069,14338,19145,29352,7511,16492,16217,24196,9808,45354,24845,38203,8356,28505,3728,8414,2614,13123,14926,21954,433,478,15624,20849,13572,47194,21605,28083,27506,39619,7942,10897,6907,15164,18656,24072,14583,3557,20417,19182,19475,4974,20709,29719,23655,5477,6196,10772,4941,1766,15109,17580,947,14306,7334,11957,12265,13336,18182,25681,12895,11541,3375,6550,3787,5489,11943,6284,4013,4329,4826,3589,3352,8192,7461,4788,4397,8025,5796,4755,4162,8393,5610,3768,315,128,5956,4933,6505,11816,10240,7771,14216,14151,13126,11264,19859,16048,7195,5248,5798,1182,6492,4649,7210,958,7050,5224,7435,1156,9350,8454,10137,1359,4589,2965,309,4393,1270,1290,2071,1994,5338,5070,5693,4117,4497,5146,7683,3979,18742,16970,7052,14502,14384,15262,9787,41910,16423,18314,7757,27742,13688,14830,10174,32997,13812,16467,604,414,11709,14062,13622,36117,22475,24190,29130,45868,33343,32676,42334,57671,19291,16736,14436,3567,19827,17667,17979,4920,16857,18863,18018,4993,29922,32323,26071,10227,10482,9748,1024,11877,4498,6507,4435,8005,13631,17358,14826,15297,12917,20427,17892,14364,10407,11027,8380,11796,13414,11291,6042,19293,9692,7317,4139,6946,11970,11099,8495,18178,9376,7341,345,180,10949,10062,10785,21421,8030,5977,11513,8535,16487,13437,20310,15283,16013,12087,10116,1436,18224,11146,13869,1968,8166,6836,7857,1064,16847,13429,11549,1638,6571,5162,450,5461,3817,4004,7664,6053,4750,4940,3858,2904,11429,12715,16015,11001,15193,25709,6128,12445,13679,18820,7087,32047,21640,34939,7475,22734,2061,3979,1393,5239,10736,14916,282,351,11010,12973,8633,27524,16037,20847,17332,27064,2839,2826,2344,3872,15658,19226,10193,2537,16499,14664,13122,3938,19974,27896,18029,4615,2980,4423,1996,829,11135,13055,921,9918,4435,6163,7238,7788,14799,20675,9456,9171,1844,3232,1858,3299,9356,5118,3656,5223,5388,4701,3358,9835,6237,4225,4113,6762,6006,5106,4813,9600,5676,4315,184,215,5997,5867,7898,15826,9526,6355,12824,13807,14605,12658,21091,18457,7887,5762,5704,748,8898,7131,8422,1173,7244,5879,8227,1474,12399,12226,10515,1487,4620,3189,444,4001,1784,2808,2675,3594,3408,4252,4860,3463,3886,5881,7703,4846,22714,20883,7382,15578,15355,21316,10179,52577,18287,19381,8192,26390,19842,26035,15553,49899,13073,15860,580,544,10767,16326,11082,40959,21685,24276,31979,52130,41912,46996,45043,68538,24831,23974,14914,4091,23483,25108,18648,5119,21871,25321,24076,5657,38991,47267,26896,7339,15502,15004,1270,15527,4933,11195,5097,11072,11622,19192,12197,14084,15064,29503,18632,17810,12062,11325,6179,8478,7545,7775,4295,12332,8726,8729,3868,7646,11377,13608,8370,25097,7885,9423,346,138,6474,6823,6683,14739,9165,8295,12900,12617,23937,27263,35519,34291,10141,8840,7558,1298,8305,6028,9021,1332,7028,7708,7572,1273,15796,19569,17076,2743,4304,4380,331,4093,2141,2943,4121,3921,4994,5873,5663,3552,11930,18773,19151,14804,14721,20968,5655,13065,10397,16173,6788,34231,15307,23416,6292,21092,2580,4260,1741,9518,12893,16464,378,263,10880,14885,11220,30584,15669,20035,21401,27366,5438,6463,5165,9994,9708,12858,9502,3570,11694,10518,13917,3571,11145,15908,17859,5742,2958,5209,3019,1526,13211,13150,1132,13602,5301,9729,7911,9228,16313,22601,13541,11733,2608,5412,3251,4408,17,35,36,19,18,22,16,26,25,27,20,42,19,21,16,29,15,18,26,14,25,28,40,41,41,41,66,58,20,20,80,39,19,15,29,3,18,25,34,15,42,36,39,14,26,35,36,15,25,29,66,42,8,5,7,8,34,45,100,61,13,21,44,19,20,19,13,17,25,38,17,51,17,30,28,69,10,16,5,35,13,19,27,19,31,29,45,39,24,27,65,82,10,17,44,24,12,23,22,6,30,28,65,12,30,18,57,11,15,13,18,7,25,28,87,47,5,5,7,6,32,29,69,49,11,11,18,21,12175,10641,6583,10978,11768,11107,5250,17232,8756,7833,3926,7523,11614,14060,7986,23220,8019,7800,349,250,9647,10100,10003,23954,7106,6420,13502,9785,17055,19081,27279,27353,12840,9845,10612,2029,13255,10200,11983,2728,10269,6325,8182,1510,16755,18499,14566,3111,5564,4507,292,4194,3377,3998,5287,5242,6231,6495,4436,3868,11848,18179,17263,14147,14174,19318,6230,14047,11935,18235,6806,36338,14480,22415,7191,22515,2920,4743,1882,11428,10863,14098,363,350,12280,15089,11040,33113,13610,17123,18654,27890,4685,5584,5182,10820,11019,12803,11144,4379,15666,13865,15269,5232,16927,16262,20023,7454,3699,6288,3746,1828,12626,14746,1193,13878,5116,8714,7130,10304,19224,25293,14153,14507,3206,5445,3520,5123,6651,5637,3943,4795,10885,10011,6237,16959,10226,9678,7793,14347,12606,11980,8922,21562,6783,5849,375,190,9558,8407,14950,29060,14585,12430,16422,20710,26144,21330,41013,37425,5709,4769,5392,1039,10317,8729,10648,1919,10018,9507,12538,2083,19654,20874,19800,3258,6157,3959,489,4811,2172,3241,3219,4101,10650,12312,14917,11317,12240,17567,20471,13141,28489,28257,12119,21004,30502,40156,18761,82851,26383,33444,13881,41284,17502,20676,11055,43502,22562,24440,629,711,24715,30717,35661,104669,32748,36010,48436,75915,35562,43113,55408,81608,24900,21982,20946,5314,38211,36140,36941,9702,23900,27946,30990,8592,36988,46067,32169,8953,23052,18747,1888,22378,9562,16898,10196,19481,27249,36651,30586,34016,18425,31173,20524,16478,14304,11822,8917,12615,12478,12026,7182,17598,15934,13600,7375,13505,17357,20914,12554,33032,9863,10397,486,286,9491,9331,11971,20638,14275,12437,22441,17677,28261,33011,48912,41909,16184,12671,12511,2009,15580,11251,14779,2159,10203,9557,11988,1817,25908,29868,24014,3493,6016,4548,305,5272,3141,3794,4580,4501,9343,9177,6996,5012,17323,27921,30085,21963,19761,26150,8472,18525,16824,23880,9259,41897,22830,34264,9902,29866,3388,6004,2163,11752,14795,19341,657,424,13088,17822,16290,40307,19805,28186,31062,40211,5950,7713,6954,12809,16489,18437,14888,4041,22631,20343,20784,5284,18642,21378,23697,6899,4676,7413,4346,1955,15045,15614,1379,17065,5576,9847,8090,10072,22222,31001,18316,14364,3394,6882,5065,6616,18510,15070,12503,13156,20801,19652,12530,33924,23740,22345,15870,28185,20824,20698,15506,32907,16395,18961,1100,689,15433,16612,21188,34622,26300,22245,28535,44438,41928,35768,70307,53943,19195,16098,15719,2926,22201,19581,23502,3515,20498,20144,26153,4773,30802,36872,30015,4735,15972,10822,1072,12268,5432,7568,8277,8881,16727,17444,22748,17258,17431,25023,31577,17823,25536,27723,11322,18831,21597,27221,15112,62531,25871,34248,13594,41812,17432,21142,10610,40947,18693,23460,1116,738,20051,23577,25684,59801,32541,38619,74523,95818,39804,46919,64827,81035,23401,23921,22947,4837,31721,30847,33222,7714,23975,28870,30871,8468,32837,39118,28433,7890,17656,16024,1664,17232,7848,14314,9709,14842,22482,28415,27422,28977,16018,24990,18251,16962,21082,17981,10458,18636,17247,15833,7424,24479,20300,15807,9361,16265,26679,31437,16949,53108,15088,11758,334,341,10710,11102,12866,21587,14863,13042,24053,19208,55651,57612,71410,74622,22178,16064,14082,3069,20282,15783,16909,3117,12368,12161,13205,2253,40987,43769,29737,5731,7735,5600,365,7461,4566,4655,6472,6191,9942,10314,8116,5305,25547,39317,36856,31667,29904,37902,12106,26113,22660,33582,11877,60367,31575,43887,13041,38865,4632,6933,2749,15266,20510,24039,581,500,16399,21896,17284,46644,24007,32654,37079,51000,10438,13759,8946,18880,26077,26684,19837,7569,29960,28761,25147,7045,24125,28470,30749,9271,6253,9691,4689,3203,20932,19723,1664,23475,7675,12330,11097,14825,32679,41842,23558,21500,4747,10058,5307,7301,25842,18335,13776,17001,23950,22066,13809,41014,29111,26475,18223,36215,25904,23687,19463,39269,19759,15113,569,400,18144,16970,25896,41847,43545,35758,48602,60327,67923,57111,104663,96796,18932,14605,14108,3074,18466,15503,20746,3519,22644,20525,27526,5444,41544,42972,37208,6063,23212,12634,864,14925,6216,8049,9334,11326,23535,23598,27318,20509,23365,32303,37289,27667,28685,29749,10836,20591,26305,36921,19280,93177,28627,38919,13133,48674,17255,24507,12561,51919,19298,22556,633,617,20065,25850,26566,77216,36120,44147,70567,109165,48689,59304,81580,133381,26155,24724,19506,5848,32927,35948,32415,9419,25736,34505,32204,10146,41061,52028,33441,11003,22770,17092,1391,20231,10800,18902,12344,22451,26766,38231,29680,30724,17866,33714,20298,20140,12298,12226,8948,15661,13816,13938,7820,29322,8408,7542,4680,9583,17267,19626,11511,40733,6978,8709,600,401,11327,10159,12029,31179,8760,8142,14097,13874,27962,25380,36479,43508,24276,21996,22596,3521,25648,16409,28898,4588,11920,11719,13014,2154,28592,26803,25300,4583,7016,5440,593,7521,3679,3823,7795,8678,9001,8717,7112,4988,15018,20522,27351,22347,20155,27735,9051,20085,12356,17530,6899,38292,17093,29477,7744,27704,2667,4002,1650,9426,15362,18601,714,649,11953,14997,12240,39142,15909,21068,25804,36584,4141,5744,4741,9783,24388,29865,21179,6355,18928,12968,25682,6816,16058,22707,21920,6687,3044,4825,2855,1439,13956,15905,1474,17975,4618,7654,8262,10942,24186,33386,15977,17485,2341,4707,3396,4879,11941,7548,5680,8541,8256,8355,5099,19731,5271,4028,4181,8046,11225,11240,8622,22248,5954,5219,355,529,7996,8041,9994,21191,12369,8495,15841,17109,28030,24453,37586,39555,18563,14486,14642,3299,16434,13478,17755,3272,9869,7043,12001,1875,22766,24642,21246,3837,4904,3831,525,5907,2429,2509,2974,4137,11364,8881,10189,8240,10989,16355,21207,16778,2014,1883,1001,2194,1777,3723,1149,8561,1346,1097,751,2419,2182,2702,1831,8678,1543,1503,78,78,1253,2142,1195,5103,1561,1547,2582,3917,6155,6077,6129,10365,3557,4284,2804,1517,3856,4747,3595,1737,1405,1817,1821,677,4723,6672,3748,2068,1487,1509,137,2497,421,1247,321,1125,2121,2492,1901,2295,3023,5597,4644,5131,13087,15862,8303,16305,13992,15787,7370,31069,8358,8106,4258,9855,19326,23037,12495,44494,10418,11920,370,326,12566,12847,12836,35069,8670,8641,13933,14276,28804,28119,37685,54459,23814,22026,19345,3976,35923,24440,37017,7479,11208,11788,11576,2136,33206,34537,26030,5768,7690,6576,607,7724,4504,5276,9078,11538,8230,9170,5643,4646,20857,31030,32504,29591,16460,23228,5969,16132,9635,14911,5179,31927,16180,26782,6203,27924,2251,4185,1319,10525,14932,17983,390,468,10464,13524,11927,37969,17849,25269,28466,42838,5136,7977,6115,17333,18736,19856,17282,6083,21084,11266,27527,8618,17749,27240,23863,7858,4193,8296,3818,3659,12031,14938,1199,14997,4646,7406,7987,12605,22993,37708,14584,19114,3175,8138,5000,8100,13637,10414,6168,10008,10935,12527,6219,26007,8520,6963,5045,12169,14893,15079,10413,28513,9865,8711,189,339,9693,11865,11607,34395,16236,13254,15998,25992,32602,29259,44221,52987,19489,17928,16128,3641,32071,28069,32826,7879,12726,12461,16224,2972,31060,34471,28011,5255,6266,5721,586,8065,3510,4905,4993,7498,13788,14314,12207,11211,16792,27029,28571,23989,3517,3145,985,2539,2150,5051,1577,10629,1793,2182,822,3290,2500,3160,1708,8692,2986,3246,41,73,2025,3298,1848,8694,2383,2541,3273,6228,5426,6389,7150,12876,4164,4771,3340,1596,7320,8381,7273,5181,2296,3108,2542,1099,5214,7796,3762,2793,2468,2636,311,3016,754,3035,917,2807,2780,3920,2257,3749,3722,7127,5222,5924,11240,13456,7878,13637,11472,11394,7305,25333,8819,7727,4193,8079,15635,19976,10908,37933,5552,10215,283,287,9740,10910,10302,24743,7564,6554,10933,10820,20798,21832,30135,33382,16636,13455,14424,2557,18695,13038,20548,3316,8602,8798,11003,1822,21721,23208,21599,3927,6721,5985,373,6375,3082,4123,6110,6984,5317,6371,4737,3453,13457,18891,27180,18250,17974,29089,7172,17200,11322,17483,6806,39059,21126,37952,8367,29849,2813,5391,1882,12867,12927,18621,327,392,10930,14312,10848,34565,17583,25872,27124,42414,4341,6860,4970,11981,17348,19942,16872,4960,17393,13626,22015,5439,19028,28985,24741,7295,3719,6969,3229,1989,14466,17489,769,14853,3762,6665,6154,9322,18707,29558,13083,13689,2462,5885,3756,4934,15574,11492,7281,10850,10581,11432,7610,27779,10207,7835,6601,12436,15518,15081,10877,31415,7707,9737,401,373,10662,12449,11433,28902,14497,11634,18778,20545,30612,30214,43363,47149,17263,13775,15501,3217,18963,17334,20342,4165,11681,10066,14301,2545,26162,32112,26582,5277,7391,6100,584,8926,2575,3994,3496,5405,11290,11218,11134,9249,13903,20580,23723,16928,3948,3961,1588,2841,2386,4965,1838,11418,2349,2289,1364,4158,3063,4027,2008,10155,2170,2726,88,98,1862,3311,1839,6410,1967,2418,3525,5437,6358,6307,7445,11536,3465,3785,3213,1352,4705,5493,4386,2048,2226,2778,3042,1019,4902,6974,3982,2023,2823,2643,205,3806,535,1894,510,1656,1946,2884,2163,2775,3218,5980,4328,4370,16680,17572,9332,19782,15865,16076,8356,34743,11298,10272,4703,13311,23071,26692,14022,56832,9786,8551,303,199,11397,12447,11821,34233,9581,7927,13361,14680,29495,33392,38539,57279,20735,19977,16363,3896,22216,16680,20455,4508,12008,11767,13328,2359,45450,48488,35417,8291,8620,7137,439,7379,4372,5602,7646,9599,7222,7097,5672,4258,18710,28312,26136,25096,27621,40784,10731,28088,17625,25087,9664,60337,28432,46096,10031,43871,3722,6499,2159,15011,17592,21247,460,480,13762,19076,14621,57158,22914,32045,33628,60853,5851,9148,6619,19605,26111,30623,20386,7846,22087,17858,22724,8031,25182,36167,30996,9499,7601,14155,5629,5004,17841,20112,1252,21147,6545,12689,10287,18262,24765,39375,16610,21973,3145,8281,4247,7213,15121,9787,6423,11208,11453,11554,6575,27242,9760,7787,6054,13003,14846,13193,10337,29644,8184,6806,276,272,8998,11242,10964,30207,14598,11391,19122,23973,29553,27520,42928,57676,16738,14639,12643,2943,15946,14602,15821,3704,10922,9714,13459,2402,37241,40178,32789,7069,6261,5148,503,6997,2758,3991,4241,6334,10438,9652,10801,8575,13607,20954,20844,18617,3346,2829,1220,2623,2700,6260,1955,14358,1992,1997,1094,3529,2255,3541,1565,9917,1740,2030,35,57,1703,3367,1473,7648,1516,1726,2526,4617,4844,6272,5523,12890,3306,4395,2308,1257,3940,6849,3453,2661,1981,2805,2331,1080,6878,11306,5347,7422,2115,2058,205,2593,843,3900,848,3510,1700,2799,1827,2559,3008,7796,3804,5396,7964,7545,4543,7656,7048,7194,3525,13063,6044,7047,3250,6731,10592,13488,7251,24943,3932,5444,213,364,5806,7343,6380,14294,8994,8367,12128,11218,20442,26184,25858,29965,9258,8712,7058,1268,11158,9783,9324,1541,6265,7283,6539,1079,16083,19457,13711,2899,3673,3473,354,3630,2137,3171,3560,3540,5612,6215,3932,3405,14333,21203,19311,22141,11272,15489,4230,9150,10124,13454,4558,24608,10445,15042,4761,13482,1282,2254,751,4914,8115,11145,513,329,8751,11865,8951,26073,10992,13419,16456,21099,2745,3775,2497,6018,11101,14234,8510,2365,10852,11077,11600,3435,8409,11575,11393,3169,1978,3838,1724,1347,12253,14778,1237,10751,3597,8048,5835,7585,13156,17964,9743,9560,1841,5076,2085,3971,58,66,42,60,72,65,57,99,63,63,60,123,44,53,35,81,46,43,78,48,91,78,116,153,94,86,167,117,59,86,129,85,57,64,77,23,102,100,117,43,92,90,129,41,79,105,138,37,81,92,207,141,19,29,29,25,106,152,350,188,70,95,223,90,10463,10210,3531,5889,9274,10920,6480,23469,10144,11762,4855,14318,6473,8136,5270,13990,7125,9202,246,405,7108,8116,7002,18764,13760,13638,17868,23625,16208,16712,19480,21250,7473,7544,6652,1380,8366,7523,8532,2103,8990,10139,11860,2814,11200,13619,10381,2500,6191,5919,666,8880,2842,4021,3197,4786,9059,11493,10545,10017,7432,11438,9966,5158,4327,5589,2053,4173,3949,5255,2240,8795,2537,3012,892,2426,4148,6216,3316,12429,3342,3616,107,86,3118,3836,2440,7240,1967,2041,3605,3429,6541,7570,6745,11093,5847,5200,3411,797,4696,4312,4387,844,2180,3081,2261,339,6412,8706,5600,1370,2495,2629,140,2647,1820,2866,2456,3091,1884,2971,1961,1980,5283,8255,5932,6133,8992,15814,2189,5938,6525,12258,4624,24593,5700,13303,1830,9920,709,2064,439,4836,8767,11185,96,196,6444,9025,5161,18028,4275,6942,7168,15050,1408,2717,1317,5013,8271,11426,6640,2904,5808,6478,5927,2357,4435,8008,7429,2960,1879,4393,1450,2223,8605,11499,429,11286,3795,8596,3827,7366,6297,12839,5716,9344,1243,3788,1154,2778,5281,5066,2307,3043,4364,5267,2830,8755,5963,6910,2879,7081,5873,7150,4521,12517,3347,5041,135,101,4224,4795,4767,9983,6398,6349,8473,10568,10625,12682,15028,19594,4032,3677,3057,947,5058,4741,4846,960,4399,4290,5533,975,8678,10862,8027,1891,2910,3427,243,3997,1662,2738,2174,3454,6331,8311,7912,6770,5765,11204,9451,7552,5027,5888,2699,4409,5980,11147,5100,22212,6413,8847,3446,8698,3740,7378,3987,10824,3243,5285,91,191,5385,8588,5942,22250,6962,9528,13602,21276,10922,15206,16835,27721,4341,6297,4514,889,10230,12255,9824,3580,5586,7372,7560,2173,10043,14575,9955,3262,3231,3621,292,4154,3424,8389,3990,8881,6357,9995,8566,10893,5833,11827,6893,4943,10625,10064,7550,11311,10078,10919,4753,16722,8981,7995,4387,8537,14242,16747,8079,28237,6364,8298,276,340,9469,10129,9548,19236,10224,10315,14846,11587,28845,36368,36281,39557,17733,12896,12108,1708,17252,13317,12782,2009,8389,9310,9325,1427,23170,26728,17888,3585,5369,3778,344,4220,3336,4193,4232,5266,9119,9628,5674,4021,17235,25703,22154,21057,17056,23049,6672,15545,16771,24057,8261,42867,18096,29905,7331,25052,2736,5692,1441,9037,12210,17210,564,537,14994,20235,15321,44862,19618,25139,28577,38986,6459,9010,5560,13933,22794,26811,17901,4492,25710,24804,21928,6156,19257,26584,23546,6059,4732,8875,3521,2446,14913,18396,1323,15783,6209,13211,9039,13321,31111,49943,16358,16213,3782,8796,3935,6264,9772,6868,5012,6755,9606,8892,5229,16057,13396,10247,8118,11724,10339,9693,6695,14581,6171,8957,471,367,9890,9498,11130,18885,17690,15931,23315,21885,21560,21026,31285,29551,8100,6909,7368,1380,11990,10166,11210,1981,11519,9065,13435,2541,15176,17074,16473,2553,5765,4366,859,5586,2679,3990,4409,4942,12799,13290,18078,11811,8780,12777,15453,9788,9537,8555,4381,6621,9157,11271,5897,23153,10154,12215,5842,15105,5554,7891,4063,11480,5310,7463,300,312,7567,9527,9862,23787,13340,16921,27309,36592,12682,17306,18268,23383,8117,8270,8279,1609,13046,11184,12124,3515,11633,13133,13343,3415,11033,13304,10227,2431,5097,4900,631,6324,3425,5894,4137,8028,9060,13790,14766,15162,5543,9523,6684,4592,10189,9741,5092,8672,9696,9605,4167,14658,6842,6779,3099,5779,13331,16019,7529,26315,8254,7186,146,132,7193,8154,6875,14424,4628,5657,10700,4023,19832,23074,22237,22825,12894,11496,7807,1370,15812,12945,10208,1666,6966,9429,6805,1199,19722,21729,13519,2687,4705,3785,167,4665,3298,4155,4093,3867,5268,6431,3916,2222,17478,25273,18319,14795,22384,32351,7361,16126,16498,23513,7412,40616,18863,30289,5899,25639,2896,5817,1662,9878,17039,23795,282,246,14165,19590,11816,36811,15511,21385,24518,36372,5195,6598,4435,14424,24078,29561,16886,4955,21047,20228,17550,5363,17504,24881,18631,5376,5089,9105,3556,3544,16510,18945,819,21176,7263,14601,9120,13853,23621,36627,13672,13488,4492,12990,4008,6068,14921,10265,6050,7686,11439,11763,5944,18395,13977,12628,8315,16550,12544,13482,8274,18364,8056,6861,186,147,10140,11767,12845,25157,20915,19457,26120,25809,28195,30877,39746,46090,10502,10527,8370,1912,15725,15277,15403,2501,12991,13205,16430,2752,21831,25264,19612,3929,5919,5130,365,6715,3041,4863,5136,5902,15463,17410,16260,11354,15194,23571,24867,15714,8789,7425,3731,7031,9289,13916,6019,27628,10409,12463,4737,15971,7380,11476,4904,14241,5012,6592,113,189,7224,8829,8414,26682,12943,18481,29320,37316,17873,27545,22065,35463,10662,10962,8319,1976,18071,16983,14757,4644,12579,16218,15656,3259,17228,20804,13188,4824,3926,3719,339,4729,3598,6565,3791,6662,9257,15234,10256,8940,9684,18927,9946,4604
Homo sapiens,9606,genomic,RefSeq,80707709,123938,51.17,55.76,42.42,55.36,20482,19242,15339,19315,24166,20933,12563,31148,24512,15284,11525,18011,28265,26162,18898,49043,22024,13456,1039,450,18809,13577,20222,35135,24998,18971,31530,27900,58642,47217,71382,62700,28220,20080,22017,2740,28202,16768,24754,3064,18440,16194,17431,2628,38347,42053,33723,5941,12410,8220,866,11438,5273,5051,8808,7301,14534,12078,11594,7846,26362,33012,42979,33987,30630,46486,12694,23154,21805,39798,12342,77442,29347,47410,11260,34807,3278,8901,2360,20379,21498,32426,853,797,20098,30785,20356,68371,24381,36777,34102,47281,7676,14136,6162,17722,28414,40669,21419,7537,23910,28695,24877,10283,25628,41349,25593,11825,4608,13478,3811,3589,21537,27197,2365,26020,9854,21063,13501,22638,30336,46091,21478,19306,3744,12490,4400,10042,15956,6793,10245,10161,12925,7655,7951,16181,14038,7124,10247,14558,8419,4921,6918,10565,12072,6896,570,385,12198,7330,17693,26309,23909,11892,32696,25362,23484,11530,41684,24271,15431,8177,12535,1898,15384,7220,15133,1894,12178,7511,14799,1694,13863,11491,15450,2223,6978,4026,637,6059,3360,2347,5200,4468,10845,7319,13297,7765,6488,6089,13235,5746,17149,9478,9259,14429,17758,14334,10868,38954,15701,12228,9224,18534,15274,13222,11681,30415,12185,10031,706,434,12165,12714,18915,36340,25577,16759,39813,38765,42129,28299,58015,54148,17656,14761,14720,3176,21100,15306,22211,4925,14858,12729,16560,4245,29252,29510,26029,6007,9538,7167,1006,9251,3874,5231,4965,8010,13469,13173,15414,12863,12691,16282,20103,15189,21563,19447,14991,22049,24645,23974,12625,41886,18746,12116,7939,13641,19474,16375,11554,26443,17717,10265,565,315,24593,16970,26305,54071,16834,10506,22876,16836,30573,20668,41578,29349,30513,20273,20772,3327,35664,21688,29683,5260,17317,11474,12870,2644,26673,22983,21904,3274,12753,9623,900,11069,8575,8139,15309,14895,10910,8975,9151,6033,17814,21697,29027,19752,32466,59424,10607,21333,21470,37697,10715,73693,31779,57869,10795,39021,4263,8771,2262,14860,24032,37920,551,806,17490,23800,19126,62405,26952,43838,30751,58014,6807,8762,5887,12188,28298,41247,23785,9191,24372,23896,24173,10904,28131,46048,26445,13836,6062,12649,4825,2737,22639,32674,2234,25817,7791,16335,12987,22285,29595,52831,18253,23668,3727,11155,5083,9311,9390,4963,4913,6239,9485,7673,6022,15303,10662,6475,6436,11966,6456,5327,5290,12590,6818,5066,499,367,9201,8312,16191,31063,17213,10650,21623,23355,17355,14438,33881,28421,6490,6556,6777,1194,12617,9154,10822,1992,9137,7509,10994,2297,12300,11716,13044,1934,4758,3717,497,4927,2995,3869,4470,6159,9153,8038,10508,8185,6170,9183,12082,8772,28923,28665,11402,25136,32144,64287,18658,156632,27339,31932,12218,46910,26272,40914,17185,103355,22141,32288,897,941,26549,53297,31116,150877,36468,42746,60016,103936,72347,96695,88255,182899,31865,45770,25903,11734,47386,73893,34983,19461,30699,50982,33267,17490,61554,113392,50882,27715,24084,31123,2029,31576,13984,35814,15072,50197,31157,55559,27526,40255,29799,85582,41795,52427,23954,18399,20636,25623,25636,19482,11906,30767,24065,14009,10707,15690,26161,23679,16249,38984,21765,14988,807,542,29407,19982,24303,46542,22347,14716,37367,24974,47039,39800,64321,47807,29827,19747,24052,2753,32523,20001,28892,3852,15458,11382,18081,2809,39215,35592,31646,5201,12469,8864,629,10588,8327,7854,12407,9276,10523,8954,10556,5973,20731,25947,33140,21973,27714,42596,12102,22564,20679,38023,11510,71253,34007,57514,13137,42420,5570,14645,3353,26066,20781,30878,682,607,20317,33995,18813,69567,31921,45843,41935,58117,10927,20354,10977,28458,24388,36292,19636,6674,25248,31155,27574,9924,29016,45694,32244,13341,8630,22150,8196,5282,19736,28605,1343,20718,8635,22309,13540,23367,25837,41357,18561,16884,4632,13875,5716,11096,20367,9384,8864,8736,9391,5107,4788,10128,15835,7787,8589,13532,10278,6812,7661,11723,10052,5405,469,200,9577,6566,12633,18876,19725,12169,28961,23712,22460,16182,37047,22009,12203,7469,11688,1421,11323,7177,12706,1631,12739,8016,13833,1986,14638,13367,17032,2031,8195,4525,593,6829,2420,1602,3460,3359,9505,7851,10470,6920,6539,7247,13359,5776,31065,24631,13576,21759,21829,22442,13055,64026,25578,26800,12653,43846,21718,22081,13843,52570,19732,22740,812,550,17200,22114,22058,57621,37642,36251,50573,67279,51107,48007,68767,85912,27846,24245,20878,7724,28714,27451,27261,8125,25575,30163,27791,8541,42126,50844,39521,17962,15348,15183,1448,19223,5729,9799,7028,15449,20584,27483,23581,22134,17487,33224,28469,23209,18647,16218,15958,20062,20586,16536,8770,25830,17964,12056,8081,11287,19393,16437,12944,24922,16338,11070,657,356,18095,14822,18406,32214,15085,9640,21266,13154,28322,19310,35424,21537,27173,18206,18096,2641,27164,16792,23381,3610,14629,11505,13636,2106,25063,20032,19904,2479,10755,8232,536,8157,5827,7221,9903,7148,7876,6801,6792,4085,17068,18486,25555,16888,21966,38081,9061,17206,19286,28629,10168,52132,29484,52193,10579,33531,3124,7900,2157,11314,14945,21977,514,357,14996,21652,12031,41888,23390,32117,26641,39893,4939,6317,3684,7951,21566,30116,15872,4904,23271,24078,19019,7190,27465,44207,25237,9378,4430,8660,2884,2010,15079,19737,1410,17248,5963,12212,7974,14024,20649,35969,13658,13068,2642,6446,3610,6629,16292,7284,8368,8168,8907,5593,4997,12380,12185,6500,7238,11741,9068,5655,7700,12177,9514,5687,336,321,9911,7000,12840,19723,17984,9982,24908,19207,22507,14079,34357,22070,13154,8874,9975,1612,13034,8314,12407,1574,13073,9130,13160,2337,16237,14730,15327,1938,7024,4336,587,6025,2944,2734,3744,4565,6127,5637,8225,5357,5743,7782,11476,7078,32180,28889,10988,20549,19749,34818,12711,88191,29061,31377,12148,39812,27831,43258,19316,83415,18208,23877,643,705,15394,26927,16586,69379,34952,35306,49974,75820,60601,75792,69929,113123,32095,36729,20447,7176,34013,45427,27061,11097,29933,43041,32423,12128,53858,84385,39427,17004,21003,23830,2084,22372,7442,19965,8291,22868,15895,30575,17632,20948,19557,51238,27545,31902,21940,16390,11538,14871,12491,11411,5858,17474,17887,12725,7702,12916,18518,19186,12985,32020,14700,14012,468,218,10692,10341,13485,25958,18928,12926,27440,20146,39108,37037,62307,47759,17160,13616,14072,2331,14583,9781,15070,2217,11591,10502,11936,2526,24320,26474,24656,4762,6444,6359,295,7202,4753,5683,6323,6227,9037,9086,10054,6505,17114,25547,30330,20761,20840,29765,8198,17015,14696,24457,9069,56407,22500,35726,8613,29123,4171,9094,2749,20052,17553,25062,518,404,14976,22229,16205,47358,22534,30973,36897,43777,8057,14073,8778,21189,12122,19637,12872,6485,15408,17585,17974,7160,14586,26166,21294,12398,4546,12049,4957,4357,15885,22014,1518,20817,6629,17391,10589,15340,21629,34749,22604,17834,4471,11405,5709,9249,11,10,7,14,13,14,9,52,15,10,6,34,5,0,6,12,12,3,3,2,4,18,22,19,17,21,18,33,10,5,17,23,12,14,7,0,10,12,33,8,8,21,23,2,13,11,10,1,2,13,22,20,1,0,0,11,11,33,49,30,1,8,9,5,7,2,18,1,10,23,49,19,15,8,7,33,1,2,2,18,0,2,8,1,26,12,11,16,29,25,55,47,3,24,17,15,5,6,17,0,7,26,5,10,14,49,47,1,3,1,17,3,5,7,9,25,2,10,2,3,35,17,41,20,4,11,25,19,20764,15699,12721,17580,17578,15978,8499,24346,15090,9865,7237,11390,18678,16557,10625,29705,14541,11542,580,381,16597,14402,16628,38321,13845,9544,21303,18107,27279,24298,44377,36626,19589,15228,17394,2978,21428,14119,18578,3326,18487,9509,12266,2707,22806,25693,20220,4708,8267,7423,539,5990,5780,6143,7008,8534,10120,8179,8119,5181,17261,23483,25534,19192,19373,28414,9048,18712,19208,29089,9273,60343,22474,35574,9942,34049,5364,10906,3430,24214,14772,23784,559,624,16682,27914,14790,51094,20238,26460,27993,41070,7649,11990,8796,22439,14331,20834,16919,8703,21151,25056,21816,12225,22887,25990,27134,14834,6138,15129,6679,5642,17811,24888,1676,21144,6222,16126,9037,16292,24284,41615,21864,22573,4600,15749,6971,11452,13799,8820,9268,8474,19044,14297,10225,24254,19826,14891,14444,24575,20073,16176,15145,29691,12826,8186,794,287,17274,11371,25296,39123,30038,19449,35018,33544,42768,30309,69350,52187,9975,7143,10364,1549,16617,12852,17293,3498,18492,14748,21347,4000,28262,28473,29735,4754,10074,5812,482,7808,4056,4924,5296,6128,18185,17632,25361,16497,17253,25793,32346,18939,44435,42567,19501,30300,43407,63023,22903,130251,39663,52135,21500,62733,25883,32086,14182,72144,32126,37592,936,838,33194,49873,51259,153700,51061,54179,77531,105715,54644,68332,82485,135917,33707,34431,30471,9591,52948,65885,53146,22386,31755,46890,39395,17074,53083,81682,45519,21170,30557,31498,2759,35979,12630,28635,16291,35905,37032,58827,46451,50066,24534,55113,32416,28232,26115,18978,19415,22467,24395,18542,10898,27423,31144,20138,15914,22967,31729,30317,20732,46594,19062,15459,791,465,17733,14925,23699,33386,28861,21077,43925,28228,53633,47055,87610,65592,28044,19544,25564,3111,26024,16968,26624,3868,18380,15192,21760,3688,40810,45964,39515,5476,10692,7521,594,9000,5863,6322,7814,6328,15614,15083,13951,7889,27638,40497,50340,34802,29085,40268,14305,26811,24057,39091,12950,66326,34585,53507,15014,43736,5473,13110,3197,26119,22563,31139,852,522,17972,28284,24026,57282,31413,42805,48378,59197,8232,14775,10449,21989,23268,28486,20874,7422,26711,33414,27690,9987,24100,33685,33582,11896,6567,16583,7211,4951,20708,25560,1746,25308,6908,16792,10901,16422,30557,48678,27903,21397,4988,15425,8014,13544,36602,22923,25353,25625,35825,29384,20831,51243,45275,36259,31090,47779,35934,30389,26102,50626,33702,30357,1598,823,29004,24994,39898,53121,52232,35268,58824,70819,76342,53713,125418,81802,36184,27124,32736,5309,41300,33877,42948,6788,36651,35384,46613,8368,48809,52450,51180,7547,33645,17779,1620,21467,10143,11475,13159,12977,30254,27844,38854,26958,26757,35726,52416,27541,38318,37723,18416,25673,31645,41574,18106,94418,40410,49144,22149,61704,25841,31329,14406,62716,24905,33937,1349,1053,27965,36500,39720,85578,51974,55517,117513,139126,62484,71472,98444,127882,31570,31985,31038,8864,40638,48693,46814,13422,33097,44355,41755,17169,44616,66169,41006,15493,23754,24256,2208,26363,10440,21789,14343,27330,29395,42585,40851,42635,19861,40762,28474,27173,37911,29139,21828,31451,30110,24194,12729,35373,38683,24067,18851,26369,44978,42864,26360,70732,28597,19650,768,470,18856,17904,23432,34791,30577,21282,48239,30165,94060,79312,118436,101411,38891,25693,27314,4162,35272,24316,27824,4625,22250,18232,21495,4070,59016,63549,45419,10323,13249,8748,801,11029,7858,7551,10091,9384,17955,14784,15523,7438,39678,55759,58605,47656,44065,56139,17580,35870,30411,51878,15344,96025,44648,65212,17664,59194,6921,16654,4309,33690,30005,38142,690,673,21671,34001,27133,65587,34609,46978,53633,73048,15295,27200,14002,40479,34190,40062,27512,13401,39517,51976,34236,14369,31494,47060,39741,17728,9247,23661,8500,8452,27802,31025,2050,36484,9378,22051,14129,25238,42439,66622,34108,30739,6978,24963,8963,18734,46051,27778,28504,29287,42107,29688,21992,55173,57594,41177,39918,62657,44331,32434,32762,57883,39354,24194,1074,538,30449,23049,45525,62028,87337,57192,99999,93578,114965,77260,181372,139395,35417,23953,28375,4751,32704,22725,33873,5975,39427,33735,50915,9406,60796,61341,58378,9175,47393,20755,1139,23569,10663,10791,14568,16081,41012,33830,49870,32840,34716,44927,59296,40580,41754,43774,16392,29041,34929,60040,23944,152623,43176,58403,20815,69262,27306,37301,17276,87468,28188,35723,921,545,27794,44515,38366,121018,54561,67990,113508,164964,74464,99265,121911,225648,32667,37387,27696,10937,48285,63586,47639,21244,33880,57543,41591,20905,58980,97834,49735,27294,31510,27765,1781,31818,13953,31493,17809,42743,37471,61503,43289,48109,25855,61280,30473,39548,20713,18336,16187,24440,22455,20362,11577,38896,13596,9980,7699,13389,28048,27843,16994,52313,11996,12870,800,635,17638,14093,21939,43560,16215,10539,24178,18829,44029,34267,59362,58776,38802,31886,35187,5584,38942,27152,41710,7595,17258,15562,19570,3397,38100,41154,36440,7790,10571,7920,734,12463,6019,6351,10171,11866,13644,11175,9828,8194,22474,28070,37661,32797,26972,40234,12531,27965,16791,30666,9378,62676,24418,43980,10772,41045,4115,8270,2728,19282,18893,29207,777,993,16821,24833,17540,60446,22319,32650,41876,52363,6517,12444,7423,20178,34152,47025,32183,12449,27954,22763,35753,16307,23762,37715,30515,15012,4757,10591,4763,4028,18642,26431,1955,28876,5868,14875,11190,21147,34289,52950,23175,25680,3356,9744,5932,9009,20693,11803,11639,13351,13095,12165,7628,25936,11128,6504,8147,12712,19460,15203,15043,33906,10203,8359,511,570,12628,12166,16350,28749,24126,15506,29395,25638,45549,34060,62777,56778,28693,21665,24107,4178,23688,19244,26542,5535,17174,11671,20416,3167,34348,38257,32961,6863,6851,5871,677,9619,3473,4711,4222,6090,18186,14885,17262,11444,16904,23033,34495,24655,3737,3184,1537,3640,2956,6608,1423,17681,1904,1761,1099,3855,3380,5743,2253,16465,2209,2500,49,100,1727,4301,1950,10302,3225,2698,3877,5289,8736,12521,9442,20480,5179,7802,4050,2604,5523,10799,6624,4152,2908,3535,2909,1547,8209,17511,6542,5636,2484,2768,220,4367,832,2796,982,3383,2981,4484,2865,3607,3686,11972,6160,10169,22044,21697,15045,24321,22728,22391,10207,41934,14665,10995,7928,13648,29648,32009,18972,60084,18932,16639,543,901,18653,17786,21282,49774,15719,9848,23169,17939,43123,39129,60901,78104,36492,32566,30079,5601,55630,39341,56998,12698,16370,15426,16554,3763,43983,56359,39382,11514,10498,9244,782,11434,7252,8944,11568,15199,10683,9975,8769,6447,31972,46477,50300,47773,23475,37967,8075,23423,15367,26908,7021,58048,23306,47026,9234,42264,3711,10522,2462,25141,22797,32493,531,580,15115,26232,17859,68837,23782,40631,43729,64998,8166,19911,10803,37565,25027,37122,24338,13119,36065,25077,48540,23875,26173,49281,32629,17482,8196,22447,8231,10660,15548,25637,2021,24456,6262,17141,11353,26151,33719,67853,22196,32384,5378,20840,9598,17832,23139,13763,10236,13899,16248,17053,8761,35496,16456,9913,9664,19367,25057,21643,16110,40650,16670,12342,378,391,14930,15489,17412,44399,28495,20036,30039,37913,48906,41732,69422,74993,28649,25201,24623,5341,48985,44153,50000,14711,21216,19040,25559,5620,42642,57468,41537,10025,9430,7984,879,11517,5157,7125,7627,10019,20568,21305,20786,15929,27732,43849,44820,38493,4752,5880,2104,3834,4449,10745,2392,27014,3327,3501,1321,5669,3760,7228,2046,15807,4757,5404,75,160,2925,7966,3248,22467,3961,3995,5334,8957,9230,14085,11728,27308,6288,10031,5008,3865,13597,24075,14965,16146,3596,6340,4340,3218,10062,22540,7789,7749,3434,5257,415,6584,1647,6990,2089,8920,5104,8628,3577,7250,6854,18294,9212,13799,20603,18057,14714,22828,17682,15791,10211,32224,15843,10058,7336,12100,24660,24966,16609,47624,10243,14074,394,275,16695,16480,17788,34414,12695,9705,21016,13630,34579,29600,51631,45659,27235,18995,23427,4098,29052,20354,31366,5769,13980,11674,16656,3226,31935,32642,30889,5944,11082,8157,492,10666,5514,6286,8134,9023,9227,8557,8309,5528,20212,25935,43765,24373,26251,45167,11928,24723,17987,31585,8915,61584,31367,58512,12835,46267,5085,12313,3045,24880,17741,33238,519,509,14124,25512,15718,54884,27768,42378,43283,64457,7297,14411,8970,22351,24741,32796,25594,10071,28753,25043,33698,13365,27662,53229,36241,16760,6336,15175,6267,4535,19713,29860,1116,24093,5698,13512,7230,16029,26730,50323,18008,23091,3664,11655,6059,9840,25757,15442,14728,15185,15012,14930,9790,33654,18253,11713,11480,19371,23362,22930,16307,43905,12904,11512,505,502,15271,15989,17481,33564,26836,18523,32685,29037,50546,40948,69665,61283,25647,18443,23515,4618,28039,22552,30352,6145,20553,16156,24678,4527,38040,45584,37827,8367,10577,7860,815,12189,4091,5338,5110,7842,18631,16487,18343,12922,21504,28441,36666,24522,6755,6692,3415,5480,4669,10037,3118,29341,4193,4283,2039,7138,5249,8288,3047,21809,4025,5700,194,271,2916,7547,3122,14651,3345,3096,5594,7799,9585,14177,12513,24041,6534,8289,5651,3002,8015,14295,7874,5940,4364,5672,4815,2555,7876,19032,9225,6035,5402,5885,342,8398,1146,4455,1478,6259,3746,5291,3683,4787,4927,14586,6999,11340,27499,23794,16482,29906,22841,21606,11295,47112,19421,11887,8887,17012,34533,35023,19549,76049,15389,10826,345,257,16378,16153,18947,49108,15483,9993,23332,19757,43279,45810,60573,79953,31360,28408,24178,4666,30994,26891,28758,7327,16499,15586,19403,3198,62896,74039,49050,14664,11693,8964,391,10860,5869,8840,9595,14199,9867,8070,8723,5053,27359,40115,40351,38315,41573,64375,14461,39859,24715,44138,12834,108579,40280,72013,13688,65898,5271,16999,3464,36407,23756,36373,723,674,19532,34221,21571,101618,32455,53564,52242,97298,9640,23593,11824,44232,37343,53297,29433,17138,35935,39970,37600,21635,34407,66191,43463,22552,12843,40677,10716,14084,24092,36628,1907,36656,9087,26384,14227,38037,34187,66075,25885,34554,5766,23723,7626,18732,26378,12625,12024,15341,16770,14035,9592,35386,19083,10693,10299,21687,22304,19363,15675,46102,13882,8260,610,373,13220,14061,17896,40213,26632,17230,36545,35455,47939,37245,70362,78657,26029,19495,18972,4482,24517,22261,22973,5976,17484,14519,22041,4418,52522,62184,47777,13208,9684,6294,582,9769,3916,5754,6325,9574,16644,14261,19287,12856,20356,31364,34396,31271,5391,5232,1943,4294,4195,12621,2866,33985,3399,4060,1712,6507,4174,7319,2831,19470,3233,3655,86,103,2716,7364,2589,17854,3046,3087,4440,7862,7994,13625,9560,29203,5156,8900,3660,3217,7063,16611,5445,7553,3223,5135,3348,2480,13106,31886,10651,18086,3699,4210,285,5309,1592,7725,1911,9157,3374,5609,2610,4503,5095,19387,7009,14343,12599,10181,7810,12158,10987,10618,5414,17653,10724,8222,5935,9203,16018,18150,9746,32302,7653,7811,331,403,9338,9902,10611,20003,16492,11836,20910,16989,30727,33759,42739,41728,13021,11336,11151,1908,15000,12601,13391,2692,9374,9288,9186,1481,21709,27429,18434,4698,5586,4738,605,5878,3043,4773,5872,5304,8619,8178,6456,4730,17755,32642,30027,35152,16981,24020,6305,12838,14934,23072,6224,41429,15514,24360,6132,18812,2455,6010,1525,12419,11251,18382,413,484,13157,21076,13651,41413,17221,21232,24861,31031,4628,9094,4159,14276,13592,23852,12340,4420,16612,21964,16628,8066,11829,19688,15608,7549,3150,9936,2784,3367,15064,21615,1596,17326,4886,14990,6753,14208,18387,31005,13783,15839,2927,11375,3772,9438,16,44,21,55,26,66,29,60,35,31,17,84,13,28,11,40,13,20,37,13,30,47,55,47,27,42,144,75,59,23,58,43,29,26,33,17,63,69,78,29,44,55,57,20,49,69,62,30,36,38,49,60,29,30,13,29,43,111,162,120,38,77,81,103,17368,15673,6134,9564,13627,17112,7824,39723,16057,17444,8123,23625,9261,12269,6823,22594,11656,13816,381,499,10412,13658,12270,30816,21873,20177,27487,36627,23883,26898,28642,37989,11748,12268,11017,3539,12143,13522,13623,4424,12493,16775,16793,6351,16368,23300,16313,5743,8956,10057,1039,15324,4216,7300,4530,8927,13209,19740,16379,16396,10170,18858,14909,10475,7697,7585,4240,6174,6283,6845,3713,12676,4469,4349,1957,3886,6720,8707,4418,17232,5181,5350,101,89,5452,4914,3629,11535,3646,3037,6320,5229,8901,10188,11070,14876,8537,7178,5967,1270,6448,5826,5940,1513,3978,4196,3067,720,7670,12731,6325,2197,3527,3407,123,3900,3556,3654,2829,4551,3284,3820,3381,2580,6949,13175,8592,10292,12255,28794,3866,8261,8687,22768,4821,41925,8629,24661,2815,18290,1578,6076,1083,13649,11486,20473,163,227,8086,16177,6667,29593,6922,13272,11909,26632,3381,7637,2102,13670,9902,20348,8977,6074,8991,12596,9470,5709,5774,14664,9684,7185,2774,11927,2475,5187,11905,22847,747,19976,4285,17201,5099,14584,9080,25555,7706,14686,1888,10902,2431,7217,8468,6429,4333,4434,6964,7530,3600,12675,9464,7815,4649,10147,7733,9141,6014,15625,5740,5996,259,62,6865,7025,6239,13609,9716,7614,13378,13195,16266,17435,21345,25718,6499,5977,5471,1064,6792,6736,7527,1837,7110,5818,8017,1578,11354,15432,11331,3032,4555,3971,274,4994,2699,3625,3253,4536,9250,10031,11738,8570,8112,16501,13517,12133,7381,9539,3714,6169,9511,21425,5852,47651,8877,14322,4982,15062,5766,12139,5462,21307,4664,7835,108,186,7991,15458,8955,39775,10299,16992,19120,33456,16570,30333,23266,54256,6680,9113,5859,2199,14625,28387,13575,9754,7271,13821,10928,5558,15724,32080,16450,9306,4442,6303,448,7323,5027,17086,6175,21109,8551,19410,12031,17461,8139,26529,11051,10944,20085,14015,14338,18130,15693,13833,6552,20986,16769,10396,7836,12009,21554,21342,11853,32980,11693,13333,371,354,13356,13149,16852,28371,18045,15525,26725,15440,48639,50716,59113,54429,24847,17572,21253,2558,25467,18558,18801,3368,13584,12729,14001,2098,31385,37734,25217,5741,8070,5369,449,7503,5492,7241,7183,7222,14573,14098,9217,6132,23527,35205,34809,29874,24095,38319,10044,21393,23808,41134,9842,70132,27047,45084,11391,37141,5063,12617,2270,22083,17238,26927,956,783,19300,33437,22648,67324,28814,39733,44383,55294,11110,20095,9218,28700,31067,44159,25956,9588,35371,47818,32260,14254,26936,44149,33921,11950,8056,21539,6343,6221,20011,28984,1823,26132,8450,23880,12281,23471,43863,79865,23033,26451,5172,20228,7009,14149,18827,10171,10345,10278,15525,12512,8641,20782,26708,15256,14950,20428,16578,14447,10992,20522,11748,13903,810,446,15667,14589,18341,24804,32149,22594,44515,32553,35506,27657,51730,41527,14111,10040,13389,1938,17667,14709,17464,2801,18908,13354,22077,3557,22972,23909,23418,4321,10563,8176,1184,9400,4514,6087,6731,6216,20598,18985,30042,17611,13128,18907,26946,13967,14307,12214,7396,9489,13621,16650,7605,36668,15284,17605,9616,22741,7866,13243,5260,17251,8125,9470,475,433,11816,14235,15106,35482,21259,23550,43309,51581,21199,26503,29049,40239,11037,11349,11070,2961,19379,20315,17165,6492,16213,19524,20052,7348,14434,21823,15009,4982,7817,7829,902,9940,4443,8794,6529,12964,13492,21779,21461,22683,8203,16842,11396,7580,17062,14971,9673,13715,14392,13012,6160,20660,11074,9370,5027,8355,19930,20283,10030,33269,13987,10962,332,257,11801,12201,11046,21797,8825,8619,16369,6221,30384,30573,35417,31845,19528,15717,13282,2075,20672,18684,15417,3482,10134,10861,9025,1450,27712,30179,19014,4671,7678,5133,288,6637,4814,5500,6108,5550,7378,8352,6131,2808,24062,34838,28022,22825,30844,52881,10339,21829,22438,41620,9743,71575,26624,46428,9345,39914,4987,14190,2273,22876,24907,39045,447,453,17966,34215,17836,59870,22005,33357,38036,53127,8485,15358,6765,30488,35104,52595,24142,10061,33347,44009,28071,13091,23482,44597,25696,12464,7638,23601,6222,10075,22533,34756,1200,35260,9976,28744,13308,27115,31876,63254,19925,20661,7857,34518,7519,16297,28940,15222,11941,11462,18508,16278,8727,24288,26023,19674,15274,28153,20160,18958,13833,27030,15663,10598,301,280,16332,16858,19963,36405,38897,29941,51243,40330,43683,43811,69109,69809,17433,15677,15470,2897,21684,22429,21382,3937,20536,21544,26540,5497,33340,37826,30184,6503,8783,6927,524,11118,5497,7480,8141,8460,25077,24704,27370,16411,22998,35495,39078,25485,12820,10579,5037,8653,15075,23553,7575,52209,14660,19572,7099,23212,11582,19985,6585,27322,7397,9376,183,251,10719,16729,12867,47694,19834,27946,46300,57765,27731,46304,33825,66456,15886,16456,11505,4027,27351,37932,22502,11024,17016,28710,22415,8244,29618,47591,21165,11061,5981,6153,495,7868,5037,12066,6782,13692,14486,27249,15500,15100,14626,39549,16419,10380
    '''  # 251231 cocoputs_8.csv

    df = pd.read_csv(StringIO(source_string))  # read string into dataframe

    # Step 2: filter dataframe for the requested species

    if species not in df['SPECIES'].values:
        print(f"Error: species '{species}' not found in provided data.")
        return None

    row = df[df['SPECIES'] == species].T.reset_index()
    row.columns = ['Attribute', 'Value']

    # Step 3: process codon-pair values
    df1 = row.iloc[10:].copy()  # remove first 10 metadata rows
    df1.reset_index(drop=True, inplace=True)

    # rename for clarity
    df1.rename(columns={'Attribute': 'Bicodon'}, inplace=True)
    df1['codon1'] = df1['Bicodon'].str[:3]
    df1['codon2'] = df1['Bicodon'].str[3:]

    # Step 4: map codons to amino acids
    codon_table, *_ = extract_kazusa()  # assumes extract_kazusa() returns codon table
    triplet_to_aa = dict(zip(codon_table['triplet'], codon_table['amino acid']))

    df1['aa1'] = df1['codon1'].map(triplet_to_aa)
    df1['aa2'] = df1['codon2'].map(triplet_to_aa)
    df1['aa_pair'] = df1['aa1'] + df1['aa2']

    # Step 5: normalize values relative to aa_pair and overall
    bicodon_to_relative_value = {}
    for aa_pair in df1['aa_pair'].unique():
        filtered_df = df1[df1['aa_pair'] == aa_pair].copy()
        mean_value = filtered_df['Value'].mean()
        if mean_value == 0:
            filtered_df['Relative_Value'] = filtered_df['Value']
        else:
            filtered_df['Relative_Value'] = filtered_df['Value'] / mean_value
        bicodon_to_relative_value.update(
            filtered_df.set_index('Bicodon')['Relative_Value'].to_dict()
        )

    df1['Relative_Value'] = df1['Bicodon'].map(bicodon_to_relative_value)

    mean_value = df1['Value'].mean()
    df1['Bicodon_Relative_Value'] = df1['Value'] / mean_value

    # Step 6: optionally save to disk
    if save_csv:
        import os
        os.makedirs(output_dir, exist_ok=True)
        output_file_ext = f"{output_dir}/cocoputs_{species}_processed.csv"
        df1.to_csv(output_file_ext, index=False)
        print(f"Created: {output_file_ext}")

    return df1


def merge_multispecies_cocoputs(Species=['ecoli', 'bacillus', 'pichia']):
    def take_first_letter(t):
        t = t.split(' ')
        t = [x[0] for x in t]
        t = ''.join(t)
        return t

    merge_name = '_'.join([take_first_letter(x) for x in Species])
    print(merge_name)
    """
    species could either be 'ecoli', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    these will be converted to scientic names
    """

    DF = []
    RV = []
    BRV = []
    for species in Species:
        df = extract_cocoputs(species)
        DF.append(df)
        RV.append(df['Relative_Value'].tolist())
        BRV.append(df['Bicodon_Relative_Value'].tolist())
        print(df)

    df = df.drop(columns=['Value'])
    df['Relative_Value'] = list(np.prod(RV, axis=0) ** (1 / len(Species)))
    df['Bicodon_Relative_Value'] = list(np.prod(BRV, axis=0) ** (1 / len(Species)))

    df.to_csv('dataset\\cocoputs_{}_processed.csv'.format(merge_name), index=False, header=True)

    return df


def codon_optimization(pp, species='ecoli',
                       preceding_triplet='ATG', tailing_triplet='TAA', aa_start_index=1,
                       rv_cutoff=0.2, mediocre=False, export_gb=False, verbose=False):
    """
    species could either be 'ecoli', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    these will be converted to scientic names in extract_cocoputs
    """
    # the first and the last use the most prevalent triplet

    df1 = extract_cocoputs(species=species)

    codon_table, *_ = extract_kazusa()
    triplet_to_aa = dict(zip(codon_table['triplet'], codon_table['amino acid']))

    # ----------------------------------------------------------------- Checkings
    pp = pp.upper()
    preceding_triplet = preceding_triplet.upper().replace('U', 'T')
    tailing_triplet = tailing_triplet.upper().replace('U', 'T')

    if pp.endswith('*'):
        pp = pp[:-1]

    if '*' in pp:
        print('internal stop codon', 'codon_optimization terminated')
        return

    if tailing_triplet in triplet_to_aa.keys():
        pp += triplet_to_aa[tailing_triplet]
    else:
        print('tailing_triplet ineligible', 'codon_optimization terminated')
        return

    if preceding_triplet in triplet_to_aa.keys():
        pp = triplet_to_aa[preceding_triplet] + pp
        dna = preceding_triplet
    else:
        print('preceding_triplet ineligible', 'codon_optimization terminated')
        return

    check0 = [x for x in pp if x not in triplet_to_aa.values()]
    if check0 != []:
        print('codon_optimization terminated due to ineligible aa', check0)
        return

    if verbose:
        print('Start codon optimization process, species = {}, rv_cutoff = {}, mediocre = {}'.format(
            species, rv_cutoff, mediocre))

    for i in range(1, len(pp) - 1):

        # ----------------------------------------------------------------- pos i-1 ~ i
        aa_pair = pp[i - 1:i + 1]

        df2 = df1[df1['aa_pair'] == aa_pair].copy()  # Make a copy to avoid SettingWithCopyWarning
        df2 = df2[df2['codon1'] == dna[-3:]].copy()

        df2.loc[df2['Relative_Value'] < rv_cutoff, 'Relative_Value'] = 0

        codon_to_score1 = dict(zip(df2['codon2'], df2['Relative_Value']))

        # ----------------------------------------------------------------- position i ~i+1
        aa_pair = pp[i:i + 2]

        df2 = df1[df1['aa_pair'] == aa_pair].copy()  # Make a copy to avoid SettingWithCopyWarning
        codon_to_score2 = {}

        for codon1 in df2['codon1'].unique():

            df3 = df2[df2['codon1'] == codon1].copy()
            # print(df3)
            df3.loc[df3['Relative_Value'] < rv_cutoff, 'Relative_Value'] = 0

            if i == len(pp) - 2:
                df3 = df3[df3['codon2'] == tailing_triplet].copy()

            score2 = df3['Relative_Value'].max()
            codon_to_score2.update({codon1: score2})

        Codon = []
        Score = []
        Score1 = []
        Score2 = []
        for codon in [x for x in codon_to_score1.keys() if x in codon_to_score2.keys()]:
            Codon.append(codon)
            Score1.append(codon_to_score1[codon])
            Score2.append(codon_to_score2[codon])
            Score.append(codon_to_score1[codon] * codon_to_score2[codon])

        df4 = pd.DataFrame({'codon': Codon,
                            'score1': Score1,
                            'score2': Score2,
                            'score': Score})

        if mediocre == False:
            target_row = df4[df4['score'] == df4['score'].max()]
        else:
            df4 = df4[df4['score'] > 0].copy()
            target_row = df4[df4['score'] == df4['score'].min()]

        choice = target_row['codon'].iloc[0]

        dna += choice
    dna = dna[3:]

    if verbose:
        print(dna)

    # Export gb file
    global empty_gb
    gb_str = empty_gb

    if export_gb == True:
        gb_str = gb_edit(gb_str, 0, 0, dna, 'f', 'CDS',
                         {'label': 'codon_optimization_{}'.format(species), 'aa_start_index': aa_start_index})
        output_gb(gb_str, 'codon_optimization')

    return dna


def codon_diagnosis(dna, species='ecoli', rv_cutoff=0.1):
    """
    species could either be 'ecoli', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    these will be converted to scientic names in extract_cocoputs
    """

    df1 = extract_cocoputs(species=species)
    # print(df1)
    codon_table, *_ = extract_kazusa()
    triplet_to_aa = dict(zip(codon_table['triplet'], codon_table['amino acid']))

    dna = dna.upper().replace('U', 'T').replace(' ', '').replace('\t', '').replace('\n', '')
    dna_len = int(len(dna) / 3) * 3
    dna = dna[:dna_len]
    # print(dna)

    check0 = [x for x in list(dna) if x not in ['A', 'T', 'C', 'G']]
    # print('check0',check0)
    if check0 != []:
        print('DNA sequence contain ineligible character', 'Terminate codon diagnosis')
        return
    else:
        print('Start codon diagnosis process, species = {}, rv_cutoff = {}'.format(species, rv_cutoff))

    line_aa = ""
    line_nt = ""
    line_diag = ""
    #
    AA = []
    Codon = []
    RV = []
    BRV = []
    valey = []
    for i in range(0, len(dna) - 3, 3):
        bicodon = dna[i:i + 6]
        aa = triplet_to_aa[dna[i:i + 3]]
        codon = dna[i:i + 3]

        line_aa += f'{aa}  '

        target_row = df1[df1['Bicodon'] == bicodon].copy()
        rv = target_row['Relative_Value'].iloc[0]
        brv = target_row['Bicodon_Relative_Value'].iloc[0]

        if rv < rv_cutoff:
            valey += list(range(i, i + 6))
            line_nt += f'{codon}'
            line_diag += '!!!'
            print('resi {}, bicodon {}, aa_pair {}, rv {:.4f}, brv {:.4f}'.format(int(i / 3) + 1, bicodon,
                                                                                  aa + triplet_to_aa[
                                                                                      dna[i + 3:i + 6]], rv, brv))
        else:
            line_nt += f'{codon.lower()}'
            line_diag += '   '

        AA.append(aa)
        Codon.append(codon)
        RV.append(rv)
        BRV.append(brv)

    aa = triplet_to_aa[dna[-3:]]
    codon = dna[-3:].lower()

    line_aa += f'{aa}  '
    line_nt += codon
    line_diag += '   '
    AA.append(aa)
    Codon.append(codon)
    RV.append(9999)
    BRV.append(np.nan)

    df4 = pd.DataFrame({'aa_ind': list(range(1, 1 + len(AA))),
                        'aa': AA,
                        'codon': Codon,
                        'Relative_Value': RV,
                        'Bicodon_Relative_Value': BRV})

    print(f'\n{line_aa}\n{line_nt}\n{line_diag}')

    valey = list(set(valey))
    valey.sort()
    return valey


# ------------------------------------------  gb processing tools, used in main & other def

def Read_gb(initial_filename,
            find_latest_version=False,
            rename_locus_by_filename=False):  # initial_filename without extensions, find the latest version

    initial_filename = initial_filename.split('.gb')[0]

    # Get a list of all files in the directory, remove extension
    filenames = [x.split('.')[0] for x in os.listdir()]

    # Define regular expressions for exact match and 'abc (int)' pattern
    exact_match_pattern = re.compile(fr'^{re.escape(initial_filename)}$')
    pattern_with_int = re.compile(fr'^{re.escape(initial_filename)} \(\d+\)$')

    # Filter filenames based on the patterns
    filtered_filenames = [filename for filename in filenames if exact_match_pattern.match(filename)]
    updated_filenames = [filename for filename in filenames if pattern_with_int.match(filename)]

    if find_latest_version == True and updated_filenames != []:
        lst = []
        for s in updated_filenames:
            pattern = r' \((\d+)\)$'
            match = re.search(pattern, s)
            extracted_int = int(match.group(1))
            lst.append(extracted_int)

        target_index = lst.index(max(lst))
        f2 = updated_filenames[target_index]

    elif filtered_filenames != []:
        f2 = filtered_filenames[0]
    else:
        print(f'"{initial_filename}.gb" unfound')
        return None

    # start with gb file, then gbk file
    if '{}.gb'.format(f2) in os.listdir():
        gb_str = Read_text('{}.gb'.format(f2))
    elif '{}.gbk'.format(f2) in os.listdir():
        gb_str = Read_text('{}.gbk'.format(f2))
    else:
        print('no filename with gb extension')
        return

    if rename_locus_by_filename == True:
        gb_str = gb_rename_locus(gb_str, initial_filename.split('.')[0])

    return gb_str


def gb_parse0(f, layer=0):
    if f is None:
        return None

    gb = {}
    f1 = f.split('\n')

    key = None
    value = []

    for line in f1:
        if re.match(r'^\s{' + '{}'.format(layer) + r'}\S', line):
            # print(line)
            if key:
                text = '\n'.join(value)
                if key not in gb.keys():
                    gb[key] = text
                else:
                    if isinstance(gb[key], list):
                        gb[key].append(text)
                    else:
                        gb[key] = [gb[key]]
                        gb[key].append(text)

            key = line.strip().split(' ')[0]
            value = []
            value.append(line)
        else:
            value.append(line)

    if key:
        text = ' '.join(value)
        if key not in gb.keys():
            gb[key] = text
        else:
            if isinstance(gb[key], list):
                gb[key].append(text)
            else:
                gb[key] = [gb[key]]
                gb[key].append(text)
    return gb


def gb_to_string(gb):
    s = ''
    for key in gb.keys():
        value = gb.get(key)
        if isinstance(value, str):
            s += f'{value}\n'
        elif isinstance(value, list):
            for item in value:
                s += f'{item}\n'
    return s


def feature_parse0(f):
    # print(f)
    f0 = f.split('\n')
    features = []
    feat = None

    f1 = []
    for line in f0:
        # print(line)
        if not re.match(r'^\s{21}(?![/])\S', line):
            f1.append(line)

        else:
            f1[-1] += line[21:]
    # print(f1)
    for line in f1:
        if re.match(r'^\s{5}\S', line):
            if feat:
                features.append(feat)
                feat = None

            key, pos = re.split(r'\s+', line.strip(), maxsplit=1)

            if pos.startswith('join('):
                rf = 'forward'
                text = pos.replace('join(', '').replace(')', '')
                text = text.split(',')
                a, b = int(text[0].split('..')[0]), int(text[-1].split('..')[1])

            elif pos.startswith('complement(join('):
                rf = 'reverse'
                text = pos.replace('complement(join(', '').replace(')', '')
                text = text.split(',')
                a, b = int(text[0].split('..')[0]), int(text[-1].split('..')[1])


            elif pos.startswith('complement'):
                rf = 'reverse'
                a, b = [int(x) for x in
                        pos.replace('complement(', '')[:-1].replace('>', '').replace('<', '').split('..')]
            else:
                rf = 'forward'
                # start, end = [int(x) for x in
                #               pos.replace('>', '').replace('<', '').split('..')]

                a, b = [int(x) for x in
                        pos.replace('>', '').replace('<', '').split('..')]

            feat = {'type': key, 'rf': rf, 'a': a, 'b': b, 'partial_l': '<' in pos, 'partial_r': '>' in pos}

        elif re.match(r'^\s{21}/', line):
            l = line[22:]
            key, value = l.split('=')[0], '='.join(l.split('=')[1:])
            if re.match(r'^\d+$', value):
                value = int(value)
            else:
                value = value

            if key not in feat.keys():
                feat[key] = value
            elif isinstance(feat[key], list):
                feat[key].append(value)
            else:
                feat[key] = [feat[key]]
                feat[key].append(value)
    if feat:
        features.append(feat)
        feat = None

    return features


def feature_to_string(features):
    s = 'FEATURES             Location/Qualifiers\n'
    for json_data in features:
        seq_type = json_data.get("type", "")
        rf = json_data.get("rf", "")
        a = json_data.get("a", 0)
        b = json_data.get("b", 0)
        partial_l = json_data.get("partial_l", 0)
        partial_r = json_data.get("partial_r", 0)

        # print('a',a)
        # print('b',b)
        location = ''

        if rf[0] == 'r':
            location += 'complement('
        if partial_l:
            location += '<'
        location += f'{a}..'
        if partial_r:
            location += '>'
        location += f'{b}'
        if rf[0] == 'r':
            location += ')'

        result_string = f'     {seq_type.ljust(16)}{location}\n'
        other_keys = [x for x in json_data.keys() if x not in ['type', 'rf', 'a', 'b', 'partial_l', 'partial_r']]
        for key in other_keys:
            result_string += f'                     /{key}='
            value = json_data[key]

            result_string += f'{value}\n'
            # if isinstance(value,str):
            #     result_string +=f'"{value}"\n'
            # else:
            #     result_string += f'{value}\n'
        s += result_string
    return s


def origin_parse0(f, reverse=False):
    if reverse == False:
        f = f.split('\n')[1:]
        sequence = ''
        for line in f:
            sequence += line[9:].replace(' ', '')
        return sequence
    # else:


def split_and_format_dna(sequence, chars_per_line=10):
    # Remove any whitespace or non-DNA characters
    sequence = ''.join(filter(lambda char: char.isalpha(), sequence))

    # Split the sequence into substrings of 10 characters each
    substrings = [sequence[i:i + chars_per_line] for i in range(0, len(sequence), chars_per_line)]

    # Group every 60 nt
    s2 = []
    for i in range(0, len(substrings), 6):
        s2.append(' '.join(substrings[i:i + 6]))
    # print(s2)

    s3 = '\n'.join(['{:>9} {}'.format(i * 60 + 1, substring) for i, substring in enumerate(s2)])
    # print (s3)

    formatted_sequence = 'ORIGIN      \n' + s3

    return formatted_sequence


def gb_singleline(f, line_separater='-new_line-', reverse=False):
    if reverse == False:
        f = f.replace('\n', line_separater)
    else:
        f = f.replace(line_separater, '\n')
    return f


def convert_gb_to_csv(csv_file='gb_singleline.csv', line_separater='-new_line-'):
    ''' input a folder containing gb files. output a csv with two column: column 0 ['gb_filename'], column 1 ['gb_singleline'] '''
    import os

    if True:
        files = os.listdir()
        gb_files = []
        for file in files:
            if file.endswith('.gb') or file.endswith('.gbk'):
                gb_files.append(file)

    gb_filename = []
    gb_string = []
    for file in gb_files:
        f = Read_text('{}'.format(file))
        # # print(f)
        # f = gb_singleline(f)
        # print(f)
        gb_filename.append(file.split('.gb')[0])
        gb_string.append(gb_singleline(f, line_separater='-new_line-'))

    # Create a DataFrame
    data = {'gb_filename': gb_filename, 'gb_string': gb_string}
    df = pd.DataFrame(data)
    df.to_csv('{}'.format(csv_file), index=False)

    print('Convert gb files to a single csv file')
    print(f'\tworking directory: "{os.getcwd()}"\n\tgb files detected: {gb_files}\n\tcsv file created:  "{csv_file}"\n')

    return df


def convert_csv_to_gbs(csv_file='gb_singleline.csv', line_separater='-new_line-'):
    import os

    if os.path.exists(csv_file):

        df = pd.read_csv(csv_file)
        df_dict = df.to_dict(orient='list')
        titles = df_dict['gb_filename']
        strings = df_dict['gb_string']

        for i in range(len(titles)):
            f = titles[i]
            s = strings[i]
            Output_text(gb_singleline(s, line_separater='-new_line-', reverse=True),
                        filename='{}'.format(f),
                        extension='gb')
        print(f'Convert "{csv_file}" to gb files')
        print(f'\tworking directory: "{os.getcwd()}"\n\tgb files created:  {[x + ".gb" for x in titles]}')

        return None

    else:
        return None


def extract_gb_locus(gb_str):
    gb = gb_parse0(gb_str)
    locus = gb["LOCUS"]
    return locus[12:35].rstrip()


def edit_sequence(gb_str, start, length, repl, silence=True):
    ''' for feature whose start or end happened to be in the replaced sequence, the new index will be such that the replacement is included in the new feature. '''

    def replace_chars(input_sequence, start, length, repl):
        if len(input_sequence) < start + length:
            print("Sequence is too short to replace characters.")
            return

        modified_sequence = input_sequence[:start] + repl + input_sequence[start + length:]

        # Create a dictionary to map original index to new index
        to_map = [i for i in range(len(input_sequence)) if i not in range(start, start + length)]
        index_mapping_c = {i: i if i < start else i + len(repl) - length for i in to_map}
        index_mapping_f = {i: i if i < start else i + len(repl) - length for i in to_map}

        for i in range(start, start + length):
            index_mapping_c[i] = start + len(repl) - 1
            index_mapping_f[i] = start

        return modified_sequence, index_mapping_c, index_mapping_f

    gb = gb_parse0(gb_str)
    # print(json.dumps(gb, indent=2))

    features = feature_parse0(gb['FEATURES'])
    #  print(json.dumps(features, indent=2))

    input_sequence = origin_parse0(gb['ORIGIN'])
    # print(sequence)

    sequence2, index_mapping_c, index_mapping_f = replace_chars(input_sequence, start, length, repl)

    # duplicate sequence2 and expand index_mapping for circular entry annotation
    expanded_sequence2 = sequence2 + sequence2
    expanded_index_mapping_c = dict()
    expanded_index_mapping_f = dict()

    for key, value in index_mapping_c.items():
        expanded_index_mapping_c[key] = value
        expanded_index_mapping_c[key + len(sequence2)] = value

    for key, value in index_mapping_f.items():
        expanded_index_mapping_f[key] = value
        expanded_index_mapping_f[key + len(sequence2)] = value

    features2 = []
    for item in features:
        if not all(key in item for key in ('a', 'b', 'rf')):
            print('feature lacking index')
            continue
        else:
            if item['a'] > item['b']:
                s = item['a'] - 1
                e = item['b'] + len(sequence2) - 1
            else:
                s = item['a'] - 1
                e = item['b'] - 1

            if s in range(start, start + length) and e in range(start, start + length):
                if silence == False:
                    print('one nested feature deleted')
                continue
            else:
                item['a'] = expanded_index_mapping_f[s] + 1
                item['b'] = expanded_index_mapping_c[e] + 1
                if item['a'] == item['b']:
                    print('one feature deleted due to zero length')
                    continue

            if item['a'] > item['b']:
                s = item['a'] - 1
                e = item['b'] + len(sequence2) - 1
            else:
                s = item['a'] - 1
                e = item['b'] - 1

            # update translation
            if 'translation' in item.keys() or item.get("type", '') == "CDS":
                codon_start = item.get('codon_start', 1)

                s2 = expanded_sequence2[s: e + 1]

                if item['rf'] == 'forward':
                    item['translation'] = translate(s2, codon_start=codon_start)
                else:
                    item['translation'] = translate(s2, codon_start=codon_start, forward=False)

            features2.append(item)

    gb["FEATURES"] = feature_to_string(features2)[:-1]  # remove the last \n
    gb["ORIGIN"] = split_and_format_dna(sequence2, chars_per_line=10)

    # Update sequence length and date in LOCUS
    locus = gb["LOCUS"]
    length = str(len(sequence2))
    date = current_date_gb()

    s = locus[12:35].rstrip()
    gb["LOCUS"] = locus[:12] + f'{s[:23].ljust(23)}{length.rjust(5)}' + locus[40:68] + f'{date.rjust(11)}'
    gb2_str = gb_to_string(gb)

    return gb2_str


def gb_edit(gb_str, j0, j1, ins_seq, ins_rf, ins_type=None, ins_annotation=None):
    ''' modification from edit_sequence() '''

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])

    if ins_rf[0] == 'r':
        ins_seq = reverse_complement(ins_seq)
    sequence0 = origin_parse0(gb['ORIGIN'])
    sequence1 = sequence0[:j0] + ins_seq + sequence0[j1:]
    sequence2 = sequence1 + sequence1

    features2 = []
    for item in features:
        item1 = item
        s = item['a'] - 1
        e = item['b']

        # all number before j0 unchanged,
        # all number after j1 + (len(ins)-(j1-j0)
        # number within j0~j1, e -> j0, s -> j0+len(ins_seq)
        # print(j0,j1)
        feature_truncated = False

        if s in range(j0, j1):
            s = j0 + len(ins_seq)
            feature_truncated = True
        elif s >= j1:
            s = s - (j1 - j0) + len(ins_seq)

        if e in range(j0, j1):
            e = j0
            feature_truncated = True
        elif e >= j1:
            e = e - (j1 - j0) + len(ins_seq)

        # if s == j1 and e == j0:
        #     continue

        if s >= e:
            continue

        item1['a'] = s + 1
        item1['b'] = e

        # update translation
        if feature_truncated == False:
            if item.get("type", '') == 'CDS':
                rf = item.get('rf')
                codon_start = item.get('codon_start', 1)
                aa_start_index = item.get('aa_start_index', 1)

                if s > e:
                    e += len(sequence1)
                transl = translate_0220(sequence2[s:e], rf[0], codon_start, aa_start_index)[0]

                item1['translation'] = transl

            features2.append(item1)
    # Update feature and sequence
    gb["FEATURES"] = feature_to_string(features2)
    gb["ORIGIN"] = split_and_format_dna(sequence1, chars_per_line=10)

    # Update gb locus
    length = str(len(sequence1))
    date = current_date_gb()
    locus = gb["LOCUS"]
    locus_name = locus[12:35].rstrip()

    gb["LOCUS"] = locus[:12] + f'{locus_name[:23].ljust(23)}{length.rjust(5)}' + locus[40:64] + f'{date.rjust(15)}'

    # Add new feature for the ins_seq
    gb_str = gb_to_string(gb)

    if ins_type is not None:
        # print('j0',j0)
        # print('j0 + len(ins_seq)',j0 + len(ins_seq))
        gb_str = gb_add_feature(gb_str, j0, j0 + len(ins_seq),
                                ins_rf, ins_type, ins_annotation)

    return gb_str


def filter_feature(gb_str, remove, by="type"):
    """
    Can also remove by 'label'
    remove can be a list or a string
    """

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])

    if isinstance(remove, str):
        remove = [remove]

    features2 = []
    for json_data in features:
        x = json_data.get(by, "")
        if x not in remove:
            features2.append(json_data)

    gb["FEATURES"] = feature_to_string(features2)[:-1]  # remove the last \n

    gb2_str = gb_to_string(gb)

    return gb2_str


def gb_reverse(gb_str):
    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])
    input_sequence = origin_parse0(gb['ORIGIN'])
    sequence2 = reverse_complement(input_sequence).lower()

    index_mapping = dict()
    for i in range(len(input_sequence)):
        index_mapping[i] = len(input_sequence) - i - 1

    features2 = []
    for item in features:
        if not all(key in item for key in ('a', 'b', 'rf')):
            print('feature lacking index')
            continue
        else:
            s = item['a'] - 1
            e = item['b'] - 1
            rf = item['rf']

            item['b'] = index_mapping[s] + 1
            item['a'] = index_mapping[e] + 1

            if rf[0] == 'f':
                item['rf'] = 'reverse'
            else:
                item['rf'] = 'forward'
            features2.append(item)

    gb["FEATURES"] = feature_to_string(features2)[:-1]  # remove the last \n
    gb["ORIGIN"] = split_and_format_dna(sequence2, chars_per_line=10)

    gb2_str = gb_to_string(gb)

    return gb2_str


def gb_reindex(gb_str, origin='gggaaacgcctggtatcttt'):
    ''' The default "gggaaacgcctggtatcttt" is pBR322ori-F, present in pUC, pET, pD871 and pD861 vectors
    in most cases, the orientation of pBR322ori-F is the same as CDS of POI
    '''

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])
    sequence = origin_parse0(gb['ORIGIN']).upper()

    if isinstance(origin, str):
        origin = origin.upper()

        if sequence.find(origin) != -1:
            index0 = sequence.find(origin)

        elif sequence.find(reverse_complement(origin)) != -1:
            gb_str = gb_reverse(gb_str)
            gb = gb_parse0(gb_str)
            features = feature_parse0(gb['FEATURES'])
            sequence = origin_parse0(gb['ORIGIN']).upper()
            index0 = sequence.find(origin)
        else:
            print('substring unfound')
            return

    elif isinstance(origin, int):
        index0 = origin

    index_mapping = dict()
    for i in range(len(sequence)):
        index_mapping[i] = (i - index0) % len(sequence)

    features2 = []
    for item in features:
        if not all(key in item for key in ('a', 'b', 'rf')):
            print('feature lacking index')
            continue
        else:
            s = item['a'] - 1
            e = item['b'] - 1

            item['a'] = index_mapping[s] + 1
            item['b'] = index_mapping[e] + 1

            features2.append(item)

    sequence2 = sequence[index0:] + sequence[:index0]
    gb["FEATURES"] = feature_to_string(features2)[:-1]  # remove the last \n
    gb["ORIGIN"] = split_and_format_dna(sequence2.lower(), chars_per_line=10)

    gb2_str = gb_to_string(gb)

    return gb2_str


def gb_sorted_feature(gb_str):
    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])

    # sorted_features = sorted(features, key=lambda d: (d['type'],d['a'], d['rf']), reverse = True)
    sorted_features = sorted(features, key=lambda d: (d['a'], d['type'], d['rf']))
    gb["FEATURES"] = feature_to_string(sorted_features)[:-1]  # remove the last \n

    gb2_str = gb_to_string(gb)

    return gb2_str


def gb_filter_feature_by_index(gb_str, f_keep=None, f_remove=None):
    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])

    if f_keep is None and f_remove is None:
        print('please specify either feature keep or feature remove')
    elif f_keep is not None:
        features = [features[i] for i in f_keep]
    elif f_remove is not None:
        features = [features[i] for i in range(len(features)) if i not in f_remove]

    gb["FEATURES"] = feature_to_string(features)[:-1]  # remove the last \n
    gb2_str = gb_to_string(gb)
    return gb2_str


def gb_add_feature(gb_str, s, e, rf, type='misc_feature', annotation='', color=None):
    ''' annotations can be either a string or a dict'''

    type = type.lstrip()
    rf = rf.replace(' ', '')

    # label = label.lstrip()

    if type == 'primer':
        color = "#f58a5e"  # primer orange

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])
    sequence = origin_parse0(gb['ORIGIN']).upper()

    if isinstance(annotation, str):
        annotation = {'label': annotation}

    if color is not None:
        annotation.update(
            {'ApEinfo_revcolor': "{}".format(color),
             'ApEinfo_fwdcolor': "{}".format(color)})

    # print(features)
    f1 = dict()
    f1['type'] = type
    f1['rf'] = rf
    f1['a'] = s + 1
    f1['b'] = e
    f1['partial_l'] = False
    f1['partial_r'] = False
    f1.update(annotation)

    if type == 'CDS':
        codon_start = annotation.get('codon_start', 1)
        aa_start_index = annotation.get('aa_start_index', 1)
        # print('here', sequence[s:e])
        s0, s1, s2, s3, s4, s5 = translate_0220(sequence[s:e], rf[0], codon_start, aa_start_index)
        f1.update({'translation': s0})

    features.append(f1)

    gb["FEATURES"] = feature_to_string(features)[:-1]  # remove the last \n

    gb2_str = gb_to_string(gb)
    return gb2_str


def extract_gb_elements(gb_str, header='DEFINITION'):
    header = header.replace(' ', '').upper()

    gb = gb_parse0(gb_str)
    a = gb.get(header, '')

    if isinstance(a, str):
        a = a.split('\n')
    elif isinstance(a, list):
        a = [x.replace(' ' * 12, '') for x in a]

    if header == 'DEFINITION':
        a = ''.join([x[12:] for x in a])
    else:
        a = '\n'.join([x[12:] for x in a])

    return a


def overwrite_gb_elements(gb_str, new_text, header='DEFINITION'):
    header = header.replace(' ', '').upper()
    gb = gb_parse0(gb_str)

    a = new_text.split('\n')
    a = [' ' * 12 + x for x in a]

    first_line = header.ljust(12, ' ') + a[0][12:]
    a[0] = first_line

    a = '\n'.join(a)

    gb[header] = a

    gb_str = gb_to_string(gb)
    return gb_str


def gb_rename_locus(gb_str, new_locus_name):
    gb = gb_parse0(gb_str)
    locus = gb["LOCUS"]

    gb["LOCUS"] = locus[:12] + f'{new_locus_name[:23].ljust(23)}' + locus[35:]
    gb2_str = gb_to_string(gb)

    return gb2_str


def output_gb(gb_str, new_locus_name, new_definition=None):
    ''' if new_locus_name = None, use original locus name
    if new_locus_name = "", use original locus name with suffix
    '''
    gb = gb_parse0(gb_str)
    locus = gb["LOCUS"]
    sequence = origin_parse0(gb['ORIGIN'])
    length = str(len(sequence))

    date = current_date_gb()

    if new_locus_name is None:
        new_locus_name = locus[12:35].rstrip()

    gb["LOCUS"] = locus[:12] + f'{new_locus_name[:23].ljust(23)}{length.rjust(5)}' + locus[40:64] + f'{date.rjust(15)}'

    gb_str = gb_to_string(gb)

    if new_definition is not None:
        gb_str = overwrite_gb_elements(gb_str, new_definition, header='DEFINITION')

    Output_text(gb_str, new_locus_name, 'gb')

    return gb_str


def remove_primer_feature_for_gb_in_a_folder():
    t = os.listdir()
    t = [x for x in t if x.endswith('.gb')]
    # print(t)
    for initial_filename in t:
        # Read and Modify the initial gb file such that locus name = filename
        gb_str = Read_gb(initial_filename, False, True)
        print('overwrite: ', initial_filename)
        # Filter annotations/features
        gb_str = filter_feature(gb_str, remove='primer', by='type')

        output_gb(gb_str, None)


def edit_sequence_for_gb_in_a_folder_copy(target_seq, new_seq, ins_type=None, ins_annotation=None):
    #
    '''only the first & forward & sequence occurrence would be detected
     if two "|" characters in target_seq, it will be translated as "preceding_seq|target_seq|tailing_seq"  and
      only the target_seq will be replaced'''

    target_seq = target_seq.replace(' ', '').upper()
    if target_seq.count('|') == 2:
        a0, a1, a2 = target_seq.split('|')
        a0, a1, a2 = len(a0), len(a1), len(a2)
        search = target_seq.replace('|', '').upper()
    elif '|' in target_seq:
        return
    else:
        a0, a1, a2 = 0, len(target_seq), 0
        search = target_seq.upper()

    t = os.listdir()
    t = [x for x in t if x.endswith('.gb')]

    for initial_filename in t:

        gb_str = Read_gb(initial_filename)

        gb = gb_parse0(gb_str)

        sequence = origin_parse0(gb['ORIGIN']).upper()

        sequence2 = sequence + sequence

        if sequence2.find(search) != -1:

            j0 = sequence2.find(search) + a0
            j1 = j0 + a1

            if j1 > len(sequence):
                continue

            print('Edit file: ', initial_filename)
            ins_seq = new_seq
            gb_str = gb_edit(gb_str, j0, j1, ins_seq, 'f', ins_type, ins_annotation)
            output_gb(gb_str, None)
    return


def edit_sequence_for_gb_in_a_folder(target_seq, new_seq, ins_type=None, ins_annotation=None):
    """
    If there are two '|' characters in target_seq, it will be interpreted as "preceding_seq|target_seq|tailing_seq". Only the target_seq will be replaced
    """

    def process_target_seq(target_seq0, rf='f'):

        target_seq = target_seq0.replace(' ', '').upper()

        if rf == 'r':
            target_seq = reverse_complement(target_seq)

        if target_seq.count('|') == 2:
            a0, a1, a2 = target_seq.split('|')
            a0, a1, a2 = len(a0), len(a1), len(a2)
            search = target_seq.replace('|', '').upper()
        else:
            a0, a1, a2 = 0, len(target_seq), 0
            search = target_seq.upper()

        return search, a0, a1, a2

    t = os.listdir()
    t = [x for x in t if x.endswith('.gb')]

    for initial_filename in t:

        gb_str = Read_gb(initial_filename, False, True)

        gb = gb_parse0(gb_str)

        sequence = origin_parse0(gb['ORIGIN']).upper()

        sequence2 = sequence + sequence

        edit_status = False

        for rf in ['f', 'r']:
            search, a0, a1, a2 = process_target_seq(target_seq, rf)
            curser = 0
            subseq = sequence2[curser:]

            while (subseq.find(search) != -1) & (curser < len(sequence)):
                j0 = curser + subseq.find(search) + a0
                if j0 > len(sequence):
                    break
                j1 = j0 + a1
                ins_seq = new_seq
                gb_str = gb_edit(gb_str, j0, j1, ins_seq, rf, ins_type, ins_annotation)

                curser = j1
                subseq = sequence2[curser:]
                edit_status = True

        if edit_status == True:
            print('Edit file: ', initial_filename)
            output_gb(gb_str, None)
    return


def add_feature_for_gb_in_a_folder(target_seq, type, annotation):
    ''' if two "|" characters in target_seq, it will be translated as "preceding_seq|target_seq|tailing_seq"  '''

    target_seq = target_seq.replace(' ', '').upper()

    if target_seq.count('|') == 2:

        a0, a1, a2 = target_seq.split('|')
        a0, a1, a2 = len(a0), len(a1), len(a2)
        search = target_seq.replace('|', '').upper()

    elif '|' in target_seq:
        return

    else:
        a0, a1, a2 = 0, len(target_seq), 0
        search_f = target_seq.upper()
        search_rc = reverse_complement(search_f)

    t = os.listdir()
    t = [x for x in t if x.endswith('.gb')]

    search = search_f
    for initial_filename in t:
        # Read and Modify the initial gb file such that locus name = filename
        gb_str = Read_gb(initial_filename, False, True)

        gb = gb_parse0(gb_str)
        # features = feature_parse0(gb['FEATURES'])
        sequence = origin_parse0(gb['ORIGIN']).upper()

        sequence2 = sequence + sequence

        if sequence2.find(search) != -1:

            j0 = sequence2.find(search) + a0
            j1 = j0 + a1

            if j1 > len(sequence):
                continue

            print('Feature added to file: ', initial_filename)

            gb_str = gb_add_feature(gb_str, j0, j1, 'f', type, annotation)
            output_gb(gb_str, None)

    search = search_rc
    for initial_filename in t:
        # Read and Modify the initial gb file such that locus name = filename
        gb_str = Read_gb(initial_filename, False, True)

        gb = gb_parse0(gb_str)
        # features = feature_parse0(gb['FEATURES'])
        sequence = origin_parse0(gb['ORIGIN']).upper()

        sequence2 = sequence + sequence

        if sequence2.find(search) != -1:

            j0 = sequence2.find(search) + a0
            j1 = j0 + a1

            if j1 > len(sequence):
                continue

            print('Feature added to file: ', initial_filename)

            gb_str = gb_add_feature(gb_str, j0, j1, 'r', type, annotation)
            output_gb(gb_str, None)

    return


def edit_definition_for_gb_in_a_folder(guiding_file='name_definition.csv'):
    t = os.listdir()
    t = [x for x in t if x.endswith('.gb')]

    df = pd.read_csv(guiding_file)

    dict1 = dict(zip(df['Name'], df['Definition']))
    # print(dict1)

    for initial_filename in t:
        # Read and Modify the initial gb file such that locus name = filename
        gb_str = Read_gb(initial_filename, False, True)
        gb = gb_parse0(gb_str)

        locus = extract_gb_locus(gb_str)

        if locus in dict1.keys():
            definition1 = dict1[locus]
            print('File modified:', initial_filename)
            gb_str = overwrite_gb_elements(gb_str, definition1, header='DEFINITION')
            output_gb(gb_str, None)
    return


def string_replace_for_gb_in_a_folder(target_str, replacement_str):
    t = os.listdir()
    t = [x for x in t if x.endswith('.gb')]

    for initial_filename in t:
        # Read and Modify the initial gb file such that locus name = filename
        gb_str = Read_gb(initial_filename, False, True)

        if target_str in gb_str:
            gb_str = gb_str.replace(target_str, replacement_str)
            print('String replacement to file: ', initial_filename)

        output_gb(gb_str, None)
    return


def Find_nt_index_of_aa_0227(gb_str, target_aa_ind, feature_select=None,
                             aa_start_index=1, neighbor=0,
                             print_inds=False):
    ''' feature_select can be either a int (match the index of a feature) or a str (match the label of a feature).
    will display the gb in the target region +/- 100 nt
    target_aa_ind has to be an int or a range

    target_aa_ind can be an int, a range, or a list of int/range/list
    '''

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])
    sequence = origin_parse0(gb['ORIGIN']).lower()
    feat = retrieve_feature_0330(gb_str, feature_select)

    s = feat['a'] - 1
    e = feat['b']

    if isinstance(target_aa_ind, int):
        target_aa_ind = [target_aa_ind]
    elif isinstance(target_aa_ind, list):
        a2 = []
        for x in target_aa_ind:
            if isinstance(x, int):
                a2.append(x)
            elif isinstance(x, list):
                a2 += x
            elif isinstance(x, range):
                a2 += list(x)
        target_aa_ind = a2

    target_nt_ind = []

    for aa_ind in target_aa_ind:
        if feat['rf'][0] == 'f':
            x = (aa_ind - aa_start_index) * 3 + s
            nt_ind = range(x, x + 3)
        else:
            x = (aa_ind - aa_start_index) * (-3) + e
            nt_ind = range(x - 3, x)
        target_nt_ind.append(nt_ind)

    flattened = [num for r in target_nt_ind for num in r]
    target_nt_ind_span = range(min(flattened), max(flattened) + 1)
    target_nt_ind_island = group_integers_within_distance(flattened, 1)[1]

    ind0 = max(min(target_nt_ind_span) - neighbor, 0)
    ind1 = min(len(sequence), max(target_nt_ind_span) + 1 + neighbor)

    # print('feature select', feature_select)

    if print_inds == True:
        print('target_aa_ind', target_aa_ind)
        print('target_nt_ind_span', target_nt_ind_span)
        print('target_nt_ind_island', target_nt_ind_island)

    # if print_region == True:
    #     print(region_display)

    return target_nt_ind_island, target_nt_ind_span, None


def gb_display(gb_str,
               display_range=None,
               feature_select=None,
               type_filter=None,
               show_overlapped_feature=True,
               automatic_feature_sort=False, display_feature_list=False, to_upper_case=False
               ):
    # abbr = False;
    print_display = True;
    output_display = False;
    max_annotate_entry = 5;
    display_instruction = False

    global ure_incl1

    def Create_aa_ruler(cds_length, nt_start, rf='f', aa_start=1):
        dot_ruler = ''
        for i in range(aa_start, cds_length // 3 + 1, 5):
            dot_ruler += '.' + ' ' * 5 + '.' + ' ' * 8
        dot_ruler = dot_ruler[: cds_length]

        if rf[0] == 'f':

            nt_ruler = ''
            for i in range(nt_start, nt_start + cds_length, 15):
                nt_ruler += f'{str(i).ljust(15)}'
            nt_ruler = nt_ruler[: cds_length + 3]

            aa_ruler = ''
            for i in range(aa_start, cds_length // 3 + 1, 5):
                aa_ruler += f'{str(i).ljust(15)}'
            aa_ruler = aa_ruler[: cds_length + 3]

        else:

            nt_ruler = ''
            for i in range(nt_start, nt_start - cds_length, -15):
                nt_ruler = f'{str(i).rjust(15)}' + nt_ruler
            nt_ruler = nt_ruler[-cds_length:]

            aa_ruler = ''
            for i in range(aa_start, cds_length // 3 + 1, 5):
                aa_ruler = f'{str(i).rjust(15)}' + aa_ruler
            aa_ruler = aa_ruler[-cds_length:]
            dot_ruler = dot_ruler[::-1]

        return nt_ruler, aa_ruler, dot_ruler

    def Create_ruler(x):
        ''' x is the total length of the sequence '''
        import math
        # calculate number of digits
        row_number = math.ceil(math.log10(x))  # rows of ruler
        Ruler = []
        for i in range(row_number):
            if i == 0:
                # unit_string = '0 2 4 6 8 '
                unit_string = '0    5    '
                repeated_string = unit_string * (x // len(unit_string) + 1)
                repeated_string = repeated_string[:x]
                Ruler.append(repeated_string)
            else:
                unit_string = ''
                curser = 0
                for j in range(10):
                    space9 = ' ' * 9
                    while curser < (j + 1) * 10 ** i:
                        unit_string += '{}{}'.format(j, space9)
                        curser = len(unit_string)

                repeated_string = unit_string * (x // len(unit_string) + 1)
                repeated_string = repeated_string[:x]
                Ruler.append(repeated_string)

        Ruler = Ruler[::-1]
        ruler_str = '\n'.join(Ruler)

        unit_string = '|    |    '
        repeated_string = unit_string * (x // len(unit_string) + 1)
        ruler_line = repeated_string[:x]

        unit_string = '|....|....'
        repeated_string = unit_string * (x // len(unit_string) + 1)
        ruler_dot = repeated_string[:x]

        return ruler_str, ruler_line, ruler_dot

    def have_shared_element(r1, l2):
        r2 = range(l2[0], l2[1])
        checker = [x for x in r1 if x in r2]
        return len(checker) > 0

    def nested_element(r1, l2):
        r2 = range(l2[0], l2[1])
        # print(r1, r2)
        checker = (min(r1) >= min(r2) - 3 and max(r1) <= max(r2) + 3)
        return checker

    def reformat_reverse_translate_0220(result):
        s0, s1, s2, s3, s4, s5 = result

        s2_rev = []
        for line in s2:
            s2_rev.append(line[::-1][3:])

        s3_rev = []
        for line in s3:
            line0 = line[::-1] + ' ' * 3
            line1 = line0
            # for i in range(0, len(line0), 3):
            for i in range(len(line0) - 3, 0, -3):
                if line0[i] != ' ':
                    c = line0[i - 1:i + 2]
                    c = c[::-1]
                    line1 = line1[:i - 1] + ' ' * 3 + line1[i + 2] + c + line1[i + 6:]

            s3_rev.append(line1[3:])
            # print(s3_rev)

        aa_start = int(s4[:15].strip())
        sequence_length = len(s0.rstrip()) * 3

        s4_rev = ''
        for i in range(aa_start, sequence_length // 3, 5):
            s4_rev = f'{str(i).rjust(15)}' + s4_rev

        s4_rev = s4_rev[-sequence_length:]
        s5_rev = s5[::-1]

        return s2_rev, s3_rev, s4_rev, s5_rev

    if automatic_feature_sort == True:
        gb_str = gb_sorted_feature(gb_str)

    if feature_select is not None:
        feat = retrieve_feature(gb_str, feature_select=feature_select)
        display_range = (feat['a'] - 1, feat['b'])
        print(f'\n\ndisplay_range {display_range}')

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])
    sequence = origin_parse0(gb['ORIGIN'])
    if to_upper_case == True:
        sequence = sequence.upper()
    locus = gb["LOCUS"]
    locus_name = locus[12:35].rstrip()

    ruler_str, ruler_line, ruler_dot = Create_ruler(len(sequence))

    Feature_draw = []
    Description = []
    Occupy = []
    feature_count = 0
    for item in features:

        s = item['a'] - 1
        e = item['b']
        rf = item['rf']
        type = item['type']

        seq_fwd = sequence[s:e]
        seq_rev = reverse_complement(seq_fwd, reverse=False)  # 3' to 5', lower case
        seq_revcomp = reverse_complement(seq_fwd)

        # Per feature, write Type and Annotations for abbr display & FULL RECORD
        annotate = []
        keys_not = ['type', 'rf', 'a', 'b', 'partial_l', 'partial_r',
                    'translation', 'codon_start', 'note', 'ApEinfo_revcolor', 'ApEinfo_fwdcolor']

        if e - s > 10:
            abbr = False
        else:
            abbr = True

        for key in [x for x in item.keys() if x not in keys_not]:
            # # print('key',key)
            # value = item[key].replace('"', '').replace("'", "")
            # annotate.append(value)
            # #
            if isinstance(item[key], list):
                item[key] = '; '.join(item[key])

            if isinstance(item[key], str):
                value = item[key].replace('"', '').replace("'", "").rstrip()
            else:
                value = item[key]
            annotate.append(value)

        annotate = list(set(annotate))
        # annotate = sorted(annotate, key=len)

        feat = []

        annotate_text_abbr = ''
        if len(annotate) > 0:
            for i in range(min(len(annotate), 1)):
                a = annotate[i]
                annotate_text_abbr += f'{a}'

        annotate_text = f'"{type}"'
        if len(annotate) > 0:
            for i in range(min(len(annotate), max_annotate_entry)):
                a = annotate[i]
                annotate_text += f', {a}'

        if abbr == True:
            feat.append(' ' * s + '{}. {}'.format(feature_count, annotate_text_abbr))
        else:
            feat.append(' ' * s + '{}. {}'.format(feature_count, annotate_text))

        # Per feature, write IND_DESCRIPTION, (LENGTH) for abbr display & FULL RECORD

        ind_description = 'range({},{}), len {}, {}'.format(s, e, e - s, rf[0])
        ind_description_abbr = '({},{})'.format(s, e)
        if abbr == True:
            feat.append(' ' * s + ind_description_abbr)
        else:
            feat.append(' ' * s + ind_description)

        # Per feature, write Sequence with Ruler_dot for display
        if rf[0] == 'f':
            feat.append(' ' * s + seq_fwd)
            feat.append(' ' * s + ruler_dot.replace('|', '>')[s: s + len(seq_fwd)])
        else:
            feat.append(' ' * s + ruler_dot.replace('|', '<')[s: s + len(seq_fwd)])
            feat.append(' ' * s + seq_rev)

        # Per feature, write Translations with AA ruler
        if type == 'CDS' and e - s > 3:
            codon_start = item.get('codon_start', 1)
            aa_start_index = item.get('aa_start_index', 1)
            transl = translate_0220(sequence[s:e], rf[0], codon_start, aa_start_index)
            s0, s1, s2, s3, s4, s5 = transl

            if rf[0] == 'f':
                nt_ruler, aa_ruler, dot_ruler = Create_aa_ruler(e - s, s, 'f', aa_start_index)
                feat.append(' ' * s + nt_ruler)
                feat.append(' ' * s + aa_ruler)
                feat.append(' ' * s + dot_ruler)

                for line in s3:
                    feat.append(' ' * s + line)

            else:
                # print(transl)
                s2_rev, s3_rev, s4_rev, s5_rev = reformat_reverse_translate_0220(transl)

                nt_ruler, aa_ruler, dot_ruler = Create_aa_ruler(e - s, e - 1, 'r', aa_start_index)
                feat.append(' ' * s + nt_ruler)
                feat.append(' ' * s + aa_ruler)
                feat.append(' ' * s + dot_ruler)

                for line in s3_rev:
                    feat.append(' ' * s + line)

        # Per feature, buffer left & write with ruler_line
        ind1 = max([len(x) for x in feat])
        feat2 = []

        for x in feat:
            feat2.append(ruler_line[:s] + f'{x[s:ind1].ljust(ind1 - s)}' + ruler_line[ind1:])

        Feature_draw.append(feat2)
        Occupy.append(range(s, ind1))

        # Per feature, FULL RECORD

        descrip = [str(feature_count), annotate_text]
        if rf[0] == 'f':
            descrip.append('forward, {}'.format(ind_description))
            descrip.append(seq_fwd)
        else:
            descrip.append('revcomp, {}'.format(ind_description))
            descrip.append(seq_revcomp)
        if type == 'CDS':
            if 'x' in s0:
                descrip.append('transl, deg. = x')
            else:
                descrip.append('transl')
            descrip.append(s0)

            if s1 != s0:
                descrip.append('transl, [deg. expanded]')
                descrip.append(s1)

        Description.append(descrip)
        feature_count += 1

    # create feature_incl by type and region
    feature_incl0 = [True] * len(features)
    if type_filter is not None:
        if isinstance(type_filter, str):
            type_filter = [type_filter]
        feature_incl0 = []
        for i in range(len(features)):
            if features[i]['type'] in type_filter:
                feature_incl0.append(True)
            else:
                feature_incl0.append(False)

    if display_range is None:  # a range
        display_range = range(len(sequence))
        feature_incl1 = [True] * len(features)
    else:
        feature_incl1 = []
        for i in range(len(features)):
            if show_overlapped_feature == True:
                feature_incl1.append(have_shared_element(Occupy[i], display_range))
            else:
                feature_incl1.append(nested_element(Occupy[i], display_range))

    feature_incl = [a and b for a, b in zip(feature_incl0, feature_incl1)]

    # Zip  [Feature_draw, Occupy, features, feature_ind, feature_incl] and sort
    feature_ind = list(range(len(features)))
    zipped_lists = list(zip(Feature_draw, Occupy, feature_ind, feature_incl))
    sorted_zipped_lists = sorted(zipped_lists, key=lambda element: (len(element[0]), min(element[1])))
    sorted_Feature_draw, sorted_Occupy, sorted_feature_ind, sorted_feature_incl = zip(*sorted_zipped_lists)

    # Create empty channels
    channel = []
    for i in range(feature_count):
        channel.append([])

    # Allot channels, by sorted linked list, those filtered out will be -1
    sorted_feature_assign = []
    from itertools import chain
    for i in range(len(features)):
        if sorted_feature_incl[i] == False:
            sorted_feature_assign.append(-1)
        else:
            r = sorted_Occupy[i]
            for i in range(len(channel)):
                flattened_list = list(chain.from_iterable(r for r in channel[i]))
                r_expand = range(min(r) - 3, max(r) + 1)
                overlap = [x for x in r_expand if x in flattened_list]
                if len(overlap) == 0:  # no overlap, ascribe to the channel
                    sorted_feature_assign.append(i)
                    channel[i].append(r)
                    break

    # reverse the sort, along with feature_assign creation
    zipped_lists = list(
        zip(sorted_Feature_draw, sorted_Occupy, sorted_feature_ind, sorted_feature_incl, sorted_feature_assign))
    sorted_zipped_lists = sorted(zipped_lists, key=lambda x: x[2])
    Feature_draw, Occupy, feature_ind, feature_incl, feature_assign = zip(*sorted_zipped_lists)

    channel2 = []
    for i in range(max(feature_assign) + 1):
        channel2.append([ruler_line] * 60)

    for i in range(len(features)):
        asi = feature_assign[i]
        if asi != -1:
            ind0 = max(0, min(Occupy[i]))
            ind1 = max(Occupy[i]) + 1

            feat = Feature_draw[i]
            for j in range(len(feat)):
                t0 = channel2[asi][j]
                channel2[asi][j] = t0[:ind0] + feat[j][ind0:ind1] + t0[ind1:]

    # Create channel3
    channel3 = []
    for channel in channel2:
        channel3.append(ruler_line)
        for line in channel:
            if line == ruler_line:
                break
            else:
                channel3.append(line)

    channel3_trim = channel3
    for j in range(0, len(channel3[0]), 5):
        st = 0
        # print(j)
        for i in range(len(channel3) - 1, -1, -1):
            if channel3[i][j] != '|':
                st = i + 1
                break

        for i in range(len(channel3)):
            if i < st:
                channel3_trim[i] = channel3_trim[i]
            else:
                channel3_trim[i] = channel3_trim[i][:j] + ' ' + channel3_trim[i][j + 1:]

    channel3 = channel3_trim

    # OUTPUT display & FULL RECORD
    output_text = ruler_str.split('\n') + [ruler_dot, sequence] + [x for x in channel3]

    # truncate the display to region
    output_text2 = []
    for line in output_text:
        output_text2.append(line[min(display_range):max(display_range)])
    output_text = output_text2

    if display_feature_list == True:
        output_text += [f'\n{"." * 40}Feature list']
        Description2 = []

        for i in range(len(features)):
            if feature_incl[i] == True:
                Description2.append(Description[i])
        Description = Description2

        for d in Description:
            output_text.append('')
            for line in d:
                output_text.append(line)

    output_text = '\n'.join(output_text)

    # Add locus name and instruction text to the top
    header = f"{'=' * 80} Overview\n{gb.get('LOCUS')}\n{gb.get('DEFINITION')}\n"

    if display_instruction == True:
        instruction = f'''{"-" * 60} Instruction
1. Access the file using Windows Notepad
2. Navigate to "Format" > "Font" and choose "Consolas"
3. Under "Format", unselect "Word Wrap"
------------------------------------------------------------ Display
'''
    else:
        instruction = f'{"-" * 60} Display\n'

    output_text = header + instruction + output_text

    if output_display == True:
        Output_text(output_text, f'{locus_name}_display')
    if print_display == True:
        print(output_text)
        print('\n/// END of display\n')

    return output_text


def retrieve_feature(gb_str, feature_select=None, silence=True):
    ''' feature_select can be either a int (match the index of a feature) or a str (match the any of the annotations of a feature).
       '''
    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])

    feat = None
    if isinstance(feature_select, int):
        feat = features[feature_select]
        return feat

    elif isinstance(feature_select, str):
        for i in range(len(features)):
            item = features[i]
            annotate = []
            keys_not = ['type', 'rf', 'a', 'b', 'partial_l', 'partial_r',
                        'translation', 'codon_start', 'note', 'ApEinfo_revcolor', 'ApEinfo_fwdcolor']

            for key in [x for x in item.keys() if x not in keys_not]:
                value = item[key].replace('"', '').replace("'", "").rstrip()
                annotate.append(value)

            # if exact_string_match == True:
            if feature_select in [x for x in annotate]:
                feat = item
                if silence == False:
                    print('feature_select by string')
                return feat
            # else:
            #     for x in annotate:
            #         if feature_select.lower() in x.lower():
            #             feat = item
            #             print('feature_select by string')
            #             return feat

    if feat is None:
        if silence == False:
            print('feature select by longest CDS')
        # find the longest CDS among the features
        cds = [item for item in features if item.get('type', '').upper() == 'CDS']
        if len(cds) == 0:
            print('please specify feature')
            return
        else:
            my_list = [(item['b'] - item['a']) for item in cds]
            max_index = my_list.index(max(my_list))
            feat = cds[max_index]
            return feat
    return


def retrieve_feature_0330(gb_str, feature_select):
    ''' feature_select has to be an exact string match  '''
    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])

    feat = None
    for i in range(len(features)):
        item = features[i]
        annotate = []
        keys_not = ['type', 'rf', 'a', 'b', 'partial_l', 'partial_r',
                    'translation', 'codon_start', 'note', 'ApEinfo_revcolor', 'ApEinfo_fwdcolor']

        for key in [x for x in item.keys() if x not in keys_not]:

            if isinstance(item[key], list):
                item[key] = '; '.join(item[key])

            if isinstance(item[key], str):
                value = item[key].replace('"', '').replace("'", "").rstrip()
            else:
                value = item[key]
            annotate.append(value)

        if feature_select in [x for x in annotate]:
            feat = item
            return feat

    return None


def gb_edit_variation(gb_str, feature_select, mutation_codon_no, replacement_codon,
                      plasmid_list=None, plasmid_prefix=None):
    '''
    mutation_codon_no : int or a list of int.
    replacement_codon: string or a list of string.
    e.g.
    mutation_codon_no = [10, 12] ; replacement_codon = ['tag', 'atg']
    return all four combinations
    '''

    replacement_note = None
    codon_table, *_ = extract_kazusa()
    triplet_to_aa = dict(zip(codon_table['triplet'], codon_table['amino acid']))

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])
    sequence = origin_parse0(gb['ORIGIN']).lower()
    sequence2 = sequence + sequence
    feat = retrieve_feature(gb_str, feature_select)

    locus = gb["LOCUS"]

    if feat['rf'][0] == 'r':  # make the target feature forward
        gb_str = gb_reverse(gb_str)

        gb = gb_parse0(gb_str)
        features = feature_parse0(gb['FEATURES'])
        sequence = origin_parse0(gb['ORIGIN']).lower()
        sequence2 = sequence + sequence
        feat = retrieve_feature(gb_str, feature_select)

    definition0 = extract_gb_elements(gb_str, header='DEFINITION')

    s = feat['a'] - 1
    e = feat['b']
    rf = feat['rf']
    codon_start = feat.get('codon_start', 1)
    aa_start_index = feat.get('aa_start_index', 1)
    cds_sequence = sequence2[s:e]
    peptide_sequence = translate_0220(cds_sequence, rf=rf, codon_start=codon_start, aa_start=aa_start_index)[0]

    if isinstance(mutation_codon_no, int):
        mutation_codon_no = [mutation_codon_no]

    if isinstance(replacement_codon, str):
        replacement_codon = [replacement_codon]

    new_gb_str = []
    new_mutation_site = []
    new_locus_name = []
    new_definition = []
    for target_aa_ind in mutation_codon_no:
        for replacement in replacement_codon:

            if isinstance(target_aa_ind, range):
                repl_len = len(target_aa_ind)
                aa_ind0 = min(target_aa_ind)
            elif isinstance(target_aa_ind, int) or isinstance(target_aa_ind, float):
                if target_aa_ind - int(target_aa_ind) == 0:
                    repl_len = 1
                    aa_ind0 = int(target_aa_ind)
                else:
                    repl_len = 0
                    target_aa_ind = int(target_aa_ind) + 1
                    aa_ind0 = target_aa_ind

            else:
                print('!! mutation_codon_no shall be a list containing either range, int, or float ')
                return

            mutation_site = []
            gb_str2 = gb_str

            target_nt_ind = Find_nt_index_of_aa_0227(gb_str, target_aa_ind,
                                                     feature_select=feature_select,
                                                     neighbor=0, print_inds=False)[0][0]
            # print(' target_nt_ind',  target_nt_ind)
            # print('replacement', replacement)

            if replacement_note is None and len(replacement) == repl_len * 3:  # without indel
                descrip1 = ''
                for j in range(repl_len):
                    aa0 = peptide_sequence[aa_ind0 + j - aa_start_index]
                    codon = replacement[j * 3:j * 3 + 3].upper()
                    transl = triplet_to_aa[codon]
                    descrip1 += '_{}{}{}'.format(aa0, aa_ind0 + j, transl)
            else:  # there's indel
                if replacement_note is None and len(replacement) % 3 == 0:  # aa
                    replacement_note = ''
                    # actual_repl_len = int(len(replacement)/3)
                    if len(replacement) > 0:
                        for j in range(int(len(replacement) / 3)):
                            codon = replacement[j * 3:j * 3 + 3]
                            codon = codon.upper()
                            transl = triplet_to_aa[codon]
                            replacement_note += transl
                    else:
                        replacement_note = 'del'
                else:  # dna
                    replacement_note = replacement.lower()

                if repl_len > 1:
                    descrip1 = '_{}_{}delins{}'.format(aa_ind0, aa_ind0 + repl_len - 1, replacement_note).replace(
                        'delinsdel', 'del')
                elif repl_len == 1:
                    descrip1 = '_{}{}{}'.format(peptide_sequence[aa_ind0 - aa_start_index], aa_ind0, replacement_note)
                elif repl_len == 0:
                    descrip1 = '_{}_{}ins{}'.format(aa_ind0 - 1, aa_ind0, replacement_note)

            # write plasmid detail in (definition)
            definition = definition0 + descrip1
            definition = reorder_mutations(definition)

            gb_str2 = overwrite_gb_elements(gb_str2, new_text=definition, header='DEFINITION')

            if len(replacement) > 0:
                mutation_site.append(range(min(target_nt_ind), min(target_nt_ind) + len(replacement)))
            else:
                mutation_site.append(range(min(target_nt_ind), min(target_nt_ind) + 1))

            # write new name in (locus)
            if plasmid_list is not None and plasmid_prefix is not None:
                j0 = 1 + find_latest_int([x.get('Name', '') for x in plasmid_list], plasmid_prefix)
                locus_name = '{}{}'.format(plasmid_prefix, str(j0).rjust(3, '0'))
                gb_str2 = gb_rename_locus(gb_str2, locus_name)

                # update plasmid_list
                plasmid_list.append({'Name': locus_name,
                                     'Definition': definition})
            else:
                locus_name = ''

            # Edit seqence
            if repl_len >= 1:
                j0 = min(target_nt_ind)
                j1 = max(target_nt_ind) + 1
            elif repl_len == 0:
                j0 = min(target_nt_ind)
                j1 = j0

            if len(replacement) > 0:
                gb_str2 = gb_edit(gb_str2, j0, j1, replacement, 'f', ins_type='variation',
                                  ins_annotation={'label': descrip1, 'ApEinfo_revcolor': "#b1ff67",
                                                  'ApEinfo_fwdcolor': "#b1ff67"})
            else:
                gb_str2 = gb_edit(gb_str2, j0, j1, replacement, 'f', ins_type=None)
                gb_str2 = gb_add_feature(gb_str2, j0, j0 + 1, 'f',
                                         type='variation',
                                         annotation={'label': descrip1, 'ApEinfo_revcolor': "#b1ff67",
                                                     'ApEinfo_fwdcolor': "#b1ff67"})

            new_gb_str.append(gb_str2)
            new_mutation_site.append(mutation_site)
            new_locus_name.append(locus_name)
            new_definition.append(definition)

    return new_gb_str, new_mutation_site, new_locus_name, new_definition, plasmid_list


def gb_edit_by_notations(gb_str, feature_select, notations, species,
                         plasmid_list=None, plasmid_prefix=None):
    '''
     notations are a list of notation where each notation is generated by seq_to_notation(ref, seq), for example,
     something like this "_R13A_32del_50~51insA_67~70del_84~85insAGAR_97~101delinsFINELLA" is a single notation

     '''

    codon_table, *_ = extract_kazusa()
    triplet_to_aa = dict(zip(codon_table['triplet'], codon_table['amino acid']))

    gb = gb_parse0(gb_str)
    features = feature_parse0(gb['FEATURES'])
    sequence = origin_parse0(gb['ORIGIN']).lower()
    sequence2 = sequence + sequence
    feat = retrieve_feature(gb_str, feature_select)

    locus = gb["LOCUS"]

    if feat['rf'][0] == 'r':  # make the target feature forward
        gb_str = gb_reverse(gb_str)

        gb = gb_parse0(gb_str)
        features = feature_parse0(gb['FEATURES'])
        sequence = origin_parse0(gb['ORIGIN']).lower()
        sequence2 = sequence + sequence
        feat = retrieve_feature(gb_str, feature_select)

    definition0 = extract_gb_elements(gb_str, header='DEFINITION')

    s = feat['a'] - 1
    e = feat['b']
    rf = feat['rf']
    codon_start = feat.get('codon_start', 1)
    aa_start_index = feat.get('aa_start_index', 1)
    cds_sequence = sequence2[s:e]
    peptide_sequence = translate_0220(cds_sequence, rf=rf, codon_start=codon_start, aa_start=aa_start_index)[0]

    new_gb_str = []
    new_mutation_site = []
    new_locus_name = []
    new_definition = []

    for notation in notations:
        gb_str2 = gb_str

        mutation_site = []
        decode, t = decode_notation(notation)

        for i in range(len(decode)):
            entry = decode[i]
            label = t[i]

            if entry[0] == 'sub':
                _, pos, new = entry

                target_nt_ind = Find_nt_index_of_aa_0227(gb_str, target_aa_ind=pos,
                                                         feature_select=feature_select,
                                                         neighbor=0, print_inds=False)[0][0]

                j0 = min(target_nt_ind)
                j1 = max(target_nt_ind) + 1

                ins_seq = codon_optimization(new, species=species, preceding_triplet=sequence2[j0 - 3:j0],
                                             tailing_triplet=sequence2[j1:j1 + 3])
                gb_str2 = gb_edit(gb_str2, j0, j1, ins_seq, 'f', ins_type='variation',
                                  ins_annotation={'label': label, 'ApEinfo_revcolor': "#b1ff67",
                                                  'ApEinfo_fwdcolor': "#b1ff67"})

                mutation_site += list(range(j0, j1))


            elif entry[0] == 'del':
                _, pos = entry

                target_nt_ind = Find_nt_index_of_aa_0227(gb_str, target_aa_ind=pos,
                                                         feature_select=feature_select,
                                                         neighbor=0, print_inds=False)[0][0]
                j0 = min(target_nt_ind)
                j1 = max(target_nt_ind) + 1

                gb_str2 = gb_edit(gb_str2, j0, j1, '', 'f', ins_type=None)
                gb_str2 = gb_add_feature(gb_str2, j0, j0 + 1, 'f',
                                         type='variation',
                                         annotation={'label': label, 'ApEinfo_revcolor': "#b1ff67",
                                                     'ApEinfo_fwdcolor': "#b1ff67"})

                mutation_site = [x if x < j0 else x - 3 for x in mutation_site]
                mutation_site.append(j0)

            elif entry[0] == 'ins':
                _, pos, new = entry
                pos = int(pos + 0.5)
                target_nt_ind = Find_nt_index_of_aa_0227(gb_str, target_aa_ind=pos,
                                                         feature_select=feature_select,
                                                         neighbor=0, print_inds=False)[0][0]
                j0 = min(target_nt_ind)
                j1 = j0
                ins_seq = codon_optimization(new, species=species, preceding_triplet=sequence2[j0 - 3:j0],
                                             tailing_triplet=sequence2[j1:j1 + 3])  # to
                gb_str2 = gb_edit(gb_str2, j0, j1, ins_seq, 'f', ins_type='variation',
                                  ins_annotation={'label': label, 'ApEinfo_revcolor': "#b1ff67",
                                                  'ApEinfo_fwdcolor': "#b1ff67"})

                mutation_site = [x if x < j0 else x + len(new) * 3 for x in mutation_site]
                mutation_site += list(range(j0, j0 + len(new) * 3))

            elif entry[0] == 'mdel':
                _, pos, pos1 = entry

                target_nt_ind = Find_nt_index_of_aa_0227(gb_str, target_aa_ind=range(pos, pos1 + 1),
                                                         feature_select=feature_select,
                                                         neighbor=0, print_inds=False)[0][0]
                j0 = min(target_nt_ind)
                j1 = max(target_nt_ind) + 1

                gb_str2 = gb_edit(gb_str2, j0, j1, '', 'f', ins_type=None)
                gb_str2 = gb_add_feature(gb_str2, j0, j0 + 1, 'f',
                                         type='variation',
                                         annotation={'label': label, 'ApEinfo_revcolor': "#b1ff67",
                                                     'ApEinfo_fwdcolor': "#b1ff67"})

                mutation_site = [x if x < j0 else x - (j1 - j0) for x in mutation_site]
                mutation_site.append(j0)

            elif entry[0] == 'delins':
                _, pos, pos1, new = entry

                target_nt_ind = Find_nt_index_of_aa_0227(gb_str, target_aa_ind=range(pos, pos1 + 1),
                                                         feature_select=feature_select,
                                                         neighbor=0, print_inds=False)[0][0]
                j0 = min(target_nt_ind)
                j1 = max(target_nt_ind) + 1
                ins_seq = codon_optimization(new, species=species, preceding_triplet=sequence2[j0 - 3:j0],
                                             tailing_triplet=sequence2[j1:j1 + 3])  # to
                gb_str2 = gb_edit(gb_str2, j0, j1, ins_seq, 'f', ins_type='variation',
                                  ins_annotation={'label': label, 'ApEinfo_revcolor': "#b1ff67",
                                                  'ApEinfo_fwdcolor': "#b1ff67"})

                mutation_site = [x if x < j0 else x - (j1 - j0) + len(new) * 3 for x in mutation_site]
                mutation_site += list(range(j0, j0 + len(new) * 3))

        # write plasmid detail in (definition)

        definition = definition0.split(feature_select)[0] + feature_select + notation
        gb_str2 = overwrite_gb_elements(gb_str2, new_text=definition, header='DEFINITION')

        if plasmid_list is not None and plasmid_prefix is not None:
            j0 = 1 + find_latest_int([x.get('Name', '') for x in plasmid_list], plasmid_prefix)
            locus_name = '{}{}'.format(plasmid_prefix, str(j0).rjust(3, '0'))
            gb_str2 = gb_rename_locus(gb_str2, locus_name)

            # update plasmid_list
            plasmid_list.append({'Name': locus_name,
                                 'Definition': definition})
        else:
            locus_name = ''

        mutation_site.sort()
        new_gb_str.append(gb_str2)
        new_mutation_site.append(mutation_site)
        new_locus_name.append(locus_name)
        new_definition.append(definition)

    return new_gb_str, new_mutation_site, new_locus_name, new_definition, plasmid_list


def current_date_gb():
    from datetime import datetime

    # Get the current date
    current_date = datetime.now().date()
    date_string = str(current_date)

    # Parse the input date string
    parsed_date = datetime.strptime(date_string, '%Y-%m-%d')

    # Format the date as a string in the desired format
    formatted_date = parsed_date.strftime('%d-%b-%Y').upper()

    return formatted_date


# general purpose
def check_encode(file_path):
    import chardet
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
        # print(result['encoding'])
    return result['encoding']


def import_oligo_list(oligo_file_path, required_field='Name', exclude=[]):
    # print('oligo_file_path', oligo_file_path)

    encoding = check_encode(oligo_file_path)
    df = pd.read_csv(oligo_file_path, encoding=encoding)

    old_column_names = list(df.columns)

    new_column_names = []

    for x in old_column_names:
        if x == 'Sequence':
            new_column_names.append('Bases')
        else:
            new_column_names.append(x)

    if required_field not in new_column_names:
        print('list incomplete')
        return

    df.columns = new_column_names
    json_string = df.to_json(orient='records')
    oligo_list = json.loads(json_string)
    oligo_list = [x for x in oligo_list if x.get(required_field) is not None]

    oligo_list = [x for x in oligo_list if x.get(required_field) not in exclude]

    # remove blank in bases, for oligo list
    if 'Bases' in new_column_names:
        oligo_list2 = []
        for x in oligo_list:
            x2 = x
            if x2['Bases'] is not None:
                x2['Bases'] = x['Bases'].replace(' ', '')
                oligo_list2.append(x2)
        oligo_list = oligo_list2
    return oligo_list


def export_oligo_list(oligo_list, oligo_file_path):
    def fill_in_list_of_dict(list_of_dict):
        key = []
        for d in list_of_dict:
            key += list(d.keys())
        key = list(set(key))

        l2 = []
        for d in list_of_dict:
            d2 = d
            for k in key:
                if d.get(k) is None:
                    d2[k] = None
            l2.append(d2)
        return l2

    if oligo_list == []:
        return
    data_list = oligo_list
    data_list = fill_in_list_of_dict(oligo_list)
    csv_file_path = oligo_file_path

    if os.path.exists(oligo_file_path):
        encoding = check_encode(oligo_file_path)
    else:
        encoding = 'utf-8'

    import csv
    # Writing the list of dictionaries to a CSV file
    with open(csv_file_path, 'w', encoding=encoding, newline='') as csvfile:
        # Define the CSV writer
        csv_writer = csv.DictWriter(csvfile, fieldnames=data_list[0].keys())

        # Write the header
        csv_writer.writeheader()

        # Write the data
        csv_writer.writerows(data_list)
    return


def Read_text(filepath, encode=''):
    '''Read file '''
    with open(filepath, encoding='utf8') as f1:
        file1 = f1.read()

    return file1


def Output_csv(df, filename='output', index=False):
    df = pd.DataFrame(df)
    df.to_csv('{}.csv'.format(filename), index=index)


def Output_text(text, filename='output', extension='txt', mode='w', encoding='utf-8'):  # version 0724
    with open('{}.{}'.format(filename, extension), mode=mode, encoding=encoding) as w:
        if isinstance(text, str):
            w.write(text)
        elif isinstance(text, list):
            t = [str(x) for x in text]
            w.write('\n'.join(t))


# small def
def to_range(list):
    lst2 = []
    for i in list:
        lst2.append(range(i, i + 1))
    return lst2


def atcg_count(seq):
    seq = seq.upper()
    seq = seq.replace(' ', '')
    print(f'"{seq}"')

    t = list(seq)
    t = ' '.join(t)
    print(f'"{t}"')

    print(f'occurrence:\nA\tT\tC\tG\n{seq.count("A")}\t{seq.count("T")}\t{seq.count("C")}\t{seq.count("G")}')
    print(f'total length: {len(seq)}')
    return


def find_latest_int(list_of_text, prefix):
    # search for the latest primer number
    count = [0]
    for text in list_of_text:
        pattern = re.compile(re.escape(prefix) + r'(\d+)')
        matches = pattern.findall(text)
        if matches:
            match = int(matches[0])
            count.append(match)

    return max(count)


def group_integers_within_distance(lst, n):
    ''' result0 is groupings of integers. result1 expand each group into a continuous segment. the third output is flattened result1'''
    from itertools import chain
    lst.sort()  # Sort the list in ascending order
    result0 = []
    result = []
    # print(lst)

    if len(lst) == 0:
        return [], [], []
    else:
        current_group = [lst[0]]

        for i in range(1, len(lst)):
            if lst[i] - current_group[-1] <= n:
                current_group.append(lst[i])
            else:
                result0.append(current_group.copy())
                result.append(range(min(current_group), max(current_group) + 1))
                current_group = [lst[i]]

        if current_group:
            result0.append(current_group.copy())
            result.append(range(min(current_group), max(current_group) + 1))

        result_range = result
        result_list = list(chain.from_iterable(result))
        return result0, result_range, result_list


def to_json(features):
    return json.dumps({"features": features}, indent=2)


def remove_u(primer0, max_len=None):
    primer0 = primer0.replace('/5deoxyU/', '').replace('/ideoxyU/', '').replace(' ', '')
    primer0 = primer0.upper()
    if max_len is not None:
        primer0 = primer0[:max_len]
    return primer0


def dataframe_to_tab_separated_string(df, tab_size=8, preceding_tab=0):  # version 240313

    def max_characters(column):
        return max([len(str(value)) for value in column] + [len(str(column.name))])

    a = list(df.apply(max_characters))  # max_chars_per_column
    b = []
    for x in a:
        t = int(x / tab_size) + 1
        b.append(t)

    writer = ''
    writer += '\t' * preceding_tab
    # def print_string_lengths(df):
    for j in range(len(df.columns)):
        t = df.columns[j]
        tab_to_add = b[j] - int(len(t) / tab_size)
        writer = writer + t + '\t' * tab_to_add

    writer += '\n'

    for row_index, row in df.iterrows():
        writer += '\t' * preceding_tab
        # print(f"Row {row_index}:")
        for j in range(len(df.columns)):
            t = str(row.iloc[j])
            tab_to_add = b[j] - int(len(t) / tab_size)
            writer = writer + t + '\t' * tab_to_add

        writer += '\n'

    return writer


def preferred_codon(pp, species='ecoli', assign={}):  # E. coli, will automatically remove space
    ''' species could be ecoli, yeast, mouse, human'''
    triplet = preferred_triplet(species)

    pp = pp.upper().replace(' ', '')
    t = ''
    for x in pp:
        t += triplet[x]
    return t


def preferred_codon_split(pp, species='ecoli', assign={}):
    ''' species could be ecoli, yeast, mouse, human'''
    triplet = preferred_triplet(species)

    pp = pp.upper().replace(' ', '')
    t = []
    for x in pp:
        if x in assign.keys():
            codon = assign[x]
            if translate(codon) == x:
                t.append(assign[x])
                continue
            else:
                print(f'{codon} do not encode {x} ')
        t.append(triplet[x])
    return t


# Fasta file processing
def parse_fasta_string(s):
    recs = []
    header = None
    seq_lines = []
    for line in s.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                recs.append((header, "".join(seq_lines)))
            header = line[1:].strip()
            seq_lines = []
        else:
            seq_lines.append(line.replace(" ", "").upper())
    if header is not None:
        recs.append((header, "".join(seq_lines)))
    return recs


def fastafile_to_tuples(fasta_file):
    fasta_file = fasta_file.split(".fa")[0] + ".fasta"

    with open(fasta_file, "r", encoding="utf-8") as file:
        fasta_str = file.read()
    fasta_tuples = parse_fasta_string(fasta_str)
    # fasta_df = pd.DataFrame(fasta_tuples, columns=["header", "sequence"])
    return fasta_tuples


def tuples_to_fastafile(fasta_tuples, fasta_file='output.fasta'):
    fasta_file = fasta_file.split(".fa")[0] + ".fasta"
    with open(fasta_file, "w") as f:
        for header, seq in fasta_tuples:
            f.write(f">{header}\n{seq}\n")
    return


def split_fasta(input_fasta, output_dir="split_fasta"):
    from pathlib import Path
    from Bio import SeqIO
    # Create output directory if it does not exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Parse and write each sequence
    for record in SeqIO.parse(input_fasta, "fasta"):
        # Clean filename (remove spaces or problematic chars)
        safe_header = record.id.replace(" ", "_").replace(":", "_").replace("/", "_")
        output_file = Path(output_dir) / f"{safe_header}.fasta"

        with open(output_file, "w") as f:
            SeqIO.write(record, f, "fasta")
        print(f"Written: {output_file}")


# oligo list csv modification
def csv_show_last(show_last=10, csvfile='Oligo_list_1.csv'):
    df = pd.read_csv(csvfile)
    print(df.tail(show_last).to_string())
    return df


def csv_delete(column_name=None, contain_str=None, by_last=None, csvfile='Oligo_list_1.csv'):
    df = pd.read_csv(csvfile)

    if contain_str:
        df = df[~df[column_name].str.contains(contain_str, na=False)]
    if by_last:
        df = df.iloc[:-by_last]

    df.to_csv(csvfile, index=False)
    return df


def csv_edit(name, edit, csvfile='Oligo_list_1.csv'):
    '''
    to add "acg" to the 3' end: edit = ['suffix', 'acg']
    to add "acg" to the 5' end: edit = ['prefix', 'acg']
    to delete 5 nt from the 3'end: edit = ['truncate', 5 ]
    '''

    df = pd.read_csv(csvfile)
    if edit[0] == 'suffix':
        seq = df.loc[df["Name"] == name, "Bases"].values[0]
        new_seq = seq + edit[1]
        df.loc[df["Name"] == name, "Bases"] = new_seq
        df.loc[df["Name"] == name, "Length"] = len(new_seq)

    elif edit[0] == 'prefix':
        seq = df.loc[df["Name"] == name, "Bases"].values[0]
        new_seq = edit[1] + seq
        df.loc[df["Name"] == name, "Bases"] = new_seq
        df.loc[df["Name"] == name, "Length"] = len(new_seq)

    elif edit[0] == 'truncate':
        seq = df.loc[df["Name"] == name, "Bases"].values[0]
        new_seq = seq[:- edit[1]]
        df.loc[df["Name"] == name, "Bases"] = new_seq
        df.loc[df["Name"] == name, "Length"] = len(new_seq)

    df.to_csv(csvfile, index=False)
    return df


def reorder_mutations(s):
    # Split into prefix and mutation parts
    parts = s.strip().split("_")
    prefix = parts[0]
    mutations = parts[1:]

    # Sort mutation parts by the numeric residue position
    mutations.sort(key=lambda m: int(re.search(r"(\d+)", m).group()))

    return prefix + "_" + "_".join(mutations)


def update_list(entity, index0='0', index1='1'):
    file0 = f"{entity}_list_{index0}.csv"
    file1 = f"{entity}_list_{index1}.csv"
    if os.path.exists(file1):
        if os.path.exists(file0):
            print(f'delete file {file0}')
            os.remove(file0)
        print(f'rename {file1} as {file0}')
        os.rename(file1, file0)
    return


# tell variant

def seq_to_notation(ref, seq, force_substitution=False, verbose=False):
    ref = ref.strip().replace('*', 'x').upper()
    seq = seq.strip().replace('*', 'x').upper()

    i = 0
    j = 0

    if not force_substitution:
        t = ''
        while i < len(ref):
            if ref[i] == seq[j]:
                i += 1
                j += 1
            else:
                if ref[i + 1:i + 3] == seq[j + 1:j + 3]:
                    t += f'_{ref[i]}{i + 1}{seq[j]}'  # pattern1, substitution
                    i += 1
                    j += 1

                elif ref[i + 1:i + 3] == seq[j:j + 2]:
                    t += f'_{i + 1}del'  # pattern2, 1-aa deletion
                    i += 1

                elif ref[i:i + 2] == seq[j + 1:j + 3]:
                    t += f'_{i}~{i + 1}ins{seq[j]}'  # pattern3, 1-aa insertion
                    j += 1

                else:
                    a = []
                    for i_ in range(i, len(ref) - 4):
                        for j_ in range(j, len(seq) - 4):
                            if ref[i_:i_ + 4] == seq[j_:j_ + 4]:
                                a = [i_, j_]
                                break
                        if a != []:
                            break
                    if a:
                        i_, j_ = a

                        if j_ == j:
                            t += f'_{i + 1}~{i_}del'  # pattern4, multi- deletion

                        elif i_ == i:
                            t += f'_{i}~{i + 1}ins{seq[j:j_]}'  # pattern5, multi- insertion

                        else:
                            t += f'_{i + 1}~{i_}delins{seq[j:j_]}'  # pattern6, delins
                        i, j = i_, j_
                    else:
                        t += f'_{i + 1}~{len(ref)}delins{seq[j:]}'
                        i, j = len(ref), len(seq)
        if verbose: print(t)
        return t

    else:
        t = ''
        while i < len(ref):
            if ref[i] == seq[j]:
                i += 1
                j += 1
            else:
                t += f'_{ref[i]}{i + 1}{seq[j]}'  # pattern1, substitution
                i += 1
                j += 1
        if verbose: print(t)
        return t


def seq_to_notations(ref, file_fasta, verbose=True):
    with open(file_fasta, "r", encoding="utf-8") as file:
        fasta_str = file.read()

    # --- main logic ---
    records = parse_fasta_string(fasta_str)
    A = [(header, seq_to_notation(ref, seq)) for header, seq in records]
    if verbose:
        for (a, b) in A:
            print(f'{a}\t{b}')
    return A


def decode_notation(notation):
    """
    variation consist of 6 types
    1-aa substitution, e.g.,    R13A or 13A
    1-aa deletion, e.g.,        28del
    1-aa insertion, e.g.,       90~91insE
    multi insertions, e.g.,     101~102insEAT
    multi deletion, e.g.,       130~135del
    deletion & insertion, e.g., 140~142delinsAAG

    Multiple variations were joined by '_' to form a notation
    """
    t = notation.split('_')[1:]
    pattern1a = re.compile(r'(\d+)([A-Z])')  # pattern1a, substitution with initial resname unknown
    pattern1 = re.compile(r'([A-Z])(\d+)([A-Z])')  # pattern1, substitution
    pattern2 = re.compile(r'(\d+)del')  # pattern2, 1-aa deletion
    pattern3 = re.compile(r'(\d+)~(\d+)ins([A-Z]+)')  # pattern3 & 5, insertions
    pattern4 = re.compile(r'(\d+)~(\d+)del')  # pattern4, multi- deletion
    pattern6 = re.compile(r'(\d+)~(\d+)delins([A-Z]+)')  # pattern6 delins

    data = []
    for x in t:

        if pattern1a.fullmatch(x):
            m = pattern1a.fullmatch(x)
            pos, new = m.groups()
            pos = int(pos)
            # print(pos, new)
            data.append(['sub', pos, new])


        elif pattern1.fullmatch(x):
            m = pattern1.fullmatch(x)
            orig, pos, new = m.groups()
            pos = int(pos)
            # print(pos, new)
            data.append(['sub', pos, new])

        elif pattern2.fullmatch(x):
            m = pattern2.fullmatch(x)
            pos, = m.groups()
            pos = int(pos)
            # print(pos)
            data.append(['del', pos])

        elif pattern3.fullmatch(x):
            m = pattern3.fullmatch(x)
            pos, _, new = m.groups()
            pos = int(pos) + 0.5
            # print(pos, new)
            data.append(['ins', pos, new])

        elif pattern4.fullmatch(x):
            m = pattern4.fullmatch(x)
            pos, pos1 = m.groups()
            pos = int(pos)
            pos1 = int(pos1)
            # print(pos, pos1)
            data.append(['mdel', pos, pos1])

        elif pattern6.fullmatch(x):
            m = pattern6.fullmatch(x)
            pos, pos1, new = m.groups()
            pos = int(pos)
            pos1 = int(pos1)
            # print([pos, pos1], new)
            data.append(['delins', pos, pos1, new])

    zipped = list(zip(data, t))
    sorted_zipped = sorted(zipped, key=lambda x: x[0][1], reverse=True)
    sorted_data, sorted_t = zip(*sorted_zipped)

    return sorted_data, sorted_t


def notation_to_seq(ref, notation, verbose=False):
    decode, t = decode_notation(notation)
    # print('decode', decode)
    a = '0' + ref
    a = list(a)

    for i in range(len(decode)):

        entry = decode[i]
        label = t[i]
        # print('i',i)
        # print('entry', entry)
        if entry[0] == 'sub':
            _, pos, new = entry
            a[pos] = new

        elif entry[0] == 'del':
            _, pos = entry
            del a[pos]

        elif entry[0] == 'ins':
            _, pos, new = entry
            pos = int(pos + 0.5)
            a.insert(pos, new)

        elif entry[0] == 'mdel':
            _, pos, pos1 = entry
            del a[pos:pos1 + 1]

        elif entry[0] == 'delins':
            _, pos, pos1, new = entry
            del a[pos:pos1 + 1]
            a.insert(pos, new)

    a = ''.join(a)[1:]
    if verbose: print(a)
    return a


def consensus_and_matches(lst1, separater='delins'):
    from collections import Counter
    """
    Given a list of strings like '_158~168delinsQSGLDSGTRLEATKGKS',
    compute the consensus sequence (most common amino acid at each position)
    and return which lines match the consensus.
    """
    if isinstance(lst1, str):
        lst1 = lst1.strip()
        lst1 = lst1.split('\n')

    # Extract sequences after 'delins'
    sequences = [line.split(separater)[1] for line in lst1]

    # Build consensus
    consensus = []
    for pos in zip(*sequences):
        most_common, _ = Counter(pos).most_common(1)[0]
        consensus.append(most_common)
    consensus_seq = "".join(consensus)

    # Collect matches
    matches = [i for i, seq in enumerate(sequences) if seq == consensus_seq]

    return consensus_seq, matches

# instruction text
def print_note(key):
    if key == 'About oligo & plasmid list':
        print(
    """ 
    # ........................................ About oligo & plasmid list
    
    This script prioritizes oligo reuse over new oligo design:
        Paste existing oligos into 'Oligo_list_0.csv'
        Newly designed entities will be added to and saved in 'Oligo_list_1.csv'

    After each design, run:
        # {
        GBparser.update_list('Oligo')
        GBparser.update_list('Plasmid')
        # }
        to replace list_0 with list_1.

    Oligo and plasmid names are generated automatically. For example:
        If oligo_prefix = 'Oz' and oligo Oz01 is available in Oligo_list_0, the next oligo will be named Oz02.
        If plasmid_prefix = 'pL-' and plasmid pL-001 is available in Plasmid_list_0, the next plasmid will be named pL-002.
    """)
    elif key == 'Primer design explained':
        print(
    """ 
    # ........................................ Primer design explained
    Indices of the following sites must be listed in `mutation_site` as either an int or a range:
        1. Mutation sites
        2. Protein-fusion sites
        3. De novo–assembled regions
           (i.e., any single base without a PCR template)

    Sites within 50 nt are automatically merged; the intervening templated regions are referred to as segments. 
    A pair of flanking (PCR) primers is designed for each segment. Each flanking primer consists of (at least):
        • a 5′ BsaI recognition site, and
        • a 3′ template-binding region.
        Mutation sites may be encoded within the middle of some primers.

    If a mutation site is too long (e.g., a de novo region assembled by primer walking), internal primers will also be designed.
        One may mix 0.5 µM of each flanking primer with 0.005 µM of each internal primer in a single PCR reaction (one-round PCR).
        However, if the flanking primers can bind the PCR template independently of the internal primers, a two-round PCR is required:
            (1) Perform the first-round PCR using the innermost primer on each side (0.5 µM each).
            (2) Gel-extract the first-round PCR product.
            (3) Perform the second-round PCR using the first-round product as template, 
                with 0.5 µM of each flanking primer and 0.005 µM of each internal primer.
    """)

    elif key == 'About golden gate':
        print(
    """ 
    # ........................................ About golden gate
    
    By default, Golden Gate cloning using BsaI is used, as it is the most efficient and accurate assembly method I have personally tested.
    
    Ensure that both the cloning vector and the gene of interest are free of BsaI sites; otherwise, remove by mutations (see 'examples_Cloning_(advanced).py' example 0a & 0d) 
    
    The side of annealing regions can be specified. For example:
        IIS_side = ['l2', 'r3'] means:
            • select the first annealing region on the left side, within 2 nt of the first linkage, and
            • select the second annealing region on the right side, within 3 nt of the second linkage.
    
    The accuracy of Golden Gate cloning can be assessed using:
        max_N_match: maximum nucleotide identity between two overhangs
            (smaller is better; if max_N_match = 4, mis-annealing will occur).
    
        max_YR_match: maximum identity between two overhangs in terms of pyrimidine (Y) and purine (R)
            (smaller is better, considering that T4 DNA ligase may tolerate transition mismatches).
    """)

    elif key =='Cloning design (advanced)':
        print(
    """ 
    # ........................................ Cloning design (advanced)

    Set a working directory (wd) from which input files will be read and to which output files will be saved.
    
    Each design is defined by nucleotide indices (starting index = 0).
    
    Required input:
        • a plasmid GB file
    
    Design one plasmid at a time (single-mode) using a 3-step workflow:
        1. Edit the sequence (by nucleotide index)
        2. Perform cloning design (by nucleotide index)
        3. View the new plasmid map and update lists
    
    Run blocks 1, 2, and 3 sequentially and observe the results after each step.
    """ )

    elif key =='Cloning design (batch-mode)':
        print(
    """
    # ........................................ Cloning design (batch-mode)
    
    Set a working directory (wd) from which input files will be read and to which output files will be saved.
    
    Design multiple gene variants based on the amino acid index (starting at 1).

    Required input:
        • a plasmid GB file containing the annotated gene/CDS
        
    Output files:
        • Updated oligo list containing new oligos (Oligo_list_1.csv)
        • Updated plasmid list containing new plasmids (Plasmid_list_1.csv)
        • New GenBank files for each variant, annotated with cloning primers
    """ )

    elif key == 'About notation':
        print(
    """
    # ........................................ About notation
    Variations consist of 6 types
        1-aa substitution, e.g.,    R13A or 13A  
        1-aa deletion, e.g.,        28del
        1-aa insertion, e.g.,       90~91insE
        multi insertions, e.g.,     101~102insEAT
        multi deletion, e.g.,       130~135del
        deletion & insertion, e.g., 140~142delinsAAG
        
    Multiple variations are joined by '_' to form a notation, e.g., '_13A_28del_90~91insE'
    """)


    return


# if __name__ == '__main__':

    # # # ================================================================================ Interconversion of gb files to a csv
    # """
    # Making it possible to store the sequence detail as a column in a spreadsheet of plasmid listt
    # """
    #
    # # { ........................................ Convert several gb files to a csv
    # """ put the gb files in the working directory """
    # GBparser.convert_gb_to_csv(csv_file='gb_singleline.csv', line_separater='-new_line-')
    # # }
    #
    #
    # # { ........................................ Recreate gb files from a csv
    # """ put the csv_file in the working directory """
    # GBparser.convert_csv_to_gbs(csv_file='gb_singleline.csv', line_separater='-new_line-')
    # # }

    # # # ================================================================================  directed mutagenesis, mode 1a

    # # { ........................................ Multiple SEQ in Fasta -> Notation
    # ref = '''MDFLKRLIAENPRLLEMRFREREAVCEPATVPFAVRLDGVGFGKRLKDFPPPRSRLVHNALVEVAKSLALTQGADYVHVVSDEINLLFFRAAPYGGRTFKIISVLASQASAELTAKLGRPLYFDGRVIKLRDNCDAASYVLFRARVGLNNYVIQLARGAGLIREYTPPIEDMLKSVVIEDYELAWGTFMRREDGFKKGVDMCSALSRLCNVC'''
    # GBparser.seq_to_notations(ref, 'fasta_input.fasta')
    # # )

    # # { ........................................ TaqMan probe design - truncation analysis
    # GBparser.primer_truncation_analysis(
    #     primer0  = 'CACCCCGCATTTACGTTTGGTGGACC',
    #     monovalent_cation=50, divalent_cation=1.5)
    # # }
    #
    #
    # # { ........................................ Count atcg in a sequence
    # GBparser.atcg_count('TGTTGGCGCATAAAGCTTCGACGTGCCAGATCACAT')
    # # }

    # # { ........................................ Edit DEFINITION
    # filename = 'pUC19'
    # new_filename = 'pUC19_new'
    # gb_str =  GBparser.Read_gb(filename)
    # text1 = GBparser.extract_gb_elements(gb_str, header ='DEFINITION') +'_hello'
    # GBparser.output_gb(gb_str, new_filename, new_definition = text1)
    # # }
    #
    #
    # # { ........................................ Edit COMMENT
    # filename = 'pUC19'
    # new_filename = 'pUC19_new'
    # gb_str =  GBparser.Read_gb(filename)
    # text1 = GBparser.extract_gb_elements(gb_str, header ='COMMENT') +'\nan additional comment'
    # gb_str =  GBparser.overwrite_gb_elements(gb_str, text1, header = 'COMMENT')
    # GBparser.output_gb(gb_str, new_filename)
    # # }
