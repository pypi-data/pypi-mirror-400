import os

from biochemHH import Gel

if __name__ == '__main__':

    wd = 'C:/Users/hsinmei/playground'; os.chdir(wd)


    """
    This example file consist of the following parts:
    1. RCSB alignment & index mapping
    2. Snippets 
    """

    # ================================================================================ RCSB alignment & index mapping
    """ 
    Procedure:
    1. Perform a flexible pairwise structure alignment on the RCSB website (https://www.rcsb.org/alignment), using:
        First input: an AlphaFold-generated model of your protein of interest (POI)
        Second input: an X-ray–determined structure of a homologous protein-ligand complex

    2. Once the analysis is complete, select Export → Download All.
    
    3. The download will include a zipped folder, a FASTA file, and a JSON file. 
        Unzip the folder (containing the aligned CIF files) and move the FASTA and JSON files into the unzipped folder.
       
    4. Move the unzipped folder into your working directory (wd).
    
    5. Run the code block below. A 'mapping_df_{}.csv' file will be created in the unzipped folder under your working directory.

    Important: Do not rename the unzipped folder or any files before running the code.
    """

    # { ........................................ Create mapping_df_{}.csv
    unzipped_folder_name = 'structures_2025-12-29-17-10-3'
    Homolog.convert_rcsbAln_output_to_mapping_df( wd, subdir=unzipped_folder_name, site_of_interest=None)
    # afterward, check inside the unzipped (structures_2025-12-29-17-10-3) folder for 'mapping_df_{}.csv 'file
    # }



    # { ........................................ Create 'mapping_df_{}.csv' & 'df1.csv'
    # if one is interested in certain residues of the first structure (forward mapping)
    unzipped_folder_name = 'structures_2025-12-29-17-10-3'
    Homolog.convert_rcsbAln_output_to_mapping_df( wd, subdir=unzipped_folder_name, site_of_interest=('forward',[141, 406]))
    # }



    # # { ........................................ Create 'mapping_df_{}.csv' & 'df1.csv'
    # if one is interested in certain residues of the second structure (reverse mapping)
    unzipped_folder_name = 'structures_2025-12-29-17-10-3'
    Homolog.convert_rcsbAln_output_to_mapping_df( wd, subdir=unzipped_folder_name, site_of_interest=('reverse',[12, 251]))
    # }

    # ================================================================================ Snippets

    # { ........................................ Find the starting index of a sequence/motif
    a = Homolog.index_start_aa('4I2B', 'KISQYA'); print(a)
    # }


    # { ........................................  load a fasta file as a list of tuples
    a = GBparser.fastafile_to_tuples('fasta_example'); print(a)
    # }


    # { ........................................  Calculate consensus from fasta string
    fasta_str = '''
    >7B08_t1
    MLLDATYITVDGKPVILLYEKENGKYKVRYDTDFKPYFYVELTDKEDVEEIMKITAERDGKTVTIVSTEWVEKTYLGKPIEVVKVYVENPRDIPAIVDKIAAHPAVKAIYEYDIPL
    >7B0F_t1
    MLLDVTHITVDGKDVILIYEKENGKFKVREDRTFEPYFYVELSDEAAAEDVLKITAERDGEKVTITRMEKVEKKYLGEPVTVWRVYLENSKDIPAIRDKVKAHPAVKDIYEYDIPI
    >7B0Hv1_t1
    MILDVTHITVDGKPVILIYKKEDGKYRIEEDRTFRPYFLALLKNDEDVEDVMKITAERDGRTVTIEKVEKVEKKLLGKPVTVYRLYVEHPDDIPAIADKIAAHPAVKEIYEYDIPL
    '''
    a = Homolog.consensus_from_fasta_string(fasta_str, verbose=True); print(a)
    # }
