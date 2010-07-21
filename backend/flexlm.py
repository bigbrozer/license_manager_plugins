#===============================================================================
# -*- coding: ISO-8859-1 -*-
# Module        : backend.flexlm
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Utility functions to get info from FLEXlm license server.
#-------------------------------------------------------------------------------
# This file is part of flexlm_nagios_plugins.
#
# flexlm_nagios_plugins is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# flexlm_nagios_plugins is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import re
import subprocess

# Plugin configuration
import config

class FlexlmStatusError(Exception):
    """Exception raised when lmutil encounter an error"""
    def __init__(self, error_msg, retcode, license):
        self.errmsg = error_msg
        self.retcode = retcode
        self.license = license

def status(license_port):
    """Execute a 'lmstat -a' command using lmutil on a remote server"""
    cmdline = [config.LMUTIL_PATH, "lmstat", "-c", license_port, '-a']
    
    lmstat = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    lmstat_return_code = lmstat.wait()
    
    lmstat_output = lmstat.stdout.readlines()
    
    # Check return code
    if lmstat_return_code != 0:
        # Get error message
        error_pattern = re.compile('Error getting status: (.*). \(.*\)')
        error_match = error_pattern.search(lmstat_output[-1])
        if error_match: lmstat_error_message = error_match.group(1)
        else: lmstat_error_message = "Unknown error !"
        raise FlexlmStatusError(lmstat_error_message, lmstat_return_code, license_port)
    
    return lmstat_output

def status_from_file(license_port):
    """Used for testing purpose"""
    lmstat = open('../output/lmstat_output.txt', 'r')
    lmstat_output = lmstat.readlines()
    lmstat.close()
    
    return lmstat_output
