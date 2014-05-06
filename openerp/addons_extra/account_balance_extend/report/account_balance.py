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

import time

from openerp.report import report_sxw as report_sxw_extend
from openerp.addons.report_extend.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header

class account_balance(report_sxw_extend.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(account_balance, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(account_balance, self).set_context(objects, data, new_ids, report_type=report_type)

    #def _add_header(self, node, header=1):
    #    if header == 0:
    #        self.rml_header = ""
    #    return True

    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_balance ,self)._get_account(data)

    def _get_opening_balance(self, form, account_ids):
        
        if(form['filter'] == 'filter_period'):
            self.cr.execute("""SELECT a.id, a.code, a.parent_id, a.name, SUM(l.debit), SUM(l.credit), SUM(l.debit) - SUM(l.credit), a.type, a.level
            FROM account_move_line l 
            JOIN account_account a ON a.id=l.account_id 
            JOIN account_journal aj ON aj.id=l.journal_id 
            JOIN account_move am ON am.id=l.move_id 
            WHERE l.account_id IN %s AND aj.type like 'situation' AND am.state=%s AND l.period_id IN %s 
            GROUP BY a.id ORDER BY a.code""", (tuple(account_ids), form['target_move'], tuple(form['period_from'], form['period_to']),))
            
        elif(form['filter'] == 'filter_date'):
            self.cr.execute("""SELECT a.id, a.code, a.parent_id, a.name, SUM(l.debit), SUM(l.credit), SUM(l.debit) - SUM(l.credit), a.type, a.level
            FROM account_move_line l 
            JOIN account_account a ON a.id=l.account_id 
            JOIN account_journal aj ON aj.id=l.journal_id 
            JOIN account_move am ON am.id=l.move_id 
            WHERE l.account_id IN %s AND aj.type like 'situation' AND am.state=%s AND l.date >= %s AND l.date <= %s 
            GROUP BY a.id ORDER BY a.code""", (tuple(account_ids),  form['target_move'], form['date_from'], form['date_to']))
        else:
            self.cr.execute("""SELECT a.id, a.code, a.parent_id, a.name, SUM(l.debit), SUM(l.credit), SUM(l.debit) - SUM(l.credit), a.type, a.level
            FROM account_move_line l 
            JOIN account_account a ON a.id=l.account_id 
            JOIN account_journal aj ON aj.id=l.journal_id 
            JOIN account_move am ON am.id=l.move_id 
            WHERE l.account_id IN %s AND aj.type like 'situation' AND am.state=%s 
            GROUP BY a.id ORDER BY a.code""", (tuple(account_ids),  form['target_move'],))
        
        res = self.cr.fetchall()
        
        return res
    
    def _get_lines(self, form, account_ids):
        
        if(form['filter'] == 'filter_period'):
            self.cr.execute("""SELECT a.id, a.code, a.parent_id, a.name, SUM(l.debit), SUM(l.credit), a.type, a.level
            FROM account_move_line l 
            JOIN account_account a ON a.id=l.account_id  
            JOIN account_move am ON am.id=l.move_id 
            WHERE l.account_id IN %s AND am.state=%s AND l.period_id IN %s AND l.journal_id IN %s
            GROUP BY a.id ORDER BY a.code""", (tuple(account_ids), form['target_move'], tuple(form['period_to'], form['period_from']), tuple(form['journal_ids'])))
            
        elif(form['filter'] == 'filter_date'):
            self.cr.execute("""SELECT a.id, a.code, a.parent_id, a.name, SUM(l.debit), SUM(l.credit), a.type, a.level
            FROM account_move_line l 
            JOIN account_account a ON a.id=l.account_id 
            JOIN account_move am ON am.id=l.move_id 
            WHERE l.account_id IN %s AND am.state=%s AND l.date >= %s AND l.date <= %s AND l.journal_id IN %s
            GROUP BY a.id ORDER BY a.code""", (tuple(account_ids),  form['target_move'], form['date_from'], form['date_to'], tuple(form['journal_ids'])))
        else:
            self.cr.execute("""SELECT a.id, a.code, a.parent_id, a.name, SUM(l.debit), SUM(l.credit), a.type, a.level
            FROM account_move_line l 
            JOIN account_account a ON a.id=l.account_id 
            JOIN account_move am ON am.id=l.move_id 
            WHERE l.account_id IN %s AND am.state=%s AND l.journal_id IN %s
            GROUP BY a.id ORDER BY a.code""", (tuple(account_ids),  form['target_move'], tuple(form['journal_ids'])))
        
        res = self.cr.fetchall()
        
        return res
    
    def _get_accounts(self, form, account_ids):
                
        self.cr.execute("""SELECT a.id, a.code, a.parent_id, a.name, a.type, a.level
        FROM account_account a 
        WHERE a.id IN %s
        ORDER BY a.code""", (tuple(account_ids),))
        
        res = self.cr.fetchall()
        
        return res
    
    
    def lines(self, form, ids=None):
        
        if not ids:
            ids = self.ids
        if not ids:
            return []
        
        obj_account = self.pool.get('account.account')
        
        ctx = self.context.copy()

        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        
        opening_balance = self._get_opening_balance(form, ids)
        lines = self._get_lines(form, ids)
        accounts = self._get_accounts(form, ids)
        
        # Get max level
        max_level = 0
        for line in lines:
            if(line[7] > max_level):
                max_level = line[7]
        
        # Create a dictionary from list of accounts.
        # The key of the dicctionary is the id of the account
        accounts_dictionary = {}
        for account in accounts:
            account_dict = {'id': account[0], 'code': account[1], 'parent_id': account[2], 'name': account[3], 'opening_balance': 0,
                            'type': account[4], 'level': account[5], 'debit': 0, 'credit': 0, 'accumulated_debit': 0, 'accumulated_credit':0, 'final_balance':0}
            accounts_dictionary[account[0]] = account_dict
        
        ## Combine opening balance with other lines
        result_lines = []
        i = 0
        j = 0
        while (i < len(lines) and j < len(opening_balance)):
            
            line = {}
            
            # Compare codes
            if(lines[i][1] == opening_balance[j][1]):
                line['id'] = lines[i][0]
                line['code'] = lines[i][1]
                line['parent_id'] = lines[i][2]
                line['name'] = lines[i][3]
                line['debit'] = lines[i][4]
                line['credit'] = lines[i][5]
                line['opening_balance'] = opening_balance[j][6]
                line['accumulated_debit'] = opening_balance[j][4] + lines[i][4]
                line['accumulated_credit'] = opening_balance[j][5] + lines[i][5]
                line['final_balance'] = line['accumulated_debit'] - line['accumulated_credit']
                line['type'] = lines[i][6]
                line['level'] = lines[i][7]
                i+=1
                j+=1
            elif(int(lines[i][1]) < int(opening_balance[j][1])):
                line['id'] = lines[i][0]
                line['code'] = lines[i][1]
                line['parent_id'] = lines[i][2]
                line['name'] = lines[i][3]
                line['debit'] = lines[i][4]
                line['credit'] = lines[i][5]
                line['opening_balance'] = 0
                line['accumulated_debit'] = lines[i][4]
                line['accumulated_credit'] = lines[i][5]
                line['final_balance'] = line['accumulated_debit'] - line['accumulated_credit']
                line['type'] = lines[i][6]
                line['level'] = lines[i][7]
                i+=1
            else:
                line['id'] = opening_balance[j][0]
                line['code'] = opening_balance[j][1]
                line['parent_id'] = opening_balance[j][2]
                line['name'] = opening_balance[j][3]
                line['debit'] = 0
                line['credit'] = 0
                line['opening_balance'] = opening_balance[j][6]
                line['accumulated_debit'] = opening_balance[j][4]
                line['accumulated_credit'] = opening_balance[j][5]
                line['final_balance'] = line['accumulated_debit'] - line['accumulated_credit']
                line['type'] = opening_balance[j][7]
                line['level'] = opening_balance[j][8]
                j+=1
                
            result_lines.append(line)
        
        while (i < len(lines)):
            
            line = {}
            
            line['id'] = lines[i][0]
            line['code'] = lines[i][1]
            line['parent_id'] = lines[i][2]
            line['name'] = lines[i][3]
            line['debit'] = lines[i][4]
            line['credit'] = lines[i][5]
            line['opening_balance'] = 0
            line['accumulated_debit'] = lines[i][4]
            line['accumulated_credit'] = lines[i][5]
            line['final_balance'] = line['accumulated_debit'] - line['accumulated_credit']
            line['type'] = lines[i][6]
            line['level'] = lines[i][7]
            i+=1
            
            result_lines.append(line)
            
        while (j < len(opening_balance)):
            
            line = {}
            
            line['id'] = opening_balance[j][0]
            line['code'] = opening_balance[j][1]
            line['parent_id'] = opening_balance[j][2]
            line['name'] = opening_balance[j][3]
            line['debit'] = 0
            line['credit'] = 0
            line['opening_balance'] = opening_balance[j][6]
            line['accumulated_debit'] = opening_balance[j][4]
            line['accumulated_credit'] = opening_balance[j][5]
            line['final_balance'] = line['accumulated_debit'] - line['accumulated_credit']
            line['type'] = opening_balance[j][7]
            line['level'] = opening_balance[j][8]
            j+=1
            
            result_lines.append(line)
            
        for line in result_lines:
            accounts_dictionary[line['id']]['debit'] = line['debit'] 
            accounts_dictionary[line['id']]['credit'] = line['credit']
            accounts_dictionary[line['id']]['opening_balance'] = line['opening_balance']
            accounts_dictionary[line['id']]['accumulated_debit'] = line['accumulated_debit']
            accounts_dictionary[line['id']]['accumulated_credit'] = line['accumulated_credit']
            accounts_dictionary[line['id']]['final_balance'] = line['final_balance']
        
        for level in xrange(max_level+1, 0, -1):
            for key, account in accounts_dictionary.iteritems():
                if(account['level'] == level):
                     parent_id = account['parent_id']
                     accounts_dictionary[parent_id]['opening_balance'] += account['opening_balance']
                     accounts_dictionary[parent_id]['debit'] += account['debit'] 
                     accounts_dictionary[parent_id]['credit'] += account['credit']
                     accounts_dictionary[parent_id]['accumulated_debit'] += account['accumulated_debit']
                     accounts_dictionary[parent_id]['accumulated_credit'] += account['accumulated_credit']
                     accounts_dictionary[parent_id]['final_balance'] += account['final_balance']
        
        result = []
        for account in accounts_dictionary.values():
            result.append(account)
        
        return result

report_sxw.report_sxw('report.account_balance_extend.account.balance', 'account.account', 'addons_extra/account_balance_extend/report/account_balance.rml', parser=account_balance, header="internal")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
