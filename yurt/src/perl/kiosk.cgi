#!/usr/bin/perl

#if 0
#
### \original author John Huffman
###
### \adapted by Heather Sha in 2016
### \for user credential verification and idle timer
### 
### /
#endif

use CGI;
use IPC::Open3;
use IO::Select;
use lib qw(/var/www/html/kiosk/lib/installed/share/perl5);
use JSON;

$query = new CGI;

$home = "KIOSKTARGETDIR";;
$program = "index.cgi";
$psd_path = "/users/cavedemo/etc/psd.txt";

$data_dir = "$home/apps";
$max_icon_columns = 8;
# get the user who is currently logged in
my $cur_user = $query->param('user');

# If a program was selected to run, it is passed as a "run" argument
my $run_program = $query->param('run');
$run_program =~ s/ /_/g;

# Determine current tab selected, or set to Video config, the only
# default tab
my $current_tab = $query->param('tab');
$current_tab =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
if (!$current_tab) {
  $current_tab = "Demos";
}

## Check for and run a program.  Also looks for special cases from
## Video Config menu
if ($run_program) {
  if ($run_program eq "kill") {
    system("apps/System/Kill_All_Cave_Procs/run > /dev/null 2>&1 ");
    
  } elsif ($run_program eq "Turn_Off_Yurt"){
    system("apps/System/Turn_Off_Yurt/run > /dev/null 2>&1 ");
  
  } elsif ($run_program eq "Turn_On_Yurt"){
    system("apps/System/Turn_On_Yurt/run > /dev/null 2>&1 ");	

  } else {
#This is where a program gets run.  The script looks for a "run"
#script in the tab directory, and runs it.
    if (-e "$home/apps/$current_tab/$run_program/run" ) {
     $pid = fork();
     if ($pid == 0) {
      system("apps/System/Kill_All_Cave_Procs/run > /dev/null 2>&1 ");
system("ssh -t cave001 $home/apps/$current_tab/$run_program/run> $home/log/running.stdout 2> $home/log/running.stderr &");
#system("ssh -t cave001 /users/cavedemo/yurt-kiosk/$current_tab/$run_program/run> $home/log/running.stdout 2> $home/log/running.stderr & ");
	#exec("ssh -t cave001 /users/cavedemo/yurt-kiosk/$current_tab/$run_program/run > $home/log/running.stdout 2> $home/log/tmp.stderr &");
      #exec("$home/apps/$current_tab/$run_program/run > $home/log/running.stdout 2> $home/log/running.stderr &");
       exit(0); 
    }
      sleep 1;
    }
    
    # If the application is not marked as a "dont_kill" app, get its
    # PID and location and save it to a file
    if (!-e "apps/$current_tab/$run_program/dont_kill") {
      open  (FILE, ">$home/log/running");
      print FILE "$current_tab/$run_program\n$pid\n";
      close(FILE);
    }
  }
  
  #Add to the log when the file was run
  open  (FILE, ">>$home/log/running.log");
  $datetime = localtime(time());
  print FILE "$cur_user  [$datetime]: $current_tab/$run_program\n";
  close(FILE);
 
}

# Get the name of the currently running program to display in the
# "running" bar
if (-e "$home/log/running") {
  open(FILE, "<$home/log/running"); 
  @lines = <FILE>;   
  $running_program = $lines[0];
  chomp($running_program);
  $running_pid = $lines[1];
  chomp($running_pid);
}
    

#Get the top level directories, these will be the tabs (stored in
#[tab_names]
opendir(DIR, $data_dir);
my @dir_names = grep -d "$data_dir/$_", readdir DIR;
$j = 0;
foreach $f (@dir_names) { $i{$f} = -M "$data_dir/$f" }
foreach $k (sort{ $i{$b} <=> $i{$a} } keys %i)
{ unless ( ($k eq ".") || ($k eq "..") ) {$tab_names[$j++] = $k;}  }
close (DIR);


