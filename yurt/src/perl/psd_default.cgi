#!/usr/bin/perl

use CGI;
use strict;
use warnings;
use lib qw(/var/www/html/kiosk/lib/installed/share/perl5);
use JSON;

# read the CGI params
my $cgi = CGI->new;
my $cur_username = $cgi->param("username");
my $cur_password = $cgi->param("password");
my $filename = 'PSDFILEPATH';
my $passwordReset = 0;
my $username;
my $password;


my @rst = ();


open(FILE, "$filename") || die "password file cannot be opened";

	while ( my $line = <FILE> ){
		chomp $line;
		( $username, $password ) = split( ",", $line);
		if (defined $cur_username) {
			if ( $cur_username eq $username ){
					if ($password eq "12345"){
						$passwordReset = 1;
					}
					
				}
		}
}
close ( FILE );




if ($passwordReset eq 0){
	push @rst, "no";
	print $cgi->header('application/json');
	print encode_json(\@rst);
}else{
	push @rst, "yes";
	print $cgi->header('application/json');
	print encode_json(\@rst);
}


