from openerp.osv import osv, fields
from openerp import tools

try:
    import simplejson as json
except ImportError:
    import json
import urllib

class google_map_partner(osv.osv):

    _inherit = "res.partner"
    _name = "res.partner"
    
    _columns = {
        'googlemap_visited': fields.boolean('Visited'),
        'partner_latitude': fields.float('Geo Latitude'),
        'partner_longitude': fields.float('Geo Longitude'),
        'date_localization': fields.date('Geo Localization Date'),
    }
    
    _defaults = {
        'googlemap_visited': False   
    }
    
    def geo_find(self, cr, uid, addr, context=None):
        key = self.pool.get('ir.config_parameter').get_param(cr, uid, "geocode_key", context)
        if key:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key='+ key +'&address='
        else:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
        url += urllib.quote(addr.encode('utf8'))
    
        try:
            result = json.load(urllib.urlopen(url))
        except Exception, e:
            raise osv.except_osv('Network error',
                                 'Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).' % e)
        if result['status'] != 'OK':
            return None
    
        try:
            geo = result['results'][0]['geometry']['location']
            return float(geo['lat']), float(geo['lng'])
        except (KeyError, ValueError):
            return None

    def geo_query_address(self, street=None, zip=None, city=None, state=None, country=None):
        if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
            # put country qualifier in front, otherwise GMap gives wrong results,
            # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
            country = '{1} {0}'.format(*country.split(',', 1))
        return tools.ustr(', '.join(filter(None, [street,
                                                  ("%s %s" % (zip or '', city or '')).strip(),
                                                  state,
                                                  country])))
 
    def write(self, cr, uid, ids, vals, context=None):
         write_return = super(google_map_partner, self).write(cr, uid, ids, vals, context=context)
         self.geo_localize(cr, uid, ids)
         return write_return
    
    def geo_localize(self, cr, uid, ids, context=None):
        # Don't pass context to browse()! We need country names in english below
        for partner in self.browse(cr, uid, ids):
            if not partner:
                continue
            result = self.geo_find(cr, uid, self.geo_query_address(street=partner.street,
                                                zip=partner.zip,
                                                city=partner.city,
                                                state=partner.state_id.name,
                                                country=partner.country_id.name), context=context)
            if result:
                super(google_map_partner, self).write(cr, uid, [partner.id], {
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.date.context_today(self, cr, uid, context=context)
                }, context=context)
        return True
    
    
    def create(self, cr, uid, vals, context={}):
        partner_id = super(google_map_partner, self).create(cr, uid, vals, context)
        self.geo_localize(cr, uid, [partner_id])
        return partner_id

    def open_map_partners_kml(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, ids, context=context)[0]
        
        urlKml = self.pool.get('googlemap.kml').get_kml_url(cr, uid, ids, context=context)
        url="http://maps.google.com/maps?q="
        url += urlKml
        
        return {
            'type': 'ir.actions.act_url',
            'url':url,
            'target': 'new'
        }
        
    def open_map_partners_wizard(self, cr, uid, ids, context=None):
        #partner = self.pool.get('res.partner')
        
        # view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'google_map_kml', 'view_partner_form_map_wizard_client')
        #view_id = view_ref and view_ref[1] or False
        
        return {
            'name': 'Google Maps Wizard',
            'type': 'ir.actions.client',
            'tag': 'location_map.partners',
        }
        
    def open_map_partners_wizard_new(self, cr, uid, ids, context=None):
        
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'google_map_kml', 'view_partner_form_map_wizard')
        view_id = view_ref and view_ref[1] or False
        
        return {
             'name': 'Google Maps Wizard',
             'type': 'ir.actions.act_window',
             'res_model': 'res.partner',
             'view_id': view_id,
             'target': 'new',
             'view_mode': 'form'
        }

