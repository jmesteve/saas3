from openerp.osv import orm, fields
import urllib
try:
    import simplejson as json
except ImportError:
    import json

class ResPartner(orm.Model):
    _inherit = "res.partner"
    _columns = {
                'location_autocomplete': fields.char('Location Autocomplete', size=60, required=False),
                }
        
    def location_autocomplete_content(self, cr, uid, state_code, state_name, country_code, country_name, context=None):
        
        if not country_code:
            country_id = False
        else:
            country_id = self.pool.get('res.country').search(cr, uid, [('code','ilike', country_code)], context=context)
            if isinstance(country_id, list) and len(country_id) > 0:
                country_id = country_id[0] 
            if not country_id:
                country_id = self.pool.get('res.country').create(cr, uid, {
                            'code': country_code,
                            'name': country_name
                        }, context=context)
        if not country_id or not state_name:
            state_id = False
        else:
            state_id = self.pool.get('res.country.state').search(cr, uid, [('name','ilike',state_name), ('country_id','=',country_id)], context=context)
            if isinstance(state_id, list) and len(state_id) > 0:
                state_id = state_id[0] 
            if not state_id:
                state_id = self.pool.get('res.country.state').create(cr, uid, {
                            'country_id': country_id,
                            'code': state_code,
                            'name': state_name
                        }, context=context)
           
        return {
                'country_id': country_id, 
                'state_id': state_id}
