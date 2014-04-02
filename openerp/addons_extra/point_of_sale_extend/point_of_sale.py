from openerp.osv import fields, osv
import openerp
    
class product_product(osv.osv):
    _inherit = 'product.product'
    
    def edit_ean(self, cr, uid, ids, context):
        products = self.browse(cr, uid, ids, context=context)
        for product in products:
            name = product.categ_id.name.lower()
            parent_name =  product.categ_id.parent_id.name.lower()
            id = str(product.id)
            default_code = parent_name[:3] +'.' + name[:3] +'.' + id
            default_code = ''.join([i if ord(i) < 128 else '' for i in default_code])
            ean13 = openerp.addons.product.product.sanitize_ean13(default_code)
            self.pool.get('product.product').write(cr,uid,ids,{'ean13':ean13})
            self.pool.get('product.product').write(cr,uid,ids,{'default_code':default_code})
        