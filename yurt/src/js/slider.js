$(function() {
		var $mainMenu = $('#main-container');
 		var $icon = $('#login-slider');
 		var leftVal = parseInt($mainMenu.css('left'));
 		$('#login-slider').click(function () {
		     animateLeft = (parseInt($mainMenu.css('left')) == 0) ? leftVal : 0;
		     $mainMenu.animate({
				left: animateLeft + 'px'
	  	     });
		});

$(window).scroll(function(){
 		$("#main-container").stop().animate({"marginTop": ($(window).scrollTop()) + "px", "marginLeft":($(window).scrollLeft()) + "px"}, "slow" );	
	});

});

