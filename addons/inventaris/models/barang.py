from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)

class Barang(models.Model):
    _name = 'inventaris.barang'
    _description = 'Data Barang'

    nama_barang = fields.Char(string='Nama Barang', required=True)
    merk_barang = fields.Char(string='Merk Barang')
    kode_barang = fields.Char(string='Kode Barang', required=True)
    id_jenis_barang = fields.Many2one('inventaris.jenis_barang', string='Jenis Barang')
    stok_barang = fields.Integer(string='Stok Barang', default=0)
    qr_code = fields.Binary(string='QR Code', compute='_generate_qr_code', store=True)

    @api.depends('kode_barang')
    def _generate_qr_code(self):
        for record in self:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(record.kode_barang)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_img = base64.b64encode(buffer.getvalue())
                record.qr_code = qr_img
                _logger.info(f"QR code generated successfully for {record.kode_barang}")
            except Exception as e:
                _logger.error(f"Failed to generate QR code for {record.kode_barang}: {e}")

