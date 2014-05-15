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

    def action_filter(self, cr, uid, ids, context=None):
         
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, 
                                                                       uid, 
                                                                       'account_financial_entries_extend', 
                                                                       'view_move_line_tree_extend_financial_no_editable')
        view_id = view_ref and view_ref[1] or False
         
        account_move_line = self.pool.get('account.move.line').browse(cr, uid, ids[0])
 
        ctx = dict(context)
        ctx.update({'account_id': account_move_line.account_id.id})
         
         
        return {
            'view_type': 'form',
            'view_mode': 'tree_account_move_line_quickadd',
            'view_id': view_id,
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
