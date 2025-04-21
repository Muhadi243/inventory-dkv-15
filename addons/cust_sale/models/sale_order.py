from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_operator = fields.Boolean(string="Is Operator")

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    customer_name = fields.Char(store=True)
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
    ], store=True, compute='_compute_type_product')
    operator_id = fields.Many2one('res.partner', string="Operator", domain="[('is_operator', '=', True)]")

        # Field yang akan diisi otomatis
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        store=True,
        readonly=True,  # Biarkan bisa diubah manual
        default=lambda self: self.env['res.partner'].search([('name', 'ilike', 'Customer')], limit=1).id
    )

    def _create_invoices(self, grouped=False, final=False, date=None):
        # Buat invoice seperti biasa
        moves = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
        
        # Post semua invoice yang baru dibuat
        if moves:
            moves.action_post()  # Untuk Odoo 13+, versi lama pakai `moves.validate()`
        
        return moves

    @api.depends('user_id')
    def _compute_type_product(self):
        for order in self:
            if self.env.user.type_user == 'atk':
                order.type_product = 'atk'
            elif self.env.user.type_user == 'custom':
                order.type_product = 'custom'
            else:
                order.type_product = 'atk'

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


