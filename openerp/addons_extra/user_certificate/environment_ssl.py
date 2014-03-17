from openerp.osv import fields, osv
import os, subprocess, shutil

class domain_ssl(osv.osv):
     _name =  'environment.ssl'
     _columns = {}
     
     def initialize_ssl_environment(self, cr, uid, ids, context=None, *args):
         certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
         absfilePath = os.path.abspath('openerp/addons_extra/user_certificate/scripts/')
         currentPath = os.getcwd()
         
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
         subprocess.call(['sh ssl_initialize.sh'], shell=True)
         os.chdir(currentPath)
         
         return
         
     def remove_ssl_environment(self, cr, uid, ids, context=None, *args):
         certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
         currentPath = os.getcwd()
         
         os.chdir(certificatesPath)
         subprocess.call(['sh ssl_remove.sh'], shell=True)
         os.chdir(currentPath)
         
         return