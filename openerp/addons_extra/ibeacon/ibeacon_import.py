from openerp.osv import fields,osv
import base64
import json

class ibeacon_import(osv.osv):
    _name = 'ibeacon.import'
    _columns = {
    'file_stream': fields.binary('File Stream', filters='*.json'), 
    'file_name': fields.char('File name',size=250),
    }
    
   
    def button_create_test(self, cr, uid, ids, context=None):
        map_obj = self.pool.get('beacon.map')
        map_beacons_obj = self.pool.get('beacon.map.beacons')
        import_obj = self.pool.get('ibeacon.import')
        test_obj = self.pool.get('beacon.test')
        points_obj = self.pool.get('beacon.point')
        beacon_obj = self.pool.get('beacon')
        try:
            for reg in self.browse(cr, uid, ids, context):
                file_content_decoded = base64.decodestring(reg.file_stream)
                decodingJsonTest = json.loads(file_content_decoded)
                mapa = decodingJsonTest.get('mapa')
                ids_import = import_obj.search(cr,uid,[],0, None)
                for line in import_obj.browse(cr, uid, ids_import):
                    name = line.file_name
                    if name == mapa:
                        file_content_decoded = base64.decodestring(line.file_stream)
                        decodingJsonMap = json.loads(file_content_decoded)
                        break
                map_id = map_obj.search(cr,uid,[('file', '=', name)],0, None)
                if len(map_id) == 0:
                    decodingJsonMap_size = decodingJsonMap.get('size')    
                    map_obj.create(cr, uid, {
                        'name':decodingJsonMap.get('name'),
                        'file':name,
                        'x': decodingJsonMap_size.get('x'),
                        'y': decodingJsonMap_size.get('y'),
                        'z': decodingJsonMap_size.get('z'),
                    })
                    beacons = decodingJsonMap.get('beacons')   
                    for beacon in beacons:
                        pos = beacon.get('pos')    
                        map_beacons_obj.create(cr, uid, {
                            'uuid':beacon.get('uuid'),
                            'major':beacon.get('major'),
                            'minor':beacon.get('minor'),
                            'x': pos.get('x'),
                            'y': pos.get('y'),
                            'z': pos.get('z'),
                            'map_id': map_id[0],
                        })
                
                try:
                    config = decodingJsonTest.get('config')
                    frequency = int(config.get('frequency').encode('utf-8'))
                    txpower = config.get('txPower')
                    nameTest = config.get('name').encode('utf-8')
                    test_id = test_obj.create(cr, uid, {
                        'name':nameTest,
                        'frecuency': frequency,
                        'txpower': txpower,
                        'map': map_id[0]
                    })
                    points = decodingJsonTest.get('puntos')
                    for point in points:
                        point_index = points.index(point) + 1 
                        point_id = points_obj.create(cr, uid, {
                            'point':point_index,                                   
                            'x':point.get('x'),
                            'y': point.get('y'),
                            'z': point.get('z'),
                            'magneticheading': point.get('magneticHeading'),
                            'trueHeading': point.get('trueHeading'),
                            'closest': point.get('closest'),
                            'test_id': test_id,
                            })
                        samples = point.get('samples')
                        for sample in samples:
                            sample_beacons = sample.get('beacons')
                            sample_index = samples.index(sample) + 1 
                            for sample_beacon in sample_beacons:
                                beacon_id = beacon_obj.create(cr, uid, {
                                    'sample':sample_index,                                    
                                    'major':sample_beacon.get('major'),
                                    'minor': sample_beacon.get('minor'),
                                    'uuid': sample_beacon.get('uuid'),
                                    'accuracy': sample_beacon.get('accuracy'),
                                    'rssi': sample_beacon.get('rssi'),
                                    'proximity':str(sample_beacon.get('proximity')),
                                    'point_id': point_id,
                                    })
                    
                except:
                    pass   
                
                    
                    
                
        except:
            return False
            
            
        return True
    