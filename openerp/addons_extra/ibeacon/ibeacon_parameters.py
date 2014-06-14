from openerp.osv import fields,osv
from openerp.tools.translate import _
import os, inspect, subprocess, shutil, signal
from pexpect import pxssh
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
                'battery': fields.integer('Battery 0x2A19',  help="0-100"),
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

    _order = "active_beacon desc, minor"
 
    def write_hnd(self, cr, uid, ids, checkall=False, context=None):
        try: 
            obj = self.pool.get('ibeacon.parameters')
            ibeacon_scanned = self.browse(cr, uid, ids[0], context=context)
            bluetooth_adr = ibeacon_scanned.mac
            template_id = ibeacon_scanned.template_id.id
            template = obj.browse(cr,uid,[template_id],context=context)
            
            hnd_uuid = ibeacon_scanned.hnd_uuid
            if hnd_uuid != False and checkall or template[0].check_uuid:
                uuid = obj.gatttool_write(bluetooth_adr, hnd_uuid.encode('ascii','ignore'), template[0].uuid)
            
            hnd_major = ibeacon_scanned.hnd_major
            if hnd_major != False and checkall or template[0].check_major:
                major = format(template[0].major,'#06x')[2:]
                major = obj.gatttool_write(bluetooth_adr, hnd_major, major)
            
            hnd_minor = ibeacon_scanned.hnd_minor
            if hnd_minor != False and checkall or template[0].check_minor:
                minor_value = template[0].minor
                if minor_value == 0:
                    minor = format(ibeacon_scanned.serial_id,'#06x')[2:]
                else:
                    minor = format(ibeacon_scanned.minor,'#06x')[2:]
                minor = obj.gatttool_write(bluetooth_adr, hnd_minor, minor)
            
            hnd_accuracy = ibeacon_scanned.hnd_accuracy 
            if hnd_accuracy != False and checkall or template[0].check_accuracy:
                accuracy = format(template[0].accuracy,'#04x')[2:]
                accuracy = obj.gatttool_write(bluetooth_adr, hnd_accuracy, accuracy)
            
            hnd_txpower = ibeacon_scanned.hnd_txpower 
            if hnd_txpower != False and checkall or template[0].check_txpower:
                txpower = template[0].txpower
                txpower = obj.gatttool_write(bluetooth_adr, hnd_txpower, txpower)
            
            hnd_password = ibeacon_scanned.hnd_password
            if hnd_password != False and checkall or template[0].check_password:
                password = format(template[0].password,'#08x')[2:]
                password = obj.gatttool_write(bluetooth_adr, hnd_password, password)
            
            hnd_broadcasting_cycle = ibeacon_scanned.hnd_broadcasting_cycle
            if hnd_broadcasting_cycle != False and checkall or template[0].check_broadcasting_cycle:
                broadcasting_cycle =  format(template[0].broadcasting_cycle,'#04x')[2:]
                broadcasting_cycle = obj.gatttool_write(bluetooth_adr, hnd_broadcasting_cycle, broadcasting_cycle)
            
            hnd_serial_id = ibeacon_scanned.hnd_serial_id
            if hnd_serial_id != False and checkall or template[0].check_serial_id:
                serial_id_value = template[0].serial_id
                if serial_id_value == 0:
                    serial_id = format(ibeacon_scanned.minor,'#06x')[2:]
                else:
                    serial_id = format(ibeacon_scanned.serial_id,'#06x')[2:]
                serial_id = obj.gatttool_write(bluetooth_adr, hnd_serial_id, serial_id)
            
            hnd_password = ibeacon_scanned.hnd_reboot 
            if hnd_password != False and checkall or template[0].reboot:
                password = format(template[0].password,'#08x')[2:]  #str(template[0].password)
                reboot = obj.gatttool_write(bluetooth_adr, hnd_password, password)  #send the password 
                
        except:
            raise osv.except_osv('Error','gatttool write Failed')
    
    def ssh_write(self, cr, uid, ids, checkall=False, context=None):
        try:
            obj = self.pool.get('ibeacon.parameters')
            obj_scanned = self.pool.get('ibeacon.scanned')
            ibeacon_scanned = self.browse(cr, uid, ids[0], context=context)
            template_id = ibeacon_scanned.template_id.id
            obj.ssh_login(cr, uid, [template_id], context=context)
            obj_scanned.write_hnd(cr, uid, ids, checkall=checkall, context=context) 
        except:
            raise osv.except_osv('Error','gatttool ssh write Failed')
        finally:
            obj.ssh_logout()
        
    
    def action_reboot(self, cr, uid, ids, context=None):
        try: 
            obj = self.pool.get('ibeacon.parameters')
            ibeacon_scanned = self.browse(cr, uid, ids[0], context=context)
            bluetooth_adr = ibeacon_scanned.mac
            template_id = ibeacon_scanned.template_id.id
            template = obj.browse(cr,uid,[template_id],context=context)
            obj.ssh_login(cr, uid, [template_id], context=context)
            password = format(template[0].password,'#08x')[2:] #str(template[0].password)
            hnd_password = ibeacon_scanned.hnd_reboot 
            obj.gatttool_write(bluetooth_adr, hnd_password, password)  #send the password
        except:
            raise osv.except_osv('Error','gatttool reboot Failed')
        finally:
            obj.ssh_logout()
        
    def read_uuid(self, cr, uid, ids, checkall=True, login=True, context=None):
        try: 
            obj = self.pool.get('ibeacon.parameters')
            obj_scanned = self.pool.get('ibeacon.scanned')
            ibeacon_scanned = obj_scanned.browse(cr, uid, ids[0], context=context)
            name = ibeacon_scanned.name
            if name == "(unknown)":
                return
            template = ibeacon_scanned.template_id
            bluetooth_adr = ibeacon_scanned.mac
                 
            handle = obj.hcitool_lecc(bluetooth_adr)
            
            object_beacon = {}
            
            char_desc = obj.gatttool_char_desc(bluetooth_adr)
            object_beacon['hnd_reboot'] = char_desc['ffff']
            object_beacon['hnd_password'] = char_desc['fff6']
            
            if checkall:
                #name verify
                response = obj.gatttool_read_uuid(bluetooth_adr, '2a00')
                name_verify = binascii.unhexlify(''.join(response[0].split()))
                #batterys state
                response = obj.gatttool_read_uuid(bluetooth_adr, '2a19')
                battery = int(response[0].replace(" ", ""),16)
                object_beacon['battery'] = battery
            
            if checkall or template.check_uuid:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff1')
                uuid = response[0].replace(" ", "")
                object_beacon['uuid'] = uuid
                object_beacon['hnd_uuid'] = response[1]
            
            if checkall or template.check_major:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff2')
                major = int(response[0].replace(" ", ""),16)
                object_beacon['major'] = major
                object_beacon['hnd_major'] = response[1]
            
            if checkall or template.check_minor:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff3')
                minor = int(response[0].replace(" ", ""),16)
                object_beacon['minor'] = minor
                object_beacon['hnd_minor'] = response[1]
            
            if checkall or template.check_accuracy:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff4')
                accuracy = int(response[0].replace(" ", ""),16)
                object_beacon['accuracy'] = accuracy
                object_beacon['hnd_accuracy'] = response[1]
                
            if checkall or template.check_txpower:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff5')
                txpower = response[0].replace(" ", "")
                object_beacon['txpower'] = txpower
                object_beacon['hnd_txpower'] = response[1]
            
            if checkall or template.check_broadcasting_cycle:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff7')
                broadcasting_cycle = int(response[0].replace(" ", ""),16)
                object_beacon['broadcasting_cycle'] = broadcasting_cycle
                object_beacon['hnd_broadcasting_cycle'] = response[1]
                
            if checkall or template.check_serial_id:
                response = obj.gatttool_read_uuid(bluetooth_adr, 'fff8')
                serial_id = int(response[0].replace(" ", ""),16)
                object_beacon['serial_id'] = serial_id
                object_beacon['hnd_serial_id'] = response[1]
                
            obj.hcitool_ledc(handle)
            
            object_beacon['validate']=True
            if object_beacon !={}:
                self.write(cr, uid, ids[0], object_beacon, context=context)
          
        except:
            self.write(cr, uid, ids[0], {'validate':False}, context=context)
            raise osv.except_osv('Error','gatttool read Failed')
    
    def ssh_read_uuid(self, cr, uid, ids, checkall=True, context=None):
        try:
            obj = self.pool.get('ibeacon.parameters')
            obj_scanned = self.pool.get('ibeacon.scanned')
            ibeacon_scanned = obj_scanned.browse(cr, uid, ids[0], context=context)
            template = ibeacon_scanned.template_id
            template_id = template.id
            obj.ssh_login(cr, uid, [template_id], context=context)
            obj_scanned.read_uuid(cr, uid, ids, checkall=checkall, context=context)
        except:
            raise osv.except_osv('Error','ssh read Failed')
        finally:
            obj.ssh_logout()
        
    def action_read(self, cr, uid, ids, context=None):
        self.ssh_read_uuid(cr, uid, ids, context)
            
    def action_write(self, cr, uid, ids, context=None):
        self.ssh_write(cr, uid, ids, context=context)
            
    def action_go_to_ibeacon_scanned(self, cr, uid, ids, context=None):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_id': ids[0],
            'res_model': 'ibeacon.scanned',
            'type': 'ir.actions.act_window',
            'context': context,
            'target':'current',
            'nodestroy': True,
            }

