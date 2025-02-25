from odoo import models, fields

class QRCodeMaster(models.Model):
    _name = 'qrcode.master'
    _description = 'QR Code Master'

    name = fields.Char(string="Name", required=True)
    qrcode = fields.Binary(string="QR Code", required=True)
