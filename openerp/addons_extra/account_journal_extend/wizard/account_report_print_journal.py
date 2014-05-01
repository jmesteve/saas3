from openerp.osv import fields, osv

class account_print_journal(osv.osv_memory):
    _inherit = "account.print.journal"
   
    _columns = {
        'group_journal': fields.boolean("Group Journal"),
    }
    _defaults = {'group_journal':True}
  