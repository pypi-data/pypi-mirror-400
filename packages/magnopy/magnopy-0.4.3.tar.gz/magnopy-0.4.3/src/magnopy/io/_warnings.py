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

# Save local scope at this moment
old_dir = set(dir())
old_dir.add("old_dir")


def _envelope_warning(text):
    lines = text.split("\n")

    short_lines = []
    for line in lines:
        if len(line) > 74:
            line = line.split()
            while len(line) > 0:
                subline = line[0]
                line = line[1:]
                while len(subline) < 74 and len(line) > 0:
                    if len(subline) + 1 + len(line[0]) <= 74:
                        subline = f"{subline} {line[0]}"
                        line = line[1:]
                    else:
                        break
                short_lines.append(subline)
        else:
            short_lines.append(line)

    enveloped_lines = [f"#W {line:<74} W#" for line in short_lines]

    return (
        f"\n{'  WARNING  ':#^80}\n"
        + "\n".join(enveloped_lines)
        + f"\n{'  END OF WARNING  ':#^80}\n"
    )


# Populate __all__ with objects defined in this file
__all__ = list(set(dir()) - old_dir)
# Remove all semi-private objects
__all__ = [i for i in __all__ if not i.startswith("_")]
del old_dir
