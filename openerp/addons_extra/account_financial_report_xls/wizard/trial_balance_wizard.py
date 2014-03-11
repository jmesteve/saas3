# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
#from openerp.addons.account.report.trial_balance import TrialBalanceWebkit
import xlwt
#import logging
#_logger = logging.getLogger(__name__)

class account_balance_report(orm.TransientModel):
    _inherit = 'account.balance.report'
       
    def xls_export(self, cr, uid, ids, context=None):
        from datetime import datetime
        style0 = xlwt.easyxf('font: name Times New Roman, colour red, bold on')
        style1 = xlwt.easyxf('',num_format_str='DD-MMM-YY')
        wb = xlwt.Workbook()
        ws = wb.add_sheet('A Test Sheet',cell_overwrite_ok=True)
        ws.write(0, 0, 'Test', style0)
        ws.write(1, 0, datetime.now(), style1)
        ws.write(2, 0, 4)
        ws.write(2, 1, 1)
        ws.write(2, 2, xlwt.Formula("A3+B3"))
        wb.save('../example.xls')

        
        
  