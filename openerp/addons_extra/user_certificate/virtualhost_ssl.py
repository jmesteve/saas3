from openerp.osv import fields, osv

from mako.template import Template
from mako.lookup import TemplateLookup
import os, inspect
import re
import subprocess
import unicodedata
import socket

class virtualhost_ssl(osv.osv):
     _name =  'virtualhost.ssl'
     
     _columns = {
                 'name': fields.char('Name', size=64, required=True),
                 'certificateserver': fields.many2one('certificate.ssl', 'Certificate Server', required=True),
                 'servername': fields.char('Server Name', size=64, required=True),
                 'serveralias': fields.char('Server Alias', size=64, required=True),
                 'ip': fields.char('IP', size=16, required=True),
                 'port': fields.char('Port', size=5, required=True),
                 'logpath': fields.char('Log Path', size=64, required=True),
                 'state': fields.selection([('draft','Draft'), ('active','Active'), ('disable','Disable')], 'State', readonly=True, help="The state.", select=True),
                 }
     
     def get_ip(self, cr, uid, context=None):
         return socket.gethostbyname(socket.gethostname())
     
     _defaults = {
                  'logpath': lambda self, cr, uid, context: self.pool.get('ir.config_parameter').get_param(cr, uid, "log_path", context),
                  'ip': get_ip,
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
         serverDir = os.path.join(serverDir, os.pardir)
         virtualhostPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "virtualhost_path", context=context)
         virtualhostPath = os.path.join(serverDir, virtualhostPath)
         return virtualhostPath
     
     def create(self, cr, uid, values, context=None):
         
         values['state'] = 'draft'
         values['name'] = values['name'].strip().replace (" ", "_")
         
         return osv.osv.create(self, cr, uid, values, context=context)
     
     def unlink(self, cr, uid, ids, context=None):

         virtualhostPath = self.get_virtualhost_path(cr, uid, context)
         
         virtualhosts = super(virtualhost_ssl, self).browse(cr, uid, ids, context=context)
         for virtualhost in virtualhosts:
            try:
                os.remove(os.path.join(virtualhostPath, virtualhost.name))
            except OSError:
                pass
         
         return osv.osv.unlink(self, cr, uid, ids, context=context)
     
     def copy_data(self, cr, uid, id, default=None, context=None):
        """
        Copy given record's data with all its fields values

        :param cr: database cursor
        :param uid: current user id
        :param id: id of the record to copy
        :param default: field values to override in the original values of the copied record
        :type default: dictionary
        :param context: context arguments, like lang, time zone
        :type context: dictionary
        :return: dictionary containing all the field values
        """
        
        field_values = super(virtualhost_ssl, self).copy_data(cr, uid, id, default=default, context=context)
        field_values.update({'name': field_values['name'] + 'copy'})
        
        return field_values
     
     def regenerate_file(self, cr, uid, ids, context=None):
         
         return
     
         # Workflow
     def action_workflow_draft(self, cr, uid, ids, context=None):
         virtualhostPath = self.get_virtualhost_path(cr, uid, context)
         scriptsPath = self.pool.get('environment.ssl').get_scripts_path(cr, uid, context)
         apachePath = self.pool.get('ir.config_parameter').get_param(cr, uid, "apache_sites_available", context=context)
         virtualhost = self.pool.get('virtualhost.ssl').browse(cr, uid, ids[0], context=context)
         virtualhostdestination = os.path.join(apachePath, virtualhost.name)
         virtualhostsource = os.path.join(virtualhostPath, virtualhost.name)
         
         p = subprocess.Popen(["sh", "virtualhost_deactivate.sh", virtualhost.name, virtualhostsource, virtualhostdestination],  cwd=scriptsPath).wait()
         
         self.write(cr, uid, ids, { 'state' : 'draft' }, context=context)
         return True
    
     def action_workflow_active(self, cr, uid, ids, context=None):
         virtualhost = super(virtualhost_ssl, self).browse(cr, uid, ids[0], context=context)
         virtualhostPath = self.get_virtualhost_path(cr, uid, context)
         scriptsPath = self.pool.get('environment.ssl').get_scripts_path(cr, uid, context)
         apachePath = self.pool.get('ir.config_parameter').get_param(cr, uid, "apache_sites_available", context=context)
         certificatesPath = self.pool.get('environment.ssl').get_certificates_path(cr, uid, context)
         certificatesCrl = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_crl", context=context)
         certificationServer = self.pool.get('certificate.ssl').browse(cr, uid, virtualhost.certificateserver.id, context=context)
         certificationAuthority = self.pool.get('certificate.ssl').browse(cr, uid, certificationServer.certification_authority.id, context=context)
         currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
         absfilePath = os.path.abspath(os.path.join(currentPath, 'templates/'))
         
         absfilePathCA = os.path.abspath(os.path.join(certificatesPath, certificationAuthority.name_file, "certs", certificationAuthority.name_file + ".cert.pem"))
         absfilePathCRL = os.path.abspath(os.path.join(certificatesPath, certificationAuthority.name_file,"crl", certificatesCrl + ".pem"))
         absfilePathCertificateServer = os.path.abspath(os.path.join(certificatesPath, certificationAuthority.name_file, "certs", certificationServer.name_file + ".cert.pem"))
         absfilePathKeyServer = os.path.abspath(os.path.join(certificatesPath, certificationAuthority.name_file, "private", certificationServer.name_file + ".key.pem"))
         absfilePathLog = os.path.abspath(os.path.join(virtualhost.logpath, virtualhost.name + ".log"))
         
         lookup = TemplateLookup(directories=[absfilePath])
         template = Template("""<%include file="virtualhost.txt"/>""", lookup=lookup)
         templateRendered = template.render(servername=virtualhost.servername, \
                                            serveralias=virtualhost.serveralias, \
                                            certificateca=absfilePathCA,\
                                            revocationfile=absfilePathCRL, \
                                            certificateserver=absfilePathCertificateServer, \
                                            keyserver=absfilePathKeyServer,\
                                            proxypass= 'http://' + virtualhost.ip + ":" + virtualhost.port + '/',\
                                            logfile= absfilePathLog,\
                                            )
         
         if not os.path.exists(virtualhostPath):
             os.makedirs(virtualhostPath)
         
         f = open(os.path.join(virtualhostPath, virtualhost.name), 'w')
         f.write(templateRendered)
         f.close()   
         
         virtualhostsource = os.path.join(virtualhostPath, virtualhost.name)
         virtualhostdestination = os.path.join(apachePath, virtualhost.name)
         
         p = subprocess.Popen(["sh", "virtualhost_activate.sh", virtualhost.name, virtualhostsource, virtualhostdestination],  cwd=scriptsPath).wait()
         
         self.write(cr, uid, ids, { 'state' : 'active' }, context=context)
         return True
    
     def action_workflow_disable(self, cr, uid, ids, context=None):
         virtualhostPath = self.get_virtualhost_path(cr, uid, context)
         scriptsPath = self.pool.get('environment.ssl').get_scripts_path(cr, uid, context)
         apachePath = self.pool.get('ir.config_parameter').get_param(cr, uid, "apache_sites_available", context=context)
         virtualhost = self.pool.get('virtualhost.ssl').browse(cr, uid, ids[0], context=context)
         virtualhostdestination = os.path.join(apachePath, virtualhost.name)
         virtualhostsource = os.path.join(virtualhostPath, virtualhost.name)
         
         p = subprocess.Popen(["sh", "virtualhost_deactivate.sh", virtualhost.name, virtualhostsource, virtualhostdestination],  cwd=scriptsPath).wait()
         
         self.write(cr, uid, ids, { 'state' : 'disable' }, context=context)
        
         return True
