#!/usr/bin/perl -w
#
#===============================================================================
# Name          : check_lum_license_expiration.pl
# Author        : Vincent BESANCON aka 'v!nZ' <besancon.vincent@gmail.com>
# Description   : Check license expiration for LUM license manager.
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

use strict;
use Getopt::Long;
use Time::Local;
use POSIX qw(ceil);
use File::Basename;

# DEBUG (don't forget to comment !!)
#use Data::Dumper;

#-------------------------------------------------------------------------------
# Globals
#-------------------------------------------------------------------------------
#
# Program info
my $plugin_name = basename($0);

# Timeout
my $TIMEOUT = 30;

# I4BLT command
my $i4blt_command = "i4blt -lp -i|";
#my $i4blt_command = "../commands/lum/i4blt -lp -i|";

# This will not exist anymore when switching Colisée from Solaris to Windows !!
#if ($^O eq "MSWin32") {
#    $i4blt_command = "i4blt_result.txt";
#} else {
#    $i4blt_command = "i4blt -lp -i|";
#}

# Store results
my %license_status;
my $product_name;
my @license_expiration_date;
my $remaining_days;
my $nbr_license_expiring_soon = 0;
my $nbr_license_expiring_very_soon = 0;
my $nbr_license_expired = 0;

# Nagios related
my $nagios_status = 'OK';
my $nagios_status_code = 0;
my $nagios_output = "";
my $nagios_longoutput = '';

# Position flags to know where we are in the results
my $in_product_section = 0;
my $in_license_section = 0;

# Command line arguments
my $o_verbose = undef;
my $o_help = undef;
my $o_license = undef;
#
#-END-GLOBALS------------------------------------------------------------------/

#-------------------------------------------------------------------------------
# PREPARING
#-------------------------------------------------------------------------------
#
# Get the alarm signal just in case the plugin timeout is reached
$SIG{'ALRM'} = sub {
     print ("Error: plugin timeout in $TIMEOUT seconds.\n");
     exit 3;
};

alarm($TIMEOUT);

# Linking arguments
GetOptions(
    'v' => \$o_verbose,     'verbose'   => \$o_verbose,
    'l=s' => \$o_license,     'license=s'   => \$o_license,
    'h' => \$o_help,        'help'      => \$o_help
);

# Checking arguments
if (defined($o_help)) { help(); exit 3; }
if (!defined($o_license)) { help(); print "\nUNKNOWN - Missing license information !\n"; exit 3; }
#
#-END-PREPARING----------------------------------------------------------------/

#-------------------------------------------------------------------------------
# SUBS
#-------------------------------------------------------------------------------
#
# Sub -- Debug function
sub verb {
    my $debug_message = shift;
    print STDERR "[DEBUG] ", $debug_message if defined($o_verbose);
}

sub print_usage {
    print "Usage: $plugin_name [-v] [-h]\n";
}

sub print_description {
    print <<EOT;
Description:
  This plugin will execute the command 'i4blt -lp -i' on the system where this plugin is running.
  The information on all products licenses will be parsed to check if a license is expired or will be soon.

EOT
}

sub help {
   print "\n==== Check license expiration for LUM license manager ====\n\n";
   print "GPL v3\n";
   print "(c)2010 Vincent 'v!nZ' BESANCON, <vincent.besancon\@faurecia.com>\n\n";
   print_description();
   print_usage();
   print <<EOT;
 -h, --help
   Print this help message.
 -v, --verbose
   Print debugging information, Nagios should truncate output.
 -l, --license
   Specify license INI file location for i4blt command (this will be used to set IFOR_CONFIG env variable).
EOT
}

# Sub -- Get the name of the current product being checked
sub get_product_name {
    my($product) = shift;
    
    $product =~ s/\s+$//;                           # Trim trailing spaces
    $product =~ s/^\s+Product Name:\s+//;           # Delete uneeded
    $product;
}

# Sub -- Return the max value from an array (avoid usage of List::Util on old perl version)
sub max { 
    my $max = pop(@_);
    foreach (@_) {
        $max = $_ if $_ > $max;
    }
    $max;
}

# Sub -- Return the min value from an array (avoid usage of List::Util on old perl version)
sub min { 
    my $min = pop(@_);
    foreach (@_) {
        $min = $_ if $_ < $min;
    }
    $min;
}

# Sub -- Get the date of a license
sub license_days_remaining {
    my($expire_date_line) = shift;
    my $days_delta;
    
    # Date variables
    my %months = (
        'Jan' => 0,
        'Feb' => 1,
        'Mar' => 2,
        'Apr' => 3,
        'May' => 4,
        'Jun' => 5,
        'Jul' => 6,
        'Aug' => 7,
        'Sep' => 8,
        'Oct' => 9,
        'Nov' => 10,
        'Dec' => 11
    );
    my $today_seconds = time();
    my @license_date;
    my $license_date_seconds;
    
    
    # Get the license date expiration from the result and transform it like localtime array
    $expire_date_line =~ /Exp. Date: ([a-zA-Z]{3})\s([0-9]{2})\s([0-9]*)/;
    if (!$1 || !$2 || !$3) {
        print "Error: Unable to parse license expiration date for product \"$product_name\" !\n";
        exit 3;
    }
    
    # We will have problem with this in year 2038 ;-)) (limitation of Time::Local)
    if (int($3) < 2038) {
        @license_date = (0, 0, 0, int($2), int($months{$1}), int($3));
        $license_date_seconds = timelocal(@license_date);
    } else {
        return $days_delta = undef;
    }
    
    # Calculate the number of days between the two dates
    $days_delta = POSIX::ceil( ($license_date_seconds - $today_seconds) / 60 / 60 / 24 );
    
    # Return
    if ($days_delta > 30) {
        return $days_delta = undef;
    } else {
        return $days_delta;
    }
}
#
#-END-SUBS---------------------------------------------------------------------/

