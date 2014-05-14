# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.report.render import render
from openerp.report.interface import report_int
from openerp.addons.account_balance_extend.report.account_balance import account_balance
import xlwt
from StringIO import StringIO
import openerp.pooler as pooler

class external_xls(render):
    def __init__(self, xls):
        render.__init__(self)
        self.xls = xls
        self.output_type='xls'

    def _render(self):
        return self.xls

class report_custom(report_int):

    def translate(self, cr, uid, text, context=None):
        lang = context['lang']
        if lang and text and not text.isspace():
            transl_obj = pooler.get_pool(cr.dbname).get('ir.translation')
            if len(text):
                translated_string = transl_obj._get_source(cr, uid, None, ('report'), lang, text)
                return translated_string
        return text

    def create(self, cr, uid, ids, datas, context=None):
        
        data = datas
        ab = account_balance(cr, uid, None, context=context)
        ab.set_context(None, data, 0)
        lines = ab.lines(data['form'])
        style0 = xlwt.easyxf('font: name Times New Roman, bold on; align: wrap on, vert centre, horiz center')
        style0.font.height = 500
        style1 = xlwt.easyxf('font: name Times New Roman, bold on; align: wrap on, vert centre, horiz center')
        style1.font.height = 300
        style2 = xlwt.easyxf('font: name Times New Roman; align: wrap on, vert centre, horiz center')
        style2.font.height = 200
        wb = xlwt.Workbook()
        ws = wb.add_sheet(self.translate(cr, uid, 'Trial Balance', context=context),cell_overwrite_ok=True)
        ws.col(0).width = 0x0d00 + 5000
        ws.col(1).width = 0x0d00 + 5000
        ws.col(2).width = 0x0d00 + 1000
        ws.col(3).width = 0x0d00 + 1000
        ws.col(4).width = 0x0d00 + 1000
        ws.col(5).width = 0x0d00 + 1000
        ws.col(6).width = 0x0d00 + 1000
        ws.col(7).width = 0x0d00 + 1000
        
        ws.write(0, 0, self.translate(cr, uid, 'Trial Balance', context=context), style0)
        
        
        ws.write(1, 1, self.translate(cr, uid, 'Chart of Accounts', context=context), style1)
        ws.write(1, 2, self.translate(cr, uid, 'Fiscal Year', context=context), style1)
        if(data['form']['filter']=='filter_date'):
            ws.write(1, 3, self.translate(cr, uid, 'Start Date', context=context), style1)
            ws.write(1, 4, self.translate(cr, uid, 'End Date', context=context), style1)
        else:
            ws.write(1, 3, self.translate(cr, uid, 'Start Period', context=context), style1)
            ws.write(1, 4, self.translate(cr, uid, 'End Period', context=context), style1)
        ws.write(1, 5, self.translate(cr, uid, 'Display Account', context=context), style1)
        ws.write(1, 6, self.translate(cr, uid, 'Target Moves', context=context), style1)
        
        
        ws.write(2, 1, ab._get_account(data), style2)
        ws.write(2, 2, ab._get_fiscalyear(data), style2)
        if(data['form']['filter']=='filter_date'):
             ws.write(2, 3, ab.formatLang(ab._get_start_date(data),date=True), style2)
             ws.write(2, 4, ab.formatLang(ab._get_end_date(data),date=True), style2)
        else:
             ws.write(2, 3, ab.formatLang(ab.get_start_period(data),date=True), style2)
             ws.write(2, 4, ab.formatLang(ab.get_end_period(data),date=True), style2)
        if data['form']['display_account']=='all':
            ws.write(2, 5, self.translate(cr, uid, 'All', context=context), style2)
        elif data['form']['display_account']=='movement':
            ws.write(2, 5, self.translate(cr, uid, 'With movements', context=context), style2)
        elif data['form']['display_account']=='not_zero':
            ws.write(2, 5, self.translate(cr, uid, 'With balance is not equal to 0', context=context), style2)
        ws.write(2, 6, ab._get_target_move(data), style2)

        
        row = 5
        
        ws.write(row, 0, self.translate(cr, uid, 'Code', context=context), style1)
        ws.write(row, 1, self.translate(cr, uid, 'Account', context=context), style1)
        ws.write(row, 2, self.translate(cr, uid, 'Opening Balance', context=context), style1)
        ws.write(row, 3, self.translate(cr, uid, 'Debit', context=context), style1)
        ws.write(row, 4, self.translate(cr, uid, 'Credit', context=context), style1)
        ws.write(row, 5, self.translate(cr, uid, 'Accumulated Debit', context=context), style1)
        ws.write(row, 6, self.translate(cr, uid, 'Accumulated Credit', context=context), style1)
        ws.write(row, 7, self.translate(cr, uid, 'Balance', context=context), style1)
        
        row += 1
        style = xlwt.XFStyle()
        style.num_format_str = '0.00'
        for line in lines:
            ws.write(row, 0, line['code'])
            ws.write(row, 1, line['name'])
            ws.write(row, 2, line['opening_balance'], style)
            ws.write(row, 3, line['debit'], style)
            ws.write(row, 4, line['credit'], style)
            ws.write(row, 5, line['accumulated_debit'], style)
            ws.write(row, 6, line['accumulated_credit'], style)
            ws.write(row, 7, line['final_balance'], style)
            row += 1
            
        #wb.save('../example.xls')
        xls_string = StringIO()
        wb.save(xls_string)
        self.obj = external_xls(xls_string.getvalue())
        self.obj.render()
        xls_string.close()
        return (self.obj.xls, 'xls')

report_custom('report.account_balance_extend.balance.xls')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

