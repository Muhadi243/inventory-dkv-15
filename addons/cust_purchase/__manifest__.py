# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Jabin MP(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': "Custom Purchase",
    'version': '15.0.1.0.1',
    'category': 'Extra Tools',
    'summary': 'This module helps to create enterprise like app drawer,'
               'Responsiveness and sticky headers included.',
    'description': """This module helps to create enterprise like app drawer,
     Responsiveness and sticky headers included.""",
    'author': 'Dimas',
    'company': 'Dimas',
    'maintainer': 'Dimas',
    'depends': ['base','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
        'wizard/report_bulanan.xml',
        'wizard/report_harian.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
