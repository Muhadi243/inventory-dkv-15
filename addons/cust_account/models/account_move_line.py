from odoo import fields, models, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    panjang = fields.Float(string='Panjang', store=True)
    lebar = fields.Float(string='Lebar', store=True)
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True, related="move_id.type_product")

    # @api.model
    # def create(self, vals):
    #     vals['tax_ids'] = [(6, 0, [])]
    #     return super(AccountMoveLine, self).create(vals)

    # def write(self, vals):
    #     vals['tax_ids'] = [(6, 0, [])]
    #     return super(AccountMoveLine, self).write(vals)

    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     self.tax_ids = [(6, 0, [])]
    #     self.name = self.product_id.name

    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=self.price_unit if price_unit is None else price_unit,
            quantity=self.quantity if quantity is None else quantity,
            discount=self.discount if discount is None else discount,
            currency=self.currency_id if currency is None else currency,
            product=self.product_id if product is None else product,
            partner=self.partner_id if partner is None else partner,
            taxes=self.tax_ids if taxes is None else taxes,
            move_type=self.move_id.move_type if move_type is None else move_type,
        )

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        if self.type_product == 'custom':
            subtotal = quantity * line_discount_price_unit * self.panjang * self.lebar
        else:
            subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            if self.type_product == 'custom':
                taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit * self.panjang * self.lebar,
                    quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            else:
                taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                    quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        # In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res