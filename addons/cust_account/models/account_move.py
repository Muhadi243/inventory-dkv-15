from odoo import fields, models, api
import datetime

class AccountMove(models.Model):
    _inherit = "account.move"
    
    customer_name = fields.Char(store=True, string="Product Type")
    origin = fields.Char(store=True, string="Origin")
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True)

    invoice_date = fields.Date(default=fields.Date.context_today, store=True)
