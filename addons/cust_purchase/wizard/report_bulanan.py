from odoo import models, fields
from datetime import datetime, timedelta
import io
import xlsxwriter
import base64

class PurchaseReportXlsx(models.TransientModel):
    _name = 'purchase.report.xlsx'
    _description = 'Purchase Report in Excel'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    def generate_xlsx_report(self):
        """Method to generate the Excel report for purchases within a date range."""
        purchase_orders = self.env['purchase.order'].search([
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
            ('state', 'in', ['purchase', 'done'])
        ])
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Purchase Report")
        
        # Define Styles
        bold = workbook.add_format({'bold': True, 'bg_color': '#FFFF99'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        time_format = workbook.add_format({'num_format': 'hh:mm:ss'})

        # Write Headers
        headers = ["Product", "Quantity", "Date", "Time", "Total"]
        sheet.write_row(0, 0, headers, bold)

        row = 1
        for order in purchase_orders:
            for line in order.order_line:
                if line.product_id.type_product == 'store':
                    product_name = line.product_id.name if line.product_id else line.name
                    quantity = line.product_qty
                    date_time = fields.Datetime.from_string(order.date_order) + timedelta(hours=7)
                    total = line.price_total

                    sheet.write(row, 0, product_name)
                    sheet.write(row, 1, quantity)
                    sheet.write(row, 2, date_time.date(), date_format)
                    sheet.write(row, 3, date_time.time(), time_format)
                    sheet.write(row, 4, total)
                    row += 1

        workbook.close()
        output.seek(0)

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'Purchase_Report.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'store_fname': 'purchase_report.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        output.close()

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
