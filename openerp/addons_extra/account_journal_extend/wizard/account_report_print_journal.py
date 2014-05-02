from openerp.osv import fields, osv
import time

class account_print_journal(osv.osv_memory):
    _inherit = "account.print.journal"
   
    _columns = {
        'group_journal': fields.boolean("Group Journal"),
    }
    
    def get_all_journals(self, cr, uid, context):        
        journal_ids = self.pool.get('account.journal').search(cr,uid,[])
        return journal_ids
    
    _defaults = {
                 'group_journal':True,
                 'journal_ids':get_all_journals,
                 'filter': 'filter_date',
                 'sort_selection': 'l.date'
                 }
    
    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = {'value': {}}
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False ,'date_to': False}
        if filter == 'filter_date':
            year = time.strftime('%Y')
            if fiscalyear_id:
                fiscalyear_name = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=context).name
                if fiscalyear_name != year:
                    res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime(fiscalyear_name + '-01-01'), 'date_to': time.strftime(fiscalyear_name + '-12-31')}
                else:
                    res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')}
            
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.special = false
                               ORDER BY p.date_start ASC, p.special ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               AND p.special = false
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
        return res
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
            
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['sort_selection'], context=context)[0])
        data['form'].update(self.read(cr, uid, ids, ['group_journal'], context=context)[0])
        data['form'].update(self.read(cr, uid, ids, ['filter'], context=context)[0])
        
        report_name = 'account.journal.period.print.extend'
        return {'type': 'ir.actions.report.xml', 'report_name': report_name, 'datas': data}