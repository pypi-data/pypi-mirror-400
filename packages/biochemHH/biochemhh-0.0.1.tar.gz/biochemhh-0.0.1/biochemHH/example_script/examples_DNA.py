import os
from biochemHH import GBparser
from biochemHH.GBparser import reverse_complement
from biochemHH.GBparser import preferred_codon
from biochemHH.GBparser import preferred_codon_split
from biochemHH.GBparser import Read_gb

if __name__ == '__main__':


    wd = 'C:/Users/hsinmei/playground'; os.chdir(wd)

    """ 
    This example file consist of the following parts:
    
    1. Primer design
        - Analyze a forward primer OR a primer pair
        - Design primer pairs
        - Analyze an oligo's secondary structure propensity
        - Pick overlapping regions for primer walk
        - Manually pick the annealing regions for golden gate cloning
        
    2. Codon choice 
        (supported species: 'ecoli', 'ecoliK', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human')
        - Codon optimization
        - Codon diagnosis
        - Choose a degenerate codon
        - Create a dictionary of preferred codon
        
    3. GB editing tools (BATCH)
        - Remove primer annotations from all GB files
        - Edit & annotate all GB files containing the target_seq
        - Edit & annotate all GB files containing the target_seq in certain context
        - Simple string replacement applied to all GB files
        
    4. GB editing tools (SINGLE)
        - Duplicate a GB file given a new filename 
        - Reverse the sequence
        - Reindex the sequence
        - Remove features
        - Add features
        - Display by range
        - Display by feature
        - Sequence editing by index
        - Sequence editing by variation of an annotated CDS/gene
    
    5. SEQ to Notation interconversion
        - SEQ to Notation
        - Notation to SEQ
    
    6. Snippets useful in cloning design
        - Check if the sequence contain BsaI site
        - Update list_0 with list_1
        - Batch-mode definition update
        - Full GB display
    """
    # ================================================================================ 1. Primer design

    # { ........................................ Analyze a forward primer OR a primer pair
    p1 = GBparser.Primer3_analysis_250617(
        left_primer = 'tgatATTcttgaggaacgccaaaaagt',
        right_primer =  'atcacccagcaggctaggaataaaacc', # or right_primer =  None
        thermodynamic=0,
        monovalent_cation=50, divalent_cation=1.5,
        verbose=True, horizontal = False)
    # }


    # { ........................................ Design primer pairs
    """
    Advanced: to design an inverse PCR primer pair, insert a comma at the intended site, e.g., f'{seq1},{seq2}' -> f'{seq2+seq1}' 
    """
    template = 'AAAATCGAAGAAGGTAAACTGGTAATCTGG,ATTAACGGCGATAAAGGCTATAACGGTCTCGCTGAA'
    if ',' in template: template = template.split(',')[1] + template.split(',')[0].replace(' ','')
    primers = GBparser.Primer3_design(template, mode=1, primer_max_size=25, primer_pick_anyway=1)
    # }



    # { ........................................ Analyze an oligo's secondary structure propensity
    seq = 'ACTCAAACCCGTGGGCTAGTTTATC'
    GBparser.analyze_single_seq(seq, verbose=True)
    # }


    # { ........................................ Pick overlapping regions for primer walk
    substring = 'CTAGCCCACGGGTTTGAGTGCTCAAGACATGGC'
    a = GBparser.Show_po_pairs(substring, exact = False, preset = 1)
    print(a)
    # }


    # { ........................................ Manually pick the annealing regions for golden gate cloning
    """ 
    Provide a list of N segments (lst_of_seq) within which the annealing region is intended.
    The function will pick a 4-nt region per segment (N) such that the resulting overhangs (2*N) have minimal tendency to mis-anneal.
    """
    GBparser.choose_golden_gate(lst_of_seq=['AACG', 'tatgtg', 'ctagaga'], N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0)
    # }



    # ================================================================================ 2. Codon choice

    # { ........................................ Codon optimization
    #  supported species include 'ecoli', 'ecoliK', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    pp = "KIEEGKLVIWINGDKGYNGLAE"
    dna1 = GBparser.codon_optimization(pp = pp , species = 'ecoli',
                                       preceding_triplet='ATG', tailing_triplet='GTC', verbose = True)
    # }


    # { ........................................ Codon diagnosis
    #  supported species include 'ecoli', 'ecoliK', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    dna1 = '''TTTCAAATTGTGAAGAATCCAAGGTCTGTGGGAAA
    AGCAAGCGAGCAGCTGGCTGGCAAGGTGGCACAAGTCAAGAAGAACGGAAGAATCAGCCTGGTGCTGGGC
    GGAGACCACAGTTTGGCAATTGGAAGCATCTCTGGCCATGCCAGGGTCCACCCTGATCTTGGAGTCATCT
    GGGTGGATGCTCACACTGATATCAACACTCCACTGACAACCACAAGTGGAAACTTGCATGGACAACCTGT
    '''
    GBparser.codon_diagnosis(dna1, rv_cutoff=0.1, species='ecoli')
    # }


    # { ........................................ Choose a degenerate codon
    # Intended for site-directed semi-random mutagenesis
    target = 'FIL'
    codon_table, _  = GBparser.extract_kazusa()
    df1, codon_detail, codon = GBparser.Degenerate_Chooser(codon_table, target)
    # }


    # { ........................................ Create a dictionary of preferred codon
    #  supported species include 'ecoli', 'ecoliK', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    dict1 = GBparser.preferred_triplet(species = 'ecoli')
    for key, value in dict1.items():
        print(key, value)
    # }


    # # ================================================================================ 3. GB editing tools (BATCH)
    """ 
    Will overwrite all matching GB files within the working directory
    """

    # { ........................................ Remove primer annotations from all GB files
    GBparser.remove_primer_feature_for_gb_in_a_folder()
    # }


    # { ........................................ Edit & annotate all GB files containing the target_seq
    GBparser.add_feature_for_gb_in_a_folder(target_seq = 'gggaaacgcctggtatcttt',
                                            type = 'primer_bind',
                                            annotation = 'pBR322ori-F')
    # }


    # { ........................................ Edit & annotate all GB files containing the target_seq in certain context
    #  If there are two '|' characters in target_seq, it will be interpreted as "preceding_seq|target_seq|tailing_seq". Only the target_seq will be replaced
    GBparser.edit_sequence_for_gb_in_a_folder( target_seq = 'aaaaggaagagtatg|agt|attcaa',
                                               new_seq = 'gtg',
                                               ins_type='variation',
                                               ins_annotation='S2V')
    # }


    # { ........................................ Simple string replacement applied to all GB files
    GBparser.string_replace_for_gb_in_a_folder( target_str = 'M13 fwd', replacement_str = 'M13F')
    # }


    # # ================================================================================ 4. GB editing tools (SINGLE)

    # { ......................................... Duplicate a GB file given a new filename
    filename = 'pUC19'
    new_filename = 'pUC19_new'
    gb_str = GBparser.Read_gb(filename)
    gb_str=  GBparser.gb_rename_locus(gb_str, new_filename)
    GBparser.output_gb(gb_str, new_filename)
    # }


    # { ........................................ Reverse the sequence
    filename = 'pUC19'
    new_filename = 'pUC19_new'
    gb_str = GBparser.Read_gb(filename)
    gb_str = GBparser.gb_reverse(gb_str)
    GBparser.output_gb(gb_str, new_filename)
    # }


    # { ........................................ Reindex the sequence
    # By setting promter as index 0, the gene of interest will be forwardly positioned near the start
    filename = 'pUC19'
    new_filename = 'pUC19_new'
    gb_str =  GBparser.Read_gb(filename)
    gb_str =  GBparser.gb_reindex(gb_str, origin='tttacactttatgcttccggctcgtatgttg') # lac promoter
    GBparser.output_gb(gb_str, new_filename)
    # }


    # { ........................................ Remove features
    filename = 'pUC19'
    new_filename = 'pUC19_new'
    gb_str = GBparser.Read_gb(filename)
    gb_str = GBparser.filter_feature(gb_str, remove='source', by= 'type')
    gb_str = GBparser.filter_feature(gb_str, remove= 'MCS', by='label')
    GBparser.output_gb(gb_str, new_filename)
    # }


    # { ........................................ Add features
    """ 
    Sequence within range(s, e) will be annotated. Index start from 0.
    (i.e., to annotate a region, select the region in Benchling or SnapGene, s = start-1, e = end)
    """
    filename = 'pUC19'
    new_filename = 'pUC19_new'
    gb_str = GBparser.Read_gb(filename)
    gb_str = GBparser.gb_add_feature(gb_str, s = 10, e = 100, rf = 'f', type = 'misc_structure', annotation = 'test')
    GBparser.output_gb(gb_str, new_filename)
    # }


    # { ........................................ Display by range
    filename = 'pUC19'
    gb_str = GBparser.Read_gb(filename)
    GBparser.gb_display(gb_str,
                        display_range=(1625, 2486),
                        type_filter=['CDS', 'variation', 'primer'],  # will only show the listed features
                        )
    # }


    # { ........................................ Display by feature
    filename = 'pUC19'
    gb_str = GBparser.Read_gb(filename)
    GBparser.gb_display(gb_str,
                        feature_select='AmpR',  # feature_select will overwrite display_range
                        type_filter=['CDS', 'variation', 'primer'],  # will only show the listed features
                        )
    # }


    # { ........................................ Sequence editing by index
    """
    To replace a region, select the region in Benchling or SnapGene, j0 = start-1, j1 = end.
    To insert, select the nucleotide after the insertion site, j0 = start-1, j1 = start-1 
    """
    filename = 'pUC19'
    new_filename = 'pUC19_new'
    gb_str = GBparser.Read_gb(filename)
    gb_str = GBparser.gb_edit(gb_str,
                              j0=2432,
                              j1=2435,
                              ins_rf='r',
                              ins_seq='GAA',
                              ins_type='misc_feature', ins_annotation='AmpR_C18E')
    GBparser.output_gb(gb_str, new_filename)
    # }



    # { ........................................ Sequence editing by variation of an annotated CDS/gene
    """ 
    Will automatically reverse the sequence if feature_select is on the reverse strand.
    Supported species include 'ecoli', 'bacillus', 'yeast', 'pichia', 'mouse', 'hamster', 'human'
    """
    filename = 'pUC19'
    new_filename = 'pUC19_new'
    gb_str = GBparser.Read_gb(filename)
    Gb_str, *_ = GBparser.gb_edit_variation(gb_str,
                                            feature_select='AmpR',
                                            mutation_codon_no=[24],
                                            replacement_codon=[preferred_codon('A', species='ecoli')],
                                            )
    GBparser.output_gb(Gb_str[0], new_filename)
    # }


    # ================================================================================ 5. SEQ to Notation interconversion
    """
       Variation consist of 6 types 
           1-aa substitution, e.g.,    R13A or 13A  
           1-aa deletion, e.g.,        28del
           1-aa insertion, e.g.,       90~91insE
           multi insertions, e.g.,     101~102insEAT
           multi deletion, e.g.,       130~135del
           deletion & insertion, e.g., 140~142delinsAAG
           
       Multiple variations were joined by '_' to form a Notation
    """

    # { ........................................ SEQ to Notation
    # Compare the difference between ref & seq, and output a notation
    ref = 'MEKKITGYTTVDISQWHRKEHFEAFQSVAQCTYNQTVQLDITAFLKTVKKNKHKFYPAFIHILARLMNAHPEFRMAMKDGELVIWDSVHPCYTVFHEQTETFSSLWSEYHDDFRQFLHIYSQDVACYGENLAYFPKGFIENMFFVSANPWVSFTSFDLNVANMDNFFAPVFTMGKYYTQGDKVLMPLAIQVHHAVCDGFHVGRMLNELQQYCDEWQGGA'
    seq = 'MEKKITGYTTVDASQWHRKEHFEAFQSVAQCYNQTVQLDITAFLKTVKKANKHKFYPAFIHILARLPEFRMAMKDGELVIAGARWDSVHPCYTVFHFINELLAFSSLWSEYHDDFRQFLHIYSQDVACYGENLAYFPKGFIENMFFVSANPWVSFTSFDLNVANMDNFFAPVFTMGKYYTQGDKVLMPLAIQVHHAVCDGFHVGRMLNELQQYCDEWQGGA'

    notation = GBparser.seq_to_notation(ref, seq, force_substitution=False)
    print(notation)
    # }


    # { ........................................  Notation to SEQ
    # create a variant (seq) based on a ref and a notation
    ref = 'MEKKITGYTTVDISQWHRKEHFEAFQSVAQCTYNQTVQLDITAFLKTVKKNKHKFYPAFIHILARLMNAHPEFRMAMKDGELVIWDSVHPCYTVFHEQTETFSSLWSEYHDDFRQFLHIYSQDVACYGENLAYFPKGFIENMFFVSANPWVSFTSFDLNVANMDNFFAPVFTMGKYYTQGDKVLMPLAIQVHHAVCDGFHVGRMLNELQQYCDEWQGGA'
    notation1 = '_I13A_32del_50~51insA_67~70del_84~85insAGAR_97~101delinsFINELLA'

    seq1 = GBparser.notation_to_seq(ref, notation1)
    print(seq1)
    # }

    # ================================================================================ 6. Snippets useful in cloning design

    # { ........................................ Check if the sequence contain BsaI site
    GBparser.check_against_IIS_site(gb_str=GBparser.Read_gb('pUC19'), IIS_site='GGTCTC', display=True)
    # }


    # { ........................................ Update list_0 with list_1
    GBparser.update_list('Oligo')
    GBparser.update_list('Plasmid')
    # }


    # { ........................................ Batch-mode definition update
    # Put the name_definition.csv in the working directory
    GBparser.edit_definition_for_gb_in_a_folder(guiding_file='name_definition.csv')
    # }


    # { ........................................ Full GB display
    GBparser.gb_display(GBparser.Read_gb('pUC19'))
    # }