from openerp.osv import fields,osv

import math

class beacon_proximity(osv.osv_memory):
    
    _name = 'beacon.proximity.bounds'
        
    _columns = {
                'test': fields.many2one('beacon.test', 'Test', select=1, ondelete="cascade"),
                #'proximity': fields.integer('Proximity'),
                'proximity': fields.selection([('0','unknow'),('1','inmediate'),('2','near'), ('3','far')], 'Proximity',  select=True),
                'tipo': fields.char('Tipo', size=12),
                'value': fields.float('Value'),
                }
    
    _order = "test,proximity"
    
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
        
        #third insert data in database
        for item in data:
            self.create(cr, uid, {
                                  'test': item[0],
                                  'proximity': item[1],
                                  'tipo': 'min',
                                  'value': item[2],
                                  }, context)
            self.create(cr, uid, {
                                  'test': item[0],
                                  'proximity': item[1],
                                  'tipo': 'max',
                                  'value': item[3],
                                  }, context)
        
        #finally return view    
        return {
            'view_type': 'form',
            'view_mode': 'tree,form,graph',
            #'search_view_id': 'proximity_search_form_view',
            'res_model': 'beacon.proximity.bounds',
            'type': 'ir.actions.act_window',
            'context': context,
            'nodestroy': True,
         }
        
class beacon_distance(osv.osv_memory):
    
    _name = 'beacon.real.distance'
        
    _columns = {
                'rssi': fields.integer('RSSI'),
                'min': fields.float('Min'),
                'median': fields.float('Median'),
                'max': fields.float('Max')
                }
    
    _order = "rssi"
    
    def generate_query(self, cr, uid, context=None):
        
        #first empty entity
        ids = self.search(cr, uid, [],context = context)
        self.unlink(cr, uid, ids, context = context)
        
        #second obtain data with SQL
        obj = self.pool.get('beacon')
       
        cr.execute('''SELECT rssi, minor, beacon.x, beacon.y, 2.5 z, point_id, beacon_point.x as point_x, beacon_point.y as point_y, beacon_point.z as point_z, test
                        FROM beacon
                        JOIN beacon_point ON (beacon.point_id = beacon_point.id);''')
        
        data = cr.fetchall()

        totalsReal = dict()
        distancesReal = dict()
        count = dict()

        for item in data:
            
            rssi = item[0]
            beacon_x = item[2]
            beacon_y = item[3]
            beacon_z = item[4]
            punto_x = item[6]
            punto_y = item[7]
            punto_z = item[8]
            
            key = str(rssi)

            dx = abs(beacon_x - punto_x)
            dy = abs(beacon_y - punto_y)
            dz = abs(beacon_z - punto_z)
            d = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if key in totalsReal:
                totalsReal[key] += d
                distancesReal[key].append(d)
                count[key] += 1
            else:
                totalsReal[key] = d
                distancesReal[key] = [d]
                count[key] = 1
                    
        resultsReal = {x:float(totalsReal[x])/count[x] for x in totalsReal}
        if '-100' in resultsReal: del resultsReal['-100']

        #print totalsReal
        #print count
        #print resultsReal
        
        for key in sorted(resultsReal):
            
            distances = sorted(distancesReal[key])
            
            print distances
            
            size = len(distances)
            start = int(size*0.1)
            end = (size-start)
            distances = distances[start:end]
            
            minimo = distances[0]
            median = resultsReal[key]
            maximo = distances[-1]
            
            self.create(cr, uid, {'rssi': int(key),
                                  'min': minimo,
                                  'median': median,
                                  'max': maximo,
                                  }, context)
        
        #finally return view    
        return {
            'view_type': 'form',
            'view_mode': 'tree,form,graph',
            #'search_view_id': 'proximity_search_form_view',
            'res_model': 'beacon.real.distance',
            'type': 'ir.actions.act_window',
            'context': context,
            'nodestroy': True,
         }
    
      
    