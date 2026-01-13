import os
from time import perf_counter
from biochemHH import GBparser
from biochemHH.GBparser import reverse_complement
from biochemHH.GBparser import preferred_codon
from biochemHH.GBparser import preferred_codon_split

if __name__ == '__main__':
    wd = 'C:/Users/hsinmei/playground';
    os.chdir(wd)

    """
    This example file consist of the following parts:
    1. Print notes
    2. Cloning design (batch-mode)
        - Example 1a: saturated mutagenesis at a single site
        - Example 1b: alanine scanning at multiple sites
        - Example 1c: cloning design based on a list of notations
    """

    # ================================================================================ 1. Print notes (batch-mode)
    # { ........................................ Print notes (simple)
    GBparser.print_note('Cloning design (batch-mode)')
    GBparser.print_note('About oligo & plasmid list')
    GBparser.print_note('About notation')
    # }

    # { ........................................ Print notes (advanced)
    GBparser.print_note('About golden gate')
    GBparser.print_note('Primer design explained')
    # }

    # ================================================================================ 2. Cloning design (batch-mode)
    """ 
    Design multiple gene variants according to the amino acid index (starting at 1).
    
    Required input: a plasmid GB file (base_filename) containing the annotated gene/CDS (feature_select).
    
    Codons are selected automatically based on the expression host. Supported species include: 'ecoli', 'ecoliK', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', and 'human'
    """

    # { ........................................ Example 1a: saturated mutagenesis at a single site
    GBparser.cloning_design_wrapper_1(
        base_filename='pUCv2-cat',  # the gb file 'pUCv2-cat.gb' shall be present in the working directory
        feature_select='cat',
        mutation_codon_no=[16],
        replacement_codon=preferred_codon_split('RHKDESTNQAVLIMFYGPCW', species='ecoli'),
        plasmid_prefix='pL-',
        oligo_prefix='Oz',
        N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
        verbose=False)
    # }
    # { after check
    GBparser.update_list('Oligo')
    GBparser.update_list('Plasmid')
    # }





    # { ........................................ Example 1b: alanine scanning at multiple sites
    GBparser.cloning_design_wrapper_1(
        base_filename='pUCv2-cat',
        feature_select='cat',
        mutation_codon_no=[41, 42, 44, 45],
        replacement_codon=preferred_codon('A', species='ecoli'),  # A for alanine.
        plasmid_prefix='pL-',
        oligo_prefix='Oz',
        N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
        verbose=False)
    # }
    # { after check
    GBparser.update_list('Oligo')
    GBparser.update_list('Plasmid')
    # }




    # { ........................................ Example 1c: cloning design based on a list of notations
    """
    Variations consist of 6 types
        1-aa substitution, e.g.,    R13A or 13A  
        1-aa deletion, e.g.,        28del
        1-aa insertion, e.g.,       90~91insE
        multi insertions, e.g.,     101~102insEAT
        multi deletion, e.g.,       130~135del
        deletion & insertion, e.g., 140~142delinsAAG
    Multiple variations are joined by '_' to form a notation, e.g., '_13A_28del_90~91insE'
    """

    notations = ['_13A_28del_90~91insE',
                 '_101~102insEAT_130~135del_140~142delinsAAG']

    GBparser.cloning_design_wrapper_1(
        base_filename='pUCv2-cat',
        feature_select='cat',
        notations=notations,
        species='ecoli',
        plasmid_prefix='pL-',
        oligo_prefix='Oz',
        N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
        verbose=False)
    # }
    # { after check
    GBparser.update_list('Oligo')
    GBparser.update_list('Plasmid')
    # }
