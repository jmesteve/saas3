from openerp.osv import fields, osv
from mako.template import Template
from mako.lookup import TemplateLookup
import os, inspect, subprocess, shutil, signal

class server_manager(osv.osv):
    _name = 'server.manager'
    
    def _get_path_server(self, cr, uid, ids,name, arg, context=None):
        res = dict.fromkeys(ids, False)
        server_path = self.pool.get('ir.config_parameter').get_param(cr, uid, "server_path", context=context)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = server_path +'openerp-' + line.name
        return res
    
    def _get_path_server_configuration(self, cr, uid, ids,name, arg, context=None):
        res = dict.fromkeys(ids, False)
        conf_path = self.pool.get('ir.config_parameter').get_param(cr, uid, "conf_path", context=context)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = conf_path + 'openerp-server-' + line.name + '.conf'
        return res
    
    def _status_server(self, cr, uid, ids, name, arg=None, context=None):
        if not len(ids):
            return False
        res = {}
        for reg in self.browse(cr, uid, ids, context):
            name = 'openerp-server-' + reg.name
            service = "ps -ax | grep " + name +" | grep 'python' | awk '{ print $1}'"
            proc = os.popen(service).read()
            proc = proc.split()
            proc = proc[:-1]
            try:
                num = len(proc)
                pid = map(int, proc)
                self.write(cr, uid, [reg.id], {'pid': pid})
                res[reg.id] = num
                
            except:
                return res
        return res
    
    _columns = {
                'name': fields.char('Name', size=50, required=True),
                'conf': fields.char('Name file configuration', size=50, required=True),
                'path_server': fields.function(_get_path_server, type='char', string='path server'),
                'path_configuration': fields.function(_get_path_server_configuration, type='char', string='path server configuration'),
                'debug_mode':fields.boolean('Debug mode'),
                'db_name': fields.char('Database Name', size=100,required=True),
                'db_filter':fields.char('Database Filter', size=100,required=True),
                'list_db':fields.boolean('List database'),
                'db_user':fields.char('Database User', size=100,required=True),
                'db_password':fields.char('Database password', size=100,required=True),
                'netrpc_interface':fields.char('xmlrpc interface', size=20,required=True),
                'xmlrpc_interface':fields.char('xmlrpc interface', size=20,required=True),
                'xmlrpc_port':fields.char('xmlrpc port', size=5,required=True),
                'static_http_document_root':fields.char('static http document root', size=200,required=True),
                'state': fields.selection([('draft','Draft'), ('conf','Conf created'),('daemon','Daemon Created'), ('active','Active'), ('disable','Disable')], 'State', readonly=True, help="The state.", select=True),
                'admin_passwd': fields.char('admin password', size=64, required=True),
                'log':fields.char('log path', size=100, required=True),
                'notes':fields.text('notes'),
                'active_process':fields.function(_status_server, type='integer', string='active processes',store=False),
                'pid':fields.text('pid list', readonly=True, store=False),
                }
    
    _defaults = {
                 'db_filter': '.*',
                 'db_name': 'False',
                 'db_user': 'openerp',
                 'db_password': 'postgres',
                 'netrpc_interface':'localhost',
                 'xmlrpc_interface':'localhost',
                 'xmlrpc_port':'65450',
                 'static_http_document_root':'/var/www/',
                 'state': 'draft',
                 'log': '/var/log/openerp/openerp.log'
                 }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique per Company!'),
    ]
  
    def create_conf(self, cr, uid, ids, context=None):
        currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        absfilePath = os.path.abspath(os.path.join(currentPath, 'templates/'))
        lookup = TemplateLookup(directories=[absfilePath])
        
        obj = self.pool.get('server.manager')
        for line in obj.browse(cr, uid, ids):
            template = Template("""<%include file="conf.mako"/>""", lookup=lookup)
            templateRendered = template.render(admin_passwd=line.admin_passwd, \
                                               db_name=line.db_name, \
                                               db_password=line.db_password, \
                                               db_user=line.db_user, \
                                               db_filter=line.db_filter, \
                                               debug_mode=line.debug_mode, \
                                               list_db=line.list_db, \
                                               log=line.log, \
                                               netrpc_interface=line.netrpc_interface, \
                                               static_http_document_root=line.static_http_document_root, \
                                               xmlrpc_interface=line.xmlrpc_interface, \
                                               xmlrpc_port=line.xmlrpc_port, \
                                           )
        
            virtualhostPath = line.path_configuration
            f = open(virtualhostPath, 'w')
            #os.chmod(virtualhostPath, 0755)
            f.write(templateRendered)
            f.close()   
        return True
   
    def create_daemon(self, cr, uid, ids, context=None):
        currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        absfilePath = os.path.abspath(os.path.join(currentPath, 'templates/'))
        lookup = TemplateLookup(directories=[absfilePath])
        
        obj = self.pool.get('server.manager')
        for line in obj.browse(cr, uid, ids):
            name = 'openerp-server-'+line.name
            template = Template("""<%include file="daemon.mako"/>""", lookup=lookup)
            templateRendered = template.render(
                                                PIDFILE1='${PIDFILE}', \
                                                CASE='${1}' ,\
                                                DAEMON1='${DAEMON}', \
                                                DAEMON_OPTS1='${DAEMON_OPTS}', \
                                                NAME1='${NAME}', \
                                                DESC1='${DESC}', \
                                                USER1='${USER}', \
                                                NAME=name, \
                                                DESC=name, \
                                                CONFIGFILE=line.path_configuration, \
                                                USER=line.db_user, \
                                           )
            
            virtualhostPath = line.path_server
            f = open(virtualhostPath, 'w')
            os.chmod(virtualhostPath, 0755)
            f.write(templateRendered)
            f.close()  
        return True 
    
    def action_start_server(self, cr, uid, ids, context=None):
        obj = self.pool.get('server.manager')
        for line in obj.browse(cr, uid, ids):
            path_service = '/etc/init.d/' 
            service ='sh ' + path_service + 'openerp-'+line.name +' start'
            proc = subprocess.call([service], shell=True)
            #self.write(cr, uid, [line.id], {'notes':proc})
            self.action_status_server( cr, uid, ids, context)
            return True
    
    def action_start_server2(self, cr, uid, ids, context=None):
        currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        absfilePath = os.path.abspath(os.path.join(currentPath, 'templates/'))
        lookup = TemplateLookup(directories=[absfilePath])
        
        obj = self.pool.get('server.manager')
        for line in obj.browse(cr, uid, ids):
            service = 'openerp-'+line.name
            template = Template("""<%include file="start_process.sh"/>""", lookup=lookup)
            templateRendered = template.render(
                                                SERVICE_PATTERN=service, \
                                              )
            subprocess.call([templateRendered], shell=True)
            
        return True 
    
    def action_stop_server(self, cr, uid, ids, context=None):
        try: 
            pids = self.action_status_server( cr, uid, ids, context)
            for pid in pids:
                os.kill(pid, signal.SIGKILL)
            self.action_status_server( cr, uid, ids, context)
            return True 
        except:
            self.action_status_server( cr, uid, ids, context)
            return False
          
    def action_restart_server(self, cr, uid, ids, context=None):
        self.action_stop_server(cr, uid, ids, context)
        self.action_start_server(cr, uid, ids, context)
        return True  
    
    def action_status_server(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            name = 'openerp-server-' + reg.name
            service = "ps -ax | grep " + name +" | grep 'python' | awk '{ print $1}'"
            proc = os.popen(service).read()
            proc = proc.split()
            proc = proc[:-1]
            try:
                num = len(proc)
                pid = map(int, proc)
                self.write(cr, uid, [reg.id], {'pid': pid,'active_process':num})
                return pid
            except:
                return []
       
    def action_workflow_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'draft' }, context=context)
        return True
    
    def action_workflow_conf(self, cr, uid, ids, context=None):
        self.create_conf( cr, uid, ids, context)
        self.write(cr, uid, ids, { 'state' : 'conf' }, context=context)
        return True
    
    def action_workflow_daemon(self, cr, uid, ids, context=None):
        self.create_daemon( cr, uid, ids, context)
        self.write(cr, uid, ids, { 'state' : 'daemon' }, context=context)
        return True

    def action_workflow_active(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'active' }, context=context)
        return True
    
    def action_workflow_disable(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'disable' }, context=context)
        return True
    