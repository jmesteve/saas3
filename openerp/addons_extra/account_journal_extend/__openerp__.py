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
    'name': 'account journal extend',
    'version': '1.2',
    'author': 'ErpAndCloud',
    'category': 'Generic Modules/Accounting',    
    'description': """
        [ENG] Extend accounting reports .
    """,
    'website': 'http://www.erpandcloud.com',
    'license': 'AGPL-3',
    'images': [],
    'depends': ['account', 'account_extend', 'report_extend'],
    'data' : [
              'account_report.xml',
#              'security/account_security.xml',
#              'security/ir.model.access.csv',
              'wizard/account_report_print_journal_view.xml',
        ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
