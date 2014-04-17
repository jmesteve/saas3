from openerp.osv import osv, fields

class google_map_partner_comparison(osv.osv):
    _name = "map.partner.comparison"
        
    def _get_id_maps(self, cr, uid, ids,name, arg, context=None):
        res = dict.fromkeys(ids, False)
        for id in ids:
            res[id] = id
        return res
    
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'id_maps': fields.function(_get_id_maps, type='integer', string='Id Maps'),
        'partners': fields.many2many('res.partner',
                 'google_map_comparison_res_partner',
                 'id',
                 'partner_id',
                 'Partners')
    }
    
    _defaults = {
    }
    
    def open_map_partners_wizard(self, cr, uid, ids, context=None):
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'google_map_kml', 'view_partner_form_map_wizard_comparison')
        view_id = view_ref and view_ref[1] or False
        
        ctx = dict(context)
        ctx.update({
            'default_id_maps': ids[0]
        })
        
        return {
             'name': 'Google Maps',
             'type': 'ir.actions.act_window',
             'res_model': 'map.partner.comparison',
             'view_id': view_id,
             'target': 'new',
             'view_mode': 'form',
             'context': ctx
        }
    
    def open_map_partners(self, cr, uid, ids, context=None):
        ctx = dict(context)
        ctx.update({
            'default_id_maps': ids[0]
        })
        
        return {
             'name': 'Google Maps',
             'type': 'ir.actions.client',
             'tag': 'location_map.partners_comparison',
             'context': ctx
        }

google_map_partner_comparison()