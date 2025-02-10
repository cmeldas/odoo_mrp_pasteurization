from odoo import models, fields

PASTEURIZATION_TEMPERATURES = [
    ("none", ""),  # Empty option
    ("63", "63°C"),
    ("90", "90°C"),
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pasteurisation_temperature = fields.Selection(
        PASTEURIZATION_TEMPERATURES,
        string="Defaultní teplota pasteurizace",
        help="Defaultní teplota pasteurizace pro tento produkt",
    )
