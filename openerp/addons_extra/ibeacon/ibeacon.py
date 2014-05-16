from openerp.osv import fields,osv
    
class beacon_test(osv.osv):
    _name = 'beacon.test'
    
    _columns = {
                'name': fields.char('name', size=250),
                'frecuency': fields.integer('Frecuency'),
                'txpower': fields.selection([('0','+0 dBm'),('1','+4 dBm'),('2','-6 dBm'), ('3','-23 dBm')], 'Tx-power', select=True),
                'map': fields.many2one('beacon.map', 'Map id', select=1),
                'image_map': fields.binary('Image map'),
                'points': fields.one2many('beacon.point', 'test_id','Points'),
                }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique per Test!'),
    ]
    
class beacon_point(osv.osv):
    _name = 'beacon.point'
    
    def _medians(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for point in ids:
            res[point] = self.pool.get('beacon').search(cr, uid, [('point_id','=', point)], context=context)
        return res
    
    def _medians_inv(self, cr, uid, field, arg, context=None):
        return True
    
    _columns = {'point':fields.integer('Point',group_operator="count"),
                'x': fields.float('x'),
                'y': fields.float('y'),
                'z': fields.float('z'),
                'magneticheading': fields.float('Magnetic Heading'),
                'trueHeading': fields.float('True Heading'),
                'closest': fields.integer('Minor Near'),
                'test_id': fields.many2one('beacon.test', 'Test id', select=1, ondelete="cascade"),
                'beacons': fields.one2many('beacon', 'point_id','Beacons'),
                'medians': fields.function(_medians,
                                           funct_inv=_medians_inv,
                                           type='one2many',
                                           obj='beacon', 
                                           string='Medians'),
                }

    def action_beacon_form(self, cr, uid, ids, context=None):
        mod_obj =self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid, 'ibeacon', 'beacon_search_form_view')
        id = result and result[1] or False
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_id': ids[0],
            'res_model': 'beacon',
            'type': 'ir.actions.act_window',
            'context': context,
            'target':'current',
            'nodestroy': True,
            'domain':[('point_id','=',ids[0])],
            'search_view_id': id,
         }


class beacon(osv.osv):
    _name = 'beacon'
    
    _columns = {'sample':fields.integer('sample',group_operator="max"),
                'major': fields.integer('Major',group_operator="max"),
                'minor': fields.integer('Minor',group_operator="max"), #['avg', 'max', 'min', 'sum', 'count']
                'uuid': fields.char('Uuid', size=36),
                'accuracy': fields.float('Accuracy', group_operator="avg"),
                'rssi': fields.integer('Rssi', group_operator="avg"),
                'proximity': fields.selection([('0','unknow'),('1','inmediate'),('2','near'), ('3','far')], 'Proximity',  select=True),
                'point_id': fields.many2one('beacon.point', 'Point id', select=1, ondelete="cascade"),
                'point': fields.related('point_id', 'point', type='integer', string='Point', store=True),
                'test': fields.related('point_id', 'test_id', type='many2one', relation='beacon.test', string='Test', store=True),
                'closest': fields.related('point_id', 'closest', type='integer', string='Minor Near', store=True, group_operator="max"),
                'x': fields.related('point_id', 'x', type='float',digits=(12,1), string='x', store=True, group_operator="ava"),
                'y': fields.related('point_id', 'y', type='float',digits=(12,1), string='y', store=True, group_operator="ava"),
                }
    _order = "test, point, sample, rssi desc, accuracy"
   
   