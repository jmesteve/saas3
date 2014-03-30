from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
    
class pos_order(osv.osv):
    _inherit = "pos.order"    
    
    def add_payment(self, cr, uid, order_id, data, context=None):
        """Create a new payment for the order"""
        if not context:
            context = {}
        statement_line_obj = self.pool.get('account.bank.statement.line')
        property_obj = self.pool.get('ir.property')
        order = self.browse(cr, uid, order_id, context=context)
        args = {
            'amount': data['amount'],
            'date': data.get('payment_date', time.strftime('%Y-%m-%d')),
            'name': order.name + ': ' + (data.get('payment_name', '') or ''),
        }

        account_def = property_obj.get(cr, uid, 'property_account_receivable', 'res.partner', context=context)
        args['account_id'] = (order.partner_id and order.partner_id.property_account_receivable \
                             and order.partner_id.property_account_receivable.id) or (account_def and account_def.id) or False
        args['partner_id'] = order.partner_id and order.partner_id.id or None

        if not args['account_id']:
            #account_id = self.pool.get('account.account').search(cr, uid, [ ('code', 'like', '430000000')], context=context)
            #args['account_id'] = account_id[0]
            if not args['partner_id']:
                msg = _('There is no receivable account defined to make payment.')
            else:
                msg = _('There is no receivable account defined to make payment for the partner: "%s" (id:%d).') % (order.partner_id.name, order.partner_id.id,)
            raise osv.except_osv(_('Configuration Error!'), msg)

        context.pop('pos_session_id', False)

        journal_id = data.get('journal', False)
        statement_id = data.get('statement_id', False)
        assert journal_id or statement_id, "No statement_id or journal_id passed to the method!"

        for statement in order.session_id.statement_ids:
            if statement.id == statement_id:
                journal_id = statement.journal_id.id
                break
            elif statement.journal_id.id == journal_id:
                statement_id = statement.id
                break

        if not statement_id:
            raise osv.except_osv(_('Error!'), _('You have to open at least one cashbox.'))

        args.update({
            'statement_id' : statement_id,
            'pos_statement_id' : order_id,
            'journal_id' : journal_id,
            'type' : 'customer',
            'ref' : order.session_id.name,
        })

        statement_line_obj.create(cr, uid, args, context=context)

        return statement_id