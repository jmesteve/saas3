from openerp.osv import fields,osv

class control_access(osv.osv):
    _name = 'control.access'
    
    _columns = {
                'user_id': fields.integer('User Id'),
                'user_name': fields.char('User Name', size=100),
                'session': fields.char('Session', size=64, readonly=True),
                'ip': fields.char('Ip', size=40),
                'url': fields.char('Url', size=250),
                'db': fields.char('Database', size=40),
                'type': fields.char('Type', size=5),
                'create_date': fields.datetime('Creation date', readonly=True)
                }
    _order = 'create_date desc'
    
    def button_form(self, cr, uid, ids, context=None):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_id': ids[0],
            'res_model': 'control.access',
            'type': 'ir.actions.act_window',
            'context': context,
            'target':'new',
            'nodestroy': True,
         }
       