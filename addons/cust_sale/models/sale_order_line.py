from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    panjang = fields.Float(string='Panjang', store=True)
    lebar = fields.Float(string='Lebar', store=True)
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True)