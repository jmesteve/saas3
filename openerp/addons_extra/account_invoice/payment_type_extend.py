from openerp.osv import fields, osv

class payment_type(osv.osv):
    _inherit = 'payment.type'
    
    _columns = {
                'account': fields.many2one('res.partner.bank', string='Bank Account', required=False),
                'has_account': fields.boolean('Has Account'),
    }
    
    def _default_company_account(self, cr, uid, context):
        company_obj = self.pool.get('res_company')
        user = self.pool.get('res.users').browse(cr, uid, [uid], context=context)[0]
        accounts = user.company_id.bank_ids
        
        account_result = None
        if len(accounts) > 0:
            account_result = accounts[0].id
        for account in accounts:
            if account.default_bank:
                account_result = account.id
        
        return account_result
    
    _defaults = {
                 'has_account': False,
                 'account':  _default_company_account
                 }