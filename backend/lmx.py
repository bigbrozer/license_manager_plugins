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
from datetime import datetime
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
# Lmx classes
#-------------------------------------------------------------------------------

class Feature(object):
    """Store data about a feature: name, used licenses and total."""

    def __init__(self, name, used_licenses, total_licenses, expire_date):
        self.name = name

        try:
            self.used_licenses = long(used_licenses)
            self.total_licenses = long(total_licenses)
            self.expires = datetime.strptime(expire_date, '%Y-%m-%d')
        except ValueError as e:
            raise NagiosUnknown('Exception: %s' % e)

    def __str__(self):
        """Print feature data as text to be used in Nagios long output."""
        return '{0:>s}: {1:d} / {2:d}'.format(self.name, self.used_licenses, self.total_licenses)

    def print_perfdata(self):
        """Print feature performance data string."""
        return '\'{0:>s}\'={1:d};;;0;{2:d}'.format(self.name, self.used_licenses, self.total_licenses)

class Features(object):
    """This class stores all features objects. She is able to compute some global stats about licenses usage."""

    today_date = datetime.today()

    # Class customization
    def __init__(self):
        self.features = []

    def __iter__(self):
        return iter(self.features)

    def __len__(self):
        return len(self.features)
    
    def __setitem__(self, key, value):
        self.features[key] = value

    def __getitem__(self, key):
        return self.features[key]

    def __str__(self):
        """Return the Nagios output when all is OK."""
        return 'LM-X: usage: %d / %d license(s) available.' % (self.calc_used_licenses(), self.calc_total_licenses())

    # Public methods
    def append(self, value):
        """Lists append-like"""
        self.features.append(value)

    def calc_total_licenses(self):
        """Calculate the total number of available licenses for all features."""
        total = 0
        for feature in self:
            total += feature.total_licenses
        return total

    def calc_used_licenses(self):
        """Calculate the total number of used licenses."""
        in_use = 0
        for feature in self:
            in_use += feature.used_licenses
        return in_use

    def calc_expired_license(self):
        """Return a dictionnary "feature name": number of days before expiration."""
        remains = 0
        expire_list = {}
        for feature in self:
            td = feature.expires - Features.today_date
            if td.days < 0:
                remains = 0
            else:
                remains = td.days
            expire_list[feature.name] = remains
        return expire_list


    def print_perfdata(self):
        """Construct and return the perfdata string for all features."""
        perfdatas = [' |']
        for feature in self:
            perfdatas.append(feature.print_perfdata())
        return " ".join(perfdatas)

#-------------------------------------------------------------------------------
# Lmx functions
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