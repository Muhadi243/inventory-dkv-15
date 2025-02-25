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
            "Product", "Date", "Time", "Operator", "Harga Awal", "Harga Jual", "Panjang", "Lebar", 
            "Quantity Penjualan", "Total Kotor Penjualan", "Profit", "Operator/Mar", 
            "Operator/Mesin", "BC", "Operasional", "Sekolah"
        ]
        sales_sheet.write_row(0, 0, sales_headers, header_format)

        # Fetch profit percentages
        profit_percentage = self.env['profit.percentage'].search([], limit=1)
        if not profit_percentage:
            raise ValueError("Profit percentage data is not configured.")

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
                    operator_name = order.operator_id.name if order.operator_id else '-'

                    # Calculate Total Kotor Penjualan
                    if line.product_id.type_product == 'custom':
                        total_kotor_penjualan = harga_jual * panjang * lebar * quantity_penjualan
                    else:
                        total_kotor_penjualan = harga_jual * quantity_penjualan

                    # Calculate Profit
                    if line.product_id.type_product == 'custom':
                        profit = total_kotor_penjualan - (harga_awal * quantity_penjualan)
                        bc = profit * (profit_percentage.bc_custom / 100)
                        operasional = profit * (profit_percentage.operasional_custom / 100)
                        sekolah = profit * (profit_percentage.sekolah_custom / 100)
                    else:
                        profit = total_kotor_penjualan - (harga_awal * quantity_penjualan)
                        bc = profit * (profit_percentage.bc_atk / 100)
                        operasional = profit * (profit_percentage.operasional_atk / 100)
                        sekolah = profit * (profit_percentage.sekolah_atk / 100)

                    operator_mar = profit * (profit_percentage.operator_mar / 100) if line.product_id.type_product == 'custom' else '-'
                    operator_mesin = profit * (profit_percentage.operator_mesin / 100) if line.product_id.type_product == 'custom' else '-'

                    # Write data to Excel
                    sales_sheet.write(sales_row, 0, product_name, data_format)
                    sales_sheet.write(sales_row, 1, order_date, date_format)
                    sales_sheet.write(sales_row, 2, order_time, data_format)
                    sales_sheet.write(sales_row, 3, operator_name, data_format)
                    sales_sheet.write(sales_row, 4, harga_awal, data_format)
                    sales_sheet.write(sales_row, 5, harga_jual, data_format)
                    sales_sheet.write(sales_row, 6, panjang, data_format)
                    sales_sheet.write(sales_row, 7, lebar, data_format)
                    sales_sheet.write(sales_row, 8, quantity_penjualan, data_format)
                    sales_sheet.write(sales_row, 9, total_kotor_penjualan, data_format)  # Total Kotor Penjualan
                    sales_sheet.write(sales_row, 10, profit, data_format)
                    sales_sheet.write(sales_row, 11, operator_mar, data_format)
                    sales_sheet.write(sales_row, 12, operator_mesin, data_format)
                    sales_sheet.write(sales_row, 13, bc, data_format)
                    sales_sheet.write(sales_row, 14, operasional, data_format)
                    sales_sheet.write(sales_row, 15, sekolah, data_format)
                    sales_row += 1

        # Write Purchase Headers
        purchase_headers = ["Product", "Date", "Time", "Quantity Pembelian", "Total Price"]
        sales_sheet.write_row(0, 17, purchase_headers, header_format)

        purchase_row = 1
        for order in purchase_orders:
            for line in order.order_line:
                if line.product_id and line.product_id.type_product in ['atk', 'custom']:
                    product_name = line.product_id.name or ""
                    order_time = (order.date_order + timedelta(hours=7)).strftime('%H:%M:%S')
                    quantity_pembelian = line.product_qty
                    total_price = line.price_total

                    sales_sheet.write(purchase_row, 17, product_name, data_format)
                    sales_sheet.write(purchase_row, 18, order.date_order, date_format)
                    sales_sheet.write(purchase_row, 19, order_time, data_format)
                    sales_sheet.write(purchase_row, 20, quantity_pembelian, data_format)
                    sales_sheet.write(purchase_row, 21, total_price, data_format)
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