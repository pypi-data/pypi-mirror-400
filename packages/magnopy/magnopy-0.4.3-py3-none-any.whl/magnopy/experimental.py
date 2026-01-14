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
import random
import numpy as np
from magnopy._plotly_engine import PlotlyEngine
from wulfric.crystal import get_vector
from magnopy._parameters._p22 import to_dmi, to_iso
from magnopy._spinham._hamiltonian import SpinHamiltonian

try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
    MATPLOTLIB_ERROR_MESSAGE = "If you see this message, please contact developers of the code (see magnopy.org)."
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    MATPLOTLIB_ERROR_MESSAGE = "\n".join(
        [
            "Installation of matplotlib is not found, can not produce .png files",
            "Please install matplotlib with",
            "",
            "    pip install matplotlib",
            "",
        ]
    )

from magnopy._constants._units import _MAGNON_ENERGY_UNITS


def plot_spinham(
    spinham: SpinHamiltonian,
    distance_digits=5,
    plot_dmi=True,
    dmi_vectors_scale=1,
    _sphinx_gallery_fix=False,
):
    r"""
    Visualizes spin Hamiltonian.

    .. warning::

        Experimental feature. Only 1, 21, 22 parameters are implemented.

    .. versionadded:: 0.2.0

    Parameters
    ----------
    spinham : :py:class:`.SpinHamiltonian`
        Spin Hamiltonian
    distance_digits : int, default 5
        Precision for comparing two linear distances.
    plot_dmi : bool, default True
        Whether to plot DMI vectors
    dmi_scale : float, default 1.0
        Scale for the maximum dmi vector length.

    Returns
    -------
    pe1 : :py:class:`.PlotlyEngine`
        Instance of the magnopy's plot engine, with plotted spin Hamiltonian. Ready to be
        saved or showed. Only on-site parameters are plotted
    pe2 : :py:class:`.PlotlyEngine`
        Instance of the magnopy's plot engine, with plotted spin Hamiltonian. Ready to be
        saved or showed. Only two-spins/two-sites parameters are plotted.
    """

    pe1 = PlotlyEngine(_sphinx_gallery_fix=_sphinx_gallery_fix)

    pe1.plot_cell(
        cell=spinham.cell,
        color="LightGrey",
        legend_label="(0, 0, 0) unit cell",
        legend_group="(0, 0, 0) unit cell",
    )

    points = spinham.magnetic_atoms.positions @ spinham.cell

    hoverinfo = [
        "<br>".join(
            [
                f'Magnetic center "{name}", located at',
                f"  Relative: ({pos[0]:.8f}, {pos[1]:.8f}, {pos[2]:.8f})",
                f"  Absolute: ({(pos @ spinham.cell)[0]:.8f}, {(pos @ spinham.cell)[1]:.8f}, {(pos @ spinham.cell)[2]:.8f})",
                "",
                f"With spin value {spin:.3f}",
                "",
                f"and g-factor {g_factor:.3f}",
            ]
        )
        for name, pos, spin, g_factor in zip(
            spinham.magnetic_atoms.names,
            spinham.magnetic_atoms.positions,
            spinham.magnetic_atoms.spins,
            spinham.magnetic_atoms.g_factors,
        )
    ]

    for alpha, parameter in spinham.p1:
        alpha = spinham.map_to_magnetic[alpha]

        hoverinfo[alpha] += "<br>".join(
            [
                "",
                "One-spin parameter:",
                f"  {parameter[0]:10.5f} {parameter[0]:10.5f} {parameter[0]:10.5f}",
                "",
            ]
        )

    for alpha, parameter in spinham.p21:
        alpha = spinham.map_to_magnetic[alpha]

        hoverinfo[alpha] += "<br>".join(
            [
                "",
                "Two-spin parameter:",
                f"  {parameter[0][0]:10.5f} {parameter[1][0]:10.5f} {parameter[2][0]:10.5f}",
                f"  {parameter[0][1]:10.5f} {parameter[1][1]:10.5f} {parameter[2][1]:10.5f}",
                f"  {parameter[0][2]:10.5f} {parameter[1][2]:10.5f} {parameter[2][2]:10.5f}",
                "",
            ]
        )

    with_parameters = []
    without_parameters = []

    for i, text in enumerate(hoverinfo):
        if text == "":
            without_parameters.append(i)
        else:
            with_parameters.append(i)

    xyz = points[with_parameters].T
    pe1.fig.add_traces(
        data=dict(
            type="scatter3d",
            mode="markers",
            legendgroup="with parameters",
            name="Magnetic cites with parameters\n(hover to see the values)",
            showlegend=True,
            x=xyz[0],
            y=xyz[1],
            z=xyz[2],
            marker=dict(size=10, color="Black"),
            text=[hoverinfo[i] for i in with_parameters],
            hoverinfo="text",
        ),
    )

    if len(without_parameters) != 0:
        xyz = points[without_parameters].T
        pe1.fig.add_traces(
            data=dict(
                type="scatter3d",
                mode="markers",
                legendgroup="without parameters",
                name="Magnetic cites without parameters",
                showlegend=True,
                x=xyz[0],
                y=xyz[1],
                z=xyz[2],
                marker=dict(size=5, color="Grey"),
                hoverinfo="none",
            ),
        )

    # Fix for plotly #7143
    points = points.T
    pe1._update_range(
        x_min=points[0].min(),
        x_max=points[0].max(),
        y_min=points[1].min(),
        y_max=points[1].max(),
        z_min=points[2].min(),
        z_max=points[2].max(),
    )

    pe2 = PlotlyEngine(_sphinx_gallery_fix=_sphinx_gallery_fix)

    start_points = []
    end_points = []
    parameters = []
    distances = []
    dmi_vectors = []
    dmi_positions = []
    alphas = []
    betas = []
    nus = []

    cells_to_plot = []
    for alpha, beta, nu, parameter in spinham.p22:
        vector = get_vector(
            cell=spinham.cell, atoms=spinham.atoms, atom1=alpha, atom2=beta, R=nu
        )
        start_points.append(spinham.atoms.positions[alpha] @ spinham.cell)
        end_points.append(start_points[-1] + vector)
        distances.append(round(np.linalg.norm(vector), ndigits=distance_digits))
        parameters.append(parameter)
        alphas.append(alpha)
        betas.append(beta)
        nus.append(nu)

        dmi_vectors.append(to_dmi(parameter=parameter))
        dmi_positions.append(start_points[-1] + vector / 2)

        if nu != (0, 0, 0):
            cells_to_plot.append(nu)

    indices = np.argsort(distances)

    start_points = np.array(start_points)[indices]
    end_points = np.array(end_points)[indices]
    parameters = np.array(parameters)[indices]
    distances = np.array(distances)[indices]
    dmi_positions = np.array(dmi_positions)[indices]
    dmi_vectors = np.array(dmi_vectors)[indices]
    alphas = np.array(alphas, dtype=int)[indices]
    betas = np.array(betas, dtype=int)[indices]
    nus = np.array(nus, dtype=int)[indices]

    dmi_max_length = np.array([np.linalg.norm(_) for _ in dmi_vectors]).max()

    if dmi_max_length != 0:
        dmi_vectors = dmi_vectors / dmi_max_length * dmi_vectors_scale

    unique_distances = np.unique(distances)

    chars = "0123456789ABCDEF"
    random_colors = [
        "#" + "".join(random.sample(chars, 6)) for _ in range(len(unique_distances))
    ]
    colors = dict(zip(unique_distances, random_colors))

    colors = [colors[_] for _ in distances]

    legend_labels = [f"d = {_:.{distance_digits}f}" for _ in unique_distances]

    legend_groups = dict(zip(unique_distances, legend_labels))
    legend_labels = dict(zip(unique_distances, legend_labels))

    hoverinfo = [
        "<br>".join(
            [
                "Bond",
                f'  from magnetic center "{spinham.atoms.names[alpha]}" in (0, 0, 0) unit cell',
                f'  to magnetic center "{spinham.atoms.names[beta]}" in ({nu[0]}, {nu[1]}, {nu[2]}) unit cell',
                "",
                "Full two-spins/two-sites parameter:",
                f"  {param[0][0]:10.5f} {param[0][1]:10.5f} {param[0][2]:10.5f}",
                f"  {param[1][0]:10.5f} {param[1][1]:10.5f} {param[1][2]:10.5f}",
                f"  {param[2][0]:10.5f} {param[2][1]:10.5f} {param[2][2]:10.5f}",
                "",
                f"Isotropic: {to_iso(param):10.5f}",
                "",
                f"DMI: {to_dmi(param)[0]:10.5f} {to_dmi(param)[1]:10.5f} {to_dmi(param)[2]:10.5f}",
            ]
        )
        for alpha, beta, nu, param in zip(alphas, betas, nus, parameters)
    ]

    legend_label = "Other_cells"
    magnetic_sites = []
    for i, j, k in cells_to_plot:
        shift = [i, j, k] @ spinham.cell
        pe2.plot_cell(
            cell=spinham.cell,
            legend_group="other cells",
            legend_label=legend_label,
            color="LightGrey",
            shift=shift,
            plot_vectors=False,
        )
        if legend_label is not None:
            legend_label = None

        magnetic_sites.extend(
            spinham.magnetic_atoms.positions @ spinham.cell + shift[np.newaxis, :]
        )
    pe2.plot_cell(
        cell=spinham.cell,
        legend_label="(0, 0, 0) unit cell",
        color="Grey",
        plot_vectors=True,
    )

    pe2.plot_points(
        points=magnetic_sites,
        colors="LightGrey",
        legend_group="Magnetic sites",
        scale=2,
    )
    pe2.plot_points(
        points=spinham.magnetic_atoms.positions @ spinham.cell,
        colors="Grey",
        legend_label="Magnetic sites",
        legend_group="Magnetic sites",
        scale=2,
    )

    for i in range(len(parameters)):
        x, y, z = np.array([start_points[i], end_points[i]]).T
        pe2.fig.add_traces(
            data=dict(
                type="scatter3d",
                mode="lines",
                legendgroup=legend_groups[distances[i]],
                name=legend_labels[distances[i]],
                showlegend=legend_labels[distances[i]] is not None,
                x=x,
                y=y,
                z=z,
                line=dict(color=colors[i], width=4),
                hoverinfo="text",
                text=hoverinfo[i],
            ),
        )
        if plot_dmi:
            pe2.plot_vector(
                start_point=dmi_positions[i] - dmi_vectors[i] / 2,
                end_point=dmi_positions[i] + dmi_vectors[i] / 2,
                color=colors[i],
                legend_group=legend_groups[distances[i]],
            )

        if legend_labels[distances[i]] is not None:
            legend_labels[distances[i]] = None

    return pe1, pe2


