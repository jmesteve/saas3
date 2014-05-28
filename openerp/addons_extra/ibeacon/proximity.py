from openerp.osv import fields,osv


class beacon_proximity(osv.osv_memory):
    
    _name = 'beacon.proximity.bounds'
        
    _columns = {
                'test': fields.many2one('beacon.test', 'Test', select=1, ondelete="cascade"),
                'proximity': fields.integer('Proximity'),
                'min': fields.float('Min'),
                'max': fields.float('Max'),
                }
    
    _order = "proximity"
    
    def generate_query(self, cr, uid, context=None):
        
        #first empty entity
        ids = self.search(cr, uid, [],context = context)
        self.unlink(cr, uid, ids, context = context)
        
        #second obtain data with SQL
        obj = self.pool.get('beacon')
       
        cr.execute('''SELECT test, proximity, min(accuracy), max(accuracy) 
            FROM beacon
            WHERE proximity != '0'
            GROUP BY test, proximity
            ORDER BY test, proximity;''')
        
        data = cr.fetchall()
        res = {}
        
        #third insert data in database
        count = 0
        for item in data:
            res[count] = {
                     'test': item[0],
                     'proximity': item[1],
                     'min': item[2],
                     'max': item[3],
                    }
            count = count + 1
            self.create(cr, uid, {
                                  'test': item[0],
                                  'proximity': item[1],
                                  'min': item[2],
                                  'max': item[3],
                                  }, context)
        
        #finally return view    
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'beacon.proximity.bounds',
            'type': 'ir.actions.act_window',
            'context': context,
            'nodestroy': True,
         }
    
      
    