$app_dir = "$data_dir/$current_tab/";
my %apps;
if (-e $app_dir ) {
  opendir(DIR, $app_dir);
  @app_dirs = grep -d "$app_dir/$_", readdir DIR;
  $j = 0;
  foreach $k (sort( @app_dirs ))
  { unless ( ($k eq ".") || ($k eq "..") ) { $unsorted_apps{$k}=$j; $app_names[$j++] = $k; }  }
  closedir(DIR);
} 
else {
#  print "$app_dir does not exist\n";
}


my %categories;
my @sorted_categories;
$i=0;
$j=0;
if ( -e "$app_dir/categories" ) {
  $current_category = "";
  open(FILE, "< $app_dir/categories"); 
  while ( <FILE> ) {
    chomp;
    $current_line=$_;
    if ($current_line =~ /^[A-Z][a-z]/ ) {
	  $current_line =~ s/ /_/g;
      $current_category = $current_line;
       $i = 0;
      $sorted_categories[$j++] = $current_line;
    }
    else {
	    $current_line =~ tr/ //ds;
	    $current_line =~ s/ /_/g;	    
	    $categories{$current_category}[$i++] = $current_line;
	    
	    delete $unsorted_apps{$current_line};
    }
  }
}
#s/_/ /g for(@sorted_categories);
s/_/ /g for(@app_names);


# getting and storing all user names from the psd.txt file into an array
# encode the perl array into json object so that can be used for populating the dropdown menu
my @usernname_array = ();
open (FILE, $psd_path) || die "the password file cannot be found";
while ($line = <FILE>){
  chomp $line;
  ($username, $password) = split(",", $line);
  push @username_array, $username;
}

my $json_str = encode_json(\@username_array);

# Generate kill buttons
# #########################################################################
sub generate_button{
  my $command = $_[0];
  print"      <td class=\"program\" style=\"text-align: center;width: 72px; height: 72px;\"> None </td>\n";
  print"      <td\><button onClick=\"$command;\">\n";    \
  print"      <img style=\"width: 54px; height: 54px;\" src=\"img/skull.png\"></button></td>\n";
  }

# HEADER  Initial header for HTML page.  This always stays the same
################################################################################
print << "((END HTML HEADER))";
Content-type: text/html


<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" dir="ltr">
<style type="text/css" >\@import url("apps/$current_tab/style.css");</style>
<head>
<!-- render in IE edge -->
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
<meta name="viewport" content="width=device-width, initial-scale=1">

<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">


<!-- css for alert box -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/sweetalert/1.1.3/sweetalert.css">

<!-- css for the login widget interface -->
<link rel="stylesheet" href="css/login.css">
<link rel="stylesheet" href="http://fonts.googleapis.com/css?family=Open+Sans:300,400,700">

<script src="http://code.jquery.com/jquery-1.11.2.min.js"></script>

<!-- sweeralert library-->
<script type="text/javascript" src="js/sweetalert.min.js"></script>
<script src="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>

<!-- js scripts for login and timer -->
<script type="text/javascript" src="js/kiosk.js"></script>
<script type="text/javascript" src="js/slider.js"></script>
<script type="text/javascript" src="js/sha1.js"></script>
<!-- boostrap IE -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js" ></script>
<script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
<script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
<title>CAVE Kiosk: $current_tab</title>

</head>
((END HTML HEADER))




print"   <script type=\"text/javascript\"> \n";
print"   function goLink(args) { \n";
print"   window.location.href = args; \n";
print"   }\n";


print" jQuery(function() { PopulateDropdown($json_str);}); \n";
print" jQuery(function() { checkDefault('$cur_user');}); \n";

# This first checks if current web browser is IE or Edge - if it is, KIOSK virtual keyboard will be initiated
# This block of codes also resets idle timer when user taps on the KIOSK screen
# ##################################################################################################