class ibeacon_parameters(osv.osv):
    _name = 'ibeacon.parameters'
    
    session = {}
 
    _columns = {'host': fields.char('Host', size=64),
                'ssh_port': fields.integer('SSH Port'),
                'ssh_user': fields.char('SSH User', size=32),
                'ssh_password': fields.char('SSH Password', size=32),
                
                'reboot': fields.boolean('Reboot'),
                
                #'progress': fields.float('Progress'),
                
                'uuid': fields.char('Uuid', size=36, help="128 bit"),
                'check_uuid': fields.boolean('Check'),
                
                'major': fields.integer('Major', help="0-65535"),
                'check_major': fields.boolean('Check'),
                
                'minor': fields.selection([('0','Serial Id'),('1','Value')], 'Minor 0xFFF3',type="char", size=1, select=True, help="0-65535"),
                'check_minor': fields.boolean('Check'),
                
                'accuracy': fields.integer('Proximity Accuracy adjust', help="0-255"),
                'check_accuracy': fields.boolean('Check'),
                
                'txpower': fields.selection([('00','+0 dBm'),('01','+4 dBm'),('02','-6 dBm'), ('03','-23 dBm')], 'Tx-power',type="char",size=2,  select=True),
                'check_txpower': fields.boolean('Check'),
                
                #'pairing': fields.boolean('Pairing password 0xFFF6', help="0-999999"),
                'broadcasting_cycle': fields.integer('Broadcasting cycle  (100ms) ', help="1-255"),
                'check_broadcasting_cycle': fields.boolean('Check'),
                
                'serial_id': fields.selection([('0','Minor'),('1','Value')], 'serial_id',type="char", size=1, select=True, help="1-9999"),
                'check_serial_id': fields.boolean('Check'),
                
                #'reboot': fields.boolean('Reboot and pairing Id 0xFFF9', help="0-999999"),
                'password': fields.integer('Password', help="0-999999"),
                'check_password': fields.boolean('Check'),
                
                'state': fields.selection([('draft','Draft'), ('done','Done'), ('disable','Disable')], 'State', readonly=True, help="The state.", select=True),
                'beacons_scanned': fields.one2many('ibeacon.scanned', 'template_id','Beacons Scanned'),
                }
    
    _defaults = {
                'ssh_port':22,
                'state': 'draft',
                'uuid':'e2c56db5dffb48d2b060d0f5a71096e0',
                'password':987123,
                'accuracy':198,
                'broadcasting_cycle': 9,
                'serial_id': '1',
                'minor': '0',
                'txpower':'00'
                }

    def validate(self, vals):
        try:
            status=[]
            if vals.get('major') and vals.get('major')<0 or vals.get('major')>65535:
                status.append('major value between 0 and 65535')
            #minor in lines scanned
            if vals.get('accuracy') and vals.get('accuracy')<0 or vals.get('accuracy')>255:
                status.append('accuracy value between 0 and 255')
            if vals.get('txpower') and (vals.get('txpower')==False or vals.get('txpower') not in ['00','01','02','03']):
                status.append('txpower selection error')
            if vals.get('password') and vals.get('password')<0 or vals.get('password')>999999:
                status.append('accuracy value between 0 and 999999')
            if vals.get('broadcasting_cycle') and vals.get('broadcasting_cycle')<1 or vals.get('broadcasting_cycle')>255:
                status.append('broadcasting_cycle value between 1 and 255')
            for line in status:
                if line != []:
                    raise osv.except_osv('Error', status)
            return status
        except:
            raise osv.except_osv('Error','validate fields')
   
    def write(self, cr, uid, ids, vals, context=None):
        self.validate(vals)
        return super(ibeacon_parameters, self).write(cr, uid, ids, vals, context=context)
    
    def create(self, cr, uid, vals, context=None):
        self.validate(vals)
        return super(ibeacon_parameters, self).create(cr, uid, vals, context=context)
    
    def reboot_system(self, cr, uid, ids, context=None):
        try: 
            self.ssh_login(cr, uid, ids, context=context)
            order = 'sudo reboot'
            self.session.sendline(order)
            self.session.prompt()  
        except:
            raise osv.except_osv('Error','reboot system Failed')
        finally:    
            self.ssh_logout()
    
    def lescan_hci(self, timeout=10):
        try:
            order = 'sudo timeout ' + str(timeout) + ' hcitool lescan'
            self.session.sendline(order)
            self.session.prompt()         # match the prompt
            response = self.session.before
            if response.find("failed")==-1 and response.find("error")==-1:
                return response.split("\r\n")
            raise osv.except_osv('Error','hcitool lescan error')
        except:
            raise osv.except_osv('Error','hcitool lescan Failed')
        
    def restart_hci(self):
        try:
            order = 'sudo hciconfig hci0 down'
            self.session.sendline(order)
            self.session.prompt()      
            
            order = 'sudo hciconfig hci0 up'
            self.session.sendline(order)
            self.session.prompt() 
        except:
            raise osv.except_osv('Error','hci restart Failed')
 
    def gatttool_write(self, mac, hnd, value, timeout=10):
        try:
            for i in range(1,3):
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
            return []
        except:
            raise osv.except_osv('Error','gatttool write Failed')

            
    def gatttool_read_uuid(self, mac, uuid, timeout=10):
        try:
            for i in range(1,3):
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
                    return [responseFormatted,responseFormatted_handle]
            return []
        except:
            raise osv.except_osv('Error','atttool read Failed')
    
    def gatttool_char_desc(self, mac, timeout=10):
        try:
            pattern_handle = "handle"
            sizePattern_handle = len(pattern_handle)
            result={}
            for i in range(1,3):
                order = 'sudo timeout '+ str(timeout) +' gatttool -b ' + mac + ' --char-desc'
                self.session.sendline(order)
                self.session.prompt()
                response = self.session.before
                if response.find("failed")==-1 and response.find("error")==-1:
                    response = response.splitlines();
                    for line in response:
                        line = line.split(',')
                        handle_pos = line[0].find(pattern_handle)
                        if handle_pos != -1:
                            handle_begin = handle_pos + sizePattern_handle +3
                            handle = line[0][handle_begin:]
                            uuid = line[1][12:16]
                            result[uuid] = handle
                    return result
            return result
        except:
            raise osv.except_osv('Error','gatttool char-desc Failed')
     
    def hcitool_lecc(self, bluetooth_adr, timeout=10):
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
                return responseFormatted_handle
            return []    
        except:
            raise osv.except_osv('Error','hci-tool lecc Failed')
        
    
    def hcitool_ledc(self, handle):
        try:
            if handle==[] or handle.isdigit()==False:
                return
            order = 'sudo hcitool ledc ' + handle
            self.session.sendline(order)
            self.session.prompt()
        except:
            raise osv.except_osv('Error','hci-tool ledc Failed')
        

    def ssh_login(self, cr, uid, ids, context=None): 
        try:
            self.session = pxssh.pxssh()
