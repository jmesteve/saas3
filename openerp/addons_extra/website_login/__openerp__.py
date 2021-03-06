# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 jmesteve All Rights Reserved
#                       https://github.com/jmesteve
#                       https://github.com/escrichov
#                       <jmesteve@me.com>
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
    'name': "Website Login",
    'version': '0.35',
    'category': 'Hidden',
    'description': """
        [ENG] Change addon Website Login 
    """,
    'author': 'escrichov,jmesteve',
    'website': 'http://www.erpandcloud.com',
    'license': 'AGPL-3',
    "depends": ['base', 'web','website', 'stock', 'auth_signup', 'website_sale', 'payment_paypal', 'payment_ogone', 'payment_adyen', 'product'],
    'data': ['security/ir.model.access.csv',
             'views/shop_redirect_view.xml',
             'views/website_templates.xml',
             'views/website_sale.xml',
             'data/website_login_data.xml'
    ],
    "application": True,
    "active": True,
    "installable": True,
    'auto_install': False,
}
