from openerp.osv import fields, orm
from openerp import netsvc
from openerp.tools.translate import _

class pos_order(orm.Model):
    _inherit = "pos.order"
    
    def action_revert_done(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        cr.execute('select id from pos_order where id IN %s and state=%s', (tuple(ids), 'cancel'))
        line_ids = map(lambda x: x[0], cr.fetchall())
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            wf_service.trg_delete(uid, 'pos.order', inv_id, cr)
            wf_service.trg_create(uid, 'pos.order', inv_id, cr)
        return True