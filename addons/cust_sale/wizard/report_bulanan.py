from odoo import models, fields
from datetime import datetime, timedelta
import io
import xlsxwriter
import base64
from collections import defaultdict

class SalesReportMonthlyXlsx(models.TransientModel):
    _name = 'sales.report.monthly.xlsx'
    _description = 'Monthly Sales Report in Excel'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    def generate_xlsx_report(self):
        """Method to generate the Excel report for monthly sales and purchases."""
        sale_orders = self.env['sale.order'].search([
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
            ('state', 'in', ['sale', 'done'])
        ])
        
        purchase_orders = self.env['purchase.order'].search([
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
            ('state', 'in', ['purchase', 'done'])
        ])
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sales_sheet = workbook.add_worksheet("Sales Report")
        purchase_sheet = workbook.add_worksheet("Purchase Report")
        
        # Define Styles
        bold = workbook.add_format({'bold': True, 'bg_color': '#FFFF99', 'border': 1, 'align': 'center'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1, 'align': 'center'})
        data_format = workbook.add_format({'border': 1, 'align': 'center'})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})

        # Write Sales Headers
        sales_headers = [
            "Product", "Date", "Time", "Harga Awal", "Harga Jual", "Panjang", "Lebar", 
            "Quantity Penjualan", "Total Kotor Penjualan", "Profit", "Operator/Mar (20%)", 
            "Operator/Mesin (10%)", "BC (30%/60%)", "Operasional (20%)", "Sekolah (20%)"
        ]
        sales_sheet.write_row(0, 0, sales_headers, header_format)

        sales_row = 1
        for order in sale_orders:
            for line in order.order_line:
                if line.product_id and line.product_id.type_product in ['atk', 'custom']:
                    product_name = line.product_id.name or ""
                    harga_awal = line.product_id.product_tmpl_id.harga_beli
                    harga_jual = line.product_id.list_price
                    panjang = line.panjang if line.product_id.type_product == 'custom' else '-'
                    lebar = line.lebar if line.product_id.type_product == 'custom' else '-'
                    quantity_penjualan = line.product_uom_qty
                    order_date = order.date_order
                    order_time = (order.date_order + timedelta(hours=7)).strftime('%H:%M:%S')

                    # Calculate Total Kotor Penjualan
                    if line.product_id.type_product == 'custom':
                        total_kotor_penjualan = harga_jual * panjang * lebar * quantity_penjualan
                    else:
                        total_kotor_penjualan = harga_jual * quantity_penjualan

                    # Calculate Profit
                    if line.product_id.type_product == 'custom':
                        profit = total_kotor_penjualan - (harga_awal * quantity_penjualan)
                    else:
                        profit = total_kotor_penjualan - (harga_awal * quantity_penjualan)

                    operator_mar = profit * 0.2 if line.product_id.type_product == 'custom' else '-'
                    operator_mesin = profit * 0.1 if line.product_id.type_product == 'custom' else '-'
                    bc = profit * 0.3 if line.product_id.type_product == 'atk' else profit * 0.6
                    operasional = profit * 0.2
                    sekolah = profit * 0.2

                    # Write data to Excel
                    sales_sheet.write(sales_row, 0, product_name, data_format)
                    sales_sheet.write(sales_row, 1, order_date, date_format)
                    sales_sheet.write(sales_row, 2, order_time, data_format)
                    sales_sheet.write(sales_row, 3, harga_awal, data_format)
                    sales_sheet.write(sales_row, 4, harga_jual, data_format)
                    sales_sheet.write(sales_row, 5, panjang, data_format)
                    sales_sheet.write(sales_row, 6, lebar, data_format)
                    sales_sheet.write(sales_row, 7, quantity_penjualan, data_format)
                    sales_sheet.write(sales_row, 8, total_kotor_penjualan, data_format)  # Total Kotor Penjualan
                    sales_sheet.write(sales_row, 9, profit, data_format)
                    sales_sheet.write(sales_row, 10, operator_mar, data_format)
                    sales_sheet.write(sales_row, 11, operator_mesin, data_format)
                    sales_sheet.write(sales_row, 12, bc, data_format)
                    sales_sheet.write(sales_row, 13, operasional, data_format)
                    sales_sheet.write(sales_row, 14, sekolah, data_format)
                    sales_row += 1

        # Write Purchase Headers
        purchase_headers = ["Product", "Date", "Time", "Quantity Pembelian", "Total Price"]
        sales_sheet.write_row(0, 16, purchase_headers, header_format)

        purchase_row = 1
        for order in purchase_orders:
            for line in order.order_line:
                if line.product_id and line.product_id.type_product in ['atk', 'custom']:
                    product_name = line.product_id.name or ""
                    order_time = (order.date_order + timedelta(hours=7)).strftime('%H:%M:%S')
                    quantity_pembelian = line.product_qty
                    total_price = line.price_total

                    sales_sheet.write(purchase_row, 16, product_name, data_format)
                    sales_sheet.write(purchase_row, 17, order.date_order, date_format)
                    sales_sheet.write(purchase_row, 18, order_time, data_format)
                    sales_sheet.write(purchase_row, 19, quantity_pembelian, data_format)
                    sales_sheet.write(purchase_row, 20, total_price, data_format)
                    purchase_row += 1

        # Calculate monthly totals (gross sales and purchases)
        monthly_totals = defaultdict(lambda: {'sales': 0, 'purchases': 0})
        for order in sale_orders:
            month = order.date_order.strftime('%Y-%m')
            for line in order.order_line:
                if line.product_id and line.product_id.type_product in ['atk', 'custom']:
                    if line.product_id.type_product == 'custom':
                        total_sales = line.product_id.list_price * line.panjang * line.lebar * line.product_uom_qty
                    else:
                        total_sales = line.product_id.list_price * line.product_uom_qty
                    monthly_totals[month]['sales'] += total_sales

        for order in purchase_orders:
            month = order.date_order.strftime('%Y-%m')
            for line in order.order_line:
                if line.product_id and line.product_id.type_product in ['atk', 'custom']:
                    monthly_totals[month]['purchases'] += line.price_total

        # Write Monthly Totals
        sales_sheet.write_row(sales_row + 2, 0, ["Month", "Total Sales (Gross)", "Total Purchases (Gross)", "Total (Sales - Purchases)"], header_format)
        for month, totals in monthly_totals.items():
            sales_sheet.write_row(sales_row + 3, 0, [month, totals['sales'], totals['purchases'], totals['sales'] - totals['purchases']], data_format)
            
            # Add Profit Row (Total Sales - Purchases)
            sales_sheet.write(sales_row + 4, 0, "Profit", header_format)
            sales_sheet.write(sales_row + 4, 3, totals['sales'] - totals['purchases'], data_format)
            sales_row += 3  # Move to the next month's data

        workbook.close()
        output.seek(0)

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'Monthly_Sales_Report.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'store_fname': 'monthly_sales_report.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        output.close()

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }