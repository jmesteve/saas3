from openerp.osv import osv

from openerp.tools.translate import _

class account_state_open(osv.osv_memory):
    _inherit = 'account.state.open'

    def change_inv_state(self, cr, uid, ids, context=None):
        obj_invoice = self.pool.get('account.invoice')
        if context is None:
            context = {}
        if 'active_ids' in context:
            data_inv = obj_invoice.browse(cr, uid, context['active_ids'][0], context=context)
            if data_inv.reconciled:
                raise osv.except_osv(_('Warning!'), _('Invoice is already reconciled.'))
            #obj_invoice.signal_open_test(cr, uid, context['active_ids'][0])
            obj_invoice.signal_open_test(cr, uid, context['active_ids'])
        return {'type': 'ir.actions.act_window_close'}
