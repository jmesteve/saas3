from openerp.osv import osv, fields


class google_map_partner(osv.osv):

    _inherit = "res.partner"
    
    _columns = {
        'googlemap_visited': fields.boolean('Visited'),
    }
    
    _defaults = {
        'googlemap_visited': False   
    }
#     
#     def write(self, cr, uid, ids, vals, context=None):
#         self.geo_localize(cr, uid, ids)
#         return super(google_map_partner, self).write(self, cr, uid, ids, vals, context=context)
    
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
        partner = self.pool.get('res.partner')
        
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

