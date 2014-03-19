from openerp.osv import fields, osv

from mako.template import Template
from mako.lookup import TemplateLookup
import os, inspect
import re

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
     
     def validateURL(self, cr, uid, ids, url):
         regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
         
         if regex.match(url) != None:
            return True
         else:
            raise osv.except_osv('Invalid URL', 'Please enter a valid URL address')
     
     def validateIP(self, cr, uid, ids, ip):
         if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip) != None:
            return True
         else:
            raise osv.except_osv('Invalid IP', 'Please enter a valid IP address')
          
     def get_virtualhost_path(self, cr, uid, context=None):
         currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
         serverDir = os.path.join(currentPath, os.pardir)
         serverDir = os.path.join(serverDir, os.pardir)
         serverDir = os.path.join(serverDir, os.pardir)
         virtualhostPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "virtualhost_path", context=context)
         virtualhostPath = os.path.join(serverDir, virtualhostPath)
         return virtualhostPath
     
     def create(self, cr, uid, values, context=None):
         virtualhostPath = self.get_virtualhost_path(cr, uid, context)
         certificatesPath = self.pool.get('environment.ssl').get_certificates_path(cr, uid, context)
         certificatesCrl = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_crl", context=context)
         certificationAuthority = self.pool.get('certificate.ssl').browse(cr, uid, values['certificateca'], context)
         certificationServer = self.pool.get('certificate.ssl').browse(cr, uid, values['certificateserver'], context)
         currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
         savedPath = os.getcwd()
         absfilePath = os.path.abspath(os.path.join(currentPath, 'templates/'))
         
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
                                            proxypass= 'http://' + values['ip'] + ":" + values['port'] + '/',\
                                            logfile= absfilePathLog,\
                                            )
         
         if not os.path.exists(virtualhostPath):
             os.makedirs(virtualhostPath)
         
         os.chdir(virtualhostPath)
         
         f = open(values['name'], 'w')
         f.write(templateRendered)
         f.close()   
        
         os.chdir(savedPath)
         
         return osv.osv.create(self, cr, uid, values, context=context)
     
     def unlink(self, cr, uid, ids, context=None):

         virtualhostPath = self.get_virtualhost_path(cr, uid, context)
         
         currentPath = os.getcwd()
         
         os.chdir(virtualhostPath)
         
         virtualhosts = super(virtualhost_ssl, self).browse(cr, uid, ids, context=context)
         for virtualhost in virtualhosts:
            try:
                os.remove(virtualhost.name)
            except OSError:
                pass
         
         os.chdir(currentPath)
         
         return osv.osv.unlink(self, cr, uid, ids, context=context)
     
     def regenerate_file(self, cr, uid, ids, context=None):
         
         return