verb("Timeout is set at $TIMEOUT seconds.\n");

# Read result of the i4blt command
$ENV{'IFOR_CONFIG'} = $o_license;
$ENV{'LANG'} = "C";
open I4BLT_RESULT, $i4blt_command or die "Error: unable to execute the i4blt command !\n";

# Start to read command output results
while (<I4BLT_RESULT>) {
    # Check if we are leaving a product section
    if (/={50,}/ && $in_product_section) {
        verb("Leaving a product section.\n\n");
        $in_product_section = 0;
        $in_license_section = 0;
    }
    
    # Check if we are entering a product section
    if (/Product Name:/ && !$in_product_section) {
        verb("Entering a product section.\n");
        $in_product_section = 1;
        $product_name = get_product_name($_);
        verb("\tProduct name: $product_name\n");
    }
    
    # Check if we are entering a license section
    if (/^\s-{5,}\sLicense Information\s-{5,}$/ && $in_product_section) {
        verb("Entering a license section.\n");
        $in_license_section = 1;
    }
    
    # Get the expiration date in a license section
    if (/Exp. Date:/ && $in_license_section) {
        verb("Trying to get license expiration date in:\n");
        verb("\t$_");
        my $days_remaining = license_days_remaining($_);
        if (defined($days_remaining)) {
            push(@{$license_status{$product_name}}, $days_remaining);
        }
    }
}

close I4BLT_RESULT;

#-------------------------------------------------------------------------------
# NAGIOS OUTPUT
#-------------------------------------------------------------------------------
#
# Read through all products and populate nagios long output with ones that will expire (if any)
if (%license_status) {
    foreach my $product (keys %license_status) {
        # Check if this product has more than one license...
        my $nbr_license = @{$license_status{$product}};
        if ($nbr_license > 1) {
            # Get the minimum days remaining for this product
            $remaining_days = min @{$license_status{$product}};
            verb("Product \"$product\" has $nbr_license licenses, get the lower remaining days: $remaining_days...\n");
        } else {
            $remaining_days = @{$license_status{$product}}[0];
        }
        
        if ($remaining_days > 15) {
            $nagios_longoutput .= "Product \"$product\" will expire in $remaining_days days !\n";
            $nbr_license_expiring_soon++;
        }
        
        if ($remaining_days > 0 && $remaining_days <= 15) {
            $nagios_longoutput .= "* Product \"$product\" is about to expire in $remaining_days days !\n";
            $nbr_license_expiring_very_soon++;
        }
        
        if ($remaining_days <= 0) {
            $nagios_longoutput .= "*** Product \"$product\" is expired since ".abs($remaining_days)." days !\n";
            $nbr_license_expired++;
        }
        
        # Check if we must set Nagios status to CRITICAL or WARNING
        if ($nbr_license_expiring_very_soon || $nbr_license_expired) {
            $nagios_status = "CRITICAL";
        } else {
            $nagios_status = "WARNING" if $nagios_status ne "CRITICAL";
        }
    }
}

# Format Nagios output
$nagios_output .= "$nagios_status: ";

if ($nbr_license_expired) {
    $nagios_output .= "$nbr_license_expired products licenses are expired";
    
    if ($nbr_license_expiring_soon) {
        $nagios_output .= ", $nbr_license_expiring_soon will expire soon";
    }
    
    if ($nbr_license_expiring_very_soon) {
        $nagios_output .= ", $nbr_license_expiring_very_soon are about to expire";
    }
    
    $nagios_output .= " !\n";
    $nagios_status_code = 2;
} elsif ($nbr_license_expiring_soon || $nbr_license_expiring_very_soon) {
    if ($nbr_license_expiring_soon) {
        $nagios_output .= "$nbr_license_expiring_soon products licenses will expire soon";
    }
    
    $nagios_output .= ", " if $nbr_license_expiring_soon && $nbr_license_expiring_very_soon;
    
    if ($nbr_license_expiring_very_soon) {
        $nagios_output .= "$nbr_license_expiring_very_soon products licenses are about to expire";
        $nagios_status_code = 2;
    }
    
    $nagios_output .= " !\n";
    $nagios_status_code = 1 if $nagios_status_code != 2;
} else {
    $nagios_output .= "Licenses are up to date.\n";
}

print $nagios_output;
print $nagios_longoutput if $nagios_longoutput;
exit $nagios_status_code;
#
#-END-NAGIOS OUTPUT------------------------------------------------------------/
