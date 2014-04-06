from openerp.osv import fields,osv

class control_access(osv.osv):
    _name = 'control.access'
    
    _columns = {
                'user_id': fields.integer('User Id'),
                'user_name': fields.char('User Name', size=100),
                'ip': fields.char('Ip', size=40),
                'url': fields.char('Url', size=250),
                'db': fields.char('Database', size=40),
                'type':fields.char('Type', size=5),
                'create_date': fields.datetime('Creation date', readonly=True),
                }