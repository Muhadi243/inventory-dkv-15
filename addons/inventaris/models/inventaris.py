from odoo import models, fields, api

class Inventaris(models.Model):
    _name = 'inventaris.inventaris'
    _description = 'Data Inventaris'
    _rec_name = 'id_barang'

    id_barang = fields.Many2one(
        'product.template', 
        string='Barang', 
        required=True, 
        domain=[('type_product', '=', 'store')]
    )
    type_product = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
        ('store', 'Storeable'),
    ], store=True, default='store')
    id_lokasi = fields.Many2one('inventaris.lokasi', string='Lokasi', required=True)
    kondisi_barang = fields.Selection([
        ('lengkap', 'Lengkap'),
        ('tidak_lengkap', 'Tidak Lengkap'),
        ('rusak', 'Rusak'),
    ], string='Kondisi Barang', required=True)
    jumlah_barang = fields.Integer(string='Jumlah Barang', required=True, default=1)


    @api.model
    def get_inventaris_details(self):
        inventaris_records = self.search([])
        inventaris_details = []
        for record in inventaris_records:
            inventaris_details.append({
                'id_inventaris': record.id,
                'id_barang': record.id_barang,
                'nama_jenis_barang': record.id_barang.id_jenis_barang.name,
                'nama_barang': record.id_barang.name,
                'merek': record.id_barang.merk_barang,
                'kode_barang': record.id_barang.default_code,
                'qrcode_image': record.id_barang.qr_code,
                'stok_barang': record.id_barang.stock,
                'id_ruangan': record.id_lokasi.id,
                'nama_ruangan': record.id_lokasi.name,
                'jumlah_barang': record.jumlah_barang,
                'kondisi_barang': record.kondisi_barang,
                # 'ket_barang': record.ket_barang,
                'created_at': record.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': record.write_date.strftime('%Y-%m-%d %H:%M:%S'),
            })
        return inventaris_details
