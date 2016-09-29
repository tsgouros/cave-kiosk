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
my $status = $cgi->param("status");
my $filename = 'PSDFILEPATH';
my $userVerified = 0;
my $passwordVerified = 0;
my $passwordReset = 0;
my $username;
my $password;


my @rst = ();

# verify password
if ($status eq "verify"){

	open(FILE, "$filename") || die "password file cannot be opened";

		while ( my $line = <FILE> ){
			chomp $line;
			( $username, $password ) = split( ",", $line);
			if (defined $cur_username && defined $cur_password) {
				if ( $cur_username eq $username ){
						if ( $cur_password eq $password ){
							$passwordVerified = 1;
							last;
						}else {
							last;
						}
				}
		}
	}
	close ( FILE );

	if ($passwordVerified eq 0){
		push @rst, "no";
		print $cgi->header('application/json');
		print encode_json(\@rst);
	}else{
		push @rst, "yes";
		if ($passwordReset eq 0){
			push @rst, "no";
		}else{
			push @rst, "yes";
		}
		print $cgi->header('application/json');
		print encode_json(\@rst);
	}

# check if current logged in user's password is the same as default password
}elsif ($status eq "default") {
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


# reset password
}elsif ($status eq "reset"){
	open(FILE, "$filename");
	my @lines = <FILE>;
	open my $newline, '>', $filename or die "Can't write the file: $!";

	for (@lines) {
	    if ($_ =~ /\b$cur_username\b/) {
	    	print $cgi->header('text/plain;charset=UTF-8');
	        print $newline $cur_username . "," . $cur_password . "\n";
	    }else{
	    	print $cgi->header('text/plain;charset=UTF-8');
	    	print $newline $_;
	    }
	}

	close $newline

}
