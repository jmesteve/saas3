openerp.leftbar_hide = function(instance) {
	
	var toggle = false;
	var toggleLeftbar = function (velocity){
		if(toggle === true){
			$(".oe_leftbar").hide(velocity);
		}
		else{
			$(".oe_leftbar").show(velocity);
		}
	}
	
	function addClassNameListener(Class, callback) {
		elem = $(Class);
	    window.setInterval( function() {   
	       var className = elem.attr('class');
	        if (typeof className !== "undefined" && className.search("oe_wait") !== -1) {
	            callback("fast");   
	        }
	        if(typeof className === "undefined"){
	        	elem = $(Class);
	        }
	        leftbar = $("a.leftbar");
	        if(typeof leftbar !== "undefined" && !leftbar.hasClass("bind")){
	        	leftbar.unbind();
	        	leftbar.addClass("bind");
	        	leftbar.click(function(){
	        		if(toggle === true){
	        			toggle = false;
	        		}
	        		else{
	        			toggle = true;
	        		}
	        		toggleLeftbar("slow");
	        	});
	        }
	    },10);
	}
	
	addClassNameListener(".openerp_webclient_container", toggleLeftbar);
};
