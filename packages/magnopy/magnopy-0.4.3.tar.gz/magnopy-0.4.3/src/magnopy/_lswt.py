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

from magnopy._diagonalization import solve_via_colpa
from magnopy._exceptions import ColpaFailed
from magnopy._local_rf import span_local_rfs

from magnopy._data_validation import _validated_units
from magnopy._constants._units import _ENERGY_UNITS, _MAGNON_ENERGY_UNITS


# Save local scope at this moment
old_dir = set(dir())
old_dir.add("old_dir")


class LSWT:
    r"""
    Linear Spin Wave theory.

    It is created from some spin Hamiltonian and set of direction vectors, that defines
    the ground state.

    Parameters
    ----------

    spinham : :py:class:`.SpinHamiltonian`
        Spin Hamiltonian.

    spin_directions : (M, 3) |array-like|_
        Directions of spin vectors. Only directions of vectors are used, modulus is
        ignored. If spin Hamiltonian contains non-magnetic atom, then only the spin
        directions for the magnetic atoms are expected. The order of spin directions is
        the same as the order of magnetic atoms in
        :py:attr:`SpinHamiltonian.magnetic_atoms`. See Notes for more details.

    Attributes
    ----------

    z : (M, 3) :numpy:`ndarray`
        Spin directions (directions of local quantization axes).

    p : (M, 3) :numpy:`ndarray`
        Hybridized x and y components of the local coordinate system
        :math:`\mathbf{p} = \mathbf{x} + i \mathbf{y}`.

    M : int
        Number of spins in the unit cell

    cell : (3, 3) :numpy:`ndarray`
        Unit cell. Rows are vectors, columns are cartesian components.

    spins : (M, ) :numpy:`ndarray`
        Spin values of the magnetic centers.

    Notes
    -----

    Let the spin Hamiltonian contain three atoms Cr1, Br, Cr3 in that order. Assume that
    two atoms are magnetic (Cr1 and Cr3), one atom is not (Br). Then ``spin_directions``
    is a (2, 3) array with ``spin_directions[0]`` being the direction for spin of Cr1 and
    ``spin_directions[1]`` being the direction of spin for Cr3.

    Examples
    --------

    .. doctest::

        >>> import magnopy
        >>> spinham = magnopy.examples.cubic_ferro_nn()
        >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
    """

    def __init__(self, spinham, spin_directions):
        spin_directions = np.array(spin_directions, dtype=float)
        spin_directions /= np.linalg.norm(spin_directions, axis=1)[:, np.newaxis]

        x, y, self.z = span_local_rfs(
            directional_vectors=spin_directions, hybridize=False
        )
        self.p = x + 1j * y

        self.spins = np.array(spinham.magnetic_atoms.spins, dtype=float)

        initial_units = spinham.units
        initial_convention = spinham.convention

        spinham.units = "mev"
        spinham.convention = initial_convention.get_modified(
            spin_normalized=False, multiple_counting=True
        )

        self.M = spinham.M
        self.cell = spinham.cell

        ########################################################################
        #                    Renormalized one-spin parameter                   #
        ########################################################################
        self._J1 = np.zeros((self.M, 3), dtype=float)

        # One spin
        for alpha, parameter in spinham.p1:
            alpha = spinham.map_to_magnetic[alpha]
            self._J1[alpha] = self._J1[alpha] + spinham.convention.c1 * parameter

        # Two spins & one site
        for alpha, parameter in spinham.p21:
            alpha = spinham.map_to_magnetic[alpha]
            self._J1[alpha] = self._J1[alpha] + (
                2
                * spinham.convention.c21
                * np.einsum("ij,j->i", parameter, self.z[alpha])
                * self.spins[alpha]
            )

        # Two spins & two sites
        for alpha, beta, _, parameter in spinham.p22:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            self._J1[alpha] = self._J1[alpha] + (
                2
                * spinham.convention.c22
                * (parameter @ self.z[beta])
                * self.spins[beta]
            )

        # Three spins & one site
        for alpha, parameter in spinham.p31:
            alpha = spinham.map_to_magnetic[alpha]
            self._J1[alpha] = self._J1[alpha] + (
                3
                * spinham.convention.c31
                * np.einsum("iju,j,u->i", parameter, self.z[alpha], self.z[alpha])
                * self.spins[alpha] ** 2
            )

        # Three spins & two sites
        for alpha, beta, _, parameter in spinham.p32:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            self._J1[alpha] = self._J1[alpha] + (
                3
                * spinham.convention.c32
                * np.einsum("iju,j,u->i", parameter, self.z[alpha], self.z[beta])
                * self.spins[alpha]
                * self.spins[beta]
            )

        # Three spins & three sites
        for alpha, beta, gamma, _, _, parameter in spinham.p33:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            gamma = spinham.map_to_magnetic[gamma]
            self._J1[alpha] = self._J1[alpha] + (
                3
                * spinham.convention.c33
                * np.einsum("iju,j,u->i", parameter, self.z[beta], self.z[gamma])
                * self.spins[beta]
                * self.spins[gamma]
            )

        # Four spins & one site
        for alpha, parameter in spinham.p41:
            alpha = spinham.map_to_magnetic[alpha]
            self._J1[alpha] = self._J1[alpha] + (
                4
                * spinham.convention.c41
                * np.einsum(
                    "ijuv,j,u,v->i",
                    parameter,
                    self.z[alpha],
                    self.z[alpha],
                    self.z[alpha],
                )
                * self.spins[alpha] ** 3
            )

        # Four spins & two sites (1+3)
        for alpha, beta, _, parameter in spinham.p421:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            self._J1[alpha] = self._J1[alpha] + (
                4
                * spinham.convention.c421
                * np.einsum(
                    "ijuv,j,u,v->i",
                    parameter,
                    self.z[alpha],
                    self.z[alpha],
                    self.z[beta],
                )
                * self.spins[alpha] ** 2
                * self.spins[beta]
            )

        # Four spins & two sites (2+2)
        for alpha, beta, _, parameter in spinham.p422:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            self._J1[alpha] = self._J1[alpha] + (
                4
                * spinham.convention.c422
                * np.einsum(
                    "ijuv,j,u,v->i",
                    parameter,
                    self.z[alpha],
                    self.z[beta],
                    self.z[beta],
                )
                * self.spins[alpha]
                * self.spins[beta] ** 2
            )

        # Four spins & three sites
        for alpha, beta, gamma, _, _, parameter in spinham.p43:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            gamma = spinham.map_to_magnetic[gamma]
            self._J1[alpha] = self._J1[alpha] + (
                4
                * spinham.convention.c43
                * np.einsum(
                    "ijuv,j,u,v->i",
                    parameter,
                    self.z[alpha],
                    self.z[beta],
                    self.z[gamma],
                )
                * self.spins[alpha]
                * self.spins[beta]
                * self.spins[gamma]
            )

        # Four spins & four sites
        for alpha, beta, gamma, epsilon, _, _, _, parameter in spinham.p44:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            gamma = spinham.map_to_magnetic[gamma]
            epsilon = spinham.map_to_magnetic[epsilon]
            self._J1[alpha] = self._J1[alpha] + (
                4
                * spinham.convention.c44
                * np.einsum(
                    "ijuv,j,u,v->i",
                    parameter,
                    self.z[beta],
                    self.z[gamma],
                    self.z[epsilon],
                )
                * self.spins[beta]
                * self.spins[gamma]
                * self.spins[epsilon]
            )

        ########################################################################
        #                   Renormalized two-spins parameter                   #
        ########################################################################
        self._J2 = {}

        # First - terms with delta in from of them

        # Two spins & one site
        for alpha, parameter in spinham.p21:
            alpha = spinham.map_to_magnetic[alpha]
            if (0, 0, 0) not in self._J2:
                self._J2[(0, 0, 0)] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[(0, 0, 0)][alpha, alpha] += spinham.convention.c21 * parameter

        # Three spins & one site
        for alpha, parameter in spinham.p31:
            alpha = spinham.map_to_magnetic[alpha]
            if (0, 0, 0) not in self._J2:
                self._J2[(0, 0, 0)] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[(0, 0, 0)][alpha, alpha] += (
                3
                * spinham.convention.c31
                * np.einsum("iju,u->ij", parameter, self.z[alpha])
                * self.spins[alpha]
            )

        # Four spins & one site
        for alpha, parameter in spinham.p41:
            alpha = spinham.map_to_magnetic[alpha]
            if (0, 0, 0) not in self._J2:
                self._J2[(0, 0, 0)] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[(0, 0, 0)][alpha, alpha] += (
                6
                * spinham.convention.c41
                * np.einsum("ijuv,u,v->ij", parameter, self.z[alpha], self.z[alpha])
                * self.spins[alpha] ** 2
            )

        # Then all other parameters

        # Two spins & two sites
        for alpha, beta, nu, parameter in spinham.p22:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            if nu not in self._J2:
                self._J2[nu] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[nu][alpha, beta] += spinham.convention.c22 * parameter

        # Three spins & two sites
        for alpha, beta, nu, parameter in spinham.p32:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            if nu not in self._J2:
                self._J2[nu] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[nu][alpha, beta] += (
                3
                * spinham.convention.c32
                * np.einsum("iuj,u->ij", parameter, self.z[alpha])
                * self.spins[alpha]
            )

        # Three spins & three sites
        for alpha, beta, gamma, nu, _, parameter in spinham.p33:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            gamma = spinham.map_to_magnetic[gamma]
            if nu not in self._J2:
                self._J2[nu] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[nu][alpha, beta] += (
                3
                * spinham.convention.c33
                * np.einsum("iju,u->ij", parameter, self.z[gamma])
                * self.spins[gamma]
            )

        # Four spins & two sites (1+3)
        for alpha, beta, nu, parameter in spinham.p421:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            if nu not in self._J2:
                self._J2[nu] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[nu][alpha, beta] += (
                6
                * spinham.convention.c421
                * np.einsum("iuvj,u,v->ij", parameter, self.z[alpha], self.z[alpha])
                * self.spins[alpha] ** 2
            )

        # Four spins & two sites (2+2)
        for alpha, beta, nu, parameter in spinham.p422:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            if nu not in self._J2:
                self._J2[nu] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[nu][alpha, beta] += (
                6
                * spinham.convention.c422
                * np.einsum("iujv,u,v->ij", parameter, self.z[alpha], self.z[beta])
                * self.spins[alpha]
                * self.spins[beta]
            )

        # Four spins & three sites
        for alpha, beta, gamma, nu, _, parameter in spinham.p43:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            gamma = spinham.map_to_magnetic[gamma]
            if nu not in self._J2:
                self._J2[nu] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[nu][alpha, beta] += (
                6
                * spinham.convention.c43
                * np.einsum("iujv,u->ij", parameter, self.z[alpha], self.z[gamma])
                * self.spins[alpha]
                * self.spins[gamma]
            )

        # Four spins & four sites
        for alpha, beta, gamma, epsilon, nu, _, _, parameter in spinham.p44:
            alpha = spinham.map_to_magnetic[alpha]
            beta = spinham.map_to_magnetic[beta]
            gamma = spinham.map_to_magnetic[gamma]
            epsilon = spinham.map_to_magnetic[epsilon]
            if nu not in self._J2:
                self._J2[nu] = np.zeros((self.M, self.M, 3, 3), dtype=float)

            self._J2[nu][alpha, beta] += (
                6
                * spinham.convention.c44
                * np.einsum("ijuv,u->ij", parameter, self.z[gamma], self.z[epsilon])
                * self.spins[gamma]
                * self.spins[epsilon]
            )

        spinham.units = initial_units
        spinham.convention = initial_convention

        self.A1 = 0.5 * np.sum(self._J1 * self.z, axis=1)

        self.A2 = {}
        self.B2 = {}

        for nu in self._J2:
            self.A2[nu] = 0.5 * np.einsum(
                "abij,a,b,ai,bj->ab",
                self._J2[nu],
                np.sqrt(self.spins),
                np.sqrt(self.spins),
                self.p,
                np.conjugate(self.p),
            )
            self.B2[nu] = 0.5 * np.einsum(
                "abij,a,b,ai,bj->ab",
                self._J2[nu],
                np.sqrt(self.spins),
                np.sqrt(self.spins),
                np.conjugate(self.p),
                np.conjugate(self.p),
            )

    def E_2(self, units="meV") -> float:
        r"""
        Computes the correction to the ground state energy that arises from the LSWT.

        Parameters
        ----------

        units : str, default "meV"
            .. versionadded:: 0.3.0

            Units of energy. See :ref:`user-guide_usage_units_energy-units` for the full
            list of supported units.

        Returns
        -------

        E_2 : float

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> # Default units are meV
            >>> lswt.E_2()
            -1.5
        """

        result = float(0.5 * np.sum(self._J1 * self.z))

        # Convert units if necessary
        if units != "meV":
            units = _validated_units(units=units, supported_units=_ENERGY_UNITS)
            result = result * _ENERGY_UNITS["mev"] / _ENERGY_UNITS[units]

        return result

    def O(self, units="meV"):  # noqa E743
        r"""
        Computes coefficient of the one-operator terms.

        Parameters
        ----------

        units : str, default "meV"
            .. versionadded:: 0.3.0

            Units of energy. See :ref:`user-guide_usage_units_energy-units` for the full
            list of supported units.


        Returns
        -------

        O : (M, ) :numpy:`ndarray`
            Elements are complex numbers.

        Notes
        -----

        Before the diagonalization, the magnon Hamiltonian has the form

        .. math::

            \mathcal{H}
            =
            \dots
            +
            \sqrt{N}
            \sum_{\alpha}
            \Bigl(
            O_{\alpha}
            a_{\alpha}(\boldsymbol{0})
            +
            \overline{O_{\alpha}}
            a^{\dagger}_{\alpha}(\boldsymbol{0})
            \Bigr)
            +
            \dots

        where overline denotes complex conjugation. This function computes the
        coefficients :math:`O_{\alpha}`.

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> lswt.O()
            array([0.+0.j])
        """

        result = np.einsum(
            "a,ai,ai->a",
            np.sqrt(self.spins) / np.sqrt(2),
            np.conjugate(self.p),
            self._J1,
        )

        # Convert units if necessary
        if units != "meV":
            units = _validated_units(units=units, supported_units=_ENERGY_UNITS)
            result = result * _ENERGY_UNITS["mev"] / _ENERGY_UNITS[units]

        return result

    def A(self, k, relative=False, units="meV"):
        r"""
        Computes part of the grand dynamical matrix.

        Parameters
        ----------

        k : (3,) |array-like|_
            Reciprocal vector

        relative : bool, default False
            If ``relative=True``, then ``k`` is interpreted as given relative to the
            reciprocal unit cell. Otherwise it is interpreted as given in absolute
            coordinates.

        units : str, default "meV"
            .. versionadded:: 0.3.0

            Units of energy. See :ref:`user-guide_usage_units_energy-units` for the full
            list of supported units.


        Returns
        -------

        A : (M, M) :numpy:`ndarray`
            :math:`A_{\alpha\beta}(\boldsymbol{k})`.

        Notes
        -----

        Before the diagonalization, the magnon Hamiltonian has the form

        .. math::

            \mathcal{H}
            =
            \dots
            +
            \sum_{\boldsymbol{k}, \alpha}
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})^{\dagger}
            \begin{pmatrix}
            \boldsymbol{A}(\boldsymbol{k}) & \boldsymbol{B}^{\dagger}(\boldsymbol{k}) \\
            \boldsymbol{B}(\boldsymbol{k}) & \overline{\boldsymbol{A}(-\boldsymbol{k})}
            \end{pmatrix}
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})

        where

        .. math::
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})
            =
            \begin{pmatrix}
            a_1(\boldsymbol{k}),
            \dots,
            a_M(\boldsymbol{k}),
            a^{\dagger}_1(-\boldsymbol{k}),
            \dots,
            a^{\dagger}_M(-\boldsymbol{k}),
            \end{pmatrix}

        This function computes the matrix :math:`\boldsymbol{A}(\boldsymbol{k})`.

        See Also
        --------

        LSWT.B
        LSWT.GDM

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> lswt.A(k=[0, 0, 0.5], relative=True)
            array([[1.+0.j]])
        """

        k = np.array(k)

        result = np.zeros((self.M, self.M), dtype=complex)

        for nu in self.A2:
            if relative:
                phase = 2 * np.pi * (k @ nu)
            else:
                phase = k @ (nu @ self.cell)
            result = result + self.A2[nu] * np.exp(1j * phase)

        result = result - np.diag(self.A1)

        # Convert units if necessary
        if units != "meV":
            units = _validated_units(units=units, supported_units=_ENERGY_UNITS)
            result = result * _ENERGY_UNITS["mev"] / _ENERGY_UNITS[units]

        return result

    def B(self, k, relative=False, units="meV"):
        r"""
        Computes part of the grand dynamical matrix.

        Parameters
        ----------

        k : (3,) |array-like|_
            Reciprocal vector.

        relative : bool, default False
            If ``relative=True``, then ``k`` is interpreted as given relative to the
            reciprocal unit cell. Otherwise it is interpreted as given in absolute
            coordinates.

        units : str, default "meV"
            .. versionadded:: 0.3.0

            Units of energy. See :ref:`user-guide_usage_units_energy-units` for the full
            list of supported units.


        Returns
        -------

        B : (M, M) :numpy:`ndarray`
            :math:`B_{\alpha\beta}(\boldsymbol{k})`.

        Notes
        -----

        Before the diagonalization, the magnon Hamiltonian has the form

        .. math::

            \mathcal{H}
            =
            \dots
            +
            \sum_{\boldsymbol{k}, \alpha}
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})^{\dagger}
            \begin{pmatrix}
            \boldsymbol{A}(\boldsymbol{k}) & \boldsymbol{B}^{\dagger}(\boldsymbol{k}) \\
            \boldsymbol{B}(\boldsymbol{k}) & \overline{\boldsymbol{A}(-\boldsymbol{k})}
            \end{pmatrix}
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})

        where

        .. math::
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})
            =
            \begin{pmatrix}
            a_1(\boldsymbol{k}),
            \dots,
            a_M(\boldsymbol{k}),
            a^{\dagger}_1(-\boldsymbol{k}),
            \dots,
            a^{\dagger}_M(-\boldsymbol{k}),
            \end{pmatrix}

        This function computes the matrix :math:`\boldsymbol{B}(\boldsymbol{k})`.

        See Also
        --------

        LSWT.A
        LSWT.GDM

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> lswt.B(k=[0, 0, 0.5], relative=True)
            array([[0.+0.j]])
        """

        k = np.array(k)

        result = np.zeros((self.M, self.M), dtype=complex)

        for nu in self.B2:
            if relative:
                phase = 2 * np.pi * (k @ nu)
            else:
                phase = k @ (nu @ self.cell)
            result = result + self.B2[nu] * np.exp(1j * phase)

        # Convert units if necessary
        if units != "meV":
            units = _validated_units(units=units, supported_units=_ENERGY_UNITS)
            result = result * _ENERGY_UNITS["mev"] / _ENERGY_UNITS[units]

        return result

    def GDM(self, k, relative=False, units="meV"):
        r"""
        Computes grand dynamical matrix.

        Parameters
        ----------

        k : (3,) |array-like|_
            Reciprocal vector.

        relative : bool, default False
            If ``relative=True``, then ``k`` is interpreted as given relative to the
            reciprocal unit cell. Otherwise it is interpreted as given in absolute
            coordinates.

        units : str, default "meV"
            .. versionadded:: 0.3.0

            Units of energy. See :ref:`user-guide_usage_units_energy-units` for the full
            list of supported units.


        Returns
        -------

        gdm : (2M, 2M) :numpy:`ndarray`
            Gran dynamical matrix.

        Notes
        -----

        Before the diagonalization, the magnon Hamiltonian has the form

        .. math::

            \mathcal{H}
            =
            \dots
            +
            \sum_{\boldsymbol{k}, \alpha}
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})^{\dagger}
            \begin{pmatrix}
            \boldsymbol{A}(\boldsymbol{k}) & \boldsymbol{B}^{\dagger}(\boldsymbol{k}) \\
            \boldsymbol{B}(\boldsymbol{k}) & \overline{\boldsymbol{A}(-\boldsymbol{k})}
            \end{pmatrix}
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})

        where

        .. math::
            \boldsymbol{\mathcal{A}}(\boldsymbol{k})
            =
            \begin{pmatrix}
            a_1(\boldsymbol{k}),
            \dots,
            a_M(\boldsymbol{k}),
            a^{\dagger}_1(-\boldsymbol{k}),
            \dots,
            a^{\dagger}_M(-\boldsymbol{k}),
            \end{pmatrix}

        This function computes the grand dynamical matrix
        :math:`\boldsymbol{D}(\boldsymbol{k})`

        .. math::

            \boldsymbol{D}(\boldsymbol{k})
            =
            \begin{pmatrix}
            \boldsymbol{A}(\boldsymbol{k}) & \boldsymbol{B}^{\dagger}(\boldsymbol{k}) \\
            \boldsymbol{B}(\boldsymbol{k}) & \overline{\boldsymbol{A}(-\boldsymbol{k})}
            \end{pmatrix}

        See Also
        --------

        LSWT.A
        LSWT.B

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> lswt.GDM(k=[0,0,0.5], relative=True) # doctest: +SKIP
            array([[1.+0.j, 0.-0.j],
                   [0.+0.j, 1.-0.j]])
        """

        k = np.array(k, dtype=float)

        A = self.A(k=k, relative=relative, units=units)
        A_m = self.A(k=-k, relative=relative, units=units)

        B = self.B(k=k, relative=relative, units=units)

        left = np.concatenate((A, np.conjugate(B).T), axis=0)
        right = np.concatenate((B, np.conjugate(A_m)), axis=0)
        gdm = np.concatenate((left, right), axis=1)

        return gdm

    def diagonalize(self, k, relative=False, units="meV"):
        r"""
        Diagonalizes the Hamiltonian for the given ``k`` point.

        Parameters
        ----------

        k : (3,) |array-like|_
            Reciprocal vector.

        relative : bool, default False
            If ``relative=True``, then ``k`` is interpreted as given relative to the
            reciprocal unit cell. Otherwise it is interpreted as given in absolute
            coordinates.

        units : str, default "meV"
            .. versionadded:: 0.3.0

            Units of energy. See :ref:`user-guide_usage_units_magnon-energy-units` for the
            full list of supported units.

        Returns
        -------

        omegas : (M, ) :numpy:`ndarray`
            Array of omegas. Note, that data type is complex. If the ground state is
            correct, then the complex part should be zero.

        delta : float
            Constant energy term that results from diagonalization. Note, that data type
            is complex. If the ground state is correct, then the complex part should be
            zero.

        G : (M, 2M) :numpy:`ndarray`
            Transformation matrix from the original boson operators.

            .. math::

                \begin{pmatrix}
                    b_1(\boldsymbol{k}) \\
                    \dots \\
                    b_M(\boldsymbol{k}) \\
                \end{pmatrix}
                =
                \mathcal{G}
                \begin{pmatrix}
                    a_1(\boldsymbol{k}) \\
                    \dots \\
                    a_M(\boldsymbol{k}) \\
                    a^{\dagger}_1(-\boldsymbol{k}) \\
                    \dots \\
                    a^{\dagger}_M(-\boldsymbol{k}) \\
                \end{pmatrix}

        See Also
        --------

        LSWT.omega
        LSWT.delta
        LSWT.G

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> lswt.diagonalize(k=[0, 0, 0.5], relative=True) # doctest: +SKIP
            (array([2.+0.j]), 0j, array([[1.+0.j, 0.+0.j]]))
        """

        GDM = self.GDM(np.array(k, dtype=float), relative=relative)

        # Diagonalize via Colpa's method
        try:
            E, G = solve_via_colpa(GDM)
        except ColpaFailed:
            # Try to diagonalize with suspected Goldstone mode
            try:
                E, G = solve_via_colpa(
                    GDM + (1e-10) * np.eye(GDM.shape[0], dtype=float),
                )
            # Return NaNs if it still fails
            except ColpaFailed:
                # Try to diagonalize for the negative GDMs
                # Note: solve_via_colpa will return positive eigenvalues,
                # so we need to negate them back
                try:
                    E, G = solve_via_colpa(-GDM)
                    E = -E
                except ColpaFailed:
                    return (
                        [np.nan for _ in range(self.M)],
                        np.nan,
                        [[np.nan for _ in range(2 * self.M)] for _ in range(self.M)],
                    )

        # Convert units if necessary
        if units != "meV":
            units = _validated_units(units=units, supported_units=_MAGNON_ENERGY_UNITS)
            tmp_factor = _MAGNON_ENERGY_UNITS["mev"] / _MAGNON_ENERGY_UNITS[units]
            E = E * tmp_factor

        # Factor of two explained in the paper (TODO: add doi after publication)
        energies = E[: self.M] * 2
        transformation_matrices = G[: self.M]

        return (
            energies,  # energies (M)
            complex(0.5 * (np.sum(E[self.M :]) - np.sum(E[: self.M]))),  # delta term
            transformation_matrices,  # transformation matrix (M x 2M)
        )

    def omega(self, k, relative=False, units="meV"):
        r"""
        Computes magnon's eigenenergies at the given ``k`` point.

        Parameters
        ----------

        k : (3,) |array-like|_
            Reciprocal vector.

        relative : bool, default False
            If ``relative=True``, then ``k`` is interpreted as given relative to the
            reciprocal unit cell. Otherwise it is interpreted as given in absolute
            coordinates.

        units : str, default "meV"
            .. versionadded:: 0.3.0

            Units of energy. See :ref:`user-guide_usage_units_magnon-energy-units` for the
            full list of supported units.


        Returns
        -------
        omegas : (M, ) :numpy:`ndarray`
            Array of omegas. Note, that data type is complex. If the ground state is correct,
            then the complex part should be zero.

        See Also
        --------

        LSWT.diagonalize
        LSWT.delta

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> lswt.omega(k=[0, 0, 0.5], relative=True)
            array([2.+0.j])
        """

        return self.diagonalize(k=k, relative=relative, units=units)[0]

    def delta(self, k, relative=False, units="meV"):
        r"""
        Computes constant delta term of the diagonalized Hamiltonian.

        .. math::

            \sum_{\boldsymbol{k}}\Delta(\boldsymbol{k})

        Parameters
        ----------

        k : (3,) |array-like|_
            Reciprocal vector.

        relative : bool, default False
            If ``relative=True``, then ``k`` is interpreted as given relative to the
            reciprocal unit cell. Otherwise it is interpreted as given in absolute
            coordinates.

        units : str, default "meV"
            .. versionadded:: 0.3.0

            Units of energy. See :ref:`user-guide_usage_units_magnon-energy-units` for the
            full list of supported units.


        Returns
        -------

        delta : float
            Constant energy term that results from diagonalization. Note, that data type is complex. If the ground state is correct,
            then the complex part should be zero.

        See Also
        --------

        LSWT.diagonalize
        LSWT.omega

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> lswt.delta(k=[0, 0, 0.5], relative=True)
            0j
        """
        return self.diagonalize(k=k, relative=relative, units=units)[1]

    def G(self, k, relative=False):
        r"""
        Computes transformation matrix to the new bosonic operators.

        .. math::

            b_{\alpha}(\boldsymbol{k})
            =
            \sum_{\beta}
            (\mathcal{G})_{\alpha, \beta}(\boldsymbol{k})
            \mathcal{A}_{\beta}(\boldsymbol{k})

        Parameters
        ----------

        k : (3,) |array-like|_
            Reciprocal vector

        relative : bool, default False
            If ``relative=True``, then ``k`` is interpreted as given relative to the
            reciprocal unit cell. Otherwise it is interpreted as given in absolute
            coordinates.

        Returns
        -------

        G : (M, 2M) :numpy:`ndarray`
            Transformation matrix from the original boson operators.

        See Also
        --------

        LSWT.diagonalize
        LSWT.omega
        LSWT.delta

        Examples
        --------

        .. doctest::

            >>> import magnopy
            >>> spinham = magnopy.examples.cubic_ferro_nn()
            >>> lswt = magnopy.LSWT(spinham=spinham, spin_directions=[[0, 0, 1]])
            >>> lswt.G(k=[0, 0, 0.5], relative=True)  # doctest: +SKIP
            array([[1.+0.j, 0.+0.j]])
        """
        return self.diagonalize(k=k, relative=relative)[2]

    # REMOVED in v0.2.0. Warning will be removed in March of 2026
    def G_inv(self, *args, **kwargs):
        r"""
        This method was removed in v0.2.0 in favor of LSWT.G.

        Raises
        ------
        DeprecationWarning
            This method was removed in v0.2.0 in favor of :py:meth:`.LSWT.G`.
        """
        raise DeprecationWarning("This method was removed in v0.2.0 in favor of LSWT.G")


# Populate __all__ with objects defined in this file
__all__ = list(set(dir()) - old_dir)
# Remove all semi-private objects
__all__ = [i for i in __all__ if not i.startswith("_")]
del old_dir
