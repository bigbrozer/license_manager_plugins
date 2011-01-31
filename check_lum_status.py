#!/usr/bin/env python2.6
# -*- coding: UTF-8 -*-
#===============================================================================
# Name          : check_lum_status
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
import backend.lum
import backend.util
from nagios.errorlevels import NagiosCritical, NagiosOk
from nagios.arguments import process_plugin_options

def run():
    """Execute the plugin"""
    # Plugin arguments
    options = process_plugin_options()
    
    # Get the output of license manager command, catching errors
    try:
        if options.debug:
            output = backend.util.test_from_file("../tests/lum_status.txt")
        else:
            output = backend.lum.status("{0.license}".format(options))
    except backend.lum.LumStatusError as e:
        raise NagiosCritical("{0.errmsg} (code: {0.retcode}, license: '{0.license}') !".format(e))

    # Find line showing state of license server
    servers_up = []
    for line in output:
        server_state_line_pattern = re.compile(r"\s+ip:(.*)\s\(WIN32\)")
        server_state_line_match = server_state_line_pattern.search(line)
        if server_state_line_match:
            servers_up.append(server_state_line_match.group(1))

    # Format output to Nagios
    nagios_longoutput = ""
    nagios_output = ""
    if len(servers_up) > 0:
        if not options.longoutput:
            for server in servers_up:
                nagios_longoutput += "\nServer up: {0}".format(server)

        if len(servers_up) > 1:
            nagios_output = "{0} servers are serving licenses.".format(len(servers_up))
        else:
            nagios_output = "{0} server is serving license.".format(len(servers_up))
        raise NagiosOk(nagios_output + nagios_longoutput)
    else:
        raise NagiosCritical("LUM status is not correct, please check !")

# Main
if __name__ == "__main__":
    run()