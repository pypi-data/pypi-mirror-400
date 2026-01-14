# ================================== LICENSE ===================================
# Magnopy - Python package for magnons.
# Copyright (C) 2023-2026 Magnopy Team
#
# e-mail: anry@uv.es, web: magnopy.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ================================ END LICENSE =================================


import os

import numpy as np
from wulfric.cell import get_params
from wulfric.crystal import get_atom_species

from magnopy._constants._si import JOULE, ELECTRON_VOLT, MILLI
from magnopy._package_info import logo
from magnopy._parameters._p22 import to_dmi, to_symm_anisotropy
from magnopy._spinham._convention import Convention
from magnopy._spinham._hamiltonian import SpinHamiltonian

# Save local scope at this moment
old_dir = set(dir())
old_dir.add("old_dir")


def _verified_materials(materials, M):
    if materials is None:
        materials = [i for i in range(M)]
    else:
        if len(materials) != M:
            raise ValueError(f"Expected {M} materials, got {len(materials)}.")
        materials_pool = set(materials)
        higher_material = max(materials_pool)
        for i in range(0, higher_material + 1):
            if i not in materials_pool:
                raise ValueError(
                    f"Materials indices should be consecutive integers between 0 and {higher_material}. Missing {i}."
                )

    return materials


def dump_vampire(
    spinham: SpinHamiltonian,
    seedname="vampire",
    anisotropic=True,
    dmi=True,
    custom_mask=None,
    decimals=5,
    materials=None,
    no_logo=False,
) -> None:
    """
    Saves spin Hamiltonian in the format suitable for |Vampire|_ (.UCF and .mat).

    Parameters
    ----------

    spinham : :py:class:`.SpinHamiltonian`
        Spin Hamiltonian object to be saved.

    seedname : str, default "vampire"
        Seedname for the .UCF and .mat files. Extensions are added automatically. Input
        file is independent of ``seedname`` and always has the name "input-template".

    anisotropic : bool, default True
        Whether to output anisotropic exchange.

    dmi : bool, default True
        Whether to output DMI exchange.

    custom_mask : func, optional
        Custom mask for the exchange parameter. Function that takes (3, 3)
        :numpy:`ndarray` as an input and returns (3, 3) :numpy:`ndarray` as an output. If
        given, then ``anisotropic`` and ``dmi`` parameters are ignored.

        .. code-block:: python

            parameter_to_output = custom_mask(parameter)

    decimals : int, default 4
        Number of decimals to be printed (only for the exchange values).

    materials : list of int, optional
        List of materials for the atoms. Length is the same as the number of magnetic
        atoms in the ``spinham`` (``spinham.M``). Order is the same as in
        :py:attr:`.SpinHamiltonian.magnetic_atoms`. If none given, each magnetic atom is
        considered as a separate material. Material indices start from 0 and should
        contain all consecutive integers between 0 and number of materials. Number of
        materials cannot be higher than number of magnetic atoms.

    no_logo : bool, default False
        Whether to include the logo in the output files.

    Notes
    -----

    Examples of the correct ``materials`` list for 5 magnetic atoms

    .. code-block:: python

        [0, 0, 0, 0, 0]
        [1, 3, 2, 1, 0]
        [0, 1, 2, 3, 4]

    Examples of the incorrect ``materials`` list for 5 magnetic atoms

    .. code-block:: python

        [0, 6, 0, 0, 0]
        [1, 3, 3, 1, 0]
        [1, 2, 3, 4, 5]
    """

    head, _ = os.path.split(seedname)

    if head != "":
        os.makedirs(head, exist_ok=True)

    dump_vampire_ucf(
        spinham,
        filename=f"{seedname}.UCF",
        anisotropic=anisotropic,
        dmi=dmi,
        custom_mask=custom_mask,
        decimals=decimals,
        materials=materials,
        no_logo=no_logo,
    )
    dump_vampire_mat(
        spinham,
        filename=f"{seedname}.mat",
        materials=materials,
        no_logo=no_logo,
    )
    with open(os.path.join(head, "input-template"), "w", encoding="utf-8") as file:
        if not no_logo:
            file.write(f"{logo(comment=True, date_time=True)}\n")

        file.write(
            "\n".join(
                [
                    "#------------------------------------------",
                    f"material:file={seedname}.mat",
                    f"material:unit-cell-file = {seedname}.UCF",
                    "#------------------------------------------",
                    "# TODO: simulation setup",
                ]
            )
        )