print << "((END KIOSK KEYBOARD))";
function keyboardStart(){
        var isIE = /*@cc_on!@*/false || !!document.documentMode;
        var isEdge = !isIE && !!window.StyleMedia;
        if (isIE || isEdge){
          var obj = new ActiveXObject("WScript.shell");
          obj.run(' "C:\\Program Files\\Common Files\\Microsoft Shared\\ink\\tabtip.exe" ');
      }
}
((END KIOSK KEYBOARD))

if ($cur_user){
  print << "((END DETECT IDLE))";
     detectIdle('$cur_user', '$program', '$current_tab');
     document.onclick = resetIdleTimer;
     setCurUser('$cur_user');
((END DETECT IDLE))
 

}

print" </script>\n";

# THE HTML <body> starts here;
# Password rest modal is captured in ((END RESET PASSWORD MODAL))
# Login modal is captured in ((END LOGIN MODAL))
# If the user has logged in ($cur_user is set), the ((END STDRR OUTPUT)) and the sign out button will be shown
# otherwise, the sign in button will be shown            
# #######################################################################################################################

print "<body style=\"font-family:Times New Roman\"><br><br>\n";

print << "((END RESET PASSWORD MODAL))";
<!-- Modal -->
<div class="modal fade" id="reset-password" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <!-- <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> -->
        <h4 class="modal-title" id="myModalLabel">Reset Password</h4>
        <p id="reset-instruction"> </p>
      </div>
      <div class="modal-body">
        <!-- <input type="password" onfocus="keyboardStart()" class="form-control" name="password" id="curpassword" value="" placeholder="Current Password" required> -->
        <br>
        <input type="password" onfocus="keyboardStart()" class="form-control" name="password" id="password" value="" placeholder="New Password" required>
        <br>
        <input type="password" onfocus="keyboardStart()" class="form-control" name="password" id="confirm-password" value="" placeholder="Confirm Password" required>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button> 
	<button type="button" class="btn btn-primary" onclick="validateInput('$cur_user')">Save changes</button>
      </div>
    </div>
  </div>
</div>
((END RESET PASSWORD MODAL))



print << "((END LOGIN MODAL))";
<div class="modal fade" id="log-in" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h4 class="modal-title" id="myModalLabel">Log In</h4>
        <p id="reset-instruction"> </p>
      </div>
      <div class="modal-body">
        <select id="userNames" class="form-control custom"></select>
        <br>
        <input type="password" type="text" class="form-control" onfocus="keyboardStart()" name="password" id="user-password" value="" placeholder="password" required>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button> 
  <button type="button" class="btn btn-primary" onclick="verifyPsw('$current_tab')">Log In</button>
      </div>
    </div>
  </div>
</div>
((END LOGIN MODAL))

## LOGIN WIDGET
###############################################################################
if($cur_user){
print << "((END LOGIN WIDGET))";
	<div id="intro">This is a testing version of the Kiosk that requires you to log in. To return to the original version, poke <a class="big-font" href="http://172.20.8.9/kiosk/kiosk.cgi"> here </a> </div>
	<div id="signout-wrapper">
	<button type="button" class="btn btn-secondary btn-lg" data-toggle="modal" data-target="#reset-password">Reset Password</button>
	<button type="button" class="btn btn-secondary btn-lg" onclick="signOut('$program', '$current_tab')"> Sign Out </button>	
</div>
((END LOGIN WIDGET))

print << "((END STDERR OUTPUT))"
<div class="jqm-content" id="main-container">
<div id="login-container">
</div>

<div id="login-slider">
	<div id="caption">STDERR</div>
</div>
</div>

((END STDERR OUTPUT))

}else{
print << "((END LOGIN WIDGET))";
        <div id="intro">This is a testing version of the Kiosk that requires you to log in. To go back to the original version, poke <a class="big-font" href="http://172.20.8.9/kiosk/kiosk.cgi"> here </a> </div>
<div id="login-wrapper">
	<button type="button" class="btn btn-secondary btn-lg" data-toggle="modal" data-target="#log-in">Log In</button>
</div>
((END LOGIN WIDGET))
}




