from odoo import models, fields

class Inventaris(models.Model):
    _name = 'inventaris.inventaris'
    _description = 'Data Inventaris'

    id_barang = fields.Many2one('inventaris.barang', string='Barang', required=True)
    id_lokasi = fields.Many2one('inventaris.lokasi', string='Lokasi', required=True)
    kondisi_barang = fields.Selection([
        ('lengkap', 'Lengkap'),
        ('tidak_lengkap', 'Tidak Lengkap'),
        ('rusak', 'Rusak'),
    ], string='Kondisi Barang', required=True)
    jumlah_barang = fields.Integer(string='Jumlah Barang', required=True, default=1)
