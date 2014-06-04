# -*- coding: utf-8 -*-
import urlparse

from openerp.osv import osv, fields

class view(osv.osv):
    _inherit = "ir.ui.view"
    
    def save_embedded_field(self, cr, uid, el, context=None):
        Model = self.pool[el.get('data-oe-model')]
        field = el.get('data-oe-field')

        column = Model._all_columns[field].column
        converter = self.pool['website.qweb'].get_converter_for(
            el.get('data-oe-type'))
        value = converter.from_html(cr, uid, Model, column, el)
        
        url = el.find('img').get('src')
        url_object = urlparse.urlsplit(url)
        query = dict(urlparse.parse_qsl(url_object.query))
        if query['model'] == 'ir.attachment' and url_object.path == '/website/image':
            attach_obj = self.pool[query['model']].browse(cr, uid, int(query['id']), context=context)
            filename = attach_obj.datas_fname
            context.update({'filename': filename})
        
        if value is not None:
            # TODO: batch writes?
            Model.write(cr, uid, [int(el.get('data-oe-id'))], { field: value}, context=context)
            if el.get('data-oe-model') == 'product.template':
                # Delete attachment
                self.pool.get(query['model']).unlink(cr, uid, int(query['id']))