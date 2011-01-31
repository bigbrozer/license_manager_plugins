#===============================================================================
# -*- coding: UTF-8 -*-
# Module        : backend.lum
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Utility functions to get info from LUM (License Use Management) license server.
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

import re
import subprocess
import os
from nagios.errorlevels import NagiosOk, NagiosUnknown

# Plugin configuration
import config

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class LumStatusError(Exception):
    """Exception raised when i4* command encounter an error"""
    def __init__(self, error_msg, retcode, license):
        self.errmsg = error_msg
        self.retcode = retcode
        self.license = license

#-------------------------------------------------------------------------------
# LUM related
#-------------------------------------------------------------------------------
def status(ini_file_location):
    """Check the status of LUM
    Set IFOR_CONFIG env variable and execute 'i4tv' command"""
    cmdline = [config.I4TV_PATH]
    # Ini file exist ?
    if not os.path.exists(ini_file_location):
        raise NagiosUnknown("INI file not found: '{0}'".format(ini_file_location))
    # Create environment variable for i4* commands
    os.putenv("IFOR_CONFIG", ini_file_location)

    cmd = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmd_output = cmd.communicate()[0]

    # Check if i4* command is successful
    done_pattern = re.compile(r"Completed license transaction.*")
    done_match = done_pattern.search(cmd_output)
    if not done_match:
        raise LumStatusError("Error occured when checking for LUM !", cmd.returncode, os.path.basename(ini_file_location))
    
    return cmd_output.split('\n')

#def expiration(license_port):
#    """Execute a 'lstc_qrun -r -s' command using lstc_qrun on a remote server"""
#    cmdline = [config.I4TV_PATH, "-r", "-s", license_port]
#
#    cmd = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
#    cmd_output = cmd.communicate()[0].split('\n')
#
#    # Check return code
#    if cmd.returncode != 0:
#        # Get error message
#        error_pattern = re.compile('.*ERROR (.*)')
#        error_match = error_pattern.search(cmd_output[-1])
#        if error_match: error_message = error_match.group(1).title()
#        else: error_message = "License server not available !"
#        raise LumStatusError(error_message, cmd.returncode, license_port)
#
#    return cmd_output
