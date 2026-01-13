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
    2. Cloning design (advanced)
        - Example 0a: mutate BsaI site on a vector
        - Example 0b: subclone a gene onto a vector
        - Example 0c: construct a fusion protein involving primer walk 
        - Example 0d: subclone a gene onto a vector & mutate BsaI site simultaneously
    """

    # ================================================================================ 1. Print notes
    # { ........................................ Print notes (advanced)
    GBparser.print_note('Cloning design (advanced)')
    GBparser.print_note('About oligo & plasmid list')
    GBparser.print_note('About golden gate')
    GBparser.print_note('Primer design explained')
    # }

    # ================================================================================ 2. Cloning design (advanced)

    # ................................................................................ Example 0a: mutate BsaI site on a vector
    """
    1. Edit the sequence (create a new gb file with the BsaI site replaced) -> 'pUCv2'
    2. Cloning design (update the gb file with designed primers)
    3. View the new plasmid map and update lists 
    Run block 1 2 3 subsequently and see what happen after each run
    """
    #
    # { block 1. Edit the sequence (create a new gb file with the BsaI site replaced) -> 'pUCv2'
    filename0 = 'pUC19'
    filename1 = 'pUCv2(1)'
    gb_str = GBparser.Read_gb(filename0)
    GBparser.check_against_IIS_site(gb_str, IIS_site='GGTCTC', display=False)   # show that a 'GGTCTC' is inreversely positioned at range(1765, 1771)
    gb_str = GBparser.gb_edit(gb_str,
                              j0=1765,
                              j1=1771,  # replace 'GGTCTC' reversely positioned at range(1765, 1771)
                              ins_seq='GCTCTC',  # with 'GcTCTC'
                              ins_rf='r',  # also in reverse (r)
                              ins_type='misc_feature',
                              ins_annotation='remove IIS site (silent mutation in AmpR)')
    gb_str = GBparser.gb_reindex(gb_str, origin='tttacactttatgcttccggctcgtatgttg')  # reindex (and reverse) by lac promoter
    gb_str = GBparser.output_gb(gb_str, new_locus_name=filename1, new_definition=filename1)
    GBparser.gb_display(gb_str)    # show that the edited region is now forwardly positioned at range(1458,1464)
    # }

    # { block 2. Cloning design (update the gb file with designed primers)
    filename1 = 'pUCv2(1)'
    GBparser.cloning_design_wrapper_0(
        initial_filename=filename1,
        new_filename=filename1,     # overwrite
        mutation_site=[1459],
        pcr_source=['pUC19'],
        oligo_prefix='Oz',
        N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
        verbose=False)
    # }

    # { block 3. check the resulting file & update list
    filename1 = 'pUCv2(1)'
    GBparser.gb_display(GBparser.Read_gb(filename1), display_range = (1359,1559))
    GBparser.update_list('Oligo')
    GBparser.update_list('Plasmid')
    # }





    # ................................................................................ Example 0b: subclone a gene onto a vector
    """
    1. Edit the sequence (create a gb file with a the lacZ-alpha replaced with cat gene) -> pUCv2-cat
    2. Cloning design (update the gb file with cloning primers flanking the cat gene)
    3. View the new plasmid map and update lists 
    Run block 1 2 3 subsequently and see what happen after each run
    """
    # { block 1. Edit the sequence (create a gb file with a the lacZ-alpha replaced with cat gene) -> pUCv2-cat
    filename0 = 'pUCv2'
    filename1 = 'pUCv2-cat(1)'
    cat_gene = '''atggagaaaaaaatcactggatataccaccgttgatatatcccaatggcatcgtaaagaacattttgaggcatttcagtcagttgctcaatgtacctataaccagaccgttcagctggatattacggcctttttaaagaccgtaaagaaaaataagcacaagttttatccggcctttattcacattcttgcccgcctgatgaatgctcatccggaattccgtatggcaatgaaagacggtgagctggtgatatgggatagtgttcacccttgttacaccgttttccatgagcaaactgaaacgttttcatcgctctggagtgaataccacgacgatttccggcagtttctacacatatattcgcaagatgtggcgtgttacggtgaaaacctggcctatttccctaaagggtttattgagaatatgtttttcgtctcagccaatccctgggtgagtttcaccagttttgatttaaacgtggccaatatggacaacttcttcgcccccgttttcaccatgggcaaatattatacgcaaggcgacaaggtgctgatgccgctggcgattcaggttcatcatgccgtctgtgatggcttccatgtcggcagaatgcttaatgaattacaacagtactgcgatgagtggcagggcggggcgtaa'''  # from pACYC184 vector

    gb_str = GBparser.Read_gb(filename0)
    gb_str = GBparser.gb_edit(gb_str,
                              j0=74,
                              j1=398,  # replace lacZ-alpha forwardly positioned at range(74,398)
                              ins_seq=cat_gene,  # with cat_gene
                              ins_rf='f',  # also in forward (f)
                              ins_type='CDS',
                              ins_annotation='cat')
    gb_str = GBparser.output_gb(gb_str, new_locus_name=filename1, new_definition=filename1)
    GBparser.gb_display(gb_str)  # show that the cat gene is now forwardly positioned at range(74,734)
    # }

    # { block 2. Cloning design (update the gb file with cloning primers flanking the cat gene)
    filename1 = 'pUCv2-cat(1)'
    GBparser.cloning_design_wrapper_0(
        initial_filename=filename1,
        new_filename=filename1,     # overwrite
        mutation_site=[74, 734],     # list the insert-to-vector connection sites (integers)
        pcr_source=['pUCv2', 'pACYC184'],
        oligo_prefix='Oz',
        IIS_side=['l3', 'r3'],   # so that vector-specific oligos can be reused for subcloning other genes
        N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
        verbose=False)
    # }

    # { block 3. View the new plasmid map and update lists
    filename1 = 'pUCv2-cat(1)'
    GBparser.gb_display(GBparser.Read_gb(filename1))
    GBparser.update_list('Oligo')
    GBparser.update_list('Plasmid')
    # }





    # ................................................................................ Example 0c: construct a fusion protein involving primer walk
    """
    1. Edit the sequence by index (clone cat gene from pACYC vector and attach an N-terminal SUMO gene by synthetic oligo)
    2. Cloning design by index (update the gb file with cloning primers)
    3. View the new plasmid map and update lists 
    Run block 1 2 3 subsequently and see what happen after each run
    """
    # { block 1. Edit the sequence (clone cat gene from pACYC vector and attach an N-terminal SUMO gene by synthetic oligo)
    filename0 = 'pUCv2'
    filename1 = 'pUCv2-SUMO-cat(1)'
    cat_gene = '''atggagaaaaaaatcactggatataccaccgttgatatatcccaatggcatcgtaaagaacattttgaggcatttcagtcagttgctcaatgtacctataaccagaccgttcagctggatattacggcctttttaaagaccgtaaagaaaaataagcacaagttttatccggcctttattcacattcttgcccgcctgatgaatgctcatccggaattccgtatggcaatgaaagacggtgagctggtgatatgggatagtgttcacccttgttacaccgttttccatgagcaaactgaaacgttttcatcgctctggagtgaataccacgacgatttccggcagtttctacacatatattcgcaagatgtggcgtgttacggtgaaaacctggcctatttccctaaagggtttattgagaatatgtttttcgtctcagccaatccctgggtgagtttcaccagttttgatttaaacgtggccaatatggacaacttcttcgcccccgttttcaccatgggcaaatattatacgcaaggcgacaaggtgctgatgccgctggcgattcaggttcatcatgccgtctgtgatggcttccatgtcggcagaatgcttaatgaattacaacagtactgcgatgagtggcagggcggggcgtaa'''  # from pACYC184 vector
    SUMO_pp = 'MSDSEVNQEAKPEVKPEVKPETHINLKVSDGSSEIFFKIKKTTPLRRLMEAFAKRQGKEMDSLRFLYDGIRIQADQTPEDLDMEDNDIIEAHREQIGGATY'
    SUMO_gene = GBparser.codon_optimization(pp=SUMO_pp, species='ecoli')

    gb_str = GBparser.Read_gb(filename0)
    gb_str = GBparser.gb_edit(gb_str,
                              j0=74,
                              j1=398,  # replace lacZ-alpha forwardly positioned at range(74,398)
                              ins_seq=cat_gene,  # with cat_gene
                              ins_rf='f',  # in forward (f)
                              ins_type='CDS',
                              ins_annotation='cat')
    gb_str = GBparser.gb_edit(gb_str,
                              j0=74,
                              j1=74,  # insert before the cat gene
                              ins_seq=SUMO_gene,  # with a SUMO_gene
                              ins_rf='f',  # in forward (f)
                              ins_type='CDS',
                              ins_annotation='SUMO')
    gb_str = GBparser.output_gb(gb_str, new_locus_name=filename1, new_definition=filename1)
    GBparser.gb_display(gb_str)  # show that the SUMO gene is at range(74,377), the cat gene is at range(377,1037)
    # }

    # { block 2. Cloning design (update the gb file with cloning primers)
    # Since the SUMO_gene is to be assembled from primers, the whole range(2217,2520) shall be listed in addition to insert-to-vector connection sites (int)
    filename1 = 'pUCv2-SUMO-cat(1)'
    GBparser.cloning_design_wrapper_0(
        initial_filename=filename1,
        new_filename=filename1,  # overwrite
        mutation_site=[range(74, 377), 1037],
        pcr_source=['pUCv2', 'pACYC184'],
        oligo_prefix='Oz',
        IIS_side=['l4', 'r4'],
        N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
        verbose=False)
    # }

    # { block 3. View the new plasmid map and update lists
    filename1 = 'pUCv2-SUMO-cat(1)'
    GBparser.gb_display(GBparser.Read_gb(filename1))
    GBparser.update_list('Oligo')
    GBparser.update_list('Plasmid')
    # }






    # ................................................................................ Example 0d:  subclone a gene onto a vector & mutate BsaI site simultaneously
    """
    1. Edit the sequence by index (clone MBP gene from E. coli genome, mutate the BsaI site on pUC19 in the MBP gene)
    2. Cloning design by index (update the gb file with cloning primers)
    3. View the new plasmid map and update lists 
    Run block 1 2 3 subsequently and see what happen after each run
    """
    # { block 1. Edit the sequence by index (clone MBP gene from E. coli genome, mutate the BsaI site on pUC19 in the MBP gene)
    filename0 = 'pUC19'
    filename1 = 'pUC-MBP(1)'
    mbp_gene = '''atgaaaatcgaagaaggtaaactggtaatctggattaacggcgataaaggctataacggtctcgctgaagtcggtaagaaattcgagaaagataccggaattaaagtcaccgttgagcatccggataaactggaagagaaattcccacaggttgcggcaactggcgatggccctgacattatcttctgggcacacgaccgctttggtggctacgctcaatctggcctgttggctgaaatcaccccggacaaagcgttccaggacaagctgtatccgtttacctgggatgccgtacgttacaacggcaagctgattgcttacccgatcgctgttgaagcgttatcgctgatttataacaaagatctgctgccgaacccgccaaaaacctgggaagagatcccggcgctggataaagaactgaaagcgaaaggtaagagcgcgctgatgttcaacctgcaagaaccgtacttcacctggccgctgattgctgctgacgggggttatgcgttcaagtatgaaaacggcaagtacgacattaaagacgtgggcgtggataacgctggcgcgaaagcgggtctgaccttcctggttgacctgattaaaaacaaacacatgaatgcagacaccgattactccatcgcagaagctgcctttaataaaggcgaaacagcgatgaccatcaacggcccgtgggcatggtccaacatcgacaccagcaaagtgaattatggtgtaacggtactgccgaccttcaagggtcaaccatccaaaccgttcgttggcgtgctgagcgcaggtattaacgccgccagtccgaacaaagagctggcaaaagagttcctcgaaaactatctgctgactgatgaaggtctggaagcggttaataaagacaaaccgctgggtgccgtagcgctgaagtcttacgaggaagagttggtgaaagatccgcgtattgccgccactatggaaaacgcccagaaaggtgaaatcatgccgaacatcccgcagatgtccgctttctggtatgccgtgcgtactgcggtgatcaacgccgccagcggtcgtcagactgtcgatgaagccctgaaagacgcgcagacttga'''  # from E. coli genome

    gb_str = GBparser.Read_gb(filename0)
    gb_str = GBparser.gb_reindex(gb_str, origin='tttacactttatgcttccggctcgtatgttg')  # reindex (and reverse) by lac promoter
    gb_str = GBparser.gb_edit(gb_str,
                              j0=74,
                              j1=398,  # replace lacZ-alpha forwardly positioned at range(74,398)
                              ins_seq=mbp_gene,  # with cat_gene
                              ins_rf='f',  # in forward (f)
                              ins_type='CDS',
                              ins_annotation='MBP')

    GBparser.check_against_IIS_site(gb_str, IIS_site='GGTCTC', display=True)   # show that a 'GGTCTC' is forwardly positioned at range(131, 137) & (2238, 2244)

    gb_str = GBparser.gb_edit(gb_str,
                              j0=133,
                              j1=134,  # replace the 3rd nucleotide of the first BsaI site
                              ins_seq='g',  # with g (silent mutation in MBP gene)
                              ins_rf='f',  # in forward (f)
                              ins_type='variation',
                              ins_annotation='remove_BsaI_site')

    gb_str = GBparser.gb_edit(gb_str,
                              j0=2239,
                              j1=2240,  # replace the 2nd nucleotide of the second BsaI site
                              ins_seq='c',  # with c (silent mutation in AmpR)
                              ins_rf='f',  # in forward (f)
                              ins_type='variation',
                              ins_annotation='remove_BsaI_site')

    gb_str = GBparser.output_gb(gb_str, new_locus_name=filename1, new_definition=filename1)
    GBparser.gb_display(gb_str)     # show that the MBP gene is now forwardly positioned at range(74,1178)
    # }

    # { block 2. Cloning design (update the gb file with cloning primers)
    filename1 = 'pUC-MBP(1)'
    GBparser.cloning_design_wrapper_0(
        initial_filename=filename1,
        new_filename=filename1,  # overwrite
        mutation_site=[74, 133, 1178, 2239],
        pcr_source=['pUC19', 'ecoli', 'ecoli', 'pUC19'],
        oligo_prefix='Oz',
        IIS_side=['l4', 'u', 'r4', 'u'],
        N_match_cutoff=2, YR_match_cutoff=4, GC_threshold=0,
        verbose=False)
    # }

    # { block 3. View the new plasmid map and update lists
    filename1 = 'pUC-MBP(1)'
    GBparser.gb_display(GBparser.Read_gb(filename1))
    GBparser.update_list('Oligo')
    GBparser.update_list('Plasmid')
    # }

