from openerp.osv import osv, fields

class account_invoice(osv.osv):

     _inherit = "account.invoice"
     _columns = {
                 'move_id': fields.many2one('account.move', 'Journal Entry', readonly=False, select=1, ondelete='restrict', help="Link to the automatically generated Journal Items.")
                 }