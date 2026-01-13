import numpy as np
import spglib
from ase.io import read
import argparse
import sys
from typing import Dict, Any

def get_magnetic_space_group_from_files(structure_file, magmoms_file):
    """
    Read structure and magnetic moments from files and determine the magnetic space group.
    
    Parameters:
    -----------
    structure_file: str
        Path to the structure file (any format supported by ASE, e.g., POSCAR, cif, xyz)
    magmoms_file: str
        Path to the magnetic moments file - a simple text file with one moment per line:
        For collinear: one column with magnetic moment values
        For non-collinear: three columns (mx, my, mz) of magnetic moment components
    
    Returns:
    --------
    dict:
        Dictionary containing magnetic space group information
        (see get_magnetic_space_group for details)
    """
    # Read structure using ASE
    atoms = read(structure_file)
    
    # Read magnetic moments from file
    magmoms = np.loadtxt(magmoms_file)
    
    # Verify number of magnetic moments matches number of atoms
    if len(magmoms.shape) == 1:
        if len(magmoms) != len(atoms):
            raise ValueError(f"Number of magnetic moments ({len(magmoms)}) "
                           f"does not match number of atoms ({len(atoms)})")
    else:
        if magmoms.shape[0] != len(atoms) or magmoms.shape[1] != 3:
            raise ValueError(f"Magnetic moments array should have shape ({len(atoms)}, 3) "
                           f"for non-collinear case, got {magmoms.shape}")
    
    return get_magnetic_space_group(atoms, magmoms)

def get_magnetic_space_group(atoms, magmoms):
    """
    Identify the magnetic space group of a structure given the atomic positions and magnetic moments.
    
    Parameters:
    -----------
    atoms: ase.Atoms
        The ASE atoms object containing the crystal structure
    magmoms: array_like
        Magnetic moments array, can be either:
        - shape (natoms,) for collinear magnetic moments
        - shape (natoms, 3) for non-collinear magnetic moments
        
    Returns:
    --------
    dict:
        Dictionary containing magnetic space group information:
        - 'uni_number': UNI number between 1 to 1651
        - 'msg_type': Type of magnetic space group (1-4)
        - 'bns_number': BNS notation
        - 'og_number': OG notation
        - 'operations': Dictionary containing symmetry operations:
            - 'rotations': (n_operations, 3, 3) array
            - 'translations': (n_operations, 3) array
            - 'time_reversals': (n_operations,) array
    """
    # Convert ASE atoms to spglib cell
    cell = (atoms.get_cell(), atoms.get_scaled_positions(), atoms.get_atomic_numbers(), magmoms)
    
    # Determine if magmoms are collinear or non-collinear based on shape
    magmoms = np.array(magmoms)
    is_axial = len(magmoms.shape) > 1 and magmoms.shape[1] == 3
    
    # Get magnetic symmetry dataset
    dataset = spglib.get_magnetic_symmetry_dataset(cell, is_axial=is_axial)
    
    if dataset is None:
        raise ValueError("Could not determine magnetic space group")
    
    # Get magnetic space group type information
    msg_type = spglib.get_magnetic_spacegroup_type(dataset.uni_number)
    if msg_type is None:
        raise ValueError(f"Could not get magnetic space group type for UNI number {dataset.uni_number}")
    
    # Construct return dictionary
    result = {
        'uni_number': dataset.uni_number,
        'msg_type': dataset.msg_type,
        'bns_number': msg_type.bns_number,
        'og_number': msg_type.og_number,
        'operations': {
            'rotations': dataset.rotations,
            'translations': dataset.translations,
            'time_reversals': dataset.time_reversals
        }
    }
    
    return result

def pretty_print_msg(msg: Dict[str, Any]) -> None:
    """
    Pretty print the magnetic space group information.
    
    Displays:
    1. Magnetic Space Group Information:
       - BNS Number (Belov-Neronova-Smirnova notation)
       - OG Number (Opechowski-Guccione notation)
       - MSG Type (1-4)
       - UNI Number (1-1651)
    
    2. Complete list of symmetry operations, for each:
       - 3×3 rotation matrix showing how atomic positions transform
       - 3D translation vector for additional translational component
       - Time reversal flag indicating if the operation includes magnetic moment flipping
    
    Parameters:
    -----------
    msg: dict
        Dictionary containing magnetic space group information from get_magnetic_space_group
    """
    print("\n=== Magnetic Space Group Information ===")
    print(f"BNS Number: {msg['bns_number']}")
    print(f"OG Number: {msg['og_number']}")
    print(f"MSG Type: {msg['msg_type']}")
    print(f"UNI Number: {msg['uni_number']}")
    
    print("\n=== Symmetry Operations ===")
    n_ops = len(msg['operations']['rotations'])
    print(f"Number of operations: {n_ops}")
    
    print("\nSymmetry operations:")
    if n_ops > 0:
        for i in range(n_ops):
            print(f"\nOperation {i+1}:")
            print("Rotation matrix:")
            print(np.array2string(msg['operations']['rotations'][i], prefix='  '))
            print("Translation vector:")
            print(np.array2string(msg['operations']['translations'][i], prefix='  '))
            print("Time reversal:", bool(msg['operations']['time_reversals'][i]))
            print("-" * 40)

def main():
    """Command line interface for magnetic space group analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze magnetic space group from structure and magnetic moments files"
    )
    parser.add_argument("structure", help="Structure file (any format supported by ASE)")
    parser.add_argument("magmoms", help="Magnetic moments file (text file with one or three columns)")
    
    try:
        args = parser.parse_args()
        msg = get_magnetic_space_group_from_files(args.structure, args.magmoms)
        pretty_print_msg(msg)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
