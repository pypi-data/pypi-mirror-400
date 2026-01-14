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

import pytest
import numpy as np
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays as harrays

from magnopy._diagonalization import _check_grand_dynamical_matrix, _inverse_by_colpa


from magnopy import solve_via_colpa
from magnopy import ColpaFailed


@pytest.mark.parametrize(
    "D",
    [
        [[1]],
        [1],
        [1, 2, 3],
        [[[1]]],
        [[1, 2, 3]],
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    ],
)
def test_check_grand_dynamical_matrix_valid_fails(D):
    with pytest.raises(ValueError):
        _check_grand_dynamical_matrix(D=D)


@pytest.mark.parametrize(
    "D, expected_N",
    [([[1, 0], [0, 1]], 1), (np.ones((6, 6)), 3)],
)
def test_check_grand_dynamical_matrix_valid_passes(D, expected_N):
    D_new, N = _check_grand_dynamical_matrix(D=D)
    assert N == expected_N
    assert np.allclose(D_new, D)


@given(
    D=harrays(
        dtype=np.complex128,
        shape=(2, 2),
        elements=st.complex_numbers(
            min_magnitude=0, max_magnitude=10, allow_subnormal=False
        ),
    )
)
def test_solve_via_colpa_2_x_2(D):
    # Small addition - to avoid dealing with finite precision issues
    D = (D + D.conj().T) / 2 + 1e-10 * np.eye(2)

    try:
        E, G = solve_via_colpa(D)

        E_prime = np.linalg.inv(np.conjugate(G).T) @ D @ np.linalg.inv(G)
        assert np.allclose(np.diag(E), E_prime)

        E_prime = _inverse_by_colpa(np.conjugate(G).T) @ D @ _inverse_by_colpa(G)
        assert np.allclose(np.diag(E), E_prime)

    except ColpaFailed:
        pass
