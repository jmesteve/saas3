from openerp.osv import fields,osv


class beacon_map(osv.osv):
    _name = 'beacon.map'
    
    _columns = {
                'name': fields.char('name', size=250),
                'file': fields.char('File', size=250),
                'x': fields.float('x'),
                'y': fields.float('y'),
                'z': fields.float('z'),
                'beacons': fields.one2many('beacon.map.beacons', 'map_id','Beacons'),
                }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique per Test!'),
    ]

class beacon_map_beacons(osv.osv):
    _name = 'beacon.map.beacons'
    
    _columns = {
                'uuid': fields.char('Uuid', size=16),
                'major': fields.char('Major',size=4),
                'minor': fields.integer('Minor',size=4),
                'x': fields.float('x'),
                'y': fields.float('y'),
                'z': fields.float('z'),
                'map_id': fields.many2one('beacon.map', 'Map id', select=1, ondelete="cascade"),
                } 
    
    