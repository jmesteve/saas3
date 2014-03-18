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
         certificatesPath = os.path.join(serverDir, certificatesPath)
         return certificatesPath
    
     def initialize_ssl_environment(self, cr, uid, ids, context=None, *args):
         currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
         certificatesPath = self.get_certificates_path(cr, uid, context)
         absfilePath = os.path.abspath(os.path.join(currentPath, 'scripts/'))
         savedPath = os.getcwd()
         
         try:
             os.mkdir(certificatesPath)
         except OSError:
             pass
         
         src_files = os.listdir(absfilePath)
         for file_name in src_files:
            full_file_name = os.path.join(absfilePath, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, certificatesPath)
         
         os.chdir(certificatesPath)
         if not os.path.isfile('index.txt'):
             subprocess.call(['sh ssl_initialize.sh'], shell=True)
         os.chdir(savedPath)
         
         return
         
     def remove_ssl_environment(self, cr, uid, ids, context=None, *args):
         currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
         certificatesPath = self.get_certificates_path(cr, uid, context)
         savedPath = os.getcwd()
         
         os.chdir(certificatesPath)
         subprocess.call(['sh ssl_remove.sh'], shell=True)
         os.chdir(savedPath)
         
         return