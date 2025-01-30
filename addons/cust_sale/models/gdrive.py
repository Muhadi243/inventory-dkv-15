import random
import string
import base64
import requests
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from odoo import models, fields

from odoo import models, fields

class GoogleDriveConfig(models.Model):
    _name = 'google.drive.config'
    _description = 'Google Drive Configuration'

    google_drive_client_id = fields.Char(string="Client ID", required=True)
    google_drive_client_secret = fields.Char(string="Client Secret", required=True)
    google_drive_refresh_token = fields.Char(string="Refresh Token", required=True)
    def save_google_drive_config(self):
        # Add any logic to save or process the configuration
        # For example, save the settings to ir.config_parameter if needed
        self.env['ir.config_parameter'].sudo().set_param('google_drive_client_id', self.google_drive_client_id)
        self.env['ir.config_parameter'].sudo().set_param('google_drive_client_secret', self.google_drive_client_secret)
        self.env['ir.config_parameter'].sudo().set_param('google_drive_refresh_token', self.google_drive_refresh_token)


    def upload_doc(self, res_id):
        # Fetch credentials from Odoo configuration parameters
        google_drive_client_id = self.env['ir.config_parameter'].sudo().get_param('google_drive_client_id')
        google_drive_client_secret = self.env['ir.config_parameter'].sudo().get_param('google_drive_client_secret')
        google_drive_refresh_token = self.env['ir.config_parameter'].sudo().get_param('google_drive_refresh_token')

        # Get access token
        access_token = self.get_access_token()

        # Prepare token information for Google API
        info_token = {
            "token": access_token,
            'refresh_token': google_drive_refresh_token,
            "client_id": google_drive_client_id,
            "client_secret": google_drive_client_secret,
        }

        # Check token validity and refresh if necessary
        creds = Credentials.from_authorized_user_info(info_token, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

        # Get sale order information
        so = self.env['sale.order'].browse(res_id)
        template_id = so._find_mail_template()
        template = self.env['mail.template'].browse(template_id)
        res_ids = so.id

        # Generate email values from template
        if isinstance(so.ids, int):
            res_ids = [so.ids]
        values = template.generate_email(res_ids, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'attachment_ids', 'mail_server_id'])

        if values and values.get('attachments'):
            attachments = values.get('attachments')
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
            pdf_name = "%s.pdf" % ran_str

            # Save the attachment as a PDF file
            with open(pdf_name, 'wb') as f:
                f.write(base64.b64decode(attachments[0][1]))

            # Upload to Google Drive
            service = build('drive', 'v3', credentials=creds)
            file_metadata = {
                'name': pdf_name,
                "parents": ['1V1NM-1d-A-Q3UXdVOGUkHcj6gNGZQMga'],  # Folder ID where the file should be uploaded
            }
            media = MediaFileUpload(f.name)

            # Create file on Google Drive
            file_id = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            # Set file permissions to 'reader' for 'anyone'
            post_data = {
                "role": "reader",
                "type": "anyone"
            }
            headers = {
                'Content-type': 'application/json',
                'Authorization': 'Bearer %s' % access_token
            }
            req2 = requests.post(f"https://www.googleapis.com/drive/v2/files/{file_id.get('id')}/permissions", headers=headers, data=json.dumps(post_data))

            # If successfully uploaded the file, get the link
            if req2.status_code == 200:
                google_drive_pdf_link = f"https://drive.google.com/file/d/{file_id.get('id')}/view"
                return google_drive_pdf_link

        return ""
    

class SaleOrder(models.Model):
   _inherit = 'sale.order'
   sale_upload = fields.Boolean(default=True)
   def action_upload_to_drive(self):
       self.ensure_one()
       self.env['google.drive.config'].upload_doc(self.id)
       return True