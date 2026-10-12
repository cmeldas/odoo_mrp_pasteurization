from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestMrpPasteurization(TransactionCase):
    """Pasterace na výrobní zakázce: převzetí teploty z produktu, start při potvrzení, kontrola při dokončení."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_63, cls.product_92, cls.product_plain = cls.env['product.product'].create([
            {'name': 'Mléko 63', 'type': 'consu', 'pasteurisation_temperature': '63'},
            {'name': 'Smetana 92', 'type': 'consu', 'pasteurisation_temperature': '92'},
            {'name': 'Bez pasterace', 'type': 'consu'},
        ])

    def _create_mo(self, product):
        return self.env['mrp.production'].create({'product_id': product.id, 'product_qty': 1.0})

    def test_temperature_copied_from_product(self):
        self.assertEqual(self._create_mo(self.product_63).pasteurisation_temperature, '63')
        self.assertEqual(self._create_mo(self.product_92).pasteurisation_temperature, '92')
        self.assertFalse(self._create_mo(self.product_plain).pasteurisation_temperature)

    def test_confirm_starts_pasteurisation(self):
        low = self._create_mo(self.product_63)
        high = self._create_mo(self.product_92)
        plain = self._create_mo(self.product_plain)
        (low | high | plain).action_confirm()

        self.assertEqual(low.state, 'confirmed')
        self.assertTrue(low.pasteurisation_start)
        self.assertTrue(30 <= low.pasteurisation_duration <= 40)
        self.assertTrue(high.pasteurisation_start)
        self.assertTrue(2 <= high.pasteurisation_duration <= 10)
        self.assertFalse(plain.pasteurisation_start)
        self.assertFalse(plain.pasteurisation_duration)

    def test_mark_done_requires_start(self):
        production = self._create_mo(self.product_plain)
        production.action_confirm()
        production.pasteurisation_temperature = '63'
        with self.assertRaises(UserError):
            production.button_mark_done()

    def test_mark_done_with_pasteurisation(self):
        production = self._create_mo(self.product_63)
        production.action_confirm()
        with Form(production) as mo_form:
            mo_form.qty_producing = 1.0
        production.button_mark_done()
        self.assertEqual(production.state, 'done')

    def test_mass_mark_done_several_productions(self):
        """Hromadná akce Označit jako hotové (mrp.action_production_order_mark_done) volá
        button_mark_done na víc zakázek najednou; kontrola nesmí spadnout na singleton."""
        low = self._create_mo(self.product_63)
        high = self._create_mo(self.product_92)
        plain = self._create_mo(self.product_plain)
        productions = low | high | plain
        productions.action_confirm()
        for production in productions:
            with Form(production) as mo_form:
                mo_form.qty_producing = 1.0

        high.pasteurisation_start = False
        with self.assertRaises(UserError) as error:
            productions.button_mark_done()
        self.assertIn(high.display_name, str(error.exception))
        self.assertNotIn(low.display_name, str(error.exception))

        high.set_pasteurisation_start()
        action = self.env.ref('mrp.action_production_order_mark_done')
        action.with_context(active_model='mrp.production', active_ids=productions.ids).run()
        self.assertEqual(set(productions.mapped('state')), {'done'})

    def test_none_temperature_means_no_pasteurisation(self):
        """Prázdná volba 'none' se chová jako bez pasterace (dřív confirm spadl na int('none'))."""
        production = self._create_mo(self.product_plain)
        production.pasteurisation_temperature = 'none'
        production.action_confirm()
        self.assertEqual(production.state, 'confirmed')
        self.assertFalse(production.pasteurisation_start)
        with self.assertRaises(UserError):
            production.set_pasteurisation_start()
        with Form(production) as mo_form:
            mo_form.qty_producing = 1.0
        production.button_mark_done()
        self.assertEqual(production.state, 'done')

    def test_start_and_end_buttons(self):
        production = self._create_mo(self.product_plain)
        with self.assertRaises(UserError):
            production.set_pasteurisation_start()
        with self.assertRaises(UserError):
            production.end_pasteurisation()

        production.pasteurisation_temperature = '92'
        production.set_pasteurisation_start()
        self.assertTrue(production.pasteurisation_start)
        production.pasteurisation_start = fields.Datetime.now() - timedelta(minutes=5)
        production.end_pasteurisation()
        self.assertEqual(production.pasteurisation_duration, 5)
