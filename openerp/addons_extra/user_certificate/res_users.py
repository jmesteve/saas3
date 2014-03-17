from openerp.osv import fields, osv

class res_users(osv.osv):
    _inherit =  'res.users'
    
    def action_generate_ssl(self, cr, uid, ids, *args):
        return
#user_ssl()