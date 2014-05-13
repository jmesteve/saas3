from openerp.osv import fields,osv

class beacon_test(osv.osv):
    _name = 'beacon.test'
    
    _columns = {
                'name': fields.char('name', size=250),
                'frecuency': fields.integer('Frecuency'),
                'txpower': fields.selection([('0','+0 dBm'),('1','+4 dBm'),('2','-6 dBm'), ('3','-23 dBm')], 'Tx-power', select=True),
                'map': fields.many2one('beacon.map', 'Map id', select=1),
                'points': fields.one2many('beacon.point', 'test_id','Points'),
                }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique per Test!'),
    ]
    


class beacon_point(osv.osv):
    _name = 'beacon.point'
    
    _columns = {
                'x': fields.float('x'),
                'y': fields.float('y'),
                'z': fields.float('z'),
                'magneticheading': fields.float('Magnetic Heading'),
                'trueHeading': fields.float('True Heading'),
                'closest': fields.integer('Minor Near'),
                'test_id': fields.many2one('beacon.test', 'Test id', select=1, ondelete="cascade"),
                'beacons': fields.one2many('beacon', 'point_id','Beacons'),
                }


class beacon(osv.osv):
    _name = 'beacon'
    
    _columns = {'sample':fields.integer('sample'),
                'major': fields.integer('Major'),
                'minor': fields.integer('Minor'),
                'uuid': fields.char('Uuid', size=36),
                'accuracy': fields.float('Accuracy'),
                'rssi': fields.integer('Rssi'),
                'proximity': fields.selection([('0','unknow'),('1','inmediate'),('2','near'), ('3','far')], 'Proximity', select=True),
                'point_id': fields.many2one('beacon.point', 'Point id', select=1, ondelete="cascade"),
                }
    _order = "sample, rssi"
   
   