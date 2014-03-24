from openerp.osv import fields, osv
import os, inspect, subprocess, shutil

class server_general(osv.osv):
     _name =  'server.general'
     
     def action_start_server_all(self, cr, uid, ids, context=None):
        currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        absfilePath = os.path.abspath(os.path.join(currentPath, 'scripts/'))
        try:
            savedPath = os.getcwd()
        except OSError:
            pass
        
        os.chdir(absfilePath)
        subprocess.call(['sh start_process_all.sh'], shell=True)
        os.chdir(savedPath)
        return True      
    
     def action_stop_server_all(self, cr, uid, ids, context=None):
        currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        absfilePath = os.path.abspath(os.path.join(currentPath, 'scripts/'))
        try:
            savedPath = os.getcwd()
        except OSError:
            pass
        
        os.chdir(absfilePath)
        subprocess.call(['sh stop_process_all.sh'], shell=True)
        os.chdir(savedPath)
        return True   
    
     def action_restart_server_all(self, cr, uid, ids, context=None):
        currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        absfilePath = os.path.abspath(os.path.join(currentPath, 'scripts/'))
        try:
            savedPath = os.getcwd()
        except OSError:
            pass
        
        os.chdir(absfilePath)
        subprocess.call(['sh restart_process_all.sh'], shell=True)
        os.chdir(savedPath)
        return True       