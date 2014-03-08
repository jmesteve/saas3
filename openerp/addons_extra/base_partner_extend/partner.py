from openerp.osv import osv, fields
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    _columns = {
                'id_commercial': fields.related('commercial_partner_id', 'id', string='Id Commercial', type='integer', readonly=True, store=False),
               }
        
    # create register
    def create(self, cr, uid, vals, context=None):  
        #if not 'ref' in vals or vals['ref'] == '/':
        #        vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')                  
        res = super(res_partner, self).create(cr, uid, vals, context)
        self.write(cr, uid, [res], vals, context)
        return res
    
    #duplicate register
    def copy(self, cr, uid, id, default={}, context=None):
        partner = self.read(cr, uid, id, ['ref'], context=context)
        if partner['ref']:
            default.update({
            #'ref': partner['ref'] + _('-copy'),
            'ref' : '/'
            })
        res = super(res_partner, self).copy(cr, uid, id, default, context)
        return res
         
   # edit register
    def write(self, cr, uid, ids, vals, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        partners_without_code = self.search(cr, uid, [
            ('ref', 'in', [False, '/']), ('id', 'in', ids)], context=context)
        direct_write_ids = set(ids) - set(partners_without_code)
        super(res_partner, self).write( cr, uid, list(direct_write_ids), vals, context)
        for partner_id in partners_without_code:
                vals['ref'] = 'P' + str(partner_id+100000)[-5:]
                super(res_partner, self).write(cr, uid, partner_id, vals, context)
        return True
    
res_partner()