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
import base64
import urllib
import os
import glob
import openerp
from openerp import tools
from openerp.osv import fields, orm, osv
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

#TODO find a good solution in order to roll back changed done on file system
#TODO add the possibility to move from a store system to an other
# (example : moving existing image on database to file system)
#./openerp/addons_extra
#/product_images/static/src/img/

class product_images(orm.Model):
    "Products Image gallery"
    _name = "product.images.website"
    _description = __doc__

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        #addon_path = self.pool.get('res.company').get_addon_path(cr, uid, context=context)
        config = openerp.tools.config
        addon_path = config['static_http_document_root']
        for image in self.browse(cr, uid, ids, context=context):
            path = self._image_path(cr, uid, image, context=context)
            name, extension = os.path.splitext(path)
            full_path = addon_path + name + '*' + extension
            if full_path:
                for filename in glob.glob(full_path):
                    os.path.isfile(filename) and os.remove(filename)
            
        return super(product_images, self).unlink(cr, uid, ids, context=context)

    def create(self, cr, uid, vals, context=None):       
        if vals.get('filename') and not vals.get('extension'):
            vals['filename'], vals['extension'] = os.path.splitext(vals['filename'])
            vals['name'] = sequenceImage = self.pool.get('ir.sequence').get(cr, uid, 'product.images.website')

        return super(product_images, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        if vals.get('filename') and not vals.get('extension'):
            vals['filename'], vals['extension'] = os.path.splitext(vals['filename'])
        upd_ids = ids[:]
        config = openerp.tools.config
        addon_path = config['static_http_document_root']
        if vals.get('filename') or vals.get('extension'):
            images = self.browse(cr, uid, upd_ids, context=context)
            for image in images:
                old_full_path = addon_path + self._image_path(cr, uid, image, context=context)
                if not old_full_path:
                    continue
                # all the stuff below is there to manage the files on the filesystem
                if vals.get('filename') and (image.name != vals['filename']) \
                    or vals.get('extension') and (image.extension != vals['extension']):
                    super(product_images, self).write(
                        cr, uid, image.id, vals, context=context)
                    upd_ids.remove(image.id)
                    
                    new_image = self.browse(cr, uid, image.id, context=context)
                    new_full_path = addon_path + self._image_path(cr, uid, new_image, context=context)
                    if 'file' in vals and old_full_path != new_full_path:
                        # a new image have been loaded we should remove the old image
                        # TODO it's look like there is something wrong with function
                        # field in openerp indeed the preview is always added in the write :(
                        
                        old_full_path_big = addon_path + self._image_path(cr, uid, image, 'big', context=context)
                        old_full_path_medium = addon_path + self._image_path(cr, uid, image, 'medium', context=context)
                        old_full_path_small = addon_path + self._image_path(cr, uid, image, 'small', context=context)
                        if os.path.isfile(old_full_path_big):
                            os.remove(old_full_path_big)
                        if os.path.isfile(old_full_path_medium):
                            os.remove(old_full_path_medium)
                        if os.path.isfile(old_full_path_small):
                            os.remove(old_full_path_small)
                        if os.path.isfile(old_full_path):
                            os.remove(old_full_path)
                    else:
                        #we have to rename the image on the file system
                        if os.path.isfile(old_full_path):
                            os.rename(old_full_path, new_full_path)
        return super(product_images, self).write(cr, uid, upd_ids, vals, context=context)

    def _image_path(self, cr, uid, image, size=None, context=None):
        full_path = False
        local_media_repository = self.pool.get('res.company').\
             get_local_media_repository_website(cr, uid, context=context)
        config = openerp.tools.config
        #addon_path = config['static_http_document_root']     
        #addon_path = self.pool.get('res.company').get_addon_path(cr, uid, context=context)
        product =  self.pool.get('product.product').browse(cr, uid, image.product_id.id, context=context)
        if isinstance(product, list):
            product = product[0]
        if local_media_repository:
            if size == 'big':
                image_name = image.name + 'big' if image.name else ''
            elif size == 'medium':
                image_name = image.name + 'medium' if image.name else ''
            elif size == 'small':
                image_name = image.name + 'small' if image.name else ''
            else:
                image_name = image.name or ''
            full_path = os.path.join(
                local_media_repository,
                '%s' % (product.default_code or '',),
                '%s%s' % (image_name, image.extension or '')
                )
        return full_path

    def get_image(self, cr, uid, id, size=None, context=None):
        image = self.browse(cr, uid, id, context=context)
        if image.link:
            if size == 'big':
                url = image.url_big
            elif size == 'medium':
                url = image.url_big
            elif size == 'small':
                url = image.url_small
            else:
                url = image.url
            if url:
                url = ''.join([i if ord(i) < 128 else '' for i in url])
                config = openerp.tools.config
                if config['netrpc_interface'] and config['xmlrpc_port']:
                    host = 'http://'+ config['netrpc_interface']+':'+ str(config['xmlrpc_port'])
                else:
                    return False
                url = host + url
                (filename, header) = urllib.urlretrieve(url)
                with open(filename, 'rb') as f:
                    img = base64.b64encode(f.read())
            else:
                return False
        else:
            try:
                product =  self.pool.get('product.product').browse(cr, uid, image.product_id.id, context=context)
                if isinstance(product, list):
                    product = product[0]
                if isinstance(product.default_code, bool):
                    _logger.debug('product not completely setup, no image available')
                    full_path = False
                else:
                    config = openerp.tools.config
                    addon_path = config['static_http_document_root']
                    if size == 'big':
                        full_path = addon_path + self._image_path(cr, uid, image, 'big', context=context)
                    elif size == 'medium':
                        full_path = addon_path + self._image_path(cr, uid, image, 'medium', context=context)
                    elif size == 'small':
                        full_path = addon_path + self._image_path(cr, uid, image, 'small', context=context)
                    else:
                        full_path = addon_path + self._image_path(cr, uid, image, context=context)
            except Exception, e:
                _logger.error("Can not find the path for image %s: %s", id, e, exc_info=True)
                return False
            if full_path:
                if os.path.exists(full_path):
                    try:
                        with open(full_path, 'rb') as f:
                            img = base64.b64encode(f.read())
                    except Exception, e:
                        _logger.error("Can not open the image %s, error : %s",
                                      full_path, e, exc_info=True)
                        return False
                else:
                    _logger.error("The image %s doesn't exist ", full_path)
                    return False
            else:
                img = image.file_db_store
        return img

    def _get_image(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each, context=context)
        return res
    
    def _get_image_big(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each, 'big', context=context)
        return res

    def _get_image_medium(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each, 'medium',context=context)
        return res
    
    def _get_image_small(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each, 'small', context=context)
        return res

    def _check_filestore(self, image_filestore):
        """check if the filestore is created, if not it create it
        automatically
        """
        try:
            dir_path = os.path.dirname(image_filestore)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, 0777)
        except OSError, e:
            raise osv.except_osv(
                    _('Error'),
                    _('The image filestore can not be created, %s') % e)
        return True

    def _save_file(self, path, b64_file):
        """Save a file encoded in base 64"""
        self._check_filestore(path)
        name, extention = os.path.splitext(path)
        with open(path, 'w') as ofile:
            #resize = tools.image_resize_image_medium(b64_file,size=(200, 150))
            ofile.write(base64.b64decode(b64_file))
            
        path_small = name + 'small' + extention 
        with open(path_small, 'w') as ofile:
            resize_small = tools.image_resize_image_small(b64_file,size=(100, 75))
            ofile.write(base64.b64decode(resize_small))
        path_medium = name + 'medium' + extention 
        with open(path_medium, 'w') as ofile:
            resize_medium = tools.image_resize_image_medium(b64_file,size=(600, 450))
            ofile.write(base64.b64decode(resize_medium))
        path_big = name + 'big' + extention 
        with open(path_big, 'w') as ofile:
            resize_big = tools.image_resize_image_big(b64_file,size=(800, 600))
            ofile.write(base64.b64decode(resize_big))
        return True
        

    def _set_image(self, cr, uid, id, name, value, arg, context=None):
        image = self.browse(cr, uid, id, context=context)
        full_path = self._image_path(cr, uid, image, context=context)
        if full_path:
            #addon_path = self.pool.get('res.company').get_addon_path(cr, uid, context=context)
            config = openerp.tools.config
            addon_path = config['static_http_document_root']
            path = addon_path + full_path
            if self._save_file(path, value):
                #config = openerp.tools.config
                #host = 'http://'+ config['db_host']+':'+ str(config['xmlrpc_port'])
                #url = host + full_path
                #name, extention = os.path.splitext(url)
                url = full_path
                name, extention = os.path.splitext(url)
                url_big = name + 'big' + extention 
                url_medium = name + 'medium' + extention 
                url_small = name + 'small' + extention 
                return self.write(cr, uid, id, {'url':url,'url_big':url_big,'url_medium':url_medium,'url_small':url_small}, context=context)
            else:
                return False
        
        return self.write(cr, uid, id, {'file_db_store': value}, context=context)

    _columns = {
        'name': fields.char('Image Title', size=64),
        'filename': fields.char('Filename', size=64),
        'extension': fields.char('file extension', oldname='extention'),
        'link': fields.boolean('Link?',
                               help="Images can be linked from files on "
                                    "your file system or remote (Preferred)"),
        'file_db_store': fields.binary('Image stored in database'),
        'file': fields.function(_get_image,
                                fnct_inv=_set_image,
                                type="binary",
                                string="File",
                                filters='*.png,*.jpg,*.gif'),
        'file_big': fields.function(_get_image_big,
                                fnct_inv=_set_image,
                                type="binary",
                                string="File Big",
                                filters='*.png,*.jpg,*.gif'),
        'file_medium': fields.function(_get_image_medium,
                                fnct_inv=_set_image,
                                type="binary",
                                string="File Medium",
                                filters='*.png,*.jpg,*.gif'),
        'file_small': fields.function(_get_image_small,
                                fnct_inv=_set_image,
                                type="binary",
                                string="File Small",
                                filters='*.png,*.jpg,*.gif'),
        'url': fields.char('File Location'),
        'url_big': fields.char('File Location Image Size Big'),
        'url_medium': fields.char('File Location Image Size Medium'),
        'url_small': fields.char('File Location Image Size Small'),
        'comments': fields.text('Comments'),
        'product_id': fields.many2one('product.template', 'Product')
        }

    _defaults = {
        'link': False,
        }

    _sql_constraints = [('uniq_name_product_id',
                         'UNIQUE(product_id, name)',
                         _('A product can have only one '
                           'image with the same name'))]
