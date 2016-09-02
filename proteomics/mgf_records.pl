# Author: John B Damask
# Created: September 2016
# Purpose: Allows for flexible printing of Mascot input files of format mgf.
# Synopsis: Print first record:
#               perl mgf_records.pl NewBlack_Hela_TMT_2hr_SPS_v3_2.mgf
#           Print first 10 lines of first 2 records
#               perl mgf_records.pl NewBlack_Hela_TMT_2hr_SPS_v3_2.mgf 2 10
use strict;
$/ = "END IONS";
open FILE, $ARGV[0] or die $!;
my $i=1; # Print single record by default
my $printMax=1;
if(defined $ARGV[1]) {
    $printMax = $ARGV[1];
}
my $printLines=-1; # Print entire record by default
if(defined $ARGV[2]) {
    $printLines = $ARGV[2];
}
while(<FILE>) {
    if($i>$printMax){exit;}
    if($printLines>0){
       	my @a=split("\n");
       	for(my $j=0; $j<$printLines; $j++){
       	    print $a[$j] . "\n";
       	}
       	print "END IONS". "\n";
    } else {
       	print $_ . "\n";
    }
    $i++;
}
close FILE;
