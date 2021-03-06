# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 ErpAndCloud All Rights Reserved
#                       https://github.com/jmesteve
#                       https://github.com/escrichov
#                       <engineering@erpandcloud.com>
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
    'name': 'account financial entries extend',
    'version': '1.7',
    'author': 'ErpAndCloud',
    'category': 'Generic Modules/Accounting',    
    'description': """
        [ENG] Extend account module.
    """,
    'website': 'http://www.erpandcloud.com',
    'license': 'AGPL-3',
    'images': [],
    'depends': ['account', 'account_move_line_extend','account_payment_extension','account_extend'],
    'data' : [
              'menu_account_financial_entries_view.xml'
        ],
    'js': [
        "static/src/js/account_move_line_extend.js",
    ],
    'qweb' : [
        "static/src/xml/account_move_line_extend.xml",
    ],
    'css':[
        "static/src/css/account_move_line_extend.css"
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
