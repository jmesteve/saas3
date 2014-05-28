from openerp.osv import fields,osv
import os, inspect, subprocess, shutil, signal
import pxssh
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import binascii

class ibeacons_scanned(osv.osv):
    _name = 'ibeacon.scanned'
    
    def _status_ibeacon(self, cr, uid, ids, name, arg=None, context=None):
        res = {}
        for reg in self.browse(cr, uid, ids, context):
            if reg.enable == True and reg.name !="(unknown)":
                res[reg.id] = True
            else:
                res[reg.id] = False
        return res
        
    _columns = {
                'mac': fields.char('Mac', size=17),
                'name': fields.char('Name', size=64),
                'name_verify': fields.char('Name verify', size=64),
                'enable': fields.boolean('Enable'),
                'create_date' : fields.datetime('Date Created', readonly=True),
                'write_date' : fields.datetime('Date Writed', readonly=True),
                'uuid': fields.char('Uuid 0xFFF1', size=36, help="128 bit"),
                'major': fields.integer('Major 0xFFF2',  help="0-65535"),
                'minor': fields.integer('Minor 0xFFF3',  help="0-65535"),
                'accuracy': fields.integer('Accuracy adjust 0xFFF4',help="0-255"),
                'txpower': fields.selection([('00','+0 dBm'),('01','+4 dBm'),('02','-6 dBm'), ('03','-23 dBm')], 'Tx-power  0xFFF5', size=2, select=True),
                'broadcasting_cycle': fields.char('Broadcasting cycle 0xFFF7',size=4, help="1-255"),
                'serial_id': fields.integer('Serial Id 0xFFF8', help="0001-9999"),
                'template_id': fields.many2one('ibeacon.parameters', 'Template id', select=1, ondelete="cascade"),
                'active_beacon': fields.function(_status_ibeacon, type='boolean', string='active',store=True),
                }
    
    _order = "active_beacon desc, minor"
    
    def ssh_write(self, cr, uid, ids, context=None):
        status=[]
        try: 
            obj = self.pool.get('ibeacon.parameters')
            
            ibeacon_scanned = self.browse(cr, uid, ids[0], context=context)
            bluetooth_adr = ibeacon_scanned.mac
            template_id = ibeacon_scanned.template_id.id
            template = obj.browse(cr,uid,[template_id],context=context)
            
            status.append(obj.ssh_login(cr, uid, [template_id], context=context))
            
            if template[0].check_uuid:
                uuid = obj.gatttool_write(bluetooth_adr, '0x33', template[0].uuid)
                #status.append(uuid)
            if template[0].check_major:
                major = hex(template[0].major)
                major = obj.gatttool_write(bluetooth_adr, '0x36', major)
                #status.append(major)
            if template[0].check_minor:
                minor = hex(template[0].minor)
                minor = obj.gatttool_write(bluetooth_adr, '0x39', minor)
                #status.append(minor)
            if template[0].check_accuracy:
                accuracy = hex(template[0].accuracy)
                accuracy = obj.gatttool_write(bluetooth_adr, '0x3c', accuracy)
                #status.append(accuracy)
            if template[0].check_txpower:
                #txpower = hex(template[0].txpower)
                txpower = obj.gatttool_write(bluetooth_adr, '0x3F', template[0].txpower)
                status.append(txpower)
            if template[0].check_password:
                password = hex(template[0].password)
                password = obj.gatttool_write(bluetooth_adr, '0x42', password)
                #status.append(password)
            if template[0].check_broadcasting_cycle:
                broadcasting_cycle = hex(template[0].broadcasting_cycle)
                broadcasting_cycle = obj.gatttool_write(bluetooth_adr, '0x45', broadcasting_cycle)
                #status.append(broadcasting_cycle)
            if template[0].check_serial_id:
                serial_id = hex(template[0].serial_id)
                serial_id = obj.gatttool_write(bluetooth_adr, '0x48', serial_id)
                #status.append(serial_id)
           
        except:
            status.append("gatttool write Failed")
            
        status.append(obj.ssh_logout())
        return status
    
    
    def action_reboot(self, cr, uid, ids, context=None):
        status=[]
        try: 
            obj = self.pool.get('ibeacon.parameters')
            
            ibeacon_scanned = self.browse(cr, uid, ids[0], context=context)
            bluetooth_adr = ibeacon_scanned.mac
            template_id = ibeacon_scanned.template_id.id
            template = obj.browse(cr,uid,[template_id],context=context)
            
            status.append(obj.ssh_login(cr, uid, [template_id], context=context))
            
            reboot = hex(template[0].reboot)
            reboot = obj.gatttool_write(bluetooth_adr, '0x4b', password)  #send the password
            #status.append(reboot)
            
        except:
            status.append("gatttool reboot Failed")
            
        status.append(obj.ssh_logout())
        return status
    
    def ssh_read(self, cr, uid, ids, context=None):
        status=[]
        try: 
            
            ibeacon_scanned = self.browse(cr, uid, ids[0], context=context)
            name = ibeacon_scanned.name
            if name == "(unknown)":
                status.append("ibeacon unknown")
                return status
            obj = self.pool.get('ibeacon.parameters')
            template_id = ibeacon_scanned.template_id.id
            status.append(obj.ssh_login(cr, uid, [template_id], context=context))
            
            #status.append(obj.restart_hci())
            
            bluetooth_adr = ibeacon_scanned.mac
            #status.append(obj.gatttool_connect(bluetooth_adr))
            
            name_verify = obj.gatttool_read(bluetooth_adr, '0x3')
            name_verify = binascii.unhexlify(''.join(name_verify.split()))
            
            uuid = obj.gatttool_read(bluetooth_adr, '0x33')
            uuid = uuid.replace(" ", "")
            #status.append(uuid)
            
            major = obj.gatttool_read(bluetooth_adr, '0x36')
            major = int(major.replace(" ", ""),16)
            #status.append(major)
            
            minor = obj.gatttool_read(bluetooth_adr, '0x39')
            minor = int(minor.replace(" ", ""),16)
            #status.append(minor)
            
            accuracy = obj.gatttool_read(bluetooth_adr, '0x3c')
            accuracy = int(accuracy.replace(" ", ""),16)
            #status.append(accuracy)
            
            txpower = obj.gatttool_read(bluetooth_adr, '0x3f')
            txpower = txpower.replace(" ", "")
            #status.append(txpower)
            
            broadcasting_cycle = obj.gatttool_read(bluetooth_adr, '0x45')
            broadcasting_cycle = broadcasting_cycle.replace(" ", "")
            #status.append(broadcasting_cycle)
            
            serial_id = obj.gatttool_read(bluetooth_adr, '0x48')
            serial_id = int(serial_id.replace(" ", ""),16)
            #status.append(serial_id)
            
            self.write(cr, uid, ids[0], {
                                    'name_verify':name_verify,
                                    'uuid':uuid,
                                    'major':major,
                                    'minor':minor,
                                    'accuracy':accuracy,
                                    'txpower':txpower,
                                    'broadcasting_cycle':broadcasting_cycle,
                                    'serial_id':serial_id,
                                }, context=context)
            
          
        except:
            status.append("gatttool read Failed")
            
        status.append(obj.ssh_logout())
        return status
        
    def action_read(self, cr, uid, ids, context=None):
        status = self.ssh_read(cr, uid, ids, context)
        for line in status:
            if line != []:
                return self.pool.get('warning_box').info(cr, uid, title='SSH Scan', message=status)  
            
    def action_write(self, cr, uid, ids, context=None):
        status = self.ssh_write(cr, uid, ids, context)
        for line in status:
            if line != []:
                return self.pool.get('warning_box').info(cr, uid, title='SSH Scan', message=status)  