## TABS  Table for top level Tabs
############################################################################
print << "((END tab table start))";
<table
 style="width: 100%; text-align: left; margin-left: auto; margin-right: auto;"
 border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td style="text-align: center; height: 60px;"
 background="img/edge_tab.png">&nbsp;</td>
((END tab table start))


#if ("Video Config" eq $current_tab) {
#  print "      <td style=\"align:center; text-align: center; height: 60px; width: 152px;\"\n";
#  print "      onClick=\"window.location='$program?tab=Video\%20Config'\"\n";
#  print "      background=\"img/open_tab.png\">Video Config</td>\n";
#}
#else {
#  print "<td style=\"text-align: center; height: 60px; width: 152px;\"\n";
#  print "      onClick=\"window.location='$program?tab=Video Config'\"\n";
#  print "background=\"img/closed_tab.png\">Video Config</td>\n";
#}


# Generate closed tabs and currently open tab
# set img/open_tab.png for opened tab background image and img/closed_tab.png for closed tab background image          
#######################################################################################################################

foreach $f (@tab_names) {
  $tab_name = $f;
  $tab_name =~ s/_/ /g;
  unless ( ($f eq ".") || ($f eq "..") ) {
    if ($f eq $current_tab) {
      if ($cur_user){
          print "      <td style=\"align:center; text-align: center; height: 60px; width: 152px;\"\n";
          print "      onClick=\"window.location='$program?&user=$cur_user&tab='\"\n";
          print "      background=\"img/open_tab.png\">$tab_name</td>\n";
        }else{
          print "      <td style=\"align:center; text-align: center; height: 60px; width: 152px;\"\n";
          print "      onClick=\"window.location='$program?tab='\"\n";
          print "      background=\"img/open_tab.png\">$tab_name</td>\n";
      }
    }
    else {
      if ($cur_user){
        print "<td style=\"text-align: center; height: 60px; width: 152px;\"\n";
        print "      onClick=\"window.location='$program?&user=$cur_user&tab=$f'\"\n";
        print "background=\"img/closed_tab.png\">$tab_name</td>\n";
      }else{
        print "<td style=\"text-align: center; height: 60px; width: 152px;\"\n";
        print "      onClick=\"window.location='$program?tab=$f'\"\n";
        print "background=\"img/closed_tab.png\">$tab_name</td>\n";
      }
    }
  }
}

print "      <td style=\"text-align: center; height: 60px;\"\n";
print "        background=\"img/edge_tab.png\">&nbsp;</td>\n";
print "    </tr>\n  </tbody>\n</table>\n";


## RUNNING  Current running program
## ((END run table start)) generates a table to hold the kill button and the current running program image
# two blocks of ((END run table start)) wrap around the ($running_program) loop for this to happen.
# In the ($running_program) loop, the program first grabs the image for the current running program - if the program has a folder.png, or else use default.png
# The program then check to see if the user is logged in and will generate the actual kill button based on the status
# ex. if the user is logged in /if ($cur_user)/, the button will be given the function Onclick="javascript:golink(specified_address)"
# otherwise, the button will simply alert the user to log in.
#######################################################################

print << "((END run table start))";
<table
 style="text-align: left; margin-left: auto; margin-right: auto;"
 border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td class="table-start" style="text-align: center; width: 12px; height: 12px;"
 background="img/border/ul.png"></td>
      <td class="table-start" style="text-align: center; width: 12px; height: 12px;"
 background="img/border/top.png"></td>
      <td class="table-start" style="text-align: center; width: 12px; height: 12px;"
 background="img/border/ur.png"></td>
    </tr>
    <tr>
      <td class="table-start" style="text-align: center; width: 12px; height: 12px;"
 background="img/border/left.png"></td>
      <td>
      <table
 style="width: 400px; height: 72px;text-align: left; margin-left: auto; margin-right: auto;"
 border="0" cellpadding="2" cellspacing="2">
        <tbody>
          <tr>
            <td class="table-start" style="text-align: center; height: 64px; width: 256px;">Current Running Program:<br>
