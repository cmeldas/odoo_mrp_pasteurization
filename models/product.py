from odoo import models, fields

PASTEURIZATION_TEMPERATURES = [
    ("63", "63°C"),
    ("90", "90°C"),
    ("none", ""),  # Empty option for no pasteurization
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pasteurisation_temperature = fields.Selection(
        PASTEURIZATION_TEMPERATURES,
        string="Defaultní teplota pasterizace",
        help="Defaultní teplota pasterizace pro tento produkt",
    )
