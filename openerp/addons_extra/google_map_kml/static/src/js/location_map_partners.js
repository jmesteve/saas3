
function map_loaded() {
	
}

openerp.google_map_kml = function (instance)
{   
	var _t = instance.web._t,
    _lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	
	instance.google_map_kml = {};

	var createMarker = function (map, pos, t, image, infoWindow) {
	    var marker = new google.maps.Marker({
			position : pos,
			title: t,
			map : map,
			icon: image,
			draggable : false,
			raiseOnDrag : true});
	    
	    google.maps.event.addListener(marker, 'click', function() { 
	    	infoWindow.open(map, marker);
	    }); 
	    return marker;  
	};
	
	var createMarkers = function(){
		if(this.map != null) {
			var Partner = new instance.web.Model('res.partner');
			Partner.query(['is_company', 'id', 'parent_id', 'has_image', 'googlemap_marker_letter', 'googlemap_marker_color', 'googlemap_select_image', 'partner_latitude', 'partner_longitude', 'name', 'googlemap_visited']).all().done($.proxy(function(partners) {
				// create markers
				var bounds = new google.maps.LatLngBounds();
				var map = this.map;
				var infowindows = [];
				var markersinfo = [];
				
				var partners_main=[];
				for(var i=0; i < partners.length; i++){
					if(partners[i].is_company === true){
						partners_main[partners[i].id] = partners[i];
					}
				}
				
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
							
							var partner_main = partners[i];
							if(partners[i].is_company === false && typeof partners_main[partners[i].parent_id[0]] !== "undefined"){
								partner_main =  partners_main[partners[i].parent_id[0]];
							}
							
							var image = instance.session.origin + "/google_map_kml/static/src/img/" + partner_main.googlemap_marker_color + "_Marker" + partner_main.googlemap_marker_letter + ".png";
							if(partner_main.googlemap_select_image && partner_main.has_image){
								image = instance.session.url('/web/binary/image', {model:'res.partner', field: 'image_small_map', id: partner_main.id})
							}
							
				            var infoWindow = new google.maps.InfoWindow({
				                content: '<div><span style="display: inline-block">' + partners[i].name + '</span></div>'
				            });
							
							var marker = this.createMarker(map, new google.maps.LatLng(lat, lng), partners[i].name, image, infoWindow);
							this.markers[i] = marker;
							markersinfo.push(marker);
				            
							//if(partner_main.googlemap_select_image === false){
					        //    infoWindow.open(this.map, this.markers[i]);
					        //}
				            infowindows.push(infoWindow);
						}
					}
					/*
					google.maps.event.addListener(map, 'zoom_changed', function() {
				        var zoomLevel = map.getZoom();
				        
				        for (var i=0; i < infowindows.length; i++){
				        	if(zoomLevel < 15){
				        		infowindows[i].close();
				        	}
				        	else{
				        		infowindows[i].open(map, markersinfo[i]);
				        	}
				        }
				      });
				      */
				}
				this.map.fitBounds(bounds);
			}, this));
		}
	};
	
	var createMarkersOne = function(){
		if(this.map != null) {
			var Partner = new instance.web.Model('res.partner');
			Partner.query(['is_company', 'id', 'parent_id', 'has_image', 'googlemap_marker_letter', 'googlemap_marker_color', 'googlemap_select_image', 'partner_latitude', 'partner_longitude', 'name', 'googlemap_visited']).filter([['id','=', this.id_maps]]).limit(1).all().done($.proxy(function(partners) {
				// create markers
				var bounds = new google.maps.LatLngBounds();
				var map = this.map;
				var infowindows = [];
				var markersinfo = [];
				
				var partners_main=[];
				for(var i=0; i < partners.length; i++){
					if(partners[i].is_company === true){
						partners_main[partners[i].id] = partners[i];
					}
				}
				
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
							
							var partner_main = partners[i];
							if(partners[i].is_company === false && typeof partners_main[partners[i].parent_id[0]] !== "undefined"){
								partner_main =  partners_main[partners[i].parent_id[0]];
							}
							
							var image = instance.session.origin + "/google_map_kml/static/src/img/" + partner_main.googlemap_marker_color + "_Marker" + partner_main.googlemap_marker_letter + ".png";
							if(partner_main.googlemap_select_image && partner_main.has_image){
								image = instance.session.url('/web/binary/image', {model:'res.partner', field: 'image_small_map', id: partner_main.id})
							}
							
				            var infoWindow = new google.maps.InfoWindow({
				                content: '<div><span style="display: inline-block">' + partners[i].name + '</span></div>'
				            });
							
							var marker = this.createMarker(map, new google.maps.LatLng(lat, lng), partners[i].name, image, infoWindow);
							this.markers[i] = marker;
							markersinfo.push(marker);
				            
							//if(partner_main.googlemap_select_image === false){
					        //    infoWindow.open(this.map, this.markers[i]);
					        //}
				            infowindows.push(infoWindow);
						}
					}
					/*
					google.maps.event.addListener(map, 'zoom_changed', function() {
				        var zoomLevel = map.getZoom();
				        
				        for (var i=0; i < infowindows.length; i++){
				        	if(zoomLevel < 15){
				        		infowindows[i].close();
				        	}
				        	else{
				        		infowindows[i].open(map, markersinfo[i]);
				        	}
				        }
				      });
				      */
				}
				this.map.fitBounds(bounds);
			}, this));
		}
	};
	
	var createMarkersCompany = function() {
		if(this.map != null) {
			var Partner = new instance.web.Model('res.partner');
			var id_maps = this.id_maps;
			Partner.query(['child_ids']).filter([['id','=', this.id_maps]]).limit(1).all().done($.proxy(function(partners_id) {
				// create markers
				partners_id[0].child_ids = [id_maps].concat(partners_id[0].child_ids)
				Partner.query(['has_image', 'googlemap_marker_letter', 'googlemap_marker_color', 'googlemap_select_image', 'partner_latitude', 'partner_longitude', 'name', 'googlemap_visited']).filter([['id','in', partners_id[0].child_ids]]).all().done($.proxy(function(partners) {
					var partner_main = partners[0];
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
								
								var image = instance.session.origin + "/google_map_kml/static/src/img/" + partner_main.googlemap_marker_color + "_Marker" + partner_main.googlemap_marker_letter + ".png";
								if(partner_main.googlemap_select_image && partner_main.has_image){
									image = instance.session.url('/web/binary/image', {model:'res.partner', field: 'image_small_map', id: partner_main.id})
								}									
								
					            var infoWindow = new google.maps.InfoWindow({
					                content: '<div><span style="display: inline-block">' + partners[i].name + '</span></div>'
					            });
								
								var marker = this.createMarker(map, new google.maps.LatLng(lat, lng), partners[i].name, image, infoWindow);
								this.markers[i] = marker;
								markersinfo.push(marker);
								
					            //if(partner_main.googlemap_select_image === false){
					            //	infoWindow.open(this.map, this.markers[i]);
					            //}
					            
					            infowindows.push(infoWindow);
							}
						}
						/*
						google.maps.event.addListener(map, 'zoom_changed', function() {
					        var zoomLevel = map.getZoom();
					        for (var i=0; i < infowindows.length; i++){
					        	if(zoomLevel < 15){
					        		infowindows[i].close();
					        	}
					        	else{
					        		infowindows[i].open(map, markersinfo[i]);
					        	}
					        }
					      });
					      */
					}
					this.map.fitBounds(bounds);
				}, this));
			}, this));
		}
		
	};
	
	var setSearchBox = function setSearchBox(){
		// Create the search box and link it to the UI element.
	    var input = /** @type {HTMLInputElement} */(
	        document.getElementById('pac-input'));
	    
	    input.className += " searchboxvisible";
	    
	    this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
	    
	    var searchBox = new google.maps.places.SearchBox(
	    	    /** @type {HTMLInputElement} */(input));
	    
	    var map = this.map;
	    google.maps.event.addListener(searchBox, 'places_changed', function() {
	    	var places = searchBox.getPlaces();
	    	
	    	if(places.length > 0){
	    		if(places[0].geometry.viewport !== undefined){
	    			map.fitBounds(places[0].geometry.viewport);
	    		}
	    		else{
	    			map.setZoom(14);
	    		}
	    		
	    		if(places[0].geometry.location !== undefined){
	    			map.setCenter(places[0].geometry.location);
	    		}
	    	}	
	    });
	};		
	
	instance.google_map_kml.MapPartner = instance.web.form.AbstractField.extend({
		mapElementId: 'location_map_partners2',
		map: null, // google.maps.Map instance
		markers: [], // partner's location marker
		template: 'location_map.partners_new_window',
		createMarker: createMarker,
		createMarkers: createMarkers,
		setSearchBox: setSearchBox,
		init: function(field_manager, node) {
			this._super(field_manager, node);
		},
		render_value: function() {
	        this._super();
	        this.id_maps = this.get_value();
	    },
		start: function(){
			var self = this;
			this._super.apply(this, arguments);
			
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById(this.mapElementId), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});
				    this.setSearchBox();
					this.createMarkers();
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
	});
	
	instance.google_map_kml.MapPartnerOne = instance.google_map_kml.MapPartner.extend({
		mapElementId: 'location_map_partners4',
		id_maps: null,
		template: 'location_map.partners_new_window_one',
		createMarker: createMarker,
		createMarkers: createMarkersOne,
		setSearchBox: setSearchBox,
	});
	
	instance.google_map_kml.MapPartnerCompany = instance.google_map_kml.MapPartner.extend({
		mapElementId: 'location_map_partners3',
		id_maps: null,
		template: 'location_map.partners_new_window_company',
		createMarker: createMarker,
		createMarkers: createMarkersCompany,
		setSearchBox: setSearchBox,
	});
	
	
	instance.google_map_kml.OpenMap = instance.web.Widget.extend({
		mapElementId: 'location_map_partners',
		map: null, // google.maps.Map instance
		markers: [], // partner's location marker
		template: 'location_map.partners',
		createMarker: createMarker,
		create_markers: createMarkers,
		setSearchBox: setSearchBox,
		init: function(parent, name) {
			//location_map_widget = this; // needed for workaround below
			// load google's api
			
			this._super(parent);
			this.name = name;
		},
		start: function(){
			var self = this;
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById(this.mapElementId), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});			
				    this.setSearchBox();
				    this.create_markers();
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
	});
	
	
	instance.google_map_kml.OpenMapCompany = instance.web.Widget.extend({
		mapElementId: 'location_map_partners_company',
		map: null, // google.maps.Map instance
		markers: [], // partner's location marker
		template: 'location_map.partners_company',
		createMarker: createMarker,
		create_markers: createMarkersCompany,
		setSearchBox: setSearchBox,
		init: function(parent, name) {
			//location_map_widget = this; // needed for workaround below
			// load google's api
			
			this._super(parent);
			this.name = name;
			
			this.id_maps = this.name.context.default_id_maps;
			if(typeof this.id_maps === "undefined" && typeof this.name.params.id !== "undefined"){
				this.id_maps = this.name.params.id;
			}
			else if(typeof this.id_maps === "undefined" && typeof this.name.params.active_id !== "undefined"){
				this.id_maps = this.name.params.active_id;
			}
		},
		start: function(){
			var self = this;
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById(this.mapElementId), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});			
				    this.setSearchBox();
				    this.create_markers();
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
	});
	
	
	instance.google_map_kml.WebsiteButtonVisited = instance.web.form.AbstractField.extend({
	    template: 'location_map.website_button_visited',
	    render_value: function() {
	        this._super();
	        this.$("button:first")
	            .toggleClass("btn-success", this.get_value())
	            .toggleClass("btn-danger", !this.get_value());
	        //this.$("a:first").attr("href", this.view.datarecord.website_url || "/" );
	        if (this.node.attrs.class) {
	            this.$el.addClass(this.node.attrs.class);
	        }
	    },
	    start: function() {
	        var self = this;
	        this._super.apply(this, arguments);

	        this.$("button:first").on("click", function () {
	            self.set_value(!!$(this).hasClass("btn-danger"));
	            return self.view.recursive_save();
	        });
	    },
	});
	
	instance.google_map_kml.WebsiteButtonSelectImage = instance.google_map_kml.WebsiteButtonVisited.extend({
	    template: 'location_map.website_button_selectimage',
	});
	
	instance.web.client_actions.add('location_map.partners', 'instance.google_map_kml.OpenMap');
	instance.web.client_actions.add('location_map.partners_company', 'instance.google_map_kml.OpenMapCompany');
	instance.web.form.widgets.add('google_map_partner', 'instance.google_map_kml.MapPartner');
	instance.web.form.widgets.add('google_map_partner_one', 'instance.google_map_kml.MapPartnerOne');
	instance.web.form.widgets.add('google_map_partner_company', 'instance.google_map_kml.MapPartnerCompany');
	instance.web.form.widgets.add('google_map_partner_website_button_visited', 'instance.google_map_kml.WebsiteButtonVisited');
	instance.web.form.widgets.add('google_map_partner_website_button_select_image', 'instance.google_map_kml.WebsiteButtonSelectImage');
}
