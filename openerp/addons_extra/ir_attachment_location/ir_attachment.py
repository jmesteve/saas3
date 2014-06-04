from openerp.osv import orm, fields
import openerp
from openerp import tools
import re
import os

class ir_attachment(orm.Model):
    _inherit = 'ir.attachment'
    
    # Set ir_attachemnt location
    # Get location from config file. If no location, default_location is: /etc/openerp/attachments
    def _set_config_location(self, cr, uid, context=None):
        
        config = openerp.tools.config
        config_attachment_path = config.get('attachment_path')
        default_attachment_path = 'file:/../../attachments'
        attachment_path = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        
        if not attachment_path:
            if config_attachment_path:
                attachment_path = config_attachment_path
            else:
                attachment_path = default_attachment_path
            self.pool.get('ir.config_parameter').set_param(cr, uid, 'ir_attachment.location', attachment_path)
    
    # 'data' field implementation
    def _full_path(self, cr, uid, location, path):
        # location = 'file:filestore'
        assert location.startswith('file:'), "Unhandled filestore location %s" % location
        location = location[5:]

        # sanitize location name and path
        #location = re.sub('[.]','',location)
        location = location.strip('/\\')

        path = re.sub('[.]','',path)
        path = path.strip('/\\')
        return os.path.join(tools.config['root_path'], location, cr.dbname, path)
    
    def _attachment_migration_to_filestore(self, cr, uid, context=None):
        ids = self.search(cr, uid, [], context=context)
        attachments = self.browse(cr, uid, ids, context=context)
        for attachment in attachments:
            if attachment.db_datas:
                # If location is set, the attachment binary is stored in files
                self.write(cr, uid, attachment.id, {'datas': attachment.db_datas}, context=context)
                # Delete value of binary field
                self.write(cr, uid, attachment.id, {'db_datas': False}, context=context)
                
                