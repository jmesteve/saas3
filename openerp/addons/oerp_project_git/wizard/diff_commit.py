# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields


class diff_commi(osv.osv_memory):
    _name = 'diff.commi'
    _description = 'Diff Commit'

    _columns = {
        'main_commit': fields.many2one('git.commit', 'Main Commit'),
        'base_commit': fields.many2one('git.commit', 'Base Commit'),
        'diff': fields.text('Diff'),
    }

diff_commi()

