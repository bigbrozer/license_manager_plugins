#===============================================================================
# -*- coding: UTF-8 -*-
# Module        : errorlevels
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Define class for Nagios error exceptions.
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

class NagiosCritical(Exception):
    """Exception raised to fire a CRITICAL event to Nagios and break the plugin"""
    def __init__(self, msg):
        print "CRITICAL - %s" % msg
        raise SystemExit(2)

class NagiosWarning(Exception):
    """Exception raised to fire a WARNING event to Nagios and break the plugin"""
    def __init__(self, msg):
        print "WARNING - %s" % msg
        raise SystemExit(1)

class NagiosUnknown(Exception):
    """Exception raised to fire a UNKNOWN event to Nagios and break the plugin"""
    def __init__(self, msg):
        print "UNKNOWN - %s" % msg
        raise SystemExit(3)

class NagiosOk(Exception):
    """Exception raised to fire a OK event to Nagios and break the plugin"""
    def __init__(self, msg):
        print "OK - %s" % msg
        raise SystemExit(0)