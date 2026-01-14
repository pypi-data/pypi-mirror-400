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


import numpy as np

# Save local scope at this moment
old_dir = set(dir())
old_dir.add("old_dir")


def read_spin_directions(filename: str):
    r"""
    Reads spin directions from the file.

    Parameters
    ----------

    filename : str
        File with the spin directions. See notes for the details of its content.

    Returns
    -------

    spin_directions : (M, ) :numpy:`ndarray`
        Array with the spin directions. Each row is a spin direction vector normalized to
        1.


    Notes
    -----

    The file is expected to contain three numbers per line, here is an example for two
    spins

    .. code-block:: text

        S1_x S1_y S1_z
        S2_x S2_y S2_z

    Only the direction of the spin vector is recognized, the modulus is ignored. Comments
    are allowed at any place of the file and preceded by the symbol "#". If the symbol "#"
    is found, then the rest of the line is ignored. Here are examples of valid use of the
    comments

    .. code-block:: text

        # Spin vectors for the material XX
        S1_x S1_y S1_z # Atom X1
        # This comments is here by some reason
        S2_x S2_y S2_z # Atom X2

    """

    spin_directions = []
    with open(filename, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            # Remove comment lines
            if line.startswith("#"):
                continue
            # Remove inline comments and leading/trailing whitespaces
            line = line.split("#")[0].strip()
            # Check for empty lines
            if line:
                line = line.split()
                if len(line) != 3:
                    raise ValueError(
                        f"Expected three numbers per line (in line {i + 1}), got: {len(line)}."
                    )
                spin_directions.append(list(map(float, line)))

    spin_directions = np.array(spin_directions, dtype=float)
    # Normalize the spin directions
    spin_directions = (
        spin_directions / np.linalg.norm(spin_directions, axis=1)[:, np.newaxis]
    )

    return spin_directions


# Populate __all__ with objects defined in this file
__all__ = list(set(dir()) - old_dir)
# Remove all semi-private objects
__all__ = [i for i in __all__ if not i.startswith("_")]
del old_dir
