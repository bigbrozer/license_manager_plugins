#!/usr/bin/env python
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

import xml.dom.minidom as XML

import backend.lmx
import backend.util
from nagios.errorlevels import NagiosCritical, NagiosWarning, NagiosOk, NagiosUnknown
from nagios.arguments import process_plugin_options, argparser

def run():
    """Execute the plugin"""

    # Plugin arguments
    # ----------------
    #
    # Define custom arguments for this plugin using argparser
    argparser.add_option('-m', dest='mode', choices=('status', 'expire'), help='Mode for the plugins, either "status" (default) or "expire".')
    # Define common arguments to all plugins
    options = process_plugin_options()

    # Check mandatory arguments
    if not options.port:
        raise NagiosUnknown("Syntax error: missing port information !")
    if not options.mode:
        raise NagiosUnknown("Syntax error: missing mode information !")

    # Get the output of license manager command, catching errors
    try:
        output = backend.lmx.status_xml("%s" % options.license, options.port)
    except backend.lmx.LmxStatusError as e:
        raise NagiosCritical("%s (code: %s, license: '%s') !" % (e.errmsg, e.retcode, e.license))

    # Process XML data
    xml_data = XML.parseString(output)
    all_features_tags = xml_data.getElementsByTagName('FEATURE')

    if not len(all_features_tags):
        raise NagiosCritical('Problem to query LM-X license manager on port %s from host %s !' % (options.port, options.license))
    
    # Get all features and compute stats (used, free, total licenses...)
    features = backend.lmx.Features()

    for node_feature in all_features_tags:
        feature = node_feature.getAttribute('NAME')
        used_licenses = node_feature.getAttribute('USED_LICENSES')
        total_licenses = node_feature.getAttribute('TOTAL_LICENSES')
        expire_date = node_feature.getAttribute('END')

        feature = backend.lmx.Feature(feature, used_licenses, total_licenses, expire_date)
        features.append(feature)

    # Format Nagios output
    # --------------------
    #
    # STATUS
    if options.mode == 'status':
        nagios_output = str(features)
        nagios_longoutput = ''
        nagios_perfdata = features.print_perfdata()

        # Must we show long output ?
        if not options.nolongoutput:
            nagios_longoutput = '\nFeatures details:\n\n'
            for feature in features:
                nagios_longoutput += '%s\n' % feature

        raise NagiosOk(nagios_output + nagios_longoutput + nagios_perfdata)
    # EXPIRATION
    elif options.mode == 'expire':
        days_remaining = features.calc_expired_license()
        if not len(days_remaining):
            raise NagiosOk('Features are up-to-date.')

        count = 0
        nagios_output = ''
        nagios_longoutput = '\n'

        # Check first for expired licenses
        if 0 in days_remaining.values():
            for feature in days_remaining:
                if not days_remaining[feature]:
                    nagios_longoutput += '** %s is expired ! **\n' % feature
                    count += 1
            nagios_output = 'There are %d features expired !' % count

            # Do not show long output if specified
            if not options.nolongoutput:
                nagios_output += nagios_longoutput

            raise NagiosCritical(nagios_output)
        else:
            # Check for about to expire licenses
            for feature in days_remaining:
                if days_remaining[feature] > 0 and days_remaining[feature] <= 15:
                    nagios_longoutput += '%s expires in %d day(s).\n' % (feature, days_remaining[feature])
                    count +=1
            nagios_output = 'There are %d features about to expire !' % count

            # Do not show long output if specified
            if not options.nolongoutput:
                nagios_output += nagios_longoutput

            raise NagiosWarning(nagios_output)

# Main
if __name__ == "__main__":
    run()