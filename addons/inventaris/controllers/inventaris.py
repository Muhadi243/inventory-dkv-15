from odoo import http
from odoo.http import request

class ProductController(http.Controller):

    @http.route('/api/inventaris_details', type='json', auth='public')
    def get_inventaris_details(self):
        inventaris = request.env['inventaris.inventaris'].get_inventaris_details()
        return {'status': 200, 'data': inventaris}
