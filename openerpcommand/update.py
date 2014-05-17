"""
Update an existing OpenERP database.
"""

def run(args):
    #assert args.database
    import openerp
    config = openerp.tools.config
    
    
    default_config_file = '../openerp-server.conf'
    if args.config == None:
        config_file = default_config_file
    else:
        config_file = args.config
    config.parse_config(['-c', config_file])
    
    if args.database != None:
        database = args.database
    elif config['db_name'] != None:
        database = config['db_name']
    
    openerp.netsvc.init_logger()
    
    if database == None:
        print """ No database name"""
        return -1
    
    if args.all != None:
        config['update']['all'] = 1
    else:
        modules = args.modules.split(',')
        for module in modules:
            config['update'][module] = 1
    openerp.modules.registry.RegistryManager.get(
        database, update_module=True)


def add_parser(subparsers):
    parser = subparsers.add_parser('update',
        description='Update an existing OpenERP database.')
    parser.add_argument('-c', '--config', metavar='CONFIG FILE', required=False,
        help='the config file')
    parser.add_argument('-m', '--modules', metavar='MODULES', required=True,
        help='the addons to update')
    parser.add_argument('-d', '--database', metavar='DATABASE', required=False,
        help='the database to update')
    parser.add_argument('-a', '--all', metavar='ALL', required=False, help='Update all addons')

    parser.set_defaults(run=run)
