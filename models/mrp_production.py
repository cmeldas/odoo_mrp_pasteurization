from odoo import models, fields, api, _
import random
from .product import PASTEURIZATION_TEMPERATURES
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    pasteurisation_temperature = fields.Selection(
        PASTEURIZATION_TEMPERATURES,
        string=_("Pasterizační teplota"),
        help=_("Teplota použitá během pasterizace"),
    )
    pasteurisation_duration = fields.Integer(
        string=_("Doba pasterizace"),
        help=_("Doba trvání pasterizace v minutách"),
    )
    pasteurisation_start = fields.Datetime(
        string=_("Začátek pasterizace"),
        help=_("Datum a čas začátku pasterizace."),
    )

    def set_pasteurisation_start(self):
        if not self.pasteurisation_temperature:
            raise UserError(_("Zadej prvně teplotu pasterizace."))
        self.pasteurisation_start = fields.Datetime.now()
        

    def set_pasteurisation_duration(self):
        def clamp(value, min_val, max_val):
            return max(min_val, min(max_val, value))

        if (
            self.pasteurisation_temperature
            and int(self.pasteurisation_temperature) < 70
        ):
            # Low temp (63°C): mean=32.5, std=1, min=30, max=35
            duration = random.gauss(32.5, 1)
            self.pasteurisation_duration = int(clamp(duration, 30, 40))
        else:
            # High temp (90°C): mean=4, std=0.5, min=2, max=6
            duration = random.gauss(4, 0.5)
            self.pasteurisation_duration = int(clamp(duration, 2, 10))

    def end_pasteurisation(self):
        if not self.pasteurisation_start:
            raise UserError(_("Nelze ukončit pasterizaci bez zadaného začátku."))

        end_time = fields.Datetime.now()
        duration = (end_time - self.pasteurisation_start).total_seconds() / 60
        self.pasteurisation_duration = int(duration)

    def _validate_pasteurisation(self):
        if self.pasteurisation_temperature and not self.pasteurisation_start:
            raise UserError(_("Nelze dokončit výrobu bez zadání začátku pasterizace."))

    def button_mark_done(self):
        self._validate_pasteurisation()
        return super().button_mark_done()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.product_id.pasteurisation_temperature:
            res.pasteurisation_temperature = res.product_id.pasteurisation_temperature
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get('state') == 'confirmed' and self.pasteurisation_start is False:
            self.set_pasteurisation_start()
            self.set_pasteurisation_duration()
        return res
