#===============================================================================
# -*- coding: UTF-8 -*-
# Module        : backend.lstc
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Utility functions to get info from LSTC (LS-Dyna) license server.
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

# TODO: Check how to group status() and expiration() as a single function.

import re
import subprocess
from nagios.errorlevels import NagiosOk

# Plugin configuration
import config

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class LstcStatusError(Exception):
    """Exception raised when lstc_qrun encounter an error"""
    def __init__(self, error_msg, retcode, license):
        self.errmsg = error_msg
        self.retcode = retcode
        self.license = license

#-------------------------------------------------------------------------------
# Lstc related
#-------------------------------------------------------------------------------
def status(license_port):
    """Execute a 'lstc_qrun -s' command using lstc_qrun on a remote server"""
    cmdline = [config.LSTCQRUN_PATH, "-s", license_port]
    
    cmd = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmd_output = cmd.communicate()[0]

    # Warn for error message if any
    error_pattern = re.compile('.*ERROR (.*)')
    error_match = error_pattern.search(cmd_output)
    if error_match:
        error_message = error_match.group(1)
        raise LstcStatusError(error_message, cmd.returncode, license_port)

    # Check return code
    if cmd.returncode == 0:
        raise NagiosOk("There is no program running or queued.")
    
    return cmd_output.split('\n')

def expiration(license_port):
    """Execute a 'lstc_qrun -r -s' command using lstc_qrun on a remote server"""
    cmdline = [config.LSTCQRUN_PATH, "-r", "-s", license_port]
    
    cmd = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    cmd_output = cmd.communicate()[0].split('\n')
    
    # Check return code
    if cmd.returncode != 0:
        # Get error message
        error_pattern = re.compile('.*ERROR (.*)')
        error_match = error_pattern.search(cmd_output[-1])
        if error_match: error_message = error_match.group(1).title()
        else: error_message = "License server not available !"
        raise LstcStatusError(error_message, cmd.returncode, license_port)
    
    return cmd_output
