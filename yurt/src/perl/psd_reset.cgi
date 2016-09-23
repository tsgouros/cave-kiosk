
#!/usr/bin/perl

#if 0
#
# this file is being called from kiosk.js for password resetting
# it reads each line from psd.txt (@PSDFILEPATH)
# if the username in the current line does not match with the username being passed from kiosk.js
# it re-writes the original line to the psd.txt
# if the username matches, it updates the password by writing the new username,password combination to psd.txt
#endif


use CGI;
use strict;
use warnings;


# read the CGI params
my $cgi = CGI->new;
my $username = $cgi->param("username");
my $password = $cgi->param("password");
my $filename = 'PSDFILEPATH';


open(FILE, "$filename");
my @lines = <FILE>;
open my $newline, '>', $filename or die "Can't write the file: $!";

for (@lines) {
    if ($_ =~ /\b$username\b/) {
    	print $cgi->header('text/plain;charset=UTF-8');
        print $newline $username . "," . $password . "\n";
    }else{
    	print $cgi->header('text/plain;charset=UTF-8');
    	print $newline $_;
    }
}

close $newline
