from openerp.osv import fields, osv
import base64
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import openerp

class google_map_kml(osv.osv):
    
    _name =  'googlemap.kml'
    _columns = {'name_file': fields.char('KML File name', size=25, required=True),
                'kml_file': fields.binary('KML file', required=True),
                'link': fields.char('KML Url', size=100, required=True)
                }

    def create_kml(self, cr, uid, ids, context=None):
        partner_obj= self.pool.get('res.partner')
        partner_ids = partner_obj.search(cr, uid, [])
        partner_data = partner_obj.browse(cr, uid, partner_ids, context)

        top = Element('kml')
        top.set('xmlns', 'http://www.opengis.net/kml/2.2')
        
        document= SubElement(top, 'Document')
        document.set('id', 'kml')
        
        child = SubElement(document, 'name')
        child.text = 'hola'
        
        child = SubElement(document, 'visibility')
        child.text = '1'
        
        child = SubElement(document, 'open')
        child.text = '1'
        
        placemark = SubElement(document, 'Placemark')
        placemark.set('id', 'target')
        child = SubElement(placemark, 'name')
        child.text = 'Start'
        point = SubElement(placemark, 'Point')
        point.set('id', 'targetpoint')
        child = SubElement(point, 'coordinates')
        child.text = '0.16212,51.5454'
        
        out = base64.encodestring(tostring(top, 'utf-8'))
        fname= 'kml.xml'
        
        return {'kml_file': out, 'name_file': fname}
    
    def get_kml_url(self, cr, uid, ids, context=None):
        
        static_path = openerp.tools.config['static_http_document_root']
        
        return ''

