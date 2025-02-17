from odoo import models, fields
from datetime import datetime, timedelta
import io
import xlsxwriter
import base64
from odoo.http import content_disposition, request
from odoo.tools import date_utils
from collections import defaultdict


class SalesReportXlsx(models.TransientModel):
    _name = 'sales.report.xlsx'
    _description = 'Daily Sales Report in Excel'

    report_date = fields.Date(string="Report Date", default=fields.Date.context_today)

    def generate_xlsx_report(self):
        """Method to generate the Excel report for daily sales."""
        sale_orders = self.env['sale.order'].search([
            ('date_order', '>=', self.report_date),
            ('date_order', '<', self.report_date + timedelta(days=1)),
            ('state', 'in', ['sale', 'done'])
        ])
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Daily Sales Report")
        
        # Define Styles
        bold = workbook.add_format({'bold': True, 'bg_color': '#FFFF99'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # Write Headers
        headers = ["Product", "Type", "Stock", "Total Sold", "Total Price"]
        sheet.write_row(0, 0, headers, bold)

        product_data = defaultdict(lambda: {'price': 0, 'type': '', 'stock': 0, 'sold': 0})
        
        for order in sale_orders:
            for line in order.order_line:
                if line.product_id:
                    product_type = line.product_id.type_product
                    if product_type in ['atk', 'custom']:
                        product_name = line.product_id.name or ""
                        product_data[product_name]['price'] += line.price_total
                        product_data[product_name]['type'] = product_type
                        product_data[product_name]['stock'] = line.product_id.product_tmpl_id.stock
                        product_data[product_name]['sold'] += line.product_uom_qty

        row = 1
        total_price = 0
        total_sold = 0
        for product_name, data in product_data.items():
            product_type = dict(line.product_id._fields['type_product'].selection(line.product_id)).get(data['type'], "")
            sheet.write(row, 0, product_name)
            sheet.write(row, 1, product_type)
            sheet.write(row, 2, data['stock'])
            sheet.write(row, 3, data['sold'])
            sheet.write(row, 4, data['price'])
            total_price += data['price']
            total_sold += data['sold']
            row += 1

        # Write Totals with colspan
        sheet.merge_range(row, 0, row, 2, "Total", bold)
        sheet.write(row, 3, total_sold, bold)
        sheet.write(row, 4, total_price, bold)

        workbook.close()
        output.seek(0)

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'Daily_Sales_Report.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'store_fname': 'daily_sales_report.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        output.close()

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
