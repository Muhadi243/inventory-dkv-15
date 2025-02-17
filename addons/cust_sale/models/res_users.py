from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    type_user = fields.Selection([
        ('atk', 'ATK'),
        ('custom', 'Custom'),
        ('print', 'Print'),
    ], string='Type User', default='atk')