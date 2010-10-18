#!/usr/bin/env python2.6
# -*- coding: UTF-8 -*-
#===============================================================================
# Name          : check_lstc_status
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Check LSTC license server status and license usage.
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

# Python Std Lib
import re
import backend.lstc
import backend.util
from nagios.errorlevels import NagiosCritical, NagiosOk, NagiosUnknown
from nagios.arguments import process_plugin_options

def run():
    """Execute the plugin"""
    # Plugin arguments
    options = process_plugin_options()
    
    # Get the output of license manager command, catching errors
    try:
        if options.debug:
            output = backend.util.test_from_file("../tests/lstc_status.txt")
        else:
            output = backend.lstc.status("%s" % options.license)
    except backend.lstc.LstcStatusError as e:
        raise NagiosCritical("%s (code: %s, license: '%s') !" % (e.errmsg, e.retcode, e.license))

    # Globals
    connected_users = []

    for line in output:
        # Checking number of connected users
        connected_users_pattern = re.compile(r'^(?:\s+|)(\w+)\s+(\d+@[\w\d.]+)')
        connected_users_match = connected_users_pattern.search(line)
        if connected_users_match:
            connected_users.append((connected_users_match.group(1), connected_users_match.group(2)))

    # Checking for unknown errors
    if not connected_users:
        raise NagiosUnknown("Unexpected error ! Check with debug mode.")

    # Format Nagios output
    # --------------------
    #
    nagios_output = "LSTC: There %s %d license%s used."
    nagios_longoutput = ''

    # Plural syntax if more than 1 user
    if len(connected_users) > 1:
        verb = 'are'
        plural = 's'
    else:
        verb = 'is'
        plural =''

    # Output to Nagios
    nagios_output = nagios_output % (verb, len(connected_users), plural)
    if not options.longoutput:
        nagios_longoutput = '\n'
        for user in connected_users:
            nagios_longoutput += "User %s from host %s.\n" % (user[0], user[1])
    raise NagiosOk(nagios_output + nagios_longoutput)

# Main
if __name__ == "__main__":
    run()