from openerp.osv import fields, osv
import uuid

class res_users(osv.osv):
    _inherit =  'res.users'
    
    _columns = { 'certificates': fields.one2many('certificate.ssl','user', string='Certificates SSL', required=False)}
    def action_generate_ssl(self, cr, uid, ids, context, *args):
        certificatesPool = self.pool.get('certificate.ssl')
        view_id = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','certificate.ssl'),\
                                        ('name','=','user.ssl.form.user')])
        
        id = context.get('id')
        
        user = self.pool.get('res.users').browse(cr, uid, id)
        authority_id = self.pool.get('certificate.ssl').search(cr, uid, [('type', 'ilike', 'authority_root'), ('state', 'ilike', 'active')], context=context)
        if isinstance(authority_id, list) and len(authority_id) > 0:
            authority_id = authority_id[0]
        context.update({'user': user.id, 'name': user.name, 'certification_authority':  authority_id})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'certificate.ssl',
            'type': 'ir.actions.act_window',
            'context': context
         }
#user_ssl()