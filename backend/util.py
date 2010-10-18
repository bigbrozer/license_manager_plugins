#===============================================================================
# -*- coding: UTF-8 -*-
# Module        : backend.util
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Various utilities.
#-------------------------------------------------------------------------------
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from nagios.errorlevels import NagiosUnknown

def test_from_file(output_file):
    """Used for testing purpose"""
    try:
        testfile = open(output_file, 'r')
    except IOError as e:
        raise NagiosUnknown("Error loading test output file: %s" % e)
    testfile_output = testfile.readlines()
    testfile.close()

    return testfile_output
