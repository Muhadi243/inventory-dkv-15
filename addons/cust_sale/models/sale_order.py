from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    customer_name = fields.Char(store=True)
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True, compute='_compute_type_product')

    @api.depends('user_id')
    def _compute_type_product(self):
        for order in self:
            if self.env.user.type_user == 'atk':
                order.type_product = 'atk'
            elif self.env.user.type_user == 'custom':
                order.type_product = 'custom'
            else:
                order.type_product = 'atk'

    def _inverse_type_product(self):
        for order in self:
            if not order.type_product:
                order.type_product = 'atk' if self.env.user.type_user == 'atk' else False

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order.
        """
        self.ensure_one()

        values = super(SaleOrder, self)._prepare_invoice()

        values.update({
            'type_product': self.type_product,
            'customer_name': self.customer_name, 
            'origin': self.name, 
        })

        return values

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.type_product == 'atk':
                for line in order.order_line:
                    product = line.product_id.product_tmpl_id.sudo()
                    product.stock -= line.product_uom_qty
        return res

