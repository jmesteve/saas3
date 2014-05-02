from openerp.osv import fields, osv

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
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
            
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['sort_selection'], context=context)[0])
        data['form'].update(self.read(cr, uid, ids, ['group_journal'], context=context)[0])
        
        report_name = 'account.journal.period.print.extend'
        return {'type': 'ir.actions.report.xml', 'report_name': report_name, 'datas': data}