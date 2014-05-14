from openerp.osv import fields, osv

class trial_balance_level(osv.osv):
    _name = 'account.balance.report.extend.level'
    _columns = {
                'digit': fields.char('Digit', required=True, readonly=True),
                'value': fields.integer('Value', required=True, readonly=True),
    }