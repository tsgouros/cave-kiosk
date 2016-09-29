#!/usr/bin/perl
use CGI;
use strict;
use warnings;
use lib qw(/var/www/html/kiosk/lib/installed/share/perl5);
use JSON;

my $filename = "/users/cavedemo/error.txt";

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

#system("rm /users/cavedemo/scratch/tmp/error.txt");

