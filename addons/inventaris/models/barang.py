from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)

class Barang(models.Model):
    _inherit = 'product.template'
    _description = 'Data Barang'

    merk_barang = fields.Char(string='Merk Barang')
    id_jenis_barang = fields.Many2one('inventaris.jenis_barang', string='Jenis Barang')
    qr_code = fields.Binary(string='QR Code', compute='_generate_qr_code', store=True)

    @api.depends('default_code')
    def _generate_qr_code(self):
        for record in self:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(record.default_code)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_img = base64.b64encode(buffer.getvalue())
                record.qr_code = qr_img
                _logger.info(f"QR code generated successfully for {record.default_code}")
            except Exception as e:
                _logger.error(f"Failed to generate QR code for {record.default_code}: {e}")

