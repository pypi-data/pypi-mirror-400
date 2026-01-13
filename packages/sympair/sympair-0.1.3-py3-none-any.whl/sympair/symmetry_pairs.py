import copy
import numpy as np
import spglib
from ase.spacegroup import Spacegroup, get_spacegroup
from sympair.spacegroup import MySpacegroup, get_spacegroup
from ase.atoms import Atoms
from dataclasses import dataclass
from itertools import groupby
from sympair.utils import (
    symbol_number,
    standardize_ijR,
    inverse_ijR,
    is_identity_matrix,
)

# References:
# https://gitlab.com/ase/ase/-/blob/master/ase/spacegroup/symmetrize.py?ref_type=heads
# See the symmetrize_rank1 and symmetrize_rank2 function.

# ideas
# - similar to rank1 (force). The distance vector is rotated and translated to another distance vector, which gives the equivalent atom pairs.
#     Perhaps some extra check is needed to see if the target atoms are with the same tag.
# - The rotation of the J in the tensor form is the R.T @J @ R.
# - In this manner, there is no need to construct a supercell.

__all__ = [
    "SymmetryPair",
    "SymmetryPairList",
    "SymmetryPairListDict",
    "SymmetryPairFinder",
]


# The data structure are related like this:
# SymmetryPairList is a list of SymmetryPair objects
# SymmetryPairListDict is a dictionary of which the keys are (i, j, R) and the values are SymmetryPairList objects
# SymmetryPairFinder is a class to find the symmetry pairs and group them by distance and tag.


@dataclass
class SymmetryPair:
    """
    A dataclass to store symmetry atom pairs. Stores one pair of atoms.
    i, j, R are the indices of atoms i and atom (j, R) defines a atom pair
    The ipairlist is the index of the SymmetryPairList. In each group, the atomic pairs are equivalent, and connected by a rotation matrix and a translation vector to a reference pair.
    """

    i: int = None
    j: int = None
    R: tuple = None
    ipairlist: int = None
    rotation_matrix: np.ndarray = None
    translation_vector: np.ndarray = None
    reversed: bool = False
    reference_pair: tuple = None

    def __repr__(self):
        return f"SymmetryPair({self.i}, {self.j}, {self.R}, {self.ipairlist})"

    @property
    def coeff(self):
        """
        Return the coefficient of the pair
        """
        return 1 if not self.reversed else -1

    @property
    def key(self):
        return (self.i, self.j, self.R)

    def set_reference_pair(self, pair):
        self.reference_pair = pair.key

    def is_original(self, atol=1e-3):
        """
        Return True if the pair is the original pair
        """
        return (
            is_identity_matrix(self.rotation_matrix, atol=atol)
            and np.allclose(self.translation_vector, 0, atol=atol)
            and not self.reversed
        )


class SymmetryPairList(list):
    """
    A list of SymmetryPair objects
    """

    def __init__(self, atoms, has_reversed=False):
        super().__init__()
        self.atoms = atoms
        self.has_reversed = has_reversed

    def set_atoms(self, atoms):
        self.atoms = atoms

    def get_all_ijR(self):
        return [(sp.i, sp.j, sp.R) for sp in self]

    def invert(self):
        """
        Invert the group
        """
        for sp in self:
            sp.reversed = not sp.reversed

    def __repr__(self) -> str:
        s = "\n".join([f"{sp}" for sp in self])
        return s

    def has_reversed_already(self):
        ijR_set = set(self.get_all_ijR())
        n_inv = 0
        for pair in self:
            if inverse_ijR(*pair.key) in ijR_set:
                n_inv += 1
        if n_inv == len(self):
            self.has_reversed = True
        return self.has_reversed

    def add_reversed(self):
        """
        Add the reversed pairs to the group
        """
        if self.has_reversed_already():
            return self
        revesed_pairs = []
        for sp in self:
            i, j, R = sp.i, sp.j, sp.R
            if not sp.reversed:
                newpair = SymmetryPair(
                    i=j,
                    j=i,
                    R=tuple(-R),
                    ipairlist=sp.ipairlist,
                    rotation_matrix=sp.rotation_matrix,
                    translation_vector=sp.translation_vector,
                    reference_pair=sp.reference_pair,
                    reversed=True,
                )
                revesed_pairs.append(newpair)
        self += revesed_pairs

    def print(self):
        for sp in self:
            print(sp)


