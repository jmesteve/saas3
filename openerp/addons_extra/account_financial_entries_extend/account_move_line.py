from openerp.osv import fields, osv

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    
    def action_go_to_account(self, cr, uid, ids, context=None):
        
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_account_form')
        view_id = view_ref and view_ref[1] or False
        
        account_move_line = self.pool.get('account.move.line').browse(cr, uid, ids[0])

        ctx = dict(context)
        ctx.update({})
        
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': account_move_line.account_id.id,
            'res_model': 'account.account',
            'type': 'ir.actions.act_window',
            'context': ctx
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
