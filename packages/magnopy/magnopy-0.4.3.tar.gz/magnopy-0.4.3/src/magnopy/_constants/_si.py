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


R"""
Units of the International system of units, physical constants expressed in SI, non-SI
units expressed in SI.
"""

# Save local scope at this moment
old_dir = set(dir())
old_dir.add("old_dir")


################################################################################
##                              Seven base units                              ##
##                                                                            ##
##  Source The International System of Units (SI) 9th edition, Table 2        ##
##  Link: https://www.bipm.org/en/publications/si-brochure                    ##
##  Last updated: 22 September 2025                                           ##
################################################################################
SECOND = 1  # Time
METRE = 1  # Length
KILOGRAM = 1  # Mass
AMPERE = 1  # Electric current
KELVIN = 1  # Thermodynamic temperature
MOLE = 1  # amount of substance
CANDELA = 1  # Luminous intensity

################################################################################
##                           Twenty two named units                           ##
##                                                                            ##
##  Source The International System of Units (SI) 9th edition, Table 4        ##
##  Link: https://www.bipm.org/en/publications/si-brochure                    ##
##  Last updated: 22 September 2025                                           ##
################################################################################
RADIAN = 1  # Plane angle
STERADIAN = 1  # Solid angle
HERTZ = 1 / SECOND  # Frequency
NEWTON = KILOGRAM * METRE / SECOND**2  # Force
PASCAL = KILOGRAM / METRE / SECOND**2  # Pressure, stress
JOULE = KILOGRAM * METRE**2 / SECOND**2  # Energy, work, amount of heat
WATT = KILOGRAM * METRE**2 / SECOND**3  # Power, radiant flux
COULOMB = AMPERE * SECOND  # Electric charge
VOLT = KILOGRAM * METRE**2 / SECOND**3 / AMPERE  # Electric potential difference
FARAD = SECOND**4 * AMPERE**2 / KILOGRAM / METRE**2  # Capacitance
OHM = KILOGRAM * METRE**2 / SECOND**3 / AMPERE**2  # Electric resistance
SIEMENS = SECOND**3 * AMPERE**2 / KILOGRAM / METRE**2  # Electric conductance
WEBER = KILOGRAM * METRE**2 / SECOND**2 / AMPERE  # Magnetic flux
TESLA = KILOGRAM / SECOND**2 / AMPERE  # Magnetic flux density
HENRY = KILOGRAM * METRE**2 / SECOND**2 / AMPERE**2  # Inductance
DEGREE_CELSIUS = KELVIN  # Celsius temperature
LUMEN = CANDELA * STERADIAN  # Luminous flux
LUX = CANDELA * STERADIAN / METRE**2  # Illuminance
BECQUEREL = 1 / SECOND  # Activity referred to a radionuclide
GRAY = METRE**2 / SECOND**2  # Absorbed dose, kerma
SIEVERT = METRE**2 / SECOND**2  # Dose equivalent
KATAL = MOLE / SECOND  # Catalytic activity

################################################################################
##                                  Prefixes                                  ##
##                                                                            ##
##  Source The International System of Units (SI) 9th edition, Table 7        ##
##  Link: https://www.bipm.org/en/publications/si-brochure                    ##
##  Last updated: 22 September 2025                                           ##
################################################################################
DECA = 1e1
HECTO = 1e2
KILO = 1e3
MEGA = 1e6
GIGA = 1e9
TERA = 1e12
PETA = 1e15
EXA = 1e18
ZETTA = 1e21
YOTTA = 1e24
RONNA = 1e27
QUETTA = 1e30

DECI = 1e-1
CENTI = 1e-2
MILLI = 1e-3
MICRO = 1e-6
NANO = 1e-9
PICO = 1e-12
FEMTO = 1e-15
ATTO = 1e-18
ZEPTO = 1e-21
YOCTO = 1e-24
RONTO = 1e-27
QUECTO = 1e-30

################################################################################
##                          Seven defining constants                          ##
##                                                                            ##
##  Source The International System of Units (SI) 9th edition, Table 1        ##
##  Link: https://www.bipm.org/en/publications/si-brochure                    ##
##  Last updated: 22 September 2025                                           ##
################################################################################
HYPERFINE_TRANSITION_FREQUENCY_OF_CS = 9192631770 * HERTZ
SPEED_OF_LIGHT_IN_VACUUM = 299792458 * METRE / SECOND
PLANCK_CONSTANT = 6.62607015e-34 * JOULE * SECOND
ELEMENTARY_CHARGE = 1.602176634e-19 * COULOMB
BOLTZMANN_CONSTANT = 1.380649e-23 * JOULE / KELVIN
AVOGADRO_CONSTANT = 6.02214076e23 / MOLE
LUMINOUS_EFFICACY = 683 * LUMEN / WATT

################################################################################
##                             Physical constants                             ##
##                                                                            ##
##  Source: 2022 CODATA recommended values                                    ##
##  Link: https://pml.nist.gov/cuu/Constants/index.html                       ##
##  Last updated: 22 September 2025                                           ##
################################################################################
ELECTRON_VOLT = 1.602176634e-19 * JOULE
BOHR_RADIUS = 5.29177210544e-11 * METRE
BOHR_MAGNETON = 9.2740100657e-24 * JOULE / TESLA
RYDBERG_CONSTANT = 10973731.568157 / METRE
VACUUM_MAGNETIC_PERMEABILITY = 1.25663706127e-6 * NEWTON / AMPERE**2  # Newton/ Ampere^2
REDUCED_PLANCK_CONSTANT = (
    6.62607015e-34 / 2 / 3.14159265358979323846 * JOULE * SECOND / RADIAN
)

################################################################################
##                                Non-SI units                                ##
################################################################################
ANGSTROM = 1e-10 * METRE
RYDBERG_ENERGY = PLANCK_CONSTANT * SPEED_OF_LIGHT_IN_VACUUM * RYDBERG_CONSTANT * JOULE
ERG = 1e-7 * JOULE


# Populate __all__ with objects defined in this file
__all__ = list(set(dir()) - old_dir)
# Remove all semi-private objects
__all__ = [i for i in __all__ if not i.startswith("_")]
del old_dir
