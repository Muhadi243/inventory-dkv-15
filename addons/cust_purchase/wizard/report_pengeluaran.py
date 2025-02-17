from odoo import models, fields
from datetime import datetime, timedelta
import io
import xlsxwriter
import base64
from collections import defaultdict


class PurchaseReportXlsx(models.TransientModel):
    _name = 'purchase.report.xlsx'
    _description = 'Purchase Report in Excel'

    report_date = fields.Date(string="Report Date", default=fields.Date.context_today)

    def generate_xlsx_report(self):
        """Method to generate the Excel report for purchases."""
        purchase_orders = self.env['purchase.order'].search([
            ('date_order', '>=', self.report_date),
            ('date_order', '<', self.report_date + timedelta(days=1)),
            ('state', 'in', ['purchase', 'done'])
        ])
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Purchase Report")
        
        # Define Styles
        bold = workbook.add_format({'bold': True, 'bg_color': '#FFFF99'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # Write Headers
        headers = ["Product", "Quantity", "Total Expenditure"]
        sheet.write_row(0, 0, headers, bold)

        product_data = defaultdict(lambda: {'quantity': 0, 'total_expenditure': 0})
        
        for order in purchase_orders:
            for line in order.order_line:
                product_name = line.product_id.name if line.product_id else line.name
                quantity = line.product_qty
                total_expenditure = line.price_total

                product_data[product_name]['quantity'] += quantity
                product_data[product_name]['total_expenditure'] += total_expenditure

        row = 1
        for product_name, data in product_data.items():
            sheet.write(row, 0, product_name)
            sheet.write(row, 1, data['quantity'])
            sheet.write(row, 2, data['total_expenditure'])
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
