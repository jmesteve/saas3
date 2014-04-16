from openerp.osv import fields, osv
from openerp.addons.web.http import request

class shop_redirect(osv.osv):
    _name = 'shop.redirect'
    
    _columns = {
                'serverhost': fields.char('Server host', size=50, required=True),
                'route': fields.char('URL', size=50, required=True),
                }
    
         
    def _get_host(self, cr, uid, context=None):
        return request.httprequest.host
    
    _defaults = {
                 'serverhost': _get_host,
                 'route': '/home',
                 }
    _sql_constraints = [
        ('name_uniq', 'unique(serverhost)', 'Name must be unique per Company!'),
    ]
    
    def action_autostart(self, cr, uid, ids, context=None):
        return False

shop_redirect()