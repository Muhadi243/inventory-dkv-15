from odoo import fields, models, api
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    panjang = fields.Float(string='Panjang', store=True)
    lebar = fields.Float(string='Lebar', store=True)
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True, related="order_id.type_product")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'panjang', 'type_product', 'lebar')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.type_product == 'custom':
                price = line.panjang * line.lebar * price
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    
    @api.onchange('product_id')
    def _onchange_product_uom_qty(self):
        if self.product_id and self.product_uom_qty > self.product_id.product_tmpl_id.stock and self.type_product == 'atk':
            raise UserError('The ordered quantity exceeds the available stock for the product.')

    def _prepare_invoice_line(self, **optional_values):
        """ Prepare the dictionary to create an invoice line from a sale order line. """
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({
            'panjang': self.panjang,
            'lebar': self.lebar,
            'type_product': self.type_product,
        })
        return res