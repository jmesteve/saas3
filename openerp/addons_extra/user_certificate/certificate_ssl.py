from openerp.osv import fields, osv

class certificate_ssl(osv.osv):
    _name =  'certificate.ssl'
    _columns = {'name': fields.char('Name', size=20, required=True),
                'state': fields.selection([('draft','Draft'), ('active','Active'), ('disable','Disable')], 'Status', readonly=True),
                'begin_date':  fields.date('Begin Date', required=True),
                'create_date':  fields.date('Create Date', required=True),
                'end_date':  fields.date('End Date', required=True),
                'type': fields.selection([('user', 'User'), ('company', 'Company'), ('authority', 'Certificate authority')], 'Type', readonly=True),
                }
    
    def action_generate_authority_ssl(self, cr, uid, ids, *args):
        return
    
    def action_generate_company_ssl(self, cr, uid, ids, *args):
        return
    
#user_ssl()