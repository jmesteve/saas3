import openerp.http as http
from openerp.http import request
import werkzeug.utils
import openerp.addons.web.controllers.main as main
import openerp
from openerp import pooler, sql_db
import logging

_logger = logging.getLogger(__name__)

        
class Session_extend(main.Session):
    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        try:
            superuser = openerp.SUPERUSER_ID
            uid = request.session.uid
            login = request.session.login
            url = request.httprequest.base_url
            ip = request.httprequest.remote_addr
            session_id = request.session_id
            dbname = request.session.db
            
            # Get database connexion
            db = sql_db.db_connect(dbname) # You can get the db name from config
            cr = db.cursor()
            pool = pooler.get_pool(cr.dbname)
            pool.get('control.access').create(cr, superuser,{'user_id': uid,
                                                                      'user_name':login,
                                                                      'url':url,
                                                                      'ip':ip,
                                                                      'db':dbname,
                                                                      'type':'OUT',
                                                                      'session': session_id,
                                                                                }
                                                      )
            cr.commit()
            cr.close()
        except:
            print "error logout"
        
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
    
   