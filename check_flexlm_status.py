#!/usr/bin/env python2.6
# -*- coding: UTF-8 -*-
#===============================================================================
# Name          : check_flexlm_status
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Check FLEXlm license server status and license usage.
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
import re
import backend.flexlm
from nagios.errorlevels import NagiosCritical, NagiosOk
from nagios.arguments import process_plugin_options

def format_perfdata(features):
    """Format the output of performance data"""
    perfdata = " | "
    for feature in features:
        if feature["status"] == "OK":
            perfdata += "'%s'=%s;;;0;%s " % (feature["name"], feature["in_use"], feature["total"])
    
    return perfdata.rstrip()

def run():
    """Execute the plugin"""
    # Plugin arguments
    options = process_plugin_options()
    
    # Get the output of lmutil / lmstat, catching errors
    try:
        if options.debug:
            output = backend.flexlm.test_from_file("../tests/lmstat_status.txt")
        else:
            output = backend.flexlm.status("%s" % options.license)
    except backend.flexlm.FlexlmStatusError as e:
        raise NagiosCritical("%s (code: %s, license: '%s') !" % (e.errmsg, e.retcode, e.license))
    
    # Some globals
    all_feature_stats = []             # Store all features statistics
    feature_error = 0                  # Counter for the number of feature in error
    total_license_available = 0        # The total license available (sum of total license issued for all features)
    total_license_used = 0             # The total license in use (sum of total license in use for all features)
    vendor_daemon = ""                 # Store the vendor daemon name
    
    # Compile regexp used to check output
    regexp_vendor_daemon = re.compile(r'\s+(.*): UP')
    regexp_feature_name = re.compile(r'^Users of (.*):')
    regexp_feature_stats = re.compile(r'^Users of .*: .* of (?P<total>\d+) .* issued; .* of (?P<in_use>\d+) .* in use')
    
    # Checking if Vendor daemon is UP
    for line in output:
        match = regexp_vendor_daemon.search(line)
        if match:
            vendor_daemon = match.group(1)
    
    if len(vendor_daemon) == 0:
        raise NagiosCritical("No vendor daemon is running !")
    
    # Retrieve features informations
    for line in output:
        feature = {
                   'name': '',
                   'in_use': '0',
                   'total': '0',
                   'status': '',
        }
        match_feature_line = regexp_feature_name.search(line)
        if match_feature_line:
            # Store feature name
            feature["name"] = match_feature_line.group(1)
            
            # Checking if this is possible to get stats from the feature
            match_feature_stats = regexp_feature_stats.search(line)
            if match_feature_stats:
                feature.update(match_feature_stats.groupdict())
                feature["status"] = "OK"
                
                # Calculate some stats about license usage
                total_license_available += int(feature["total"])
                total_license_used += int(feature["in_use"])
            else:
                feature["status"] = "ERROR"
                feature_error+=1
        
            all_feature_stats.append(feature)

    # Formating Nagios output
    #
    nagios_output = ""
    nagios_longoutput = ""
    nagios_perfdata = format_perfdata(all_feature_stats)
    
    # Output if errors are found in features
    if feature_error > 0:
        if not options.longoutput:
            for feature in all_feature_stats:
                if feature["status"] == "ERROR":
                    nagios_longoutput += "Feature: %s\n" % feature["name"]

        nagios_output = "%s: %d feature(s) in error(s) !\n%s" % (vendor_daemon, feature_error, nagios_longoutput.rstrip('\n'))
        raise NagiosCritical(nagios_output + nagios_perfdata)

    # Output when everything is fine
    #
    if not options.longoutput:
        for feature in all_feature_stats:
            nagios_longoutput += "Feature '%s': %s / %s\n" % (feature["name"], feature["in_use"], feature["total"])
    
    nagios_output = "%s: usage: %d / %d license(s) available.\n%s" % (vendor_daemon, total_license_used, total_license_available, nagios_longoutput.rstrip('\n'))
    
    raise NagiosOk(nagios_output + nagios_perfdata)
    
# Main
if __name__ == "__main__":
    run()