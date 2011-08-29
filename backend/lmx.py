#===============================================================================
# -*- coding: UTF-8 -*-
# Module        : backend.lmx
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Utility functions to get info from LM-X (Altair) license server.
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

import subprocess
from nagios.errorlevels import NagiosUnknown

# Plugin configuration
import config

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class LmxStatusError(Exception):
    """Exception raised when lmxendutil encounter an error"""

    def __init__(self, error_msg, retcode, license):
        self.errmsg = error_msg
        self.retcode = retcode
        self.license = license

#-------------------------------------------------------------------------------
# Lmx related
#-------------------------------------------------------------------------------

def status_xml(remote_host, license_port):
    """Execute a 'lmxendutil' command on a remote server. Return results as XML."""

    cmdline = [config.LMXENDUTIL_PATH, "-licstatxml", "-host", remote_host, '-port', license_port]

    cmd = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmd_output = cmd.communicate()[0]

    if cmd.returncode:
        raise LmxStatusError("Unexpected error !", cmd.returncode, '%s@%s' % (license_port, remote_host))

    # Make output to be XML. Remove first 3 lines that includes software name and copyright informations.
    xml_data = "\n".join(cmd_output.split('\n')[3:])

    return xml_data