class SymmetryPairListDict(dict):
    """
    A dictionary for finding which group the ijR pair belong to.
    The keys: (i,j, R) The values: SymmetryPairList

    """

    def __init__(self, atoms):
        self.atoms = atoms
        self.pairlists = []
        super().__init__()

    def append_group(self, pairlist):
        self.pairlists.append(pairlist)

    @property
    def npairlist(self):
        return len(self.pairlists)

    @property
    def groups(self):
        return self.pairlists

    @property
    def ngroups(self):
        return len(self.pairlists)

    def get_ipairlist(self, i, j, R):
        """
        Return the ipairlist of (i, j, R)
        """
        return self[(i, j, R)].ipairlist

    def __iter__(self):
        return iter(self.symmetry_pairs)

    def __len__(self):
        return len(self.symmetry_pairs)

    def __getitem__(self, i):
        return self.symmetry_pairs[i]

    def __repr__(self) -> str:
        s = f"===SymmetryPairListDict with {self.ngroups} groups ===\n"
        s += "\n".join(
            [
                f"Group {i} with {len(group)} pairs: \n Has reversed:, {group.has_reversed_already()}\n {group}\n"
                for i, group in enumerate(self.groups)
            ]
        )
        return s

    def join_reversed_pairs(self):
        """
        if two groups of symmetric pairs are the inverse of each other, join them as one group
        """
        new_groups = SymmetryPairListDict(self.atoms)
        for ig, group1 in enumerate(self.groups):
            key1 = group1[0].reference_pair
            i_group_inv = self.get_igroup(*key1)
            if i_group_inv == ig:
                group2 = self.groups[i_group_inv]
                group1 += group2
                new_groups.append_group(group1)


# def tag_sites_by_spacegroup(spacegroup, scaled_positions, symprec=1e-3):
#         scaled = np.array(scaled_positions, ndmin=2)
#         scaled %= 1.0
#         scaled %= 1.0
#         tags = -np.ones((len(scaled), ), dtype=int)
#         sym_ops = {}
#         mask = np.ones((len(scaled), ), dtype=bool)
#         rotations = np.ones((len(scaled), 3, 3), dtype=float)
#         translations = np.ones((len(scaled), 3), dtype=float)
#         rot, trans = spacegroup.get_op()
#         i = 0
#         while mask.any():
#             pos = scaled[mask][0]
#             sympos = np.dot(rot, pos) + trans
#             # Must be done twice, see the scaled_positions.py test
#             sympos %= 1.0
#             sympos %= 1.0
#             m = ~np.all(np.any(np.abs(scaled[np.newaxis, :, :] -
#                                       sympos[:, np.newaxis, :]) > symprec,
#                                axis=2),
#                         axis=0)
#             assert not np.any((~mask) & m)
#             tags[m] = i
#             #rotations[m] = rot
#             #translations[m] = trans
#             for j in np.where(m)[0]:
#                 rotations[j] = rot
#                 translations[j] = trans
#             mask &= ~m
#             i += 1
#         return tags, sym_ops


