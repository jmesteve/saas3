
function map_loaded() {
	
}

openerp.crm_partner_map = function (instance)
{   

	instance.web.form.widgets.add('location_map_partners', 'instance.crm_partner_map.Map');

	instance.crm_partner_map.Map = instance.web.form.AbstractField.extend({
		map: null, // google.maps.Map instance
		markers: [], // partner's location marker
		template: 'location_map_partners',
		create_markers: function() {
			if(this.map != null) {
				var Partner = new instance.web.Model('res.partner');
				Partner.query(['partner_latitude', 'partner_longitude', 'name', 'googlemap_visited']).all().done($.proxy(function(partners) {
					// create markers
					var bounds = new google.maps.LatLngBounds();
					
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
								
					            var infoWindow = new google.maps.InfoWindow({
					                content: partners[i].name
					            });
					            
					            infoWindow.open(this.map, this.markers[i]);
					            google.maps.event.addListener(this.markers[i], 'click', function () {
					                infoWindow.open(map, marker);
					            });
							}
						}
					}
					this.map.fitBounds(bounds);
				}, this));
			}
			
		},
		init: function(parent, options) {
			//location_map_widget = this; // needed for workaround below
			// load google's api		
			this._super(parent, options);
		},
		
		start: function () {
			// initialize the widget with new map
			if(typeof google !== "undefined") { // clear offline usage errors....
				    this.map = new google.maps.Map(document.getElementById("location_map_partners"), 
									{zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});				
			} else {
				this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
			}
			
			// have to refresh the value
			this.create_markers();
			return this._super();
		},

	});

}

