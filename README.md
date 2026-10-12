# MRP Pasteurization

An Odoo module for managing pasteurization data in manufacturing orders.

## Overview

This module extends Odoo's Manufacturing (MRP) module to track and manage pasteurization processes for manufactured products. It enables logging of pasteurization temperature, duration, and timing data directly on manufacturing orders.

## Features

- **Pasteurization Temperature Selection**: Choose from predefined pasteurization temperatures (63°C or 92°C) for each manufacturing order. If you want different temperatures, you can customize the selection field.
- **Default Product Settings**: Set default pasteurization temperatures at the product level
- **Automated Duration Calculation**: Automatic calculation of pasteurization duration based on temperature:
  - Low temperature (63°C): 30-40 minutes (mean: 32.5 minutes)
  - High temperature (92°C): 2-10 minutes (mean: 4 minutes)
- **Time Tracking**: Record pasteurization start time and calculate actual duration
- **Validation**: Ensures pasteurization data is complete before marking manufacturing orders as done
- **Auto-population**: Automatically inherits pasteurization temperature from product settings when creating a new manufacturing order

## Requirements

- Odoo 20.0 (branch `20.0`; `master` = Odoo 18, `19.0` = Odoo 19)
- MRP (Manufacturing) module

## Installation

1. Copy the `mrp_pasteurization` module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Manufacturing Pasteurisation Data" module

## Usage

### Setting Up Products

1. Navigate to a product template
2. Set the default pasteurization temperature in the product form
3. This temperature will be automatically applied to new manufacturing orders for this product

### Manufacturing Orders

1. Create or open a manufacturing order
2. Select the pasteurization temperature (if not already set from product)
3. When ready to start pasteurization:
   - The system can automatically record the start time and calculate duration
   - Or manually track the start and end times
4. Complete the manufacturing order once pasteurization is finished

### Workflow

- **Start Pasteurization**: Records the current date/time as the start of the pasteurization process
- **Set Duration**: Automatically calculates appropriate duration based on temperature
- **End Pasteurization**: Records the end time and calculates actual duration
- **Validation**: The system prevents completion of manufacturing orders without proper pasteurization data

## Odoo 20

Větev `20.0`, verze `20.0.1.0.1`. Všechno, na co modul v jádře sahá, funguje v Odoo 20 stejně
(ověřeno proti zdrojům 20):

- Tlačítko Vyrobit dál volá `mrp.production.button_mark_done()`, kontrola začátku pasterace
  před dokončením proto platí beze změny.
- `action_confirm()` nastavuje stav přiřazením `state = 'confirmed'`, přepsaný `write` tedy
  při potvrzení dál zapíše začátek a dobu pasterace.
- Pohledy `mrp.mrp_production_form_view` (notebook), `mrp.mrp_production_tree_view`
  (pole `product_id`) a `product.product_template_form_view` (notebook) existují beze změny.
- Přejmenování `product_uom_id` → `uom_id` na výrobní zakázce se modulu netýká.

Opravy chování při portu (proto verze `1.0.1`):

- Prázdná volba teploty (`none`) se bere jako „bez pasterace“. Dřív potvrzení zakázky s touto
  volbou spadlo na `int('none')` a tlačítko Začátek pasterizace ji brala jako zadanou teplotu.
- Kontrola před dokončením funguje i pro víc zakázek najednou (hromadná akce Označit jako
  hotové v seznamu). Dřív padala na „Expected singleton“; chybová hláška teď vypíše zakázky
  bez začátku pasterace.

Nově jsou v `tests/` testy (převzetí teploty z produktu, start a doba pasterace při potvrzení,
zákaz dokončení bez začátku, hromadné dokončení, volba `none`, tlačítka Začátek/Ukončit).

**Migrace dat:** žádná. Modul ukládá jen vlastní sloupce `pasteurisation_*` na
`mrp_production` a `pasteurisation_temperature` na `product_template`; jejich typ ani hodnoty
se nemění (na produkci 6. 10. 2026: 1 271 zakázek s teplotou 63 nebo 92 °C, 11 produktů s výchozí
teplotou, hodnota `none` se v datech nevyskytuje).

## License

LGPL-3
