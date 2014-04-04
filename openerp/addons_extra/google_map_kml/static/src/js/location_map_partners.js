
function map_loaded() {
	
}

openerp.google_map_kml = function (instance)
{   
	var _t = instance.web._t,
    _lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	
	instance.google_map_kml = {};
	
	

	instance.google_map_kml.MapPartner = instance.web.form.AbstractField.extend({
		map: null, // google.maps.Map instance
		markers: [], // partner's location marker
		template: 'location_map.partners_new_window',
		create_markers: function() {
			if(this.map != null) {
				var Partner = new instance.web.Model('res.partner');
				Partner.query(['partner_latitude', 'partner_longitude', 'name', 'googlemap_visited']).all().done($.proxy(function(partners) {
					// create markers
					var bounds = new google.maps.LatLngBounds();
					var map = this.map;
					var infowindows = [];
					var markersinfo = [];
					for(var i=0; i < partners.length; i++){
						var lat = partners[i].partner_latitude;
						var lng = partners[i].partner_longitude;
						var pos = new google.maps.LatLng(lat, lng);
						if(lat != 0 && lng != 0 && partners[i].googlemap_visited === true){
							bounds.extend(pos);
						}
						if(this.map) {
							if(lat != 0.0 & lng != 0.0 && partners[i].googlemap_visited === true) {
								
								if(typeof this.markers[i] !== "undefined" && this.markers[i] != null) {
									this.markers[i].setMap(null);
									delete this.markers;									
								}
								
								this.map.panTo(new google.maps.LatLng(lat, lng));
								
								var marker = new google.maps.Marker({
									position : new google.maps.LatLng(lat, lng),
									title: partners[i].name,
									map : this.map,
									draggable : false,
									raiseOnDrag : true});
								
								this.markers[i] = marker;
								markersinfo.push(marker);
								
					            var infoWindow = new google.maps.InfoWindow({
					                content: '<div><span style="display: inline-block">' + partners[i].name + '</span></div>'
					            });
					            
					            infoWindow.open(this.map, this.markers[i]);
					            google.maps.event.addListener(this.markers[i], 'click', function () {
					                infoWindow.open(map, marker);
					            });
					            
					            infowindows.push(infoWindow);
							}
						}
					}
					
					google.maps.event.addListener(map, 'zoom_changed', function() {
				        var zoomLevel = map.getZoom();
				        
				        for (var i=0; i < infowindows.length; i++){
				        	if(zoomLevel < 15){
				        		infowindows[i].close();
				        		console.log("entra zoom 1");
				        	}
				        	else{
				        		infowindows[i].open(map, markersinfo[i]);
				        		console.log("entra zoom 2");
				        	}
				        }
				      });
					
					this.map.fitBounds(bounds);
				}, this));
			}
			
		},
		init: function(field_manager, node) {
			//location_map_widget = this; // needed for workaround below
			// load google's api
			console.log("entra");
			this._super(field_manager, node);
			this.name = name;
		},
		start: function(){
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById("location_map_partners2"), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});				
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
			
			// have to refresh the value
			this.create_markers();
		},
	});
	
	instance.google_map_kml.OpenMap = instance.web.Widget.extend({
		map: null, // google.maps.Map instance
		markers: [], // partner's location marker
		template: 'location_map.partners',
		create_markers: function() {
			if(this.map != null) {
				var Partner = new instance.web.Model('res.partner');
				Partner.query(['partner_latitude', 'partner_longitude', 'name', 'googlemap_visited']).all().done($.proxy(function(partners) {
					// create markers
					var bounds = new google.maps.LatLngBounds();
					var map = this.map;
					var infowindows = [];
					var markersinfo = [];
					for(var i=0; i < partners.length; i++){
						var lat = partners[i].partner_latitude;
						var lng = partners[i].partner_longitude;
						var pos = new google.maps.LatLng(lat, lng);
						if(lat != 0 && lng != 0 && partners[i].googlemap_visited === true){
							bounds.extend(pos);
						}
						if(this.map) {
							if(lat != 0.0 & lng != 0.0 && partners[i].googlemap_visited === true) {
								
								if(typeof this.markers[i] !== "undefined" && this.markers[i] != null) {
									this.markers[i].setMap(null);
									delete this.markers;									
								}
								
								this.map.panTo(new google.maps.LatLng(lat, lng));
								
								var marker = new google.maps.Marker({
									position : new google.maps.LatLng(lat, lng),
									title: partners[i].name,
									map : this.map,
									draggable : false,
									raiseOnDrag : true});
								
								this.markers[i] = marker;
								markersinfo.push(marker);
								
					            var infoWindow = new google.maps.InfoWindow({
					                content: '<div><span style="display: inline-block">' + partners[i].name + '</span></div>'
					            });
					            
					            infoWindow.open(this.map, this.markers[i]);
					            google.maps.event.addListener(this.markers[i], 'click', function () {
					                infoWindow.open(map, marker);
					            });
					            infowindows.push(infoWindow);
							}
						}
						
						google.maps.event.addListener(map, 'zoom_changed', function() {
					        var zoomLevel = map.getZoom();
					        
					        for (var i=0; i < infowindows.length; i++){
					        	if(zoomLevel < 15){
					        		infowindows[i].close();
					        		console.log("entra zoom 1");
					        	}
					        	else{
					        		infowindows[i].open(map, markersinfo[i]);
					        		console.log("entra zoom 2");
					        	}
					        }
					      });
					}
					this.map.fitBounds(bounds);
				}, this));
			}
			
		},
		init: function(parent, name) {
			//location_map_widget = this; // needed for workaround below
			// load google's api
			
			this._super(parent);
			this.name = name;
		},
		start: function(){
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById("location_map_partners"), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});				
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
			
			// have to refresh the value
			this.create_markers();
		},
	});
	
	instance.web.client_actions.add('location_map.partners', 'instance.google_map_kml.OpenMap');
	instance.web.form.widgets.add('google_map_partner', 'instance.google_map_kml.MapPartner');
}

