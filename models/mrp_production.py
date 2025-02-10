from odoo import models, fields, api
import random


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    pasteurisation_temperature = fields.Selection(
        [("90", "90"), ("63", "63")],
        string="Pasteurisation Temperature",
        help="Temperature used during the pasteurisation process",
    )
    pasteurisation_duration = fields.Integer(
        string="Pasteurisation Duration (minutes)",
        help="Duration of the pasteurisation process in minutes",
    )
    pasteurisation_start = fields.Datetime(
        string="Pasteurisation Start Time",
        help="Start time of the pasteurisation process",
    )

    def set_pasteurisation_start(self):
        self.pasteurisation_start = fields.Datetime.now()

    def set_pasteurisation_duration(self):
        if (
            self.pasteurisation_temperature
            and int(self.pasteurisation_temperature) < 70
        ):
            self.pasteurisation_duration = int(random.uniform(30, 35))
        else:
            self.pasteurisation_duration = int(random.uniform(2, 6))
