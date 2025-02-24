from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
        ('store', 'Storeable'),
    ], store=True, related="order_id.type_product")