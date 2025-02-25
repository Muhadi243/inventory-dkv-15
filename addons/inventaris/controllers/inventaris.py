from odoo import http
from odoo.http import request
import json
import base64

class InventarisAPI(http.Controller):

    @http.route("/api/inventaris", type='http', auth='public', methods=['GET'], csrf=False)
    def get_inventaris(self):
        # Mengambil semua record dari model inventaris.inventaris
        inventaris_records = request.env['inventaris.inventaris'].sudo().search([])
        inventaris_details = []

        # Loop melalui setiap record dan menyusun data
        for record in inventaris_records:
            qrcode_image = base64.b64encode(record.id_barang.qr_code).decode('utf-8') if record.id_barang.qr_code else None
            inventaris_details.append({
                'id_inventaris': record.id,
                'id_barang': record.id_barang.id,
                'nama_jenis_barang': record.id_barang.id_jenis_barang.name,
                'nama_barang': record.id_barang.name,
                'merek': record.id_barang.merk_barang,
                'kode_barang': record.id_barang.default_code,
                'qrcode_image': qrcode_image,
                'stok_barang': record.id_barang.stock,
                'id_ruangan': record.id_lokasi.id,
                'nama_ruangan': record.id_lokasi.nama_lokasi,
                'jumlah_barang': record.jumlah_barang,
                'kondisi_barang': record.kondisi_barang,
                'created_at': record.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': record.write_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # Membuat respons JSON
        response = {
            'status': 200,
            'message': 'Data inventaris berhasil diambil',
            'data': inventaris_details
        }

        # Mengembalikan respons JSON
        return http.Response(
            json.dumps(response, indent=4),
            content_type='application/json',
            status=200
        )