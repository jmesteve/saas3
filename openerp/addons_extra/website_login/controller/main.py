from openerp import http
from openerp.addons.web.http import request, LazyResponse
import openerp.addons.website.controllers.main as website
import openerp.addons.web.controllers.main as web

class Home_extend(web.Home):
    @http.route('/shop/login', type='http', auth='public', website=True, multilang=True)
    def login_shop(self, *args, **kw):
        response = super(Home_extend, self).web_login(*args, **kw)
        if isinstance(response, LazyResponse):
            values = dict(response.params['values'], disable_footer=True)
            response = request.website.render(response.params['template'], values)
        return response


    
