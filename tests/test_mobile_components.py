from lxml import etree

from odoo.tests import Form, TransactionCase, tagged

# Pole zakázky, se kterými simulace webového klienta pracuje (podmnožina formuláře).
MO_FIELDS = ['product_id', 'product_qty', 'uom_id', 'bom_id', 'company_id', 'picking_type_id',
             'location_src_id', 'location_dest_id', 'date_start']


def _plain(value):
    return value['id'] if isinstance(value, dict) and 'id' in value else value


@tagged('post_install', '-at_install')
class TestMobileComponents(TransactionCase):
    """Komponenty zakázky z telefonu (kanban stock.move) si drží vazbu na řádek kusovníku.

    Odoo 20 zobrazuje na malé obrazovce move_raw_ids jako kanban. Simulace posílá onchange
    a web_save jen s poli z toho kanbanu, stejně jako webový klient.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.milk = cls.env['product.product'].create({'name': 'Mléko', 'type': 'consu'})
        cls.natur, cls.chilli = cls.env['product.product'].create([
            {'name': 'Sýr natur', 'type': 'consu'},
            {'name': 'Sýr chilli', 'type': 'consu'},
        ])
        cls.bom_natur, cls.bom_chilli = cls.env['mrp.bom'].create([
            {
                'product_tmpl_id': product.product_tmpl_id.id,
                'product_qty': 1.0,
                'bom_line_ids': [(0, 0, {'product_id': cls.milk.id, 'product_qty': qty})],
            }
            for product, qty in ((cls.natur, 6.0), (cls.chilli, 10.0))
        ])

    def _kanban_fields(self):
        """Pole kanbanu stock.move a z nich ta, která klient při uložení pošle (ne jen pro čtení)."""
        Move = self.env['stock.move']
        arch = Move.get_views([(False, 'kanban')])['views']['kanban']['arch']
        fields, writable = {}, set()
        for node in etree.fromstring(arch).iter('field'):
            name = node.get('name')
            fields[name] = {}
            if not Move._fields[name].readonly and node.get('readonly') not in ('1', 'True'):
                writable.add(name)
        return fields, writable

    def _to_vals(self, values, move_writable):
        """Hodnoty z onchange převedené na to, co klient pošle do web_save."""
        vals = {name: _plain(value) for name, value in values.items() if name in MO_FIELDS}
        if 'move_raw_ids' in values:
            commands = []
            for command in values['move_raw_ids']:
                if command[0] in (0, 1):
                    move_vals = {k: _plain(v) for k, v in command[2].items() if k in move_writable}
                    commands.append([command[0], 0 if command[0] == 0 else command[1], move_vals])
                else:
                    commands.append(list(command))
            vals['move_raw_ids'] = commands
        return vals

    def test_kanban_loads_bom_line(self):
        fields, _writable = self._kanban_fields()
        self.assertIn('bom_line_id', fields)

    def test_mobile_product_change_keeps_single_component(self):
        move_fields, move_writable = self._kanban_fields()
        spec = dict.fromkeys(MO_FIELDS, {}) | {'move_raw_ids': {'fields': move_fields}}
        MO = self.env['mrp.production']

        # Nová zakázka: vybrat produkt a uložit.
        values = MO.onchange({}, [], spec)['value']
        values['product_id'] = self.natur.id
        values.update(MO.onchange(self._to_vals(values, move_writable), ['product_id'], spec)['value'])
        mo = MO.browse(MO.web_save(self._to_vals(values, move_writable), {})[0]['id'])
        self.assertEqual(mo.move_raw_ids.bom_line_id, self.bom_natur.bom_line_ids)

        # Uložená zakázka v návrhu (jako po Duplikovat): změnit produkt a uložit.
        current = mo.web_read(spec)[0]
        values = {name: _plain(value) for name, value in current.items() if name in MO_FIELDS}
        values['move_raw_ids'] = [[4, _plain(move)] for move in current['move_raw_ids']]
        values['product_id'] = self.chilli.id
        change = mo.onchange(values, ['product_id'], spec)['value']
        mo.web_save(self._to_vals(change | {'product_id': self.chilli.id}, move_writable), {})

        self.assertEqual(len(mo.move_raw_ids), 1, "mléko má být v zakázce jednou")
        self.assertEqual(mo.move_raw_ids.bom_line_id, self.bom_chilli.bom_line_ids)
        self.assertEqual(mo.move_raw_ids.product_uom_qty, 10.0)

        mo.action_confirm()
        self.assertEqual(len(mo.move_raw_ids), 1)

    def _broken_order(self):
        """Zakázka jako na produkci před opravou: mléko dvakrát a bez vazby na kusovník."""
        mo = self.env['mrp.production'].create({'product_id': self.natur.id, 'product_qty': 3.0})
        mo.move_raw_ids.bom_line_id = False
        mo.move_raw_ids.copy({'raw_material_production_id': mo.id})
        self.assertEqual(len(mo.move_raw_ids), 2)
        self.assertFalse(mo.move_raw_ids.bom_line_id)
        return mo

    def test_copy_takes_components_from_bom(self):
        copy = self._broken_order().copy()

        self.assertEqual(copy.product_qty, 3.0)
        self.assertEqual(len(copy.move_raw_ids), 1, "duplikát má mít mléko jednou")
        self.assertEqual(copy.move_raw_ids.bom_line_id, self.bom_natur.bom_line_ids)
        self.assertEqual(copy.move_raw_ids.product_uom_qty, 18.0)

    def test_copy_then_product_change(self):
        """Duplikovat rozbitou zakázku a ve formuláři změnit produkt i množství."""
        copy = self._broken_order().copy()
        with Form(copy) as form:
            form.product_id = self.chilli
            form.product_qty = 2.0

        self.assertEqual(len(copy.move_raw_ids), 1)
        self.assertEqual(copy.move_raw_ids.bom_line_id, self.bom_chilli.bom_line_ids)
        self.assertEqual(copy.move_raw_ids.product_uom_qty, 20.0)

    def test_copy_without_bom_keeps_components(self):
        product = self.env['product.product'].create({'name': 'Bez kusovníku', 'type': 'consu'})
        mo = self.env['mrp.production'].create({
            'product_id': product.id,
            'product_qty': 1.0,
            'move_raw_ids': [(0, 0, {'product_id': self.milk.id, 'product_uom_qty': 4.0})],
        })
        self.assertFalse(mo.bom_id)

        copy = mo.copy()
        self.assertEqual(copy.move_raw_ids.product_id, self.milk)
        self.assertEqual(copy.move_raw_ids.product_uom_qty, 4.0)

    def test_backorder_keeps_core_components(self):
        """Nedodělek si komponenty řídí jádro (move_raw_ids v default), kopie je nemění."""
        mo = self.env['mrp.production'].create({'product_id': self.natur.id, 'product_qty': 4.0})
        mo.action_confirm()
        backorder = mo._split_productions({mo: [1.0, 3.0]})[-1]

        self.assertEqual(backorder.product_qty, 3.0)
        self.assertEqual(len(backorder.move_raw_ids), 1)
        self.assertEqual(backorder.move_raw_ids.product_uom_qty, 18.0)
        self.assertEqual(mo.move_raw_ids.product_uom_qty, 6.0)
