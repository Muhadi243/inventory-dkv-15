from odoo import models, fields

class JenisBarang(models.Model):
    _name = 'inventaris.jenis_barang'
    _description = 'Data Master Jenis Barang'

    name = fields.Char(string='Jenis Barang', required=True)
