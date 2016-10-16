#!/usr/bin/perl
use CGI;
use strict;
use warnings;
use lib qw(/users/cavedemo/yurt-kiosk-test/lib/installed/share/perl5);
use JSON;

my $filename = "ERRORPATH";

my $cgi = CGI->new;

my @tmp;
my @rst;
open(my $fh, "<", "$filename") or die "failed to open error file";

while (<$fh>) {
	chomp;
	push @tmp, $_;
}

close $fh;
my $scalar = join( '\n' , @tmp ) ;

push @rst, $scalar;

print $cgi->header('application/json');
print encode_json(\@rst);