def change_cell(spinham, new_cell, new_atoms_specs):
    r"""
    Changes the unit cell of a spin Hamiltonian.

    .. warning::
        Experimental feature. Not tested well.

    Parameters
    ----------
    spinham : :py:class:`.SpinHamiltonian`
    new_cell : (3, 3) |array-like|_
    new_atoms_specs : list of tuple

        .. code-block:: python

            new_atoms_specs = [(index, nu), ...]

        where ``index`` is an index of an atom in ``spinham.atoms`` and ``nu = (i,j,k)``
        is the unit cell to which an atom belongs.

    Returns
    -------
    new_spinham : :py:class:`.SpinHamiltonian`
    """

    new_cell = np.array(new_cell)

    new_atoms = {}

    for key in spinham.atoms:
        new_atoms[key] = []

    for atom_index, (i, j, k) in new_atoms_specs:
        for key in spinham.atoms:
            if key == "positions":
                position = spinham.atoms.positions[atom_index]
                new_position = (
                    np.array([(position[0] + i), (position[1] + j), (position[2] + k)])
                    @ spinham.cell
                    @ np.linalg.inv(new_cell)
                )
                new_atoms["positions"].append(new_position)
            else:
                new_atoms[key].append(spinham.atoms[key][atom_index])

    map_to_indices = {
        tuple(np.around(new_atoms["positions"][i], decimals=2)): i
        for i in range(len(new_atoms["positions"]))
    }

    new_spinham = SpinHamiltonian(
        cell=new_cell, atoms=new_atoms, convention=spinham.convention
    )

    def get_new_indices(atom_index, ijk):
        i, j, k = ijk
        position = spinham.atoms.positions[atom_index]
        new_position = (
            np.array([(position[0] + i), (position[1] + j), (position[2] + k)])
            @ spinham.cell
            @ np.linalg.inv(new_cell)
        )

        new_ijk = new_position // 1

        new_ijk = tuple(map(int, new_ijk))

        new_index = map_to_indices[tuple(np.around(new_position % 1, decimals=2))]

        return new_index, new_ijk

    # Re-populate parameters
    for new_alpha, (atom_index, (i, j, k)) in enumerate(new_atoms_specs):
        # One spin
        for alpha, parameter in spinham._1:
            if alpha == atom_index:
                new_spinham.add_1(alpha=new_alpha, parameter=parameter)

        # Two spins
        for alpha, parameter in spinham._21:
            if alpha == atom_index:
                new_spinham.add_21(alpha=new_alpha, parameter=parameter)

        for alpha, beta, nu, parameter in spinham._22:
            if alpha == atom_index:
                new_beta, new_nu = get_new_indices(
                    atom_index=beta, ijk=np.array(nu) + (i, j, k)
                )

                new_spinham.add_22(
                    alpha=new_alpha,
                    beta=new_beta,
                    nu=new_nu,
                    parameter=parameter,
                    when_present="replace",
                )

        # Three spins
        for alpha, parameter in spinham._31:
            if alpha == atom_index:
                new_spinham.add_31(alpha=new_alpha, parameter=parameter)

        for alpha, beta, nu, parameter in spinham._32:
            if alpha == atom_index:
                new_beta, new_nu = get_new_indices(
                    atom_index=beta, ijk=np.array(nu) + (i, j, k)
                )

                new_spinham.add_32(
                    alpha=new_alpha,
                    beta=new_beta,
                    nu=new_nu,
                    parameter=parameter,
                    when_present="replace",
                )

        for alpha, beta, gamma, nu, _lambda, parameter in spinham._33:
            if alpha == atom_index:
                new_beta, new_nu = get_new_indices(
                    atom_index=beta, ijk=np.array(nu) + (i, j, k)
                )
                new_gamma, new_lambda = get_new_indices(
                    atom_index=gamma, ijk=np.array(_lambda) + (i, j, k)
                )

                new_spinham.add_33(
                    alpha=new_alpha,
                    beta=new_beta,
                    gamma=new_gamma,
                    nu=new_nu,
                    _lambda=new_lambda,
                    parameter=parameter,
                    when_present="replace",
                )

        # Four spins
        for alpha, parameter in spinham._41:
            if alpha == atom_index:
                new_spinham.add_41(alpha=new_alpha, parameter=parameter)

        for alpha, beta, nu, parameter in spinham._421:
            if alpha == atom_index:
                new_beta, new_nu = get_new_indices(
                    atom_index=beta, ijk=np.array(nu) + (i, j, k)
                )

                new_spinham.add_421(
                    alpha=new_alpha,
                    beta=new_beta,
                    nu=new_nu,
                    parameter=parameter,
                    when_present="replace",
                )

        for alpha, beta, nu, parameter in spinham._422:
            if alpha == atom_index:
                new_beta, new_nu = get_new_indices(
                    atom_index=beta, ijk=np.array(nu) + (i, j, k)
                )

                new_spinham.add_422(
                    alpha=new_alpha,
                    beta=new_beta,
                    nu=new_nu,
                    parameter=parameter,
                    when_present="replace",
                )

        for alpha, beta, gamma, nu, _lambda, parameter in spinham._43:
            new_beta, new_nu = get_new_indices(
                atom_index=beta, ijk=np.array(nu) + (i, j, k)
            )
            new_gamma, new_lambda = get_new_indices(
                atom_index=gamma, ijk=np.array(_lambda) + (i, j, k)
            )

            new_spinham.add_43(
                alpha=new_alpha,
                beta=new_beta,
                gamma=new_gamma,
                nu=new_nu,
                _lambda=new_lambda,
                parameter=parameter,
                when_present="replace",
            )

        for (
            alpha,
            beta,
            gamma,
            epsilon,
            nu,
            _lambda,
            rho,
            parameter,
        ) in spinham._44:
            new_beta, new_nu = get_new_indices(
                atom_index=beta, ijk=np.array(nu) + (i, j, k)
            )
            new_gamma, new_lambda = get_new_indices(
                atom_index=gamma, ijk=np.array(_lambda) + (i, j, k)
            )
            new_epsilon, new_rho = get_new_indices(
                atom_index=epsilon, ijk=np.array(rho) + (i, j, k)
            )

            new_spinham.add_44(
                alpha=new_alpha,
                beta=new_beta,
                gamma=new_gamma,
                epsilon=new_epsilon,
                nu=new_nu,
                _lambda=new_lambda,
                rho=new_rho,
                parameter=parameter,
                when_present="replace",
            )

    return new_spinham


