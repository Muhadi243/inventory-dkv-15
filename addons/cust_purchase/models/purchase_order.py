from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_set_quantities(self):
        for line in self.order_line:
            line.qty_received = line.product_qty

    def button_confirm(self):
        """Override button_confirm untuk langsung menambah stok di product.template."""
        res = super(PurchaseOrder, self).button_confirm()  # Jalankan logika bawaan Odoo

        # Tambahkan jumlah produk yang dibeli ke stock
        for line in self.order_line:
            product = line.product_id.product_tmpl_id  # Ambil template produk
            product.stock += line.product_qty  # Tambahkan ke stok

        return res