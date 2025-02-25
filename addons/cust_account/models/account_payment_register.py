from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    qrcode = fields.Many2one('qrcode.master', string="QR Code")
    image_qrcode = fields.Binary(string="QR Code Image")
    show_qrcode = fields.Boolean(default=False, string="Show QR Code")

    @api.onchange('qrcode')
    def _onchange_image_qrcode(self):
        if self.qrcode:
            self.image_qrcode = self.qrcode.qrcode
        else:
            self.image_qrcode = False

    @api.onchange('journal_id')
    def _onchange_qrcode(self):
        if self.journal_id:
            self.show_qrcode = 'Qris' in self.journal_id.name
        else:
            self.show_qrcode = False