((END run table start))

if ($running_program) {
  @name = split("/", $running_program);
  $name[1] =~ s/_/ /g;
  print"      $name[1]</td><td style=\"text-align: center;\"> \n";
  print"      <img style=\"width: 64px; height: 64px;\" ";
  if (-e "apps/$running_program/folder.png" ) {
    print"src=\"apps/$running_program/folder.png\"></td>\n";
  }else {
    print"src=\"default.png\"></td>\n";
   }
  if ($cur_user){
  print"      <td\><button onClick=\"javascript:goLink(\'$program?&user=$cur_user&tab=$current_tab&run=kill\');\">\n";    print"      <img style=\"width: 54px; height: 54px;\" src=\"img/skull.png\"></button></td>\n";
}else{
  print"      <td\><button onClick=\"alert(\'please log in first\')\">\n";    \
  print"      <img style=\"width: 54px; height: 54px;\" src=\"img/skull.png\"></button></td>\n";
}
}
elsif ($cur_user) {
  &generate_button("javascript:goLink(\'$program?&user=$cur_user&tab=$current_tab&run=kill\')");
}
else{
  &generate_button("alert(\'please log in first\')");
}
print << "((END run table start))";
<!--            <td style="text-align: center;"> <img
 style="width: 64px; height: 64px;" src="img/skull.png"> -->
            </td>
          </tr>
        </tbody>
      </table>
      </td>
      <td class="table-start" style="text-align: center; width: 12px; height: 12px;"
 background="img/border/right.png"></td>
    </tr>
    <tr>
      <td class="table-start" style="text-align: center; width: 12px; height: 12px;"
 background="img/border/ll.png"></td>
      <td class="table-start" style="text-align: center; width: 12px; height: 12px;"
 background="img/border/bottom.png"></td>
      <td class="table-start" style="text-align: center; width: 12px; height: 12px;"
 background="img/border/lr.png"></td>
    </tr>
  </tbody>
</table>
((END run table start))




## ICONS   Table for icons
### The program first checks to see if the user is logged in and generates the run button based on the status
# ex. if the user is logged in /if ($cur_user)/, the button will be given the function Onclick="javascript:golink(specified_address)"
# otherwise, the button will simply alert the user to log in.
############################################################################

