from openerp.osv import fields,osv
import openerp


class res_users(osv.osv):
    _inherit = "res.users"
    def authenticate(self, db, login, password, user_agent_env):
        """Verifies and returns the user ID corresponding to the given
          ``login`` and ``password`` combination, or False if there was
          no matching user.

           :param str db: the database on which user is trying to authenticate
           :param str login: username
           :param str password: user password
           :param dict user_agent_env: environment dictionary describing any
               relevant environment attributes
        """
        uid = self.login(db, login, password)
        superuser = openerp.SUPERUSER_ID
        try:
            cr = self.pool.db.cursor()
            
            self.pool.get('control.access').create(cr, superuser,{'user_id': uid,
                                                                  'user_name':login,
                                                                  'url':user_agent_env.get('base_location'),
                                                                  'ip':user_agent_env.get('REMOTE_ADDR'),
                                                                  'db':db,
                                                                  'type':'IN'
                                                                            }
                                                  )
            cr.commit()
        except:
            print "error authetificate"
        
        if uid == superuser:
            # Successfully logged in as admin!
            # Attempt to guess the web base url...
            if user_agent_env and user_agent_env.get('base_location'):
                try:
                    #cr = self.pool.db.cursor()
                    base = user_agent_env['base_location']
                    ICP = self.pool['ir.config_parameter']
                    if not ICP.get_param(cr, uid, 'web.base.url.freeze'):
                        ICP.set_param(cr, uid, 'web.base.url', base)
                    cr.commit()
                except Exception:
                    _logger.exception("Failed to update web.base.url configuration parameter")
                #finally:
                #    cr.close()
        cr.close()
        return uid