from odoo import models, fields

class Lokasi(models.Model):
    _name = 'inventaris.lokasi'
    _description = 'Data Master Lokasi'
    _rec_name = 'nama_lokasi'

    nama_lokasi = fields.Char(string='Nama Lokasi', required=True)