class SymmetryPairFinder:
    def __init__(self, atoms, pairs=None, Rlist=None, symprec=1e-3, pbc=False):
        self.dvec_red = {}
        self.dvec_cart = {}
        self.d_red = {}
        self.d_cart = {}

        self.atoms = atoms
        self.Rlist = Rlist
        self.symprec = symprec
        self.pbc = pbc
        if pbc:
            raise NotImplementedError("PBC is not implemented yet")
        self.spacegroup = get_spacegroup(atoms, symprec=symprec)

        self.xred = self.atoms.get_scaled_positions()

        if pairs is None:
            self.all_pairs = self._get_all_pairs()
        else:
            self.all_pairs = pairs
        self.get_all_distances()
        self.get_equivalent_sites()

    def _get_all_pairs(self):
        indices = range(len(self.atoms))
        all_pairs = [
            (i, j, tuple(R))
            for i in indices
            for j in indices
            for R in self.Rlist
            if i != j
        ]
        return all_pairs

    def get_all_distances(self):
        """
        Return all distances between atoms and their images
        """
        cell = self.atoms.get_cell()
        for key in self.all_pairs:
            i, j, R = key
            self.dvec_red[key] = self.xred[i] - self.xred[j] - R
            self.dvec_cart[key] = np.dot(self.dvec_red[key], cell)
            self.d_red[key] = np.linalg.norm(self.dvec_red[key])
            self.d_cart[key] = np.linalg.norm(self.dvec_cart[key])

    def group_pairs_by_distance(self, symprec=1e-3):
        """
        Group pairs by distance
        """
        self.get_all_distances()
        d_cart_sorted = sorted(self.d_cart.items(), key=lambda x: x[1])
        groups = groupby(d_cart_sorted, lambda x: round(x[1] / symprec))
        return groups

    def group_pairs_by_tag_and_distance(self):
        """
        Group pairs by tag and distance
        """
        self.get_all_distances()
        # keys: (i, j, R)
        keys = tuple(self.d_cart.keys())
        atomic_numbers = self.atoms.get_atomic_numbers()
        # sort the keys  (distance, tag_i, tag_j) by (distance, tag_i, tag_j)
        # sortdict: (i, j, R) -> (distance, tag_i, tag_j)
        sortdict = {
            key: (
                round(self.d_cart[key] / self.symprec),
                self.tags[key[0]],
                self.tags[key[1]],
                atomic_numbers[key[0]],
                atomic_numbers[key[1]],
            )
            for key in keys
        }
        d_cart_sorted = sorted(sortdict.items(), key=lambda x: x[1])
        sorted_keys = [key for key, value in d_cart_sorted]

        # group by the distance, tag_i, tag_j
        groups = groupby(sorted_keys, lambda x: sortdict[x])

        # The groups can be iterated by the following code
        # for key, group in groups:
        # where key is the tuple (distance, tag_i, tag_j), and group is the iterator of the pairs.
        # if we need the shell number, which is the index of the group, we can use the following code
        # for ishell, (key, group) in enumerate(groups):
        return groups

    @property
    def symbol_number(self):
        """
        ["Sr", "Ti", "O",  "O" , "O"] -> ["Sr1", "Ti1", "O1", "O2", "O3"]
        """
        if not hasattr(self, "_symbol_number"):
            symbols = self.atoms.get_chemical_symbols()
            self._symbol_number = symbol_number(symbols)
        return self._symbol_number

    def print_groups(self, groups, use_symnum=True):
        """
        pretty print of the groups.
        """
        # Note that we use deepcopy as groups are iterators and we don't want to exhaust the iterator
        print("=== Groups ===")
        ngroups = len(list(copy.deepcopy(groups)))
        print("Total number of groups: ", ngroups)
        # the key is the tuple (tag1, tag2, distance), but the distance is in
        #  interger format related to the symprec.
        for i, (key, group) in enumerate(copy.deepcopy(groups)):
            group = list(group)
            n = len(group)
            print(f"=== Group{i} with {n} elements, key = {key} ===")
            for pair in group:
                i, j, R = pair
                if use_symnum:
                    print(f"{self.symbol_number[i]} - {self.symbol_number[j]} - {R}")

    def get_symmetry_pair_list_dict(self):
        """
        Return a dictionary of SymmetryPairList objects
        """
        groups = self.group_pairs_by_tag_and_distance()
        ret = SymmetryPairListDict(self.atoms)

        for igroup, (key, group) in enumerate(groups):
            spg = SymmetryPairList(self.atoms)
            refpair = None
            for ipairlist, pair in enumerate(group):
                if ipairlist == 0:
                    refpair = pair
                i, j, R = pair
                sp = SymmetryPair(
                    i=i, j=j, R=R, ipairlist=ipairlist, reference_pair=refpair
                )
                spg.append(sp)
                ret[(i, j, R)] = spg
            ret.append_group(spg)
        return ret

    def get_equivalent_sites(self):
        """
        Return equivalent sites in atoms object.
        """
        # self.tags, self.tag_sym_ops = tag_sites_by_spacegroup(self.spacegroup, self.xred, symprec=self.symprec)
        self.tags = self.spacegroup.tag_sites(self.xred, symprec=self.symprec)
        return self.tags

    def find_symmmetry_pairs_by_distance(self):
        symmetry_pairs = []
        for key in self.all_pairs:
            i, j, R = key
            if self.get_all_distances()[key] < self.symprec:
                symmetry_pairs.append((i, j, R))
        return symmetry_pairs

    def find_symmetry_pairs(self):
        symmetry_pairs = []
        for key in self.all_pairs:
            i, j, R = key
            if self.get_all_distances()[key] < self.symprec:
                symmetry_pairs.append((i, j, R))

    def symmetrize_distance_vector(self, dvec):
        """
        Rotate and translate the distance vector to the new frame defined by R
        """
        return dvec


def symmetrized_J_tensor(J, R, T=None):
    """
    Rotate and translate the J tensor to the new frame defined by R and T
    params:
    ======
    J: np.ndarray, shape=(3, 3) The tensor to be rotated and translated
    R: np.ndarray, shape=(3, 3) The rotation matrix
    T: np.ndarray, shape=(3,) The translation vector.
    """
    return R.T @ J @ R


def reverse_J_tensor(J):
    """
    For a pair of (i,j, R), the reverse (j, i, -R) pair is equivalent.
    The J tensor is reversed by the following transformation:
    The antisymmetric part is reversed, whereas the symmetric part is unchanged.
    """
    # Janti = 0.5*(J - J.T)
    # Jsym = 0.5*(J + J.T)
    # return Jsym - Janti # It is actually the same as J.T
    return J.T


# Example of usage
def test_SymmetryPairFinder():
    # SrTiO3 cubic structure
    atoms = Atoms(
        "SrTiO3",
        scaled_positions=[
            [0, 0, 0],
            [0.5, 0.5, 0.5],
            [0, 0.5, 0.5],
            [0.5, 0, 0.5],
            [0.5, 0.5, 0],
        ],
        cell=np.eye(3) * 3.905,
        pbc=True,
    )
    # Rlist=[(i,j,k) for i in range(-1, 2) for j in range(-1, 2) for k in range(-1, 2) if i!=0 or j!=0 or k!=0]

    # Rlist within the unitcell
    Rlist = [(0, 0, 0)]
    spf = SymmetryPairFinder(atoms, symprec=1e-3, Rlist=Rlist)

    # equivalence sites
    print(f"Equivalent sites: {spf.get_equivalent_sites()}")

    # print the spacegroup information
    print(spf.spacegroup)
    # print(spf.get_all_pairs())
    # print(spf.get_equivalent_sites())
    # print the distances
    #print(spf.get_all_distances())

    #groups = spf.group_pairs_by_tag_and_distance()

    #spf.print_groups(groups)

    #d = spf.get_symmetry_pair_list_dict()
    #for pl in d.pairlists:
    #    pl.print()



if __name__ == "__main__":
    test_SymmetryPairFinder()
