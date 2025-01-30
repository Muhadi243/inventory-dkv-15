from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    customer_name = fields.Char(store=True)
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True)

    @api.onchange('type_product')
    def _onchange_type_product(self):
        for line in self.order_line:
            if self.type_product:
                line.type_product = self.type_product
            else:
                line.type_product = False


    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order.
        """
        self.ensure_one()

        values = super(SaleOrder, self)._prepare_invoice()

        values.update({
            'type_product': self.type_product,
            'customer_name': self.customer_name, 
        })

        return values

