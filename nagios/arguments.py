#===============================================================================
# -*- coding: UTF-8 -*-
# Module        : arguments
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Handle plugin arguments.
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

import optparse
from nagios.errorlevels import NagiosUnknown

# Argument parser object
argparser = optparse.OptionParser()

def process_plugin_options():
	"""Process plugin arguments"""
	argparser.add_option('-l', dest='license', help='License file or remote host as <port>@<remote_host>')
	argparser.add_option('-p', dest='port', help='License port (only for backend that does not support remote host as <port>@<remote_host>)')
	argparser.add_option('-d', '--debug', dest='debug', action='store_true', help='Enable debug mode')
	argparser.add_option('--no-long-output', dest='nolongoutput', action='store_true', help='Disable Nagios long output (compatibility with Nagios < 3.x)')
	opt = argparser.parse_args()[0]
	
	# Checking for options
	if not opt.license:
		raise NagiosUnknown("Syntax error: missing license or remote host information !")
	if opt.debug:
		print "Debug mode is on."

	return opt
