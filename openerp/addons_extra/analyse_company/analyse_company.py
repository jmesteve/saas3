from openerp.osv import fields,osv
from openerp import pooler
import datetime;
    
    
class analyse_type(osv.osv):
    _name = 'analyse.type'
    _columns = {
                'name': fields.char('Name',  size=64, required=True),
                }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique per type!'),
    ]
    
class analyse_company(osv.osv):
    _name = 'analyse.company'
    
    def _datetime_year(self, cr, uid, context):
        now = datetime.datetime.now()
        return str(now.year)
    
    _columns = {
                'company': fields.many2one('res.partner', 'Company', select=1, required=True),
                'year': fields.char('Year',  size=4, required=True),
                'type': fields.many2one('analyse.type', 'Type', select=1, required=True),
                'value': fields.float('Value',  digits=(16,2), required=True),
                'date_begin': fields.date('Date begin'),
                'date_end': fields.date('Date end'),
                'notes': fields.text('notes'),
                }
    _defaults ={
               'year': _datetime_year,
               }
    _sql_constraints = [
        ('name_uniq', 'unique(company, year, type)', 'Name must be unique per analyse!'),
    ]