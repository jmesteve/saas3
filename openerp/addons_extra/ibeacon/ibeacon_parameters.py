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
                'txpower': fields.selection([('00','+0 dBm'),('01','+4 dBm'),('02','-6 dBm'), ('03','-23 dBm')], 'Tx-power  0xFFF5',type="char", size=2, select=True),
                'broadcasting_cycle': fields.integer('Broadcasting cycle 0xFFF7',help="1-255"),
                'serial_id': fields.integer('Serial Id 0xFFF8', help="0001-9999"),
                'template_id': fields.many2one('ibeacon.parameters', 'Template id', select=1, ondelete="cascade"),
                'active_beacon': fields.function(_status_ibeacon, type='boolean', string='active',store=True),
                'hnd_uuid': fields.char('hnd uuid', size=6),
                'hnd_major': fields.char('hnd major', size=6),
                'hnd_minor': fields.char('hnd minor', size=6),
                'hnd_accuracy': fields.char('hnd accuracy', size=6),
                'hnd_txpower': fields.char('hnd txpower', size=6),
                'hnd_broadcasting_cycle': fields.char('hnd broadcasting cycle', size=6),
                'hnd_serial_id': fields.char('hnd serial id', size=6),
                'hnd_password': fields.char('hnd password', size=6),
                'hnd_reboot': fields.char('hnd reboot', size=6),
                }
    
    _defaults = {
                'hnd_password': '0x0042',
                'hnd_reboot': '0x004b',
                }
    
    _order = "active_beacon desc, minor"
 
    def write_hnd(self, cr, uid, ids, checkall=False, context=None):
        status=[]
        try: 
            obj = self.pool.get('ibeacon.parameters')
            
            ibeacon_scanned = self.browse(cr, uid, ids[0], context=context)
            bluetooth_adr = ibeacon_scanned.mac
            template_id = ibeacon_scanned.template_id.id
            template = obj.browse(cr,uid,[template_id],context=context)
            
            handle = obj.hcitool_lecc(bluetooth_adr)
            
            hnd_uuid = ibeacon_scanned.hnd_uuid
            if hnd_uuid != False and checkall or template[0].check_uuid:
                uuid = obj.gatttool_write(bluetooth_adr, hnd_uuid.encode('ascii','ignore'), template[0].uuid)
                #status.append(uuid)
            hnd_major = ibeacon_scanned.hnd_major
            if hnd_major != False and checkall or template[0].check_major:
                major = format(template[0].major,'#06x')[2:]
                major = obj.gatttool_write(bluetooth_adr, hnd_major, major)
                #status.append(major)
            hnd_minor = ibeacon_scanned.hnd_minor
            if hnd_minor != False and checkall or template[0].check_minor:
                minor = format(template[0].minor,'#06x')[2:]
                minor = obj.gatttool_write(bluetooth_adr, hnd_minor, minor)
                #status.append(minor)
            hnd_accuracy = ibeacon_scanned.hnd_accuracy 
            if hnd_accuracy != False and checkall or template[0].check_accuracy:
                accuracy = format(template[0].accuracy,'#04x')[2:]
                accuracy = obj.gatttool_write(bluetooth_adr, hnd_accuracy, accuracy)
                #status.append(accuracy)
            hnd_txpower = ibeacon_scanned.hnd_txpower 
            if hnd_txpower != False and checkall or template[0].check_txpower:
                txpower = template[0].txpower
                txpower = obj.gatttool_write(bluetooth_adr, hnd_txpower, txpower)
                #status.append(txpower)
            hnd_password = ibeacon_scanned.hnd_password
            if hnd_password != False and checkall or template[0].check_password:
                password = format(template[0].password,'#08x')[2:]
                password = obj.gatttool_write(bluetooth_adr, hnd_password, password)
                #status.append(password)
            hnd_broadcasting_cycle = ibeacon_scanned.hnd_broadcasting_cycle
            if hnd_broadcasting_cycle != False and checkall or template[0].check_broadcasting_cycle:
                broadcasting_cycle =  format(template[0].broadcasting_cycle,'#04x')[2:]
                broadcasting_cycle = obj.gatttool_write(bluetooth_adr, hnd_broadcasting_cycle, broadcasting_cycle)
                #status.append(broadcasting_cycle)
            hnd_serial_id = ibeacon_scanned.hnd_serial_id
            if hnd_serial_id != False and checkall or template[0].check_serial_id:
                serial_id = format(template[0].serial_id,'#06x')[2:]
                serial_id = obj.gatttool_write(bluetooth_adr, hnd_serial_id, serial_id)
                #status.append(serial_id)
            hnd_password = ibeacon_scanned.hnd_reboot 
            if hnd_password != False and checkall or template[0].reboot:
                password = format(template[0].password,'#08x')[2:]
                reboot = obj.gatttool_write(bluetooth_adr, hnd_password, password)  #send the password   
                self.read_uuid(cr, uid, ids, checkall=False, context=context)
                
            obj.hcitool_ledc(handle)
           
        except:
            status.append("gatttool write Failed")
        
        return status
    
    def ssh_write(self, cr, uid, ids, checkall=False, context=None):
        status=[]
        obj = self.pool.get('ibeacon.parameters')
        obj_scanned = self.pool.get('ibeacon.scanned')
        ibeacon_scanned = self.browse(cr, uid, ids[0], context=context)
        template_id = ibeacon_scanned.template_id.id
        status.append(obj.ssh_login(cr, uid, [template_id], context=context))
        status.append(obj_scanned.write_hnd(cr, uid, ids, checkall=checkall, context=context))    
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
            
            password = format(template[0].password,'#08x')[2:]
            hnd_password = ibeacon_scanned.hnd_reboot 
            reboot = obj.gatttool_write(bluetooth_adr, hnd_password, password)  #send the password
            status.append(reboot)
            
        except:
            status.append("gatttool reboot Failed")
            
        status.append(obj.ssh_logout())
        return status
    

            
        
    def read_uuid(self, cr, uid, ids, checkall=True, login=True, context=None):
        status=[]
        try: 
            obj = self.pool.get('ibeacon.parameters')
            obj_scanned = self.pool.get('ibeacon.scanned')
            ibeacon_scanned = obj_scanned.browse(cr, uid, ids[0], context=context)
            name = ibeacon_scanned.name
            if name == "(unknown)":
                status.append("ibeacon unknown")
                return status
            template = ibeacon_scanned.template_id
            bluetooth_adr = ibeacon_scanned.mac
                 
            handle = obj.hcitool_lecc(bluetooth_adr)
            
            object_beacon = {}
            if checkall:
                response = obj.gatttool_read_uuid(bluetooth_adr, '2a00')
                name_verify = binascii.unhexlify(''.join(response[0].split()))
            
            if checkall or template.check_uuid:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff1')
                uuid = response[0].replace(" ", "")
                #status.append(uuid)
                object_beacon['uuid'] = uuid
                object_beacon['hnd_uuid'] = response[1]
            
            if checkall or template.check_major:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff2')
                major = int(response[0].replace(" ", ""),16)
                #status.append(major)
                object_beacon['major'] = major
                object_beacon['hnd_major'] = response[1]
            
            if checkall or template.check_minor:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff3')
                minor = int(response[0].replace(" ", ""),16)
                #status.append(minor)
                object_beacon['minor'] = minor
                object_beacon['hnd_minor'] = response[1]
            
            if checkall or template.check_accuracy:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff4')
                accuracy = int(response[0].replace(" ", ""),16)
                #status.append(accuracy)
                object_beacon['accuracy'] = accuracy
                object_beacon['hnd_accuracy'] = response[1]
                
            if checkall or template.check_txpower:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff5')
                txpower = response[0].replace(" ", "")
                #status.append(txpower)
                object_beacon['txpower'] = txpower
                object_beacon['hnd_txpower'] = response[1]
            
            if checkall or template.check_broadcasting_cycle:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff7')
                broadcasting_cycle = int(response[0].replace(" ", ""),16)
                #status.append(broadcasting_cycle)
                object_beacon['broadcasting_cycle'] = broadcasting_cycle
                object_beacon['hnd_broadcasting_cycle'] = response[1]
                
            if checkall or template.check_serial_id:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff8')
                serial_id = int(response[0].replace(" ", ""),16)
                #status.append(serial_id)
                object_beacon['serial_id'] = serial_id
                object_beacon['hnd_serial_id'] = response[1]
                
            obj.hcitool_ledc(handle)
            
            object_beacon['validate']=True
            if object_beacon !={}:
                self.write(cr, uid, ids[0], object_beacon, context=context)
           
            
          
        except:
            self.write(cr, uid, ids[0], {'validate':False}, context=context)
            status.append("gatttool read Failed")
        return status
   
    
    def ssh_read_uuid(self, cr, uid, ids, checkall=True, context=None):
        status=[]
        obj = self.pool.get('ibeacon.parameters')
        obj_scanned = self.pool.get('ibeacon.scanned')
        ibeacon_scanned = obj_scanned.browse(cr, uid, ids[0], context=context)
        template = ibeacon_scanned.template_id
        template_id = template.id
        status.append(obj.ssh_login(cr, uid, [template_id], context=context))
        status.append(obj_scanned.read_uuid(cr, uid, ids, checkall=checkall, context=context))
        status.append(obj.ssh_logout())
        return status
        
    def action_read(self, cr, uid, ids, context=None):
        status = self.ssh_read_uuid(cr, uid, ids, context)
        for line in status:
            if line != []:
                return self.pool.get('warning_box').info(cr, uid, title='SSH Scan', message=status)  
            
    def action_write(self, cr, uid, ids, context=None):
        status = self.ssh_write(cr, uid, ids, context=context)
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
                
                'major': fields.integer('Major', help="0-65535"),
                'check_major': fields.boolean('Check'),
                
                'minor': fields.integer('Minor', help="0-65535"),
                'check_minor': fields.boolean('Check'),
                
                'accuracy': fields.integer('Proximity Accuracy adjust', help="0-255"),
                'check_accuracy': fields.boolean('Check'),
                
                'txpower': fields.selection([('00','+0 dBm'),('01','+4 dBm'),('02','-6 dBm'), ('03','-23 dBm')], 'Tx-power',type="char",size=2,  select=True),
                'check_txpower': fields.boolean('Check'),
                
                #'pairing': fields.boolean('Pairing password 0xFFF6', help="0-999999"),
                'broadcasting_cycle': fields.integer('Broadcasting cycle  (100ms) ', help="1-255"),
                'check_broadcasting_cycle': fields.boolean('Check'),
                
                'serial_id': fields.integer('Serial Id', help="0001-9999"),
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
                'txpower':'00'
                }
    
    # battery level uuid:2a19 hnd:0x0025
    # reboot and pairing uuid:ffff hnd:0x004b
    # pairing uuid:fff6 hnd:0x0042 change password
    
    session = {}
    
    def reboot_system(self, cr, uid, ids, context=None):
        status=[]
        try: 
            
            status.append(self.ssh_login(cr, uid, ids, context=context))
            
            order = 'sudo reboot'
            self.session.sendline(order)
            self.session.prompt()  
            
            status.append("reboot system Ok")
        except:
            status.append("reboot system Failes")
            
        status.append(self.ssh_logout())
        return status
    
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
                  
    
#     def gatttool_read_uuid(self, mac, uuid, timeout=1):
#         status = []
#         try:
#             order = 'char-read-uuid ' + uuid 
#             self.session.sendline(order)
#             self.session.prompt()       
#             status.append(self.session.before.split("\r\n"))
#         except:
#             status.append("gatttool read Failed")
#         return status 
#     
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
 
    def gatttool_read_uuid(self, mac, uuid, timeout=500):
        status = []
        try:
            for i in range(1,5):
                order = 'sudo timeout '+ str(timeout) +' gatttool -b ' + mac + ' --char-read -u ' + uuid
                self.session.sendline(order)
                self.session.prompt()
                response = self.session.before
                if response.find("failed")==-1 and response.find("error")==-1:
                    pattern = "value:"
                    sizePattern = len(pattern)
                    responseBegin = response.find(pattern) + sizePattern + 1
                    responseFormatted = response[responseBegin:-3]
                    
                    pattern_handle = "handle:"
                    sizePattern_handle = len(pattern_handle)
                    responseBegin_handle = response.find(pattern_handle) + sizePattern_handle + 1
                    responseEnd_handle = responseBegin_handle + 6
                    responseFormatted_handle = response[responseBegin_handle:responseEnd_handle]
                    #status.append("gatttool read Ok")
                    return [responseFormatted,responseFormatted_handle]
                
        except:
            status.append("gatttool read Failed")
        return status  
     
    def hcitool_lecc(self, bluetooth_adr, timeout=10):
        status=[]
        try:
            order = 'sudo timeout '+ str(timeout) +' hcitool lecc ' + bluetooth_adr
            self.session.sendline(order)
            self.session.prompt()
            response = self.session.before
            if response.find("failed")==-1 and response.find("error")==-1:
                pattern_handle = "handle"
                sizePattern_handle = len(pattern_handle)
                responseBegin_handle = response.find(pattern_handle) + sizePattern_handle + 1
                responseFormatted_handle = response[responseBegin_handle:-2]
                #status.append("gatttool read Ok")
                return responseFormatted_handle
        except:
            status.append("hci-tool lecc Failed")
        return status     
    
    def hcitool_ledc(self, handle):
        status=[]
        try:
            if handle==[] or handle.isdigit()==False:
                return status
            order = 'sudo hcitool ledc ' + handle
            self.session.sendline(order)
            self.session.prompt()
            #self.session.sendline ('uptime')
            #self.session.prompt()
            response = self.session.before
            status.append(response)
        except:
            status.append("hci-tool ledc Failed")
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
            
    def action_reboot(self, cr, uid, ids, context=None):
        status = self.reboot_system(cr, uid, ids, context)
        for line in status:
            if line != []:
                return self.pool.get('warning_box').info(cr, uid, title='Reboot System', message=status) 
            
    def action_restart(self, cr, uid, ids, context=None):
        status=[]
        status.append(self.ssh_login(cr, uid, ids, context=context))
        status.append(self.restart_hci())
        status.append(self.ssh_logout())  
        for line in status:
            if line != []:
                return self.pool.get('warning_box').info(cr, uid, title='Restart hci BLE', message=status) 
            
    def action_read_all(self, cr, uid, ids, context=None):
        obj = self.pool.get('ibeacon.scanned')
        obj_id = obj.search(cr, uid, [('template_id', '=', ids[0]),('active_beacon', '=', True)] , limit=None, context=context)
        #obj_browse = obj.browse(cr, uid, obj_id, context=context)
        status=[]
        status.append(self.ssh_login(cr, uid, ids, context=context))
        for id in obj_id:
            status.append(obj.read_uuid(cr, uid,[id], checkall=True, context=context))
            
        status.append(self.ssh_logout())
        
        for line in status:
            if line != []:
                return self.pool.get('warning_box').info(cr, uid, title='Reboot System', message=status) 
    def action_write_all(self, cr, uid, ids, context=None):
        obj = self.pool.get('ibeacon.scanned')
        obj_id = obj.search(cr, uid, [('template_id', '=', ids[0]),('active_beacon', '=', True)] , limit=None, context=context)
        #obj_browse = obj.browse(cr, uid, obj_id, context=context)
        status=[]
        status.append(self.ssh_login(cr, uid, ids, context=context))
        for id in obj_id:
            status.append(obj.write_hnd(cr, uid,[id], checkall=True, context=context))
            
        status.append(self.ssh_logout())
        
        for line in status:
            if line != []:
                return self.pool.get('warning_box').info(cr, uid, title='Reboot System', message=status) 
        
        
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
    
    
    
        