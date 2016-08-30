#!/usr/bin/perl
use CGI;
use strict;
use warnings;


# read the CGI params
my $cgi = CGI->new;
print $cgi->header('text/plain;charset=UTF-8');

my $username = $cgi->param("username");
my $password = $cgi->param("password");
my $filename = 'PSDFILEPATH';


open(FILE, ">$filename") or die "Can't write the file ($filename): $!";
my @lines = <FILE>;


for (@lines) {
    if ($_ =~ /\b$username\b/) {
        print FILE $username . "," . $password . "\n";
    }else{
    	print FILE $_;
    }
}

close FILE
