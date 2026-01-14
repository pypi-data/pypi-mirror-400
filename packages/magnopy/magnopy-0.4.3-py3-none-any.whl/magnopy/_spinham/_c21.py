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

from magnopy._data_validation import _validate_atom_index, _validated_units
from magnopy._constants._units import _PARAMETER_UNITS


@property
def _p21(spinham) -> list:
    r"""
    Parameters of (two spins & one site) term of the Hamiltonian.

    .. math::

        \boldsymbol{J}_{2,1}(\boldsymbol{r}_{\alpha})

    of the term

    .. math::

        C_{2,1}
        \sum_{\mu, \alpha, i, j}
        J^{ij}_{2,1}(\boldsymbol{r}_{\alpha})
        S_{\mu,\alpha}^i
        S_{\mu,\alpha}^j

    Returns
    -------

    parameters : list
        List of parameters. The list has a form of

        .. code-block:: python

            [[alpha, J], ...]

        ``0 <= len(parameters) <= len(spinham.atoms.names)``.

        where ``alpha`` is an index of the atom to which the parameter is assigned and
        ``J``  is a (3, ) :numpy:`ndarray`. The parameters are sorted by the index of an
        atom ``alpha`` in the ascending order.

    See Also
    --------

    add_21
    remove_21
    """

    return spinham._21


# ARGUMENT "replace" DEPRECATED since 0.4.0
# Remove in May of 2026
def _add_21(
    spinham,
    alpha: int,
    parameter,
    units=None,
    when_present="raise error",
    replace=None,
) -> None:
    r"""
    Adds a (two spins & one site) parameter to the Hamiltonian.

    Parameters
    ----------

    alpha : int
        Index of an atom, with which the parameter is associated.

        ``0 <= alpha < len(spinham.atoms.names)``.

    parameter : (3, ) |array-like|_
        Value of the parameter (:math:`3\times1` vector). Given in the units of ``units``.

    units : str, optional
        .. versionadded:: 0.3.0

        Units in which the ``parameter`` is given. Parameters have the the units of energy.
        By default assumes :py:attr:`.SpinHamiltonian.units`. For the list of the supported
        units see :ref:`user-guide_usage_units_parameter-units`. If given ``units`` are different from
        :py:attr:`.SpinHamiltonian.units`, then the parameter's value will be converted
        automatically from ``units`` to :py:attr:`.SpinHamiltonian.units`.

    when_present : str, default "raise error"
        .. versionadded:: 0.4.0

        Action to take if an atom already has a parameter associated with it.
        Case-insensitive. Supported values are:

        - ``"raise error"`` (default): raises an error if an atom already has a parameter
          associated with it.
        - ``"replace"``: replace existing value of the parameter with the new one.
        - ``"add"``: add the value of the parameter to the existing one.
        - ``"mean"``: replace the value of the parameter with the arithmetic mean of
          existing and new parameters.
        - ``"skip"``: Leave existing parameter unchanged and continue without raising an
          error.

    replace : bool, default False
        Whether to replace the value of the parameter if an atom already has a
        parameter associated with it.

        .. deprecated:: 0.4.0
            The ``replace`` argument will be removed in May of 2026. Use
            ``when_present="replace"`` instead.

    Raises
    ------

    ValueError
        If an atom already has a parameter associated with it and ``when_present="raise error"``.

    ValueError
        If ``when_present`` has an unsupported value.

    See Also
    --------

    p21
    remove_21
    """

    if replace is not None:
        import warnings

        warnings.warn(
            'The "replace" argument is deprecated since version 0.4.0 and will be removed in May of 2026. Use when_present="replace" instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        if replace:
            when_present = "replace"
        else:
            when_present = "raise error"

    _validate_atom_index(index=alpha, atoms=spinham.atoms)
    spinham._reset_internals()

    parameter = np.array(parameter)

    if units is not None:
        units = _validated_units(units=units, supported_units=_PARAMETER_UNITS)
        parameter = (
            parameter * _PARAMETER_UNITS[units] / _PARAMETER_UNITS[spinham._units]
        )

    # TODO BINARY SEARCH
    # Try to find the place for the new one inside the list
    index = 0
    while index < len(spinham._21):
        # If already present in the model
        if spinham._21[index][0] == alpha:
            # Either replace
            if when_present.lower() == "replace":
                spinham._21[index][1] = parameter
            # Or add
            elif when_present.lower() == "add":
                spinham._21[index][1] = spinham._21[index][1] + parameter
            # Or replace with mean value
            elif when_present.lower() == "mean":
                spinham._21[index][1] = (spinham._21[index][1] + parameter) / 2.0
            # Or do nothing
            elif when_present.lower() == "skip":
                pass
            # Or raise an error
            elif when_present.lower() == "raise error":
                raise ValueError(
                    f"(Two spins & one site) parameter is already set for atom {alpha} ('{spinham.atoms.names[alpha]}'."
                )
            else:
                raise ValueError(
                    f'Unsupported value of when_present: "{when_present}". Supported values are: "raise error", "replace", "add", "mean", "skip".'
                )

            return

        # If it should be inserted before current element
        if spinham._21[index][0] > alpha:
            spinham._21.insert(index, [alpha, parameter])
            return

        index += 1

    # If it should be inserted at the end or at the beginning of the list
    spinham._21.append([alpha, parameter])


def _remove_21(spinham, alpha: int) -> None:
    r"""
    Removes a (two spins & one site) parameter from the Hamiltonian.

    Parameters
    ----------

    alpha : int
        Index of an atom, with which the parameter is associated.

        ``0 <= alpha < len(spinham.atoms.names)``.

    See Also
    --------

    p21
    add_21
    """

    _validate_atom_index(index=alpha, atoms=spinham.atoms)

    for i in range(len(spinham._21)):
        # As the list is sorted, there is no point in resuming the search
        # when a larger element is found
        if spinham._21[i][0] > alpha:
            return

        if spinham._21[i][0] == alpha:
            del spinham._21[i]
            spinham._reset_internals()
            return
