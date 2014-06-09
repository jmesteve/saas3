# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 ErpAndCloud All Rights Reserved
#                       https://github.com/jmesteve
#                       https://github.com/escrichov
#                       <engineering@erpandcloud.com>
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
{
    'name': 'Google Map KML',
    'version': '1.3',
    'author': 'ErpAndCloud',
    'category': 'Customer Relationship Management',    
    'description': """
        [ENG] View all customers on Google maps.
    """,
    'website': 'http://www.erpandcloud.com',
    'license': 'AGPL-3',
    'images': [],
    'depends' : ['base','web', 'website'],
    'data': [
             'data/google_map_kml_data.xml',
             'google_map_kml_view.xml',
             'security/groups.xml',
             'security/ir.model.access.csv',
             'partner_view.xml'
             ],
    'css': ['static/src/css/location_map_partner.css'],
    'js': ['https://maps.googleapis.com/maps/api/js?sensor=false&libraries=places',
           'static/src/js/location_map_partners.js'],
    'qweb' : ['static/src/xml/templates.xml'],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}


