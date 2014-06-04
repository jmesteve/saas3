# -*- coding: utf-8 -*-
#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
# Copyright (C) 2011 Akretion Sébastien BEAU sebastien.beau@akretion.com#
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################
import os
import shutil
import logging
import base64
import urllib

import openerp
from openerp.osv import orm, fields
from openerp import tools

class product_product(orm.Model):
    _inherit = "product.template"

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        original = self.read(cr, uid, id, fields=['default_code', 'image_ids'], context=context)
        default.update({
            'image_ids': False,
        })
        local_media_repository = self.pool.get('res.company').get_local_media_repository(cr, uid, context=context)
        if local_media_repository:
            if original['image_ids']:
                old_path = os.path.join(local_media_repository, original['default_code'])
                if os.path.isdir(old_path):
                    try:
                        shutil.copytree(old_path, old_path + '-copy')
                    except:
                        logger = logging.getLogger('product_images_olbs')
                        logger.exception('error while trying to copy images '
                                         'from %s to %s',
                                         old_path,
                                         old_path + '.copy')

        return super(product_product, self).copy(cr, uid, id, default, context=context)

    def get_main_image(self, cr, uid, id, context=None):
        if isinstance(id, list):
            id = id[0]
        images_ids = self.read(cr, uid, id, ['image_website_ids'], context=context)['image_website_ids']
        if images_ids:
            return images_ids[0]
        return False

    def _get_main_image(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        img_obj = self.pool.get('product.images.website')
        for id in ids:
            image_id = self.get_main_image(cr, uid, id, context=context)
            if image_id:
                image = img_obj.browse(cr, uid, image_id, context=context)
                res[id] = image.file
            else:
                res[id] = False
        return res

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        img_obj = self.pool.get('product.images.website')
        image_id = self.get_main_image(cr, uid, id, context=context)
        res = {'file': value,'product_id': id, 'filename': context.get('filename') if 'filename' in context else 'image' }
        if image_id:
            return img_obj.write(cr, uid, [image_id], res, context=context)
        else:
            image_id = img_obj.create(cr, uid, res, context=context)
            return 
    
    def get_image(self, cr, uid, id, size, context=None):
        product = self.browse(cr, uid, id, context=context)
        images_ids = self.read(cr, uid, id, ['image_website_ids'], context=context)['image_website_ids']
        if images_ids:
            image_website = self.pool.get('product.images.website').browse(cr, uid, images_ids[0], context=context)
        if image_website:
            if size == 'big':
                img = image_website.file_big
            elif size == 'medium':
                img = image_website.file_medium
            else:
                img = image_website.file_small
        else:
            img = product.image
        return img
    
    def _get_image_big(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each, 'big', context=context)
        return res
    
    def _get_image_medium(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each, 'medium', context=context)
        return res
    
    def _get_image_small(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each, 'small', context=context)
        return res
    
    #def _set_image(self, cr, uid, id, name, value, args, context=None):
    #    return self.write(cr, uid, [id], {'image_website': tools.image_resize_image_big(value)}, context=context)
    
    _columns = {
        'image_website_ids': fields.one2many(
                'product.images.website',
                'product_id',
                string='Product Images'),
        'image_website_main': fields.function(
            _get_main_image,fnct_inv=_set_image,
            type="binary",
            string="Main Image"),
        'image_website': fields.many2one('product.images.website','Image', required=False,
            domain="[('product_id','=',id)]"),
        'image_website_big': fields.function(_get_image_big,fnct_inv=_set_image,
            string="Big-sized image", type="binary", 
            help="Big-sized image of the product. It is automatically "\
                 "resized as a 800x600px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_website_medium': fields.function(_get_image_medium,fnct_inv=_set_image,
            string="Medium-sized image", type="binary", 
            help="Medium-sized image of the product. It is automatically "\
                 "resized as a 600x450px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_website_small': fields.function(_get_image_small, fnct_inv=_set_image,
            string="Small-sized image", type="binary",     
            help="Small-sized image of the category. It is automatically "\
                 "resized as a 100x75px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
    }

    def create_image_from_url(self, cr, uid, id, url, image_name=None, context=None):
        (filename, header) = urllib.urlretrieve(url)
        with open(filename, 'rb') as f:
            data = f.read()
        img = base64.encodestring(data)
        filename, extension = os.path.splitext(os.path.basename(url))
        data = {'name': image_name or filename,
                'extension': extension,
                'file': img,
                'product_id': id,
                }
        new_image_id = self.pool.get('product.images.website').create(cr, uid, data, context=context)
        return True
    
        
