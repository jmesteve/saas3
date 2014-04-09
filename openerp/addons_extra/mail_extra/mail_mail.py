from openerp.osv import fields, osv
from urlparse import urljoin
from urllib import urlencode

class mail_mail(osv.osv):
    
    _inherit = 'mail.mail'
    
    #------------------------------------------------------
    # mail_mail formatting, tools and send mechanism
    #------------------------------------------------------

    def _get_partner_access_link(self, cr, uid, mail, partner=None, context=None):
        """ Generate URLs for links in mails:
            - partner is an user and has read access to the document: direct link to document with model, res_id
        """
        if partner and partner.user_ids:
            return ""
        else:
            return None