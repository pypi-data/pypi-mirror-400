import os
from biochemHH import Homolog
from biochemHH import StructureHH
from biochemHH import GBparser


if __name__ == '__main__':

    wd = 'C:/Users/hsinmei/playground'; os.chdir(wd)

    """
    This example file consist of the following parts:
    
    1. Edit a single PDB(CIF) file
        - Duplicate a structure
        - Extract certain residue (ligand) from a structure
        - Substitute the nucleobase
        - Rename chains
        - Delete chains
        - Edit residue: re-assign, rename, and keep all atoms
        - Edit residue: remove certain atoms
        - Edit chain: retain a list of residues
        - Edit chain: remove a list of residues
        - Duplicate a residue
        - ATOM to HETATM (some AI tools only consider HETATM as ligand)
      
    2. Align & merge two PDB(CIF) files
        - Chimera example 1, alignment by oligonucleotide
        - Chimera example 2, alignment by amino acid
        - Chimera example 3, alignment by atoms
    """

    # ////////////////////////////////////////////////////////////////////////////////  Edit a single PDB(CIF) file
    # { ........................................ Duplicate a structure
    """ 
    Useful in case of successive editing.
    """
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose =  True
    StructureHH.copy_structure_file(filename0, filename1, verbose = verbose)

    # }


    # { ........................................ Extract certain residue (ligand) from a structure
    """
    The resulting .cif will be exported to the working directory
    """
    filename0 = '2W35.cif'
    chain = 'C'
    resi = 8
    verbose = True
    atoms_to_remove = ["C2'", "C3'", "C4'", "C5'", "O2'", "O3'", "O4'", "O5'",
                       "H1'", "H2'", "H2''", "H3'", "H4'", "H5'", "H5''", "HO2'", "HO3'", "P", "OP1", "OP2"]

    StructureHH.create_residue_cif(filename0 ,
                                   chain = chain,
                                   resi = resi,
                                   atoms_to_remove = atoms_to_remove,
                                   verbose = verbose)
    # }


    # { ........................................ Substitute the nucleobase
    """
    Available change_to include 'adenine', 'thymine',  'cytosine' , 'guanine', 'uracil', 'inosine'
    Below is an example of successive editing.
    """
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.base_substitution(filename1,
                                  chain='A',
                                  resi=304,
                                  change_to='uracil')

    StructureHH.base_substitution(filename1,
                                  chain='P',
                                  resi=72,
                                  change_to='adenine',
                                  verbose=verbose)

    # }


    # { ........................................ Rename chains
    """
    The example rename chain 'A' -> 'C', chain 'B' -> 'D' respectively.
    """
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.rename_chains(filename1,
                              initial_chain_id=['A', 'B'],
                              new_chain_id=['C', 'D'],
                              verbose= verbose)
    # }


    # { ........................................ Delete chains
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.delete_chains(filename1, chains_to_remove = ['B'], verbose = verbose)
    # }


    # { ........................................ Edit residue: re-assign, rename, and keep all atoms
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.edit_residue(filename1,
                             initial_chain_resi = ['A', 304],
                             new_chain_resi = ['L', 1],
                             new_resname = 'LIG',
                             remove_atoms = None,
                             verbose = verbose)
    # }


    # { ........................................ Edit residue: remove certain atoms
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.edit_residue(filename1,
                             initial_chain_resi = ['A', 304],
                             new_chain_resi = None,
                             new_resname = None,
                             remove_atoms = ["O2'", "O3'"],
                             verbose = verbose)
    # }


    # { ........................................ Edit chain: retain a list of residues
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.chain_shrinking(filename1,
                                chain = 'A',
                                resi_to_retain = range(100,200),
                                verbose = verbose)
    # }


    # { ........................................ Edit chain: remove a list of residues
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.chain_shrinking(filename1,
                                chain = 'A',
                                resi_to_remove = range(10,200),
                                verbose = verbose)
    # }


    # { ........................................ Duplicate a residue
    """
    the duplicated residue will be attached to the end of the same chain
    """
    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.duplicate_residue(filename1,
                                  initial_chain_resi = ['A', 304],
                                  verbose=verbose)
    # }


    # { ........................................ ATOM to HETATM (some AI tools only consider HETATM as ligand)

    filename0 = '5AXN.cif'
    filename1 = 'temporary.pdb'
    verbose = True
    StructureHH.copy_structure_file(filename0, filename1)

    StructureHH.atom_to_hetatm(filename1,
                               chain_id = 'P',
                               verbose = verbose)
    # }



    # ////////////////////////////////////////////////////////////////////////////////  Align & merge two PDB(CIF) files

    ''' 
    The function merges structures t0 and t1, aligning t1 to t0 based on specified residues (t0_align and t1_align).
        For polypeptide residues, alignment is performed using atoms ["N", "CA", "C"].
        For DNA or RNA residues, alignment is performed using atoms ["C1'", "C2'", "C3'", "C4'", "O4'"].
        To skip alignment, set t0_align = None.

    You can choose to retain specific residues from t0 (t0_sele) and t1 (t1_sele). For example:
        To retain all residues of all chains in t0, set t0_sele = 'all'.
        To retain all residues in chain A, residues 1–23 in chain B, and residues 2, 4, and 6 in chain P, set t0_sele = "A B1~23 P2 P4 P6".

    Note: After merging, chains from t0 and t1 will be renamed in alphabetical order.
    '''

    # { ........................................ Chimera example 1, alignment by oligonucleotide
    StructureHH.make_chimera(
        t0='5AXN.cif',
        t0_align = 'P2 P4 P6',      # align by reisude 2, 4, 6 in chain P
        t0_sele = 'A B1~23 P2~6 P49~72',    # retain all residues in chain A, residue 1~23 in chain B, resideu 49~72 in c hain P

        t1 = '1FIX.cif',
        t1_align = 'A2 A4 A6',      # align by reisude 2, 4, 6 in chain A
        t1_sele = 'all',    # retain all residues from all chains

        new_filename= 'chimera1.pdb')
    # }



    # { ........................................ Chimera example 2, alignment by amino acid
    StructureHH.make_chimera(
        t0='2PYL.cif',
        t0_align='A8~136 A483~574',
        t0_sele='all',

        t1='2EX3.cif',
        t1_align='A8~136 A483~574',  # be careful all the residues shall be in structured region
        t1_sele='A B',

        new_filename='chimera2.pdb')
    # }



    # { ........................................ Chimera example 3, alignment by atoms
    ''' 
    The function will merge structure t0 & t1, among which t1 will be aligned to t0 by a list of atoms (t0_atoms, t1_atoms).   
    Specify each atom by (chain, resi, atom.id)
    '''
    t0_atoms = [('A', 303, 'MG'),
                ('A', 302, 'MG'),
                ('A', 301, 'MG'),
                ('A', 304, 'PG'),
                ('A', 304, 'PB'),
                ('A', 304, 'PA'),
                ]

    t1_atoms = [('A', 405, 'MG'),
                ('A', 404, 'MG'),
                ('A', 403, 'MG'),
                ('A', 402, 'PG'),
                ('A', 402, 'PB'),
                ('A', 402, 'PA'),
                ]

    StructureHH.make_chimera_by_atom_aln(
        t0='5AXN.cif',
        t0_atoms=t0_atoms,
        t0_sele='A B P2~7 P49~72',

        t1='3WC0.cif',
        t1_sele='A',
        t1_atoms=t1_atoms,

        new_filename='chimera3.pdb')
    # }



