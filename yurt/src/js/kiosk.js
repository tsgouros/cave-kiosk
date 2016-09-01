/*
 * \author Heather Sha (hsha), 2016
 *
 * \JS functions for handling login credentials
 * \password setting and signout timer
 *
 */

var pswMap = {};
var curUser = undefined;
var timeout;
//showing alert every 20 mins - needs to double check with Kiosk sleep 
//sign out user if no repsonses is given in 10 secs 
var idleTime = 1000 * 1200, timeoutTime = 10000;
var curProgram, curTab;
var stderr = "apps/error.txt";


//reading an external file and populate the dropdown list
//also store user-password key-value pairs in a hashmap
$(function() {
	$.ajaxSetup({ cache: false });
	PopulateDropdown();
	//populate dropdown list while storing password user-password pairs in a hashmap
	function PopulateDropdown() { 
	    var inputfile="PSDFILEPATH";
	    var DDL = $("#userNames");
            DDL.append("<option value> </option>"); 
	    $.get(inputfile,function(data) {
	        var entryList = data.split("\n");
	        for (var i=0; i < entryList.length-1; i++) {
	        	var temp = entryList[i].split(",");
	        	//setting user-password key-value pair in a hashmap
	        	pswMap[temp[0]] = temp[1];
	        }   

		Object.keys(pswMap).sort().forEach(function(key) {
  			DDL.append("<option value='" + key + "'>" + key + "</option>")
		});


		    if (pswMap[curUser] == "12345"){
		        $('#reset-password').modal({
		        	backdrop: 'static',
		        	keyboard: false,
		        	show: true
		        });
		        document.getElementById("reset-instruction").innerHTML = "This is the first time you have signed in. Please choose your own password."
		    }
	    });
	}

	$("#resetPsw").click(function(){
        $("#resetContent").toggle();
    });
	getSTDERR();
});


//this function gets and displays error messages read from @stderr
//it deletes the temporary file @stderr by executing del.cgi to avoid duplication
function getSTDERR(){
	setTimeout(function(){	
		$.get(stderr, function(data){
			console.log(data);
			if (data != undefined){
				var stderrMsg  = document.createElement("p");
				var content = document.createTextNode(data.toString());
				stderrMsg.appendChild(content);
				document.getElementById("login-container").appendChild(stderrMsg);
			 }
		});
		$.ajax({
			url : 'del.cgi',
			method : 'post'
		});
	}, 5000);
}

//this function is called from index.cgi when the user is logged in
function setCurUser(name){
	curUser = name
}

//password verification
//success: change url, start idle timer
//otherwise: alert user of invalid user-password combination
function verifyPsw(curTab){
	curUser = document.getElementById("userNames").value;
    var password = document.getElementById("user-password").value;
    if (password != "12345"){
    	password = Sha1.hash(password.toString());
	}
	if (pswMap[curUser] == password){
		window.location.href = '?user=' + curUser.toLowerCase() + "&tab=" + curTab;
	}else{
		$("#log-in").modal('hide');
		curUser = undefined;
		alert("Your password is incorrect")
	}	
}



// @username, @program, @tab - $cur_user, $program and $current_tab values passed from kiosk.cgi
// this function starts the idleTimer (20 mins), and is being called from index.cgi if users are logged in
// the timer will be reset when there's a click on the screen (or poke by hand)
// if the timer is not cleared in 20 mins, the alert will show up and prompt users to confirm their presence
function detectIdle(username, program, tab){
	curUser = username;
	curProgram = program;
	curTab = tab;
	timeout = setTimeout(createAlert, idleTime)
}


//this function clears and resets the idleTimer for a new 20 mins session (@idleTime)
function resetIdleTimer(){
	clearTimeout(timeout);
	timeout = setTimeout(createAlert, idleTime);
}


//this function creates the alert for users to confirm their presence
//users will be logged out if not response is given in 10 secs (@timeoutTime)
function createAlert(){
	var val = parseInt(timeoutTime)/1000;
	    swal({
		title: "Auto close alert!",
		text: "Please confirm your presence <br>" + "or else you will be logged out in " +
		       "<span id='alertCountDown'>"+ val +"</span> seconds.",
		html: true,
		timer: timeoutTime,
		showConfirmButton: true,
		confirmButtonClass: 'btn-confirm',
        confirmButtonText: 'Yes, I am here',
	},function (isConfirm) {
			if(isConfirm == true){
				clearInterval(alertTime);
				resetIdleTimer();
			}else{
				signOut();
			}
		}
	);
	//showing countdown time in the alert box
	var alertTime = setInterval(function(){
		val = parseInt(val) - 1;
    	document.getElementById("alertCountDown").innerHTML = val;
    }, 1000);

}


//change url and clear idleTimer
function signOut(){
	clearTimeout(timeout);
	window.location = curProgram + "?tab=" + curTab;
}


//write new password to the password.txt file
//password is encrypted using SHA-1
function updatePsw(user){
	var password = Sha1.hash(document.getElementById('password').value);
	$.ajax({
	    //cache: false,
            url     : 'psd.cgi',
            method  : 'post',
            data    : "username=" + user + "&password=" + password,
            success : function( response ) {
                alert("You have successfully reset your password")
            },
            error: function (request, status, error) {
                alert(request.responseText);
            }
        });
	$("#reset-password").modal('hide');
}



// when the users reset password, check if the inputs are valid
// prompt the users to re-enter if 
// 1. the password is the same as the default password "12345"
// 2. the password is shorter than 5 chars
// 3. repeat password does not match 
function validateInput(user){
	var password = document.getElementById('password').value;
	var repeat = document.getElementById('confirm-password').value;
	if (password == "12345") alert("Your new password cannot be the same as the default password.");

	else if (password.length < 5) alert('Your new password needs to be have at least 5 characters');
	else{
		if (repeat != password){
			alert("The password you entered do not match each other. Please try again")
		}else{
			updatePsw(user);
		}
	}
}


//convert js interpretable time into human understandable format
//this function is never used atm
function convertTime(time){
	var seconds = parseInt(time / 1000)
	var minutes = parseInt(seconds / 1000)
	if (minutes > 0){
		return minutes + "minutes"
	}else{
		return seconds + " seconds"
	}
}


//capitalize first letter
//this function is never used atm
String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}