from openerp.osv import osv, fields
from openerp.addons.point_of_sale.point_of_sale import pos_session


class pos_session_opening(osv.osv_memory):
    _inherit = 'pos.session.opening'

    def open_ui(self, cr, uid, ids, context=None):
        context = context or {}
        data = self.browse(cr, uid, ids[0], context=context)
        context['active_id'] = data.pos_session_id.id
        self.pool.get('pos.session').write(cr, uid,context['active_id'],{'user_id' :uid}, context=context)
        return {
            'type' : 'ir.actions.act_url',
            'url':   '/pos/web/',
            'target': 'self',
        }

  