def dump_vampire_mat(
    spinham: SpinHamiltonian, filename, materials=None, no_logo=False
) -> None:
    """
    Generates .mat file for |Vampire|_.

    Parameters
    ----------

    spinham : :py:class:`.SpinHamiltonian`
        Spin Hamiltonian object to be saved.

    filename : str
        Name for the .mat file. Extension ".mat" is added if not present.

    materials : list of int, optional
        List of materials for the atoms. Length is the same as the number of magnetic
        atoms in the ``spinham`` (``spinham.M``). Order is the same as in
        :py:attr:`.SpinHamiltonian.magnetic_atoms`. If none given, each magnetic atom is
        considered as a separate material. Material indices start from 0 and should
        contain all consecutive integers between 0 and number of materials. Number of
        materials cannot be higher than number of magnetic atoms.

    no_logo : bool, default False
        Whether to include the logo in the output files.

    Raises
    ------

    ValueError
        If ``materials`` list is given and its length is not equal to the number of
        magnetic atoms in the ``spinham``.

    ValueError
        If ``materials`` list does not contain all consecutive integers between 0 and
        the highest material index.

    Notes
    -----

    Examples of the correct ``materials`` list for 5 magnetic atoms

    .. code-block:: python

        [0, 0, 0, 0, 0]
        [1, 3, 2, 1, 0]
        [0, 1, 2, 3, 4]

    Examples of the incorrect ``materials`` list for 5 magnetic atoms

    .. code-block:: python

        [0, 6, 0, 0, 0]
        [1, 3, 3, 1, 0]
        [1, 2, 3, 4, 5]
    """

    if len(filename) < 4 or filename[-4:] != ".mat":
        filename += ".mat"

    materials = _verified_materials(materials, spinham.M)

    if no_logo:
        text = []
    else:
        text = [logo(comment=True, date_time=True)]

    text.append(f"material:num-materials = {max(materials) + 1}")

    for i, (material, name, spin, g_factor) in enumerate(
        zip(
            materials,
            spinham.magnetic_atoms.names,
            spinham.magnetic_atoms.spins,
            spinham.magnetic_atoms.g_factors,
        )
    ):
        if material not in materials[:i]:
            m_i = material + 1
            text.append("#---------------------------------------------------")
            text.append(f"# Material {m_i}")
            text.append("#---------------------------------------------------")
            text.append(f"material[{m_i}]:material-name = {name}")
            text.append(f"material[{m_i}]:material-element = {get_atom_species(name)}")
            text.append(f"material[{m_i}]:atomic-spin-moment={spin * g_factor} ! muB")
            text.append(f"material[{m_i}]:initial-spin-direction = random")
            text.append(f"material[{m_i}]:damping-constant = 0.1")
            text.append(f"material[{m_i}]:uniaxial-anisotropy-constant = 0.0")

    text.append("#---------------------------------------------------")

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(text))


