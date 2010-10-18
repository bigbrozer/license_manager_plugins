#===============================================================================
# -*- coding: UTF-8 -*-
# Module        : backend.flexlm
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Utility functions to get info from FLEXlm license server.
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

# Plugin configuration
import config

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class FlexlmStatusError(Exception):
    """Exception raised when lmutil encounter an error"""
    def __init__(self, error_msg, retcode, license):
        self.errmsg = error_msg
        self.retcode = retcode
        self.license = license

#-------------------------------------------------------------------------------
# FlexLM related
#-------------------------------------------------------------------------------
def status(license_port):
    """Execute a 'lmstat -a' command using lmutil on a remote server"""
    cmdline = [config.LMUTIL_PATH, "lmstat", "-c", license_port, '-a']
    
    cmd = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    cmd_output = cmd.communicate()[0].split('\n')
    
    # Check return code
    if cmd.returncode != 0:
        # Get error message
        error_pattern = re.compile('Error getting status: (.*). \(.*\)')
        error_match = error_pattern.search(cmd_output[-1])
        if error_match: error_message = error_match.group(1).title()
        else: error_message = "License server not available !"
        raise FlexlmStatusError(error_message, cmd.returncode, license_port)
    
    return cmd_output

def expiration(license_port):
    """Execute a 'lmstat -i' command using lmutil on a remote server"""
    cmdline = [config.LMUTIL_PATH, "lmstat", "-c", license_port, '-i']
    
    cmd = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    cmd_output = cmd.communicate()[0].split('\n')
    
    # Check return code
    if cmd.returncode != 0:
        # Get error message
        error_pattern = re.compile('Error getting status: (.*). \(.*\)')
        error_match = error_pattern.search(cmd_output[-1])
        if error_match: error_message = error_match.group(1).title()
        else: error_message = "License server not available !"
        raise FlexlmStatusError(error_message, cmd.returncode, license_port)
    
    return cmd_output
