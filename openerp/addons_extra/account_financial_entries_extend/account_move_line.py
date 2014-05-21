from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    
#     def action_go_to_account(self, cr, uid, ids, context=None):
#         
#         view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_account_form')
#         view_id = view_ref and view_ref[1] or False
#         
#         account_move_line = self.pool.get('account.move.line').browse(cr, uid, ids[0])
# 
#         ctx = dict(context)
#         ctx.update({})
#         
#         
#         return {
#             'view_type': 'form',
#             'view_mode': 'form',
#             'view_id': view_id,
#             'res_id': account_move_line.account_id.id,
#             'res_model': 'account.account',
#             'type': 'ir.actions.act_window',
#             'context': ctx
#          }

    def _check_company_id(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        for l in lines:
            if l.account_id.company_id != l.period_id.company_id:
                return False
        return True
    
    _constraints = [
        (_check_company_id, 'Account and Period must belong to the same company.', ['company_id']),
    ]

    def action_filter(self, cr, uid, ids, context=None):
         
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, 
                                                                       uid, 
                                                                       'account_financial_entries_extend', 
                                                                       'view_move_line_tree_extend_financial_no_editable')
        view_id = view_ref and view_ref[1] or False
         
        account_move_line = self.pool.get('account.move.line').browse(cr, uid, ids[0])
        
        ctx = dict(context)
        ctx.update({'account_id': account_move_line.account_id.id})
        if 'period_id' not in ctx:
            ctx.update({'no_period_id': True})
         
        return {
            'view_type': 'form',
            'view_id': view_id,
            'view_mode': 'tree_account_move_line_quickadd_extend,form',
            'views': [(view_id,'tree_account_move_line_quickadd_extend'),(False,'form')],
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'name': account_move_line.account_id.code,
         }

    
    def action_go_to_account_move(self, cr, uid, ids, context=None):
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_move_form')
        view_id = view_ref and view_ref[1] or False
        
        account_move_line = self.pool.get('account.move.line').browse(cr, uid, ids[0])

        ctx = dict(context)
        ctx.update({})
        
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': account_move_line.move_id.id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': ctx
         }
        
    def action_go_to_invoice(self, cr, uid, ids, context=None):
        
        account_move = self.pool.get('account.move.line').browse(cr, uid, ids[0])
        
        if account_move.invoice.type == "in_invoice":
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
            view_id = view_ref and view_ref[1] or False                          
        else:
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')
            view_id = view_ref and view_ref[1] or False
        
        

        ctx = dict(context)
        ctx.update({})
        
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': account_move.invoice.id,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'context': ctx
         }
