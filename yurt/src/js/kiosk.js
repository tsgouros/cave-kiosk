var pswMap = {};
var curUser = undefined;
var timeout;
//showing alert every 30 mins.
//sign out user if no repsonses is given in 10 secs 
var idleTime = 1000 * 1800, timeoutTime = 10000;
var curProgram, curTab;
var stderr = "apps/error.txt";

//reading an external file and populate the dropdown list
//also store user-password key-value pairs in a hashmap
$(function() {
	$.ajaxSetup({ cache: false });

	$("#resetPsw").click(function(){
        $("#resetContent").toggle();
    });
	getSTDERR();
});


//populate dropdown menu
function PopulateDropdown(data){
   var DDL = $("#userNames");
   DDL.append("<option value> </option>");

   for (var i=0; i < data.length-1; i++) {
	var temp = data[i].split(",");
        pswMap[temp[0]] = temp[1];
   }

   Object.keys(pswMap).sort().forEach(function(key) {
	DDL.append("<option value='" + key + "'>" + key  + "</option>");   
   });
  
}

//check if current password is the same as default password
//prompt users to reset if it is 
function checkDefault(curUser){
	if (curUser) {
		$.ajax({
	            url     : 'psd_default.cgi',
	            method  : 'post',
	            data    : "username=" + curUser  + "&password=default",
	            dataType:'json',
	            success : function( response ) {
	            if(response[0] == "yes"){
        			$('#reset-password').modal({
						 backdrop: 'static',
					       	keyboard: false,
				         	show: true
				       });
				    document.getElementById("reset-instruction").innerHTML = "This is the first time you have signed in. Please choose your own password."
	           		 }
	            },
	            error: function (request, status, error) {
	                alert("Cannot check if current password is the same as default");
	            }
	        });
	}
}


function getSTDERR(){
	setTimeout(function(){	
	$.get(stderr, function(data){
		console.log(data);
		if (data != undefined){
			//var stderrMsg  = document.createElement("p");
			//var content = document.createTextNode(data.toString());
			//stderrMsg.appendChild(content);
			//document.getElementById("login-container").appendChild(stderrMsg);
		 }
	});
	$.ajax({
		url : 'del.cgi',
		method : 'post'
	});
}, 5000);
}


//capitalize first letter
String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

function setCurUser(name){
	curUser = name
}

//password verification
//success: change url, start idle timer
//otherwise: alert user of invalid user-password combination
function verifyPsw(curTab){
	curUser = document.getElementById("userNames").value;
    var password = document.getElementById("user-password").value;
    if (curUser.length < 1){
    	alert("Please choose your username first");
    }else{

	    if (password != "12345"){
	    	password = Sha1.hash(password.toString());
		}
	    	$.ajax({
	            url     : 'psd_verify.cgi',
	            method  : 'post',
	            data    : "username=" + curUser + "&password=" + password,
	            dataType:'json',
	            success : function( response ) {
	            	if(response[0] == "yes"){
	            		window.location.href = '?user=' + curUser.toLowerCase() + "&tab=" + curTab;
	            	}else{
	            		alert("Wrong password");
	            	}
	            },
	            error: function (request, status, error) {
	                alert("password checking was not successfull");
	            }
	        });
    }

}



//@username, @program, @tab - $cur_user, $program and $current_tab values passed from kiosk.cgi
function detectIdle(username, program, tab){
	curUser = username;
	curProgram = program;
	curTab = tab;
	timeout = setTimeout(createAlert, idleTime)
}


function resetIdleTimer(){
	clearTimeout(timeout);
	timeout = setTimeout(createAlert, idleTime);
}

//ask the user if they are still there
//clear the original timer and set another timer for the prompt
//log user out if no response is given
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

	var alertTime = setInterval(function(){
		val = parseInt(val) - 1;
    	document.getElementById("alertCountDown").innerHTML = val;
    }, 1000);

}

//change url and clear timer
function signOut(){
	clearTimeout(timeout);
	window.location = curProgram + "?tab=" + curTab;
}

//write new password to the password.txt file
function updatePsw(user){
	var password = Sha1.hash(document.getElementById('password').value);
	$.ajax({
	    //cache: false,
            url     : 'psd_reset.cgi',
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
function convertTime(time){
	var seconds = parseInt(time / 1000)
	var minutes = parseInt(seconds / 1000)
	if (minutes > 0){
		return minutes + "minutes"
	}else{
		return seconds + " seconds"
	}
}