# DEPRECATED in v0.4.0
# Remove in May 2026
def plot_dispersion(data, kp=None, output_filename=None, ylabel=None):
    r"""
    Plots some k-resolved data.

    .. deprecated:: 0.4.0
        Function deprecated in 0.4.0 and will be removed in May 2026. Use :py:func:`magnopy.io.plot_dispersion()` instead.

    If only the ``data`` are given, then an index of the omegas is used for abscissa (x
    axis).

    Parameters
    ----------
    data : (N, M) |array-like|_
        Some k-resolved data. N (:math:`\ge 1`) is the amount of kpoints. M is the
        number of data modes/entries.  Expected to be given in meV.
    kp : :py:class:`wulfric.Kpoints`, optional.
        Instance of the :py:class:`wulfric.Kpoints` class. It should be the same
        instance that were used in the preparation of the ``data``.
    output_filename : str, optional
        Name of the file for saving the image. If ``None``, then the graph would be
        opened in the interactive matplotlib window.
    ylabel : str, optional
        Label for the ordinate (y axis). Do not include units, units are included automatically.
    """

    import warnings

    warnings.warn(
        "Function magnopy.experimental.plot_dispersion() was deprecated in 0.4.0 and will be removed in May 2026. Use magnopy.io.plot_dispersion() instead",
        DeprecationWarning,
        stacklevel=2,
    )

    if not MATPLOTLIB_AVAILABLE:
        import warnings

        warnings.warn(MATPLOTLIB_ERROR_MESSAGE, RuntimeWarning, stacklevel=2)

        return

    data = np.array(data).T

    fig, ax = plt.subplots()

    if len(data.shape) == 2:
        for entry in data:
            if kp is not None:
                ax.plot(kp.flat_points(), entry, lw=1, color="#A47864")
            else:
                ax.plot(entry, lw=1, color="#A47864")
                ax.set_xlim(0, len(entry))
    else:
        if kp is not None:
            ax.plot(kp.flat_points(), data, lw=1, color="#A47864")
        else:
            ax.plot(data, lw=1, color="#A47864")
            ax.set_xlim(0, len(data))

    if kp is not None:
        ax.set_xticks(kp.ticks(), kp.labels, fontsize=13)
        ax.set_xlim(kp.ticks()[0], kp.ticks()[-1])
        ax.vlines(
            kp.ticks(),
            0,
            1,
            lw=0.5,
            color="grey",
            ls="dashed",
            zorder=0,
            transform=ax.get_xaxis_transform(),
        )

    if ylabel is not None:
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
