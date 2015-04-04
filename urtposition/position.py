#
# UrTPosition Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 Daniele Pantaleone <fenix@bigbrotherbot.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA


class Position(object):

    def __init__(self, x, y, z):
        """
        :param x: The X coordinate
        :param y: The Y coordinate
        :param z: The Z coordinate
        :raise ValueError: If bad coordinates are supplied
        """
        self.x, self.y, self.z = float(x), float(y), float(z)

    def __eq__(self, other):
        return isinstance(other, Position) and self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not isinstance(other, Position) or self.x != other.x or self.y != other.y or self.z != other.z

    def __str__(self):
        return 'Position <%f, %f, %f>' % (self.x, self.y, self.z)


ORIGIN = Position(0.0, 0.0, 0.0)