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

import warnings
import numpy as np


try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    MATPLOTLIB_WARNING_MESSAGE = "Matplotlib is not available. Please install 'magnopy[visual]' or matplotlib itself."

from magnopy._constants._units import _MAGNON_ENERGY_UNITS


def plot_dispersion(
    modes,
    x_data=None,
    ticks=None,
    labels=None,
    output_filename=None,
    ylabel="Energy",
    colors=None,
) -> None:
    r"""
    Plot dispersion curves.

    Input data (``modes``) are expected in meV. meV converted into THz for the twin axis
    via

    .. math::
        E = h \nu

    Parameters
    ----------

    modes : (M,) or (N, M) |array-like|_
        Dispersion data, Either one or :math:`N` modes with :math:`M` points each.

    x_data : (M,) |array-like|_, optional
        Abscissa (x axis) data. If ``None``, then integer indices would
        be used.

    ticks : (K,) |array-like|_, optional
        Positions of high-symmetry points along the x axis. If ``None``, then
        no high-symmetry points would be marked. coordinates are interpreted
        together with ``x_data``, whether the latter is provided or not.

    labels : (K,) list of str, optional
        Labels of high-symmetry points.

    output_filename : str, optional
        Name of the file for saving the image. If ``None``, then the graph would be
        opened in the interactive matplotlib window.

    ylabel : str, default "Energy"
        Label for the ordinate (y axis). Do not include units, units are included
        automatically - meV for primary axis and THz for twin axis.

    colors : "random" or (N,) |array-like|_, optional
        Colors for each mode. If "random", random colors are assigned. If ``None``, then a
        default color is used for all modes.

    Raises
    ------

    ValueError
        If shapes of ``x_data`` and ``modes`` are incompatible, i. e.
        ``x_data.shape[0] != modes.shape[1]``.

    ValueError
        If lengths of ``ticks`` and ``labels`` are incompatible, i. e.
        ``len(ticks) != len(labels)``.

    ValueError
        If length of ``colors`` is incompatible with number of modes, i. e.
        ``len(colors) != modes.shape[0]``.

    Notes
    -----

    If ``matplotlib`` is not available, a warning is issued and the function plots
    nothing.

    * If ``ticks`` is given and ``labels`` is not, labels are filled as ``K1, K2, ...``.
    * If ``labels`` is given and ``ticks`` is not, ``labels`` is ignored.
    * If both ``ticks`` and ``labels`` are not given, no high-symmetry points are marked.
    """

    if not MATPLOTLIB_AVAILABLE:
        warnings.warn(MATPLOTLIB_WARNING_MESSAGE, RuntimeWarning, stacklevel=2)
        return

    modes = np.array(modes)

    if len(modes.shape) == 1:
        modes = modes[np.newaxis, :]

    if x_data is None:
        x_data = np.arange(modes.shape[1])
    else:
        x_data = np.array(x_data)

    if x_data.shape[0] != modes.shape[1]:
        raise ValueError(
            f"Incompatible shapes between x_data ({x_data.shape}) and modes ({modes.shape}): {x_data.shape[0]} != {modes.shape[1]}."
        )

    if ticks is not None and labels is None:
        labels = [f"K{i + 1}" for i in range(len(ticks))]

    if ticks is not None and len(labels) != len(ticks):
        raise ValueError(
            f"Incompatible lengths between ticks ({len(ticks)}) and labels ({len(labels)}): {len(ticks)} != {len(labels)}."
        )

    if colors is None:
        colors = ["#A47864" for _ in range(modes.shape[0])]
    elif colors == "random":
        import random

        colors = []
        for _ in range(modes.shape[0]):
            color = "#"
            for _ in range(6):
                color += random.choice("0123456789ABCDEF")
            colors.append(color)
    elif len(colors) != modes.shape[0]:
        raise ValueError(
            f"Incompatible length of colors ({len(colors)}) and number of modes ({modes.shape[0]}): {len(colors)} != {modes.shape[0]}."
        )

    fig, ax = plt.subplots()

    for mode, color in zip(modes, colors):
        ax.plot(x_data, mode, lw=1, color=color)

    if ticks is not None:
        ax.set_xticks(ticks=ticks, labels=labels, fontsize=13)
        ax.vlines(
            ticks,
            0,
            1,
            lw=0.5,
            color="grey",
            ls="dashed",
            zorder=0,
            transform=ax.get_xaxis_transform(),
        )
    else:
        ax.set_xticks([], [])
        ax.set_xlabel("k-points (arbitrary units)", fontsize=15)

    ax.set_xlim(x_data[0], x_data[-1])
    ax.set_ylabel(f"{ylabel}, meV", fontsize=15)

    ax.hlines(
        0,
        0,
        1,
        lw=0.5,
        color="grey",
        linestyle="dashed",
        transform=ax.get_yaxis_transform(),
    )

    # Add twin axis

    ylims = ax.get_ylim()

    meV_to_THz = _MAGNON_ENERGY_UNITS["mev"] / _MAGNON_ENERGY_UNITS["thz"]

    twinax = ax.twinx()

    twinax.set_ylim(meV_to_THz * ylims[0], meV_to_THz * ylims[1])

    twinax.set_ylabel(f"{ylabel}, THz", fontsize=15)

    if output_filename is not None:
        plt.savefig(output_filename, dpi=400, bbox_inches="tight")
    else:
        plt.show()

    plt.close()
