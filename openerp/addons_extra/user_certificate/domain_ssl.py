from openerp.osv import fields, osv

class domain_ssl(osv.osv):
     _name =  'domain.ssl'
     _columns = {
                 'name': fields.char('Name', size=64, required=True),
                 'certificate_id': fields.many2one('certificate.ssl', 'Certificate', readonly=True)
                 }