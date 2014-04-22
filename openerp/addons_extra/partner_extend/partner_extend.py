# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 jmesteve All Rights Reserved
#                       https://github.com/jmesteve
#                       <jmesteve@me.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'number_collegiate': fields.integer('Number collegiate'),  
        'date_brother': fields.date('Date brother', select=1),  
        'date_collegiate': fields.date('Date collegiate', select=1), 
        'date_governing': fields.date('Date governing', select=1), 
        'date_presidency': fields.date('Date presidency', select=1),   
        'date_brother_end': fields.date('Date brother end', select=1),  
        'date_collegiate_end': fields.date('Date collegiate end', select=1), 
        'date_governing_end': fields.date('Date governing end', select=1), 
        'date_presidency_end': fields.date('Date presidency end', select=1),             
        'phone_business': fields.char('Business phone', size=64),    
        'phone_other': fields.char('Other phone'),     
        'brother': fields.boolean('Brother'),       
        'governing': fields.boolean('Governing board'),  
        'collegiate': fields.boolean('Collegiate'),      
        'presidency': fields.boolean('Presidency'),                 
        }
    
    #_sql_constraints = [('number_collegiate_no_uniq','unique(number_collegiate)', 'number collegiate must be unique!')]

res_partner()    
    