class ibeacon_parameters(osv.osv):
    _name = 'ibeacon.parameters'
     
    _columns = {'host': fields.char('Host', size=64),
                'ssh_user': fields.char('SSH User', size=32),
                'ssh_password': fields.char('SSH Password', size=32),
                'reboot': fields.boolean('Reboot'),
                'uuid': fields.char('Uuid', size=36, help="128 bit"),
                'check_uuid': fields.boolean('Check'),
                'major': fields.integer('Major', size=36, help="0-65535"),
                'check_major': fields.boolean('Check'),
                'minor': fields.integer('Minor', help="0-65535"),
                'check_minor': fields.boolean('Check'),
                'accuracy': fields.integer('Proximity Accuracy adjust', help="0-255"),
                'check_accuracy': fields.boolean('Check'),
                'txpower': fields.selection([('0','+0 dBm'),('1','+4 dBm'),('2','-6 dBm'), ('3','-23 dBm')], 'Tx-power', select=True),
                'check_txpower': fields.boolean('Check'),
                #'pairing': fields.boolean('Pairing password 0xFFF6', help="0-999999"),
                'broadcasting_cycle': fields.integer('Broadcasting cycle  (100ms) ', help="1-255"),
                'check_broadcasting_cycle': fields.boolean('Check'),
                'serial_id': fields.char('Serial Id', size=4, help="0001-9999"),
                'check_serial_id': fields.boolean('Check'),
                #'reboot': fields.boolean('Reboot and pairing Id 0xFFF9', help="0-999999"),
                'password': fields.integer('Password', help="0-999999"),
                'check_password': fields.boolean('Check'),
                'state': fields.selection([('draft','Draft'), ('done','Done'), ('disable','Disable')], 'State', readonly=True, help="The state.", select=True),
                'beacons_scanned': fields.one2many('ibeacon.scanned', 'template_id','Beacons Scanned'),
                }
    _defaults = {
                'state': 'draft',
                'uuid':'e2c56db5dffb48d2b060d0f5a71096e0',
                'password':987123,
                'accuracy':198,
                'broadcasting_cycle': 9,
                'serial_id': '3714',
                'txpower':'0'
                }
    
    # battery level uuid:2a19 hnd:0x0025
    # reboot and pairing uuid:ffff hnd:0x004b
    # pairing uuid:fff6 hnd:0x0042 change password
    
    session = {}
    
    def lescan_hci(self, timeout=5):
        status = []
        try:
            order = 'sudo timeout ' + str(timeout) + ' hcitool lescan'
            self.session.sendline(order)
            self.session.prompt()         # match the prompt
            status.append(self.session.before.split("\r\n"))     # print everything before the prompt.
        except:
            status.append("hcitool lescan Failed")
        return status
        
    def restart_hci(self,timeout=1):
        status = []
        try:
            order = 'sudo timeout '+ str(timeout) + ' hciconfig hci0 down'
            self.session.sendline(order)
            self.session.prompt()      
            
            order = 'sudo hciconfig hci0 up'
            self.session.sendline(order)
            self.session.prompt()     
            #status.append("hci restart Ok")
        except:
            status.append("hci restart Failed")
        return status
 
    def gatttool_connect(self, bluetooth_adr, timeout=1):
        status = []
        try:
            order ='sudo gatttool -t random --interactive'
            self.session.sendline(order)
            order = 'connect '+  bluetooth_adr
            self.session.sendline(order)
            #self.session.prompt()       
            #status.append(self.session.before.split("\r\n"))
        except:
            status.append("gatttool connect Failed")
        return status
        
    def gatttol_disconnect(self):
        status = []
        try:
            order ='disconnect'  
            self.session.sendline(order)
            #self.session.prompt()   
            order ='exit'  
            self.session.sendline(order)
            #self.session.prompt()       
            #status.append(self.session.before.split("\r\n")) 
        except:
            status.append("gatttool disconnect Failed")
        return status
                  
    
    def gatttool_read_uuid(self, mac, uuid, timeout=1):
        status = []
        try:
            order = 'char-read-uuid ' + uuid 
            self.session.sendline(order)
            self.session.prompt()       
            status.append(self.session.before.split("\r\n"))
        except:
            status.append("gatttool read Failed")
        return status 
    
    def gatttool_write(self, mac, hnd, value, timeout=500):
        status = []
        try:
            for i in range(1,5):
                order = 'sudo timeout '+ str(timeout) +' gatttool -b ' + mac + ' --char-write-req -a ' + hnd + ' -n '+ value 
                self.session.sendline(order)
                self.session.prompt()
                response = self.session.before
                if response.find("failed")==-1 and response.find("error")==-1:
                    pattern = "Characteristic value/descriptor:"
                    
                    sizePattern = len(pattern)
                    responseBegin = response.find("Characteristic value/descriptor:") + sizePattern + 1
                    responseFormatted = response[responseBegin:-3]
                    #status.append("gatttool read Ok")
                    return responseFormatted
                
        except:
            status.append("gatttool write Failed")
        return status  
    
    def gatttool_read(self, mac, hnd, timeout=500):
        status = []
        try:
            for i in range(1,5):
                order = 'sudo timeout '+ str(timeout) +' gatttool -b ' + mac + ' --char-read -a ' + hnd #+ ' > output'
                self.session.sendline(order)
                self.session.prompt()
                response = self.session.before
                if response.find("failed")==-1 and response.find("error")==-1:
                    pattern = "Characteristic value/descriptor:"
                    
                    sizePattern = len(pattern)
                    responseBegin = response.find("Characteristic value/descriptor:") + sizePattern + 1
                    responseFormatted = response[responseBegin:-3]
                    #status.append("gatttool read Ok")
                    return responseFormatted
                
        except:
            status.append("gatttool read Failed")
        return status  
 
     
    def ssh_login(self, cr, uid, ids, context=None): 
        self.session = pxssh.pxssh()
        #login(server, username, password='', terminal_type='ansi', original_prompt='[#$]', 
        #login_timeout=10, port=None, auto_prompt_reset=True, ssh_key=None, quiet=True, 
        #sync_multiplier=1, check_local_ip=True)[source]
        ibeacon_parameters = self.browse(cr, uid, ids[0], context=context)
        host = ibeacon_parameters.host
        user = ibeacon_parameters.ssh_user
        password = ibeacon_parameters.ssh_password
        status = []
        try:
            self.session.login(host, user, password=password)
            self.session.sendline ('uptime')
            self.session.prompt()         # match the prompt
            #status.append(self.session.before)     # print everything before the prompt.
            #status.append("SSH login Ok")
        except:
            status.append("SSH login Failed")
        return status
        
    def ssh_logout(self):
        status = []
        try:
            self.session.logout()
            #status.append("SSH logout Ok")
        except:
            status.append("SSH logout Failed")
        return status
                
    def ssh_scan(self, cr, uid, ids, context=None):
        status=[]
        status.append(self.ssh_login(cr, uid, ids, context=context))
        try: 
            status.append(self.restart_hci())
            
            result_lescan = self.lescan_hci()
            ibeacon_parameters = self.browse(cr, uid, ids[0], context=context)
            beacons_scanned = ibeacon_parameters.beacons_scanned
            status.append(self.create_scanned(cr, uid, ids[0], result_lescan[0], beacons_scanned, context)) 
            
            status.append(self.restart_hci())
        except:
            status.append("hci Failed")
            
        status.append(self.ssh_logout())
        return status
    
    def create_scanned(self, cr, uid, id, result, beacons_scanned,context=None):
        ibeacons = []
        ibeacons_mac = []
        for line in result:
            ibeacon=line.split(" ")
            if len(ibeacon[0])==17:
                if ibeacon[0] not in ibeacons_mac:
                    ibeacons.append(ibeacon)
                    ibeacons_mac.append(ibeacon[0])
                else:
                    if ibeacon[1] != "(unknown)":
                        ibeacons[ibeacons_mac.index(ibeacon[0])][1] = ibeacon[1]
                        
                            
        obj = self.pool.get('ibeacon.scanned')
        
        scanneds = []
        for scanned in beacons_scanned: #los beacons en base de datos
            scanneds.append(scanned.mac)
            obj_id = obj.search(cr, uid, [('template_id', '=', id),('mac', 'like', scanned.mac)] , limit=None, context=context)
            if len(obj_id)>0:
                obj.write(cr, uid, obj_id, {
                                        'enable': False,
                                    }, context=context)
        status = []
        for ibeacon in ibeacons:
            try:
                if ibeacon[0] not in scanneds:
                    obj.create(cr, uid, {
                                'mac':ibeacon[0],
                                'name':ibeacon[1],
                                #'write_date': datetime.date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                'template_id':id,
                                'enable': True
                            })
                else:
                    obj_id = obj.search(cr, uid, [('template_id', '=', id),('mac', 'like', ibeacon[0])] , limit=None, context=context)
                    obj_browse = obj.browse(cr, uid, obj_id[0], context=context)
                    if obj_browse.name != ibeacon[1]:
                        obj.write(cr, uid, obj_id, {
                                    'name':ibeacon[1],
                                    'enable': True,
                                }, context=context)
                    else:
                        obj.write(cr, uid, obj_id, {
                                    'enable': True,
                                    }, context=context)
            except:
                status.append("Failed " + ibeacon)
        return status
    
    
    def action_scan(self, cr, uid, ids, context=None):
        status = self.ssh_scan(cr, uid, ids, context)
        for line in status:
            if line != []:
                return self.pool.get('warning_box').info(cr, uid, title='SSH Scan', message=status)  
        
    def action_workflow_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'draft' }, context=context)
        return True
    
    def action_workflow_done(self, cr, uid, ids, context=None):
        
        self.action_scan( cr, uid, ids,context)
        self.write(cr, uid, ids, { 'state' : 'done' }, context=context)
        return True
    
    def action_workflow_disable(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'disable' }, context=context)
        return True
    
    
    
        