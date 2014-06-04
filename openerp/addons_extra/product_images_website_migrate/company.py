from openerp.osv import orm, fields

class ResCompany(orm.Model):
    _inherit = "res.company"

    def _set_local_media_repository_website(self, cr, uid, context=None):
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        if company:
            if not company.local_media_repository_website:
                self.write(cr, uid, company.id, {'local_media_repository_website':
                                                 '/product_website_images/static/src/img/'})