import numpy as np
from ase.spacegroup import Spacegroup
from ase.spacegroup.symmetrize import check_symmetry
from sympair.utils import index_of_true

def get_spacegroup(atoms, symprec=1e-3, mag=False):
    """
    get the spacegroup of an atoms object
    """
    import spglib
    if mag:
        raise NotImplementedError('Magnetic spacegroups not implemented')
    else:
        sg = spglib.get_spacegroup((atoms.get_cell(), atoms.get_scaled_positions(),
                                atoms.get_atomic_numbers()),
                               symprec=symprec)
    if sg is None:
        raise RuntimeError('Spacegroup not found')
    sg_no = int(sg[sg.find('(') + 1:sg.find(')')])
    return MySpacegroup(sg_no)


    

def apply_symmetry_operations(positions, rotations, translations):
    """Apply symmetry operations to positions.

    Parameters:
    ===========
    positions : array_like
        The positions to apply the symmetry operations to.
    rotations : array_like
        The rotations of the symmetry operations.
    translations : array_like
        The translations of the symmetry operations.

    Returns:
    ========
    array_like
        The positions after applying the symmetry operations.
    """
    positions = np.array(positions, ndmin=2)
    rotations = np.array(rotations, ndmin=3)
    translations = np.array(translations, ndmin=2)
    return np.dot(rotations, positions[:, :, np.newaxis])[:, :, 0] + translations

class MySpacegroup(Spacegroup):
    def tag_sites(self, scaled_positions, symprec=1e-3):
        """
        Modified version of the tag_sites method from the ase.spacegroup.Spacegroup class, so that the rotations and translations are returned too.
        Returns an integer array of the same length as *scaled_positions*,
        tagging all equivalent atoms with the same index.

        Example:

        >>> from ase.spacegroup import Spacegroup
        >>> sg = Spacegroup(225)  # fcc
        >>> sg.tag_sites([[0.0, 0.0, 0.0],
        ...               [0.5, 0.5, 0.0],
        ...               [1.0, 0.0, 0.0],
        ...               [0.5, 0.0, 0.0]])
        array([0, 0, 0, 1])
        """
        natoms = len(scaled_positions)
        scaled = np.array(scaled_positions, ndmin=2)
        scaled %= 1.0
        scaled %= 1.0
        tags = -np.ones((len(scaled), ), dtype=int)
        mask = np.ones((len(scaled), ), dtype=bool)
        rot, trans = self.get_op()
        i = 0
        rot_ops = np.ones((natoms, 3, 3)) * np.nan
        trans_ops = np.ones((natoms, 3)) * np.nan
        print("number of rotations: ", len(rot))
        print("number of translations", len(trans))
        while mask.any():
            pos = scaled[mask][0]
            sympos = np.dot(rot, pos) + trans
            # Must be done twice, see the scaled_positions.py test
            sympos %= 1.0
            sympos %= 1.0
            #print(f"shape of sympos: {sympos.shape}")
            #print(f"sympos: {sympos}")
            c=np.any(np.abs(scaled[np.newaxis, :, :] -
                                      sympos[:, np.newaxis, :]) > symprec,
                               axis=2)
            #print(f"c: {c}")
            #print(f"c.shape: {c.shape}")
            # c is a array of the shape (n_symops, n_atoms)
            # Note that symprec is True means that the atoms are not equivalent
            # and False means that they are equivalent
            m = ~np.all(c, axis=0)
            #print(f"m: {m}")
            assert not np.any((~mask) & m)
            tags[m] = i
            #print(f"m: {m}")
            mask &= ~m
            i += 1
        return tags


def symmetry_equivalent_vectors(vec, sym_ops, mask=None):
    """
    Return the symmetry equivalent vectors of a given vector.
    the vectos are given by scaled coordinates.
    """
    raise NotImplementedError('This function is not implemented yet')
    rot, _trans = sym_ops
    sym_vecs= rot @ vec 
    return sym_vecs

def get_rotation_operation_from_vec1_to_vec2(vec1, vec2, symops, symprec=1e-3):
    """
    Return the rotation operation that transforms vec1 to vec2.
    """
    raise NotImplementedError('This function is not implemented yet')
    sym_vecs = symmetry_equivalent_vectors(vec1, symops)
    # sym_vecs: (n_symops, 3)
    m=np.allclose(sym_vecs, vec2[np.newaxis, :], atol=symprec)
    ind = index_of_true(m)
    return ind




def symmetry_equivalend_pairs(vec1, vec2, sym_ops):
    """
    Return the symmetry equivalent vectors of a pair of vectors.
    """
    raise NotImplementedError('This function is not implemented yet')


def get_symmetry_operators_for_transformation(vec1, vec2, symops, symprec=1e-3):
    """Find the symmetry operators (rotation and translation) that transform vec1 to vec2.
    
    Parameters
    ----------
    vec1 : array_like (3,)
        The starting vector in fractional coordinates
    vec2 : array_like (3,)
        The target vector in fractional coordinates
    symops : tuple
        Tuple of (rotations, translations) from spacegroup operations
    symprec : float
        Precision for comparing vectors
        
    Returns
    -------
    rot : array_like (3, 3)
        The rotation matrix that transforms vec1 to vec2
    trans : array_like (3,)
        The translation vector. None if no translation is needed.
    """
    raise NotImplementedError('This function is not implemented yet')
    rot, trans = symops
    sym_vecs = symmetry_equivalent_vectors(vec1, symops)
    # Find which symmetry operation transforms vec1 to vec2
    matches = np.allclose(sym_vecs, vec2[np.newaxis, :], atol=symprec)
    op_index = index_of_true(matches)
    
    if op_index is not None:
        return rot[op_index], trans[op_index]
    return None, None