if ($current_tab eq "Video Config") { # The video menu is special, for turning cave on/off
print << "((END icons table start))";
<table
 style="text-align: left; margin-left: auto; margin-right: auto;"
 border="0" cellpadding="10" cellspacing="10">
  <tbody>
    <tr>
      <td align="undefined" valign="undefined">
      <table
 style="text-align: left; margin-left: auto; margin-right: auto;"
 border="0" cellpadding="0" cellspacing="0">
        <tbody>
          <tr>
            <td class="table-start" 
 style="text-align: center; width: 12px; height: 12px;"
 background="img/border/ul.png"></td>
            <td class="table-start"
 style="text-align: center; width: 12px; height: 12px;"
 background="img/border/top.png"></td>
            <td class="table-start"
 style="text-align: center; width: 12px; height: 12px;"
 background="img/border/ur.png"></td>
          </tr>
          <tr>
            <td
 style="text-align: center; width: 12px; height: 12px;"
 background="img/border/left.png"></td>
            <td>
            <table
 style="width: 350px; text-align: left; margin-left: auto; margin-right: auto;"
 border="0" cellpadding="5" cellspacing="5">
              <tbody>
                <tr>
                  <td style="text-align: center;">
                  <button onClick=\"javascript:goLink(\'$program?tab=$current_tab&run=wall_on\');\"><img
 style="border: 0px solid ; width: 128px; height: 128px;" alt=""
 src="img/wall_on.png"><br>
Wall On</button></td>
                  <td style="text-align: center;">
                  <button onClick=\"javascript:goLink(\'$program?tab=$current_tab&run=wall_off\');\"><img
 style="border: 0px solid ; width: 128px; height: 128px;" alt=""
 src="img/wall_off.png"><br>
Wall Off</button></td>
                </tr>
              </tbody>
            </table>
            </td>
            <td
 style="text-align: center; width: 12px; height: 12px;"
 background="img/border/right.png"></td>
          </tr>
          <tr>
            <td
 style="text-align: center; width: 12px; height: 12px;"
 background="img/border/ll.png"></td>
            <td
 style="text-align: center; width: 12px; height: 12px;"
 background="img/border/bottom.png"></td>
            <td
 style="text-align: center; width: 12px; height: 12px;"
 background="img/border/lr.png"></td>
          </tr>
        </tbody>
      </table>
      </td>   
    </tr>
  </tbody>
</table>
((END icons table start))
}
else {  # This prints the rest of the icons

# These are icons not already in columns:

print  "<table \n  style='text-align: center; margin-left: auto; margin-right: auto;'\n";
print  " border='0' cellpadding='10' cellspacing='10'>\n  <tbody>\n    <tr>\n";

$column = 0;
foreach my $key ( sort keys %unsorted_apps ) {
  if ($column >= $max_icon_columns) {
    print"  </tr>\n    <tr>\n";
    $column = 0;
  }
    print"      <td class=\"program\" style=\"text-align: center;\"><button\n";
    if ($cur_user){
    print"          onClick=\"javascript:goLink(\'$program?&user=$cur_user&tab=$current_tab&run=$key\');\">\n"; 
    } else {
    print"          onClick=\"alert(\'please log in first\')\">\n"; 
    }   
    print"        <img style=\"width: 128px; height: 128px;\"";
    if ( -e "$app_dir/$key/folder.png" )  { print " src='apps/$current_tab/$key/folder.png'>"; }
    else { print " src='img/default.png'>"; }
    $key =~ s/_/ /g;
    print "<br>$key</button></td>\n";
    $column++;
}
print "    </tr>\n  </tbody>\n</table>\n";
$column = 0;

# These are icons/apps that are found in the categories file.
foreach my $key ( @sorted_categories ) {
  $key_with_spaces = $key;
  $key_with_spaces =~ s/_/ /g;
  
  print "<div id='$key'>\n<center> <H3>$key_with_spaces</H3></center>\n";
  print  "<table \n  style='text-align: center; margin-left: auto; margin-right: auto;'\n";
  print  " border='0' cellpadding='10' cellspacing='10'>\n  <tbody>\n    <tr>\n";
  foreach my $element ( @{$categories{$key}} ) {
  if ($column >= $max_icon_columns) {
    print"  </tr>\n    <tr>\n";
    $column = 0;
  }
    print"      <td class=\"program\" style=\"text-align: center;\"><button\n";
    if ($cur_user){
    print"          onClick=\"javascript:goLink(\'$program?&user=$cur_user&tab=$current_tab&run=$element\');\">\n"; 
    }else{
     print"          onClick=\"alert(\'please log in first\')\">\n";  
    }   
    print"        <img style=\"width: 128px; height: 128px;\"";
    if ( -e "$app_dir/$element/folder.png" )  { print " src='apps/$current_tab/$element/folder.png'>"; }
    else { print " src='img/default.png'>"; }
    $element =~ s/_/ /g;
    print "<br>$element</button></td>\n";
    $column++;  }
  print "    </tr>\n  </tbody>\n</table>\n</div>\n\n";
  $column = 0;
}
}
#use Data::Dumper;
#print Dumper(\%unsorted_apps);
#print Dumper(\%categories);

print "</body>\n";



