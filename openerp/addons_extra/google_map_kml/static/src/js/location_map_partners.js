
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
	
	var createMarkers = function(isPoint){
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
							if(isPoint){
								image = instance.session.origin + "/google_map_kml/static/src/img/points/" + partner_main.googlemap_marker_color + "_point.png"
							}
							else if(partner_main.googlemap_select_image && partner_main.has_image){
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
	
	var createMarkersCompany = function(isPoint) {
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
								if(isPoint){
									image = instance.session.origin + "/google_map_kml/static/src/img/points/" + partner_main.googlemap_marker_color + "_point.png";
								}
								else if(partner_main.googlemap_select_image && partner_main.has_image){
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
	
	
	var createMarkersComparison = function(isPoint) {
		if(this.map != null) {
			var Partner = new instance.web.Model('res.partner');
			var Comparison = new instance.web.Model('map.partner.comparison');
			var id_maps = this.id_maps;
			
			Comparison.query(['partners']).filter([['id','=', this.id_maps]]).limit(1).all().done($.proxy(function(partners_comparison) {
			
				Partner.query(['child_ids']).filter([['id','in', partners_comparison[0].partners]]).all().done($.proxy(function(partners_id) {
					// create markers
					var child_ids = partners_comparison[0].partners;
					for(var i=0; i < partners_id.length; i++){
						child_ids = child_ids.concat(partners_id[i].child_ids);
					}
					
					Partner.query(['id','parent_id', 'has_image', 'googlemap_marker_letter', 'googlemap_marker_color', 'googlemap_select_image', 'partner_latitude', 'partner_longitude', 'name', 'googlemap_visited']).filter([['id','in', child_ids]]).all().done($.proxy(function(partners) {
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
									
									for(var j=0; j < partners.length; j++){
										if(partners[i].parent_id[0] === partners[j].id){
											partner_main = partners[j];
											break;
										}
									}
									
									var image = instance.session.origin + "/google_map_kml/static/src/img/" + partner_main.googlemap_marker_color + "_Marker" + partner_main.googlemap_marker_letter + ".png";
									if(isPoint){
										image = instance.session.origin + "/google_map_kml/static/src/img/points/" + partner_main.googlemap_marker_color + "_point.png";
									}
									else if(partner_main.googlemap_select_image && partner_main.has_image){
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
					this.createMarkers(false);
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
	});
	
	instance.google_map_kml.MapPartnerPoint = instance.web.form.AbstractField.extend({
		mapElementId: 'location_map_partners_point',
		map: null, // google.maps.Map instance
		markers: [], // partner's location marker
		template: 'location_map.partners_new_window_point',
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
					this.createMarkers(true);
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
	
	instance.google_map_kml.MapPartnerCompanyPoint = instance.google_map_kml.MapPartner.extend({
		mapElementId: 'location_map_partners3_point',
		id_maps: null,
		template: 'location_map.partners_new_window_company_point',
		createMarker: createMarker,
		createMarkers: createMarkersCompany,
		setSearchBox: setSearchBox,
		start: function(){
			var self = this;
			this._super.apply(this, arguments);
			
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById(this.mapElementId), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});
				    this.setSearchBox();
					this.createMarkers(true);
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
	});
	
	instance.google_map_kml.MapPartnerComparison = instance.google_map_kml.MapPartner.extend({
		mapElementId: 'location_map_partnerscomparison',
		id_maps: null,
		template: 'location_map.partners_comparison_wizard',
		createMarker: createMarker,
		createMarkers: createMarkersComparison,
		setSearchBox: setSearchBox,
	});
	
	instance.google_map_kml.MapPartnerComparisonPoint = instance.google_map_kml.MapPartner.extend({
		mapElementId: 'location_map_partnerscomparison_point',
		id_maps: null,
		template: 'location_map.partners_comparison_wizard_point',
		createMarker: createMarker,
		createMarkers: createMarkersComparison,
		setSearchBox: setSearchBox,
		start: function(){
			var self = this;
			this._super.apply(this, arguments);
			
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById(this.mapElementId), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});
				    this.setSearchBox();
					this.createMarkers(true);
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
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
				    this.create_markers(false);
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
	});
	
	instance.google_map_kml.OpenMapPoint = instance.google_map_kml.OpenMap.extend({
		mapElementId: 'location_map_partners_point',
		template: 'location_map.partners_point',
		start: function(){
			var self = this;
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById(this.mapElementId), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});			
				    this.setSearchBox();
				    this.create_markers(true);
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		}
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
				    this.create_markers(false);
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
	});
	
	instance.google_map_kml.OpenMapCompanyPoint = instance.google_map_kml.OpenMapCompany.extend({
		mapElementId: 'location_map_partners_company_point',
		template: 'location_map.partners_company_point',
		start: function(){
			var self = this;
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById(this.mapElementId), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});			
				    this.setSearchBox();
				    this.create_markers(true);
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
		},
	});
	
	instance.google_map_kml.OpenMapComparison = instance.google_map_kml.OpenMapCompany.extend({
		mapElementId: 'location_map_partners_comparison',
		map: null, // google.maps.Map instance
		markers: [], // partner's location marker
		template: 'location_map.partners_comparison',
		createMarker: createMarker,
		create_markers: createMarkersComparison,
		setSearchBox: setSearchBox
	});
	
	instance.google_map_kml.OpenMapComparisonPoint = instance.google_map_kml.OpenMapComparison.extend({
		mapElementId: 'location_map_partners_comparison_point',
		template: 'location_map.partners_comparison_point',
		start: function(){
			var self = this;
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById(this.mapElementId), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});			
				    this.setSearchBox();
				    this.create_markers(true);
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
	
	instance.google_map_kml.location_autocomplete = instance.web.form.FieldChar.extend({
	    template: 'location_autocomplete',
	    init: function (field_manager, node) {
	        this._super(field_manager, node);
	        this.password = this.node.attrs.password === 'True' || this.node.attrs.password === '1';
	    },
	    initialize_content: function() {
	        this.setupFocus(this.$('input'));
	        this.autocomplete = false;
	        var options = {
	        		types: ['geocode']
	        };
	        var componentForm = {
	        		  street_number: ['long_name'],
	        		  route: ['long_name'],
	        		  locality: ['long_name'],
	        		  administrative_area_level_2: ['short_name', 'long_name'],
	        		  administrative_area_level_1: ['short_name', 'long_name'],
	        		  country: ['short_name', 'long_name'],
	        		  postal_code: ['short_name']
	        };
	        var fields = this.fields;
	        var field_manager = this.field_manager;
	        var input = this.$('input').get(0);
	        if(typeof google !== "undefined" && typeof input !== "undefined") {
			   var autocomplete = new google.maps.places.Autocomplete(input, options);
			   google.maps.event.addListener(autocomplete, 'place_changed', function() {
				   var place = autocomplete.getPlace();
				   if(place && place.address_components){
					   var values = {};
					   for (var i=0; i < place.address_components.length; i++){
						   var addressType = place.address_components[i].types[0];
						   values[addressType] = {};
						   if (componentForm[addressType]) {
							   for (var j=0; j < componentForm[addressType].length; j++){
							   
								   var val = place.address_components[i][componentForm[addressType][j]];
								   values[addressType][componentForm[addressType][j]] = val;
							   }
						   }
					   }
						   
					   var street = "";
					   if(values['route'] && values['street_number']){
						   street = values['route']['long_name'] + ", " + values['street_number']['long_name'];
					   }
					   else if(values['route']){
						   street = values['route']['long_name'];
					   }
					   var Partner = new instance.web.Model('res.partner');
					   
					   state_name = "";
					   state_code = "";
					   if(values['administrative_area_level_2']){
						   state_code = values['administrative_area_level_2']['short_name'];
						   state_name = values['administrative_area_level_2']['long_name'];
					   }
					   else if(values['administrative_area_level_1']){
						   state_code = values['administrative_area_level_1']['short_name'];
						   state_name = values['administrative_area_level_1']['long_name'];
					   }
					   
					   country_name = "";
					   country_code = "";
					   if(values['country']){
						   country_code = values['country']['short_name'];
						   country_name = values['country']['long_name'];
					   }
					   
					   Partner.call('location_autocomplete_content', [state_code, state_name, country_code, country_name]).then(function(result) {
						   field_manager.set_values({
					            "city": values['locality'] && values['locality']['long_name'] ? values['locality']['long_name'] : "",
					            "zip": values['postal_code'] && values['postal_code']['short_name'] ? values['postal_code']['short_name'] : "",
					            "street": street ? street : field_manager.get_field_value('street'),
					            "country_id": result['country_id'],
					            "state_id": result['state_id']
					       });;
			            });						   
				   }
			   });
			}
	    }
	});
	
	instance.web.client_actions.add('location_map.partners', 'instance.google_map_kml.OpenMap');
	instance.web.client_actions.add('location_map.partners_point', 'instance.google_map_kml.OpenMapPoint');
	instance.web.client_actions.add('location_map.partners_company', 'instance.google_map_kml.OpenMapCompany');
	instance.web.client_actions.add('location_map.partners_company_point', 'instance.google_map_kml.OpenMapCompanyPoint');
	instance.web.client_actions.add('location_map.partners_comparison', 'instance.google_map_kml.OpenMapComparison');
	instance.web.client_actions.add('location_map.partners_comparison_point', 'instance.google_map_kml.OpenMapComparisonPoint');
	
	instance.web.form.widgets.add('google_map_partner', 'instance.google_map_kml.MapPartner');
	instance.web.form.widgets.add('google_map_partner_point', 'instance.google_map_kml.MapPartnerPoint');
	instance.web.form.widgets.add('google_map_partner_one', 'instance.google_map_kml.MapPartnerOne');
	instance.web.form.widgets.add('google_map_partner_company', 'instance.google_map_kml.MapPartnerCompany');
	instance.web.form.widgets.add('google_map_partner_company_point', 'instance.google_map_kml.MapPartnerCompany');
	instance.web.form.widgets.add('google_map_partner_comparison', 'instance.google_map_kml.MapPartnerComparison');
	instance.web.form.widgets.add('google_map_partner_comparison_point', 'instance.google_map_kml.MapPartnerComparisonPoint');
	instance.web.form.widgets.add('google_map_partner_website_button_visited', 'instance.google_map_kml.WebsiteButtonVisited');
	instance.web.form.widgets.add('google_map_partner_website_button_select_image', 'instance.google_map_kml.WebsiteButtonSelectImage');
	instance.web.form.widgets.add('location_autocomplete', 'instance.google_map_kml.location_autocomplete');
}
