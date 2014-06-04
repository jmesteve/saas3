# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 escrichov All Rights Reserved
#                       https://github.com/jmesteve
#                       <escrichov@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Product Website Image Gallery",
    "version" : "1.0",
    'author': 'escrichov',
    'website': 'https://github.com/escrichov',
    "category" : "Generic Modules",
    "depends" : ['base','product', 'product_images'],
    "description": """
This Module implements an Image Gallery for products in website.
You can add images to every product.
    """,
    "data": [
        'security/ir.model.access.csv',
        'images_sequence.xml',
        'company_view.xml',
        'views/website_templates.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
