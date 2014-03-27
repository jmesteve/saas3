from openerp.osv import fields, osv
import os, subprocess, shutil, inspect

class environment_ssl(osv.osv):
     _name =  'environment.ssl'
     _columns = {}
     
     def get_certificates_path(self, cr, uid, context=None):
         currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
         certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
         serverDir = os.path.join(currentPath, os.pardir)
         serverDir = os.path.join(serverDir, os.pardir)
         serverDir = os.path.join(serverDir, os.pardir)
         serverDir = os.path.join(serverDir, os.pardir)
         certificatesPath = os.path.join(serverDir, certificatesPath)
         return certificatesPath
     
     def get_certificates_path_private(self, cr, uid, context=None):
         certificatesPath = self.get_certificates_path(cr, uid, context=context)
         privatePath = os.path.join(certificatesPath, 'private/')
         return privatePath
     
     def get_certificates_path_certs(self, cr, uid, context=None):
         certificatesPath = self.get_certificates_path(cr, uid, context=context)
         certsPath = os.path.join(certificatesPath, 'certs/')
         return certsPath
    
     def get_scripts_path(self, cr, uid, context=None):
         currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
         scriptsPath = os.path.abspath(os.path.join(currentPath, 'scripts/'))
         
         return scriptsPath
    
     def initialize_ssl_environment(self, cr, uid, ids, context=None, *args):
         certificatesPath = self.get_certificates_path(cr, uid, context=context)
         scriptsPath = self.get_scripts_path(cr, uid, context=context)

         try:
             os.mkdir(certificatesPath)
         except OSError:
             pass
         
         #src_files = os.listdir(scriptsPath)
         #for file_name in src_files:
         #   full_file_name = os.path.join(scriptsPath, file_name)
         #   if (os.path.isfile(full_file_name)):
         #       shutil.copy(full_file_name, certificatesPath)
         
         #if not os.path.isfile(os.path.join(certificatesPath, 'index.txt')):
         #    p = subprocess.Popen(["sh", "ssl_initialize.sh"],  cwd=certificatesPath).wait()
         
         return
         
     def remove_ssl_environment(self, cr, uid, ids, context=None, *args):
         certificatesPath = self.get_certificates_path(cr, uid, context)
         p = subprocess.Popen(["sh", "ssl_remove.sh"],  cwd=certificatesPath).wait()
         
         return