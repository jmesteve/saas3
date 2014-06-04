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
    "name" : "Attachment Set Location",
    "version" : "1.0",
    'author': 'escrichov',
    'website': 'https://github.com/escrichov',
    "category" : "Generic Modules",
    "depends" : ['base'],
    "description": """
This Module set parameter 'ir_attachment.location' of ir.config_parameter for store attachments in filestore 
instead of store in dabatase
    """,
    "data": [
        'data/data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
