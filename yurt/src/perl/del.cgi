#!/usr/bin/perl
use CGI;
use strict;
use warnings;

my $cgi = CGI->new;
print $cgi->header('text/plain;charset=UTF-8');

system("rm /users/cavedemo/yurt-kiosk-test/error.txt");