#login(server, username, password='', terminal_type='ansi', original_prompt='[#$]', 
#login_timeout=10, port=None, auto_prompt_reset=True, ssh_key=None, quiet=True, 
#sync_multiplier=1, check_local_ip=True)[source]
            ibeacon_parameters = self.browse(cr, uid, ids[0], context=context)
            host = ibeacon_parameters.host
            user = ibeacon_parameters.ssh_user
            password = ibeacon_parameters.ssh_password
            port = str(ibeacon_parameters.ssh_port)
            self.session.login(host, user, password=password, port=port)
            self.session.sendline ('uptime')
            self.session.prompt()   
        except:
            raise osv.except_osv('Error','SSH login Failed')
        
    def ssh_logout(self):
        try:
            self.session.logout()
        except:
            raise osv.except_osv('Error','SSH logout Failed')
    
#     def progress(self ,cr, uid, id, value, context=None):
#         object_beacon = {}
#         object_beacon['progress'] = value
#         self.write(cr, uid, id, object_beacon, context=context)
                
    def ssh_scan(self, cr, uid, ids, context=None):
        try: 
            self.ssh_login(cr, uid, ids, context=context)
            #self.restart_hci()
            result_lescan = self.lescan_hci()
            ibeacon_parameters = self.browse(cr, uid, ids[0], context=context)
            beacons_scanned = ibeacon_parameters.beacons_scanned
            self.create_scanned(cr, uid, ids[0], result_lescan, beacons_scanned, context)
            self.restart_hci()
        except:
            raise osv.except_osv('Error', 'ssh scan')
        finally:
            self.ssh_logout()
    
    def create_scanned(self, cr, uid, id, result, beacons_scanned,context=None):
        try:
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
            
            for ibeacon in ibeacons:
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
            raise osv.except_osv('Error', 'create scanned')
        
    
    def action_scan(self, cr, uid, ids, context=None):
        self.ssh_scan(cr, uid, ids, context)
            
    def action_reboot(self, cr, uid, ids, context=None):
        self.reboot_system(cr, uid, ids, context)
            
    def action_restart(self, cr, uid, ids, context=None):
        try:
            self.ssh_login(cr, uid, ids, context=context)
            self.restart_hci()
        except:
            raise osv.except_osv('Error','action Restart')
        finally:
            self.ssh_logout()
            
    def action_read_all(self, cr, uid, ids, context=None):
        try:
            obj = self.pool.get('ibeacon.scanned')
            obj_id = obj.search(cr, uid, [('template_id', '=', ids[0]),('active_beacon', '=', True)] , limit=None, context=context)
            self.ssh_login(cr, uid, ids, context=context)
            id = 0
            for id in obj_id:
                obj.read_uuid(cr, uid,[id], checkall=True, context=context)
        except:
            raise osv.except_osv(_('Error!'), _('Read all id:%s') % (str(id),))
        finally:
            self.ssh_logout()
       
    def action_write_all(self, cr, uid, ids, context=None):
        try:
            obj = self.pool.get('ibeacon.scanned')
            obj_id = obj.search(cr, uid, [('template_id', '=', ids[0]),('active_beacon', '=', True)] , limit=None, context=context)
            self.ssh_login(cr, uid, ids, context=context)
            id = 0
            for id in obj_id:
                obj.write_hnd(cr, uid,[id], checkall=False, context=context)
        except:
            raise osv.except_osv(_('Error!'), _('Write all id:%s') % (str(id),))
        finally:
            self.ssh_logout()
        
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

        