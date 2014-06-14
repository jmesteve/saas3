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

class beacon_estimated(osv.osv_memory):
    
    _name = 'beacon.estimated.distance'
        
    _columns = {
                'rssi': fields.integer('RSSI'),
                'txpower': fields.selection([('0','+0 dBm'),('1','+4 dBm'),('2','-6 dBm'), ('3','-23 dBm')], 'Tx-power', select=True),
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
       
        cr.execute('''SELECT rssi, minor, beacon.x, beacon.y, 2.5 z, point_id, beacon_point.x as point_x, beacon_point.y as point_y, beacon_point.z as point_z, accuracy, beacon_test.txpower, test
                        FROM beacon
                        JOIN beacon_point ON (beacon.point_id = beacon_point.id)
                        JOIN beacon_test ON (beacon.test = beacon_test.id);''')
        
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
            accuracy = item[9]
            txPower = item[10]
            
            key = str(rssi)

            d = accuracy
            
            if txPower not in totalsReal:
                totalsReal[txPower] = {}
                distancesReal[txPower] = {}
                count[txPower] = {}
            
            if key in totalsReal[txPower]:
                totalsReal[txPower][key] += d
                distancesReal[txPower][key].append(d)
                count[txPower][key] += 1
            else:
                totalsReal[txPower][key] = d
                distancesReal[txPower][key] = [d]
                count[txPower][key] = 1
        
        resultsReal = {}
        for txPower in totalsReal:
            resultsReal[txPower] = {x:float(totalsReal[txPower][x])/count[txPower][x] for x in totalsReal[txPower]}
            if '-100' in resultsReal[txPower]: del resultsReal[txPower]['-100']
    
        #resultsReal = {x:float(totalsReal[x])/count[x] for x in totalsReal}
        #if '-100' in resultsReal: del resultsReal['-100']

        for txPower in resultsReal:
            for key in sorted(resultsReal[txPower]):
                
                distances = sorted(distancesReal[txPower][key])
                
                size = len(distances)
                start = int(size*0.1)
                end = (size-start)
                distances = distances[start:end]
                
                minimo = distances[0]
                median = resultsReal[txPower][key]
                maximo = distances[-1]
                
                self.create(cr, uid, {'rssi': int(key),
                                      'txpower': str(txPower),
                                      'min': minimo,
                                      'median': median,
                                      'max': maximo,
                                      }, context)
        
        #finally return view    
        return {
            'view_type': 'form',
            'view_mode': 'tree,form,graph',
            'res_model': 'beacon.estimated.distance',
            'type': 'ir.actions.act_window',
            'context': context,
            'nodestroy': True,
         }
                
class beacon_distance(osv.osv_memory):
    
    _name = 'beacon.real.distance'
        
    _columns = {
                'rssi': fields.integer('RSSI'),
                'txpower': fields.selection([('0','+0 dBm'),('1','+4 dBm'),('2','-6 dBm'), ('3','-23 dBm')], 'Tx-power', select=True),
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
       
        cr.execute('''SELECT rssi, minor, beacon.x, beacon.y, 2.5 z, point_id, beacon_point.x as point_x, beacon_point.y as point_y, beacon_point.z as point_z, accuracy, beacon_test.txpower, test
                        FROM beacon
                        JOIN beacon_point ON (beacon.point_id = beacon_point.id)
                        JOIN beacon_test ON (beacon.test = beacon_test.id);''')
        
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
            accuracy = item[9]
            txPower = item[10]
            
            if txPower not in totalsReal:
                totalsReal[txPower] = {}
                distancesReal[txPower] = {}
                count[txPower] = {}
                
            key = str(rssi)

            dx = abs(beacon_x - punto_x)
            dy = abs(beacon_y - punto_y)
            dz = abs(beacon_z - punto_z)
            d = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if key in totalsReal[txPower]:
                totalsReal[txPower][key] += d
                distancesReal[txPower][key].append(d)
                count[txPower][key] += 1
            else:
                totalsReal[txPower][key] = d
                distancesReal[txPower][key] = [d]
                count[txPower][key] = 1
                    
        resultsReal = {}
        for txPower in totalsReal:
            resultsReal[txPower] = {x:float(totalsReal[txPower][x])/float(count[txPower][x]) for x in totalsReal[txPower]}
            if '-100' in resultsReal[txPower]: del resultsReal[txPower]['-100']
        
        for txPower in resultsReal:
            for key in sorted(resultsReal[txPower]):
                
                distances = sorted(distancesReal[txPower][key])
                
                size = len(distances)
                start = int(size*0.1)
                end = (size-start)
                distances = distances[start:end]
                
                minimo = float(distances[0])
                median = float(resultsReal[txPower][key])
                maximo = float(distances[-1])
                
                self.create(cr, uid, {'rssi': int(key),
                                      'txpower': str(txPower),
                                      'min': minimo,
                                      'median': median,
                                      'max': maximo,
                                      }, context)
        
        #finally return view    
        return {
            'view_type': 'form',
            'view_mode': 'tree,form,graph',
            'res_model': 'beacon.real.distance',
            'type': 'ir.actions.act_window',
            'context': context,
            'nodestroy': True,
         }
        
    
    class beacon_triangulation(osv.osv_memory):
    
        _name = 'beacon.triangulation.error'
            
        _columns = {
                    'txpower': fields.selection([('0','+0 dBm'),('1','+4 dBm'),('2','-6 dBm'), ('3','-23 dBm')], 'Tx-power', select=True),
                    'test': fields.char('Test', size=64),
                    'min': fields.float('Min'),
                    'median': fields.float('Median'),
                    'max': fields.float('Max')
                    }
        
        def generate_query(self, cr, uid, context=None):
            
            #first empty entity
            ids = self.search(cr, uid, [],context = context)
            self.unlink(cr, uid, ids, context = context)
            
            cr.execute('''SELECT rssi, minor, beacon.x, beacon.y, 2.5 z, point_id, beacon_point.x as point_x, beacon_point.y as point_y, beacon_point.z as point_z, accuracy, beacon_test.txpower, test
                            FROM beacon
                            JOIN beacon_point ON (beacon.point_id = beacon_point.id)
                            JOIN beacon_test ON (beacon.test = beacon_test.id);''')
            
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
                accuracy = item[9]
                txPower = item[10]
                
                if txPower not in totalsReal:
                    totalsReal[txPower] = {}
                    distancesReal[txPower] = {}
                    count[txPower] = {}
                    
                key = str(rssi)
    
                dx = abs(beacon_x - punto_x)
                dy = abs(beacon_y - punto_y)
                dz = abs(beacon_z - punto_z)
                d = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if key in totalsReal[txPower]:
                    totalsReal[txPower][key] += d
                    distancesReal[txPower][key].append(d)
                    count[txPower][key] += 1
                else:
                    totalsReal[txPower][key] = d
                    distancesReal[txPower][key] = [d]
                    count[txPower][key] = 1
                        
            resultsReal = {}
            for txPower in totalsReal:
                resultsReal[txPower] = {x:float(totalsReal[txPower][x])/count[txPower][x] for x in totalsReal[txPower]}
                if '-100' in resultsReal[txPower]: del resultsReal[txPower]['-100']
        
            rssiData = {} 
            
            for txPower in resultsReal:
                rssiData[txPower] = {}
                for key in sorted(resultsReal[txPower]):
                    
                    distances = sorted(distancesReal[txPower][key])
                    
                    size = len(distances)
                    start = int(size*0.1)
                    end = (size-start)
                    distances = distances[start:end]
                    
                    minimo = distances[0]
                    median = resultsReal[txPower][key]
                    maximo = distances[-1]
                    
                    rssiData[txPower][key] = {}
                    rssiData[txPower][key]['median'] = median
                    rssiData[txPower][key]['min'] = minimo
                    rssiData[txPower][key]['max'] = maximo
        

            nBests = 3

            deviation = []
            totalDeviations = []
            
            cr.execute('''SELECT beacon_test.name, beacon_test.txpower, beacon_test.map, beacon_map.name as map_name, beacon_map.x as map_x, beacon_map.y as map_y, beacon_test.id
                            FROM beacon_test
                            JOIN beacon_map ON (beacon_test.map = beacon_map.id);''')
            listOfTests = cr.fetchall()
            
            for test in listOfTests:
                    
                deviation = []
                
                test_id = test[6]
                name = test[0]
                txPower = test[1]
                mapId = test[2]
                mapName = test[3]
                mapX = test[4]
                mapY = test[5]
                
                cr.execute('''SELECT id, x, y, z 
                                FROM beacon_point
                                WHERE beacon_point.test_id = {id};'''.format(id = test_id))
                listOfPoints = cr.fetchall()
            
                for punto in listOfPoints:
            
                    punto_id = punto[0]
                    x = punto[1]
                    y = punto[2]
                    z = punto[3]
                    
                    maxWeight = 0
            
                    rssiMedians = {}
                    countMedians = {}
                    wildcards = {}
            
                    cr.execute('''SELECT id, minor, rssi FROM beacon WHERE beacon.point_id = {id};'''.format(id = punto_id))
                    listOfBeacons = cr.fetchall()
                 
                    for beacon in listOfBeacons:
                        
                        beacon_id = beacon[0]
                        minor = beacon[1]
                        rssi = beacon[2]
                               
                        key = str(minor)
                        rssi = int(rssi)
                        if key not in wildcards:
                            wildcards[key] = True
             
                        if rssi == -100 and wildcards[key] == True:
                            wildcards[key] = False
                        elif key in rssiMedians:
                            rssiMedians[key] += rssi
                            countMedians[key] += 1
                            wildcards[key] = True
                        else:
                            rssiMedians[key] = rssi
                            countMedians[key] = 1
                            wildcards[key] = True
                            
                    rssiMedians = {x:float(rssiMedians[x])/countMedians[x] for x in rssiMedians}
             
                    # Creamos lista ordenada de tuplas (minor, rssiMedio)
                    rssiMediansSorted = sorted(rssiMedians.items(), key=lambda x:x[1])
                    # Damos la vuelta para ordenarlas de mejor (mayor) a peor (menor)
                    rssiMediansSorted = rssiMediansSorted[::-1]
             
                    weights = []
                    beacons = []
                    for beaconPair in rssiMediansSorted[0:nBests]:

                        cr.execute('''SELECT * FROM beacon WHERE beacon.minor = {minor};'''.format(minor = int(beaconPair[0])))
                        beacon = cr.dictfetchone()
                        #beacon = findBeaconInMap(mapObject, int(beaconPair[0]))

                        if beacon is not None:
             
                            key = str(int(beaconPair[1]))
             
                            try:
                                if key in rssiData[txPower]:
                                    media = rssiData[txPower][key]['median']
                                else:
                                    media = 10
             
                            except Exception, e:
                                print beaconPair, rssiMediansSorted
             
                            weight = float(1/(math.pow(media, 5)))
             
                            weights.append(weight)
                            beacons.append(beacon)
                            
                    xTotal = 0
                    yTotal = 0
                    zTotal = 0
                    for index, bestBeacon in enumerate(beacons):
                        xTotal += float(bestBeacon['x']) * weights[index]
                        yTotal += float(bestBeacon['y']) * weights[index]
                        zTotal += float(2.5 * weights[index])
                         
                    total = sum(weights)
                    if total > 0:
                        estimatedPosition = (xTotal/total, yTotal/total, zTotal/total)
             
                        dx = abs(float(x) - float(estimatedPosition[0]))
                        dy = abs(float(y) - float(estimatedPosition[1]))
                             
                        dz = abs(2.5 - float(estimatedPosition[2]))
                        d = math.sqrt(dx*dx + dy*dy + dz*dz)
                             
                        deviation.append(d)
                        totalDeviations.append(d)
             
                self.create(cr, uid, {'txpower': str(txPower),
                                        'test': name,
                                        'min': min(deviation),
                                        'median': (sum(deviation)/len(deviation)),
                                        'max': max(deviation),
                                        }, context)

            #finally return view    
            return {
                'view_type': 'form',
                'view_mode': 'tree,form,graph',
                'res_model': 'beacon.triangulation.error',
                'type': 'ir.actions.act_window',
                'context': context,
                'nodestroy': True,
             }
    
      
    
