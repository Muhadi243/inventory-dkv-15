from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "product.template"
    
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True)


class AccountMove(models.Model):
    _inherit = "product.product"
    
    type_product = fields.Selection(related='product_tmpl_id.type_product', store=True)