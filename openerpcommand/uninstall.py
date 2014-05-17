"""
Install OpenERP on a new (by default) database.
"""
import os
import sys

import common

# TODO turn template1 in a parameter
# This should be exposed from openerp (currently in
# openerp/service/web_services.py).
def create_database(database_name):
    import openerp
    db = openerp.sql_db.db_connect('template1')
    cr = db.cursor() # TODO `with db as cr:`
    try:
        cr.autocommit(True)
        cr.execute("""CREATE DATABASE "%s"
            ENCODING 'unicode' TEMPLATE "template1" """ \
            % (database_name,))
    finally:
        cr.close()

def run(args):
    #assert args.database
    assert args.module

    import openerp

    config = openerp.tools.config

    default_config_file = '../openerp-server.conf'
    if args.config == None:
        config_file = default_config_file
    else:
        config_file = args.config
    
    config.parse_config(['-c', config_file])

    config['log_handler'] = [':CRITICAL']
#    if args.addons:
#        args.addons = args.addons.split(':')
#    else:
#        args.addons = []
#    config['addons_path'] = ','.join(args.addons)
    openerp.netsvc.init_logger()

    # Install the import hook, to import openerp.addons.<module>.
    openerp.modules.module.initialize_sys_path()

    if args.database != None:
        database = args.database
    elif config['db_name'] != None:
        database = config['db_name']
    
    if database == None:
		return -1;

    registry = openerp.modules.registry.RegistryManager.get(database, update_module=False)

    ir_module_module = registry.get('ir.module.module')
    cr = registry.db.cursor() # TODO context manager
    try:
        ids = ir_module_module.search(cr, openerp.SUPERUSER_ID, [('name', 'in', args.module), ('state', '=', 'installed')], {})
        if len(ids) == len(args.module):
            ir_module_module.button_immediate_uninstall(cr, openerp.SUPERUSER_ID, ids, {})
        else:
            print "At least one module not found (database `%s`)." % (database,)
    finally:
        cr.close()

def add_parser(subparsers):
    parser = subparsers.add_parser('uninstall',
        description='Uninstall some modules from an OpenERP database.')
    parser.add_argument('-d', '--database', metavar='DATABASE', required=False)
    #common.add_addons_argument(parser)
    parser.add_argument('-c', '--config', metavar='CONFIG FILE', required=False,
        help='the config file')
    parser.add_argument('-m','--module', metavar='MODULE', action='append',
        help='specify a module to uninstall'
        ' (this option can be repeated)')

    parser.set_defaults(run=run)
