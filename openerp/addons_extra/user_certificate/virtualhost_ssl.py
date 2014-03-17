from openerp.osv import fields, osv

from mako.template import Template
from mako.lookup import TemplateLookup
import os

class virtualhost_ssl(osv.osv):
     _name =  'virtualhost.ssl'
     _columns = {
                 'name': fields.char('Name', size=64, required=True),
                 'certificateca': fields.many2one('certificate.ssl', 'Certificate CA', readonly=False, required=True),
                 'certificateserver': fields.many2one('certificate.ssl', 'Certificate Server', required=True),
                 'servername': fields.char('Server Name', size=64, required=True),
                 'serveralias': fields.char('Server Alias', size=64, required=True),
                 'ip': fields.char('IP', size=15, required=True),
                 'port': fields.char('Port', size=5, required=True),
                 'logpath': fields.char('Log Path', size=64, required=True)
                 }
     
     _defaults = {
                  'logpath': lambda self, cr, uid, context: self.pool.get('ir.config_parameter').get_param(cr, uid, "log_path", context),
                  'port': lambda self, cr, uid, context: self.pool.get('ir.config_parameter').get_param(cr, uid, "virtualhost_port", context)
     }
     _sql_constraints = [('item_name_unique','unique(name)', 'Item Name must be unique!')]
     
     def create(self, cr, uid, values, context=None):
         virtualhostPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "virtualhost_path", context=context)
         certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
         certificatesCrl = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_crl", context=context)
         certificationAuthority = self.pool.get('certificate.ssl').browse(cr, uid, values['certificateca'], context)
         certificationServer = self.pool.get('certificate.ssl').browse(cr, uid, values['certificateserver'], context)
         absfilePath = os.path.abspath('openerp/addons_extra/user_certificate/templates/')
         currentPath = os.getcwd()
         
         absfilePathCA = os.path.abspath(os.path.join(certificatesPath, "certs", certificationAuthority.name_file + ".cert.pem"))
         absfilePathCRL = os.path.abspath(os.path.join(certificatesPath, "crl", certificatesCrl + ".pem"))
         absfilePathCertificateServer = os.path.abspath(os.path.join(certificatesPath, "certs", certificationServer.name_file + ".cert.pem"))
         absfilePathKeyServer = os.path.abspath(os.path.join(certificatesPath, "private", certificationServer.name_file + ".key.pem"))
         absfilePathLog = os.path.abspath(os.path.join(values['logpath'], values['name'] + ".log"))
         
         lookup = TemplateLookup(directories=[absfilePath])
         template = Template("""<%include file="virtualhost.txt"/>""", lookup=lookup)
         templateRendered = template.render(servername=values['servername'], \
                                            serveralias=values['serveralias'], \
                                            certificateca=absfilePathCA,\
                                            revocationfile=absfilePathCRL, \
                                            certificateserver=absfilePathCertificateServer, \
                                            keyserver=absfilePathKeyServer,\
                                            proxypass= "http://" + values['ip'] + ":" + values['port'],\
                                            logfile= absfilePathLog,\
                                            )
         
         if not os.path.exists(virtualhostPath):
             os.makedirs(virtualhostPath)
         
         os.chdir(virtualhostPath)
         
         f = open(values['name'], 'w')
         f.write(templateRendered)
         f.close()   
        
         os.chdir(currentPath)
         
         return osv.osv.create(self, cr, uid, values, context=context)
     
     def unlink(self, cr, uid, ids, context=None):
         virtualhostPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "virtualhost_path", context=context)
         currentPath = os.getcwd()
         
         os.chdir(virtualhostPath)
         
         virtualhosts = super(virtualhost_ssl, self).browse(cr, uid, ids, context=context)
         for virtualhost in virtualhosts:
             os.remove(virtualhost.name)
         
         os.chdir(currentPath)
         
         return osv.osv.unlink(self, cr, uid, ids, context=context)
     
     def regenerate_file(self, cr, uid, ids, context=None):
         
         return