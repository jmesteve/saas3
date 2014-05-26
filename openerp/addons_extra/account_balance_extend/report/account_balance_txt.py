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
#from StringIO import StringIO
import openerp.pooler as pooler
from mako.template import Template
from mako.lookup import TemplateLookup
import os, inspect

class external_txt(render):
    def __init__(self, txt):
        render.__init__(self)
        self.txt = txt
        self.output_type='txt'

    def _render(self):
        return self.txt

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
        
        
        self.title = "Trial Balance"
        self.filename = "Trial Balance"
        data = datas
        
        ab = account_balance(cr, uid, None, context=context)
        ab.set_context(None, data, 0)
        lines = ab.lines(data['form'])
        
        currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        currentPath = os.path.join(currentPath, os.pardir)
        absfilePath = os.path.abspath(os.path.join(currentPath, 'templates/'))
        lookup = TemplateLookup(directories=[absfilePath+'/'])
        template = Template("""<%include file="balance.txt"/>""", lookup=lookup)
        
        title = self.translate(cr, uid, 'Trial Balance', context=context)
        headers1 = [self.translate(cr, uid, 'Chart of Accounts', context=context),
                    self.translate(cr, uid, 'Fiscal Year', context=context)]
        if(data['form']['filter']=='filter_date'):
            headers1.append(self.translate(cr, uid, 'Start Date', context=context))
            headers1.append(self.translate(cr, uid, 'End Date', context=context))
        else:
            headers1.append(self.translate(cr, uid, 'Start Period', context=context))
            headers1.append(self.translate(cr, uid, 'End Period', context=context))
        headers1.append(self.translate(cr, uid, 'Display Account', context=context))
        headers1.append(self.translate(cr, uid, 'Target Moves', context=context))
        
        
        data1 = [ab._get_account(data),
                 ab._get_fiscalyear(data)]
        if(data['form']['filter']=='filter_date'):
            data1.append(ab.formatLang(ab._get_start_date(data),date=True))
            data1.append(ab.formatLang(ab._get_end_date(data),date=True))
        else:
            data1.append(ab.get_start_period(data))
            data1.append(ab.get_end_period(data))
        if data['form']['display_account']=='all':
            data1.append(self.translate(cr, uid, 'All', context=context))
        elif data['form']['display_account']=='movement':
            data1.append(self.translate(cr, uid, 'With movements', context=context))
        elif data['form']['display_account']=='not_zero':
            data1.append(self.translate(cr, uid, 'With balance is not equal to 0', context=context))
        data1.append(ab._get_target_move(data))
        
        headers2 = [self.translate(cr, uid, 'Code', context=context),
                    self.translate(cr, uid, 'Account', context=context),
                    self.translate(cr, uid, 'Opening Balance', context=context),
                    self.translate(cr, uid, 'Debit', context=context),
                    self.translate(cr, uid, 'Credit', context=context),
                    self.translate(cr, uid, 'Accumulated Debit', context=context),
                    self.translate(cr, uid, 'Accumulated Credit', context=context),
                    self.translate(cr, uid, 'Balance', context=context)]
        
        templateRendered = template.render(lines=lines, title=title, headers1=headers1, data1=data1, headers2=headers2)

        #txt_string = StringIO()
        
        self.obj = external_txt(templateRendered)
        self.obj.render()
        #txt_string.close()
        return (self.obj.txt, 'txt')

report_custom('report.account_balance_extend.balance.txt')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

