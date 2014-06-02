from openerp.osv import fields, osv

class product(osv.osv):
    _inherit = 'product.product'
    
    _columns = {'is_delivery': fields.boolean('Is Delivery')}
    
    _defaults = {'is_delivery': False }