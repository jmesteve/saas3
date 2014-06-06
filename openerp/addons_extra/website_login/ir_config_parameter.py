from openerp.tools import config
from openerp.osv import osv
from openerp import SUPERUSER_ID

class ir_config_parameter(osv.osv):
    _inherit = 'ir.config_parameter'
    
    def _set_website_url(self, cr, uid, context=None):
        """
        Set the parameter listed in _default_parameters.
        """
        key = 'website_payment.base.url'
        ids = self.search(cr, SUPERUSER_ID, [('key','=',key)])
        if not ids:
            self.set_param(cr, SUPERUSER_ID, key, "http://localhost:%s" % config.get('xmlrpc_port'))