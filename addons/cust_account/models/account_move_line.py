from odoo import fields, models, api
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    panjang = fields.Float(string='Panjang', store=True)
    lebar = fields.Float(string='Lebar', store=True)
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True, related="move_id.type_product")

    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None, panjang=None, lebar=None, type_product=None):
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
            panjang=self.panjang if panjang is None else panjang,
            lebar=self.lebar if lebar is None else lebar,
            type_product=self.type_product if type_product is None else type_product,
        )


    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type, panjang, lebar, type_product):
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
        if type_product == 'custom':
            line_discount_price_unit = panjang * lebar * line_discount_price_unit
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        # In case of multi-currency, round before it's used for computing debit/credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res


    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')

        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded

            # Ensure balance == amount_currency in case of missing currency or same currency as the one from the
            # company.
            currency_id = vals.get('currency_id') or move.company_id.currency_id.id
            if currency_id == move.company_id.currency_id.id:
                balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                vals.update({
                    'currency_id': currency_id,
                    'amount_currency': balance,
                })
            else:
                vals['amount_currency'] = vals.get('amount_currency', 0.0)
                if not move.is_invoice(include_receipts=True) and vals.get('debit') is False and vals.get('credit') is False:
                    vals['balance'] = move.currency_id._convert(vals['amount_currency'], move.company_id.currency_id, move.company_id, move.date)
                    vals['debit'] = vals['balance'] if vals['balance'] > 0.0 else 0.0
                    vals['credit'] = -vals['balance'] if vals['balance'] < 0.0 else 0.0

            if move.is_invoice(include_receipts=True):
                currency = move.currency_id
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
                tax_ids = set(taxes.ids)
                taxes = self.env['account.tax'].browse(tax_ids)
                panjang = vals.get('panjang')
                lebar = vals.get('lebar')
                type_product = vals.get('type_product')

                # Ensure consistency between accounting & business fields.
                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    # Call to _get_price_total_and_subtotal_model only once to update price_subtotal
                    price_subtotal = self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        type_product,
                        vals.get('lebar', 0.0),
                        vals.get('panjang', 0.0),
                    ).get('price_subtotal', 0.0)

                    # Now update vals with the computed price_subtotal
                    vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        vals['amount_currency'],
                        move.move_type,
                        currency,
                        taxes,
                        price_subtotal
                    ))

        return super(AccountMoveLine, self).create(vals_list)
