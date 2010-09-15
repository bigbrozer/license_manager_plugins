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

# TODO: Check how to group status() and expiration() as a single function.

import re
import subprocess
from nagios.errorlevels import NagiosUnknown

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
    
    lmstat = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    lmstat_output = lmstat.communicate()[0].split('\n')
    
    # Check return code
    if lmstat.returncode != 0:
        # Get error message
        error_pattern = re.compile('Error getting status: (.*). \(.*\)')
        error_match = error_pattern.search(lmstat_output[-1])
        if error_match: lmstat_error_message = error_match.group(1)
        else: lmstat_error_message = "License server not available !"
        raise FlexlmStatusError(lmstat_error_message, lmstat.returncode, license_port)
    
    return lmstat_output

def expiration(license_port):
    """Execute a 'lmstat -i' command using lmutil on a remote server"""
    cmdline = [config.LMUTIL_PATH, "lmstat", "-c", license_port, '-i']
    
    lmstat = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    lmstat_output = lmstat.communicate()[0].split('\n')
    
    # Check return code
    if lmstat.returncode != 0:
        # Get error message
        error_pattern = re.compile('Error getting status: (.*). \(.*\)')
        error_match = error_pattern.search(lmstat_output[-1])
        if error_match: lmstat_error_message = error_match.group(1)
        else: lmstat_error_message = "License server not available !"
        raise FlexlmStatusError(lmstat_error_message, lmstat.returncode, license_port)
    
    return lmstat_output

#-------------------------------------------------------------------------------
# Testing zone
#-------------------------------------------------------------------------------
def test_from_file(output_file):
    """Used for testing purpose"""
    try:
        lmstat = open(output_file, 'r')
    except IOError as e:
        raise NagiosUnknown("Error loading test output file: %s" % e)
    lmstat_output = lmstat.readlines()
    lmstat.close()
    
    return lmstat_output
