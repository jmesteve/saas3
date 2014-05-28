from openerp.osv import fields,osv


class beacon_proximity(osv.osv_memory):
    
    _name = 'beacon.proximity.bounds'
    
#     def _calculate(self, cr, ids, query):
#         cr.execute(query)
#         mins = cr.fetchall()[0]
#         res = {}
#         for id in ids:
#             res[id] = mins[0]
#         return res
#   
#     def _min_inm(self, cr, uid, ids, name, arg, context=None):
#         return self._calculate( cr, ids, '''SELECT min(accuracy) FROM beacon WHERE proximity LIKE '1' GROUP BY test;''')
#     
#     def _max_inm(self, cr, uid, ids, name, arg, context=None):
#         return self._calculate( cr, ids, '''SELECT max(accuracy) FROM beacon WHERE proximity LIKE '1' GROUP BY test;''')
#     
#     def _min_near(self, cr, uid, ids, name, arg, context=None):
#         return self._calculate( cr, ids, '''SELECT min(accuracy) FROM beacon WHERE proximity LIKE '2' GROUP BY test;''')
#     
#     def _max_near(self, cr, uid, ids, name, arg, context=None):
#         return self._calculate( cr, ids, '''SELECT max(accuracy) FROM beacon WHERE proximity LIKE '2' GROUP BY test;''')
#     
#     def _min_far(self, cr, uid, ids, name, arg, context=None):
#         return self._calculate( cr, ids, '''SELECT min(accuracy) FROM beacon WHERE proximity LIKE '3' GROUP BY test;''')
#     
#     def _max_far(self, cr, uid, ids, name, arg, context=None):
#         return self._calculate( cr, ids, '''SELECT max(accuracy) FROM beacon WHERE proximity LIKE '3' GROUP BY test;''')
#     
    
    def default_get(self, cr, uid, fields, context=None):
        
        obj = self.pool.get('beacon')
        #res = super(payment_order_create, self).default_get(cr, uid, fields, context=context)
        
        cr.execute('''SELECT beacon_test.name, proximity, min(accuracy), max(accuracy) 
FROM beacon
JOIN beacon_test ON (beacon.test = beacon_test.id)
WHERE proximity != '0'
GROUP BY beacon_test.name, proximity
ORDER BY beacon_test.name, proximity;''')
        
        data = cr.fetchall()
        res = {}
        
        count = 0
        for item in data:
            res[count] = {
                     'test': item[0],
                     'proximity': item[1],
                     'min': item[2],
                     'max': item[3],
                    }
            count = count + 1
#             self.create(cr, uid, {
#                                   'test': item[0],
#                                   'proximity': item[1],
#                                   'min': item[2],
#                                   'max': item[3],
#                                   }, context)
            
        return res
    
        #ids = obj.search(cr, uid, [], limit=none, context=context)
        #for line in obj.browse(cr,uid, ids, context=context)
            
        
#         if 'entries' in fields:
#             if context and 'line_ids' in context and context['line_ids']:
#                 res.update({'entries':  context['line_ids']})
# 
#         return res
    
    _columns = {
                'test': fields.char('Test', size=128),
                'proximity': fields.integer('Proximity'),
                'min': fields.float('Min'),
                'max': fields.float('Max'),
                }
    
    
    