from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import os
import openerp.pooler
import subprocess
import datetime
import uuid
import environment_ssl
import base64
import string
import shutil
import inspect
from mako.template import Template
from mako.lookup import TemplateLookup

class certificate_ssl(osv.osv):
    _name =  'certificate.ssl'
    _columns = {'name': fields.char('Name', size=25, required=True),
                'commonname': fields.char('Common Name', size=25, required=True),
                'password': fields.char('Password', size=25, required=True),
                'country': fields.char('Country', size=2, required=False),
                'city': fields.char('City', size=25, required=False),
                'state_place': fields.char('State', size=25, required=False),
                'organization': fields.char('Organization', size=25, required=False),
                'name_file': fields.char('Name File', size=60, required=False),
                'name_filep12': fields.char('Name File', size=60, required=False),
                'state': fields.selection([('draft','Draft'), ('active','Active'), ('disable','Disable')], 'State', readonly=True, help="The state.", select=True),
                'begin_date':  fields.date('Begin Date', required=False),
                'create_date':  fields.date('Create Date', required=False),
                'end_date':  fields.date('End Date', required=False),
                'type': fields.selection([('user', 'User'), ('server', 'Server'), ('authority_root', 'Certification ROOT authority')], 'Type', readonly=False),
                'certificate_data_p12': fields.binary('Download Certificate', readonly=False),
                'certificate_data_pem': fields.char('Data PEM', size=10000, required=False, readonly=True),
                'private_key': fields.char('Data PrivateKey', size=10000, required=False, readonly=True),
                'certification_authority': fields.many2one('certificate.ssl', string='Certification Authority', required=False),
                'certificates': fields.one2many('certificate.ssl','certification_authority', string='Certificates', required=False),
                'domains': fields.one2many('domain.ssl','certificate_id', string='Alternate Domains', required=False),
                'user': fields.many2one('res.users', string='User', required=False),
                'crlnumber': fields.char('CRL Number', size=10, required=False)
                }
    
    _sql_constraints = [('item_name_unique', 'unique(name)', 'Item Name must be unique!'), ('item_name_file_unique','unique(name_file, certification_authority)', 'Item Name File must be unique!'), ('item_commonname_unique','unique(commonname, certification_authority)', 'Item Common Name must be unique!')]
    
    def generate_random_password(self, cr, uid, context):
        chars = '23456789ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz'
        #assert 256 % len(chars) == 0  # non-biased later modulo
        PWD_LEN = 16
        password = ''.join(chars[ord(c) % len(chars)] for c in os.urandom(PWD_LEN))
        
        return password
    
    def get_company(self, cr, uid, context):
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'certificate.ssl', context=context)
        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        return company
    
    def get_company_name(self, cr, uid, context):
        company = self.get_company(cr, uid, context)
        name = company.name
        if name == '' or name == None or name == False:
            name = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_organization", context)
        return name
    
    def get_company_city(self, cr, uid, context):
        company = self.get_company(cr, uid, context)
        city = company.city
        if city == '' or city == None or city == False:
            city = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_city", context)
        return city
    
    def get_company_country(self, cr, uid, context):
        company = self.get_company(cr, uid, context)
        country = company.country_id.code

        if country == '' or country == None or country == False:
            country = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_country", context)
        return country
    
    def get_company_state(self, cr, uid, context):
        company = self.get_company(cr, uid, context)
        state = company.state_id.name
        if state == '' or state == None or state == False:
            state = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_state_place", context)
        else:
            state = state.encode('ascii', 'ignore')
            
        return state
    
    _defaults = {
        'password': generate_random_password,
        'city': get_company_city,
        'state_place':  get_company_state,
        'country': get_company_country,
        'organization': get_company_name,
        'type': 'user',
        'begin_date': lambda self, cr, uid, context: datetime.date.today().strftime("%Y-%m-%d"),
        'end_date': lambda self, cr, uid, context: (datetime.date.today() + datetime.timedelta(days=3650)).strftime("%Y-%m-%d")
    }
    
    def onchange_attribute_name(self, cr, uid, ids, name=False, context=None):
        result = {}
        if name:
            result['value'] = {'commonname': cr.dbname + ' ' + name}
        return result
    
    def default_get(self, cr, uid, fields, context=None):
        """
             To get default values for the object.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param fields: List of fields for which we want default values
             @param context: A standard dictionary

             @return: A dictionary which of fields with values.

        """
        res = super(certificate_ssl, self).default_get(cr, uid, fields, context=context)
        
        if 'user' in context:
            user_id = context.get('user', False)
            res['user'] = user_id
            res['type'] = 'user'
        if 'name' in context:
            name = context.get('name', False)
            res['name'] = name
        if 'certification_authority' in context:
            authority_id = context.get('certification_authority', False)
            res['certification_authority'] = authority_id
        if 'name' in context and 'certification_authority' in context:
            res['commonname'] = cr.dbname + " " + res['name']
        
        return res
    
    def initialize_ca(self, cr, uid, ids, context=None):
         certificate = super(certificate_ssl, self).browse(cr, uid, ids, context=context)
         certificatesPath = self.pool.get('environment.ssl').get_certificates_path(cr, uid, context=context)
         certificatesPath = os.path.join(certificatesPath, certificate.name_file)
         scriptsPath = self.pool.get('environment.ssl').get_scripts_path(cr, uid, context=context)

         try:
             os.mkdir(certificatesPath)
         except OSError:
             pass
         
         src_files = os.listdir(scriptsPath)
         for file_name in src_files:
            full_file_name = os.path.join(scriptsPath, file_name)
            if (os.path.isfile(full_file_name)):
                try:
                    shutil.copy(full_file_name, certificatesPath)
                except OSError:
                    pass
         
         if not os.path.isfile(os.path.join(certificatesPath, 'index.txt')):
             p = subprocess.Popen(["sh", "ssl_initialize.sh"],  cwd=certificatesPath).wait()
         
         return
     
    def write(self, cr, uid, ids, vals, context=None):
        state = self.read(cr, uid, ids, ['state'], context=context)
        for t in state:
            if t['state'] in ('active', 'disable'):
                raise osv.except_osv(('Invalid action !'),('You can not edit a record which is in Active or Disable state.'))
                return True
        
        return super(certificate_ssl, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, values, context=None):
        
        values['state'] = 'draft'
        values['name_file'] = (cr.dbname + '_' + values['name'].strip()).replace (" ", "_")
        values['name_filep12'] = values['name_file'] + ".p12"
        
        return super(certificate_ssl, self).create(cr, uid, values, context=context)
        
    def unlink(self, cr, uid, ids, context=None, *args):
        
         state = self.read(cr, uid, ids, ['state'], context=context)
         for t in state:
            if t['state'] in ('active'):
                raise osv.except_osv(('Invalid action !'),('You can not delete a record which is in Active state.'))
         
         certificates = self.read(cr, uid, ids, ['certificates'], context=context)
         for t in certificates:
            if t['certificates'] != []:
                raise osv.except_osv(('Invalid action !'),('You can not delete a certification authority with certificates.'))
         
         certificatesPath = self.pool.get('environment.ssl').get_certificates_path(cr, uid, context)
         authorities = self.read(cr, uid, ids, ['type', 'name'], context=context)
         for t in authorities:
             if t['type'] == 'authority_root':
                 try:
                     shutil.rmtree(os.path.join(certificatesPath, t['name']))
                 except OSError:
                     pass
            
         return super(certificate_ssl, self).unlink(cr, uid, ids, context=context, *args)
    
    def generate_ssl_crl(self, cr, uid, ids, context=None, *args):
         certificatesPath = self.pool.get('environment.ssl').get_certificates_path(cr, uid, context)
         namefileCrl = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_crl", context=context)
         certificate = super(certificate_ssl, self).browse(cr, uid, ids[0], context=context)
         certificatesPath = os.path.join(certificatesPath, certificate.name_file)
         
         self.initialize_ca(cr, uid, ids[0], context=context)
         
         p = subprocess.Popen(["sh", "ssl_gen_crl.sh",
                               namefileCrl, 
                               certificate.name_file, 
                               certificate.password, 
                               'openssl_client.cnf'],  cwd=certificatesPath).wait()
         return
    
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
        
        field_values = super(certificate_ssl, self).copy_data(cr, uid, id, default=default, context=context)
        
        field_values.update({'commonname': field_values['commonname'] + ' copy'})
        field_values.update({'name_file': field_values['name_file'] + 'copy'})
        field_values.update({'name': field_values['name'] + 'copy'})
        
        return field_values
    
    # Workflow
    def action_workflow_draft(self, cr, uid, ids, context=None):
        certificatesPath = self.pool.get('environment.ssl').get_certificates_path(cr, uid, context)
        certificate = self.pool.get('certificate.ssl').browse(cr, uid, ids[0], context)
        namefileCrl = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_crl", context=context)
        
        if certificate.type == 'user' or certificate.type == 'server':
            certificatesPath = os.path.join(certificatesPath, certificate.certification_authority.name_file)
            privatePath = os.path.join(certificatesPath,'private/')
            certsPath = os.path.join(certificatesPath,'certs/')            
            try:
                p = subprocess.Popen(["sh", 
                                  "ssl_revoke_user.sh",
                                  certificate.name_file,
                                  certificate.certification_authority.password,
                                  namefileCrl,
                                  certificate.certification_authority.name_file,
                                  'openssl_client.cnf'],  cwd=certificatesPath).wait()
            except OSError:
                pass
                                  
            self.generate_ssl_crl(cr, uid, [certificate.certification_authority.id], context=context)
            
            try:
                os.remove(os.path.join(certsPath, certificate.name_file + '.cert.pem'))
                os.remove(os.path.join(privatePath, certificate.name_file + '.key.pem'))
                os.remove(os.path.join(certsPath, certificate.name_file + '.csr.pem'))
            except OSError:
                pass
            
            if certificate.type == 'user':
                try:
                    os.remove(os.path.join(certsPath, certificate.name_filep12))
                except:
                    pass
                 
            
        super(certificate_ssl, self).write(cr, uid, ids, { 'state' : 'draft' }, context=context)
        return True

    def action_workflow_active(self, cr, uid, ids, context=None):
        certificatesPath = self.pool.get('environment.ssl').get_certificates_path(cr, uid, context)
        certificatesKeysize = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_keysize", context=context)
        certificatesDays = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_days_root", context=context)
        certificate = self.pool.get('certificate.ssl').browse(cr, uid, ids[0], context)
        
        if certificate.type == 'user' or certificate.type == 'server':
            certificatesPath = os.path.join(certificatesPath, certificate.certification_authority.name_file)
            self.initialize_ca(cr, uid, certificate.certification_authority.id, context=context)
        else:
            certificatesPath = os.path.join(certificatesPath, certificate.name_file)
            self.initialize_ca(cr, uid, ids[0], context=context)
        
        values = {}    
        
        if certificate.crlnumber:
            certificatesPathNewcerts = os.path.join(certificatesPath, 'newcerts')
            
            try:
                os.remove(os.path.join(certificatesPathNewcerts, certificate.crlnumber + '.pem'))
            except OSError:
               pass
            
            p = subprocess.Popen(["sh", "ssl_remove_revoked.sh", certificate.crlnumber],  cwd=certificatesPath).wait()
            self.generate_ssl_crl(cr, uid, [certificate.certification_authority.id], context=context)
            
        
        if certificate.type == 'user' or certificate.type == 'server':
            crlnumber = os.path.join(certificatesPath, 'serial')
            f = open(crlnumber, 'r')
            crlnumberData = f.read()
            f.close()
            values['crlnumber'] = crlnumberData.strip()
            
        privatePath = os.path.join(certificatesPath,'private/')
        certsPath = os.path.join(certificatesPath,'certs/')
        
        certificateNameUser =  os.path.join(certsPath, certificate.name_file + ".cert.pem") 
        certificateP12 = os.path.join(certsPath, certificate.name_filep12)
        privateKeyNameUser =  os.path.join(privatePath, certificate.name_file + ".key.pem")
        
        if certificate.type == 'user':
            
            if certificate.user == False or certificate.user == None:
                user = self.pool.get('res.users').browse(cr, uid, uid)
                values['user'] = user.id
            
            certificationAuthority = self.pool.get('certificate.ssl').browse(cr, uid, certificate.certification_authority.id, context)
            
            begin_date = datetime.datetime.strptime(certificate.begin_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(certificate.end_date, "%Y-%m-%d")
            
            p = subprocess.Popen(["sh", "ssl_gen_user.sh",
                                  certificate.name_file,
                                  certificate.commonname,
                                  certificate.password,
                                  begin_date.strftime("%y%m%d%H%M%S") + 'Z',
                                  end_date.strftime("%y%m%d%H%M%S") + 'Z',
                                  certificate.country,
                                  certificate.city,
                                  certificate.state_place,
                                  certificate.organization,
                                  certificatesKeysize,
                                  certificationAuthority.name_file,
                                  certificationAuthority.password,
                                  'openssl_client.cnf'],  cwd=certificatesPath).wait()
            
            p = subprocess.Popen(["sh", "ssl_gen_p12.sh",
                                  certificate.name_file,
                                  certificationAuthority.name_file,
                                  certificate.password,
                                  certificationAuthority.password],  cwd=certificatesPath).wait()
            
        elif certificate.type == 'authority_root':
            p = subprocess.Popen(["sh", "ssl_root_authority.sh",
                                  certificate.name_file,
                                  certificate.commonname,
                                  certificate.password,
                                  certificate.country,
                                  certificate.city,
                                  certificate.state_place,
                                  certificate.organization,
                                  certificatesKeysize,
                                  certificatesDays],  cwd=certificatesPath).wait()
                                  
            self.generate_ssl_crl(cr, uid, ids, context=context)
                                  
        elif certificate.type == 'server':
            
            certificationAuthority = self.pool.get('certificate.ssl').browse(cr, uid, certificate.certification_authority.id, context)
            
            begin_date = datetime.datetime.strptime(certificate.begin_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(certificate.end_date, "%Y-%m-%d")
            
            # Generar configuracion del servidor con alternames
            domains = map(lambda(domain): domain.id, certificate.domains)
            dnss = self.pool.get('domain.ssl').read(cr, uid, domains, ['name'], context=context)
            if dnss:
                currentPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                absfilePath = os.path.abspath(os.path.join(currentPath, 'templates/'))
                lookup = TemplateLookup(directories=[absfilePath])
                template = Template("""<%include file="openssl_server.cnf"/>""", lookup=lookup)
                dnss.insert(0, {'name': certificate.commonname, 'id': certificate.id})
                templateRendered = template.render(dnss=dnss)
                
                f = open(os.path.join(certificatesPath, "openssl_server.cnf"), 'w')
                f.write(templateRendered)
                f.close()
            
            
            p = subprocess.Popen(["sh", "ssl_gen_server.sh",
                                  certificate.name_file,
                                  certificate.commonname,
                                  begin_date.strftime("%y%m%d%H%M%S") + 'Z',
                                  end_date.strftime("%y%m%d%H%M%S") + 'Z',
                                  certificate.country,
                                  certificate.city,
                                  certificate.state_place,
                                  certificate.organization,
                                  certificatesKeysize,
                                  certificationAuthority.name_file,
                                  certificationAuthority.password,
                                  'openssl_server.cnf'],  cwd=certificatesPath).wait()
        
        f = open(certificateNameUser, 'r')
        certificate_data_pem = f.read()
        f.close()

        f = open(privateKeyNameUser, 'r')
        private_key = f.read()
        f.close() 
        
        if certificate.type == 'user':
            f = open(certificateP12, 'rb')
            certificate_data_p12 = f.read()
            f.close()
            values['certificate_data_p12'] = base64.encodestring(certificate_data_p12)
        
        values['create_date'] = datetime.date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        values['private_key'] = private_key
        values['certificate_data_pem'] = certificate_data_pem
        values['state']  = 'active'

        super(certificate_ssl, self).write(cr, uid, ids, values, context=context)
        return True
    
    def action_workflow_disable(self, cr, uid, ids, context=None):
        certificatesPath = self.pool.get('environment.ssl').get_certificates_path(cr, uid, context)
        namefileCrl = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_crl", context=context)
        certificate = super(certificate_ssl, self).browse(cr, uid, ids[0], context=context)
        
        if certificate.type == 'user' or certificate.type == 'server':
            certificatesPath = os.path.join(certificatesPath, certificate.certification_authority.name_file)
            #self.initialize_ca(cr, uid, certificate.certification_authority.id, context=context)
        else:
            certificatesPath = os.path.join(certificatesPath, certificate.name_file)
            #self.initialize_ca(cr, uid, ids[0], context=context)
        
        
        if certificate.type == 'user' or certificate.type == 'server':
            privatePath = os.path.join(certificatesPath,'private/')
            certsPath = os.path.join(certificatesPath,'certs/')
            try:
                p = subprocess.Popen(["sh", 
                                  "ssl_revoke_user.sh",
                                  certificate.name_file,
                                  certificate.certification_authority.password,
                                  namefileCrl,
                                  certificate.certification_authority.name_file,
                                  'openssl_client.cnf'],  cwd=certificatesPath).wait()
            except OSError:
                pass
                
                                  
            self.generate_ssl_crl(cr, uid, [certificate.certification_authority.id], context=context)
        
            try:
                os.remove(os.path.join(certsPath, certificate.name_file + '.cert.pem'))
                os.remove(os.path.join(privatePath, certificate.name_file + '.key.pem'))
                os.remove(os.path.join(certsPath, certificate.name_file + '.csr.pem'))
            except OSError:
                pass
            
            if certificate.type == 'user':
                try:
                    os.remove(os.path.join(certsPath, certificate.name_filep12))
                except:
                    pass
        
        super(certificate_ssl, self).write(cr, uid, ids, { 'state' : 'disable' }, context=context)
        
        return True

#user_ssl()