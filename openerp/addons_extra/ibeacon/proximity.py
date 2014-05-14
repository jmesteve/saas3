from openerp.osv import fields,osv


class beacon_proximity(osv.osv):
    _name = 'beacon.proximity.bounds'
    
    def _min_near(self, cr, uid, ids, name, arg, context=None):
        cr.execute('''SELECT min(accuracy) FROM beacon WHERE proximity LIKE '1';''')
        mins = cr.fetchall()[0]
        res = {}
        for id in ids:
            res[id] = mins[0]
        return res
    
    def _max_near(self, cr, uid, ids, name, arg, context=None):
        cr.execute('''SELECT max(accuracy) FROM beacon WHERE proximity LIKE '1';''')
        mins = cr.fetchall()[0]
        res = {}
        for id in ids:
            res[id] = mins[0]
        return res
        
    _columns = {
                'min_near': fields.function(_min_near,
                                                 type='float',
                                                 string='Min. Near'),
                'max_near': fields.function(_max_near,
                                                 type='float',
                                                 string='Max. Near'),
                }
    
    
    