from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import os
import openerp.pooler
import subprocess
import datetime
import uuid
import environment_ssl

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
                'state': fields.selection([('draft','Draft'), ('active','Active'), ('disable','Disable')], 'State', readonly=True, help="The state.", select=True),
                'begin_date':  fields.date('Begin Date', required=False),
                'create_date':  fields.date('Create Date', required=False),
                'end_date':  fields.date('End Date', required=False),
                'type': fields.selection([('user', 'User'), ('server', 'Server'), ('authority_root', 'Certification ROOT authority')], 'Type', readonly=False),
                'certificate_data_pem': fields.char('Data PEM', size=10000, required=True, readonly=True),
                'private_key': fields.char('Data PrivateKey', size=10000, required=True, readonly=True),
                'certification_authority': fields.many2one(
                    'certificate.ssl',
                    string='Certification Authority', required=False),
                'certificates': fields.one2many('certificate.ssl','certification_authority', string='Certificates', required=False),
                'domains': fields.one2many('domain.ssl','certificate_id', string='Alternate Domains', required=False)
                }
    
    _sql_constraints = [('item_name_file_unique','unique(name_file)', 'Item Name File must be unique!')]
    
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
        #print country
        if country == '' or country == None or country == False:
            country = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_country", context)
        return country
    
    def get_company_state(self, cr, uid, context):
        company = self.get_company(cr, uid, context)
        state = company.state_id.name.encode('utf8')
        #print state
        if state == '' or state == None or state == False:
            state = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_state_place", context)
        return state
    
    _defaults = {
        'city': get_company_city ,
        'state_place':  get_company_state,
        'country': get_company_country,
        'organization': get_company_name,
        'type': 'user',
        'begin_date': lambda self, cr, uid, context: datetime.date.today().strftime("%Y-%m-%d"),
        'end_date': lambda self, cr, uid, context: (datetime.date.today() + datetime.timedelta(days=3650)).strftime("%Y-%m-%d")
    }

    def create(self, cr, uid, values, context=None):
        
        certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
        certificatesKeysize = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_keysize", context=context)
        certificatesDays = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_days_root", context=context)
        savedPath = os.getcwd()
        
        domain_ssl = self.pool.get('environment.ssl')
        domain_ssl.initialize_ssl_environment(cr, uid, [], context=None)
        
        os.chdir(certificatesPath)
        
        values['name_file'] = uuid.uuid4().hex + '_' + values['name']
        certificateNameUser = 'certs/' + values['name_file'] + ".cert.pem"
        privateKeyNameUser = 'private/' + values['name_file'] + ".key.pem"
        
        values['country'] = values['country'].replace (" ", "_")
        values['city'] = values['city'].replace (" ", "_")
        values['state_place'] = values['state_place'].replace (" ", "_")
        values['organization'] = values['organization'].replace (" ", "_")
        values['name_file'] = values['name_file'].replace (" ", "_")
        values['commonname'] = values['commonname'].replace (" ", "_")
        values['password'] = values['password'].replace (" ", "_")
        
        if values['type'] == 'user':
            
            certificationAuthority = self.pool.get('certificate.ssl').browse(cr, uid, values['certification_authority'], context)
            
            begin_date = datetime.datetime.strptime(values['begin_date'], "%Y-%m-%d")
            end_date = datetime.datetime.strptime(values['end_date'], "%Y-%m-%d")
            
            subprocess.call(["sh ssl_gen_user.sh " + 
                             values['name_file'] + " " +
                             values['commonname'] + " " +
                             values['password'] + " " +
                             begin_date.strftime("%y%m%d%H%M%S") + 'Z' + " " +
                             end_date.strftime("%y%m%d%H%M%S") + 'Z' + " " +
                             values['country'] + " " +
                             values['city'] + " " +
                             values['state_place'] + " " +
                             values['organization'] + " " +
                             certificatesKeysize + " " +
                             certificationAuthority.name_file + " " +
                             certificationAuthority.password + " " + 
                             'openssl_client.cnf'
                             ], shell=True)
            
            subprocess.call(["sh ssl_gen_p12.sh " +
                             values['name_file'] + " " +
                             certificationAuthority.name_file + " " +
                             values['password'] + " " +
                             certificationAuthority.password
                             ], shell=True)
            
        elif values['type'] == 'authority_root':
            #print values['name_file'], values['password'], certificatesKeysize
            subprocess.call(["sh ssl_root_authority.sh " + 
                             values['name_file'] + " "+
                             values['commonname'] + " "+
                             values['password'] + " "+
                             values['country']+ " "+
                             values['city']+ " "+
                             values['state_place']+ " "+
                             values['organization']+ " "+
                             certificatesKeysize + " " +
                             certificatesDays
                             ], shell=True)
        elif values['type'] == 'server':
            
            certificationAuthority = self.pool.get('certificate.ssl').browse(cr, uid, values['certification_authority'], context)
            
            begin_date = datetime.datetime.strptime(values['begin_date'], "%Y-%m-%d")
            end_date = datetime.datetime.strptime(values['end_date'], "%Y-%m-%d")
            
            subprocess.call(["sh ssl_gen_server.sh " + 
                             values['name_file'] + " "+
                             values['commonname'] + " "+
                             begin_date.strftime("%y%m%d%H%M%S") + 'Z' + " " +
                             end_date.strftime("%y%m%d%H%M%S") + 'Z' + " " +
                             values['country']+ " "+
                             values['city']+ " "+
                             values['state_place']+ " "+
                             values['organization']+ " "+
                             certificatesKeysize + " " +
                             certificationAuthority.name_file + " " +
                             certificationAuthority.password + " " + 
                             'openssl_server.cnf'
                             ], shell=True)
            
        
        f = open(certificateNameUser, 'r')
        certificate_data_pem = f.read()
        f.close()

        f = open(privateKeyNameUser, 'r')
        private_key = f.read()
        f.close()   
        
        os.chdir(savedPath)
        
        values['create_date'] = datetime.date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        values['private_key'] = private_key
        values['certificate_data_pem'] = certificate_data_pem
        
        return super(certificate_ssl, self).create(cr, uid, values, context=context)
        
    def unlink(self, cr, uid, ids, context=None, *args):
        
        certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
        savedPath = os.getcwd()
        
        os.chdir(certificatesPath)
        
        certificates = super(certificate_ssl, self).browse(cr, uid, ids, context=context)
        for certificate in certificates:
            if certificate.type == 'user':
                if certificate.state == 'active':
                    self.generate_ssl_revoke_user(cr, uid, [certificate.id], context=context)
                    
                try:
                    os.remove('private/' + certificate.name_file + ".key.pem")
                    os.remove('certs/' + certificate.name_file + ".cert.pem")
                    os.remove('certs/' + certificate.name_file + ".csr.pem")
                    os.remove('certs/' + certificate.name_file + ".p12")
                except OSError:
                    pass
            elif certificate.type == 'server':
                if certificate.state == 'active':
                    self.generate_ssl_revoke_user(cr, uid, [certificate.id], context=context)
                
                try:
                    os.remove('private/' + certificate.name_file + ".key.pem")
                    os.remove('certs/' + certificate.name_file + ".csr.pem")
                    os.remove('certs/' + certificate.name_file + ".cert.pem")
                except OSError:
                    pass
            elif certificate.type == 'authority_root' and (certificate.state == 'draft' or certificate.state == 'disable'):
                try:
                    os.remove('private/' + certificate.name_file + ".key.pem")
                    os.remove('certs/' + certificate.name_file + ".cert.pem")
                except OSError:
                    pass
            else:
                ids.remove(certificate.id)
                
        os.chdir(savedPath)
        
        return super(certificate_ssl, self).unlink(cr, uid, ids, context=context, *args)
    
    def generate_ssl_crl(self, cr, uid, ids, context=None, *args):
         certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
         namefileCrl = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_crl", context=context)
         certificate = super(certificate_ssl, self).browse(cr, uid, ids[0], context=context)
         currentPath = os.getcwd()
         
         os.chdir(certificatesPath)
         subprocess.call(['sh ssl_gen_crl.sh ' + 
                           namefileCrl + " " + 
                           certificate.name_file + " " +
                           certificate.password + " " +
                           'openssl_client.cnf'
                          ], shell=True)
         os.chdir(currentPath)
         
         return
    
    def generate_ssl_revoke_user(self, cr, uid, ids, context=None, *args):
         certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
         namefileCrl = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_crl", context=context)
         certificate = super(certificate_ssl, self).browse(cr, uid, ids[0], context=context)
         
         currentPath = os.getcwd()
         
         if certificate.type == 'user' or certificate.type == 'server':
             os.chdir(certificatesPath)
         
             subprocess.call(['sh ssl_revoke_user.sh ' + 
                               certificate.name_file + " " + 
                               certificate.password + " " +
                               namefileCrl + " " +
                               certificate.certification_authority.name_file + " "
                               'openssl_client.cnf'
                              ], shell=True)
             
             os.chdir(currentPath)
         
             self.write(cr, uid, ids, { 'state' : 'disable' }, context=context)
         
         return
     
    def regenerate_certificate(self, cr, uid, ids, context=None, *args):
        certificatesPath = self.pool.get('ir.config_parameter').get_param(cr, uid, "certificates_path", context=context)
        currentPath = os.getcwd()
        certificate = super(certificate_ssl, self).browse(cr, uid, ids[0], context=context)
        
        os.chdir(certificatesPath)
        
        f = open('private/' + certificate.name_file + '.key.pem', 'w')
        f.write(certificate.private_key)
        f.close()
        
        f = open('certs/' + certificate.name_file + '.cert.pem', 'w')
        f.write(certificate.certificate_data_pem)
        f.close()
        
        if certificate.type == 'user':
            subprocess.call(["sh ssl_gen_p12.sh " +
                     certificate.name_file + " " +
                     certificate.certification_authority.name_file + " " +
                     certificate.password + " " +
                     certificate.certification_authority.password
                     ], shell=True)


        os.chdir(currentPath)
        
        return
    
    # Workflow
    def action_workflow_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'draft' }, context=context)
        return True

    def action_workflow_active(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'active' }, context=context)
        return True
    
    def action_workflow_disable(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'disable' }, context=context)
        
        return True

#user_ssl()