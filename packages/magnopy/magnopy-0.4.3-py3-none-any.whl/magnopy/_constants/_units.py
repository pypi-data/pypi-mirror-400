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
from magnopy._constants._si import (
    BOLTZMANN_CONSTANT,
    ELECTRON_VOLT,
    JOULE,
    KELVIN,
    MILLI,
    RYDBERG_ENERGY,
    ERG,
    GIGA,
    TERA,
    PLANCK_CONSTANT,
)


################################################################################
#                                    Energy                                    #
################################################################################

# Name : value when expressed in SI
_ENERGY_UNITS = {
    "ev": ELECTRON_VOLT,
    "mev": MILLI * ELECTRON_VOLT,
    "joule": JOULE,
    "j": JOULE,
    "ry": RYDBERG_ENERGY,
    "rydberg": RYDBERG_ENERGY,
    "erg": ERG,
}

# Name : Pretty name
_ENERGY_UNITS_MAKEUP = {
    "ev": "eV",
    "mev": "meV",
    "joule": "Joule",
    "j": "Joule",
    "ry": "Rydberg",
    "rydberg": "Rydberg",
    "erg": "Erg",
}

################################################################################
#                         Parameter of spin Hamiltonian                        #
################################################################################

# Name : value when expressed in SI
_PARAMETER_UNITS = {key: _ENERGY_UNITS[key] for key in _ENERGY_UNITS}
_PARAMETER_UNITS["k"] = BOLTZMANN_CONSTANT * KELVIN
_PARAMETER_UNITS["kelvin"] = BOLTZMANN_CONSTANT * KELVIN


# Name : Pretty name
_PARAMETER_UNITS_MAKEUP = {
    key: _ENERGY_UNITS_MAKEUP[key] for key in _ENERGY_UNITS_MAKEUP
}
_PARAMETER_UNITS_MAKEUP["k"] = "Kelvin"
_PARAMETER_UNITS_MAKEUP["kelvin"] = "Kelvin"

################################################################################
#                              Magnon frequencies                              #
################################################################################

# Name : value when expressed in SI
_MAGNON_ENERGY_UNITS = {key: _ENERGY_UNITS[key] for key in _ENERGY_UNITS}
_MAGNON_ENERGY_UNITS["hertz"] = PLANCK_CONSTANT
_MAGNON_ENERGY_UNITS["hz"] = PLANCK_CONSTANT
_MAGNON_ENERGY_UNITS["gigahertz"] = PLANCK_CONSTANT * GIGA
_MAGNON_ENERGY_UNITS["ghz"] = PLANCK_CONSTANT * GIGA
_MAGNON_ENERGY_UNITS["terahertz"] = PLANCK_CONSTANT * TERA
_MAGNON_ENERGY_UNITS["thz"] = PLANCK_CONSTANT * TERA


# Name : Pretty name
_MAGNON_ENERGY_UNITS_MAKEUP = {
    key: _ENERGY_UNITS_MAKEUP[key] for key in _ENERGY_UNITS_MAKEUP
}
_MAGNON_ENERGY_UNITS_MAKEUP["hertz"] = "Hz"
_MAGNON_ENERGY_UNITS_MAKEUP["hz"] = "Hz"
_MAGNON_ENERGY_UNITS_MAKEUP["gigahertz"] = "GHz"
_MAGNON_ENERGY_UNITS_MAKEUP["ghz"] = "GHz"
_MAGNON_ENERGY_UNITS_MAKEUP["terahertz"] = "THz"
_MAGNON_ENERGY_UNITS_MAKEUP["thz"] = "THz"
