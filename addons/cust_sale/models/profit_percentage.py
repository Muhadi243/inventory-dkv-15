from odoo import models, fields

class ProfitPercentage(models.Model):
    _name = 'profit.percentage'
    _description = 'Profit Percentage'

    name = fields.Char(string="Name", required=True)
    operator_mar = fields.Float(string="Operator/Mar (%)", required=True)
    operator_mesin = fields.Float(string="Operator/Mesin (%)", required=True)
    bc_atk = fields.Float(string="BC ATK (%)", required=True)
    bc_custom = fields.Float(string="BC Custom (%)", required=True)
    operasional_atk = fields.Float(string="Operasional ATK (%)", required=True)
    operasional_custom = fields.Float(string="Operasional Custom (%)", required=True)
    sekolah_atk = fields.Float(string="Sekolah ATK (%)", required=True)
    sekolah_custom = fields.Float(string="Sekolah Custom (%)", required=True)
