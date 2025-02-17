from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "product.template"
    
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True)

    # detailed_type = fields.Selection([
    #     ('consu', 'Consumable'),
    #     ('service', 'Service'),
    #     ('store', 'Storable Product'),
    # ], store=True)

    stock = fields.Integer(store=True, string="Stock")


class AccountMove(models.Model):
    _inherit = "product.product"
    
    type_product = fields.Selection(related='product_tmpl_id.type_product', store=True)
    # detailed_type = fields.Selection([
    #     ('consu', 'Consumable'),
    #     ('service', 'Service'),
    #     ('store', 'Storable Product'),
    # ], store=True)