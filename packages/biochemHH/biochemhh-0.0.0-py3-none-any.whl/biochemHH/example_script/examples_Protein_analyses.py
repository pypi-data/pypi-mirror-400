import os
from biochemHH import Homolog
from biochemHH import StructureHH
from biochemHH import GBparser
from biochemHH import Gel

if __name__ == '__main__':

    wd = 'C:/Users/hsinmei/playground'; os.chdir(wd)

    """ 
    This example file contains the following code blocks:
        - Detect cysteine (reduced) and disulfide bond (oxidized)
        - Load a structure and create a PyMOL script for visualization
        - Shell-wise analysis of residue-level interactions
    
    Input files:
        The scripts search for a structure file (PDB or CIF) in the working directory (wd).
        If no file is found, the structure will be downloaded automatically from the RCSB website.
        
        Therefore:
            For a standard PDB entry, no input file is required.
            To analyze a custom structure, place the structure file in the working directory.
    """


    # { ........................................ Detect cysteine (reduced) and disulfide bond (oxidized)
    filename  = '1AO6.cif'
    StructureHH.Detect_disulfide_and_cysteine(wd, filename)
    # }



    # { ........................................ Load a structure and create a PyMOL script for visualization
    filename = '2PYL.cif'
    StructureHH.Fetch_and_view(wd, filename, sele_head = '', save_pse = False)
    # }



    # { ........................................  Shell-wise analysis of residue-level interactions
    """ Shell-wise analysis
    Output files:
        A bond matrix is automatically generated and saved in a subfolder under the working directory.
        A PyMOL (.pml) file is created to facilitate visualization.
    
    By setting the ligand as the target, shell = 2, and analyze_potential = True, the analysis includes:
        shell1: first-shell residues framing the active site (i.e. residues directly contacting the target)
        shell2: second-shell residues (residues contacting shell1, excluding those belonging to the target or shell1)
        potent1: residues not in direct contact but within a specified distance of the target (default: 5 A)
        potent2: residues not in direct contact but within a specified distance of first-shell residues (default: 5 A)
    
    To analyze interactions between the target and residues from specific chains, list those chains in coi.
    To analyze residues from all chains, set coi = [].
    
    Note: Interactions are identified solely by distance cutoffs; some may not satisfy ideal coordination geometry.
    """
    filename = '5AXN.cif'
    target_chain = 'B'
    target_resi = [80, 81, 82, 83, 84, 85, 86]
    coi = ['A']      # To analyze against residues from all chains instead, set coi = [].
    shell = 2
    analyze_potential = True
    D, d, n, N = StructureHH.Shell_analyses(wd, filename,
                                            target_chain=target_chain,
                                            target_resi=target_resi,
                                            coi=coi,
                                            shell=shell,
                                            analyze_potential=analyze_potential,
                                            potential_cutoff=5,
                                            combine_categories=['shell1', 'potent1', 'shell2'],
                                            neighbor_expand=2)
    # }


