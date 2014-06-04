# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 jmesteve All Rights Reserved
#                       https://github.com/jmesteve
#                       <jmesteve@me.com>
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
    "name" : "Product Image Gallery",
    "version" : "1.0",
    'author': 'jmesteve',
    'website': 'https://github.com/jmesteve',
    "category" : "Generic Modules",
    "depends" : ['base','product', 'website'],
    "description": """
This Module implements an Image Gallery for products.
You can add images to every product.
    """,
    "data": [
        'security/ir.model.access.csv',
        'product_images_view.xml',
        'images_sequence.xml',
        'company_view.xml',
        'product_view.xml',
    ],
    'installable': True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