def dump_vampire_ucf(
    spinham: SpinHamiltonian,
    filename,
    anisotropic=True,
    dmi=True,
    custom_mask=None,
    decimals=5,
    materials=None,
    no_logo=False,
) -> None:
    """
    Generates .UCF file for |Vampire|_.

    Parameters
    ----------

    spinham : :py:class:`.SpinHamiltonian`
        Spin Hamiltonian object to be saved.

    filename : str, optional
        Name for the .UCF file. Extension ".UCF" is added if not present.

    anisotropic : bool, default True
        Whether to output anisotropic exchange.

    dmi : bool, default True
        Whether to output DMI exchange.

    custom_mask : func, optional
        Custom mask for the exchange parameter. Function that takes (3, 3)
        :numpy:`ndarray` as an input and returns (3, 3) :numpy:`ndarray` as an output. If
        given, then ``anisotropic`` and ``dmi`` parameters are ignored.

        .. code-block:: python

            parameter_to_output = custom_mask(parameter)

    decimals : int, default 4
        Number of decimals to be printed (only for the exchange values).

    materials : list of int, optional
        List of materials for the atoms. Length is the same as the number of magnetic
        atoms in the ``spinham`` (``spinham.M``). Order is the same as in
        :py:attr:`.SpinHamiltonian.magnetic_atoms`. If none given, each magnetic atom is
        considered as a separate material. Material indices start from 0 and should
        contain all consecutive integers between 0 and number of materials. Number of
        materials cannot be higher than number of magnetic atoms.

    no_logo : bool, default False
        Whether to include the logo in the output files.

    Raises
    ------

    ValueError
        If ``materials`` list is given and its length is not equal to the number of
        magnetic atoms in the ``spinham``.

    ValueError
        If ``materials`` list does not contain all consecutive integers between 0 and
        the highest material index.

    Notes
    -----

    Examples of the correct ``materials`` list for 5 magnetic atoms

    .. code-block:: python

        [0, 0, 0, 0, 0]
        [1, 3, 2, 1, 0]
        [0, 1, 2, 3, 4]

    Examples of the incorrect ``materials`` list for 5 magnetic atoms

    .. code-block:: python

        [0, 6, 0, 0, 0]
        [1, 3, 3, 1, 0]
        [1, 2, 3, 4, 5]
    """

    if len(filename) < 4 or filename[-4:] != ".UCF":
        filename += ".UCF"

    materials = _verified_materials(materials, spinham.M)

    original_convention = spinham.convention
    spinham.convention = Convention.get_predefined(name="Vampire")

    if no_logo:
        text = []
    else:
        text = [logo(comment=True, date_time=True)]

    a, b, c, _, _, _ = get_params(spinham.cell)
    text.append("# Unit cell size:")
    text.append(f"{a:.8f} {b:.8f} {c:.8f}")
    text.append("# Unit cell lattice vectors:")
    text.append(
        f"{spinham.cell[0][0]:15.8f} {spinham.cell[0][1]:15.8f} {spinham.cell[0][2]:15.8f}"
    )
    text.append(
        f"{spinham.cell[1][0]:15.8f} {spinham.cell[1][1]:15.8f} {spinham.cell[1][2]:15.8f}"
    )
    text.append(
        f"{spinham.cell[2][0]:15.8f} {spinham.cell[2][1]:15.8f} {spinham.cell[2][2]:15.8f}"
    )
    text.append("# Atoms")
    text.append(f"{len(spinham.magnetic_atoms.names)} {len(np.unique(materials))}")

    for alpha in range(spinham.M):
        position = spinham.magnetic_atoms.positions[alpha]
        text.append(
            f"{alpha:<5} {position[0]:15.8f} {position[1]:15.8f} {position[2]:15.8f} {materials[alpha]:>5}"
        )

    text.append("# Interactions")
    text.append(f"{len(spinham.p22)} tensorial")

    IID = 0
    fmt = f"{7 + decimals}.{decimals}e"

    # Write (two spins & one site)
    for alpha, J in spinham.p21:
        alpha = spinham.map_to_magnetic[alpha]
        if custom_mask is not None:
            J = custom_mask(J)
        else:
            if not dmi:
                J -= to_dmi(J, matrix_form=True)
            if not anisotropic:
                J -= to_symm_anisotropy(J)
        J = J * (MILLI * ELECTRON_VOLT) / JOULE
        text.append(
            f"{IID:<5} {alpha:>3} {alpha:>3}  {0:>2} {0:>2} {0:>2}  "
            f"{J[0][0]:{fmt}} {J[0][1]:{fmt}} {J[0][2]:{fmt}} "
            f"{J[1][0]:{fmt}} {J[1][1]:{fmt}} {J[1][2]:{fmt}} "
            f"{J[2][0]:{fmt}} {J[2][1]:{fmt}} {J[2][2]:{fmt}}"
        )
        IID += 1

    # Write (two spins & two sites)
    bonds = []
    for alpha, beta, nu, J in spinham.p22:
        alpha = spinham.map_to_magnetic[alpha]
        beta = spinham.map_to_magnetic[beta]
        if custom_mask is not None:
            J = custom_mask(J)
        else:
            if not dmi:
                J -= to_dmi(J, matrix_form=True)
            if not anisotropic:
                J -= to_symm_anisotropy(J)
        # print(alpha, beta, nu)
        # print(J, end="\n\n")
        J = J * (MILLI * ELECTRON_VOLT) / JOULE
        r_alpha = np.array(spinham.magnetic_atoms.positions[alpha])
        r_beta = np.array(spinham.magnetic_atoms.positions[beta])

        distance = np.linalg.norm((r_beta - r_alpha + nu) @ spinham.cell)
        bonds.append([alpha, beta, nu, J, distance])

    bonds = sorted(bonds, key=lambda x: x[4])
    for alpha, beta, (i, j, k), J, _ in bonds:
        text.append(
            f"{IID:<5} {alpha:>3} {beta:>3}  {i:>2} {j:>2} {k:>2}  "
            f"{J[0][0]:{fmt}} {J[0][1]:{fmt}} {J[0][2]:{fmt}} "
            f"{J[1][0]:{fmt}} {J[1][1]:{fmt}} {J[1][2]:{fmt}} "
            f"{J[2][0]:{fmt}} {J[2][1]:{fmt}} {J[2][2]:{fmt}}"
        )
        IID += 1

    spinham.convention = original_convention

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(text))


# Populate __all__ with objects defined in this file
__all__ = list(set(dir()) - old_dir)
# Remove all semi-private objects
__all__ = [i for i in __all__ if not i.startswith("_")]
del old_dir
