from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"
    
    customer_name = fields.Char(store=True, string="Product Type")
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True)