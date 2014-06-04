from openerp.osv import orm, fields 

class product_product(orm.Model):
    _inherit = "product.template"
    
    def _migrate_images_to_files(self, cr, uid, context=None):
        product_ids = self.search(cr, uid, [], context=context)
        product_templates = self.browse(cr, uid, product_ids, context=context)
        for product_template in product_templates:
            if product_template.image:
                # Copiar imagen antigua desde la base de datos
                image = product_template.image
                
                # Borrar todas las imagenes de website si las hay
                images_ids = self.read(cr, uid, product_template.id, ['image_website_ids'], context=context)['image_website_ids']
                if images_ids:
                    self.pool.get('product.images.website').unlink(
                                                                   cr,
                                                                   uid, 
                                                                   images_ids, 
                                                                   context=context
                                                                   )
                
                # Crear nueva imagen
                # La imagen se asocia automaticamente al producto al poner el id
                res = {
                       'file': image,
                       'product_id': product_template.id, 
                       'filename': 'image_migrate.jpg'
                       }
                self.pool.get('product.images.website').create(cr, uid, res, context=context)
                
    def _delete_bin_images(self, cr, uid, context=None):
        # Borrar imagen antigua de la base de datos
        product_ids = self.search(cr, uid, [], context=context)
        self.write(cr, uid, product_ids, {'image': False}, context=context)
                