#===============================================================================
# -*- coding: ISO-8859-1 -*-
# Module        : arguments
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Handle plugin arguments.
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

import optparse
from nagios.errorlevels import NagiosUnknown

def process_plugin_options():
    """Process plugin arguments"""
    o_parser = optparse.OptionParser()
    o_parser.add_option('-l', dest='license', help='FLEXlm port or license file to check')
    o_parser.add_option('-d', '--debug', dest='debug', action='store_true', help='Enable debug mode')
    opt = o_parser.parse_args()[0]
    
    # Checking for options
    if not opt.license:
        raise NagiosUnknown("Syntax error: missing license information !")
    if opt.debug:
        print "Debug mode is on."
    
    return opt
