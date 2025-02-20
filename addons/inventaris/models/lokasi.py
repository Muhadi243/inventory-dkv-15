from odoo import models, fields

class Lokasi(models.Model):
    _name = 'inventaris.lokasi'
    _description = 'Data Master Lokasi'

    nama_lokasi = fields.Char(string='Nama Lokasi', required=True)
