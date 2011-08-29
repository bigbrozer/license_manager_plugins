#!/usr/bin/env python2.6
# -*- coding: UTF-8 -*-
#===============================================================================
# Name          : check_lmx_status
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Check LM-X license server status and license usage.
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

# Python Std Lib
import xml.dom.minidom as XML

import backend.lmx
import backend.util
from nagios.errorlevels import NagiosCritical, NagiosOk, NagiosUnknown
from nagios.arguments import process_plugin_options

def run():
    """Execute the plugin"""
	
    # Plugin arguments
    options = process_plugin_options()

    # Check mandatory arguments
    if not options.port:
        raise NagiosUnknown("Syntax error: missing port information !")

    # Get the output of license manager command, catching errors
    try:
        output = backend.lmx.status_xml("%s" % options.license, options.port)
    except backend.lmx.LmxStatusError as e:
        raise NagiosCritical("%s (code: %s, license: '%s') !" % (e.errmsg, e.retcode, e.license))

    # Process XML data
    xml_data = XML.parseString(output)
    all_features_tags = xml_data.getElementsByTagName('FEATURE')

    if len(all_features_tags) == 0:
        raise NagiosCritical('Problem to query LM-X license manager on port %s from host %s !' % (options.port, options.license))
    
    # Get all features and compute stats (used, free, total licenses...)
    features = backend.lmx.Features()

    for node_feature in all_features_tags:
        name = node_feature.getAttribute('NAME')
        used_licenses = node_feature.getAttribute('USED_LICENSES')
        total_licenses = node_feature.getAttribute('TOTAL_LICENSES')

        feature = backend.lmx.Feature(name, used_licenses, total_licenses)
        features.append(feature)

    # Format Nagios output
    # --------------------
    #
    nagios_output = str(features)
    nagios_longoutput = ''
    nagios_perfdata = features.print_perfdata()

    # Must we show long output ?
    if not options.longoutput:
        nagios_longoutput = '\nFeatures details:\n\n'
        for feature in features:
            nagios_longoutput += '%s\n' % feature

    raise NagiosOk(nagios_output + nagios_longoutput + nagios_perfdata)

# Main
if __name__ == "__main__":
    run()